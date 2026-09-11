"""Rejouer trois scénarios fictifs réussis sur un candidat distinct.

Aucune migration : les sources sont lues comme preuves et restent inchangées.
Une invocation normale ouvre Excel ; coordonner son créneau avec les autres
recettes. --check contrôle les préconditions sans créer de stockage ni ouvrir Excel.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.storage import atomic_json, canonical, digest, uid
from tools.validate_workflows import financial_oracles


CASES = {"test_services": "services", "test_fabrication": "fabrication", "test_recherche": "recherche"}
ORACLE_COUNTS = {"services": 4, "fabrication": 6, "recherche": 5}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _source_path(source_dir: Path) -> Path:
    source = Path(source_dir).resolve()
    runtime = (ROOT / "runtime").resolve()
    if source.parent != runtime or not source.name.startswith("recette_") or not source.is_dir():
        raise ValueError("La source doit être un répertoire recette_* directement sous runtime/.")
    return source


def _file_in(folder: Path, path: str | Path) -> Path:
    candidate = (folder / path).resolve()
    if not candidate.is_relative_to(folder.resolve()) or not candidate.is_file():
        raise ValueError("Une preuve de recette est absente ou sort de son dossier fictif.")
    return candidate


def _source_cases(source: Path) -> tuple[dict, dict]:
    recipe = _read_json(_file_in(source, "recette.json"))
    if recipe.get("status") != "SUCCES" or recipe.get("native") is not True:
        raise ValueError("La recette source doit être SUCCES avec recalcul natif avant tout lancement.")
    if sorted(recipe.get("case_ids", [])) != sorted(CASES):
        raise ValueError("La recette doit contenir exactement les trois cas fictifs autorisés.")
    checks = recipe.get("checks")
    if not isinstance(checks, list) or not checks or not all(isinstance(c, dict) and c.get("passed") is True for c in checks):
        raise ValueError("Tous les contrôles de la recette source doivent avoir réussi.")
    oracles = [c.get("name", "") for c in checks if "_oracle_" in c.get("name", "")]
    if len(oracles) != 15 or len(set(oracles)) != 15:
        raise ValueError("Les quinze attentes financières distinctes doivent être réussies dans la recette source.")
    for key, count in ORACLE_COUNTS.items():
        if sum(name.startswith(key + "_oracle_") for name in oracles) != count:
            raise ValueError("Les attentes de la recette source ne couvrent pas les trois scénarios requis.")
    case_root = source / "dossiers"
    if case_root.resolve() != case_root or not case_root.resolve().is_relative_to(source):
        raise ValueError("Le répertoire des cas fictifs est redirigé hors de son emplacement autorisé.")
    if not case_root.is_dir() or {p.name for p in case_root.iterdir() if p.is_dir()} != set(CASES):
        raise ValueError("Le stockage source contient un dossier absent de la liste fictive autorisée.")
    result = {}
    for case_id, key in CASES.items():
        folder = (case_root / case_id).resolve()
        if folder.parent != case_root.resolve() or not folder.is_relative_to(source):
            raise ValueError("Un dossier fictif sort du stockage de la recette.")
        state_path = _file_in(folder, "etat_dossier.json")
        state = _read_json(state_path)
        if (state.get("id") != case_id or state.get("calculation_status") != "RECALCULE"
                or state.get("outputs_current") is not True):
            raise ValueError("L'état source doit identifier le cas fictif et un calcul courant.")
        workbook = _file_in(folder, state.get("workbook_path", ""))
        if digest(workbook) != state.get("sha256"):
            raise ValueError("Le classeur source ne correspond plus à son état de recette.")
        states = state.get("field_states")
        if not isinstance(states, dict) or not states:
            raise ValueError("Le cas fictif ne contient aucun état de saisie à rejouer.")
        updates = []
        for address, value in sorted(states.items()):
            if not isinstance(address, str) or "!" not in address or not isinstance(value, dict):
                raise ValueError("État de champ source invalide.")
            sheet, cell = address.rsplit("!", 1)
            status = value.get("status")
            if "value" not in value or status not in {"NON_RENSEIGNE", "HYPOTHESE", "CONFIRME"}:
                raise ValueError("Un état de module ou de calcul ne peut être rejoué comme saisie.")
            if (value["value"] is None) != (status == "NON_RENSEIGNE"):
                raise ValueError("La valeur et son état source sont incohérents.")
            updates.append({"sheet": sheet, "cell": cell, "value": value["value"], "status": status,
                            "replace_existing": True, "override_default": True,
                            "reason": "Rejeu fictif du scénario validé " + key + " pour contrôler le candidat distinct."})
        # Rejeter NaN/Infinity avant la création du moindre dossier de destination.
        canonical(updates)
        result[case_id] = {"key": key, "updates": updates, "state_sha256": digest(state_path),
                           "workbook_sha256": digest(workbook), "workbook_relative": workbook.relative_to(source).as_posix(),
                           "source_model_id": state.get("model_id")}
    return recipe, result


def _tree_hashes(folder: Path) -> dict:
    result = {}
    folder = folder.resolve()
    def visit(directory):
        for path in sorted(directory.iterdir()):
            # Vérifier la redirection avant de parcourir un sous-répertoire.
            if path.is_symlink() or path.resolve() != path or not path.resolve().is_relative_to(folder):
                raise ValueError("La recette contient une redirection de fichier hors périmètre.")
            if path.is_file():
                result[path.relative_to(folder).as_posix()] = digest(path)
            elif path.is_dir():
                visit(path)
    visit(folder)
    return result


def preflight(source_dir: Path, candidate_dir: Path) -> dict:
    source = _source_path(source_dir)
    recipe_sha = digest(source / "recette.json")
    recipe, cases = _source_cases(source)
    candidate = Path(candidate_dir).resolve()
    if candidate != (ROOT / "models" / "generic-v1-guards").resolve():
        raise ValueError("Cette recette vise uniquement le candidat distinct models/generic-v1-guards.")
    engine = ModelEngine(ROOT, model_dir=candidate)
    receipt = engine.ensure_built()
    default = ROOT / "models" / "generic-v1" / "TCA_BP_Trame_generique.xlsm"
    if candidate == default.parent.resolve() or engine.template_path.resolve() == default.resolve():
        raise ValueError("La recette ne peut utiliser ni remplacer le modèle par défaut.")
    source_hashes = _tree_hashes(source)
    if source_hashes.get("recette.json") != recipe_sha:
        raise ValueError("Le rapport de recette a changé pendant sa lecture.")
    # Confirmer que les états lus plus haut n'ont pas changé pendant l'inventaire.
    for case_id, case in cases.items():
        if source_hashes.get("dossiers/" + case_id + "/etat_dossier.json") != case["state_sha256"]:
            raise ValueError("La recette source a changé pendant sa lecture.")
        if source_hashes.get(case["workbook_relative"]) != case["workbook_sha256"]:
            raise ValueError("Un classeur source a changé pendant sa lecture.")
    return {"source_dir": source, "candidate_dir": candidate, "cases": cases,
            "source_tree_sha256": source_hashes, "recipe_sha256": recipe_sha,
            "candidate_template_sha256": receipt["template_sha256"],
            "candidate_schema_sha256": receipt["schema_sha256"], "candidate_model_id": engine.model_id,
            "default_template_sha256": digest(default), "engine": engine}


def _state_hash(state):
    return hashlib.sha256(canonical(state).encode("utf-8")).hexdigest()


def run(source_dir: Path, candidate_dir: Path, output_dir: Path | None = None, *, prepare_only=False) -> dict:
    context = preflight(source_dir, candidate_dir)
    source = context["source_dir"]
    runtime = (ROOT / "runtime").resolve()
    output = (Path(output_dir).resolve() if output_dir else runtime / ("validation_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uid()[:8]))
    if output.parent != runtime or not output.name.startswith("validation_") or output.exists():
        raise ValueError("La destination doit être un NOUVEAU répertoire validation_* directement sous runtime/.")
    output.mkdir(exist_ok=False)
    checks, cases = [], []
    report = {"schema": "tca-bp-candidate-validation/1", "status": "PREPARATION_EN_COURS", "native": False,
              "source_dir": str(source), "data_dir": str(output), "candidate_dir": str(context["candidate_dir"]),
              "candidate_model_id": context["candidate_model_id"], "recipe_sha256": context["recipe_sha256"],
              "candidate_template_sha256": context["candidate_template_sha256"],
              "candidate_schema_sha256": context["candidate_schema_sha256"],
              "default_template_sha256": context["default_template_sha256"],
              "source_tree_sha256": context["source_tree_sha256"], "checks": checks, "cases": cases,
              "original_cases_migrated": False, "default_model_replaced": False, "published": False,
              "financial_results_verified": False,
              "scope": "Rejeu des saisies des trois cas fictifs, compatibilité du candidat et quinze oracles financiers natifs. Aucune publication ni certification fiscale ou économique complète."}
    report_path = output / "validation.json"

    def check(name, condition, actual=None, expected=None):
        checks.append({"name": name, "passed": bool(condition), "actual": actual, "expected": expected})
        atomic_json(report_path, report)
        if not condition:
            raise AssertionError(name + ": " + repr(actual))

    try:
        app = Application(ROOT, output, engine=context["engine"])
        app.initialize()
        for case_id, source_case in context["cases"].items():
            key = source_case["key"]
            check(key + "_source_inchangee_avant_rejeu", _tree_hashes(source) == context["source_tree_sha256"])
            print("Rejeu fictif complet du candidat : " + key, flush=True)
            app.create_case("Validation fictive " + key, "Candidat — " + key, case_id=case_id)
            proof = app.add_source(case_id, text="RECETTE EXCLUSIVEMENT FICTIVE. Rejeu d'un scénario logiciel, aucun client réel.\n" + canonical({
                "source_recipe": source.name, "source_case": case_id, "source_state_sha256": source_case["state_sha256"],
                "source_workbook_sha256": source_case["workbook_sha256"], "updates": source_case["updates"]}),
                title="Scénario fictif validé — " + key)
            updates = [{**item, "evidence": proof["id"]} for item in source_case["updates"]]
            plan = app.prepare_changes(case_id, updates, "rejeu_complet_" + key)
            applied = app.apply_plan(case_id, plan["id"])
            check(key + "_un_seul_lot", applied["revision"] == 1 and len(applied["changes"]) == len(updates),
                  {"revision": applied["revision"], "changes": len(applied["changes"])}, {"revision": 1, "changes": len(updates)})
            state = app.get_case(case_id)
            case_report = {"id": case_id, "source_state_sha256": source_case["state_sha256"],
                           "source_workbook_sha256": source_case["workbook_sha256"], "field_count": len(updates),
                           "plan_id": plan["id"], "prepared_revision": state["revision"],
                           "prepared_workbook": str(Path(state["workbook_path"]).relative_to(output)),
                           "prepared_sha256": state["sha256"], "field_states_sha256": _state_hash(state["field_states"])}
            cases.append(case_report)
        check("source_complete_inchangee", _tree_hashes(source) == context["source_tree_sha256"])
        check("candidat_immuable", digest(context["engine"].template_path) == context["candidate_template_sha256"])
        check("manifeste_candidat_immuable", digest(context["candidate_dir"] / "modele.json") == context["candidate_schema_sha256"])
        check("modele_defaut_inchange", digest(ROOT / "models/generic-v1/TCA_BP_Trame_generique.xlsm") == context["default_template_sha256"])
        report["status"] = "PREPARE"
    except Exception as error:
        report.update(status="ECHEC", error=type(error).__name__ + ": " + str(error))
        atomic_json(report_path, report)
        raise
    preparation_path = output / "preparation.json"
    with preparation_path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
    report["preparation_sha256"] = digest(preparation_path)
    atomic_json(report_path, report)
    print(json.dumps({"status": "PREPARE", "native": False, "cases": len(cases), "data_dir": str(output), "report_path": str(report_path)}, ensure_ascii=False, indent=2), flush=True)
    return report if prepare_only else resume(output)


def _prepared_context(output):
    report = _read_json(_file_in(output, "validation.json"))
    preparation_path = _file_in(output, "preparation.json")
    if report.get("status") != "PREPARE" or report.get("native") is not False:
        raise ValueError("Seule une préparation complète, sans calcul commencé, peut être reprise. Un échec natif exige un nouveau rejeu contrôlé.")
    if report.get("schema") != "tca-bp-candidate-validation/1" or report.get("preparation_sha256") != digest(preparation_path):
        raise ValueError("Le manifeste de préparation a changé.")
    preparation = _read_json(preparation_path)
    if {k: v for k, v in report.items() if k != "preparation_sha256"} != preparation:
        raise ValueError("Le rapport ne correspond plus à la préparation figée.")
    if Path(report.get("data_dir", "")).resolve() != output:
        raise ValueError("Le manifeste de préparation appartient à un autre espace.")
    context = preflight(Path(report["source_dir"]), Path(report["candidate_dir"]))
    for key in ("source_tree_sha256", "recipe_sha256", "candidate_template_sha256", "candidate_schema_sha256", "candidate_model_id", "default_template_sha256"):
        if report.get(key) != context[key]:
            raise ValueError("Une preuve de départ a changé depuis la préparation : " + key)
    if {case.get("id") for case in report.get("cases", [])} != set(CASES) or len(report["cases"]) != 3:
        raise ValueError("La préparation ne contient pas exactement les trois cas autorisés.")
    app = Application(ROOT, output, engine=context["engine"])
    if {case["id"] for case in app.list_cases()} != set(CASES):
        raise ValueError("Le stockage préparé ne contient pas les trois cas attendus.")
    for case in report["cases"]:
        state = app.get_case(case["id"])
        workbook = _file_in(output, case["prepared_workbook"])
        if (state["revision"] != 1 or state["revision"] != case["prepared_revision"]
                or state["sha256"] != case["prepared_sha256"] or digest(workbook) != case["prepared_sha256"]
                or Path(state["workbook_path"]).resolve() != workbook
                or state["calculation_status"] != "A_RECALCULER" or state["outputs_current"]
                or _state_hash(state["field_states"]) != case["field_states_sha256"]):
            raise ValueError("Un cas préparé a changé : " + case["id"])
    return context, report, app


def resume(output_dir: Path) -> dict:
    """Reprendre les trois versions préparées exactes, jamais selon leur date."""
    output = Path(output_dir).resolve()
    if output.parent != (ROOT / "runtime").resolve() or not output.name.startswith("validation_") or not output.is_dir():
        raise ValueError("La reprise vise un espace validation_* existant directement sous runtime/.")
    lock = output / ".candidate-validation.lock"
    try:
        with lock.open("x", encoding="utf-8") as handle:
            handle.write(canonical({"pid": os.getpid(), "started_at": dt.datetime.now(dt.timezone.utc).isoformat()}))
    except FileExistsError as error:
        raise ValueError("Cet espace possède déjà un verrou de validation. Aucune suppression automatique.") from error
    try:
        context, report, app = _prepared_context(output)
        report.update(status="VALIDATION_EN_COURS", native=True)
        report_path = output / "validation.json"
        atomic_json(report_path, report)
        def check(name, condition, actual=None, expected=None):
            report["checks"].append({"name": name, "passed": bool(condition), "actual": actual, "expected": expected})
            atomic_json(report_path, report)
            if not condition:
                raise AssertionError(name + ": " + repr(actual))
        try:
            for case in report["cases"]:
                key = CASES[case["id"]]
                print("Recalcul Excel du candidat : " + key, flush=True)
                native = app.recalculate(case["id"])
                case["native"] = native
                check(key + "_native_inputs_unchanged", native.get("inputs_unchanged") is True)
                financial_oracles(key, native["workbook_path"], check)
                case["oracle_count"] = ORACLE_COUNTS[key]
            check("quinze_oracles_financiers", sum("_oracle_" in item["name"] for item in report["checks"]) == 15)
            check("source_complete_inchangee_apres_excel", _tree_hashes(context["source_dir"]) == context["source_tree_sha256"])
            check("candidat_immuable_apres_excel", digest(context["engine"].template_path) == context["candidate_template_sha256"])
            check("manifeste_candidat_immuable_apres_excel", digest(context["candidate_dir"] / "modele.json") == context["candidate_schema_sha256"])
            check("modele_defaut_inchange_apres_excel", digest(ROOT / "models/generic-v1/TCA_BP_Trame_generique.xlsm") == context["default_template_sha256"])
            report["status"] = "SUCCES"
        except Exception as error:
            report.update(status="ECHEC", error=type(error).__name__ + ": " + str(error))
            atomic_json(report_path, report)
            raise
        atomic_json(report_path, report)
        print(json.dumps({"status": report["status"], "oracles": 15, "data_dir": str(output), "report_path": str(report_path)}, ensure_ascii=False, indent=2))
        return report
    finally:
        lock.unlink(missing_ok=True)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--source-dir", type=Path)
    mode.add_argument("--resume", type=Path, help="Valider dans Excel les trois versions exactes d'une préparation PREPARE")
    parser.add_argument("--candidate-dir", type=Path, default=ROOT / "models/generic-v1-guards")
    parser.add_argument("--output-dir", type=Path, help="Destination nouvelle runtime/validation_* ; jamais une reprise")
    parser.add_argument("--check", action="store_true", help="Préconditions en lecture seule, sans stockage ni Excel")
    parser.add_argument("--prepare-only", action="store_true", help="Créer les trois lots contrôlés sans ouvrir Excel")
    args = parser.parse_args(argv)
    try:
        if args.resume:
            if args.check or args.prepare_only or args.output_dir:
                raise ValueError("--resume ne se combine pas avec --check, --prepare-only ou --output-dir.")
            resume(args.resume)
        elif args.check:
            result = preflight(args.source_dir, args.candidate_dir)
            print(json.dumps({"status": "PRET", "candidate_model_id": result["candidate_model_id"],
                              "candidate_template_sha256": result["candidate_template_sha256"],
                              "cases": {key: len(value["updates"]) for key, value in result["cases"].items()},
                              "source_files_verified": len(result["source_tree_sha256"])}, ensure_ascii=False, indent=2))
        else:
            run(args.source_dir, args.candidate_dir, args.output_dir, prepare_only=args.prepare_only)
        return 0
    except (ValueError, OSError, KeyError, TypeError, AssertionError) as error:
        print(json.dumps({"status": "REFUSE_OU_ECHEC", "reason": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
