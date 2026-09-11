"""Recette indépendante sur trois dossiers fictifs, toujours dans un nouvel espace.

Les attentes sont calculées depuis les événements métier, jamais copiées des
formules Excel. Les résultats détaillés restent dans runtime/, hors de Git.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tca_bp.service import Application
from tca_bp.storage import atomic_json, digest, uid
from tca_bp.vendor.input_engine import Workbook


def financial_oracles(key, path, check):
    """Lire les caches de la copie dont Excel et le service ont vérifié l'identité.

    Les événements de recette ci-dessous constituent les attentes ; aucune
    formule du classeur ne sert à produire le résultat attendu.
    """
    expectations = {
        "services": [("Revenue", "E282", 1 * 120000), ("COGS", "E253", 0),
                     ("Effectifs", "E162", 60000 * 1.4 * 9 / 12),
                     ("Effectifs", "F162", 60000 * 1.4)],
        "fabrication": [("Revenue", "E282", 100 * 200), ("COGS", "E253", 100 * 80),
                        ("CAPEX", "P77", 12000), ("CAPEX", "P75", 12000 / 3),
                        ("CAPEX", "Q77", 0), ("CAPEX", "P81", 0)],
        "recherche": [("Financement Dette", "M43", 120000 / 2),
                      ("Financement Dette", "N43", 120000 / 2),
                      ("Financement Dette", "O43", 0), ("Financement Dette", "M86", 0),
                      ("Modèle financier", "C290", 50000)],
    }
    workbook = Workbook(Path(path))
    try:
        for sheet, cell, expected in expectations[key]:
            value = workbook.value(sheet, cell)
            check(key + "_oracle_" + sheet + "_" + cell,
                  isinstance(value, (float, int)) and not isinstance(value, bool) and abs(value - expected) < 0.01,
                  value, expected)
    finally:
        workbook.close()


def run(native=False, resume_dir=None):
    folder = Path(resume_dir).resolve() if resume_dir else ROOT / "runtime" / ("recette_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    if not folder.resolve().is_relative_to((ROOT / "runtime").resolve()) or not folder.name.startswith("recette_"):
        raise ValueError("La recette utilise exclusivement un répertoire recette_* sous runtime/.")
    if resume_dir and (folder / "recette.json").is_file():
        snapshot = folder / ("tentative_precedente_" + uid()[:8] + ".json")
        with snapshot.open("xb") as stream:
            stream.write((folder / "recette.json").read_bytes())
    app = Application(ROOT, folder)
    app.initialize()
    checks = []

    def check(name, condition, actual=None, expected=None):
        checks.append({"name": name, "passed": bool(condition), "actual": actual, "expected": expected})
        atomic_json(folder / "recette.json", {"checks": checks, "status": "EN_COURS" if condition else "ECHEC"})
        if not condition:
            atomic_json(folder / "recette.json", {"checks": checks, "status": "ECHEC"})
            raise AssertionError(name + ": " + repr(actual))

    def batch(case, source, values, label):
        print("Saisie contrôlée : " + label, flush=True)
        updates = [{"sheet": sheet, "cell": cell, "value": value, "reason": "Jeu fictif de recette : " + label,
                    "evidence": source, "status": "NON_RENSEIGNE" if value is None else "CONFIRME",
                    "replace_existing": True, "override_default": True} for sheet, cell, value in values]
        plan = app.prepare_changes(case, updates, "req_" + label)
        result = app.apply_plan(case, plan["id"])
        replay = app.apply_plan(case, plan["id"])
        check(label + "_rejeu_sans_doublon", replay["status"] == "DEJA_APPLIQUE")
        return result

    def record(case, source, sheet, values, label):
        print("Ligne de registre : " + label, flush=True)
        plan = app.prepare_record(case, sheet, values, source, "record_" + label)
        check(label + "_plan", plan["status"] in {"PRET_A_APPLIQUER", "DEJA_APPLIQUE"}, plan.get("questions", []), "PRET_A_APPLIQUER ou DEJA_APPLIQUE")
        result = app.apply_plan(case, plan["id"])
        repeated = app.prepare_record(case, sheet, values, source, "other_" + label)
        check(label + "_doublon_metier", repeated["status"] == "DEJA_APPLIQUE")
        return result

    cases = []
    existing = {case["id"] for case in app.list_cases()} if resume_dir else set()
    template_hash = digest(app.engine.template_path)
    for key, name in (("services", "Services fictifs"), ("fabrication", "Fabrication fictive"), ("recherche", "Recherche fictive")):
        case = app.get_case("test_" + key) if "test_" + key in existing else app.create_case("Recette " + key, name, case_id="test_" + key)
        case_id = case["id"]; cases.append(case_id)
        source = case["sources"][0] if case["sources"] else app.add_source(case_id, text="RECETTE FICTIVE. Les montants et qualifications de ce scénario sont inventés exclusivement pour vérifier le logiciel. Aucun client réel.", title="Hypothèses fictives de recette")
        context = app.engine.context(Path(case["folder"]) / "versions" / "v0000.xlsm")
        check(key + "_registres_vides", all(not r["occupied_rows"] for r in context["registers"].values()))
        common = [("Control", "C59", 3), ("Assumptions", "D4", 0), ("Assumptions", "D5", 0), ("Assumptions", "D7", 0),
                  ("Assumptions", "D66", 0), ("Assumptions", "D126", 100000), ("Assumptions", "D83", 0),
                  ("Control", "C28", 0), ("Control", "C29", 0), ("Control", "C30", 0), ("Control", "C31", 0), ("Control", "C32", 0),
                  ("Stock", "E10", 0), ("Stock", "E11", 0)]
        batch(case_id, source["id"], common, key + "_cadre")
        if key in ("services", "fabrication"):
            common_offer = [("Assumptions", "C15", 1), ("Assumptions", "D15", "forfait" if key == "services" else "unité"),
                            ("Assumptions", "E15", "Oui"), ("Assumptions", "F15", 1 if key == "services" else 200),
                            ("Assumptions", "K15", 0), ("Assumptions", "L15", 0), ("Assumptions", "M15", 0),
                            ("Assumptions", "P15", 0), ("Assumptions", "Q15", 0), ("Assumptions", "R15", 0),
                            ("Assumptions", "U15", 0), ("Assumptions", "V15", 0), ("Assumptions", "W15", 0),
                            ("Assumptions", "X15", 0), ("Assumptions", "Y15", 0), ("Assumptions", "Z15", 1),
                            ("DATA COGS", "D15", "Manuel"), ("DATA COGS", "L15", 0 if key == "services" else 80)]
            batch(case_id, source["id"], common_offer, key + "_offre")
            values = {"contract_client": "Client fictif " + key, "contract_offer": "Offre 01",
                      "contract_quantity": 1 if key == "services" else 100, "contract_unit_price": 120000 if key == "services" else 200,
                      "contract_start": "2026-01-01", "contract_end": "2026-03-31", "contract_recognition": "Etalee sur la duree",
                      "contract_invoicing": "Au fil de l'eau", "contract_status": "Signe", "contract_weight": 1,
                      "contract_deposit_rate": 0, "contract_milestone_rate": 0, "contract_vat_regime": "Exonéré / hors champ", "contract_vat_rate": 0}
            record(case_id, source["id"], "DATA Contrats", values, key + "_contrat")
        if key == "services":
            record(case_id, source["id"], "Effectifs", {
                "employee_position": "Consultant fictif", "employee_department": "Operations", "employee_analytic": "G&A",
                "employee_rnd_share": 0, "employee_start": "2026-04-01", "employee_fte": 1,
                "employee_salary": 60000, "employee_charges": 0.4, "employee_status": "Recrute"}, "services_rh")
        if key == "fabrication":
            record(case_id, source["id"], "DATA CAPEX", {
                "data_capex_b13_b72": "Machine fictive", "data_capex_c13_c72": "Machines-outils et équipements d'atelier",
                "data_capex_d13_d72": 12000, "data_capex_e13_e72": "2026-01-01", "data_capex_g13_g72": "Non", "data_capex_i13_i72": "Cash",
                **{field: {"value": value, "status": "CONFIRME", "override_default": True,
                           "reason": "Hypothèse fictive de recette explicitement fixée pour la machine testée."}
                   for field, value in {"data_capex_f13_f72": 3, "data_capex_h13_h72": 0,
                       "data_capex_m13_m72": "Corporelle", "data_capex_n13_n72": "Non", "data_capex_o13_o72": "Non"}.items()}}, "fabrication_capex")
        if key == "recherche":
            record(case_id, source["id"], "Financement Dette", {
                "financement_dette_b3_b42": "Prêt fictif", "financement_dette_c3_c42": 120000,
                "financement_dette_d3_d42": 0, "financement_dette_e3_e42": 2,
                "financement_dette_f3_f42": "Amortissement constant", "financement_dette_h3_h42": 0,
                "financement_dette_i3_i42": "2026-01-01", "financement_dette_j3_j42": "Pret bancaire"}, "recherche_dette")
            record(case_id, source["id"], "DATA Financement", {
                "data_financement_b14_b413": "Apport fictif", "data_financement_c14_c413": "FOUNDER",
                "data_financement_d14_d413": 50000, "data_financement_e14_e413": "2026-01-01",
                "data_financement_g14_g413": 0}, "recherche_equity")
        state = app.get_case(case_id)
        if state["outputs_current"]:
            check(key + "_reprise_calcul_exact", state["integrity"] == "CONFORME")
        else:
            check(key + "_cache_invalide", state["calculation_status"] == "A_RECALCULER" and not state["outputs_current"])
        report = Path(app.export_report(case_id)).read_text(encoding="utf-8")
        for other in ("services", "fabrication", "recherche"):
            if other != key:
                check(key + "_isolation_" + other, "Client fictif " + other not in report)
        if native:
            print("Recalcul Excel : " + key, flush=True)
            if state["outputs_current"]:
                native_result = next(e["details"] for e in state["history"] if e["kind"] == "RECALCUL_EXCEL" and e["details"]["output_sha256"] == state["sha256"])
                native_result = {**native_result, "workbook_path": state["workbook_path"]}
            else:
                native_result = app.recalculate(case_id)
            check(key + "_native_inputs_unchanged", native_result["inputs_unchanged"])
            financial_oracles(key, native_result["workbook_path"], check)
    check("template_immutable", digest(app.engine.template_path) == template_hash)
    app2 = Application(ROOT, folder)
    check("reprise_trois_dossiers", len(app2.list_cases()) == 3)
    result = {"status": "SUCCES", "native": native, "checks": checks, "case_ids": cases, "data_dir": str(folder),
              "scope": "Isolation, reprise, preuves, lignes de registres, cache invalidé ; si Excel demandé, oracles de CA, coûts, RH, CAPEX cash/amortissement, dette et apport. Ce n'est pas une certification fiscale ou économique complète."}
    atomic_json(folder / "recette.json", result)
    print(json.dumps({"status": result["status"], "checks": len(checks), "data_dir": str(folder)}, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(); p.add_argument("--native", action="store_true")
    p.add_argument("--resume-dir", type=Path, help="Reprendre exclusivement une recette fictive sous runtime/ ; les lots sont rejoués de manière idempotente")
    args = p.parse_args()
    run(args.native, args.resume_dir)
