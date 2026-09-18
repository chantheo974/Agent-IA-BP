"""Period guards preserve every selected payment and global diagnostic."""
import unittest
from tca_bp.qualifications import error_perimeter
from tca_bp.web_model_profile import cell_name


class CalendarErrorPerimeterTests(unittest.TestCase):
    def test_monthly_tax_guards_use_payment_month_even_for_prior_year_tax(self):
        for years in range(1,11):
            for month in range(132):
                for row in (52,70,74,78,97,99):
                    scope,active=error_perimeter('ATELIER_CIR_IS',cell_name(14+month,row),years)
                    self.assertEqual(scope,'FISCALITE')
                    self.assertEqual(active,month<12*years)
        # May2027 payment for FY2026: active on a two-year calendar. Its
        # accounting vintage does not make the tax settlement disappear.
        self.assertTrue(error_perimeter('ATELIER_CIR_IS',cell_name(14+16,74),2)[1])
        self.assertFalse(error_perimeter('ATELIER_CIR_IS',cell_name(14+16,74),1)[1])

    def test_exact_annual_rectangles_and_eleventh_year(self):
        for sheet,start,row in [('Modèle financier',3,281),('Compte de Résultat',4,87),
                ('Bilan',4,59),('Flux de trésorerie',4,47),('Plan de financement',4,44),('Contrôles',3,19)]:
            for years in range(1,11):
                for index in range(11):
                    self.assertEqual(error_perimeter(sheet,cell_name(start+index,row),years)[1],index<years)

    def test_opening_balances_summaries_and_unknown_positions_remain_active(self):
        for sheet,address in [('Bilan','C59'),('Contrôles','N19'),('Contrôles','C91'),
                ('ATELIER_CIR_IS','N160'),('Compte de Résultat','N88'),('Other','ZZ999')]:
            self.assertTrue(error_perimeter(sheet,address,3)[1])
        for years in (0,11,True,None):self.assertTrue(error_perimeter('ATELIER_CIR_IS','EO52',years)[1])
        self.assertTrue(error_perimeter('Sensi TCA','F21',3)[1])
        self.assertFalse(error_perimeter('Sensi TCA','F22',3)[1])
        self.assertTrue(error_perimeter('Sensi TCA','F24',3)[1])


if __name__=='__main__':unittest.main()
