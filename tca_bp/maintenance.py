"""Évolution de formules sur une version distincte, testée avant publication.

Ce module n'est pas appelé par le parcours de saisie et ne migre aucun dossier.
Le support présent porte sur les formules ordinaires existantes. Les structures,
macros et tables natives nécessitent un autre développement explicitement testé.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import tempfile
import uuid
import zipfile

from .knowledge import contracts
from .storage import atomic_json, canonical, digest
from .vendor import input_engine as core
from .model_build import invalidate_caches


def _now():
    return datetime.now(timezone.utc).isoformat()


def _fingerprint(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _safe_formula(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 8192:
        raise ValueError("Une formule Excel non vide, de 8 192 caractères maximum, est requise.")
    formula = value.strip().removeprefix("=")
    if any(ord(char) < 32 for char in formula) or any(char in formula for char in ("[", "]", "|")):
        raise ValueError("Les références externes et caractères de contrôle sont exclus de ce parcours.")
    if re.search(r"\b(?:WEBSERVICE|HYPERLINK|RTD|CALL|EXEC|REGISTER\.ID)\s*\(", formula, re.I):
        raise ValueError("Une formule appelant un service ou du code externe est hors périmètre.")
    return formula


class Maintenance:
    def __init__(self, engine, *, recalculator=None):
        self.engine = engine
        self.project_root = Path(engine.project_root).resolve()
        self.versions_root = self.project_root / "models" / "versions"
        if recalculator is None:
            from .native_excel import recalculate
            recalculator = recalculate
        self.recalculator = recalculator

    def _impact(self, sheets):
        graph_path = Path(getattr(self.engine, "model_dir", self.engine.template_path.parent)) / "graphe_dependances.json"
        basis = "CONTRATS_METIER_CONSERVATEURS"
        if graph_path.is_file():
            graph = json.loads(graph_path.read_text(encoding="utf-8"))["sheets"]
            basis = "GRAPHE_EXTRAIT_MODELE; références dynamiques et VBA à qualifier séparément"
        else:
            graph = {spec["sheet"]: spec["dependencies"] for spec in contracts()}
        impacted = set(sheets)
        changed = True
        while changed:
            changed = False
            for sheet, sources in graph.items():
                if sheet not in impacted and impacted.intersection(sources):
                    impacted.add(sheet)
                    changed = True
        return sorted(impacted), basis

    def propose(self, changes: list[dict], version_id: str, reason: str) -> dict:
        self.engine.ensure_built()
        if not isinstance(version_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]{2,95}", version_id) or ".." in version_id:
            raise ValueError("Identifiant de version invalide.")
        if version_id == self.engine.model_id:
            raise ValueError("Une évolution doit posséder un nouvel identifiant de modèle.")
        if not isinstance(reason, str) or len(reason.strip()) < 15:
            raise ValueError("Décrire la règle économique et la raison de l'évolution.")
        if not isinstance(changes, list) or not 1 <= len(changes) <= 100:
            raise ValueError("Décrire entre une et cent modifications de formules.")
        wb = self.engine._open(self.engine.template_path)
        normalized = []
        seen = set()
        try:
            for change in changes:
                if not isinstance(change, dict) or set(change) - {"sheet", "cell", "formula", "new_formula", "old_formula", "reason"}:
                    raise ValueError("Structure de modification inconnue.")
                sheet, cell = change.get("sheet"), change.get("cell")
                if not isinstance(sheet, str) or not isinstance(cell, str):
                    raise ValueError("Chaque modification doit identifier une feuille et une cellule.")
                _, col, row = core.coord(cell)
                cell = core.colname(col) + str(row)
                if (sheet, cell) in seen:
                    raise ValueError("Une cellule apparaît deux fois dans la proposition.")
                seen.add((sheet, cell))
                original = wb.formula(sheet, cell)
                if original is None:
                    raise ValueError("Ce parcours modifie une formule existante ; une nouvelle cellule ou constante suit un développement distinct.")
                node = wb.sheet(sheet)[1][cell].find("m:f", core.N)
                if node.get("t") not in (None, "normal", "shared"):
                    raise ValueError("Les formules matricielles et tables natives sont hors de ce parcours.")
                if "old_formula" in change and change["old_formula"] != original:
                    raise ValueError("La formule a changé depuis la lecture de la proposition.")
                new = _safe_formula(change.get("formula", change.get("new_formula")))
                if original == new:
                    raise ValueError("La nouvelle formule est identique à l'ancienne.")
                normalized.append({"sheet": sheet, "cell": cell, "old_formula": original,
                                   "new_formula": new, "reason": change.get("reason") or reason.strip()})
        finally:
            wb.close()
        impact, basis = self._impact([change["sheet"] for change in normalized])
        from .maintenance_impact import impact_report
        components = impact_report(self.engine, normalized)
        proposal = {"schema": "tca-bp-maintenance-proposal/1", "source_model_id": self.engine.model_id,
                    "source_template_sha256": digest(self.engine.template_path), "version_id": version_id,
                    "reason": reason.strip(), "changes": normalized, "affected_sheets": impact,
                    "dependency_basis": basis, "created_at": _now(), "status": "PROPOSITION",
                    "component_impact": components,
                    "limits": ["Formules ordinaires existantes uniquement.", "Aucune migration d'un dossier existant.",
                               "Les tests natifs indépendants précèdent la publication."]}
        proposal["proposal_sha256"] = _fingerprint(proposal)
        return proposal

    def _validate_proposal(self, proposal):
        if not isinstance(proposal, dict) or proposal.get("schema") != "tca-bp-maintenance-proposal/1":
            raise ValueError("Proposition de maintenance invalide.")
        value = {key: item for key, item in proposal.items() if key != "proposal_sha256"}
        if proposal.get("proposal_sha256") != _fingerprint(value):
            raise ValueError("La proposition a été modifiée après sa préparation.")
        if proposal.get("source_model_id") != self.engine.model_id or proposal.get("source_template_sha256") != digest(self.engine.template_path):
            raise ValueError("La proposition appartient à une autre version de référence.")
        # Revérifier permissions de maintenance, adresses et formules après import.
        fresh = self.propose(proposal["changes"], proposal["version_id"], proposal["reason"])
        if fresh["changes"] != proposal["changes"]:
            raise ValueError("Le contenu de la proposition ne correspond plus à la référence.")
        if 'component_impact' in proposal and fresh['component_impact'] != proposal['component_impact']:
            raise ValueError("Les composants ou le graphe ont changé depuis l'analyse d'impact.")

    def build(self, proposal: dict) -> dict:
        self._validate_proposal(proposal)
        self.versions_root.mkdir(parents=True, exist_ok=True)
        if not self.versions_root.resolve().is_relative_to(self.project_root):
            raise ValueError("Le répertoire de versions sort du projet.")
        name = "version_" + hashlib.sha256(proposal["version_id"].encode()).hexdigest()[:20]
        destination = self.versions_root / name
        if destination.exists():
            raise ValueError("Cette version existe déjà ; une version ne peut pas être écrasée.")
        source_sha = digest(self.engine.template_path)
        with tempfile.TemporaryDirectory(prefix=".maintenance-", dir=self.versions_root) as temporary:
            staging = Path(temporary)
            workbook = staging / "candidate.xlsm"
            wb = self.engine._open(self.engine.template_path)
            replacements = {}
            materialized = {}
            try:
                for sheet in {change["sheet"] for change in proposal["changes"]}:
                    edits = {change["cell"]: change["new_formula"] for change in proposal["changes"] if change["sheet"] == sheet}
                    raw = wb.z.read(wb.sheets[sheet]["part"])
                    nodes = {match[1].decode(): match[0] for match in core.CELL_RX.finditer(raw)}
                    _, cells, _ = wb.sheet(sheet)
                    actual = dict(edits)
                    converted = []
                    for cell in edits:
                        formula_node = cells[cell].find("m:f", core.N)
                        if formula_node.get("t") == "shared" and formula_node.text:
                            shared_id = formula_node.get("si")
                            for other, node in cells.items():
                                f = node.find("m:f", core.N)
                                if other not in edits and f is not None and f.get("t") == "shared" and f.get("si") == shared_id:
                                    actual[other] = wb.formula(sheet, other)
                                    converted.append(other)
                    patches = {cell: invalidate_caches(core.xml_cell(nodes[cell], None, "number", formula=formula)) for cell, formula in actual.items()}
                    replacements[wb.sheets[sheet]["part"]] = core.CELL_RX.sub(lambda match: patches.get(match[1].decode(), match[0]), raw)
                    if converted:
                        materialized[sheet] = converted
                replacements["xl/workbook.xml"] = core.mark_for_native_calculation(wb.z.read("xl/workbook.xml"))
                with zipfile.ZipFile(workbook, "w") as output:
                    for info in wb.z.infolist():
                        raw = replacements.get(info.filename, wb.z.read(info.filename))
                        if info.filename.startswith("xl/worksheets/") and info.filename.endswith(".xml"):
                            raw = invalidate_caches(raw)
                        output.writestr(deepcopy(info), raw)
            finally:
                wb.close()
            staged_version = staging / "version"
            receipt = self.engine.reseal_variant(workbook, staged_version, proposal["version_id"], proposal["changes"])
            if digest(self.engine.template_path) != source_sha:
                raise ValueError("La référence a changé pendant la construction.")
            descriptor = {"schema": "tca-bp-maintenance-version/1", "status": "EXPERIMENTALE",
                          "version_id": proposal["version_id"], "source_model_id": self.engine.model_id,
                          "source_template_sha256": source_sha, "template_sha256": receipt["template_sha256"],
                          "schema_sha256": receipt["schema_sha256"], "model_dir": str(destination),
                          "created_at": _now(), "proposal": deepcopy(proposal),
                          "equivalent_shared_formula_serialization": materialized,
                          "native_validation": "NOT_EXECUTED", "existing_cases_migrated": False}
            atomic_json(staged_version / "maintenance.json", descriptor)
            # Les chemins descriptifs sont adaptés avant la publication du dossier.
            build_path = staged_version / "build_receipt.json"
            if build_path.is_file():
                build_receipt = json.loads(build_path.read_text(encoding="utf-8"))
                for key in ("template_path", "schema_path"):
                    if build_receipt.get(key):
                        build_receipt[key] = str(destination / Path(build_receipt[key]).name)
                atomic_json(build_path, build_receipt)
            staged_version.rename(destination)
        return descriptor

    def _version(self, model_dir):
        folder = Path(model_dir).resolve()
        if not folder.is_relative_to(self.versions_root.resolve()):
            raise ValueError("Cette version n'appartient pas à l'espace de maintenance du projet.")
        descriptor = json.loads((folder / "maintenance.json").read_text(encoding="utf-8"))
        variant = type(self.engine)(self.project_root, model_dir=folder)
        variant.ensure_built()
        if (variant.model_id != descriptor["version_id"] or digest(variant.template_path) != descriptor["template_sha256"]
                or digest(folder / "modele.json") != descriptor["schema_sha256"]):
            raise ValueError("La version de maintenance a changé depuis sa construction.")
        proposal = descriptor["proposal"]
        if (proposal.get("proposal_sha256") != _fingerprint({k: v for k, v in proposal.items() if k != "proposal_sha256"})
                or proposal.get("version_id") != descriptor["version_id"]
                or proposal.get("source_model_id") != descriptor["source_model_id"]
                or proposal.get("source_template_sha256") != descriptor["source_template_sha256"]):
            raise ValueError("Le descripteur et la proposition de maintenance ne concordent plus.")
        return folder, descriptor, variant

    def validate(self, model_dir: str | Path, scenarios: list[dict]) -> dict:
        folder, descriptor, variant = self._version(model_dir)
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("Au moins un scénario fictif avec attentes indépendantes est requis.")
        targets = {(change["sheet"], change["cell"]) for change in descriptor["proposal"]["changes"]}
        covered = set()
        for scenario in scenarios:
            if not isinstance(scenario, dict) or scenario.get("fictional") is not True or not scenario.get("name"):
                raise ValueError("Chaque scénario doit être nommé et explicitement fictif.")
            if not isinstance(scenario.get("outputs"), list) or not scenario["outputs"]:
                raise ValueError("Des valeurs attendues indépendantes sont requises pour chaque scénario.")
            if "include_tables" in scenario and type(scenario["include_tables"]) is not bool:
                raise ValueError("include_tables doit être un booléen explicite.")
            for assertion in scenario["outputs"]:
                if not isinstance(assertion, dict) or not {"sheet", "cell", "expected"} <= set(assertion):
                    raise ValueError("Chaque attente indique une feuille, une cellule et une valeur attendue.")
                tolerance = assertion.get("tolerance", 0)
                if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or tolerance < 0:
                    raise ValueError("La tolérance doit être un nombre fini positif ou nul.")
                covered.add((assertion["sheet"], assertion["cell"]))
        if not targets <= covered:
            raise ValueError("Chaque formule modifiée doit avoir au moins une attente native indépendante.")
        run_folder = folder / "validation" / ("run_" + uuid.uuid4().hex)
        run_folder.mkdir(parents=True)
        reports = []
        for index, scenario in enumerate(scenarios, 1):
            case_folder = run_folder / f"scenario_{index:03d}"
            case_folder.mkdir()
            report = {"name": scenario["name"], "fictional": True, "status": "FAIL", "assertions": []}
            try:
                input_workbook = variant.template_path
                if scenario.get("updates"):
                    plan = variant.prepare(variant.template_path, scenario["updates"])
                    input_workbook = case_folder / "inputs.xlsm"
                    variant.apply(variant.template_path, plan, input_workbook)
                before = variant.context(input_workbook)
                output = case_folder / "recalculated.xlsm"
                native_path = case_folder / "native.json"
                native = self.recalculator(input_workbook, output, native_path, include_tables=bool(scenario.get("include_tables", False)))
                if native.get("status") != "RECALCULE" or native.get("calculation_state") != 0:
                    raise ValueError("Le calcul natif n'est pas terminé.")
                if native.get("source_sha256") != digest(input_workbook) or native.get("output_sha256") != digest(output):
                    raise ValueError("La preuve native ne correspond pas aux fichiers du scénario.")
                if native.get("macros_enabled") is True:
                    raise ValueError("Ce parcours d'oracles n'autorise pas l'exécution de macros.")
                after = variant.context(output)
                if not before.get("input_signature") or before["input_signature"] != after.get("input_signature"):
                    raise ValueError("Le calcul a modifié les entrées ou leur signature n'est pas vérifiable.")
                for assertion in scenario["outputs"]:
                    inspection = variant.inspect(output, assertion["sheet"], [assertion["cell"]])
                    cell = inspection.get("cells", inspection.get("inputs", {}).get(assertion["sheet"], {}))[assertion["cell"]]
                    actual = cell.get("current", cell).get("value")
                    expected = assertion["expected"]
                    numeric = all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in (actual, expected))
                    passed = abs(actual - expected) <= assertion.get("tolerance", 0) if numeric else type(actual) is type(expected) and actual == expected
                    report["assertions"].append({**assertion, "actual": actual, "passed": passed})
                report.update(status="PASS" if all(item["passed"] for item in report["assertions"]) else "FAIL",
                              native_receipt=str(native_path.relative_to(folder)), native_receipt_sha256=digest(native_path),
                              native_workbook=str(output.relative_to(folder)), native_workbook_sha256=digest(output),
                              completeness=after.get("completeness", {}), formula_errors=after.get("formula_errors", {}),
                              sensitivity_tables=native.get("sensitivity_tables", "NON_VERIFIEES"),
                              wacc_macro=native.get("wacc_macro", "NON_EXECUTEE"))
            except (ValueError, OSError, KeyError, TypeError) as exc:
                report["error"] = str(exc)
            reports.append(report)
        validation = {"schema": "tca-bp-maintenance-validation/1", "version_id": descriptor["version_id"],
                      "template_sha256": descriptor["template_sha256"], "schema_sha256": descriptor["schema_sha256"],
                      "proposal_sha256": descriptor["proposal"]["proposal_sha256"], "scenario_sha256": _fingerprint(scenarios),
                      "status": "PASS" if all(report["status"] == "PASS" for report in reports) else "FAIL",
                      "native_execution_required": True, "financial_results_verified": False,
                      "verified_scope": "Valeurs des oracles explicitement listés, dans les scénarios fictifs fournis.",
                      "executed_at": _now(), "scenarios": reports,
                      "report_path": str(run_folder / "validation.json")}
        atomic_json(run_folder / "scenarios.json", scenarios)
        atomic_json(run_folder / "validation.json", validation)
        return validation

    def approve(self, model_dir: str | Path, validation_path: str | Path, approved_by: str) -> dict:
        folder, descriptor, variant = self._version(model_dir)
        if not isinstance(approved_by, str) or len(approved_by.strip()) < 2:
            raise ValueError("Identifier le responsable ayant explicitement validé cette version.")
        report_path = Path(validation_path).resolve()
        if not report_path.is_relative_to(folder / "validation"):
            raise ValueError("La validation ne provient pas de cette version.")
        validation = json.loads(report_path.read_text(encoding="utf-8"))
        if (validation.get("status") != "PASS" or validation.get("version_id") != descriptor["version_id"]
                or validation.get("template_sha256") != descriptor["template_sha256"]
                or validation.get("schema_sha256") != descriptor["schema_sha256"]
                or validation.get("proposal_sha256") != descriptor["proposal"]["proposal_sha256"]
                or not validation.get("scenarios")):
            raise ValueError("Une validation native réussie de cette version précise est requise.")
        scenarios_path = report_path.with_name("scenarios.json")
        if not scenarios_path.resolve().is_relative_to(folder / "validation"):
            raise ValueError("Les scénarios sortent du périmètre de validation.")
        scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
        if (_fingerprint(scenarios) != validation.get("scenario_sha256")
                or not isinstance(scenarios, list) or len(scenarios) != len(validation["scenarios"])):
            raise ValueError("Les scénarios ont changé depuis leur validation.")
        covered = set()
        for specification, scenario in zip(scenarios, validation["scenarios"]):
            if scenario.get("status") != "PASS" or not scenario.get("assertions") or not all(a.get("passed") is True for a in scenario["assertions"]):
                raise ValueError("Toutes les attentes indépendantes doivent être vérifiées.")
            if (specification.get("fictional") is not True or specification.get("name") != scenario.get("name")
                    or len(specification.get("outputs", [])) != len(scenario["assertions"])):
                raise ValueError("Le rapport ne correspond pas aux scénarios originaux.")
            for path_key, hash_key in (("native_receipt", "native_receipt_sha256"), ("native_workbook", "native_workbook_sha256")):
                evidence = (folder / scenario[path_key]).resolve()
                if not evidence.is_relative_to(folder / "validation") or digest(evidence) != scenario[hash_key]:
                    raise ValueError("Une preuve native a changé depuis la validation.")
            output = (folder / scenario["native_workbook"]).resolve()
            receipt = json.loads((folder / scenario["native_receipt"]).read_text(encoding="utf-8-sig"))
            if (receipt.get("status") != "RECALCULE" or receipt.get("calculation_state") != 0
                    or receipt.get("output_sha256") != digest(output) or receipt.get("macros_enabled") is True):
                raise ValueError("La preuve native n'atteste pas le calcul de la copie vérifiée.")
            for expected, assertion in zip(specification["outputs"], scenario["assertions"]):
                if {k: v for k, v in assertion.items() if k not in ("actual", "passed")} != expected:
                    raise ValueError("Les attentes du rapport ont changé.")
                inspection = variant.inspect(output, expected["sheet"], [expected["cell"]])
                cell = inspection.get("cells", inspection.get("inputs", {}).get(expected["sheet"], {}))[expected["cell"]]
                actual, wanted = cell.get("current", cell).get("value"), expected["expected"]
                numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (actual, wanted))
                passed = abs(actual - wanted) <= expected.get("tolerance", 0) if numeric else type(actual) is type(wanted) and actual == wanted
                if not passed or actual != assertion.get("actual"):
                    raise ValueError("Une sortie relue ne satisfait pas l'attendu indépendant.")
                covered.add((expected["sheet"], expected["cell"]))
        if not {(c["sheet"], c["cell"]) for c in descriptor["proposal"]["changes"]} <= covered:
            raise ValueError("Une formule modifiée ne possède pas d'oracle vérifié.")
        publication = {"schema": "tca-bp-model-publication/1", "version_id": variant.model_id, "status": "PUBLIEE",
                       "model_dir": str(folder), "template_sha256": descriptor["template_sha256"],
                       "schema_sha256": descriptor["schema_sha256"], "approved_by": approved_by.strip(),
                       "approved_at": _now(), "validation_path": str(report_path), "validation_sha256": digest(report_path),
                       "source_model_id": descriptor["source_model_id"], "existing_cases_migrated": False,
                       "default_model_replaced": False}
        publication_path = folder / "publication.json"
        if publication_path.exists():
            raise ValueError("Cette version a déjà été publiée ; une publication ne peut pas être remplacée.")
        with publication_path.open("x", encoding="utf-8") as stream:
            json.dump(publication, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        return publication
