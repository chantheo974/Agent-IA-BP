"""Exact annual aggregation contracts; XML writes are not Excel proof."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import zipfile
from xml.sax.saxutils import escape

from tca_bp.fiscal_calendar_migration import (BLOCKS, OWNERS, expected_formulas,
    plan_fiscal_calendar_migration, prepare_fiscal_calendar_variant,
    certificate_fiscal_calendar_change, verified_fiscal_calendar_exemptions)
from tca_bp.model_engine import ModelEngine
from tca_bp.storage import atomic_json, digest
from tca_bp.vendor import input_engine as core
from tca_bp.web_model import ProfileEngine
from tca_bp.web_model_profile import initial_profile, seal_profile
from tca_bp.web_structure import plan_operations
from tests.test_wacc_fingerprint_migration import xml_runner


def fixture(folder):
    folder.mkdir();template=folder/'TCA_BP_Trame_generique.xlsm'
    names=['ATELIER_CIR_IS','Modèle financier','KPI Dashboard']
    def build(data):
        with zipfile.ZipFile(template,'w') as z:
            sheets=''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i,name in enumerate(names,1))
            z.writestr('xl/workbook.xml',f'<workbook xmlns="{core.NS}" xmlns:r="{core.REL}"><sheets>{sheets}</sheets><calcPr calcMode="autoNoTable"/></workbook>')
            rels=''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="worksheet"/>' for i in range(1,4))
            z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+rels+'</Relationships>')
            for i,name in enumerate(names,1):
                by_row={}
                for cell,formula in data.get(name,{}).items():by_row.setdefault(core.coord(cell)[2],[]).append((cell,formula))
                rows=''.join(f'<row r="{row}">'+''.join(f'<c r="{cell}"><f>{escape(formula)}</f></c>' for cell,formula in items)+'</row>' for row,items in sorted(by_row.items()))
                z.writestr(f'xl/worksheets/sheet{i}.xml',f'<worksheet xmlns="{core.NS}"><sheetData>{rows}</sheetData></worksheet>')
            z.writestr('xl/styles.xml',f'<styleSheet xmlns="{core.NS}"><fills><fill><patternFill patternType="none"/></fill></fills><cellXfs><xf fillId="0"/></cellXfs></styleSheet>')
            z.writestr('xl/vbaProject.bin',b'NONEXECUTABLE_FICTITIOUS_VBA')
    def seal():
        schema={'model_id':'fictitious/fiscal-calendar','template_sha256':digest(template),'cells':{},'fields':[],'registers':{}}
        wb=core.Workbook(template)
        try:schema['signature']=wb.semantic_signature(schema)
        finally:wb.close()
        atomic_json(folder/'modele.json',schema)
        atomic_json(folder/'build_receipt.json',{'model_id':schema['model_id'],'template_sha256':digest(template),'schema_sha256':digest(folder/'modele.json')})
        return ModelEngine(folder.parent,folder)
    build({});engine=seal();profile=initial_profile(engine,template)
    data={name:{} for name in names}
    for item in expected_formulas(profile):data[item['sheet']][item['cell']]=item['old_formula']
    data['ATELIER_CIR_IS']['C35']='C34+1'
    data['ATELIER_CIR_IS']['C36']='"\'BFR\'!"'
    build(data)
    return seal()


class FiscalCalendarMigrationTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='tca-fiscal-calendar-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.engine=fixture(self.root/'original')

    def test_exact_56_formulas_and_december_balance_preserve_selected_errors(self):
        plan=plan_fiscal_calendar_migration(self.engine,self.engine.template_path,'source')
        self.assertEqual(plan['status'],'PROPOSED');self.assertEqual(len(plan['operations']),56)
        self.assertTrue(all(op['formula'].startswith('=') and 'IFERROR' not in op['formula'] for op in plan['operations']))
        formulas={i['owner']:i['new_formula'] for i in plan['changes']}
        self.assertEqual(formulas['ATELIER_CIR_IS!C34'],'SUMPRODUCT(IF(YEAR($N$50:$EO$50)=C$12,$N$52:$EO$52,0))')
        self.assertIn('SUMPRODUCT(IF(',formulas['KPI Dashboard!E68'])
        self.assertIn('_xlfn.AGGREGATE(15,6,',formulas['KPI Dashboard!E68'])
        self.assertEqual(formulas['Modèle financier!C321'],'SUMPRODUCT(IF((YEAR($T$3:$QI$3)=C$3)*(MONTH($T$3:$QI$3)=12),$T321:$QI321,0))')
        # Independent predicate witness: an error in another year is excluded;
        # an error in the selected year or selected December still propagates.
        error=object()
        def selected(values,years,year):return [value if owner==year else 0 for value,owner in zip(values,years)]
        self.assertEqual(selected([120,error],[2026,2027],2026),[120,0])
        self.assertIs(selected([120,error],[2026,2027],2027)[1],error)
        for horizon in range(1,11):
            self.assertEqual(sum(selected([1]*120,[2026+i//12 for i in range(120)],2025+horizon)),12)

    def test_sealed_certificate_and_idempotence(self):
        result=prepare_fiscal_calendar_variant(self.engine,self.engine.template_path,self.root/'out.xlsm',self.root/'model','source',runner=xml_runner)
        self.assertFalse(result['blocked']);current=ProfileEngine(self.root,self.root/'model');current.ensure_built()
        wb=current._open(current.template_path)
        try:self.assertEqual(verified_fiscal_calendar_exemptions(current.profile,wb),set(OWNERS))
        finally:wb.close()
        self.assertEqual(plan_fiscal_calendar_migration(current,current.template_path,'source')['status'],'ALREADY_MIGRATED')
        self.assertFalse(result['profile']['reviewed_financial_migrations'][-1]['native_proof_transfer'])
        item=expected_formulas(result['profile'])[0]
        xml_runner(self.root/'out.xlsm',self.root/'changed-anchor.xlsm',[
            {'sheet':item['sheet'],'cell':item['cell'],'formula':item['new_formula'].replace('$N$50','N$50',1)}])
        altered=core.Workbook(self.root/'changed-anchor.xlsm')
        try:self.assertEqual(verified_fiscal_calendar_exemptions(result['profile'],altered),set())
        finally:altered.close()

    def test_foreign_change_and_forged_certificate_refused(self):
        def extra(source,output,operations,**kwargs):return xml_runner(source,output,[*operations,{'sheet':'ATELIER_CIR_IS','cell':'C35','formula':'0'}],**kwargs)
        with self.assertRaisesRegex(ValueError,'hors des 56'):
            prepare_fiscal_calendar_variant(self.engine,self.engine.template_path,self.root/'bad.xlsm',self.root/'bad-model','source',runner=extra)
        result=prepare_fiscal_calendar_variant(self.engine,self.engine.template_path,self.root/'out.xlsm',self.root/'model','source',runner=xml_runner)
        forged=deepcopy(result['profile']);forged['reviewed_financial_migrations'][-1]['qualification_exemptions'].append('ATELIER_CIR_IS!C35')
        wb=core.Workbook(self.root/'out.xlsm')
        try:self.assertEqual(verified_fiscal_calendar_exemptions(seal_profile(forged),wb),set())
        finally:wb.close()

    def test_mapping_and_ordinary_56_operations_without_anchors(self):
        profile=initial_profile(self.engine,self.engine.template_path)
        _,moved=plan_operations(profile,[{'type':'insert_rows','sheet':'ATELIER_CIR_IS','index':1,'count':2},
            {'type':'rename_sheet','sheet':'ATELIER_CIR_IS','name':'Fiscalité'}])
        first=expected_formulas(moved)[0]
        self.assertEqual(first['cell'],'C36');self.assertEqual(first['new_formula'],'SUMPRODUCT(IF(YEAR($N$52:$EO$52)=C$14,$N$54:$EO$54,0))')
        from tests.test_model_versions import fixture as ordinary_fixture
        engine=ordinary_fixture(self.root/'ordinary');profile=initial_profile(engine,engine.template_path)
        ops=[{'type':'set_formula','sheet':'Inputs','cell':'B'+str(i+2),'formula':'=1','evidence_id':'source'} for i in range(56)]
        self.assertIs(certificate_fiscal_calendar_change(profile,self.root/'not-read-a',self.root/'not-read-b',profile,ops),profile)

    def test_absolute_reference_and_literal_changes_outside_migration_refused(self):
        for index,(cell,formula) in enumerate([('C35','$C$34+1'),('C36','"BFR!"')]):
            with self.subTest(cell=cell):
                def extra(source,output,operations,**kwargs):
                    return xml_runner(source,output,[*operations,{'sheet':'ATELIER_CIR_IS','cell':cell,'formula':formula}],**kwargs)
                with self.assertRaisesRegex(ValueError,'hors des 56'):
                    prepare_fiscal_calendar_variant(self.engine,self.engine.template_path,self.root/f'foreign{index}.xlsm',
                        self.root/f'foreign-model{index}','source',runner=extra)


if __name__=='__main__':unittest.main()
