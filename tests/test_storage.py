import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.storage import atomic_json


class AtomicWriteTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Verrous transitoires Windows")
    def test_sharing_violation_retries_without_removing_previous_version(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            atomic_json(target, {"revision": 1})
            replace = os.replace
            calls = []
            def intermittent(source, destination):
                calls.append(True)
                if len(calls) < 3:
                    self.assertEqual(1, json.loads(target.read_text())["revision"])
                    error = PermissionError("fichier temporairement occupé")
                    error.winerror = 32
                    raise error
                replace(source, destination)
            with patch("tca_bp.storage.os.replace", intermittent), patch("tca_bp.storage.time.sleep"):
                atomic_json(target, {"revision": 2})
            self.assertEqual(3, len(calls))
            self.assertEqual(2, json.loads(target.read_text())["revision"])
            self.assertEqual([target], list(Path(directory).iterdir()))

    @unittest.skipUnless(os.name == "nt", "Verrous transitoires Windows")
    def test_permanent_refusal_preserves_previous_version(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            atomic_json(target, {"revision": 1})
            error = PermissionError("accès refusé")
            error.winerror = 5
            with patch("tca_bp.storage.os.replace", side_effect=error) as replace, patch("tca_bp.storage.time.sleep"):
                with self.assertRaises(PermissionError):
                    atomic_json(target, {"revision": 2})
            self.assertEqual(8, replace.call_count)
            self.assertEqual(1, json.loads(target.read_text())["revision"])
            self.assertEqual([target], list(Path(directory).iterdir()))
