"""Contrats natifs dérivés en lecture seule : aucune reconstruction ni COM."""
import copy
import json
import os
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET
from tca_bp.model_build import native_execution_metadata
from tca_bp.storage import digest
from tca_bp.vendor.input_engine import Workbook, N


class NativeGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parent.parent
        configured=os.environ.get('TCA_TEST_MODEL_DIR')
        cls.folder=Path(configured).resolve() if configured else root/'models/generic-v1-qualified'
        if not (cls.folder/'modele.json').is_file(): cls.folder=root/'models/generic-v1'
        if not (cls.folder/'modele.json').is_file(): raise unittest.SkipTest('Modèle généré absent ; aucun rebuild implicite.')
        cls.schema=json.loads((cls.folder/'modele.json').read_text(encoding='utf-8'))

    def setUp(self):
        self.path=self.folder/'TCA_BP_Trame_generique.xlsm'
        self.before=digest(self.path)
        self.book=Workbook(self.path)

    def tearDown(self):
        self.book.close()
        self.assertEqual(digest(self.path), self.before)

    def test_wacc_names_actual_dependencies_write_guards_and_fingerprint(self):
        result=native_execution_metadata(self.book,self.schema)
        wacc=result['wacc']
        self.assertEqual(len(wacc['defined_names']),12)
        self.assertEqual(wacc['write_contract']['allowed_cells'],['D136','D141','D142','D143','D156'])
        self.assertFalse(wacc['write_contract']['mode_write_allowed'])
        self.assertFalse(wacc['write_contract']['global_circular_iteration_allowed'])
        self.assertFalse(wacc['executed']);self.assertFalse(wacc['legacy_vba']['execution_claimed'])
        self.assertEqual(wacc['freshness']['reference_count'],263)
        self.assertEqual([len(p['references']) for p in wacc['freshness']['parts']],[124,94,45,0])
        self.assertFalse(wacc['freshness']['is_cryptographic_hash'])
        edges=wacc['literal_dependency_edges']
        self.assertIn({'source':"'Valorisation'!$D$136",'target':"'Valorisation'!D7"},edges)
        self.assertIn({'source':"'Valorisation'!D40",'target':"'Valorisation'!D128"},edges)
        for item in wacc['formula_nodes']:
            self.assertEqual(item['formula'], self.book.formula('Valorisation',item['cell']))

    def test_three_tables_have_exact_orientation_and_57_scalar_targets(self):
        result=native_execution_metadata(self.book,self.schema)
        tables=result['native_tables']
        self.assertEqual([t['result_count'] for t in tables],[36,12,9])
        self.assertEqual(sum(t['scalar_count'] for t in tables),24)
        self.assertEqual(tables[2]['row_input'],'C14')
        self.assertEqual(tables[2]['column_input'],'C8')
        self.assertEqual(tables[2]['native_attributes']['dt2D'],'1')
        self.assertEqual(tables[2]['native_attributes']['dtr'],'1')
        self.assertEqual(result['sensitivity']['technical_copy_writes'],['C8','C14','C18'])
        for table in tables:
            self.assertEqual(table['native_validation'],'NOT_EXECUTED')
            self.assertTrue(all(g['locked'] and not g['business_input'] and not g['has_formula']
                                for g in table['driver_protection'].values()))

    def test_moved_name_extra_native_write_and_instrument_formula_are_refused(self):
        names=self.book.wb.findall('m:definedNames/m:definedName',N)
        target=next(n for n in names if n.get('name')=='ISP_WACC_Candidat')
        target.text='Valorisation!$D$108'
        with self.assertRaises(ValueError):native_execution_metadata(self.book,self.schema)
        target.text='Valorisation!$D$136'
        schema=copy.deepcopy(self.schema);schema['native_outputs']['Valorisation'].append('D107')
        with self.assertRaises(ValueError):native_execution_metadata(self.book,schema)
        driver=self.book.sheet('Sensi Analyses')[1]['C8']
        ET.SubElement(driver,'{'+N['m']+'}f').text='1'
        with self.assertRaises(ValueError):native_execution_metadata(self.book,self.schema)


if __name__=='__main__':unittest.main()
