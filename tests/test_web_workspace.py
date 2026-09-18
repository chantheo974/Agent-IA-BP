"""HTTP-independent end-to-end transactions on deliberately small OOXML."""
from pathlib import Path
import tempfile
import unittest
from contextlib import nullcontext
from unittest.mock import patch
from tests.test_model_versions import fixture
from tests.test_web_structure import move_fixture
from tca_bp.service import Application
from tca_bp.storage import digest
from tca_bp.web_workspace import WebWorkspace


class WorkspaceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.excel_mutex = patch('tca_bp.web_workspace.excel_lock', nullcontext)
        self.excel_mutex.start()
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.engine=fixture(self.root/'model')
        self.app=Application(self.root,self.root/'data',engine=self.engine)
        self.app.create_case('Client fictif','Variante',case_id='fixture_case')
        self.work=WebWorkspace(self.app,variant_runner=move_fixture)

    def tearDown(self):
        self.work.close()
        self.temp.cleanup()
        self.excel_mutex.stop()

    def test_preview_adopt_migrate_read_download_restore_and_replay(self):
        initial=self.app._row('fixture_case')
        source=self.app._workbook(initial)
        old_hash=digest(source)
        draft=self.work.add_operations('fixture_case',[
            {'type':'insert_rows','sheet':'Inputs','index':1,'count':1},
            {'type':'rename_sheet','sheet':'Inputs','name':'Renamed'}],{'sheet':'Inputs','allow_structure':True})
        preview=self.work.preview('fixture_case',draft['id'])
        self.assertEqual(preview['status'],'READY')
        self.assertEqual(self.app._row('fixture_case')['revision'],0)
        applied=self.work.apply('fixture_case',draft['id'],preview['approval_token'])
        self.assertEqual(applied['revision'],1)
        current=self.app.get_case('fixture_case')
        self.assertEqual(current['model_status'],'VERSION_EXACTE_DISPONIBLE')
        engine=self.app.engine_for_case('fixture_case')
        self.assertEqual(engine.catalog()[0]['sheet'],'Renamed')
        self.assertEqual(engine.catalog()[0]['cells'],['A2'])
        cells=self.work.cells('fixture_case','Renamed',row=2,rows=1,columns=2)
        self.assertEqual(cells['cells'][1]['formula'],'=A2*2')
        self.assertTrue(self.work.apply('fixture_case',draft['id'],preview['approval_token'])['replayed'])
        self.assertEqual(self.app._row('fixture_case')['revision'],1)
        original=next(x for x in self.work.versions('fixture_case')['versions'] if x['revision']==0)
        self.work.restore('fixture_case',original['id'])
        self.assertEqual(self.app._row('fixture_case')['revision'],2)
        self.assertEqual(self.app.engine_for_case('fixture_case').catalog()[0]['sheet'],'Inputs')
        self.assertEqual(digest(source),old_hash)

    def _previews(self):
        folder=self.app.store.case_dir('fixture_case')/'transactions'
        return sorted(path.name for path in folder.glob('web_preview_*') if path.is_dir())

    def _structural_draft(self):
        return self.work.add_operations('fixture_case',[
            {'type':'insert_rows','sheet':'Inputs','index':1,'count':1},
            {'type':'rename_sheet','sheet':'Inputs','name':'Renamed'}],{'sheet':'Inputs','allow_structure':True})

    def test_applied_preview_copy_is_removed_and_published_version_kept(self):
        draft=self._structural_draft()
        preview=self.work.preview('fixture_case',draft['id'])
        self.assertEqual(len(self._previews()),1)
        receipt=self.work.apply('fixture_case',draft['id'],preview['approval_token'])
        self.assertEqual(self._previews(),[])
        published=self.app.store.case_dir('fixture_case')/receipt['workbook']
        self.assertTrue(published.is_file())
        self.assertEqual(digest(published),receipt['output_sha256'])
        self.assertTrue(self.work.apply('fixture_case',draft['id'],preview['approval_token'])['replayed'])

    def test_cleanup_summarizes_raw_request_but_preserves_reviewed_manifest_and_receipt(self):
        import json
        case=self.app.store.case_dir('fixture_case')
        preview=case/'transactions'/'web_preview_redaction';native=preview/'.web-structure-fixture'
        native.mkdir(parents=True)
        source_sha='a'*64
        request=native/'request.json'
        request.write_text(json.dumps({'operations':[{'value':'private financial answer'}],
            'source_sha256':source_sha,'output':str(preview/'apercu.xlsm')}),encoding='utf-8')
        request_sha=digest(request)
        (native/'receipt.json').write_text('{"before": 1, "after": 2}',encoding='utf-8')
        (preview/'apercu.variant.json').write_text('{"all_changes": [1,2,3]}',encoding='utf-8')
        (preview/'apercu.xlsm').write_bytes(b'temporary only')
        self.work._drop_preview('fixture_case',{'preview_path':str((preview/'apercu.xlsm').relative_to(case))})
        saved=case/'transactions'/'preview_diagnostics'/preview.name
        summary=json.loads((saved/native.name/'request.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['sha256'],request_sha)
        self.assertEqual(summary['operation_count'],1)
        self.assertEqual(summary['source_sha256'],source_sha)
        self.assertEqual(summary['outputbasename'],'apercu.xlsm')
        self.assertNotIn('private financial answer',json.dumps(summary))
        self.assertEqual((saved/'apercu.variant.json').read_text(encoding='utf-8'),'{"all_changes": [1,2,3]}')
        self.assertTrue((saved/native.name/'receipt.json').is_file())
        self.assertFalse(preview.exists())

    def test_new_preview_replaces_the_previous_copy_and_discard_removes_it(self):
        draft=self._structural_draft()
        self.work.preview('fixture_case',draft['id'])
        first=self._previews()
        self.assertEqual(len(first),1)
        self.work.preview('fixture_case',draft['id'])
        second=self._previews()
        self.assertEqual(len(second),1)
        self.assertNotEqual(first,second)
        self.work.discard('fixture_case')
        self.assertEqual(self._previews(),[])
        self.assertEqual(self.app._row('fixture_case')['revision'],0)

    def test_editing_the_draft_removes_the_preview_it_invalidates(self):
        draft=self._structural_draft()
        self.work.preview('fixture_case',draft['id'])
        self.assertEqual(len(self._previews()),1)
        updated=self.work.add_operations('fixture_case',[{'type':'set_value','sheet':'Inputs','cell':'A1','value':7}],
                                         {'sheet':'Inputs','allow_structure':True})
        self.assertEqual(updated['status'],'DRAFT')
        self.assertEqual(self._previews(),[])

    def test_preview_file_tampering_prevents_apply(self):
        draft=self.work.add_operations('fixture_case',[
            {'type':'insert_rows','sheet':'Inputs','index':1,'count':1},
            {'type':'rename_sheet','sheet':'Inputs','name':'Renamed'}],{'sheet':'Inputs','allow_structure':True})
        preview=self.work.preview('fixture_case',draft['id'])
        import json
        payload=json.loads(self.work._draft_row('fixture_case')['payload'])
        path=self.app.store.case_dir('fixture_case')/payload['preview_path']
        with path.open('ab') as handle:
            handle.write(b'tamper')
        with self.assertRaisesRegex(ValueError,'changé'):
            self.work.apply('fixture_case',draft['id'],preview['approval_token'])
        self.assertEqual(self.app._row('fixture_case')['revision'],0)

    def test_recognized_input_revision_keeps_exact_model_and_requires_recalculation(self):
        import zipfile
        from tca_bp.model_registry import model_pin
        initial=self.app._row('fixture_case')
        def input_only(source,output,operations,**kwargs):
            with zipfile.ZipFile(source) as src,zipfile.ZipFile(output,'w') as dst:
                for info in src.infolist():
                    raw=src.read(info.filename)
                    if info.filename=='xl/worksheets/sheet1.xml':raw=raw.replace(b'<c r="A1"/>',b'<c r="A1"><v>5</v></c>')
                    dst.writestr(info,raw)
            return {'status':'SIMULATED_ONLY','macros_enabled':False}
        self.work.variant_runner=input_only
        draft=self.work.add_operations('fixture_case',[{'type':'set_value','sheet':'Inputs','cell':'A1','value':5}],{'sheet':'Inputs'})
        preview=self.work.preview('fixture_case',draft['id'])
        self.assertEqual(preview['status'],'READY')
        with patch('tca_bp.web_model.seal_profile_model',side_effect=AssertionError('No new template for a recognized input')):
            receipt=self.work.apply('fixture_case',draft['id'],preview['approval_token'])
        current=self.app._row('fixture_case')
        self.assertTrue(receipt['model_unchanged'])
        self.assertEqual(model_pin(current),model_pin(initial))
        self.assertEqual(current['revision'],1)
        self.assertEqual(current['calculation_status'],'A_RECALCULER')
        self.assertNotEqual(current['sha256'],initial['sha256'])


if __name__=='__main__':
    unittest.main()
