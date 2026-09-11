"""Refuser une recette qui annoncerait une autre version que celle calculée."""
from pathlib import Path
import unittest

from tools.validate_qualified_wacc import validate_prepared_identity


class QualifiedWaccIdentityTests(unittest.TestCase):
    def test_exact_identity_and_every_pin_component(self):
        folder = Path('runtime/recette_fictive').resolve()
        prepared = {'case_id': 'test_qualifications_wacc', 'runtime_dir': str(folder),
                    'model_sha256': 'template'}
        pin = {'model_id': 'model/1', 'model_ref': 'archive',
               'template_sha256': 'template', 'schema_sha256': 'schema'}
        validate_prepared_identity(prepared, pin, pin, folder)
        for key in pin:
            with self.subTest(component=key), self.assertRaisesRegex(ValueError, 'épinglé'):
                validate_prepared_identity(prepared, {**pin, key: 'foreign'}, pin, folder)
        for change in ({'case_id': 'client_reel'}, {'runtime_dir': str(folder / 'other')},
                       {'model_sha256': 'other'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_prepared_identity({**prepared, **change}, pin, pin, folder)


if __name__ == '__main__':
    unittest.main()
