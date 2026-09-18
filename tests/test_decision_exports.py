import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import zipfile

from tca_bp.decision_exports import identified_copy,read_identity,roundtrip,_signature,_report_calendar,_calendar_questions
from tca_bp.storage import digest
from tests.test_model_versions import fixture

class ReportCalendarTests(unittest.TestCase):
    def inputs(self,date=46023,years=3):
        profile={'company_name':'Entreprise fictive','start_year':2030,'years':5,'activity_start_month':4}
        questions=[{'field_id':'model_start_date','sheet':'Paramètres renommés','cell':'D12','value':date,'value_type':'date'},
                   {'field_id':'active_horizon_years','sheet':'Paramètres renommés','cell':'D61','value':years}]
        periods=[f'{year}-{month:02d}' for year in range(2026,2029) for month in range(1,13)]
        series=[{'id':'cash','categories':periods,'values':[None]*36}]
        annual=[{'period':str(year),'value':120000} for year in range(2026,2029)]
        return profile,questions,series,annual

    def test_calculated_calendar_overrides_pending_profile_only_in_report(self):
        profile,questions,series,annual=self.inputs()
        before=json.dumps([profile,questions,series,annual],sort_keys=True)
        effective,calendar,warnings=_report_calendar(profile,questions,1900,series,annual)
        self.assertEqual((effective['start_year'],effective['years']),(2026,3))
        self.assertEqual(effective['activity_start_month'],4)
        self.assertEqual(calendar['start_date'],'2026-01-01')
        self.assertEqual(calendar['source_fields'][0]['cell'],'D12')
        self.assertEqual(calendar['periods'][-1],'2028-12')
        self.assertEqual(len(warnings),1)
        self.assertEqual(json.dumps([profile,questions,series,annual],sort_keys=True),before)

    def test_1904_and_iso_calendar_keep_the_same_three_year_horizon(self):
        for date,epoch in ((44561,1904),('2026-01-01',1900)):
            with self.subTest(date=date):
                profile,questions,series,annual=self.inputs(date=date)
                profile.update(start_year=2026,years=3)
                effective,calendar,warnings=_report_calendar(profile,questions,epoch,series,annual)
                self.assertEqual((effective['start_year'],effective['years']),(2026,3))
                self.assertEqual(warnings,[])

    def test_real_questionnaire_filter_cannot_hide_renamed_calendar_from_report(self):
        from tca_bp.decision_workspace import DecisionWorkspace
        profile,bindings,series,annual=self.inputs()
        profile['modules']=['sales']
        row={'field_states':'{}'}
        values={(b['sheet'],b['cell']):b['value'] for b in bindings}
        wb=SimpleNamespace(value=lambda sheet,cell:values[(sheet,cell)],formula=lambda *args:None)
        d=DecisionWorkspace.__new__(DecisionWorkspace)
        d.app=SimpleNamespace(_row=lambda case:row,engine_for_case=lambda case:SimpleNamespace(schema={}))
        d.profile=lambda case:profile
        d.bindings=lambda case:bindings
        d.work=SimpleNamespace(_read=lambda case,action:action(wb,row))
        visible=d.questionnaire('renamed')['questions']
        self.assertEqual(visible,[])  # The real guided view filters this renamed sheet.
        calendar_questions=_calendar_questions(d,'renamed',visible)
        effective,calendar,warnings=_report_calendar(profile,calendar_questions,1900,series,annual)
        self.assertEqual((effective['start_year'],effective['years']),(2026,3))
        self.assertEqual(calendar['source_fields'][0]['sheet'],'Paramètres renommés')
        self.assertEqual(visible,[])
        self.assertEqual(profile['years'],5)
        self.assertEqual(_calendar_questions(d,'renamed',calendar_questions),calendar_questions)

    def test_missing_ambiguous_invalid_or_inconsistent_calendar_is_refused(self):
        mutations=[lambda p,q,s,a:q.pop(),lambda p,q,s,a:q.append(dict(q[0])),
                   lambda p,q,s,a:q[0].update(value=60),lambda p,q,s,a:q[0].update(value=True),
                   lambda p,q,s,a:q[0].update(value=46023.5),lambda p,q,s,a:q[0].update(value=float('inf')),
                   lambda p,q,s,a:q[1].update(value=3.5),lambda p,q,s,a:q[1].update(value=True),
                   lambda p,q,s,a:q[1].update(value=None),lambda p,q,s,a:s[0]['categories'].pop(),
                   lambda p,q,s,a:a.pop()]
        for mutate in mutations:
            values=self.inputs();mutate(*values)
            with self.assertRaises(ValueError):_report_calendar(values[0],values[1],1900,values[2],values[3])

class ExportRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        engine=fixture(self.root/'model')
        self.source=engine.template_path
        with zipfile.ZipFile(self.source,'a') as z:
            z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>')
            z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        self.identity={'case_id':'case_a','report_id':'report_a','revision':0,'workbook_sha256':digest(self.source),'snapshot_sha256':'fake-snapshot'}
        self.export=self.root/'export.xlsm'; identified_copy(self.source,self.export,self.identity)
        self.report={'id':'report_a','kind':'report','identity':self.identity,'files':{'xlsm':{'path':'export.xlsm','sha256':digest(self.export)}}}
        self.d=SimpleNamespace(check_revision=lambda c,r:{'revision':0,'sha256':self.identity['workbook_sha256']},
                               get=lambda c,i,k:self.report,store=SimpleNamespace(case_dir=lambda c:self.root),
                               bindings=lambda c:[{'sheet':'Inputs','cell':'A1','kind':'number'}],
                               app=SimpleNamespace(add_source=lambda *a,**k:{'id':'source_1'}),propose=lambda c,ops,r:{'operations':ops,'applied':False})
    def tearDown(self):self.tmp.cleanup()
    def modified(self,name,replace):
        output=self.root/name
        with zipfile.ZipFile(self.export) as src,zipfile.ZipFile(output,'w') as dst:
            for item in src.infolist(): dst.writestr(item,replace(item.filename,src.read(item.filename)))
        return output
    def test_identity_preserves_every_native_binary_and_is_readable(self):
        with zipfile.ZipFile(self.source) as source,zipfile.ZipFile(self.export) as exported:
            self.assertEqual(read_identity(exported),self.identity)
            self.assertEqual(source.read('xl/vbaProject.bin'),exported.read('xl/vbaProject.bin'))
        self.assertEqual(roundtrip(self.d,'case_a',self.export,0)['status'],'IDENTIQUE')
    def test_only_recognized_literal_input_reaches_shared_draft(self):
        path=self.modified('changed.xlsm',lambda part,raw:raw.replace(b'<c r="A1"/>',b'<c r="A1"><v>7</v></c>') if part=='xl/worksheets/sheet1.xml' else raw)
        result=roundtrip(self.d,'case_a',path,0)
        self.assertEqual(result['operations'][0]['value'],7)
        self.assertFalse(result['applied'])
        self.assertEqual(result['operations'][0]['evidence_id'],'source_1')

    def date_binding(self,*,date1904=False,initial=b'<c r="A1"/>'):
        self.d.bindings=lambda c:[{'sheet':'Inputs','cell':'A1','kind':'date','value_type':'date','field_id':'date'}]
        baseline=self.modified('baseline-date.xlsm',lambda part,raw:
            raw.replace(b'<sheets>',b'<workbookPr date1904="'+(b'1' if date1904 else b'0')+b'"/><sheets>') if part=='xl/workbook.xml'
            else raw.replace(b'<c r="A1"/>',initial) if part=='xl/worksheets/sheet1.xml' else raw)
        baseline.replace(self.export)
        self.report['files']['xlsm']['sha256']=digest(self.export)
        self.initial_date_xml=initial

    def changed_date(self,name,literal):
        return self.modified(name,lambda part,raw:raw.replace(self.initial_date_xml,literal) if part=='xl/worksheets/sheet1.xml' else raw)

    def assert_date_prepared(self,serial,iso):
        from tca_bp.web_model_profile import initial_profile,seal_profile
        from tca_bp.web_validation import prepare_native_operations
        path=self.changed_date('date-changed.xlsm',f'<c r="A1"><v>{serial}</v></c>'.encode())
        result=roundtrip(self.d,'case_a',path,0)
        self.assertFalse(result['applied'])
        self.assertEqual(result['operations'][0]['value'],iso)
        self.assertEqual(result['operations'][0]['evidence_id'],'source_1')
        engine=fixture(self.root/('native-preparation-'+str(serial)))
        profile=initial_profile(engine,engine.template_path)
        profile['origin_schema']['cells']['Inputs']['A1']={'kind':'date','fill':None}
        prepared=prepare_native_operations(engine,self.export,seal_profile(profile),result['operations'])
        self.assertEqual(prepared[0]['value'],serial)
        self.assertEqual(result['operations'][0]['value'],iso)

    def test_serial_1900_roundtrip_reaches_native_preparation_once_as_iso(self):
        self.date_binding()
        self.assert_date_prepared(46388,'2027-01-01')
        self.assert_date_prepared(46812,'2028-02-29')
        self.assert_date_prepared(61,'1900-03-01')

    def test_serial_1904_roundtrip_uses_the_workbook_epoch(self):
        self.date_binding(date1904=True)
        self.assert_date_prepared(44926,'2027-01-01')
        self.assert_date_prepared(0,'1904-01-01')
        self.assert_date_prepared(60,'1904-03-01')

    def test_date_clear_and_iso_literal_remain_null_and_iso(self):
        self.date_binding(initial=b'<c r="A1"><v>46388</v></c>')
        cleared=roundtrip(self.d,'case_a',self.changed_date('clear.xlsm',b'<c r="A1"/>'),0)
        self.assertIsNone(cleared['operations'][0]['value'])
        for kind,xml in [('d',b'<c r="A1" t="d"><v>2027-02-01</v></c>'),
                         ('inline',b'<c r="A1" t="inlineStr"><is><t>2027-02-01</t></is></c>')]:
            with self.subTest(kind=kind):
                result=roundtrip(self.d,'case_a',self.changed_date(kind+'.xlsm',xml),0)
                self.assertEqual(result['operations'][0]['value'],'2027-02-01')

    def test_date_encoding_change_alone_creates_no_source_or_draft(self):
        self.date_binding(initial=b'<c r="A1"><v>46388</v></c>')
        self.d.app.add_source=Mock();self.d.propose=Mock()
        for value in [b'<c r="A1"><v>46388.000</v></c>',b'<c r="A1" t="d"><v>2027-01-01</v></c>']:
            result=roundtrip(self.d,'case_a',self.changed_date('same-date.xlsm',value),0)
            self.assertEqual(result['status'],'IDENTIQUE')
        self.d.app.add_source.assert_not_called();self.d.propose.assert_not_called()

    def test_invalid_or_fractional_dates_are_refused_before_any_source_or_draft(self):
        # This initial serial also catches a fraction hidden by float equality.
        self.date_binding(initial=b'<c r="A1"><v>46388</v></c>')
        self.d.app.add_source=Mock();self.d.propose=Mock()
        values=[b'<c r="A1"><v>'+v+b'</v></c>' for v in (
            b'60',b'59',b'-1',b'46388.5',b'46388.00000000000000000001',b'1e9999',b'NaN',b'73416')]
        values += [b'<c r="A1" t="d"><v>'+v+b'</v></c>' for v in (
            b'1900-02-29',b'2027-02-29',b'2027-02-31',b'20270101',b'2027-01-01T12:00:00',b'2101-01-01')]
        values += [b'<c r="A1" t="b"><v>1</v></c>',b'<c r="A1" t="e"><v>#VALUE!</v></c>',
                   b'<c r="A1" t="inlineStr"><is><t>01/02/2027</t></is></c>']
        for value in values:
            with self.subTest(value=value),self.assertRaises(ValueError):
                roundtrip(self.d,'case_a',self.changed_date('invalid-date.xlsm',value),0)
        self.d.app.add_source.assert_not_called();self.d.propose.assert_not_called()

    def test_date_epoch_change_is_still_a_structural_rejection(self):
        self.date_binding()
        path=self.modified('epoch-changed.xlsm',lambda part,raw:raw.replace(b'date1904="0"',b'date1904="1"') if part=='xl/workbook.xml' else raw)
        with self.assertRaisesRegex(ValueError,'structure modifiée'):roundtrip(self.d,'case_a',path,0)

    def formula_output_fixture(self,kind='dataTable',reference='B3:C4',attributes='r1="A2" dt2D="0"'):
        formula=f'<f t="{kind}" ref="{reference}" {attributes}>'+('A1*2' if kind=='array' else '')+'</f>'
        rows=('<row r="2"><c r="A2"><v>1</v></c><c r="B2"><f>A1*2</f><v>2</v></c><c r="C2"><v>5</v></c></row>'
              '<row r="3"><c r="A3"><v>10</v></c><c r="B3">'+formula+'<v>20</v></c><c r="C3"><v>30</v></c></row>'
              '<row r="4"><c r="A4"><v>15</v></c><c r="B4"><v>40</v></c><c r="C4"><v>50</v></c><c r="D4"><v>60</v></c></row>')
        baseline=self.modified('formula-output-baseline.xlsm',lambda part,raw:raw.replace(b'</sheetData>',rows.encode()+b'</sheetData>') if part=='xl/worksheets/sheet1.xml' else raw)
        baseline.replace(self.export)
        self.report['files']['xlsm']['sha256']=digest(self.export)

    def test_data_table_caches_do_not_become_literal_modifications(self):
        self.formula_output_fixture()
        def rewrite(part,raw):
            if part!='xl/worksheets/sheet1.xml':return raw
            raw=raw.replace(b'<c r="A1"/>',b'<c r="A1"><v>7</v></c>')
            for value in (20,30,40,50):raw=raw.replace(f'<v>{value}</v>'.encode(),f'<v>{value+1}</v>'.encode())
            return raw
        result=roundtrip(self.d,'case_a',self.modified('table-calculated.xlsm',rewrite),0)
        self.assertEqual([(op['cell'],op['value']) for op in result['operations']],[('A1',7)])
        self.assertFalse(result['applied'])

    def test_array_caches_are_ignored_but_recognized_inputs_are_never_hidden(self):
        self.formula_output_fixture(kind='array',attributes='')
        path=self.modified('array-calculated.xlsm',lambda p,b:b.replace(b'<v>50</v>',b'<v>55</v>') if p=='xl/worksheets/sheet1.xml' else b)
        self.assertEqual(roundtrip(self.d,'case_a',path,0)['status'],'IDENTIQUE')
        self.d.bindings=lambda c:[{'sheet':'Inputs','cell':'C4','kind':'number'}]
        result=roundtrip(self.d,'case_a',path,0)
        self.assertEqual([(op['cell'],op['value']) for op in result['operations']],[('C4',55)])

    def test_table_drivers_axes_unknown_literals_and_formula_changes_still_refused(self):
        self.formula_output_fixture()
        replacements=[(b'<v>1</v>',b'<v>2</v>'),(b'<v>5</v>',b'<v>6</v>'),(b'<v>10</v>',b'<v>11</v>'),
                      (b'<v>60</v>',b'<v>61</v>'),(b'r1="A2"',b'r1="A3"'),(b'ref="B3:C4"',b'ref="B3:D4"'),
                      (b'A1*2',b'A1*3'),(b'<f t="dataTable" ref="B3:C4" r1="A2" dt2D="0"></f>',b'')]
        for before,after in replacements:
            with self.subTest(before=before),self.assertRaises(ValueError):
                path=self.modified('table-damaged.xlsm',lambda p,b:b.replace(before,after) if p=='xl/worksheets/sheet1.xml' else b)
                roundtrip(self.d,'case_a',path,0)

    def test_unknown_broad_and_misanchored_formula_ranges_grant_no_exemption(self):
        # Independent fixtures keep each malformed original identical to its
        # imported structure: the cache exemption itself must fail closed.
        for reference in ('B3:XFD1048576','A1:C4','invalid','B3:C1048577'):
            with self.subTest(reference=reference):
                original=self.export.read_bytes()
                try:
                    self.formula_output_fixture(reference=reference)
                    path=self.modified('invalid-ref.xlsm',lambda p,b:b.replace(b'<v>50</v>',b'<v>55</v>') if p=='xl/worksheets/sheet1.xml' else b)
                    with self.assertRaisesRegex(ValueError,'Entrée non reconnue'):roundtrip(self.d,'case_a',path,0)
                finally:
                    self.export.write_bytes(original)
                    self.report['files']['xlsm']['sha256']=digest(self.export)

    def test_formula_unrecognized_input_foreign_case_and_vba_changes_refused(self):
        cases=[('formula.xlsm',lambda p,b:b.replace(b'A1*2',b'A1*3') if p=='xl/worksheets/sheet1.xml' else b),
               ('unknown.xlsm',lambda p,b:b.replace(b'<v>3</v>',b'<v>4</v>') if p=='xl/worksheets/sheet2.xml' else b),
               ('vba.xlsm',lambda p,b:b'CHANGED' if p=='xl/vbaProject.bin' else b)]
        for name,rewrite in cases:
            with self.subTest(name=name),self.assertRaises(ValueError):roundtrip(self.d,'case_a',self.modified(name,rewrite),0)
        with self.assertRaisesRegex(ValueError,'autre dossier'):roundtrip(self.d,'case_b',self.export,0)

    def test_native_merge_order_and_recalculation_flags_are_semantically_identical(self):
        from tca_bp.vendor.input_engine import Workbook
        def edit(part,raw,reverse=False,changed=False):
            if part!='xl/worksheets/sheet1.xml': return raw
            merges=b'<mergeCells count="2"><mergeCell ref="A4:B4"/><mergeCell ref="A5:B5"/></mergeCells>'
            if reverse: merges=b'<mergeCells count="2"><mergeCell ref="A5:B5"/><mergeCell ref="A4:B4"/></mergeCells>'
            raw=raw.replace(b'</worksheet>',merges+b'</worksheet>')
            raw=raw.replace(b'<f>',b'<f ca="1">' if not reverse else b'<f>')
            return raw.replace(b'A1*2',b'A1*3') if changed else raw
        paths=[self.modified(name,lambda p,b,reverse=rev,changed=chg:edit(p,b,reverse,changed))
               for name,rev,chg in [('before.xlsm',False,False),('saved.xlsm',True,False),('formula-changed.xlsm',True,True)]]
        books=[Workbook(p) for p in paths]
        try:
            self.assertEqual(_signature(books[0]),_signature(books[1]))
            self.assertNotEqual(_signature(books[0]),_signature(books[2]))
        finally:
            for book in books:book.close()
