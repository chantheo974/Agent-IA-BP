"""Validation du protocole natif WACC par worker simulé, sans aucun COM."""
import copy
import io
import json
import math
from pathlib import Path
import queue
import tempfile
import unittest
from unittest.mock import patch

from tca_bp import wacc_native
from tca_bp.storage import digest
from tca_bp.wacc_solver import ALGORITHM_ID


OUTPUTS = ['D136', 'D141', 'D142', 'D143', 'D156']


def proof():
    return {'algorithm': ALGORITHM_ID, 'status': 'CONVERGENCE_LOCALE', 'converged': True,
            'candidate': 0.12, 'calculated': 0.12, 'residual': 0, 'equity': 1_000_000,
            'fingerprint': 'immutable-test-inputs', 'evaluations': 2,
            'global_uniqueness_proven': False, 'domain': [0.020002, 5], 'tolerance': 1e-10}


def receipt_values():
    return {**proof(), 'method': 'LOCAL_SCALAR_SOLVER', 'mode': 'Itération', 'validity': 'OK',
            'macros_enabled': False, 'wacc_macro': 'NON_EXECUTEE', 'iteration_enabled': False,
            'calculation_state': 0, 'save_reopen_verified': True, 'source_preserved': True,
            'written_outputs': OUTPUTS.copy()}


class ReceiptValidationTests(unittest.TestCase):
    def test_valid_local_receipt_is_accepted(self):
        wacc_native.validate_saved_receipt(receipt_values(), proof(), 0.02)

    def test_nonfinite_boolean_or_missing_financial_values_are_refused(self):
        for field in ('candidate', 'calculated', 'residual', 'equity', 'evaluations'):
            for invalid in (None, True, False, '#N/A', math.nan, math.inf):
                with self.subTest(field=field, value=invalid), self.assertRaises(ValueError):
                    wacc_native.validate_saved_receipt({**receipt_values(), field: invalid}, proof(), 0.02)

    def test_financial_and_execution_inconsistencies_are_refused(self):
        wrong = {'candidate': 0.13, 'calculated': 0.13, 'residual': 0.0001, 'equity': 0,
                 'evaluations': 1, 'mode': 'Manuel', 'validity': 'A_COMPLETER', 'algorithm': 'different',
                 'method': 'VBA', 'macros_enabled': 0, 'wacc_macro': 'EXECUTEE',
                 'iteration_enabled': 0, 'calculation_state': False}
        for field, invalid in wrong.items():
            with self.subTest(field=field), self.assertRaises(ValueError):
                wacc_native.validate_saved_receipt({**receipt_values(), field: invalid}, proof(), 0.02)
        saved = receipt_values()
        saved['calculated'] += 5e-11
        with self.assertRaises(ValueError):
            wacc_native.validate_saved_receipt(saved, proof(), 0.02)


class FakeOwnedExcel:
    def __init__(self):
        self.terminated = False
        self.closed = False

    def terminate(self):
        self.terminated = True

    def close(self):
        self.closed = True


class FakeWorker:
    """Dialogue isolé. Aucun objet Excel ni exécutable système n'est créé."""
    def __init__(self, source, output, receipt, *, changes=None, iteration=False, pid=31415):
        self.source, self.output, self.receipt = source, output, receipt
        self.changes = changes or {}
        self.iteration = iteration
        self.events = queue.Queue()
        self.sent = []
        self.returncode = None
        self.killed = False
        self.stderr = io.StringIO('')
        self.stdout = self._lines()
        self.stdin = self
        self.events.put({'event': 'owned_process', 'pid': pid})

    def _lines(self):
        while True:
            value = self.events.get()
            if value is None:
                return
            yield json.dumps(value) + '\n'

    def write(self, text):
        request = json.loads(text)
        self.sent.append(request)
        operation = request['operation']
        if operation == 'ownership_confirmed':
            self.events.put({'event': 'ready', 'iteration_enabled': self.iteration, 'growth': 0.02,
                             'fingerprint': 'immutable-test-inputs', 'excel_version': 'SIMULEE'})
        elif operation == 'evaluate':
            self.events.put({'event': 'evaluation', 'calculated': 0.12, 'equity': 1_000_000,
                             'validity': 'OK', 'fingerprint': 'immutable-test-inputs'})
        elif operation == 'save':
            # Ce fichier n'est pas un vrai classeur. Seul le protocole est testé ;
            # la vérification métier du format/signature reste au service.
            self.output.write_bytes(b'FAUX_CLASSEUR_POUR_TEST_DE_PROTOCOLE')
            values = {**receipt_values(), 'source_sha256': digest(self.source),
                      'output_sha256': digest(self.output), **self.changes}
            self.receipt.write_text(json.dumps(values), encoding='utf-8')
            self.events.put({'event': 'saved', 'status': 'CONVERGENCE_LOCALE'})
            self.returncode = 0
            self.events.put(None)
        elif operation == 'abort':
            self.events.put({'event': 'aborted', 'source_preserved': True})
            self.returncode = 0
            self.events.put(None)
        else:
            raise AssertionError('Commande inattendue dans le test : ' + operation)

    def flush(self):
        pass

    def close(self):
        pass

    def wait(self, timeout=None):
        if self.returncode is None:
            raise AssertionError('Attente d’un worker simulé non terminé.')
        return self.returncode

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9
        self.events.put(None)


def fake_solver(evaluate, growth, **_kwargs):
    if growth != 0.02:
        raise AssertionError('Croissance inattendue.')
    for _ in range(2):
        response = evaluate(0.12)
        if response['calculated'] != 0.12:
            raise AssertionError('Réponse scalaire incohérente.')
    return proof()


class NativeProtocolTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='tca_wacc_protocol_test_')
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.source, self.output, self.receipt = root / 'source.xlsm', root / 'result.xlsm', root / 'receipt.json'
        self.source.write_bytes(b'SOURCE_FICTIVE_INCHANGEABLE')
        self.source_sha = digest(self.source)
        self.owned = FakeOwnedExcel()

    def _run(self, worker, *, previous=None, solver=fake_solver):
        with patch.object(wacc_native, 'available', return_value=True), \
             patch.object(wacc_native, 'existing_excel_pids', return_value=previous or set()), \
             patch.object(wacc_native.subprocess, 'Popen', return_value=worker), \
             patch.object(wacc_native, 'OwnedExcelProcess', return_value=self.owned) as ownership, \
             patch.object(wacc_native, 'solve', side_effect=solver):
            result = wacc_native.solve_native(self.source, self.output, self.receipt, timeout=3)
            return result, ownership

    def test_success_preserves_source_and_remains_unadopted(self):
        worker = FakeWorker(self.source, self.output, self.receipt)
        result, ownership = self._run(worker)
        self.assertFalse(result['adopted'])
        self.assertEqual(result['solver_proof'], proof())
        self.assertEqual(digest(self.source), self.source_sha)
        self.assertEqual(worker.sent[0], {'operation': 'ownership_confirmed'})
        self.assertEqual([item['operation'] for item in worker.sent], ['ownership_confirmed', 'evaluate', 'evaluate', 'save'])
        ownership.assert_called_once_with(31415)
        self.assertFalse(self.owned.terminated)
        self.assertTrue(self.owned.closed)

    def test_preexisting_excel_is_never_owned_acknowledged_or_terminated(self):
        worker = FakeWorker(self.source, self.output, self.receipt, pid=31415)
        with self.assertRaisesRegex(ValueError, 'déjà présente'):
            self._run(worker, previous={31415})
        self.assertEqual(worker.sent, [])
        self.assertFalse(self.owned.terminated)
        self.assertFalse(self.owned.closed)
        self.assertTrue(worker.killed)
        self.assertEqual(digest(self.source), self.source_sha)
        self.assertFalse(self.output.exists())

    def test_circular_iteration_is_refused_before_evaluation(self):
        worker = FakeWorker(self.source, self.output, self.receipt, iteration=True)
        with self.assertRaises(ValueError):
            self._run(worker)
        self.assertEqual([item['operation'] for item in worker.sent], ['ownership_confirmed'])
        self.assertTrue(self.owned.terminated)
        self.assertTrue(self.owned.closed)
        self.assertFalse(self.output.exists())

    def test_failed_solver_cannot_save_or_adopt(self):
        worker = FakeWorker(self.source, self.output, self.receipt)
        def failure(*args, **kwargs):
            return {**proof(), 'converged': False, 'status': 'BUDGET_EPUISE'}
        with self.assertRaisesRegex(ValueError, 'BUDGET_EPUISE'):
            self._run(worker, solver=failure)
        self.assertEqual([item['operation'] for item in worker.sent], ['ownership_confirmed', 'abort'])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.receipt.exists())
        failed = json.loads(self.receipt.with_name('receipt.echec.json').read_text(encoding='utf-8'))
        self.assertFalse(failed['adopted'])
        self.assertTrue(failed['source_preserved'])
        self.assertEqual(digest(self.source), self.source_sha)

    def test_inconsistent_worker_receipt_cannot_be_adopted(self):
        worker = FakeWorker(self.source, self.output, self.receipt, changes={'calculation_state': 1})
        with self.assertRaises(ValueError):
            self._run(worker)
        self.assertTrue(self.owned.terminated)
        self.assertTrue(self.owned.closed)
        self.assertNotIn('solver_proof', json.loads(self.receipt.read_text(encoding='utf-8')))
        self.assertEqual(digest(self.source), self.source_sha)

    def test_strings_do_not_count_as_true_reopen_proofs(self):
        worker = FakeWorker(self.source, self.output, self.receipt, changes={'save_reopen_verified': 'false'})
        with self.assertRaises(ValueError):
            self._run(worker)
        self.assertEqual(digest(self.source), self.source_sha)


if __name__ == '__main__':
    unittest.main()
