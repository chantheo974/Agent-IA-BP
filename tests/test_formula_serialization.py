"""Excel may remove optional sheet quotes; formula semantics stay strict."""
from pathlib import Path
import tempfile
import unittest
from tests.test_fiscal_calendar_migration import fixture
from tests.test_wacc_fingerprint_migration import xml_runner
from tca_bp.web_model_profile import initial_profile
from tca_bp.web_structure import _formula_key,prepare_variant


class FormulaSerializationTests(unittest.TestCase):
    def test_literal_text_escaped_quotes_and_absolute_references_are_significant(self):
        self.assertEqual(_formula_key("='BFR'!$P$10+BFR!P10"),_formula_key('BFR!$P$10+BFR!P10'))
        self.assertNotEqual(_formula_key('BFR!$P$10'),_formula_key('BFR!P10'))
        self.assertNotEqual(_formula_key('"\'BFR\'!"'),_formula_key('"BFR!"'))
        self.assertNotEqual(_formula_key('"a""\'BFR\'!"'),_formula_key('"a""BFR!"'))
        self.assertNotEqual(_formula_key("'Some name'!A1"),_formula_key("'Other name'!A1"))
        self.assertEqual(_formula_key('_xlfn.AGGREGATE(15,6,A1,1)'),_formula_key('AGGREGATE(15,6,A1,1)'))
        self.assertNotEqual(_formula_key('"_xlfn.AGGREGATE("'),_formula_key('"AGGREGATE("'))

    def test_preview_accepts_only_excel_serialization_and_refuses_literal_change(self):
        with tempfile.TemporaryDirectory(prefix='tca-formula-normalization-') as temp:
            root=Path(temp);engine=fixture(root/'model');profile=initial_profile(engine,engine.template_path)
            proposed='IF(COUNT(\'ATELIER_CIR_IS\'!C34)=1,\'ATELIER_CIR_IS\'!C34,"\'ATELIER_CIR_IS\'!")'
            operations=[{'type':'set_formula','sheet':'ATELIER_CIR_IS','cell':'C35','formula':'='+proposed,'evidence_id':'source'}]
            def correct(source,output,ops,**kw):
                normalized=_formula_key(proposed)
                return xml_runner(source,output,[{**ops[0],'formula':normalized}],**kw)
            good=prepare_variant(engine.template_path,root/'good.xlsm',profile,operations,runner=correct)
            self.assertFalse(good['blocked'])
            def corrupt(source,output,ops,**kw):
                normalized=_formula_key(proposed).replace('"\'ATELIER_CIR_IS\'!"','"ATELIER_CIR_IS!"')
                return xml_runner(source,output,[{**ops[0],'formula':normalized}],**kw)
            bad=prepare_variant(engine.template_path,root/'bad.xlsm',profile,operations,runner=corrupt)
            self.assertTrue(bad['blocked'])
            self.assertIn('FORMULA_DIFFERS_FROM_PROPOSAL',[d['code'] for d in bad['diagnostics']])


if __name__=='__main__':unittest.main()
