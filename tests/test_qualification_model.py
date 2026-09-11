"""Contrat de qualification confronté au vrai schéma, en lecture statique."""
import json
from pathlib import Path
import unittest

from tca_bp.qualifications import collect_snapshot, evaluate, scope_for_output
from tca_bp.vendor.input_engine import Workbook


class QualificationModelTests(unittest.TestCase):
    def test_real_authorized_cells_are_read_and_no_protected_closing_is_requested(self):
        root = Path(__file__).resolve().parents[1]
        model = root / 'models' / 'generic-v1'
        if not model.is_dir():
            self.skipTest('Trame locale absente du dépôt de code ; aucune recette de modèle prétendue exécutée.')
        schema = json.loads((model / 'modele.json').read_text(encoding='utf-8'))
        wb = Workbook(model / 'TCA_BP_Trame_generique.xlsm')
        try:
            snapshot = collect_snapshot(wb, schema)
            result = evaluate(snapshot, {}, set())
            self.assertGreater(len(snapshot['cells']), 14000)
            self.assertNotIn('Valorisation!D15', result['cells'])
            self.assertTrue(all(key in snapshot['cells'] for key in result['cells']),
                            sorted(set(result['cells']) - set(snapshot['cells'])))
            self.assertFalse(any(s['available'] for s in result['scopes'].values()))
            self.assertEqual(snapshot['cells']['Valorisation!D9']['value'], None)
            self.assertEqual(scope_for_output('Revenue', 'E282'), 'CA')
            self.assertEqual(scope_for_output('Contrats', 'E92'), 'CA')
        finally:
            wb.close()


if __name__ == '__main__':
    unittest.main()
