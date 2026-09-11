"""Arrêts aux frontières de transaction, sur fichiers fictifs temporaires."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    from tests.test_service_adversarial import WitnessEngine
except ModuleNotFoundError:
    from test_service_adversarial import WitnessEngine
from tca_bp.service import Application
from tca_bp.storage import atomic_json, canonical, digest


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.engine = WitnessEngine(self.root)
        self.app = Application(self.root, self.root / "data", engine=self.engine)
        self.app.create_case("Fictif", "Reprise", case_id="cas")
        self.folder = self.app.store.case_dir("cas")

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_lock_is_reported_without_unlock_or_adoption(self):
        lock = self.folder / ".transaction.lock"
        lock.write_text("", encoding="utf-8")
        result = self.app.recovery_status("cas")
        self.assertEqual(result["lock"]["status"], "ILLISIBLE")
        self.assertTrue(lock.exists())
        self.assertEqual(result["current_revision"], 0)
        self.assertEqual(result["integrity"], "CONFORME")
        with self.assertRaises(ValueError):
            self.app.add_source("cas", text="Le diagnostic ne libère pas un verrou.")

    def test_incomplete_transaction_json_does_not_break_recovery(self):
        folder = self.folder / "transactions" / "interruption_fictive"
        folder.mkdir()
        marker = folder / "transaction.json"
        marker.write_text('{"status":', encoding="utf-8")
        result = self.app.recovery_status("cas")
        self.assertEqual(result["transactions_to_inspect"][0]["status"], "ILLISIBLE")
        self.assertEqual(marker.read_text(encoding="utf-8"), '{"status":')
        self.assertEqual(result["current_revision"], 0)

    def test_post_commit_marker_failure_is_not_a_second_application(self):
        source = self.app.add_source("cas", text="Valeur fictive de test : 5")
        plan = self.app.prepare_changes("cas", [{"sheet": "Entrées", "cell": "A1", "value": 5,
            "reason": "Valeur fictive pour le test de reprise", "evidence": source["id"]}])
        def failing_terminal_marker(path, value):
            if path.name == "transaction.json" and value.get("status") == "TERMINE":
                raise OSError("Panne fictive après commit de la base")
            return atomic_json(path, value)
        with patch("tca_bp.service.atomic_json", failing_terminal_marker):
            with self.assertRaises(OSError):
                self.app.apply_plan("cas", plan["id"])
        result = self.app.recovery_status("cas")
        transaction = result["transactions_to_inspect"][0]
        self.assertEqual(result["current_revision"], 1)
        self.assertEqual(result["integrity"], "CONFORME")
        self.assertEqual(transaction["status"], "COMMIT_CONFIRME_MIROIR_INCOMPLET")
        self.assertEqual(transaction["raw_status"], "ECHEC_A_INSPECTER")
        self.assertIs(transaction["needs_reapply"], False)
        replay = self.app.apply_plan("cas", plan["id"])
        self.assertEqual(replay["status"], "DEJA_APPLIQUE")
        self.assertEqual(self.engine.apply_calls, 1)
        self.assertEqual(self.app.get_case("cas")["revision"], 1)

    def native_recalculation(self, source, output, receipt, **kwargs):
        data = json.loads(source.read_text(encoding='utf-8'))
        data['cache'] = 10
        output.write_text(canonical(data), encoding='utf-8')
        result = {'status': 'RECALCULE', 'source_sha256': digest(source),
                  'output_sha256': digest(output), 'calculation_state': 0, 'adopted': False}
        atomic_json(receipt, result)
        return result

    def test_ordinary_recalculation_is_adopted_only_after_commit(self):
        def observing_history(db, case_id, kind, details):
            if kind == 'RECALCUL_EXCEL':
                self.assertTrue(details['adopted'])
                reports = list(self.folder.glob('versions/*.recalcul.json'))
                self.assertEqual(len(reports), 1)
                self.assertFalse(json.loads(reports[0].read_text(encoding='utf-8'))['adopted'])
            history(db, case_id, kind, details)
        history = self.app.store.history
        with patch('tca_bp.native_excel.recalculate', self.native_recalculation), \
                patch.object(self.app.store, 'history', side_effect=observing_history):
            result = self.app.recalculate('cas')
        self.assertTrue(result['adopted'])
        self.assertTrue(json.loads(Path(result['report_path']).read_text(encoding='utf-8'))['adopted'])
        self.assertEqual(self.app.get_case('cas')['revision'], 1)

    def test_ordinary_receipt_mirror_failure_after_commit_preserves_adopted_result(self):
        def writing(path, value):
            if path.name.endswith('.recalcul.json') and value.get('adopted') is True:
                raise OSError('Miroir bloqué après commit fictif')
            atomic_json(path, value)
        with patch('tca_bp.native_excel.recalculate', self.native_recalculation), \
                patch('tca_bp.service.atomic_json', side_effect=writing):
            result = self.app.recalculate('cas')
        self.assertTrue(result['adopted'])
        self.assertIn('miroir', result['report_notice'])
        self.assertEqual(self.app.get_case('cas')['revision'], 1)
        with self.app.store.connection() as db:
            rows = db.execute("SELECT kind,details FROM history WHERE case_id='cas' AND kind IN ('RECALCUL_EXCEL','RECU_RECALCUL_MIROIR_INCOMPLET')").fetchall()
        self.assertEqual(len(rows), 2)
        calculation = next(json.loads(row['details']) for row in rows if row['kind'] == 'RECALCUL_EXCEL')
        self.assertTrue(calculation['adopted'])
        self.assertFalse(json.loads(Path(result['report_path']).read_text(encoding='utf-8'))['adopted'])


if __name__ == "__main__":
    unittest.main()
