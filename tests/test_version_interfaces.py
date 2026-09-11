"""Parcours CLI/MCP des modèles de dossier, sur un espace fictif uniquement."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.__main__ import main, parser
from tca_bp.mcp_server import dispatch, handle, TOOLS
from tca_bp.service import Application
from tca_bp.storage import canonical
from tests.test_model_versions import fixture


class VersionInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tca-version-interface-")
        self.root = Path(self.tmp.name)
        self.engine = fixture(self.root / "old")
        self.app = Application(self.root, self.root / "data", engine=self.engine)
        self.case = self.app.create_case("Client fictif", "Ancien dossier", case_id="case_fixture")

    def tearDown(self):
        self.tmp.cleanup()

    def command(self, arguments):
        output, error = io.StringIO(), io.StringIO()
        with patch("tca_bp.service.Application", return_value=self.app), contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = main(arguments)
        return status, json.loads(output.getvalue() if status == 0 else error.getvalue())

    def unpin(self):
        with self.app.store.connection() as db:
            db.execute("UPDATE cases SET model_ref=NULL,template_sha256=NULL,schema_sha256=NULL WHERE id='case_fixture'")
            db.execute("UPDATE history SET details=? WHERE case_id='case_fixture' AND kind='CREATION'", (canonical({"model_id": self.engine.model_id, "revision": 0}),))

    def test_cli_agents_and_explanation_pass_case_identity(self):
        with patch.object(self.app, "agents", return_value=[{"case": "case_fixture"}]) as agents:
            status, result = self.command(["agents", "--case", "case_fixture"])
            self.assertEqual(status, 0)
            agents.assert_called_once_with(case_id="case_fixture")
        with patch.object(self.app, "sheet_info", return_value={"case": "case_fixture"}) as explain:
            status, result = self.command(["explain", "Control", "--case", "case_fixture"])
            self.assertEqual(status, 0)
            explain.assert_called_once_with("Control", case_id="case_fixture")

    def test_mcp_agents_and_explanation_pass_case_identity_and_reject_wrong_types(self):
        with patch.object(self.app, "agents", return_value=[]) as agents:
            dispatch(self.app, "bp_agents", {"case_id": "case_fixture"})
            agents.assert_called_once_with(case_id="case_fixture")
        with patch.object(self.app, "sheet_info", return_value={}) as explain:
            dispatch(self.app, "bp_explain", {"sheet": "Control", "case_id": "case_fixture"})
            explain.assert_called_once_with(sheet="Control", case_id="case_fixture")
        with self.assertRaisesRegex(ValueError, "Type invalide"):
            dispatch(self.app, "bp_agents", {"case_id": 1})

    def test_cli_explicit_binding_and_already_pinned_migration_refusal(self):
        self.unpin()
        args = ["bind-model", "case_fixture", "--model-dir", str(self.root / "old")]
        status, result = self.command(args)
        self.assertEqual(status, 0)
        self.assertEqual(result["model_ref"], self.case["model_ref"])
        self.assertEqual(result["revision"], 0)
        status, result = self.command(args)
        self.assertEqual(status, 2)
        self.assertIn("déjà épinglé", result["reason"])

    def test_mcp_binding_keeps_exact_initial_proof_and_never_migrates(self):
        self.unpin()
        wrong = fixture(self.root / "wrong", multiple=9)
        message = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "bp_bind_legacy_model", "arguments": {"case_id": "case_fixture", "model_dir": str(wrong.model_dir)}}}
        result = handle(self.app, message)["result"]
        self.assertTrue(result["isError"])
        self.assertIn("v0000", result["content"][0]["text"])
        self.assertIsNone(self.app.get_case("case_fixture")["model_ref"])
        message["params"]["arguments"]["model_dir"] = str(self.engine.model_dir)
        self.assertFalse(handle(self.app, message)["result"]["isError"])
        self.assertEqual(self.app.get_case("case_fixture")["model_ref"], self.case["model_ref"])
        spec = next(tool for tool in TOOLS if tool["name"] == "bp_bind_legacy_model")
        self.assertFalse(spec["annotations"]["readOnlyHint"])
        self.assertEqual(parser().parse_args(["bind-model", "case_fixture", "--model-dir", "old"]).model_dir, Path("old"))

    def test_cli_and_mcp_qualification_calls_preserve_source_and_documentary_status(self):
        declaration = {"module": "DATA CAPEX", "state": "INACTIF", "status": "CONFIRME", "evidence": "source_fixture", "reason": "Décision du porteur fictif."}
        path = self.root / "declaration.json"
        path.write_text(canonical(declaration), encoding="utf-8")
        with patch.object(self.app, "declare_qualification", create=True, return_value=declaration) as submit:
            status, result = self.command(["declare-qualification", "case_fixture", str(path)])
            self.assertEqual(status, 0)
            submit.assert_called_once_with("case_fixture", declaration)
        with patch.object(self.app, "declare_qualification", create=True, return_value=declaration) as submit:
            dispatch(self.app, "bp_declare_qualification", {"case_id": "case_fixture", "declaration": declaration})
            submit.assert_called_once_with(case_id="case_fixture", declaration=declaration)
        with patch.object(self.app, "qualifications", create=True, return_value={"scopes": {}}) as evaluate:
            self.assertEqual(self.command(["qualifications", "case_fixture"])[0], 0)
            evaluate.assert_called_once_with("case_fixture")
        with patch.object(self.app, "qualifications", create=True, return_value={"scopes": {}}) as evaluate:
            dispatch(self.app, "bp_qualifications", {"case_id": "case_fixture"})
            evaluate.assert_called_once_with(case_id="case_fixture")
        with self.assertRaisesRegex(ValueError, "Type invalide"):
            dispatch(self.app, "bp_declare_qualification", {"case_id": "case_fixture", "declaration": []})

    def test_real_qualification_service_round_trip_through_cli_and_mcp(self):
        snapshot = self.app.engine_for_case("case_fixture").qualification_snapshot(Path(self.case["workbook_path"]))
        self.assertIsNone(snapshot["diagnostics"]["BFR!E49"])
        source = self.app.add_source("case_fixture", text="Aucun investissement dans cette recette fictive.")
        declaration = {"module": "DATA CAPEX", "state": "INACTIF", "status": "CONFIRME", "evidence": source["id"], "reason": "Décision sourcée de recette fictive."}
        path = self.root / "actual-declaration.json"
        path.write_text(canonical(declaration), encoding="utf-8")
        status, result = self.command(["declare-qualification", "case_fixture", str(path)])
        self.assertEqual(status, 0)
        self.assertEqual(result["status"], "ENREGISTREE_A_EVALUER")
        result = dispatch(self.app, "bp_qualifications", {"case_id": "case_fixture"})
        self.assertEqual(result["declarations"]["DATA CAPEX"]["evidence"], source["id"])
        self.assertEqual(result["model_ref"], self.case["model_ref"])
        self.assertEqual(set(result["scopes"]), {"CA", "COGS", "CASH", "FISCALITE", "DCF"})
        self.assertTrue(all(not item["available"] for item in result["scopes"].values()))
        self.assertEqual(self.app.get_case("case_fixture")["revision"], 0)
        self.assertEqual(self.app.get_case("case_fixture")["sha256"], self.case["sha256"])
        declaration["evidence"] = "missing_source"
        with self.assertRaisesRegex(ValueError, "source"):
            dispatch(self.app, "bp_declare_qualification", {"case_id": "case_fixture", "declaration": declaration})


if __name__ == "__main__":
    unittest.main()
