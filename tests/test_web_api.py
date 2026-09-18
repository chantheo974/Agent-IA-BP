from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tca_bp.service import Application
from tca_bp.storage import canonical
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace
from tests.test_service import FakeEngine


class WebApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.service=Application(self.root,self.root/'data',engine=FakeEngine(self.root))
        self.service.create_case('Client A','Dossier A',case_id='case_a')
        self.service.create_case('Client B','Dossier B',case_id='case_b')
        self.work=WebWorkspace(self.service)
        self.client=TestClient(create_app(self.service,workspace=self.work,start_jobs=False),base_url='http://127.0.0.1:8765')

    def tearDown(self):
        self.client.close()
        self.work.close()
        self.temp.cleanup()

    def op(self,value=7):
        return {'type':'set_value','sheet':'Entrées','cell':'A1','value':value}

    def add(self,op=None):
        return self.client.post('/api/cases/case_a/draft/operations',json={'operations':[op or self.op()],'scope':{'sheet':'Entrées','range':'A1:A2'}})

    def test_cases_sources_versions_and_download_existing(self):
        self.assertEqual(len(self.client.get('/api/cases').json()['cases']),2)
        source=self.client.post('/api/cases/case_a/sources',json={'title':'Commande','text':'Contrat confirmé.'}).json()
        self.assertIn(source['id'],str(self.client.get('/api/cases/case_a/sources').json()))
        self.assertEqual(self.client.get('/api/cases/case_b/sources/'+source['id']).status_code,409)
        versions=self.client.get('/api/cases/case_a/versions').json()['versions']
        self.assertTrue(versions[0]['current'])
        response=self.client.get('/api/cases/case_a/download')
        self.assertEqual(response.status_code,200)
        self.assertIn('.xlsm',response.headers['content-disposition'])

    def test_manual_and_chat_share_draft_conflict_needs_resolution(self):
        first=self.add().json()
        source=self.service.add_source('case_a',text='Proposition 8')
        second=self.work.add_operations('case_a',[{**self.op(8),'evidence_id':source['id']}],{'sheet':'Entrées','range':'A1:A2'},origin='chat')
        self.assertEqual(first['id'],second['id'])
        self.assertEqual(len(second['conflicts']),1)
        response=self.client.post('/api/cases/case_a/draft/resolve',json={'index':0,'choice':'incoming'})
        self.assertEqual(response.json()['operations'][0]['value'],8)
        self.assertEqual(response.json()['conflicts'],[])
        self.assertEqual(self.service._row('case_a')['revision'],0)

    def test_cross_source_scope_and_arbitrary_code_refused(self):
        source=self.service.add_source('case_b',text='Montant 9')
        self.assertEqual(self.add({**self.op(),'evidence_id':source['id']}).status_code,409)
        self.assertEqual(self.add({**self.op(),'cell':'B5'}).status_code,409)
        self.assertEqual(self.add({'type':'run_python','code':'print(1)'}).status_code,409)
        self.assertEqual(self.work.draft('case_a')['status'],'EMPTY')

    def test_stale_draft_refused(self):
        self.add()
        with self.service.store.connection() as db:
            db.execute('UPDATE cases SET revision=1 WHERE id=?',('case_a',))
        response=self.add(self.op(8))
        self.assertEqual(response.status_code,409)
        self.assertIn('périmé',response.json()['detail'])

    def test_request_replay_and_changed_payload(self):
        payload={'message':'Bonjour','selection':{'sheet':'Entrées'},'request_id':'request_one'}
        a=self.client.post('/api/cases/case_a/chat',json=payload).json()
        b=self.client.post('/api/cases/case_a/chat',json=payload).json()
        self.assertEqual(a['job']['id'],b['job']['id'])
        self.assertTrue(b['replayed'])
        self.assertEqual(self.client.post('/api/cases/case_a/chat',json={**payload,'message':'Autre'}).status_code,409)

    def test_external_origin_host_and_source_file_path_refused(self):
        for headers in ({'origin':'https://evil.test'},{'host':'evil.test'},{'sec-fetch-site':'cross-site'}):
            self.assertEqual(self.client.get('/api/cases',headers=headers).status_code,403)
        self.assertEqual(self.client.post('/api/cases/case_a/sources',json={'path':'C:/secret.txt'}).status_code,409)

    def test_upload_and_http_limits_headers_and_dev_origin(self):
        for value,status in ((str(53*1024*1024),413),('invalid',400),('-1',400)):
            self.assertEqual(self.client.post('/api/cases/case_a/sources',content=b'',headers={'content-length':value}).status_code,status)
        response=self.client.get('/api/cases')
        self.assertEqual(response.headers['x-content-type-options'],'nosniff')
        self.assertEqual(response.headers['cache-control'],'no-store')
        self.assertIn("frame-ancestors 'none'",response.headers['content-security-policy'])
        origin={'origin':'http://127.0.0.1:5173'}
        self.assertEqual(self.client.get('/api/cases',headers=origin).status_code,403)
        with TestClient(create_app(self.service,workspace=self.work,start_jobs=False,dev=True),base_url='http://127.0.0.1:8765') as dev:
            self.assertEqual(dev.get('/api/cases',headers=origin).status_code,200)
        upload=self.client.post('/api/cases/case_a/sources/upload',files={'file':('hypothese.txt','Document fictif à vérifier.'.encode('utf8'),'text/plain')})
        self.assertEqual(upload.status_code,200,upload.text)
        self.assertEqual(upload.json()['title'],'hypothese.txt')
        named=self.client.post('/api/cases/case_a/sources/upload',data={'title':'  Contrat confirmé  '},files={'file':('scan.txt',b'Piece avec titre choisi','text/plain')})
        self.assertEqual(named.status_code,200,named.text)
        self.assertEqual(named.json()['title'],'Contrat confirmé')
        self.assertEqual(self.client.get('/api/cases/case_b/sources/'+upload.json()['id']).status_code,409)

    def test_api_key_not_in_public_or_validation_responses(self):
        secret='test-key-web-secret'
        response=self.client.put('/api/settings',json={'api_key':secret})
        self.assertEqual(response.status_code,200)
        self.assertNotIn(secret,response.text)
        self.assertNotIn(secret,self.client.get('/api/settings').text)
        self.assertNotIn(secret,(self.root/'data'/'web_settings.json').read_text())
        response=self.client.put('/api/settings',json=[secret])
        self.assertNotIn(secret,response.text)

    def test_private_reasoning_never_exposed_by_messages(self):
        with self.service.store.connection() as db:
            db.execute('INSERT INTO web_messages VALUES(?,?,?,?,?,?,?,?,?)',('msg_a','case_a',None,'assistant','Réponse','[]',canonical([{'reasoning_content':'private_reasoning'}]),'COMPLETE','2026-09-12'))
        response=self.client.get('/api/cases/case_a/chat')
        self.assertIn('Réponse',response.text)
        self.assertNotIn('private_reasoning',response.text)

    def test_event_replay_survives_new_workspace(self):
        event_id=self.work.jobs.emit('case_a','chat',{'message':'prêt'})
        restarted=WebWorkspace(self.service)
        self.assertEqual(restarted.jobs.events('case_a',event_id-1)[0]['id'],event_id)
        restarted.close()

    def test_incomplete_jobs_not_automatically_applied_after_restart(self):
        job=self.work.jobs.submit('case_a','apply',{'draft_id':'draft_x'})['job']
        with self.service.store.connection() as db:
            db.execute("UPDATE web_jobs SET status='RUNNING' WHERE id=?",(job['id'],))
        self.work.jobs.start()
        self.work.jobs.close()
        self.assertEqual(self.work.jobs.list('case_a')[0]['status'],'INTERRUPTED')

    def test_http_retry_is_case_scoped_and_idempotent(self):
        original=self.work.jobs.submit('case_a','chat',{'message':'Demande fictive','selection':{'sheet':'Entrées'}})['job']
        with self.service.store.connection() as db:
            db.execute("UPDATE web_jobs SET status='INTERRUPTED' WHERE id=?",(original['id'],))
        route='/api/cases/case_a/jobs/'+original['id']+'/retry'
        first=self.client.post(route,json={'request_id':'retry_one'})
        self.assertEqual(first.status_code,200,first.text)
        again=self.client.post(route,json={'request_id':'retry_one'})
        self.assertEqual(first.json()['job']['id'],again.json()['job']['id'])
        self.assertTrue(again.json()['replayed'])
        self.assertEqual(self.client.post(route.replace('case_a','case_b'),json={'request_id':'retry_one'}).status_code,409)
        self.assertEqual(self.service._row('case_a')['revision'],0)

    def test_event_stream_is_capped_without_losing_the_recent_catch_up(self):
        queue=self.work.jobs
        for index in range(queue.RETAINED_EVENTS+600):
            queue.emit('case_a','refresh',{'index':index})
        queue.emit('case_b','refresh',{})
        with self.service.store.connection() as db:
            kept=[dict(row) for row in db.execute('SELECT id,data FROM web_events WHERE case_id=? ORDER BY id',('case_a',))]
            other=db.execute('SELECT COUNT(*) n FROM web_events WHERE case_id=?',('case_b',)).fetchone()['n']
        self.assertLessEqual(len(kept),queue.RETAINED_EVENTS+256)
        self.assertGreaterEqual(len(kept),queue.RETAINED_EVENTS)
        self.assertEqual(other,1)
        # Le dernier événement reste lisible et les identifiants restent croissants.
        self.assertEqual(json.loads(kept[-1]['data'])['index'],queue.RETAINED_EVENTS+599)
        self.assertEqual([row['id'] for row in kept],sorted(row['id'] for row in kept))
        catch_up=queue.events('case_a',kept[-4]['id'])
        self.assertEqual([item['data']['index'] for item in catch_up],
                         [json.loads(row['data'])['index'] for row in kept[-3:]])


if __name__=='__main__':
    unittest.main()
