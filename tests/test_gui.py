"""Contrat de saisie et parcours Tk cachés, sans classeur ni Excel."""

import copy
import threading
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from tca_bp.gui import (BPWindow, describe_native_receipt, describe_sheet, display_cell, expand_cells, parse_value,
                        plan_is_ready, preview_changes, smoke_test, snapshot_cells)


class PresentationTests(unittest.TestCase):
    def test_french_numbers_percent_and_explicit_zero(self):
        self.assertEqual(parse_value("1\u202f250,50 €", {"kind": "number"}), 1250.5)
        self.assertEqual(parse_value("4 %", {"kind": "number"}), .04)
        self.assertEqual(parse_value("0", {"kind": "integer"}), 0)
        self.assertEqual(parse_value("4", {"kind": "percent"}), 4)

    def test_unknown_is_not_zero_and_nonfinite_is_refused(self):
        for raw in ("", "NaN", "Infinity", "-Infinity", "pas connu"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_value(raw, {"kind": "number"})
        with self.assertRaises(ValueError):
            parse_value("1,5", {"kind": "integer"})

    def test_dates_and_choices(self):
        self.assertEqual(parse_value("29/02/2028", {"kind": "date"}), "2028-02-29")
        self.assertEqual(parse_value("2027-01-01", {"kind": "date"}), "2027-01-01")
        with self.assertRaises(ValueError):
            parse_value("29/02/2027", {"kind": "date"})
        choices = {"choices": [{"label": "Confirmée", "value": "CONFIRME"}]}
        self.assertEqual(parse_value("Confirmée", choices), "CONFIRME")
        with self.assertRaises(ValueError):
            parse_value("inventé", choices)

    def test_excel_current_dates_require_explicit_calendar(self):
        self.assertEqual(display_cell(46023, "date", False), "01/01/2026")
        self.assertEqual(display_cell(44561, "date", True), "01/01/2026")
        self.assertEqual(display_cell(46023, "date", None), "46023")
        self.assertEqual(display_cell(46023, "number", False), "46023")

    def test_cell_scopes_and_nested_inspection_preserve_zero_and_formula(self):
        self.assertEqual(expand_cells(["$B$3:C4", "C4"]), ["B3", "C3", "B4", "C4"])
        self.assertEqual(expand_cells(["A1:ZZ999999", "oops"]), [])
        raw = {"inputs": {"Control": {"C59": {"kind": "integer", "current": {"value": 0, "formula": None}}}}}
        self.assertEqual(snapshot_cells(raw)["C59"]["value"], 0)
        self.assertEqual(snapshot_cells(raw)["C59"]["kind"], "integer")
        self.assertEqual(snapshot_cells({"cells": {"C1": {"current": {"value": None, "formula": "SUM(A1:B1)"}}}})["C1"]["formula"], "SUM(A1:B1)")

    def test_only_current_ready_proposal_is_applicable(self):
        base = {"id": "p1", "changes": [{"cell": "C59", "value": 6}]}
        self.assertTrue(plan_is_ready({**base, "status": "PRET_A_APPLIQUER"}))
        for status in ("NEEDS_INPUT", "A_COMPLETER", "DEJA_APPLIQUE", "APPLIQUE", "REFUSED", "inventé"):
            self.assertFalse(plan_is_ready({**base, "status": status}))
        self.assertFalse(plan_is_ready({**base, "status": "PRET_A_APPLIQUER", "questions": ["Préciser"]}))
        self.assertFalse(plan_is_ready({**base, "status": "PRET_A_APPLIQUER", "id": None}))

    def test_preview_uses_engine_snapshot_not_guessed_empty(self):
        changes = [{"sheet": "Control", "cell": "C59", "value": 6}]
        plan = {"changes": changes, "engine_plan": {"changes": [{**changes[0], "expected": {"value": 8, "formula": None}}]}}
        self.assertEqual(preview_changes(plan)[0]["before_display"], "8")
        plan["engine_plan"]["changes"][0]["expected"] = {"value": 42, "formula": "A1+B1"}
        self.assertEqual(preview_changes(plan)[0]["before_display"], "Défaut calculé : A1+B1")
        self.assertEqual(preview_changes({"changes": changes})[0]["before_display"], "Non fourni par le moteur")

    def test_sheet_fiche_shows_business_context(self):
        info = {"role": "Qualifier les offres.", "dependencies": ["Control"], "questions": ["Quel prix ?"], "model_id": "private-technical-id", "workbook": "C:/private/technical/template.xlsm"}
        text = describe_sheet(info)
        self.assertIn("Rôle de la feuille", text)
        self.assertIn("Quel prix ?", text)
        self.assertNotIn("private-technical", text)

    def test_native_receipt_keeps_small_residual_and_local_scope_explicit(self):
        text = describe_native_receipt({"status": "CONVERGENCE_LOCALE", "candidate": .125, "residual": 8e-11, "evaluations": 9, "global_uniqueness_proven": False, "macros_enabled": False})
        self.assertIn("12,5 %", text)
        self.assertIn("8.000e-11", text)
        self.assertIn("unicité globale", text)
        self.assertIn("Macros activées : Non", text)
        self.assertNotIn("Classeur :", text)
        self.assertNotIn("vérifiée", describe_native_receipt({"status": "NON_ADOPTE"}).lower())


class FakeService:
    def __init__(self):
        self.worker_threads = []
        self.records = []
        self.agent_cases = []
        self.explanation_cases = []
        self.bindings = []
        self.declarations = []
        self.qualification_cases = []
        self.native_calls = []
        self.case = {"id": "cas", "name": "Prévisionnel", "client_name": "Client fictif", "revision": 0,
                     "calculation_status": "A_RECALCULER", "sources": [], "history": [], "questions": [],
                     "field_states": {}, "notice": "Données à qualifier."}

    def fields(self, case_id, sheet):
        self.worker_threads.append(threading.get_ident())
        return [{"id": "montant", "sheet": sheet, "label": "Montant", "kind": "number", "cells": ["C3", "C4"], "constraints": {"minimum": 0}}]

    def inspect(self, case_id, sheet):
        return {"cells": {"C3": {"current": {"value": 17, "formula": None}}, "C4": {"current": {"value": None, "formula": None}}}}

    def agents(self, case_id=None):
        self.agent_cases.append(case_id)
        return [{"id": "control", "sheet": "Control"}]

    def sheet_info(self, sheet, case_id=None):
        self.explanation_cases.append((sheet, case_id))
        return {"role": "Décrire les lignes de financement."}

    def bind_legacy_case(self, case_id, model_dir):
        self.worker_threads.append(threading.get_ident())
        self.bindings.append((case_id, model_dir))
        self.case.update(model_ref="a" * 64, model_status="VERSION_EXACTE_DISPONIBLE", model_notice="Version d'origine conservée.")
        return self.get_case(case_id)

    def declare_qualification(self, case_id, declaration):
        self.worker_threads.append(threading.get_ident())
        self.declarations.append((case_id, copy.deepcopy(declaration)))
        return declaration

    def qualifications(self, case_id):
        self.qualification_cases.append(case_id)
        return {"scopes": {"DCF": {"status": "HYPOTHESES_A_CONFIRMER", "scenario_ready": True, "available": False, "blockers": [], "hypotheses": [{"field": "BFR_TERMINAL", "message": "Traitement terminal à confirmer."}]}}}

    def solve_wacc(self, case_id, timeout=600):
        self.worker_threads.append(threading.get_ident())
        self.native_calls.append(("wacc", case_id, timeout))
        self.case["revision"] += 1
        return {"status": "CONVERGENCE_LOCALE", "candidate": .12, "residual": 1e-11, "revision": self.case["revision"], "workbook_path": "fixture-wacc.xlsm", "report_path": "fixture-wacc.json", "global_uniqueness_proven": False}

    def verify_sensitivity(self, case_id, timeout=3600):
        self.worker_threads.append(threading.get_ident())
        self.native_calls.append(("sensitivity", case_id, timeout))
        self.case["revision"] += 1
        return {"status": "TABLES_VERIFIEES", "revision": self.case["revision"], "report_path": "fixture-tables.json", "comparisons": [{"passed": True}, {"passed": True}], "financial_model_globally_validated": False}

    def get_case(self, case_id):
        return copy.deepcopy(self.case)

    def prepare_record(self, case_id, sheet, values, evidence_id):
        self.records.append((case_id, sheet, values, evidence_id))
        return {"status": "A_COMPLETER", "changes": [], "questions": [{"question": "Quelle date ?"}]}

    def route(self, case_id, text):
        self.case["questions"].append({"id": "q1", "question": "Quelle date ?", "status": "OUVERTE", "topic": "Control"})
        return {"message": "Renseignons le calendrier.", "sheets": ["Control"], "questions": ["Quelle date ?"]}


class NativeWindowTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.service = FakeService()
        self.window = BPWindow(self.root, self.service, start=False)
        self.errors = []
        self.window._error = lambda action, error: self.errors.append((action, str(error)))
        self.window.agent_rows = [{"id": "control", "sheet": "Control"}]
        self.window.agent_combo["values"] = ["01 · Control"]
        self.window.agent_combo.current(0)
        self.window._render_case(self.service.get_case("cas"))

    def settle(self):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.root.update()
            if not self.window.busy and self.window.events.empty():
                self.root.update()
                return
            time.sleep(.01)
        self.fail("Opération de service non terminée")

    def tearDown(self):
        self.settle()
        self.window.close()

    def select_field(self):
        self.window.load_sheet()
        self.settle()
        self.window.fields_tree.selection_set("montant")
        self.window._field_selected()
        self.window.reason_var.set("Hypothèse fournie dans le dossier.")

    def test_required_source_then_batch_preserves_confirmed_zero(self):
        self.select_field()
        self.window.value_var.set("0")
        self.window.add_pending()
        self.assertFalse(self.window.pending)
        self.assertIn("Ajoutez d'abord", self.errors[-1][1])
        self.service.case["sources"] = [{"id": "p1", "title": "Réponse datée"}]
        self.window._render_case(self.service.get_case("cas"))
        self.window.input_status.set("Confirmé")
        self.window.add_pending()
        update = self.window.pending[0]
        self.assertEqual((update["value"], update["status"], update["evidence"], update["cell"]), (0, "CONFIRME", "p1", "C3"))
        self.window.mode_var.set("record")
        self.window._mode_changed()
        self.assertEqual(self.window.mode_var.get(), "update")
        self.assertEqual(len(self.window.pending), 1)

    def test_record_keeps_field_identifier_evidence_and_status(self):
        self.service.case["sources"] = [{"id": "p1", "title": "Pièce"}]
        self.window._render_case(self.service.get_case("cas"))
        self.select_field()
        self.window.mode_var.set("record")
        self.window._mode_changed()
        self.window.value_var.set("0")
        self.window.input_status.set("Confirmé")
        self.window.add_pending()
        self.window.prepare()
        self.settle()
        case_id, sheet, values, source_id = self.service.records[0]
        self.assertEqual((case_id, sheet, source_id), ("cas", "Control", "p1"))
        self.assertEqual(values["montant"]["value"], 0)
        self.assertEqual(values["montant"]["status"], "CONFIRME")
        self.assertNotIn("cell", values["montant"])
        self.assertEqual(str(self.window.apply_button["state"]), "disabled")
        self.assertEqual(self.window.plan_dialog.state(), "withdrawn")
        self.assertFalse(self.errors)

    def test_service_runs_off_main_thread_and_current_value_is_shown(self):
        self.select_field()
        self.assertIn("17", self.window.current_var.get())
        self.assertTrue(self.service.worker_threads)
        self.assertTrue(all(t != threading.get_ident() for t in self.service.worker_threads))
        self.assertFalse(self.errors)

    def test_agents_and_explanations_follow_selected_case_version(self):
        self.window.refresh_case()
        self.settle()
        self.assertEqual(self.service.agent_cases[-1], "cas")
        self.select_field()
        self.assertEqual(self.service.explanation_cases[-1], ("Control", "cas"))
        with patch.object(self.window, "_detail_dialog") as detail:
            self.window.show_sheet_info()
            self.settle()
            self.assertEqual(self.service.explanation_cases[-1], ("Control", "cas"))
            detail.assert_called_once()

    def test_explicit_legacy_binding_preserves_revision_and_displays_exact_reference(self):
        self.service.case.update(model_status="VERSION_NON_EPINGLEE", model_ref=None)
        self.window._render_case(self.service.get_case("cas"))
        self.window.bind_legacy_model()
        self.assertFalse(self.service.bindings)
        self.assertEqual(self.window.model_bind_dialog.state(), "withdrawn")
        self.window.model_dir_var.set("fictitious-old-model")
        self.window.model_bind_button.invoke()
        self.settle()
        self.assertEqual(self.service.bindings, [("cas", Path("fictitious-old-model"))])
        self.assertEqual(self.window.case["revision"], 0)
        self.assertEqual(self.window.model_reference.get(), "a" * 64)
        self.assertIn("Archive exacte", self.window.model_status.get())
        self.assertEqual(str(self.window.bind_model_button["state"]), "disabled")
        self.assertFalse(self.errors)

    def test_unavailable_model_does_not_substitute_default_agents(self):
        self.service.case.update(model_status="VERSION_INDISPONIBLE_OU_MODIFIEE", model_ref="a" * 64)
        self.window.refresh_case()
        self.settle()
        self.assertFalse(self.service.agent_cases)
        self.assertFalse(self.window.agent_rows)
        self.assertIn("Archive absente", self.window.model_status.get())

    def test_missing_default_still_lists_existing_dossiers(self):
        self.service.list_cases = lambda: [self.service.get_case("cas")]
        self.service.initialize = lambda: (_ for _ in ()).throw(ValueError("Référence absente"))
        self.window.initialize()
        self.settle()
        self.assertIn("cas", self.window.case_rows)
        self.assertFalse(self.errors)
        self.assertIn("dossiers archivés", self.window.status.get())

    def test_qualification_declaration_requires_source_and_never_calls_cell_mutation(self):
        self.window.qual_module.set("Investissements")
        self.window.qual_state.set("Inactif")
        self.window.qual_status.set("Confirmé")
        self.window.qual_reason.set("Aucun investissement prévu selon le porteur.")
        self.window.declare_qualification()
        self.assertFalse(self.service.declarations)
        self.assertIn("Ajoutez d'abord", self.errors[-1][1])
        self.service.case["sources"] = [{"id": "p1", "title": "Déclaration datée"}]
        self.window._render_case(self.service.get_case("cas"))
        self.window.declare_qualification()
        self.settle()
        self.assertEqual(self.service.declarations[0], ("cas", {"module": "DATA CAPEX", "state": "INACTIF", "status": "CONFIRME", "evidence": "p1", "reason": "Aucun investissement prévu selon le porteur."}))
        self.assertFalse(self.service.records)
        self.assertFalse(self.window.pending)
        self.assertEqual(self.service.qualification_cases, ["cas"])
        row = self.window.qualification_tree.item(self.window.qualification_tree.get_children()[0], "values")
        self.assertEqual(row[-2:], ("Prêt", "Non disponibles"))
        self.assertIn("terminal à confirmer", self.window.qualification_text.get("1.0", "end"))

    def test_fiscal_declaration_requires_jurisdiction_dates_and_formats_iso(self):
        self.service.case["sources"] = [{"id": "p1", "title": "Règles applicables documentées"}]
        self.window._render_case(self.service.get_case("cas"))
        self.window.qual_module.set("Règles fiscales")
        self.window._qualification_module_changed()
        self.window.qual_reason.set("Règles fiscales identifiées dans la pièce.")
        self.window.declare_qualification()
        self.assertFalse(self.service.declarations)
        self.assertIn("juridiction", self.errors[-1][1])
        self.window.qual_jurisdiction.set("Juridiction fictive")
        self.window.qual_valid_from.set("01/01/2027")
        self.window.qual_valid_to.set("2029-12-31")
        self.window.declare_qualification()
        self.settle()
        self.assertEqual(self.service.declarations[0][1]["valid_from"], "2027-01-01")
        self.assertEqual(self.service.declarations[0][1]["status"], "HYPOTHESE")
        self.assertTrue(all(t != threading.get_ident() for t in self.service.worker_threads))

    def test_empty_evaluation_does_not_claim_no_blockers_and_refresh_invalidates_display(self):
        self.window._render_qualifications({})
        self.assertIn("Aucune évaluation", self.window.qualification_text.get("1.0", "end"))
        self.window._render_qualifications(self.service.qualifications("cas"))
        self.window._render_case(self.service.get_case("cas"))
        self.assertFalse(self.window.qualification_tree.get_children())
        self.assertIn("cette version", self.window.qualification_text.get("1.0", "end"))

    def test_case_switch_clears_unsent_qualification_values(self):
        self.window.qual_reason.set("Données du premier client")
        self.window.qual_jurisdiction.set("Juridiction précédente")
        self.window._render_case({**self.service.case, "id": "second_case"})
        self.assertEqual(self.window.qual_reason.get(), "")
        self.assertEqual(self.window.qual_jurisdiction.get(), "")

    def test_native_buttons_are_explicit_threaded_and_refresh_revision_receipt(self):
        self.assertFalse(self.service.native_calls)
        with patch.object(self.window, "_detail_dialog") as detail:
            self.window.wacc_button.invoke()
            self.settle()
            self.assertEqual(self.service.native_calls, [("wacc", "cas", 600)])
            self.assertEqual(self.window.case["revision"], 1)
            self.assertIn("fixture-wacc.json", detail.call_args.args[1])
            self.window.sensitivity_button.invoke()
            self.settle()
            self.assertEqual(self.service.native_calls[-1], ("sensitivity", "cas", 3600))
            self.assertEqual(self.window.case["revision"], 2)
            self.assertIn("2 sur 2", detail.call_args.args[1])
        self.assertTrue(all(t != threading.get_ident() for t in self.service.worker_threads))
        self.assertFalse(self.errors)

    def test_native_actions_do_not_consume_unsaved_proposal_or_run_from_refresh(self):
        self.window.pending = [{"sheet": "Control", "cell": "C59", "value": 4}]
        self.window.solve_wacc()
        self.window.verify_sensitivity()
        self.assertFalse(self.service.native_calls)
        self.assertEqual(len(self.window.pending), 1)
        self.assertIn("proposition de saisie", self.errors[-1][1])
        self.window.pending = []
        self.window.refresh_case()
        self.settle()
        self.assertFalse(self.service.native_calls)

    def test_native_refusal_does_not_show_success_or_change_ui_revision(self):
        self.service.solve_wacc = lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("Source fiscale manquante"))
        with patch.object(self.window, "_detail_dialog") as detail:
            self.window.solve_wacc()
            self.settle()
            detail.assert_not_called()
        self.assertEqual(self.window.case["revision"], 0)
        self.assertIn("Source fiscale manquante", self.errors[-1][1])

    def test_conversation_refreshes_open_questions_and_answered_are_hidden(self):
        self.window.message_var.set("Quel calendrier ?")
        self.window.send_message()
        self.settle()
        self.assertIn("q1", self.window.question_rows)
        self.assertIn("Renseignons le calendrier", self.window.transcript.get("1.0", "end"))
        self.service.case["questions"][0]["status"] = "REPONDUE"
        self.window._render_case(self.service.get_case("cas"))
        self.assertFalse(self.window.question_rows)
        self.assertFalse(self.errors)

    def test_hidden_smoke_exercises_preview_apply_and_revision(self):
        result = smoke_test()
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["client_files_touched"])
        self.assertIn("application unique", result["checks"])


if __name__ == "__main__":
    unittest.main()
