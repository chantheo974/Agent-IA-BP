"""Finalize a tiny 33-sheet synthetic build after closing its source ZIP."""
from pathlib import Path
import json,tempfile,unittest,zipfile
from unittest.mock import patch
from tca_bp.model_build import build_model
from tca_bp.vendor import input_engine as core


class BuildFinalizationTests(unittest.TestCase):
    def test_graph_and_receipt_are_written_after_source_archive_is_closed(self):
        with tempfile.TemporaryDirectory(prefix='tca-synthetic-builder-') as temporary:
            root=Path(temporary);source=root/'source.xlsm';out=root/'result'
            names=['Fictive'+str(i) for i in range(1,34)]
            binary=b'NON_EXECUTABLE_SYNTHETIC_VBA'
            with zipfile.ZipFile(source,'w') as archive:
                sheets=''.join(f'<sheet name="{s}" sheetId="{i}" r:id="rId{i}"/>' for i,s in enumerate(names,1))
                archive.writestr('xl/workbook.xml',f'<workbook xmlns="{core.NS}" xmlns:r="{core.REL}"><sheets>{sheets}</sheets><calcPr/></workbook>')
                rels=''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="worksheet"/>' for i in range(1,34))
                archive.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+rels+'</Relationships>')
                archive.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
                for i in range(1,34):
                    body='<c r="A1"><f t="shared" si="0" ref="A1:B1">A2*2</f></c><c r="B1"><f t="shared" si="0"/></c>' if i==1 else '<c r="A1"><is><t>Fictitious</t></is></c>'
                    archive.writestr(f'xl/worksheets/sheet{i}.xml',f'<worksheet xmlns="{core.NS}"><sheetData><row r="1">{body}</row></sheetData></worksheet>')
                archive.writestr('xl/styles.xml',f'<styleSheet xmlns="{core.NS}"><fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0"/></cellXfs></styleSheet>')
                archive.writestr('xl/vbaProject.bin',binary)
            original=source.read_bytes()
            schema={'model_id':'fixture/build','cells':{s:{} for s in names},'fields':[],'native_outputs':{},'native_table_outputs':{}}
            with patch('tca_bp.model_build._source_assets',return_value=(source,schema)), \
                 patch('tca_bp.model_build._schema',return_value=schema), \
                 patch('tca_bp.model_build._migrations',return_value=({},[])), \
                 patch('tca_bp.model_build._audit_vba',return_value={'scope':'nonexecutable synthetic fixture'}), \
                 patch('tca_bp.model_build._clean_formula',side_effect=lambda text,mapping:'A2*3' if text=='A2*2' else text), \
                 patch('tca_bp.model_build.native_execution_metadata',return_value={}):
                result=build_model(root,out)
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(result['counts']['sheets'],33)
            graph=json.loads((out/'graphe_dependances.json').read_text(encoding='utf8'))
            self.assertEqual(graph['macro']['sha256'],core.sha(binary))
            self.assertFalse(graph['macro']['executed'])
            self.assertTrue((out/'build_receipt.json').is_file())
            wb=core.Workbook(out/'TCA_BP_Trame_generique.xlsm')
            try:
                self.assertEqual(wb.formula('Fictive1','A1'),'A2*3')
                self.assertEqual(wb.formula('Fictive1','B1'),'B2*2')
                self.assertEqual(wb.z.read('xl/vbaProject.bin'),binary)
            finally:wb.close()


if __name__=='__main__':unittest.main()
