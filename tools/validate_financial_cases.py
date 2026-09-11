"""Recette native depuis des événements fictifs et des oracles indépendants.

Chaque invocation crée des dossiers neufs sous runtime/recette_financiere_*.
--prepare-only n'ouvre pas Excel. --resume reprend uniquement les cas exacts
figés par cette préparation ; un échec natif exige une nouvelle campagne.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.storage import atomic_json, canonical, digest, uid
from tca_bp.vendor.input_engine import Workbook
from tools.financial_cases_common import common_updates, merge_updates
from tools import financial_cases_assets


def definitions(group="assets"):
    if group == "assets":
        return financial_cases_assets.cases(), financial_cases_assets.rejection_cases()
    if group == "operations":
        from tools import financial_cases_operations
        return financial_cases_operations.cases(), financial_cases_operations.rejection_cases()
    if group == "wacc":
        from tools import financial_cases_wacc
        return financial_cases_wacc.cases(), financial_cases_wacc.rejection_cases()
    if group == 'qualification':
        from tools import financial_cases_qualification
        return financial_cases_qualification.cases(), []
    raise ValueError("Groupe de recette inconnu.")


def oracle_results(read_value, oracles):
    if not oracles:
        raise ValueError("Un cas sans attente indépendante ne peut pas réussir.")
    results = []
    seen = set()
    for item in oracles:
        if item["id"] in seen:
            raise ValueError("Oracle dupliqué.")
        seen.add(item["id"])
        kind = item.get('expected_kind', 'number')
        if kind in {'boolean', 'text', 'excel_error'}:
            expected = item['expected']
            if ((kind == 'boolean' and not isinstance(expected, bool)) or
                    (kind != 'boolean' and not isinstance(expected, str)) or
                    (kind == 'excel_error' and expected not in {'#N/A', '#VALUE!', '#DIV/0!', '#REF!', '#NAME?', '#NUM!', '#NULL!'})):
                raise ValueError('Oracle typé invalide.')
            value = read_value(item['sheet'], item['cell'])
            results.append({**item, 'actual': value, 'passed': type(value) is type(expected) and value == expected})
            continue
        if kind != 'number':
            raise ValueError('Type d’oracle inconnu.')
        expected, tolerance = item["expected"], item.get("tolerance", 0.01)
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
               for x in (expected, tolerance)) or tolerance < 0:
            raise ValueError("Attente ou tolérance non numérique.")
        value = read_value(item["sheet"], item["cell"])
        numeric = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        results.append({**item, "actual": value if numeric or not isinstance(value, float) else repr(value),
                        "passed": numeric and abs(value - expected) <= tolerance})
    return results


def _folder(path, existing):
    folder = Path(path).resolve()
    if folder.parent != (ROOT / "runtime").resolve() or not folder.name.startswith("recette_financiere_"):
        raise ValueError("Répertoire de recette fictive requis directement sous runtime/.")
    if folder.exists() != existing:
        raise ValueError("La destination doit être nouvelle, ou une préparation existante en reprise.")
    return folder


def _load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _hash_object(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def prepare(model_dir, group="assets", selected=None):
    cases, rejected = definitions(group)
    if selected:
        requested = set(selected)
        if requested - {item["id"] for item in cases}:
            raise ValueError("Identifiant de cas inconnu.")
        cases = [item for item in cases if item["id"] in requested]
    if not cases or len({item["id"] for item in cases + rejected}) != len(cases + rejected):
        raise ValueError("Campagne vide ou identifiants dupliqués.")
    engine = ModelEngine(ROOT, model_dir=Path(model_dir).resolve())
    receipt = engine.ensure_built()
    folder = _folder(ROOT / "runtime" / ("recette_financiere_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uid()[:8]), False)
    folder.mkdir()
    report = {"schema": "tca-bp-financial-cases/1", "status": "PREPARATION_EN_COURS", "native": False,
              "data_dir": str(folder), "model_dir": str(engine.model_dir), "model_id": engine.model_id,
              "template_sha256": receipt["template_sha256"], "schema_sha256": receipt["schema_sha256"],
              "group": group, "fixtures_sha256": _hash_object({"cases": cases, "rejected": rejected}),
              "cases": [], "rejections": [], "financial_outputs_verified": False}
    app = Application(ROOT, folder, engine=engine)
    path = folder / "validation.json"
    atomic_json(path, report)
    try:
        for case in cases + rejected:
            case_id = case["id"]
            print("Préparation fictive : " + case_id, flush=True)
            state = app.create_case("Recette fictive " + case_id, case["title"], case_id=case_id)
            source = app.add_source(case_id, text="SCENARIO LOGICIEL ENTIEREMENT FICTIF. Aucun client réel.\n" + canonical(case),
                                    title="Événements fictifs indépendants")
            updates = merge_updates(common_updates(horizon=case.get('horizon', 3), start=case.get('start', '2026-01-01')), case["updates"])
            updates = [{**item, "reason": "Événements fictifs de la recette " + case_id, "evidence": source["id"],
                        "status": "NON_RENSEIGNE" if item["value"] is None else "CONFIRME",
                        "replace_existing": True, "override_default": True} for item in updates]
            if case in rejected:
                before = app.get_case(case_id)
                try:
                    app.prepare_changes(case_id, updates, "refus_" + case_id)
                except ValueError as error:
                    if not any(fragment in str(error) for fragment in case["expected_error_any"]):
                        raise AssertionError("Mauvais motif de refus : " + str(error)) from error
                    after = app.get_case(case_id)
                    unchanged = (after["sha256"] == before["sha256"] and after["revision"] == before["revision"]
                                 and not after["plans"] and digest(Path(after["workbook_path"])) == before["sha256"])
                    if not unchanged:
                        raise AssertionError("Un refus a changé le dossier.")
                    report["rejections"].append({"id": case_id, "passed": True, "reason": str(error), "version_unchanged": True})
                else:
                    raise AssertionError("Lot invalide accepté : " + case_id)
            else:
                plan = app.prepare_changes(case_id, updates, "creation_" + case_id)
                app.apply_plan(case_id, plan["id"])
                replay = app.apply_plan(case_id, plan["id"])
                if replay["status"] != "DEJA_APPLIQUE":
                    raise AssertionError("Le rejeu a créé une seconde écriture.")
                state = app.get_case(case_id)
                report["cases"].append({"id": case_id, "definition": case, "prepared_revision": state["revision"],
                                        "prepared_sha256": state["sha256"], "prepared_path": state["workbook_path"],
                                        "field_states_sha256": _hash_object(state["field_states"]),
                                        "source_id": source["id"], "source_sha256": source["sha256"], "replay_verified": True})
            atomic_json(path, report)
        if digest(engine.template_path) != report["template_sha256"]:
            raise AssertionError("La trame a changé.")
        report["status"] = "PREPARE"
        with (folder / "preparation.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        report["preparation_sha256"] = digest(folder / "preparation.json")
    except Exception as error:
        report.update(status="ECHEC_PREPARATION", error=type(error).__name__ + ": " + str(error))
        atomic_json(path, report)
        raise
    atomic_json(path, report)
    print(canonical({"status": report["status"], "folder": str(folder), "cases": len(report["cases"])}), flush=True)
    return folder


def resume(folder):
    folder = _folder(folder, True)
    report = _load(folder / "validation.json")
    expected = _load(folder / "preparation.json")
    if (report.get("status") != "PREPARE" or report.get("native") is not False
            or report.get("preparation_sha256") != digest(folder / "preparation.json")
            or {k: v for k, v in report.items() if k != "preparation_sha256"} != expected
            or report["data_dir"] != str(folder)):
        raise ValueError("La préparation a changé ou son calcul a déjà commencé.")
    engine = ModelEngine(ROOT, model_dir=Path(report["model_dir"]))
    receipt = engine.ensure_built()
    if any(report[k] != receipt[k] for k in ("template_sha256", "schema_sha256", "model_id")):
        raise ValueError("Version modèle différente de la préparation.")
    app = Application(ROOT, folder, engine=engine)
    legacy_bindings = []
    for case in report["cases"]:
        state = app.get_case(case["id"])
        if (state["revision"] != case["prepared_revision"] or state["sha256"] != case["prepared_sha256"]
                or state["workbook_path"] != case["prepared_path"] or state["outputs_current"]
                or digest(Path(state["workbook_path"])) != case["prepared_sha256"]
                or _hash_object(state["field_states"]) != case["field_states_sha256"]):
            raise ValueError("Le dossier préparé a changé : " + case["id"])
        if hasattr(app, 'bind_legacy_case') and not state.get('model_ref'):
            # Préparation créée par la version antérieure du logiciel. Son
            # modèle et v0000 sont désignés par les preuves figées ci-dessus.
            # Le rattachement ne change ni le classeur ni sa révision.
            binding = app.bind_legacy_case(case['id'], Path(report['model_dir']))
            legacy_bindings.append({'case_id': case['id'], 'result': binding})
        # La source exacte appartient à ce dossier ; son hash fait partie du plan.
        source = app.source_text(case["id"], case["source_id"])
        if source["sha256"] != case["source_sha256"]:
            raise ValueError("Source de scénario modifiée.")
    lock = folder / ".native-financial.lock"
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(canonical({"pid": os.getpid(), "started_at": dt.datetime.now(dt.timezone.utc).isoformat()}))
    report.update(status="CALCUL_EN_COURS", native=True, legacy_bindings=legacy_bindings)
    path = folder / "validation.json"
    try:
        atomic_json(path, report)
        for case in report["cases"]:
            print("Recalcul Excel : " + case["id"], flush=True)
            native = app.recalculate(case["id"])
            case["native"] = native
            if not native.get("inputs_unchanged") or not native.get("model_verified"):
                raise AssertionError("Recalcul sans contrôle des entrées et du modèle.")
            wb = Workbook(Path(native["workbook_path"]))
            try:
                case["oracles"] = oracle_results(wb.value, case["definition"]["oracles"])
            finally:
                wb.close()
            case["passed"] = all(item["passed"] for item in case["oracles"])
            atomic_json(path, report)
            print(canonical({"id": case["id"], "passed": case["passed"], "oracles": len(case["oracles"]),
                             "failures": [item for item in case["oracles"] if not item["passed"]]}), flush=True)
        if digest(engine.template_path) != report["template_sha256"]:
            raise AssertionError("Le modèle a changé pendant la recette.")
        report["status"] = "SUCCES" if all(case["passed"] for case in report["cases"]) else "ECHEC_ORACLES"
    except Exception as error:
        report.update(status="ECHEC_EXECUTION", error=type(error).__name__ + ": " + str(error))
        atomic_json(path, report)
        raise
    finally:
        lock.unlink(missing_ok=True)
    atomic_json(path, report)
    return report


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--group", choices=("assets", "operations", "wacc", "qualification"), default="assets")
    parser.add_argument("--case", action="append")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args(argv)
    if args.resume:
        result = resume(args.resume)
    else:
        if not args.model_dir:
            parser.error("--model-dir est obligatoire pour une nouvelle campagne")
        folder = prepare(args.model_dir, args.group, args.case)
        result = {"status": "PREPARE"} if args.prepare_only else resume(folder)
    print(canonical({"status": result["status"]}), flush=True)
    return 0 if result["status"] in {"PREPARE", "SUCCES"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
