"""Préconditions du rejeu candidat sur fixtures locales, sans Excel."""
from __future__ import annotations

import json
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import validate_candidate as candidate
from tca_bp.storage import canonical, digest


class FixtureModel:
    model_id = "fixture-candidate/1"
    def __init__(self, root, model_dir):
        self.template_path = model_dir / "TCA_BP_Trame_generique.xlsm"
        self.model_dir = model_dir
        self.schema = {"cells": {}}
    def ensure_built(self):
        return {"template_sha256": digest(self.template_path), "schema_sha256": digest(self.model_dir / "modele.json")}
    def catalog(self):
        return []
    def prepare(self, path, updates):
        return {"source_sha256": digest(path), "updates": updates}
    def apply(self, path, plan, output):
        if digest(path) != plan["source_sha256"]:
            raise ValueError("Source fictive modifiée")
        output.write_bytes(path.read_bytes() + canonical(plan["updates"]).encode("utf-8"))
        return {"output_sha256": digest(output)}


class CandidatePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "runtime/recette_fixture"
        self.source.mkdir(parents=True)
        self.model = self.root / "models/generic-v1-guards"
        self.model.mkdir(parents=True)
        (self.model / "TCA_BP_Trame_generique.xlsm").write_bytes(b"CANDIDATE_FIXTURE")
        (self.model / "modele.json").write_text("{}")
        default = self.root / "models/generic-v1/TCA_BP_Trame_generique.xlsm"
        default.parent.mkdir()
        default.write_bytes(b"DEFAULT_FIXTURE")
        checks = [{"name": key + "_oracle_" + str(i), "passed": True} for key, count in candidate.ORACLE_COUNTS.items() for i in range(count)]
        self.recipe = {"status": "SUCCES", "native": True, "case_ids": list(candidate.CASES), "checks": checks}
        self.write_recipe()
        for case_id in candidate.CASES:
            folder = self.source / "dossiers" / case_id
            folder.mkdir(parents=True)
            workbook = folder / "fixture.xlsm"
            workbook.write_bytes(b"NATIVE_FIXTURE")
            state = {"id": case_id, "calculation_status": "RECALCULE", "outputs_current": True,
                     "workbook_path": str(workbook), "sha256": digest(workbook), "model_id": "fixture-source/1",
                     "field_states": {"Control!C59": {"status": "CONFIRME", "value": 3},
                                      "Assumptions!D4": {"status": "CONFIRME", "value": 0}}}
            (folder / "etat_dossier.json").write_text(canonical(state), encoding="utf-8")
        self.patch_root = patch.object(candidate, "ROOT", self.root)
        self.patch_model = patch.object(candidate, "ModelEngine", FixtureModel)
        self.patch_root.start(); self.patch_model.start()

    def tearDown(self):
        self.patch_model.stop(); self.patch_root.stop()
        self.tmp.cleanup()

    def write_recipe(self):
        (self.source / "recette.json").write_text(canonical(self.recipe), encoding="utf-8")

    def test_preflight_reads_exact_three_cases_without_any_write(self):
        before = candidate._tree_hashes(self.root)
        result = candidate.preflight(self.source, self.model)
        self.assertEqual(set(result["cases"]), set(candidate.CASES))
        self.assertEqual(candidate._tree_hashes(self.root), before)
        updates = result["cases"]["test_services"]["updates"]
        self.assertEqual(next(item["value"] for item in updates if item["cell"] == "D4"), 0)
        self.assertTrue(all(item["status"] == "CONFIRME" for item in updates))

    def test_source_outside_recipe_namespace_is_refused(self):
        for path in (self.root, self.root / "runtime", self.root / "runtime/client_real", self.root / "runtime/nested/recette_fixture"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                candidate.preflight(path, self.model)

    def test_success_and_native_and_fifteen_checks_are_required(self):
        for key, value in (("status", "EN_COURS"), ("native", False), ("checks", self.recipe["checks"][:-1])):
            original = self.recipe[key]
            self.recipe[key] = value; self.write_recipe()
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.preflight(self.source, self.model)
            self.recipe[key] = original
        self.write_recipe()

    def test_unrecognized_case_refused_even_if_other_cases_are_fictitious(self):
        (self.source / "dossiers/client_real").mkdir()
        with self.assertRaises(ValueError):
            candidate.preflight(self.source, self.model)

    def test_altered_workbook_and_inactive_input_are_refused(self):
        folder = self.source / "dossiers/test_services"
        workbook = folder / "fixture.xlsm"
        workbook.write_bytes(b"CHANGED")
        with self.assertRaises(ValueError):
            candidate.preflight(self.source, self.model)
        workbook.write_bytes(b"NATIVE_FIXTURE")
        path = folder / "etat_dossier.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["field_states"]["Control!C59"]["status"] = "INACTIF"
        path.write_text(canonical(state), encoding="utf-8")
        with self.assertRaises(ValueError):
            candidate.preflight(self.source, self.model)

    def test_default_model_and_existing_output_cannot_be_used(self):
        with self.assertRaises(ValueError):
            candidate.preflight(self.source, self.root / "models/generic-v1")
        output = self.root / "runtime/validation_existing"
        output.mkdir()
        with patch.object(candidate, "Application") as app, self.assertRaises(ValueError):
            candidate.run(self.source, self.model, output)
        app.assert_not_called()

    def test_prepare_only_creates_one_revision_per_case_and_never_calls_excel(self):
        before = candidate._tree_hashes(self.source)
        with patch("tca_bp.native_excel.recalculate", side_effect=AssertionError("Excel interdit pendant préparation")) as native, contextlib.redirect_stdout(io.StringIO()):
            report = candidate.run(self.source, self.model, prepare_only=True)
        native.assert_not_called()
        self.assertEqual((report["status"], report["native"]), ("PREPARE", False))
        self.assertEqual(len(report["cases"]), 3)
        self.assertTrue(all(case["prepared_revision"] == 1 and case["field_count"] == 2 for case in report["cases"]))
        self.assertEqual(candidate._tree_hashes(self.source), before)
        context, restored, app = candidate._prepared_context(Path(report["data_dir"]))
        self.assertEqual(restored, report)
        self.assertEqual(len(app.list_cases()), 3)

    def test_resume_refuses_modified_prepared_copy_before_any_excel(self):
        with contextlib.redirect_stdout(io.StringIO()):
            report = candidate.run(self.source, self.model, prepare_only=True)
        output = Path(report["data_dir"])
        workbook = output / report["cases"][0]["prepared_workbook"]
        workbook.write_bytes(workbook.read_bytes() + b"UNEXPECTED_CHANGE")
        with patch("tca_bp.native_excel.recalculate") as native, self.assertRaises(ValueError):
            candidate.resume(output)
        native.assert_not_called()
        self.assertFalse((output / ".candidate-validation.lock").exists())
        self.assertEqual(json.loads((output / "validation.json").read_text(encoding="utf-8"))["status"], "PREPARE")


if __name__ == "__main__":
    unittest.main()
