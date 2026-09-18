"""Native mapping protocols on moved owners; no Excel process is launched."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from tca_bp import sensitivity_native, wacc_native
from tca_bp.calculation_proofs import validate
from tca_bp.storage import atomic_json, digest
from tca_bp.web_model_profile import PROFILE_SCHEMA, seal_profile
from tests.test_wacc_native import FakeOwnedExcel, FakeWorker, fake_solver, proof, receipt_values
from tests.test_sensitivity_native import mathematical_campaign


def moved_profile():
    sheets=[]
    for index,(original,name) in enumerate((('Valorisation','Valeur actuelle'),('Sensi Analyses','Tests de sensibilité'),
                                           ('Control','Calendrier'),('Sensi TCA','Scénarios'))):
        sheets.append({'id':str(index),'name':name,'original_name':original,'deleted':False,
                       'transforms':[{'type':'insert_rows','index':1,'count':3},
                                     {'type':'insert_columns','index':1,'count':2}]})
    return seal_profile({'schema':PROFILE_SCHEMA,'version':2,'sheets':sheets})


class PhysicalSensitivityBook:
    """Values and native table XML exist only at mapped physical coordinates."""
    def __init__(self,mapping):
        self.mapping=mapping
        self.values={}
        self.nodes={}
        self.reads=[]
        def put(cell,value):
            self.values[(mapping['sheet'],mapping['cells'][cell])]=value
        for cell in ('C8','C14','C18'):
            put(cell,0)
        for row in range(8,17):
            put('F'+str(row),.05)
        for row in range(25,34):
            put('C'+str(row),row-24)
        for row,value in zip(range(40,46),(-.3,-.2,-.1,0,.1,.2)):
            put('B'+str(row),value)
        for cell,value in zip(('D49','E49','F49','C50','C51','C52'),(0,-.5,-1,0,-.1,-.2)):
            put(cell,value)
        for key,location in mapping['auxiliary'].items():
            self.values[(location['sheet'],location['cell'])]=8 if key=='Control!C59' else 0
        for anchor,area,driver,driver2 in (('D25','D25:G33','C18',None),('C40','C40:D45','C8',None),('D50','D50:F52','C14','C8')):
            node=ET.Element('c')
            attrs={'t':'dataTable','ref':mapping['ranges'][area],'r1':mapping['cells'][driver]}
            if driver2:
                attrs.update(r2=mapping['cells'][driver2],dt2D='1',dtr='1')
            ET.SubElement(node,'{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f',attrs)
            self.nodes[mapping['cells'][anchor]]=node

    def value(self,sheet,cell):
        self.reads.append((sheet,cell))
        return self.values[(sheet,cell)]

    def formula(self,sheet,cell):
        self.reads.append((sheet,cell))
        if (sheet,cell) not in self.values:
            raise AssertionError('Read outside physical mapping')
        return None

    def sheet(self,sheet):
        if sheet!=self.mapping['sheet']:
            raise AssertionError('Logical name sent to native workbook')
        return None,self.nodes


class NativeMappingTests(unittest.TestCase):
    def test_wacc_and_auxiliary_owners_follow_rows_columns_and_renames(self):
        profile=moved_profile()
        wacc=wacc_native.native_mapping(profile,'wacc')
        self.assertEqual(wacc['sheet'],'Valeur actuelle')
        self.assertEqual(wacc['cells']['D136'],'F139')
        self.assertEqual(wacc['written_outputs'],['F139','F144','F145','F146','F159'])
        sensitivity=wacc_native.native_mapping(profile,'sensitivity')
        self.assertEqual(sensitivity['cells']['C8'],'E11')
        self.assertEqual(sensitivity['ranges']['D25:G33'],'F28:I36')
        self.assertEqual(sensitivity['auxiliary']['Control!C59']['cell'],'E62')
        self.assertEqual(sensitivity['auxiliary']['Sensi TCA!C15']['sheet'],'Scénarios')
        self.assertEqual(wacc['profile_sha256'],profile['profile_sha256'])
        self.assertNotEqual(wacc['mapping_sha256'],sensitivity['mapping_sha256'])
        self.assertIsNone(wacc_native.native_mapping(None,'wacc'))

    def test_deleted_native_owner_refused_before_any_worker(self):
        profile=moved_profile()
        profile['sheets'][0]['transforms'].append({'type':'delete_rows','index':139,'count':1})
        profile=seal_profile(profile)
        with self.assertRaisesRegex(ValueError,'supprimé'):
            wacc_native.native_mapping(profile,'wacc')

    def test_internal_change_to_table_shape_requires_requalification(self):
        profile=moved_profile()
        profile['sheets'][1]['transforms'].append({'type':'insert_rows','index':30,'count':1})
        with self.assertRaisesRegex(ValueError,'forme'):
            wacc_native.native_mapping(seal_profile(profile),'sensitivity')

    def test_tampered_profile_never_generates_execution_mapping(self):
        profile=moved_profile()
        profile['sheets'][0]['name']='Malicious changed profile'
        with self.assertRaisesRegex(ValueError,'modifié'):
            wacc_native.native_mapping(profile,'wacc')

    def test_instrumentation_only_rewrites_the_three_physical_drivers(self):
        mapping=wacc_native.native_mapping(moved_profile(),'sensitivity')
        raw=b'<sheetData><c r="C8"><v>999</v></c><c r="E11"><v>0</v></c><c r="E17"><v>0</v></c><c r="E21"><v>0</v></c><c r="F28"><f t="dataTable" ref="F28:I36" r1="E21"/></c></sheetData>'
        patched=sensitivity_native._patch_literals(raw,{'C8':-.1,'C14':-.5,'C18':0},mapping)
        self.assertIn(b'<c r="C8"><v>999</v></c>',patched)
        self.assertIn(b'<c r="E17"><v>-0.5</v></c>',patched)
        self.assertEqual(sensitivity_native._patch_literals(patched,dict.fromkeys(sensitivity_native.DRIVERS,0),mapping),raw)

    def test_preconditions_inspect_physical_names_cells_and_table_definitions(self):
        mapping=wacc_native.native_mapping(moved_profile(),'sensitivity')
        wb=PhysicalSensitivityBook(mapping)
        initial=sensitivity_native._preconditions(wb,mapping)
        self.assertEqual(initial['horizon'],8)
        self.assertEqual(initial['drivers'],{'C8':0,'C14':0,'C18':0})
        self.assertTrue(all(name not in ('Sensi Analyses','Valorisation','Control','Sensi TCA') for name,cell in wb.reads))
        wb.nodes[mapping['cells']['D25']][0].set('r1','C18')
        with self.assertRaisesRegex(ValueError,'table incompatible'):
            sensitivity_native._preconditions(wb,mapping)

    def test_all_57_comparisons_remain_in_stable_logical_coordinates(self):
        plan,receipt=mathematical_campaign()
        plan['native_mapping']=wacc_native.native_mapping(moved_profile(),'sensitivity')
        checked=sensitivity_native.compare_results(plan,receipt)
        self.assertTrue(checked['passed'])
        self.assertEqual(len(checked['comparisons']),57)
        self.assertEqual(checked['comparisons'][0]['cell'],'D25')

    def test_diagnostic_pair_cannot_be_accepted_as_a_qualified_campaign(self):
        plan,receipt=mathematical_campaign()
        # Even with a complete base, two real scalar observations cannot qualify
        # the tables. A maintenance probe never weakens the 24/57 contract.
        receipt['schema']='tca-sensitivity-probe/1'
        receipt['scalars']=[item for item in receipt['scalars'] if item['id'] in ('volume_40','volume_44')]
        with self.assertRaisesRegex(ValueError,'24 scénarios'):
            sensitivity_native.compare_results(plan,receipt)

    def test_wacc_mock_protocol_receives_sealed_mapping_and_verifies_physical_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source,output,receipt=(root/name for name in ('source.xlsm','output.xlsm','receipt.json'))
            source.write_bytes(b'fixture input, not an Excel workbook')
            profile=moved_profile()
            mapping=wacc_native.native_mapping(profile,'wacc')
            worker=FakeWorker(source,output,receipt,changes={'written_outputs':mapping['written_outputs'],
                              'profile_sha256':mapping['profile_sha256'],'native_mapping_sha256':mapping['mapping_sha256']})
            owned=FakeOwnedExcel()
            with patch.object(wacc_native,'available',return_value=True), \
                 patch.object(wacc_native,'existing_excel_pids',return_value=set()), \
                 patch.object(wacc_native.subprocess,'Popen',return_value=worker) as spawn, \
                 patch.object(wacc_native,'OwnedExcelProcess',return_value=owned), \
                 patch.object(wacc_native,'solve',side_effect=fake_solver):
                result=wacc_native.solve_native(source,output,receipt,timeout=3,profile=profile)
            args=spawn.call_args.args[0]
            mapping_path=Path(args[args.index('-MappingPath')+1])
            self.assertEqual(digest(mapping_path),args[args.index('-MappingSha256')+1])
            self.assertEqual(json.loads(mapping_path.read_text(encoding='utf-8'))['cells']['D136'],'F139')
            self.assertEqual(result['written_outputs'],mapping['written_outputs'])
            self.assertEqual(result['profile_sha256'],profile['profile_sha256'])
            self.assertFalse(owned.terminated)

    def test_wacc_receipt_rejects_legacy_addresses_and_another_profile(self):
        mapping=wacc_native.native_mapping(moved_profile(),'wacc')
        result={**receipt_values(),'written_outputs':mapping['written_outputs'],
                'profile_sha256':mapping['profile_sha256'],'native_mapping_sha256':mapping['mapping_sha256']}
        wacc_native.validate_saved_receipt(result,proof(),.02,mapping)
        for changed in ({'written_outputs':['D136','D141','D142','D143','D156']},{'profile_sha256':'0'*64},{'native_mapping_sha256':'0'*64}):
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                wacc_native.validate_saved_receipt({**result,**changed},proof(),.02,mapping)

    def test_persistent_proof_must_bind_to_same_profile_as_native_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            receipt=root/'receipt.json'
            mapping=wacc_native.native_mapping(moved_profile(),'wacc')
            recorded={**receipt_values(),'output_sha256':'output_hash','profile_sha256':mapping['profile_sha256'],
                      'native_mapping_sha256':mapping['mapping_sha256']}
            atomic_json(receipt,recorded)
            pin={'model_id':'model/2','model_ref':'ref','template_sha256':'template','schema_sha256':'schema'}
            check={**pin,'status':'VERIFIE','input_signature':'inputs','workbook_sha256':'output_hash',
                   'receipt_path':'receipt.json','receipt_sha256':digest(receipt),
                   'profile_sha256':mapping['profile_sha256'],'native_mapping_sha256':mapping['mapping_sha256']}
            self.assertIsNotNone(validate(check,'wacc',root,pin))
            self.assertIsNone(validate({**check,'profile_sha256':'0'*64},'wacc',root,pin))
            legacy={key:value for key,value in check.items() if key not in ('profile_sha256','native_mapping_sha256')}
            self.assertIsNone(validate(legacy,'wacc',root,pin))


if __name__=='__main__':
    unittest.main()
