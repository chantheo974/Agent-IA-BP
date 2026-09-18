"""Crash and stale-approval regressions on isolated fictitious OOXML, no COM."""
import json
import zipfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tca_bp.storage import canonical
from tca_bp.web_server import create_app
from tests import test_web_workspace as workspace_fixture


class WebIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = workspace_fixture.WorkspaceIntegrationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.app, self.work = self.fixture.app, self.fixture.work
        self.case_id = 'fixture_case'

    def op(self, value, cell='A1'):
        return {'type':'set_value','sheet':'Inputs','cell':cell,'value':value}

    def first_variant(self):
        draft = self.work.add_operations(self.case_id,[
            {'type':'insert_rows','sheet':'Inputs','index':1,'count':1},
            {'type':'rename_sheet','sheet':'Inputs','name':'Renamed'}],{'sheet':'Inputs','allow_structure':True})
        preview = self.work.preview(self.case_id,draft['id'])
        self.work.apply(self.case_id,draft['id'],preview['approval_token'])
        return next(item for item in self.work.versions(self.case_id)['versions'] if item['revision']==0)

    def test_conflict_ids_never_reused_after_resolution(self):
        self.work.add_operations(self.case_id,[self.op(1),self.op(2,'B1')],{'sheet':'Inputs'})
        source = self.app.add_source(self.case_id,text='Fictitious conflicting proposals.')
        def propose(value, cell='A1'):
            return self.work.add_operations(self.case_id,[{**self.op(value,cell),'evidence_id':source['id']}],{'sheet':'Inputs'},origin='chat')
        propose(7); propose(8,'B1')
        self.work.resolve(self.case_id,0,'existing')
        result = propose(9)
        self.assertEqual([item['index'] for item in result['conflicts']],[1,2])
        self.work.resolve(self.case_id,2,'incoming')
        result = self.work.draft(self.case_id)
        self.assertEqual(result['operations'][0]['value'],9)
        self.assertEqual(result['operations'][1]['value'],2)
        self.assertEqual([item['index'] for item in result['conflicts']],[1])

    def test_interrupted_preview_releases_draft_state_without_removing_lock_or_diagnostics(self):
        draft = self.work.add_operations(self.case_id,[self.op(7)],{'sheet':'Inputs'})
        job = self.work.jobs.submit(self.case_id,'preview',{'draft_id':draft['id']})['job']
        lock = self.app.store.case_dir(self.case_id)/'.transaction.lock'
        import os
        lock.write_text(canonical({'pid':os.getpid(),'started_at':'2026-09-12'}))
        self.addCleanup(lambda: lock.unlink(missing_ok=True))
        with self.app.store.connection() as db:
            payload=json.loads(self.work._draft_row(self.case_id,db)['payload'])
            payload['diagnostics']=[{'code':'EARLIER_CHECK','severity':'INFO'}]
            self.work._save_draft(db,draft['id'],payload,'PREPARING')
            db.execute("UPDATE web_jobs SET status='RUNNING' WHERE id=?",(job['id'],))
        self.work.jobs.start(); self.work.jobs.close()
        restored = self.work.draft(self.case_id)
        self.assertEqual(restored['status'],'DRAFT')
        self.assertEqual(restored['diagnostics'],payload['diagnostics'])
        self.assertEqual(restored['operations'],payload['operations'])
        self.assertIsNone(restored['approval_token'])
        self.assertEqual(self.work.jobs.list(self.case_id)[0]['status'],'INTERRUPTED')
        self.assertTrue(lock.exists())
        with self.assertRaisesRegex(ValueError,'transaction en cours'):
            self.work.discard(self.case_id)

    def test_restore_replay_survives_hard_stop_after_sql_commit(self):
        version = self.first_variant()
        job = self.work.jobs.submit(self.case_id,'restore',{'version_id':version['id']},'restore_once')['job']
        with self.app.store.connection() as db:
            payload=json.loads(db.execute('SELECT payload FROM web_jobs WHERE id=?',(job['id'],)).fetchone()[0])
        with patch.object(self.app,'_save_state',side_effect=SystemExit('simulated hard stop')):
            with self.assertRaises(SystemExit): self.work.run_job(job,payload,lambda _:None)
        self.assertEqual(self.app._row(self.case_id)['revision'],2)
        result = self.work.run_job({**job,'id':'retry_job'},payload,lambda _:None)
        self.assertTrue(result['replayed'])
        self.assertEqual(result['revision'],2)
        self.assertEqual(self.app._row(self.case_id)['revision'],2)
        self.assertEqual(len(self.work.versions(self.case_id)['versions']),3)
        with self.assertRaisesRegex(ValueError,'contenu différent'):
            self.work.restore(self.case_id,'changed_version',operation_id=payload['operation_id'],expected_revision=payload['expected_revision'],source_sha256=payload['source_sha256'])

    def test_failed_postcommit_mirror_does_not_report_failed_adoption(self):
        version = self.first_variant()
        with patch.object(self.app,'_save_state',side_effect=OSError('fixture mirror failure')):
            result=self.work.restore(self.case_id,version['id'],operation_id='restore_mirror',expected_revision=1,source_sha256=self.app._row(self.case_id)['sha256'])
        self.assertEqual(result['revision'],2)
        self.assertIn('state_mirror_warning',result)
        self.assertEqual(self.app._row(self.case_id)['revision'],2)

    def test_queued_restore_refuses_changed_case_before_first_adoption(self):
        version = self.first_variant()
        job = self.work.jobs.submit(self.case_id,'restore',{'version_id':version['id']})['job']
        with self.app.store.connection() as db:
            payload=json.loads(db.execute('SELECT payload FROM web_jobs WHERE id=?',(job['id'],)).fetchone()[0])
        self.work.restore(self.case_id,version['id'])
        with self.assertRaisesRegex(ValueError,'changé depuis'):
            self.work.run_job(job,payload,lambda _:None)
        self.assertEqual(self.app._row(self.case_id)['revision'],2)

    @staticmethod
    def scalar_runner(source, output, operations, **kwargs):
        value=next(op['value'] for op in operations if op['type']=='set_value')
        with zipfile.ZipFile(source) as before, zipfile.ZipFile(output,'w') as after:
            for info in before.infolist():
                data=before.read(info.filename)
                if info.filename=='xl/worksheets/sheet1.xml':
                    data=data.replace(b'<c r="A1"/>',f'<c r="A1" t="n"><v>{value}</v></c>'.encode())
                after.writestr(info,data)
        return {'status':'SIMULATED_ONLY'}

    def test_apply_bound_to_exact_reviewed_preview_and_api_replay(self):
        self.work.variant_runner=self.scalar_runner
        client=TestClient(create_app(self.app,workspace=self.work,start_jobs=False),base_url='http://127.0.0.1:8765')
        self.addCleanup(client.close)
        draft=self.work.add_operations(self.case_id,[self.op(7)],{'sheet':'Inputs','range':'A1'})
        first=self.work.preview(self.case_id,draft['id'])
        endpoint=f'/api/cases/{self.case_id}/draft/apply'
        self.assertEqual(client.post(endpoint,json={}).status_code,409)
        request={'draft_id':draft['id'],'approval_token':first['approval_token'],'request_id':'apply_first'}
        job=client.post(endpoint,json=request).json()['job']
        self.work.add_operations(self.case_id,[self.op(9)],{'sheet':'Inputs','range':'A1'})
        second=self.work.preview(self.case_id,draft['id'])
        self.assertNotEqual(first['approval_token'],second['approval_token'])
        self.assertEqual(client.post(endpoint,json={**request,'request_id':'stale_new_request'}).status_code,409)
        with self.app.store.connection() as db:
            payload=json.loads(db.execute('SELECT payload FROM web_jobs WHERE id=?',(job['id'],)).fetchone()[0])
        with self.assertRaisesRegex(ValueError,'aperçu approuvé'):
            self.work.run_job(job,payload,lambda _:None)
        self.assertEqual(self.app._row(self.case_id)['revision'],0)
        accepted={**request,'approval_token':second['approval_token'],'request_id':'apply_second'}
        job=client.post(endpoint,json=accepted).json()['job']
        result=self.work.run_job(job,{'draft_id':draft['id'],'approval_token':second['approval_token']},lambda _:None)
        with self.app.store.connection() as db:
            db.execute("UPDATE web_jobs SET status='SUCCEEDED',result=? WHERE id=?",(canonical(result),job['id']))
        self.assertEqual(self.work.cells(self.case_id,'Inputs',1,1,1,1)['cells'][0]['value'],9)
        replay=client.post(endpoint,json=accepted).json()
        self.assertTrue(replay['replayed']); self.assertEqual(replay['job']['id'],job['id'])
        self.assertEqual(client.post(endpoint,json={**accepted,'approval_token':first['approval_token']}).status_code,409)
        self.assertTrue(self.work.apply(self.case_id,draft['id'],second['approval_token'])['replayed'])
        self.assertEqual(self.app._row(self.case_id)['revision'],1)

    def test_source_changed_after_approval_refuses_adoption(self):
        self.work.variant_runner=self.scalar_runner
        draft=self.work.add_operations(self.case_id,[self.op(7)],{'sheet':'Inputs','range':'A1'})
        preview=self.work.preview(self.case_id,draft['id'])
        with self.app.store.connection() as db:
            db.execute('UPDATE sources SET text=? WHERE id=?',('changed fixture evidence',draft['operations'][0]['evidence_id']))
        with self.assertRaisesRegex(ValueError,'changé'):
            self.work.apply(self.case_id,draft['id'],preview['approval_token'])
        self.assertEqual(self.app._row(self.case_id)['revision'],0)

    def test_failed_serializer_leaves_no_workbook_and_preserves_diagnostic(self):
        def failed(source, output, operations, **kwargs):
            import shutil
            shutil.copyfile(source, output)
            output.with_suffix('.failure.json').write_text('{"reason":"fixture"}')
            raise ValueError('Simulated serialization failure')
        self.work.variant_runner=failed
        draft=self.work.add_operations(self.case_id,[self.op(7)],{'sheet':'Inputs'})
        with self.assertRaisesRegex(ValueError,'Simulated'):
            self.work.preview(self.case_id,draft['id'])
        transactions=self.app.store.case_dir(self.case_id)/'transactions'
        self.assertEqual(list(transactions.glob('web_preview_*/*.xlsm')),[])
        self.assertEqual(len(list((transactions/'preview_diagnostics').rglob('*.failure.json'))),1)
        self.assertEqual(self.work.draft(self.case_id)['status'],'DRAFT')
        self.work.discard(self.case_id)
        self.assertEqual(list(transactions.glob('web_preview_*')),[])

    def test_events_are_bounded_per_case_despite_interleaved_global_ids(self):
        self.app.create_case('Another fictitious client','Other',case_id='other_case')
        self.work.jobs.RETAINED_EVENTS=4
        first=self.work.jobs.emit(self.case_id)
        for _ in range(12):
            self.work.jobs.emit('other_case')
            self.work.jobs.emit(self.case_id)
        for case in (self.case_id,'other_case'):
            self.assertEqual(len(self.work.jobs.events(case)),4)
        status=self.work.jobs.replay_status(self.case_id,first)
        self.assertTrue(status['resync_required'])
        self.assertFalse(self.work.jobs.replay_status(self.case_id,status['latest_event_id'])['resync_required'])

    def test_request_lookup_is_strictly_isolated_by_case(self):
        self.app.create_case('Another fictitious client','Other',case_id='other_case')
        job=self.work.jobs.submit(self.case_id,'recalculate',{},'intent_once')['job']
        self.assertEqual(self.work.jobs.lookup(self.case_id,'intent_once')['id'],job['id'])
        self.assertIsNone(self.work.jobs.lookup('other_case','intent_once'))


if __name__=='__main__': unittest.main()
