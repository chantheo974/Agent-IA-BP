"""Boundary tests for the generic writer and its generated template."""
from pathlib import Path
import copy
import json
import os
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET
from tca_bp.model_engine import ModelEngine
from tca_bp.model_build import invalidate_caches, invalidate_chart, serialize_xml, formula_references, SOURCE_SHA
from tca_bp.vendor import input_engine as core

ROOT=Path(__file__).resolve().parents[1]


class CalendarBoundary(unittest.TestCase):
    def test_missing_horizon_is_a_refusal_not_type_error(self):
        class W:
            def value(self,s,a):return None if (s,a)==('Control','C59') else 10
        with self.assertRaisesRegex(ValueError,'Horizon actif requis'):
            core.business_checks(W(),{},[])

    def test_false_is_not_a_numeric_horizon(self):
        class W:
            def value(self,s,a):return False
        with self.assertRaises(ValueError):core.business_checks(W(),{},[])

    def test_explicit_zero_manual_cost_is_valid_but_missing_negative_or_bool_is_not(self):
        class W:
            def __init__(self,cost):self.cost=cost
            def value(self,s,a):
                return {('Control','C59'):3,('DATA COGS','D15'):'Manuel',('DATA COGS','L15'):self.cost}.get((s,a))
        schema={'cells':{'DATA COGS':{'D15':{}}}}
        changes=[{'sheet':'DATA COGS','cell':'D15','value':'Manuel','kind':'text'}]
        core.business_checks(W(0),schema,changes)
        for invalid in (None,-1,False):
            with self.subTest(cost=invalid),self.assertRaises(ValueError):core.business_checks(W(invalid),schema,changes)

    def test_explicit_missing_variant_never_builds_from_local_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            engine=ModelEngine(ROOT,model_dir=Path(folder)/'missing')
            with self.assertRaisesRegex(ValueError,'aucune reconstruction implicite'):engine.ensure_built()
            self.assertFalse(engine.model_dir.exists())

    def test_serialization_retains_markup_compatibility_prefix_bindings(self):
        source=b'<root xmlns="urn:root" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:x="urn:future" mc:Ignorable="x"><mc:Choice Requires="x"/></root>'
        output=serialize_xml(ET.fromstring(source),source)
        self.assertIn(b'xmlns:x="urn:future"',output)
        self.assertIn(b'Requires="x"',output)
        ET.fromstring(output)
        empty=b'<root xmlns="urn:root" xmlns:x="urn:future"/>'
        ET.fromstring(serialize_xml(ET.fromstring(empty),empty))

    def test_graph_indexes_local_references_and_ignores_quoted_text(self):
        refs=formula_references('SUM(A1:B3)+YEAR(Control!$C$10)+IF(C4="D5",0,\'DATA COGS\'!E15)','Sheet')
        self.assertEqual(refs,["'Sheet'!A1:B3","'Control'!$C$10","'Sheet'!C4","'DATA COGS'!E15"])

    def test_caches_removed_without_rewriting_formula_or_constant(self):
        raw=b'<row r="1"><c r="A1"><f>SUM(B1:C1)</f><v>999999</v></c><c r="B1"><v>2</v></c></row>'
        updated=invalidate_caches(raw)
        self.assertIn(b'<f>SUM(B1:C1)</f>',updated)
        self.assertNotIn(b'999999',updated)
        self.assertIn(b'<c r="B1"><v>2</v></c>',updated)

    def test_chart_cache_removed_but_source_reference_retained(self):
        raw=b'<c:numRef><c:f>Sheet1!A1:A2</c:f><c:numCache><c:pt idx="0"><c:v>99</c:v></c:pt></c:numCache></c:numRef>'
        self.assertEqual(invalidate_chart(raw),b'<c:numRef><c:f>Sheet1!A1:A2</c:f></c:numRef>')


@unittest.skipUnless((ROOT/'models/generic-v1/build_receipt.json').exists(),'Run tools/build_model.py for model integration tests')
class GenericModelIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine=ModelEngine(ROOT)
        cls.engine.ensure_built()

    def test_template_is_empty_and_every_register_is_free(self):
        c=self.engine.context(self.engine.template_path)
        self.assertEqual(c['status'],'EMPTY')
        self.assertFalse(c['financial_results_available'])
        for r in c['registers'].values():self.assertEqual(r['occupied_rows'],[])
        self.assertEqual(c['registers']['DATA Contrats']['free_count'],400)
        self.assertEqual(c['registers']['Effectifs']['free_count'],100)
        self.assertIn('input_signature',c)
        self.assertEqual(c['formula_errors']['count'],0)

    def test_package_has_no_financial_caches_or_previous_market_default(self):
        with zipfile.ZipFile(self.engine.template_path) as z:
            self.assertNotIn(b'absPath',z.read('xl/workbook.xml'))
            self.assertFalse(any(n.startswith('xl/media/') for n in z.namelist()))
            self.assertFalse(any('comments' in n.lower() for n in z.namelist()))
            for n in z.namelist():
                if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'):
                    root=ET.fromstring(z.read(n))
                    for c in root.iter('{'+core.NS+'}c'):
                        if c.find('m:f',core.N) is not None:self.assertIsNone(c.find('m:v',core.N))
                if n.startswith('xl/charts/') and n.endswith('.xml'):
                    self.assertNotIn(b'numCache',z.read(n));self.assertNotIn(b'strCache',z.read(n))
        with_schema=self.engine.schema
        self.assertNotIn('default_formula',with_schema['cells']['Valorisation']['D112'])
        self.assertFalse(with_schema['cells']['Control']['C59']['allow_blank'])

    def test_catalog_distinguishes_id_label_and_missing_business_values(self):
        wb=core.Workbook(self.engine.template_path)
        try:
            for r in range(15,28):
                self.assertEqual(wb.value('Assumptions','A'+str(r)),f'OFFRE_{r-14:02d}')
                self.assertEqual(wb.value('Assumptions','B'+str(r)),f'Offre {r-14:02d}')
                self.assertEqual(wb.value('Assumptions','C'+str(r)),0)
                self.assertIsNone(wb.value('Assumptions','F'+str(r)))
            for c in ['D68','D79','D83','D93','D126']:
                self.assertIsNone(wb.value('Assumptions',c))
        finally:wb.close()
        self.assertTrue(all(isinstance(f['cells'],list) for f in self.engine.catalog()))

    def test_excel_manual_cost_checks_distinguish_zero_from_missing(self):
        wb=core.Workbook(self.engine.template_path)
        try:
            self.assertIn('NOT(ISNUMBER($L15))',wb.formula('DATA COGS','V15'))
            self.assertIn('NOT(ISNUMBER($L27))',wb.formula('DATA COGS','V27'))
            self.assertIn('ISNUMBER',wb.formula('Contrôles','C76'))
            self.assertNotIn('$L$15:$L$27=0',wb.formula('Contrôles','C76'))
        finally:wb.close()

    def test_changed_cell_protection_is_rejected_even_when_formulas_unchanged(self):
        wb=core.Workbook(self.engine.template_path)
        try:
            idx=int(wb.sheet('Control')[1]['C59'].get('s','0'))
        finally:wb.close()
        with tempfile.TemporaryDirectory(prefix='tca-lock-test-') as folder:
            target=Path(folder)/'tampered.xlsm'
            with zipfile.ZipFile(self.engine.template_path) as source,zipfile.ZipFile(target,'w') as output:
                for info in source.infolist():
                    raw=source.read(info.filename)
                    if info.filename=='xl/styles.xml':
                        styles=ET.fromstring(raw);xf=styles.find('m:cellXfs',core.N)[idx]
                        p=xf.find('m:protection',core.N)
                        if p is None:p=ET.SubElement(xf,'{'+core.NS+'}protection')
                        p.set('locked','1');xf.set('applyProtection','1')
                        raw=ET.tostring(styles,encoding='utf-8',xml_declaration=True)
                    output.writestr(copy.copy(info),raw)
            with self.assertRaisesRegex(ValueError,'Protections de cellules modifiées'):
                self.engine.context(target)

    def test_transaction_zero_and_prospective_calendar_with_replay_refused(self):
        e=self.engine;source=e.template_path;before=core.sha(source.read_bytes())
        updates=[{'sheet':'Control','cell':'C10','value':'2028-01-01','reason':'Date confirmée du dossier fictif','evidence':'TEST_CALENDAR','replace_existing':True},
                 {'sheet':'Control','cell':'C59','value':3,'reason':'Horizon confirmé du dossier fictif','evidence':'TEST_CALENDAR','replace_existing':True},
                 {'sheet':'Assumptions','cell':'D126','value':0,'reason':'Création sans solde historique confirmée','evidence':'TEST_OPENING'}]
        with tempfile.TemporaryDirectory(prefix='tca-model-test-') as folder:
            out=Path(folder)/'case.xlsm';plan=e.prepare(source,updates);receipt=e.apply(source,plan,out)
            self.assertTrue(receipt['source_unchanged']);self.assertFalse(receipt['financial_results_available'])
            self.assertEqual(core.sha(source.read_bytes()),before)
            wb=core.Workbook(out)
            try:
                self.assertEqual(wb.value('Control','C10'),core.excel_serial('2028-01-01'))
                self.assertEqual(wb.value('Control','C59'),3)
                self.assertEqual(wb.value('Assumptions','D126'),0)
            finally:wb.close()
            with self.assertRaisesRegex(ValueError,'périmé'):
                e.apply(out,plan,Path(folder)/'replay.xlsm')
            self.assertFalse((Path(folder)/'replay.xlsm').exists())

    def test_null_horizon_and_free_formula_and_wrong_model_refused(self):
        e=self.engine
        with self.assertRaises(ValueError):
            e.prepare(e.template_path,[{'sheet':'Control','cell':'C59','value':None,'reason':'Suppression non valide du paramètre','evidence':'TEST','replace_existing':True}])
        with self.assertRaises(ValueError):
            e.prepare(e.template_path,[{'sheet':'Assumptions','cell':'B15','value':'=1+1','reason':'Formule libre non autorisée en saisie','evidence':'TEST','replace_existing':True}])
        with self.assertRaises(ValueError):
            e.prepare(e.template_path,[{'sheet':'Bilan','cell':'D24','value':100,'reason':'Une sortie doit rester un calcul','evidence':'TEST'}])

    def test_original_reference_preserved(self):
        files=list((ROOT/'exemple'/'01_Previsionnels').glob('*Pilotage_protege.xlsm'))
        if files:self.assertEqual(core.sha(files[0].read_bytes()),SOURCE_SHA)


if __name__=='__main__':unittest.main()
