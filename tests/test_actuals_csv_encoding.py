"""Explicit CSV encoding through the real import route; no Excel job is run."""
import json
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient
from tca_bp.decision_actuals import read_import
from tca_bp.service import Application
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace
from tests.test_service import FakeEngine


class ActualsEncodingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.app=Application(self.root,self.root/'data',engine=FakeEngine(self.root))
        self.app.create_case('Entreprise fictive','Encodage CSV',case_id='encoding_case')
        self.work=WebWorkspace(self.app)
        self.api=create_app(self.app,workspace=self.work,start_jobs=False)
        self.client=TestClient(self.api,base_url='http://127.0.0.1:8765')

    def tearDown(self):
        self.client.close();self.work.close();self.tmp.cleanup()

    def test_utf8_with_and_without_bom_and_explicit_windows_encoding(self):
        text='période;poste;valeur\n2026-01;cash;10,50\n'
        path=self.root/'actuals.csv'
        mapping={'period':'période','metric':'poste','value':'valeur'}
        for encoding in ('utf-8','utf-8-sig'):
            with self.subTest(encoding=encoding):
                path.write_bytes(text.encode(encoding))
                columns,rows=read_import(path,mapping,'fr')
                self.assertEqual(columns,['période','poste','valeur'])
                self.assertEqual(rows[0]['value'],'10,50')
        path.write_bytes(text.encode('cp1252'))
        with self.assertRaisesRegex(ValueError,'Choisir son encodage'):
            read_import(path,mapping,'fr')
        self.assertEqual(read_import(path,mapping,'fr','cp1252')[1][0]['period'],'2026-01')
        with self.assertRaisesRegex(ValueError,'UTF-8 ou Windows-1252'):
            read_import(path,mapping,'fr','auto')

    def post(self,raw,encoding='utf-8',request_id='encoding_request',mapping=None):
        return self.client.post('/api/cases/encoding_case/actuals/import',
            files={'file':('realise.csv',raw,'text/csv')},
            data={'encoding':encoding,'numeric_locale':'fr','cutoff':'2026-01-31',
                  'expected_revision':'0','request_id':request_id,
                  'mapping':json.dumps(mapping or {'period':'période','metric':'poste','value':'valeur'})})

    def test_http_windows_preview_keeps_encoding_trace_and_retry_is_idempotent(self):
        raw='période;poste;valeur\n2026-01;cash;10,50\n'.encode('cp1252')
        failure=self.post(raw)
        self.assertEqual(failure.status_code,409,failure.text)
        self.assertIn('Choisir son encodage',failure.text)
        response=self.post(raw,'cp1252')
        self.assertEqual(response.status_code,200,response.text)
        result=response.json();self.assertEqual(result['encoding'],'cp1252')
        self.assertEqual(result['preview']['changes'][0]['new'],'10.50')
        self.assertEqual(self.post(raw,'cp1252').json(),result)
        with self.app.store.connection() as db:
            traces=db.execute("SELECT details FROM history WHERE case_id='encoding_case' AND kind='LECTURE_IMPORT_REALISE'").fetchall()
            self.assertEqual(len(traces),1)
            trace=json.loads(traces[0]['details'])
            self.assertEqual(trace['encoding'],'cp1252')
            self.assertEqual(trace['mapping']['period'],'période')
            self.assertTrue(trace['source_sha256'])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sources WHERE case_id='encoding_case'").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM web_jobs WHERE case_id='encoding_case'").fetchone()[0],0)
        self.assertEqual(self.app._row('encoding_case')['revision'],0)
        self.assertEqual(self.api.state.decision.objects('encoding_case','actuals'),[])

    def test_encoding_is_part_of_the_request_identity_even_when_ascii_bytes_match(self):
        raw=b'period;metric;value\n2026-01;cash;100\n'
        mapping={'period':'period','metric':'metric','value':'value'}
        response=self.post(raw,mapping=mapping)
        self.assertEqual(response.status_code,200,response.text)
        changed=self.post(raw,'cp1252',mapping=mapping)
        self.assertEqual(changed.status_code,409,changed.text)
        self.assertIn('contenu différent',changed.text)


if __name__=='__main__':unittest.main()
