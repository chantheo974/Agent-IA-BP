"""Cas adversariaux indépendants de l'implémentation du moteur Excel.

Ils portent sur les frontières de transaction, de protocole et de provenance.
Tous les fichiers sont fictifs et placés dans TemporaryDirectory.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.mcp_server import serve, dispatch
from tca_bp.service import Application
from tca_bp.storage import canonical, digest


class WitnessEngine:
    model_id = "witness/1"

    def __init__(self, root):
        self.template_path = root / "template.xlsm"
        self.template_path.write_text(canonical({"input": None, "formula": "INPUT*2", "cache": None}), encoding="utf-8")
        self.schema = {"cells": {"Entrées": {"A1": {}}}}
        self.apply_calls = 0

    def ensure_built(self):
        return {"ready": True}

    def catalog(self):
        return [{"id": "input", "sheet": "Entrées", "label": "Valeur", "kind": "number", "cells": ["A1"]}]

    def context(self, path):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["formula"] != "INPUT*2":
            raise ValueError("Mauvais modèle")
        return {"model_id": self.model_id, "input_signature": canonical(data["input"]), "source_sha256": digest(path)}

    def prepare(self, path, updates):
        return {"hash": digest(path), "updates": updates}

    def apply(self, path, plan, output):
        self.apply_calls += 1
        if digest(path) != plan["hash"]:
            raise ValueError("Source périmée")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["input"] = plan["updates"][0]["value"]
        output.write_text(canonical(data), encoding="utf-8")
        return {"output_sha256": digest(output)}


class ServiceAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.engine = WitnessEngine(self.root)
        self.app = Application(self.root, self.root / "data", engine=self.engine)
        self.case = self.app.create_case("Fictif A", "Dossier", case_id="a")
        self.source = self.app.add_source("a", text="Valeur de travail explicitement choisie : 5")

    def tearDown(self):
        self.tmp.cleanup()

    def update(self, **extra):
        return {"sheet": "Entrées", "cell": "A1", "value": 5, "reason": "Valeur documentée par une réponse", "evidence": self.source["id"], "status": "HYPOTHESE", **extra}

    def test_flags_require_boolean_not_truthy_strings(self):
        for flag in ("replace_existing", "override_default"):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                self.app.prepare_changes("a", [self.update(**{flag: "false"})])

    def test_inactive_metadata_cannot_implicitly_disable_a_value(self):
        before = self.app.get_case("a")
        for value in (5, 0):
            with self.subTest(value=value), patch.object(self.engine, "prepare", wraps=self.engine.prepare) as prepare:
                with self.assertRaises(ValueError):
                    self.app.prepare_changes("a", [self.update(value=value, status="INACTIF")])
                prepare.assert_not_called()
        after = self.app.get_case("a")
        self.assertEqual((after["revision"], after["sha256"]), (before["revision"], before["sha256"]))
        self.assertEqual(after["plans"], [])

    def test_explicit_confirmed_zero_remains_a_valid_value(self):
        plan = self.app.prepare_changes("a", [self.update(value=0, status="CONFIRME")])
        self.assertEqual(plan["changes"][0]["value"], 0)
        self.assertEqual(plan["changes"][0]["status"], "CONFIRME")

    def test_unknown_case_operation_cannot_reserve_its_directory(self):
        with self.assertRaises(ValueError):
            self.app.add_source("future_case", text="Donnée fictive")
        self.assertFalse(self.app.store.case_dir("future_case").exists())
        created = self.app.create_case("Fictif B", "Nouveau", case_id="future_case")
        self.assertEqual(created["id"], "future_case")

    def test_import_extracts_a_consistent_copied_snapshot(self):
        original = self.root / "changing.txt"
        original.write_text("Prix initial : 100", encoding="utf-8")
        def changing_extract(path):
            extracted = path.read_text(encoding="utf-8")
            # Un utilisateur modifie l'original pendant l'import. La copie
            # immuable doit soit conserver l'ancien état, soit être refusée.
            original.write_text("Prix révisé : 999", encoding="utf-8")
            return extracted, "TEXTE"
        with patch.object(Application, "_extract", staticmethod(changing_extract)):
            try:
                source = self.app.add_source("a", path=original)
            except ValueError:
                return  # Refuser une source instable est également conforme.
        stored = self.app.store.case_dir("a") / source["path"]
        self.assertEqual(source["text"], stored.read_text(encoding="utf-8"))
        self.assertEqual(source["sha256"], digest(stored))

    def test_recalculation_cannot_silently_change_inputs(self):
        def bad_recalculation(source, output, receipt, **kwargs):
            data = json.loads(source.read_text(encoding="utf-8"))
            data["input"] = 999
            data["cache"] = 1998
            output.write_text(canonical(data), encoding="utf-8")
            result = {"status": "RECALCULE", "calculation_state": 0, "source_sha256": digest(source), "output_sha256": digest(output)}
            receipt.write_text(canonical(result), encoding="utf-8")
            return result
        before = self.app.get_case("a")
        with patch("tca_bp.native_excel.recalculate", bad_recalculation):
            with self.assertRaises(ValueError):
                self.app.recalculate("a")
        after = self.app.get_case("a")
        self.assertEqual(before["revision"], after["revision"])
        self.assertEqual(before["sha256"], after["sha256"])
        self.assertFalse(after["outputs_current"])

    def test_recalculation_preserves_exact_input_state_and_only_refreshes_cache(self):
        def good_recalculation(source, output, receipt, **kwargs):
            data = json.loads(source.read_text(encoding="utf-8"))
            data["cache"] = "fresh"
            output.write_text(canonical(data), encoding="utf-8")
            result = {"status": "RECALCULE", "calculation_state": 0, "source_sha256": digest(source), "output_sha256": digest(output), "wacc_macro": "NON_EXECUTEE"}
            receipt.write_text(canonical(result), encoding="utf-8")
            return result
        before = self.app.get_case("a")
        with patch("tca_bp.native_excel.recalculate", good_recalculation):
            result = self.app.recalculate("a")
        after = self.app.get_case("a")
        self.assertEqual(before["revision"] + 1, after["revision"])
        self.assertEqual(result["wacc_macro"], "NON_EXECUTEE")
        self.assertEqual(self.engine.context(Path(before["workbook_path"]))["input_signature"], self.engine.context(Path(after["workbook_path"]))["input_signature"])

    def test_source_changed_after_prepare_blocks_apply(self):
        document = self.root / "proof.txt"
        document.write_text("Valeur : 5", encoding="utf-8")
        source = self.app.add_source("a", path=document)
        plan = self.app.prepare_changes("a", [self.update(evidence=source["id"])])
        stored = self.app.store.case_dir("a") / source["path"]
        stored.write_text("Valeur : 500", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.app.apply_plan("a", plan["id"])
        self.assertEqual(self.engine.apply_calls, 0)
        self.assertEqual(self.app.get_case("a")["revision"], 0)

    def test_stale_plan_remains_stale_after_application_restart(self):
        first = self.app.prepare_changes("a", [self.update()], request_id="first")
        second = self.app.prepare_changes("a", [self.update(value=6)], request_id="second")
        self.app.apply_plan("a", first["id"])
        restarted = Application(self.root, self.root / "data", engine=self.engine)
        with self.assertRaises(ValueError):
            restarted.apply_plan("a", second["id"])
        self.assertEqual(self.engine.apply_calls, 1)


class MCPAdversarialTests(unittest.TestCase):
    def test_malformed_params_cannot_kill_stdio_server(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": []},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": "invalid"},
            {"jsonrpc": "2.0", "id": 3, "method": "ping"},
        ]
        output = io.StringIO()
        serve(None, io.StringIO("\n".join(json.dumps(m) for m in messages) + "\n"), output)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(responses), 3)
        self.assertIn("error", responses[0])
        self.assertIn("error", responses[1])
        self.assertEqual(responses[2]["result"], {})

    def test_mcp_boolean_argument_rejects_string(self):
        class SpyApp:
            called = False
            def __getattr__(self, name):
                def method(**kwargs):
                    self.called = True
                    return kwargs
                return method
        app = SpyApp()
        with self.assertRaises(ValueError):
            dispatch(app, "bp_recalculate", {"case_id": "a", "include_tables": "false"})
        self.assertFalse(app.called)


if __name__ == "__main__":
    unittest.main()
