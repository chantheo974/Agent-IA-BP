"""Structural coordinates and immutable variants on fictitious OOXML.

The fixture runner below simulates serialization only; native Excel has a
separate receipt and is not inferred from these unit tests.
"""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from contextlib import nullcontext
from unittest.mock import patch
import zipfile
from xml.etree import ElementTree as ET

from tests.test_model_versions import fixture
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core
from tca_bp.web_model import ProfileEngine, initial_profile, seal_profile_model
from tca_bp.web_model_profile import map_location, map_between_profiles, seal_profile
from tca_bp.web_structure import plan_operations, operation_targets, prepare_variant, vba_preservation, _repair_groups


def move_fixture(source, output, operations, **kwargs):
    """Deliberately narrow fake: insert Inputs row 1 then rename it."""
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, 'w') as after:
        for info in original.infolist():
            raw = original.read(info.filename)
            if info.filename == 'xl/workbook.xml':
                raw = raw.replace(b'name="Inputs"', b'name="Renamed"')
            if info.filename == 'xl/worksheets/sheet1.xml':
                raw = raw.replace(b'r="1"', b'r="2"').replace(b'A1', b'A2').replace(b'B1', b'B2')
            after.writestr(info, raw)
    return {'status': 'SIMULATED_ONLY', 'macros_enabled': False}


class StructuralProfiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tca-web-structure-')
        self.root = Path(self.tmp.name)
        self.engine = fixture(self.root / 'original')
        self.profile = initial_profile(self.engine, self.engine.template_path)

    def tearDown(self):
        self.tmp.cleanup()

    def ops(self):
        return [{'type': 'insert_rows', 'sheet': 'Inputs', 'index': 1, 'count': 1,
                 'evidence_id': 'fake-source', 'reason': 'Fictitious structural test'},
                {'type': 'rename_sheet', 'sheet': 'Inputs', 'name': 'Renamed'}]

    def test_mapping_round_trip_and_inserted_cell_not_previous_owner(self):
        _, profile = plan_operations(self.profile, self.ops())
        self.assertEqual(map_location(profile, 'Inputs', 'A1')['cell'], 'A2')
        self.assertEqual(map_location(profile, 'Renamed', 'A2', reverse=True)['sheet'], 'Inputs')
        self.assertIsNone(map_location(profile, 'Renamed', 'A1', reverse=True))
        self.assertEqual(profile['fields'][0]['cells'], ['A2'])
        self.assertEqual(profile['fields'][0]['sheet'], 'Renamed')
        self.assertEqual(self.profile['sheets'][0]['id'], profile['sheets'][0]['id'])

    def test_sequential_targets_track_new_sheet_rename_rows_columns_and_overwrite(self):
        ops = [{'type':'add_sheet','name':'New','role':'Fictitious custom analysis'},
               {'type':'set_value','sheet':'New','cell':'B2','value':7,'evidence_id':'fake'},
               {'type':'insert_rows','sheet':'New','index':2,'count':1},
               {'type':'insert_columns','sheet':'New','index':2,'count':2},
               {'type':'rename_sheet','sheet':'New','name':'Later'},
               {'type':'set_value','sheet':'Later','cell':'D3','value':9,'evidence_id':'fake'}]
        targets = operation_targets(self.profile, ops)
        self.assertEqual((targets[0]['sheet'], targets[0]['cell']), ('Later','D3'))
        self.assertTrue(targets[0]['superseded'])
        self.assertFalse(targets[1]['superseded'])
        self.assertEqual(targets[0]['operation_index'], 1)

    def test_deleted_targets_are_explicit_not_adjacent_cells(self):
        ops = [{'type':'set_value','sheet':'Inputs','cell':'A1','value':7,'evidence_id':'fake'},
               {'type':'delete_rows','sheet':'Inputs','index':1,'count':1}]
        target = operation_targets(self.profile, ops)[0]
        self.assertTrue(target['deleted']); self.assertIsNone(target['cell'])
        _, profile = plan_operations(self.profile, ops)
        self.assertTrue(profile['deleted_owners'])

    def test_invalid_requests_and_external_formula_are_refused(self):
        cases = [{'type':'insert_rows','sheet':'Inputs','index':True,'count':1},
                 {'type':'rename_sheet','sheet':'Inputs','name':'Control'},
                 {'type':'set_formula','sheet':'Inputs','cell':'A1','formula':'WEBSERVICE("https://example.invalid")','evidence_id':'fake'},
                 {'type':'set_formula','sheet':'Inputs','cell':'A1','formula':'[Book]Sheet!A1','evidence_id':'fake'},
                 {'type':'delete_rows','sheet':'Inputs','index':0,'count':1}]
        for operation in cases:
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                plan_operations(self.profile, [operation])

    def test_forward_sheet_reference_is_refused_before_excel_can_create_external_link(self):
        setter={'type':'set_formula','sheet':'Inputs','cell':'B1','formula':"'Future sheet'!A1",'evidence_id':'fake'}
        create={'type':'add_sheet','name':'Future sheet','role':'Fictitious future analysis'}
        with self.assertRaisesRegex(ValueError,'avant cette formule'):
            plan_operations(self.profile,[setter,create])
        operations,_=plan_operations(self.profile,[create,setter])
        self.assertEqual(operations[1]['formula'],setter['formula'])
        plan_operations(self.profile,[{**setter,'formula':'"Missing sheet!A1"'}])

    def test_new_external_link_components_and_retargeted_relationships_are_blocked(self):
        def linked(source,output,operations,**kwargs):
            with zipfile.ZipFile(source) as before,zipfile.ZipFile(output,'w') as after:
                for info in before.infolist():after.writestr(info,before.read(info.filename))
                after.writestr('xl/externalLinks/externalLink1.xml',
                    '<externalLink xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>')
                after.writestr('xl/externalLinks/_rels/externalLink1.xml.rels',
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/externalLinkPath" '
                    'Target="file:///fictitious/source.xlsx" TargetMode="External"/></Relationships>')
            return {}
        setter={'type':'set_formula','sheet':'Inputs','cell':'B1','formula':'A1*2','evidence_id':'fake'}
        output=self.root/'linked.xlsm'
        result=prepare_variant(self.engine.template_path,output,self.profile,[setter],runner=linked)
        self.assertTrue(result['blocked'])
        diagnostic=next(d for d in result['diagnostics'] if d['code']=='NEW_EXTERNAL_LINK')
        self.assertEqual(diagnostic['parts'],['xl/externalLinks/externalLink1.xml'])
        self.assertEqual(len(diagnostic['relationships']),1)
        unchanged=prepare_variant(output,self.root/'unchanged-link.xlsm',result['profile'],[setter],
            runner=lambda source,target,*args,**kwargs:(shutil.copyfile(source,target) and {}))
        self.assertFalse(unchanged['blocked'])
        def retarget(source,target,*args,**kwargs):
            with zipfile.ZipFile(source) as before,zipfile.ZipFile(target,'w') as after:
                for info in before.infolist():
                    raw=before.read(info.filename)
                    if info.filename.endswith('externalLink1.xml.rels'):
                        raw=raw.replace(b'file:///fictitious/source.xlsx',b'file:///fictitious/different.xlsx')
                    after.writestr(info,raw)
            return {}
        changed=prepare_variant(output,self.root/'retargeted.xlsm',result['profile'],[setter],runner=retarget)
        self.assertIn('NEW_EXTERNAL_LINK',{d['code'] for d in changed['diagnostics']})

    def test_profile_history_does_not_duplicate_literal_source_answers(self):
        _, result = plan_operations(self.profile, [{'type':'set_value','sheet':'Inputs','cell':'A1','value':'private-answer','evidence_id':'fake'}])
        self.assertNotIn('private-answer', canonical(result))

    def test_large_preview_keeps_complete_hashed_manifest_and_bounded_samples(self):
        repairs=[{'sheet':'Inputs','cell':'B'+str(i+1),'before':'1','after':'2'} for i in range(30)]
        def runner(source,output,operations,**kwargs):
            result=move_fixture(source,output,operations,**kwargs)
            return {**result,'reference_repairs':deepcopy(repairs)}
        output=self.root/'details.xlsm'
        with patch('tca_bp.formula_bindings.structural_index_repairs',return_value=deepcopy(repairs)):
            result=prepare_variant(self.engine.template_path,output,self.profile,self.ops(),runner=runner)
        details=result['preview_details'];path=output.parent/details['filename']
        complete=json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(details['sha256'],digest(path))
        self.assertEqual(details['size'],path.stat().st_size)
        self.assertEqual(details['total_changes'],32)
        self.assertEqual(details['index_repairs'],30)
        self.assertEqual(len(complete['reference_repairs']),30)
        self.assertEqual(len(result['reference_repairs']),10)
        self.assertIn('final',complete['reference_repairs'][0])
        self.assertNotIn('reference_repairs',result['validation']['native'])

    def test_native_formula_matrices_never_include_unrequested_neighbours(self):
        positions=[('Inputs','B1'),('Inputs','C1'),('Inputs','E1'),('Inputs','F1'),
                   ('Inputs','F2'),('Other','G2'),('Inputs','H2'),('Inputs','H2')]
        repairs=[{'sheet':s,'cell':c} for s,c in positions]
        self.assertEqual(_repair_groups(repairs),[[0,1],[2,3],[4],[5],[6],[7]])

    def test_variant_seal_adapter_inspection_apply_and_remap(self):
        source_sha = digest(self.engine.template_path)
        output = self.root / 'preview.xlsm'
        result = prepare_variant(self.engine.template_path, output, self.profile, self.ops(), runner=move_fixture)
        self.assertFalse(result['blocked'])
        seal_profile_model(self.engine, output, result['profile'], self.root / 'variant')
        candidate = ProfileEngine(self.root, self.root / 'variant')
        self.assertEqual(candidate.inspect(output, 'Renamed', ['B2'])['cells']['B2']['current']['formula'], 'A2*2')
        self.assertEqual(candidate.catalog()[0]['cells'], ['A2'])
        states = candidate.remap_states_from(self.engine, {'Inputs!A1': {'value': 5, 'source_id':'fake'}})
        self.assertEqual(states['Renamed!A2']['source_id'], 'fake')
        context = candidate.context(output)
        self.assertEqual(context['active_years'], 3)
        snapshot = candidate.qualification_snapshot(output)
        self.assertIn('Inputs!A1', snapshot['cells'])
        plan = candidate.prepare(output, [{'sheet':'Renamed','cell':'A2','value':7,'reason':'Fictitious source answer','evidence':'fake'}])
        receipt = candidate.apply(output, plan, self.root / 'applied.xlsm')
        self.assertTrue(receipt['source_unchanged'])
        self.assertEqual(candidate.inspect(self.root/'applied.xlsm','Renamed',['A2'])['cells']['A2']['current']['value'], 7)
        self.assertEqual(digest(self.engine.template_path), source_sha)
        with self.assertRaises(ValueError):
            candidate.prepare(output, [{'sheet':'Renamed','cell':'A2','value':101,'reason':'Fictitious source answer','evidence':'fake'}])

    def test_stale_profile_existing_output_and_noop_runner_for_setter_refused(self):
        bad = seal_profile({**self.profile, 'current_workbook_sha256':'0'*64})
        with self.assertRaisesRegex(ValueError, 'révision'):
            prepare_variant(self.engine.template_path, self.root/'a.xlsm', bad, self.ops(), runner=move_fixture)
        def noop(source, output, operations, **kwargs): shutil.copyfile(source, output); return {'status':'SIMULATED_ONLY'}
        result = prepare_variant(self.engine.template_path,self.root/'b.xlsm',self.profile,
            [{'type':'set_value','sheet':'Inputs','cell':'A1','value':7,'evidence_id':'fake'}],runner=noop)
        self.assertTrue(result['blocked'])
        self.assertIn('VALUE_NOT_PERSISTED', {x['code'] for x in result['diagnostics']})
        with self.assertRaises(ValueError):
            prepare_variant(self.engine.template_path,self.root/'b.xlsm',self.profile,self.ops(),runner=noop)

    def test_vba_changed_opaque_binary_is_not_approved(self):
        self.assertTrue(vba_preservation(b'fake', b'fake')['preserved'])
        self.assertFalse(vba_preservation(b'fake', b'changed')['preserved'])

    def test_new_local_sheet_states_survive_a_second_variant_then_delete(self):
        from types import SimpleNamespace
        _, first=plan_operations(self.profile,[{'type':'add_sheet','name':'Custom','role':'Fictitious analysis'}])
        _, second=plan_operations(first,[{'type':'insert_rows','sheet':'Custom','index':2,'count':3},
                                       {'type':'rename_sheet','sheet':'Custom','name':'Custom later'}])
        old=SimpleNamespace(profile=first); current=SimpleNamespace(profile=second)
        states={'Custom!B2':{'value':7,'source_id':'fake'}}
        mapped=ProfileEngine.remap_states_from(current,old,states)
        self.assertEqual(mapped,{'Custom later!B5':states['Custom!B2']})
        _, third=plan_operations(second,[{'type':'delete_rows','sheet':'Custom later','index':5,'count':1}])
        newest=SimpleNamespace(profile=third)
        self.assertEqual(ProfileEngine.remap_states_from(newest,current,mapped),{})
        self.assertEqual(newest.last_state_remap['removed_current_bindings'],['Custom later!B5'])

    def test_history_states_with_absent_or_malformed_coordinates_are_retained_as_removed(self):
        from types import SimpleNamespace
        _,after=plan_operations(self.profile,self.ops())
        current=SimpleNamespace(profile=after);old=SimpleNamespace(profile=self.profile)
        states={'Gone!B2':{'value':1},'no-address':{'value':2},'Inputs!bad':{'value':3},'Inputs!A1':{'value':4}}
        self.assertEqual(ProfileEngine.remap_states_from(current,old,states),{'Renamed!A2':{'value':4}})
        self.assertEqual(current.last_state_remap['removed_current_bindings'],['Gone!B2','no-address','Inputs!bad'])
        divergent=deepcopy(after);divergent['sheets'][0]['transforms']=[]
        with self.assertRaisesRegex(ValueError,'chaîne'):
            map_between_profiles(after,divergent,'Renamed','A2')

    def test_deleted_native_output_blocks_preview_and_seal_without_a_ref_error(self):
        from tca_bp.web_model_profile import refresh_profile
        before=deepcopy(self.profile)
        before['origin_schema']['native_outputs']={'Inputs':['B1']}
        before=refresh_profile(before)
        self.engine.profile=before
        def noop(source,output,operations,**kwargs):shutil.copyfile(source,output);return {}
        result=prepare_variant(self.engine.template_path,self.root/'native-anchor.xlsm',before,
            [{'type':'delete_columns','sheet':'Inputs','index':2,'count':1}],runner=noop)
        self.assertTrue(result['blocked'])
        self.assertIn('NATIVE_ANCHOR_DELETED',{d['code'] for d in result['diagnostics']})
        self.assertFalse(result['profile']['deleted_owners'])
        with self.assertRaisesRegex(ValueError,'ancrages'):
            seal_profile_model(self.engine,self.root/'native-anchor.xlsm',result['profile'],self.root/'bad-native-model')

    def test_same_formula_not_written_does_not_pass_existing_formula_check(self):
        def noop(source,output,operations,**kwargs):shutil.copyfile(source,output);return {}
        result=prepare_variant(self.engine.template_path,self.root/'bad_formula.xlsm',self.profile,
            [{'type':'set_formula','sheet':'Inputs','cell':'B1','formula':'A1*99','evidence_id':'fake'}],runner=noop)
        self.assertTrue(result['blocked'])
        self.assertIn('FORMULA_DIFFERS_FROM_PROPOSAL',{x['code'] for x in result['diagnostics']})

    def test_edited_owner_cannot_inherit_established_field_semantics(self):
        def replace(source,output,operations,**kwargs):
            with zipfile.ZipFile(source) as before,zipfile.ZipFile(output,'w') as after:
                for info in before.infolist():
                    raw=before.read(info.filename)
                    if info.filename=='xl/worksheets/sheet1.xml':raw=raw.replace(b'<c r="A1"/>',b'<c r="A1"><f>9*3</f></c>')
                    after.writestr(info,raw)
            return {}
        result=prepare_variant(self.engine.template_path,self.root/'formula.xlsm',self.profile,
            [{'type':'set_formula','sheet':'Inputs','cell':'A1','formula':'9*3','evidence_id':'fake'}],runner=replace)
        self.assertFalse(result['blocked'])
        self.assertEqual(result['profile']['fields'][0]['semantics']['status'],'REEXAMEN_REQUIS')
        self.assertIn('Inputs!A1',result['profile']['mechanical_owner_changes'])

    def test_loss_of_sheet_protection_is_a_blocking_diagnostic(self):
        # Start from a fixture with protection so the fake runner can drop it.
        source=self.root/'protected.xlsm'
        with zipfile.ZipFile(self.engine.template_path) as before,zipfile.ZipFile(source,'w') as after:
            for info in before.infolist():
                raw=before.read(info.filename)
                if info.filename=='xl/worksheets/sheet1.xml':raw=raw.replace(b'</worksheet>',b'<sheetProtection sheet="1"/></worksheet>')
                after.writestr(info,raw)
        profile=seal_profile({**self.profile,'current_workbook_sha256':digest(source)})
        def lose(source,output,operations,**kwargs):shutil.copyfile(self.engine.template_path,output);return {}
        result=prepare_variant(source,self.root/'unprotected.xlsm',profile,
             [{'type':'set_formula','sheet':'Inputs','cell':'B1','formula':'A1*2','evidence_id':'fake'}],runner=lose)
        self.assertTrue(result['blocked'])
        self.assertIn('SHEET_PROTECTION_CHANGED',{x['code'] for x in result['diagnostics']})

    def test_native_serialization_does_not_leave_old_formula_cache_available(self):
        def cached(source,output,operations,**kwargs):
            with zipfile.ZipFile(source) as before,zipfile.ZipFile(output,'w') as after:
                for info in before.infolist():
                    raw=before.read(info.filename)
                    if info.filename=='xl/worksheets/sheet1.xml':raw=raw.replace(b'<f>A1*2</f>',b'<f>A1*2</f><v>999</v>')
                    after.writestr(info,raw)
            return {}
        result=prepare_variant(self.engine.template_path,self.root/'cached.xlsm',self.profile,
            [{'type':'set_formula','sheet':'Inputs','cell':'B1','formula':'A1*2','evidence_id':'fake'}],runner=cached)
        self.assertFalse(result['blocked'])
        wb=core.Workbook(self.root/'cached.xlsm')
        try:self.assertIsNone(wb.value('Inputs','B1'))
        finally:wb.close()
        self.assertTrue(result['validation']['native']['formula_chart_and_native_caches_invalidated'])

    def test_seal_refuses_redefined_original_business_contract(self):
        output=self.root/'preview.xlsm'
        result=prepare_variant(self.engine.template_path,output,self.profile,self.ops(),runner=move_fixture)
        forged=deepcopy(result['profile']);forged['origin_schema']['cells']['Inputs']['A1']['max']=999
        forged=seal_profile(forged)
        with self.assertRaisesRegex(ValueError,'origine'):
            seal_profile_model(self.engine,output,forged,self.root/'forged')

    def test_standard_application_saisie_remains_operational_after_web_relocation(self):
        from tca_bp.service import Application
        from tca_bp.web_workspace import WebWorkspace
        app=Application(self.root,self.root/'data',engine=self.engine)
        app.create_case('Fictitious client','Compatibility',case_id='compatibility')
        web=WebWorkspace(app,variant_runner=move_fixture)
        try:
            operations=[{k:v for k,v in op.items() if k!='evidence_id'} for op in self.ops()]
            draft=web.add_operations('compatibility',operations,{'sheet':'Inputs','allow_structure':True})
            # Use an actual case source instead of the test helper's source ID.
            # The web route has attached its own explicit manual source.
            with patch('tca_bp.web_workspace.excel_lock', nullcontext):
                preview=web.preview('compatibility',draft['id'])
            web.apply('compatibility',draft['id'],preview['approval_token'])
            source=app.add_source('compatibility',text='Fictitious amount 7 for compatibility test.')
            plan=app.prepare_changes('compatibility',[{'field_id':'amount','value':7,
                'reason':'Fictitious sourced amount','evidence':source['id'],'status':'CONFIRME'}],'legacy-after-web')
            app.apply_plan('compatibility',plan['id'])
            self.assertEqual(app.inspect('compatibility','Renamed',['A2'])['cells']['A2']['current']['value'],7)
        finally:web.close()

    def test_missing_literal_sheet_reference_is_blocked_even_without_ref_error(self):
        from tca_bp.web_structure import workbook_diagnostics
        output=self.root/'missing.xlsm'
        with zipfile.ZipFile(self.engine.template_path) as before,zipfile.ZipFile(output,'w') as after:
            for info in before.infolist():
                raw=before.read(info.filename).replace(b'A1*2',b'Ghost!A1*2')
                after.writestr(info,raw)
        errors=workbook_diagnostics(output)['errors']
        self.assertIn('MISSING_SHEET_REFERENCE',{item['code'] for item in errors})

    def test_orphan_or_duplicate_shared_formula_anchor_has_explicit_diagnostic(self):
        from tca_bp.web_structure import workbook_diagnostics
        for member in (b'<f t="shared" si="0"/>',b'<f t="shared" si="0" ref="B1:B2">A1*2</f>'):
            output=self.root/('shared'+str(len(member))+'.xlsm')
            with zipfile.ZipFile(self.engine.template_path) as before,zipfile.ZipFile(output,'w') as after:
                for info in before.infolist():
                    raw=before.read(info.filename)
                    if info.filename=='xl/worksheets/sheet1.xml':
                        replacement=member if not b'ref=' in member else member+b'</c><c r="C1">'+member
                        raw=raw.replace(b'<f>A1*2</f>',replacement)
                    after.writestr(info,raw)
            self.assertIn('INVALID_SHARED_FORMULA_GROUP',{e['code'] for e in workbook_diagnostics(output)['errors']})

    def test_deletion_does_not_authorize_a_validation_loss_on_another_sheet(self):
        source=self.root/'validated.xlsm'
        with zipfile.ZipFile(self.engine.template_path) as before,zipfile.ZipFile(source,'w') as after:
            for info in before.infolist():
                raw=before.read(info.filename)
                if info.filename=='xl/worksheets/sheet2.xml':
                    raw=raw.replace(b'</worksheet>',b'<dataValidations><dataValidation type="whole" sqref="D2"><formula1>1</formula1></dataValidation></dataValidations></worksheet>')
                after.writestr(info,raw)
        profile=seal_profile({**self.profile,'current_workbook_sha256':digest(source)})
        def lose(source,output,operations,**kwargs):shutil.copyfile(self.engine.template_path,output);return {}
        result=prepare_variant(source,self.root/'lost.xlsm',profile,[{'type':'delete_rows','sheet':'Inputs','index':5,'count':1}],runner=lose)
        self.assertTrue(result['blocked'])
        loss=[d for d in result['diagnostics'] if d['code']=='COMPONENT_LOST' and d.get('sheet')=='Control']
        self.assertEqual(loss[0]['severity'],'ERROR')

    def test_range_deletion_checks_interior_not_just_both_corners(self):
        from tca_bp.web_structure import _range_survives
        self.assertTrue(_range_survives('A1:A100',[{'type':'delete_rows','index':100,'count':1},{'type':'delete_rows','index':1,'count':1}]))
        self.assertFalse(_range_survives('A1:A100',[{'type':'delete_rows','index':1,'count':100}]))


if __name__ == '__main__': unittest.main()
