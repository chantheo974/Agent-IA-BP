"""Technical fingerprint witnesses; simulated OOXML writes are not Excel proof."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from xml.sax.saxutils import escape

from tca_bp.model_engine import ModelEngine
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core
from tca_bp.web_model import ProfileEngine
from tca_bp.web_model_profile import initial_profile, map_location, seal_profile
from tca_bp.web_structure import plan_operations
from tca_bp.wacc_fingerprint_migration import (plan_fingerprint_migration, prepare_fingerprint_variant,
    logical_owners, legacy_element, error_typed_element, _parse_helpers, _chunks, _reference, _owner,
    HELPERS, PREFIX, FORMULA_LIMIT, SEPARATOR, verified_fingerprint_exemptions)


def fixture(folder, profile=None):
    folder.mkdir()
    names = ['Valorisation', 'Control', 'BFR', 'Comparables']
    def mapped(sheet, cell):
        return map_location(profile, sheet, cell) if profile else {'sheet':sheet,'cell':cell}
    current_names = [mapped(name,'A1')['sheet'] for name in names]
    valuation = current_names[0]
    data = {name:{} for name in current_names}
    references = []
    for sheet, cell in logical_owners():
        point = mapped(sheet,cell)
        data[point['sheet']][point['cell']] = '<v>0</v>'
        references.append(_reference(point['sheet'],point['cell'],valuation))
    # Exact audited partition sizes, with empty fourth helper before migration.
    partitions = [references[:124], references[124:218], references[218:], []]
    for logical, refs in zip(HELPERS,partitions):
        data[valuation][mapped('Valorisation',logical)['cell']] = '<f>'+escape(SEPARATOR.join(map(legacy_element,refs)) if refs else '""')+'</f>'
    validity=mapped('Valorisation','D138')['cell']
    helpers=[mapped('Valorisation',cell)['cell'] for cell in HELPERS]
    data[valuation][validity]='<is><t>OK</t></is>'
    data[valuation][mapped('Valorisation','D155')['cell']]='<f>'+escape('IF('+validity+'="OK",'+SEPARATOR.join(helpers)+',"")')+'</f>'
    data[valuation][mapped('Valorisation','D156')['cell']]='<is><t>OLD_FINGERPRINT</t></is>'
    template=folder/'TCA_BP_Trame_generique.xlsm'
    with zipfile.ZipFile(template,'w') as archive:
        sheets=''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i,name in enumerate(current_names,1))
        archive.writestr('xl/workbook.xml',f'<workbook xmlns="{core.NS}" xmlns:r="{core.REL}"><sheets>{sheets}</sheets><calcPr calcMode="autoNoTable"/></workbook>')
        rels=''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="worksheet"/>' for i in range(1,5))
        archive.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+rels+'</Relationships>')
        for i,name in enumerate(current_names,1):
            by_row={}
            for cell,body in data[name].items():
                row=core.coord(cell)[2]
                by_row.setdefault(row,[]).append((core.coord(cell)[1],cell,body))
            rows=''.join(f'<row r="{row}">'+''.join(f'<c r="{cell}"'+(' t="inlineStr"' if body.startswith('<is>') else '')+'>'+body+'</c>' for _,cell,body in sorted(items))+'</row>' for row,items in sorted(by_row.items()))
            archive.writestr(f'xl/worksheets/sheet{i}.xml',f'<worksheet xmlns="{core.NS}"><sheetData>{rows}</sheetData></worksheet>')
        archive.writestr('xl/styles.xml',f'<styleSheet xmlns="{core.NS}"><fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0"/></cellXfs></styleSheet>')
        archive.writestr('xl/vbaProject.bin',b'NONEXECUTABLE_FICTITIOUS_VBA')
    schema={'model_id':'fictitious/fingerprint','template_sha256':digest(template),'cells':{},'fields':[],'registers':{}}
    wb=core.Workbook(template)
    try:schema['signature']=wb.semantic_signature(schema)
    finally:wb.close()
    (folder/'modele.json').write_text(canonical(schema),encoding='utf-8')
    (folder/'build_receipt.json').write_text(canonical({'model_id':schema['model_id'],'template_sha256':digest(template),'schema_sha256':digest(folder/'modele.json')}),encoding='utf-8')
    engine=ModelEngine(folder.parent,folder)
    if profile:
        engine.profile=seal_profile({**profile,'current_workbook_sha256':digest(template)})
    return engine


def xml_runner(source, output, operations, **ignored):
    wb=core.Workbook(source)
    try:
        changes={}
        for op in operations:
            changes.setdefault(wb.sheets[op['sheet']]['part'],{})[op['cell']]=op['formula']
        with zipfile.ZipFile(output,'w') as archive:
            for info in wb.z.infolist():
                raw=wb.z.read(info.filename)
                if info.filename in changes:
                    edits=changes[info.filename]
                    raw=core.CELL_RX.sub(lambda m: ('<c r="'+m[1].decode()+'"><f>'+escape(edits[m[1].decode()])+'</f></c>').encode() if m[1].decode() in edits else m[0],raw)
                archive.writestr(info,raw)
    finally:wb.close()
    return {'status':'SIMULATED_XML_ONLY','macros_enabled':False}


class FingerprintMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='tca-fingerprint-migration-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.engine=fixture(self.root/'original')

    def test_all_263_owners_preserved_in_four_bounded_helpers(self):
        before=digest(self.engine.template_path)
        plan=plan_fingerprint_migration(self.engine,self.engine.template_path,'source_fictive')
        self.assertEqual(plan['reference_count'],263)
        self.assertEqual(len(plan['operations']),5)
        helpers=[c['new_formula'] for c in plan['changes'] if c['logical_cell'] in HELPERS]
        refs,version=_parse_helpers(helpers)
        self.assertEqual(version,2)
        self.assertEqual([_owner(ref,'Valorisation') for ref in refs],logical_owners())
        self.assertTrue(all(len(f)<=FORMULA_LIMIT for f in helpers))
        self.assertTrue(all('"E:"&ERROR.TYPE(' in f for f in helpers))
        self.assertIn(PREFIX,plan['changes'][-1]['new_formula'])
        self.assertEqual(digest(self.engine.template_path),before)
        self.assertFalse(any(c['cell']=='D156' for c in plan['changes']))
        self.assertEqual({op['evidence_id'] for op in plan['operations']},{'source_fictive'})

    def test_reference_order_unknown_formula_and_missing_owner_are_refused(self):
        refs=['A1','A2']
        for formulas in [[legacy_element('A1')+'+1'],[legacy_element('A1'),error_typed_element('A2')],['SUM(A1:A2)']]:
            with self.assertRaises(ValueError):_parse_helpers(formulas)
        profile=initial_profile(self.engine,self.engine.template_path)
        profile['sheets'][0]['deleted']=True
        self.engine.profile=seal_profile(profile)
        with self.assertRaises(ValueError):plan_fingerprint_migration(self.engine,self.engine.template_path,'source')
        # Oversized owner references require a separate structural migration.
        with self.assertRaises(ValueError):_chunks(["'Very long fictitious worksheet'!XFD1048576"]*500)

    def test_error_type_tokens_do_not_discard_other_values(self):
        expr=error_typed_element('G26')
        self.assertEqual(expr,'TYPE(G26)&":"&IFERROR(LEN(G26)&":"&G26,"E:"&ERROR.TYPE(G26))')
        # Independent protocol witness: errors are type16 with distinct error
        # codes; text '#N/A', zero and another normal value remain distinguishable.
        tokens=['16:E:7','16:E:2','2:4:#N/A','1:1:0','1:3:123']
        self.assertEqual(len(set(tokens)),5)
        self.assertIn('1:3:123','|'.join(tokens))
        self.assertNotIn('IFERROR(TYPE',expr)

    def test_relocated_helpers_follow_stable_profile_owners(self):
        profile=initial_profile(self.engine,self.engine.template_path)
        _,moved=plan_operations(profile,[{'type':'insert_rows','sheet':'Valorisation','index':1,'count':2},
                                        {'type':'rename_sheet','sheet':'Valorisation','name':'Valeur déplacée'}])
        moved_engine=fixture(self.root/'moved',moved)
        plan=plan_fingerprint_migration(moved_engine,moved_engine.template_path,'source_fictive')
        self.assertEqual({c['sheet'] for c in plan['changes']},{'Valeur déplacée'})
        self.assertEqual({c['cell'] for c in plan['changes']},{'J157','J158','J159','J160','D157'})
        self.assertIn('IF(D140="OK"',plan['changes'][-1]['new_formula'])

    def test_private_sealed_variant_is_idempotent_and_never_adopted(self):
        source=self.engine.template_path
        before=digest(source)
        result=prepare_fingerprint_variant(self.engine,source,self.root/'preview.xlsm',self.root/'variant','source_fictive',runner=xml_runner)
        self.assertFalse(result['blocked'])
        self.assertFalse(result['adopted'])
        self.assertFalse(result['validation']['financial_outputs_verified'])
        candidate=ProfileEngine(self.root,self.root/'variant')
        plan=plan_fingerprint_migration(candidate,candidate.template_path,'source_fictive')
        self.assertEqual(plan['status'],'ALREADY_MIGRATED')
        self.assertEqual(plan['operations'],[])
        self.assertTrue(candidate.profile['technical_migrations'])
        self.assertEqual(candidate.profile['version'],2)
        self.assertEqual(candidate.profile['parent_profile_sha256'],result['migration']['source_profile_sha256'])
        self.assertEqual(digest(source),before)
        with zipfile.ZipFile(source) as a,zipfile.ZipFile(candidate.template_path) as b:
            self.assertEqual(a.read('xl/vbaProject.bin'),b.read('xl/vbaProject.bin'))
        self.assertNotEqual(candidate.model_id,self.engine.model_id)
        self.assertFalse(json.loads((self.root/'variant/migrations.json').read_text())['automatic_adoption'])

    def test_certificate_exempts_only_live_exact_helpers_and_not_dcf_guards(self):
        result=prepare_fingerprint_variant(self.engine,self.engine.template_path,self.root/'preview.xlsm',self.root/'variant','source_fictive',runner=xml_runner)
        profile=result['profile']
        wb=core.Workbook(self.root/'preview.xlsm')
        try:
            self.assertEqual(verified_fingerprint_exemptions(profile,wb),{'Valorisation!'+c for c in (*HELPERS,'D155')})
            self.assertNotIn('Valorisation!D138',verified_fingerprint_exemptions(profile,wb))
            changed=SimpleNamespace(formula=lambda s,c:'0' if c=='J155' else wb.formula(s,c))
            self.assertEqual(verified_fingerprint_exemptions(profile,changed),set())
            missing=deepcopy(profile);missing['technical_migrations']=[]
            self.assertEqual(verified_fingerprint_exemptions(seal_profile(missing),wb),set())
            forged=deepcopy(profile);forged['technical_migrations'][0]['qualification_exemptions'].append('Valorisation!D138')
            self.assertEqual(verified_fingerprint_exemptions(seal_profile(forged),wb),set())
        finally:wb.close()

    def test_extra_formula_change_cannot_receive_technical_certificate(self):
        def extra_runner(source,output,operations,**kwargs):
            return xml_runner(source,output,[*operations,{'sheet':'Valorisation','cell':'D138','formula':'"OK"'}],**kwargs)
        with self.assertRaisesRegex(ValueError,'cinq helpers'):
            prepare_fingerprint_variant(self.engine,self.engine.template_path,self.root/'preview.xlsm',self.root/'variant','source_fictive',runner=extra_runner)
        self.assertFalse((self.root/'variant').exists())


if __name__=='__main__':unittest.main()
