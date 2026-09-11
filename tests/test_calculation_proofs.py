"""Reçus scellés et chaînes de conservation, sans travailleur natif."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from tca_bp.calculation_proofs import validate
from tca_bp.storage import atomic_json, digest


class CalculationProofTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.pin = {'model_id': 'fixture/1', 'model_ref': 'a' * 64,
                    'template_sha256': 'b' * 64, 'schema_sha256': 'c' * 64}
        self.number = 0

    def proof(self, kind='wacc', *, source='d' * 64, output='e' * 64, **extra):
        self.number += 1
        path = self.folder / (str(self.number) + '.native.json')
        receipt = {'status': 'CONVERGENCE_LOCALE' if kind == 'wacc' else 'TABLES_VERIFIEES',
            'source_sha256': source, 'output_sha256': output, 'source_preserved': True,
            'macros_enabled': False, 'iteration_enabled': False, 'calculation_state': 0,
            'save_reopen_verified': True, 'adopted': False}
        if kind == 'sensitivity':
            receipt.update(passed=True, input_signature_before='input/fixture',
                           input_signature_after='input/fixture')
        receipt.update(extra)
        atomic_json(path, receipt)
        return {**self.pin, 'status': 'VERIFIE', 'workbook_sha256': output,
                'input_signature': 'input/fixture', 'receipt_path': str(path), 'receipt_sha256': digest(path)}

    def carry(self, inherited, preserved):
        return {**self.pin, 'status': 'VERIFIE', 'workbook_sha256': preserved['workbook_sha256'],
                'input_signature': inherited['input_signature'], 'inherited_wacc_proof': inherited,
                'preserved_by_sensitivity_receipt': preserved}

    def test_direct_and_chained_proof_returns_origin_wacc_receipt(self):
        origin = self.proof()
        first = self.proof('sensitivity', source='e' * 64, output='f' * 64)
        second = self.proof('sensitivity', source='f' * 64, output='1' * 64)
        chained = self.carry(self.carry(origin, first), second)
        expected = validate(origin, 'wacc', self.folder, self.pin)
        self.assertIsNotNone(expected)
        self.assertEqual(validate(chained, 'wacc', self.folder, self.pin), expected)
        self.assertIsNotNone(validate(second, 'sensitivity', self.folder, self.pin))

    def test_model_pin_change_is_not_a_migration(self):
        proof = self.proof()
        for key in self.pin:
            with self.subTest(key=key):
                candidate = {**self.pin, key: 'different'}
                self.assertIsNone(validate(proof, 'wacc', self.folder, candidate))

    def test_receipt_tampering_and_missing_receipt_invalidate_proof(self):
        proof = self.proof()
        path = Path(proof['receipt_path'])
        atomic_json(path, {'status': 'CONVERGENCE_LOCALE'})
        self.assertIsNone(validate(proof, 'wacc', self.folder, self.pin))
        path.unlink()
        self.assertIsNone(validate(proof, 'wacc', self.folder, self.pin))

    def test_receipt_outside_case_is_refused_even_with_valid_digest(self):
        proof = self.proof()
        other_case = self.folder / 'other_case'
        other_case.mkdir()
        self.assertIsNone(validate(proof, 'wacc', other_case, self.pin))

    def test_json_arrays_and_malformed_or_empty_proofs_fail_closed(self):
        proof = self.proof()
        path = Path(proof['receipt_path'])
        for payload in ([], None, 'text', 7):
            atomic_json(path, payload)
            proof['receipt_sha256'] = digest(path)
            with self.subTest(payload=payload):
                self.assertIsNone(validate(proof, 'wacc', self.folder, self.pin))
        for value in (None, [], 5, {}, {'status': 'VERIFIE'}):
            with self.subTest(value=value):
                self.assertIsNone(validate(value, 'wacc', self.folder, self.pin))
        self.assertIsNone(validate(proof, 'arbitrary_macro', self.folder, self.pin))

    def test_unsafe_native_flags_and_unfinished_calculation_invalidate(self):
        for key, value in [('source_preserved', False), ('macros_enabled', True),
                           ('iteration_enabled', True), ('save_reopen_verified', False),
                           ('calculation_state', 1), ('calculation_state', False)]:
            with self.subTest(key=key, value=value):
                proof = self.proof(**{key: value})
                self.assertIsNone(validate(proof, 'wacc', self.folder, self.pin))

    def test_tables_require_passed_and_equal_input_signatures(self):
        for extra in ({'passed': False}, {'input_signature_before': 'changed'},
                      {'input_signature_after': 'changed'}):
            with self.subTest(extra=extra):
                proof = self.proof('sensitivity', **extra)
                self.assertIsNone(validate(proof, 'sensitivity', self.folder, self.pin))

    def test_inherited_source_output_and_input_links_must_all_match(self):
        original = self.proof()
        wrong_source = self.proof('sensitivity', source='7' * 64, output='f' * 64)
        self.assertIsNone(validate(self.carry(original, wrong_source), 'wacc', self.folder, self.pin))
        correct = self.proof('sensitivity', source='e' * 64, output='f' * 64)
        chain = self.carry(original, correct)
        for changed in ({'workbook_sha256': '8' * 64}, {'input_signature': 'changed'}):
            self.assertIsNone(validate({**chain, **changed}, 'wacc', self.folder, self.pin))
        malformed = deepcopy(chain)
        malformed['inherited_wacc_proof'] = []
        self.assertIsNone(validate(malformed, 'wacc', self.folder, self.pin))

    def test_modifying_any_older_preservation_receipt_invalidates_full_chain(self):
        original = self.proof()
        first = self.proof('sensitivity', source='e' * 64, output='f' * 64)
        second = self.proof('sensitivity', source='f' * 64, output='1' * 64)
        chain = self.carry(self.carry(original, first), second)
        Path(first['receipt_path']).write_text('{}', encoding='utf-8')
        self.assertIsNone(validate(chain, 'wacc', self.folder, self.pin))
        self.assertIsNotNone(validate(second, 'sensitivity', self.folder, self.pin))

    def test_chain_depth_is_bounded_and_cycles_are_refused(self):
        original = self.proof()
        preservation = self.proof('sensitivity', source='e' * 64, output='e' * 64)
        chain = original
        for _ in range(128):
            chain = self.carry(chain, preservation)
        self.assertIsNotNone(validate(chain, 'wacc', self.folder, self.pin))
        self.assertIsNone(validate(self.carry(chain, preservation), 'wacc', self.folder, self.pin))
        cycle = self.carry(original, preservation)
        cycle['inherited_wacc_proof'] = cycle
        self.assertIsNone(validate(cycle, 'wacc', self.folder, self.pin))


if __name__ == '__main__':
    unittest.main()
