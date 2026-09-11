"""Routage des actions natives : services simulés, aucun Excel ni classeur."""
import contextlib
import io
import json
import unittest
from unittest.mock import patch

from tca_bp.__main__ import main, parser
from tca_bp.mcp_server import dispatch, handle, TOOLS


class RecordingService:
    def __init__(self):
        self.calls = []

    def solve_wacc(self, case_id, timeout=600):
        self.calls.append(("solve_wacc", case_id, timeout))
        return {"status": "CONVERGENCE_LOCALE", "revision": 2, "report_path": "fixture-wacc.json"}

    def verify_sensitivity(self, case_id, timeout=3600):
        self.calls.append(("verify_sensitivity", case_id, timeout))
        return {"status": "TABLES_VERIFIEES", "revision": 3, "report_path": "fixture-tables.json"}


class NativeInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = RecordingService()

    def command(self, args):
        output = io.StringIO()
        with patch("tca_bp.service.Application", return_value=self.app), contextlib.redirect_stdout(output):
            status = main(args)
        return status, json.loads(output.getvalue())

    def test_cli_defaults_and_explicit_timeout_reach_only_selected_service(self):
        for command, method, default in (("solve-wacc", "solve_wacc", 600), ("verify-sensitivity", "verify_sensitivity", 3600)):
            with self.subTest(command=command):
                status, result = self.command([command, "fixture"])
                self.assertEqual(status, 0)
                self.assertEqual(self.app.calls[-1], (method, "fixture", default))
                self.assertIn("report_path", result)
                self.command([command, "fixture", "--timeout", "19"])
                self.assertEqual(self.app.calls[-1], (method, "fixture", 19))

    def test_invalid_cli_timeouts_never_reach_service(self):
        for command, raw in (("solve-wacc", "601"), ("solve-wacc", "0"), ("verify-sensitivity", "3601"), ("verify-sensitivity", "false"), ("verify-sensitivity", "1.5")):
            with self.subTest(command=command, raw=raw), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                parser().parse_args([command, "fixture", "--timeout", raw])
            self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.app.calls)

    def test_mcp_routes_native_actions_and_marks_them_as_mutations(self):
        for tool, method, default in (("bp_solve_wacc", "solve_wacc", 600), ("bp_verify_sensitivity", "verify_sensitivity", 3600)):
            with self.subTest(tool=tool):
                result = dispatch(self.app, tool, {"case_id": "fixture"})
                self.assertEqual(self.app.calls[-1], (method, "fixture", default))
                self.assertIn("revision", result)
                dispatch(self.app, tool, {"case_id": "fixture", "timeout": 19})
                self.assertEqual(self.app.calls[-1], (method, "fixture", 19))
                spec = next(spec for spec in TOOLS if spec["name"] == tool)
                self.assertFalse(spec["annotations"]["readOnlyHint"])

    def test_mcp_rejects_timeout_boolean_fraction_bounds_and_arbitrary_macro(self):
        for timeout in (True, False, "10", None, .5, 0, -1, 601):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                dispatch(self.app, "bp_solve_wacc", {"case_id": "fixture", "timeout": timeout})
        for name in ("bp_solve_wacc", "bp_verify_sensitivity"):
            with self.assertRaises(ValueError):
                dispatch(self.app, name, {"case_id": "fixture", "macro": "ARBITRARY"})
        self.assertFalse(self.app.calls)

    def test_listing_tools_or_initializing_mcp_never_starts_native_work(self):
        for method in ("initialize", "tools/list", "ping"):
            response = handle(self.app, {"jsonrpc": "2.0", "id": 1, "method": method})
            self.assertIn("result", response)
        self.assertFalse(self.app.calls)


if __name__ == "__main__":
    unittest.main()
