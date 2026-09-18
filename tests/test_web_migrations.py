from pathlib import Path
import json
import tempfile
import unittest

from tca_bp.service import Application
from tca_bp.storage import canonical,digest
from tca_bp.web_workspace import WebWorkspace
from tests.test_service import FakeEngine


class WebMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.engine=FakeEngine(self.root)
        self.app=Application(self.root,self.root/'data',engine=self.engine)
        self.case=self.app.create_case('Témoin','Migration',case_id='case_migration')
        self.work=WebWorkspace(self.app)
        self.source=self.app.add_source('case_migration',text='Valeur prouvée : 12.')

    def tearDown(self):
        self.work.close()
        self.temp.cleanup()

    def test_migration_explicit_then_restore_creates_revision_and_keeps_sources(self):
        before=self.app._row('case_migration')
        old_file=self.app._workbook(before)
        old_hash=digest(old_file)
        candidate_root=self.root/'candidate'
        candidate_root.mkdir()
        candidate=FakeEngine(candidate_root)
        candidate.model_id='fixture/2'
        pin=self.app.registry.register(candidate)
        with self.app.store.case_lock(before['id']),self.app.store.connection() as db:
            receipt=self.work._adopt(before,candidate.template_path,pin,{'Entrées!A1':{'evidence':self.source['id']}},'TEST_MIGRATION',{},db)
        self.assertEqual(receipt['revision'],1)
        self.assertEqual(self.app.get_case(before['id'])['model_status'],'VERSION_EXACTE_DISPONIBLE')
        self.assertEqual(digest(old_file),old_hash)
        with self.app.store.connection() as db:
            origin=json.loads(db.execute("SELECT details FROM history WHERE kind='CREATION'").fetchone()[0])
        self.assertEqual(origin['model_id'],'fixture/1')
        versions=self.work.versions(before['id'])['versions']
        original=next(x for x in versions if x['revision']==0)
        restored=self.work.restore(before['id'],original['id'])
        self.assertEqual(restored['revision'],2)
        self.assertEqual(self.app.get_case(before['id'])['model_id'],'fixture/1')
        self.assertEqual(self.app.get_case(before['id'])['sources'][0]['id'],self.source['id'])
        self.assertEqual(len(self.work.versions(before['id'])['versions']),3)

    def test_migration_receipt_tampering_is_detected(self):
        before=self.app._row('case_migration')
        candidate_root=self.root/'candidate'
        candidate_root.mkdir()
        candidate=FakeEngine(candidate_root)
        candidate.model_id='fixture/2'
        pin=self.app.registry.register(candidate)
        with self.app.store.connection() as db:
            self.work._adopt(before,candidate.template_path,pin,{},'TEST_MIGRATION',{},db)
        with self.app.store.connection() as db:
            migration=json.loads(db.execute("SELECT details FROM history WHERE kind='MIGRATION_MODELE'").fetchone()[0])
        receipt=self.app.store.case_dir(before['id'])/migration['receipt_path']
        receipt.write_text('{}')
        with self.assertRaisesRegex(ValueError,'migration'):
            self.app.engine_for_case(before['id'])

    def test_old_service_revisions_are_indexed_without_modifying_them(self):
        update={'sheet':'Entrées','cell':'A1','value':12,'reason':'Source du porteur','evidence':self.source['id'],'status':'CONFIRME'}
        plan=self.app.prepare_changes('case_migration',[update],'req_old')
        self.app.apply_plan('case_migration',plan['id'])
        versions=self.work.versions('case_migration')['versions']
        self.assertEqual([x['revision'] for x in versions],[1,0])
        self.assertEqual(versions[-1]['sha256'],self.case['sha256'])


if __name__=='__main__':
    unittest.main()
