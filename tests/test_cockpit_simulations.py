"""Persistent simulation protocol, not financial or native Excel qualification.

Small OOXML and an explicitly fake recalculation receipt exercise commit/retry
boundaries. Financial metrics below are transport fixtures only.
"""
from contextlib import nullcontext
import json
import shutil
import unittest
from unittest.mock import patch
import zipfile

from tca_bp.cockpit_simulations import CockpitSimulations, KIND
from tca_bp.decision_model import scenario_list
from tca_bp.model_registry import model_pin
from tca_bp.storage import canonical, digest, now
from tests import test_cockpit_api as api_fixture


def input_fixture(source, output, operations, **kwargs):
    value = next(op['value'] for op in operations if op['cell'] == 'A1')
    with zipfile.ZipFile(source) as before, zipfile.ZipFile(output, 'w') as after:
        for info in before.infolist():
            raw = before.read(info.filename)
            if info.filename == 'xl/worksheets/sheet1.xml':
                raw = raw.replace(b'<c r="A1"/>', ('<c r="A1"><v>' + str(value) + '</v></c>').encode())
            after.writestr(info, raw)
    return {'status': 'SIMULATED_ONLY', 'macros_enabled': False}


class CockpitSimulationTests(unittest.TestCase):
    get = api_fixture.CockpitApiTests.get
    entries = api_fixture.CockpitApiTests.entries
    body = api_fixture.CockpitApiTests.body
    post = api_fixture.CockpitApiTests.post

    def setUp(self):
        api_fixture.CockpitApiTests.setUp(self)
        self.work.variant_runner = input_fixture
        self.simulations = self.api.state.cockpit_simulations
        self.calculations = []
        self.patches = [patch('tca_bp.web_workspace.excel_lock', nullcontext),
                        patch.object(self.app, 'recalculate', side_effect=self.recalculate),
                        patch.object(CockpitSimulations, '_observations', self.observations)]
        for item in self.patches:
            item.start()
        response = self.post(self.body())
        self.assertEqual(response.status_code, 200, response.text)

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        api_fixture.CockpitApiTests.tearDown(self)

    def recalculate(self, child_id):
        self.calculations.append(child_id)
        row = self.app._row(child_id)
        relative = 'versions/fake_recalculation_' + str(row['revision'] + 1) + '.xlsm'
        output = self.store_path(child_id) / relative
        shutil.copyfile(self.app._workbook(row), output)
        receipt = {'case_id': child_id, 'client_id': row['client_id'], 'revision': row['revision'] + 1,
                   'source_sha256': row['sha256'], 'output_sha256': digest(output),
                   'adopted': True, **model_pin(row), 'test_only': True}
        with self.store.connection() as db:
            db.execute("UPDATE cases SET revision=?,workbook=?,sha256=?,calculation_status='RECALCULE' WHERE id=?",
                       (receipt['revision'], relative, receipt['output_sha256'], child_id))
            self.store.history(db, child_id, 'RECALCUL_EXCEL', receipt)
        return receipt

    @property
    def store(self):
        return self.app.store

    def store_path(self, case_id):
        return self.store.case_dir(case_id)

    @staticmethod
    def observations(simulations, child_id):
        row = simulations.app._row(child_id)
        return {'revision': row['revision'], 'sha256': row['sha256'], 'calculation_status': row['calculation_status'],
                'metrics': [{'id': 'protocol_only', 'value': 25, 'unit': 'TEST'}], 'annual_metrics': [], 'series': []}

    def submit(self):
        impacts = self.get('/draft/impacts')
        self.assertTrue(impacts['can_simulate'], impacts)
        body = {'expected_revision': 0, 'request_id': 'simulation_request', 'draft_id': impacts['draft_id'],
                'draft_fingerprint': impacts['draft_fingerprint'], 'name': 'Simulation fictive'}
        response = self.post(body, '/simulations')
        self.assertEqual(response.status_code, 200, response.text)
        self.submit_body = body
        return response.json()['job']

    def execute(self, public_job):
        with self.store.connection() as db:
            db.execute("UPDATE web_jobs SET status='RUNNING' WHERE id=?", (public_job['id'],))
            job = dict(db.execute('SELECT * FROM web_jobs WHERE id=?', (public_job['id'],)).fetchone())
        try:
            result = self.d.run_job(job, json.loads(job['payload']), lambda message: None)
        except Exception as error:
            with self.store.connection() as db:
                db.execute("UPDATE web_jobs SET status='FAILED',error=? WHERE id=?", (str(error), job['id']))
            raise
        with self.store.connection() as db:
            db.execute("UPDATE web_jobs SET status='SUCCEEDED',result=? WHERE id=?", (canonical(result), job['id']))
        return result

    def retry(self, public_job):
        with self.store.connection() as db:
            job = db.execute('SELECT * FROM web_jobs WHERE id=?', (public_job['id'],)).fetchone()
        # Same payload as the historical explicit /jobs/{id}/retry endpoint.
        return self.work.jobs.submit('case_a', job['kind'], json.loads(job['payload']), 'retry_' + job['id'])['job']

    def only_simulation(self):
        items = self.get('/simulations')['simulations']
        self.assertEqual(len(items), 1)
        return items[0]

    def test_isolated_simulation_maps_sources_and_preserves_reference(self):
        before = self.work.draft('case_a')
        job = self.submit()
        self.assertEqual(self.post(self.submit_body, '/simulations').json()['job']['id'], job['id'])
        result = self.execute(job)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['metrics'][0]['unit'], 'TEST')
        child_id = result['scenario_case_id']
        self.assertNotEqual(child_id, 'case_a')
        self.assertEqual(self.calculations, [child_id])
        self.assertEqual(self.app._row('case_a')['revision'], 0)
        self.assertEqual(self.app._row('case_a')['sha256'], self.initial['sha256'])
        self.assertEqual(self.work.draft('case_a'), before)
        self.assertEqual(self.app._row(child_id)['revision'], 2)
        proof = self.d.objects('case_a', 'scenario')[0]['origin']['sources']
        self.assertNotEqual(proof[self.source['id']], self.source['id'])
        child = self.app._row(child_id)
        self.assertEqual(json.loads(child['field_states'])['Inputs!A1']['evidence'], proof[self.source['id']])
        self.assertEqual(self.only_simulation()['status'], 'READY')

    def test_changed_fingerprint_before_submission_is_not_simulated(self):
        old = self.get('/draft/impacts')
        self.post(self.body(value=30, request_id='modified'))
        body = {'expected_revision': 0, 'request_id': 'stale_sim', 'draft_id': old['draft_id'],
                'draft_fingerprint': old['draft_fingerprint'], 'name': 'Périmé'}
        self.assertEqual(self.post(body, '/simulations').status_code, 409)
        self.assertEqual(self.d.objects('case_a', KIND), [])
        self.assertEqual(self.d.objects('case_a', 'scenario'), [])

    def test_keep_and_propose_adoption_reuse_copy_and_require_parent_approval(self):
        result = self.execute(self.submit())
        ident = result['id']
        keep = {'request_id': 'keep_once', 'expected_revision': 0, 'name': 'Scénario conservé'}
        first = self.post(keep, '/simulations/' + ident + '/keep')
        self.assertEqual(first.status_code, 200, first.text)
        self.assertTrue(first.json()['saved'])
        kept = scenario_list(self.d, 'case_a')
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]['case_id'], result['scenario_case_id'])
        self.assertEqual(kept[0]['name'], 'Scénario conservé')
        self.assertEqual(self.post(keep, '/simulations/' + ident + '/keep').json(), first.json())
        self.work.discard('case_a')
        propose = {'request_id': 'adopt_once', 'expected_revision': 0}
        response = self.post(propose, '/simulations/' + ident + '/propose-adoption')
        self.assertEqual(response.status_code, 200, response.text)
        draft = response.json()
        self.assertEqual(draft['operations'][0]['value'], 25)
        self.assertEqual(draft['operations'][0]['evidence_id'], self.source['id'])
        self.assertEqual(draft['status'], 'DRAFT')
        self.assertIsNone(draft['approval_token'])
        self.assertEqual(self.post(propose, '/simulations/' + ident + '/propose-adoption').json(), draft)
        self.assertEqual(len(self.d.objects('case_a', 'scenario')), 1)
        self.assertEqual(self.app._row('case_a')['revision'], 0)
        preview = self.work.preview('case_a', draft['id'])
        self.work.apply('case_a', draft['id'], preview['approval_token'])
        self.assertEqual(self.app._row('case_a')['revision'], 1)
        self.assertEqual(self.calculations, [result['scenario_case_id']])

    def test_different_parent_draft_and_changed_reference_cannot_be_overwritten(self):
        result = self.execute(self.submit())
        self.post(self.body(value=40, request_id='other_hypothesis'))
        before = self.work.draft('case_a')
        route = '/simulations/' + result['id'] + '/propose-adoption'
        self.assertEqual(self.post({'expected_revision': 0, 'request_id': 'adoption_conflict'}, route).status_code, 409)
        self.assertEqual(self.work.draft('case_a'), before)
        with self.store.connection() as db:
            db.execute('UPDATE cases SET revision=1 WHERE id=?', ('case_a',))
        self.assertTrue(self.only_simulation()['stale'])
        self.assertEqual(self.post({'expected_revision': 1, 'request_id': 'adoption_stale'}, route).status_code, 409)

    def test_resume_after_copy_commit_discovers_same_child(self):
        from tca_bp.cockpit_simulations import create_scenario as original
        def interrupted(*args, **kwargs):
            original(*args, **kwargs)
            raise RuntimeError('test interrupted after copy commit')
        job = self.submit()
        with patch('tca_bp.cockpit_simulations.create_scenario', side_effect=interrupted):
            with self.assertRaises(RuntimeError):
                self.execute(job)
        copies = self.d.objects('case_a', 'scenario')
        self.assertEqual(len(copies), 1)
        self.assertNotIn('metrics', self.only_simulation())
        result = self.execute(self.retry(job))
        self.assertEqual(result['scenario_case_id'], copies[0]['scenario_case_id'])
        self.assertEqual(len(self.d.objects('case_a', 'scenario')), 1)
        self.assertEqual(len(self.calculations), 1)

    def test_resume_after_apply_commit_reuses_token_and_adoption_receipt(self):
        original = self.work.apply
        def interrupted(*args, **kwargs):
            original(*args, **kwargs)
            raise RuntimeError('test interrupted after apply commit')
        job = self.submit()
        with patch.object(self.work, 'apply', side_effect=interrupted):
            with self.assertRaises(RuntimeError):
                self.execute(job)
        child = self.only_simulation()['scenario_case_id']
        self.assertEqual(self.app._row(child)['revision'], 1)
        result = self.execute(self.retry(job))
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(self.app._row(child)['revision'], 2)
        self.assertEqual(self.calculations, [child])

    def test_resume_after_recalculation_commit_never_runs_second_calculation(self):
        def interrupted(child):
            self.recalculate(child)
            raise RuntimeError('test interrupted after recalc commit')
        job = self.submit()
        with patch.object(self.app, 'recalculate', side_effect=interrupted):
            with self.assertRaises(RuntimeError):
                self.execute(job)
        self.assertNotIn('metrics', self.only_simulation())
        result = self.execute(self.retry(job))
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(self.calculations, [result['scenario_case_id']])
        self.assertEqual(self.app._row(result['scenario_case_id'])['revision'], 2)

    def test_modified_child_hides_results_and_refuses_adoption(self):
        result = self.execute(self.submit())
        path = self.app._workbook(self.app._row(result['scenario_case_id']))
        with path.open('ab') as stream:
            stream.write(b'changed-after-proof')
        visible = self.only_simulation()
        self.assertEqual(visible['status'], 'NEEDS_REVIEW')
        self.assertNotIn('metrics', visible)
        response = self.post({'expected_revision': 0, 'request_id': 'tampered_adoption'},
                             '/simulations/' + result['id'] + '/propose-adoption')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.app._row('case_a')['revision'], 0)

    def test_native_revision_change_during_snapshot_cannot_queue_mixed_operations(self):
        before = self.get('/draft/impacts')
        original = self.work._read
        def changed_after_read(*args, **kwargs):
            result = original(*args, **kwargs)
            with self.store.connection() as db:
                db.execute('UPDATE cases SET revision=1 WHERE id=?', ('case_a',))
            return result
        with patch.object(self.work, '_read', side_effect=changed_after_read):
            with self.assertRaisesRegex(ValueError, 'changé'):
                self.simulations.submit('case_a', {'request_id': 'native_change', 'expected_revision': 0,
                    'draft_id': before['draft_id'], 'draft_fingerprint': before['draft_fingerprint'], 'name': 'Snapshot refusé'})
        self.assertEqual(self.d.objects('case_a', KIND), [])
        self.assertEqual(self.d.objects('case_a', 'scenario'), [])
        self.assertEqual(self.work.jobs.list('case_a'), [])


if __name__ == '__main__':
    unittest.main()

