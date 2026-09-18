"""Calendar repair boundaries; XML fixtures do not claim native calculation."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from xml.sax.saxutils import escape

from tests.test_wacc_fingerprint_migration import fixture,xml_runner
from tca_bp.dcf_calendar_migration import (OWNERS,plan_calendar_migration,prepare_calendar_variant,
                                         expected_formulas,verified_calendar_exemptions,certificate_calendar_change)
from tca_bp.model_engine import ModelEngine
from tca_bp.storage import atomic_json,digest
from tca_bp.vendor import input_engine as core
from tca_bp.web_model import ProfileEngine
from tca_bp.web_model_profile import initial_profile,seal_profile
from tca_bp.web_structure import plan_operations


class CalendarMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='tca-calendar-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);base=fixture(self.root/'original')
        target=self.root/'with-calendar.xlsm'
        with zipfile.ZipFile(base.template_path) as before,zipfile.ZipFile(target,'w') as after:
            for info in before.infolist():
                raw=before.read(info.filename)
                if info.filename=='xl/worksheets/sheet1.xml':
                    cells=''.join('<c r="'+c+'33"><f>'+escape(c+'26*'+c+'32*MAX(0,MIN(1,'+c+'31))')+'</f></c>' for c in 'DEFGHIJKLM')
                    raw=raw.replace(b'</sheetData>',('<row r="33">'+cells+'</row><row r="34"><c r="D34"><f>SUM(D33:M33)</f></c></row>'
                        '<row r="35"><c r="D35"><f>"\'Control\'!"</f></c></row></sheetData>').encode())
                after.writestr(info,raw)
        target.replace(base.template_path)
        schema_path=base.model_dir/'modele.json';build_path=base.model_dir/'build_receipt.json'
        schema=json.loads(schema_path.read_text(encoding='utf-8'))
        wb=core.Workbook(base.template_path)
        try:schema['signature']=wb.semantic_signature(schema)
        finally:wb.close()
        schema['template_sha256']=digest(base.template_path);atomic_json(schema_path,schema)
        atomic_json(build_path,{'model_id':schema['model_id'],'template_sha256':digest(base.template_path),'schema_sha256':digest(schema_path)})
        self.engine=ModelEngine(self.root,base.model_dir)

    def test_exact_ten_formulas_preserve_active_errors_and_all_horizons(self):
        plan=plan_calendar_migration(self.engine,self.engine.template_path,'source')
        self.assertEqual(plan['status'],'PROPOSED');self.assertEqual(len(plan['operations']),10)
        self.assertTrue(all(op['formula'].startswith('=') for op in plan['operations']))
        for item in plan['changes']:
            self.assertTrue(item['new_formula'].endswith(',0,'+item['old_formula']+')'))
            self.assertNotIn('IFERROR',item['new_formula'])
        # Every horizon keeps all active cash-flow terms, including an error;
        # a discarded inactive placeholder never becomes an active assumption.
        sentinel=object()
        for years in range(1,11):
            values=[sentinel if i==0 or i>=years else 72000 for i in range(10)]
            active=[v for i,v in enumerate(values) if 2026+i<=2025+years]
            self.assertEqual(len(active),years);self.assertIs(active[0],sentinel)
        self.assertEqual(digest(self.engine.template_path),plan['source_sha256'])

    def test_sealed_variant_has_narrow_certificate_and_no_native_proof(self):
        result=prepare_calendar_variant(self.engine,self.engine.template_path,self.root/'variant.xlsm',self.root/'model','source',runner=xml_runner)
        self.assertFalse(result['blocked'])
        current=ProfileEngine(self.root,self.root/'model');current.ensure_built()
        wb=current._open(current.template_path)
        try:self.assertEqual(verified_calendar_exemptions(current.profile,wb),set(OWNERS))
        finally:wb.close()
        self.assertFalse(result['profile']['reviewed_financial_migrations'][-1]['native_proof_transfer'])
        self.assertFalse(result['profile']['reviewed_financial_migrations'][-1]['financial_outputs_verified'])
        self.assertEqual(plan_calendar_migration(current,current.template_path,'source')['status'],'ALREADY_MIGRATED')
        item=expected_formulas(result['profile'])[0]
        xml_runner(self.root/'variant.xlsm',self.root/'changed-anchor.xlsm',[
            {'sheet':item['sheet'],'cell':item['cell'],'formula':item['new_formula'].replace('D26','$D$26',1)}])
        altered=core.Workbook(self.root/'changed-anchor.xlsm')
        try:self.assertEqual(verified_calendar_exemptions(result['profile'],altered),set())
        finally:altered.close()

    def test_additional_financial_formula_change_is_not_certified(self):
        def extra(source,output,operations,**kwargs):
            return xml_runner(source,output,[*operations,{'sheet':'Valorisation','cell':'D34','formula':'0'}],**kwargs)
        with self.assertRaisesRegex(ValueError,'hors des dix'):
            prepare_calendar_variant(self.engine,self.engine.template_path,self.root/'bad.xlsm',self.root/'bad-model','source',runner=extra)

    def test_changed_formula_or_forged_metadata_loses_exemption(self):
        result=prepare_calendar_variant(self.engine,self.engine.template_path,self.root/'variant.xlsm',self.root/'model','source',runner=xml_runner)
        profile=result['profile'];wb=core.Workbook(self.root/'variant.xlsm')
        try:
            forged=deepcopy(profile);forged['reviewed_financial_migrations'][0]['qualification_exemptions'].append('Valorisation!D34')
            self.assertEqual(verified_calendar_exemptions(seal_profile(forged),wb),set())
        finally:wb.close()
        xml_runner(self.root/'variant.xlsm',self.root/'tampered.xlsm',[{'sheet':'Valorisation','cell':'D33','formula':'0'}])
        wb=core.Workbook(self.root/'tampered.xlsm')
        try:self.assertEqual(verified_calendar_exemptions(profile,wb),set())
        finally:wb.close()

    def test_calendar_references_follow_sheet_and_row_mapping(self):
        profile=initial_profile(self.engine,self.engine.template_path)
        _,moved=plan_operations(profile,[{'type':'insert_rows','sheet':'Valorisation','index':1,'count':2},
            {'type':'rename_sheet','sheet':'Control','name':'Calendar settings'}])
        first=expected_formulas(moved)[0]
        self.assertEqual(first['cell'],'D35')
        self.assertEqual(first['new_formula'],"IF(D21>'Calendar settings'!C60,0,D28*D34*MAX(0,MIN(1,D33)))")

    def test_ordinary_ten_formula_draft_without_dcf_anchors_is_unchanged(self):
        from tests.test_model_versions import fixture as ordinary_fixture
        engine=ordinary_fixture(self.root/'ordinary')
        profile=initial_profile(engine,engine.template_path)
        operations=[{'type':'set_formula','sheet':'Inputs','cell':'B'+str(i+2),'formula':'=1','evidence_id':'source'} for i in range(10)]
        self.assertIs(certificate_calendar_change(profile,self.root/'not-read-a',self.root/'not-read-b',profile,operations),profile)

    def test_foreign_absolute_reference_or_literal_change_is_not_exempted(self):
        for index,(cell,formula) in enumerate([('D34','SUM($D$33:$M$33)'),('D35','"Control!"')]):
            with self.subTest(cell=cell):
                def extra(source,output,operations,**kwargs):
                    return xml_runner(source,output,[*operations,{'sheet':'Valorisation','cell':cell,'formula':formula}],**kwargs)
                with self.assertRaisesRegex(ValueError,'hors des dix'):
                    prepare_calendar_variant(self.engine,self.engine.template_path,self.root/f'foreign{index}.xlsm',
                        self.root/f'foreign-model{index}','source',runner=extra)


if __name__=='__main__':unittest.main()
