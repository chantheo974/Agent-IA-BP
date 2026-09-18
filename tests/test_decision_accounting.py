import unittest
from tca_bp.decision_accounting import catalog,suggest

class AccountingReferenceTests(unittest.TestCase):
    def test_two_tables_and_longest_prefix(self):
        reference=catalog()
        self.assertEqual(len(reference['accounts']),506)
        self.assertEqual(len(reference['posts']),54)
        self.assertEqual(suggest('44566000','123.45',2024)['matched_prefix'],'44566')
        self.assertEqual(suggest('6226TCA','500',2024)['matched_prefix'],'6226')
    def test_balance_direction_auxiliary_and_reform_are_explicit(self):
        self.assertEqual(suggest('512001','100',2024)['post']['code'],'A13')
        self.assertEqual(suggest('512001','-100',2024)['post']['code'],'P15')
        self.assertEqual(suggest('411DUPONT','-100',2024)['post']['code'],'P12')
        self.assertEqual(suggest('777','-100',2026)['status'],'A_REVOIR')
        self.assertEqual(suggest('649','100',2026)['status'],'A_REVOIR')
        self.assertFalse(suggest('512001','100',2024)['applied'])
    def test_unknown_and_invalid_are_never_zero(self):
        self.assertEqual(suggest('9900','0',2026)['status'],'A_REVOIR')
        with self.assertRaises(ValueError): suggest('512','NaN',2026)
        with self.assertRaises(ValueError): suggest(512,'100',2026)

