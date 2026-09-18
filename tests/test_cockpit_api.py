"""Cockpit contracts on tiny fictitious OOXML; no Excel or provider calls."""
from __future__ import annotations

from contextlib import nullcontext
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import datetime as dt
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from tca_bp.cockpit_api import install_routes
from tca_bp.cockpit_workspace import SHEET_VIEWS
from tca_bp.decision_workspace import DecisionWorkspace, IntentReviewRequired
from tca_bp.service import Application
from tca_bp.model_engine import ModelEngine
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core
from tca_bp.web_model_profile import seal_profile
from tca_bp.web_structure import plan_operations
from tca_bp.web_workspace import WebWorkspace
from tests.test_model_versions import fixture
from tests.test_web_structure import move_fixture


class CockpitApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='cockpit-api-')
        self.root = Path(self.tmp.name)
        self.engine = fixture(self.root / 'model')
        # Include a known calculated default to prove the business route refuses
        # it although the historical maintenance atelier supports formula edits.
        schema_path = self.root / 'model' / 'modele.json'
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
        schema['cells']['Inputs']['B1'] = {'kind': 'number', 'default_formula': 'A1*2'}
        schema['fields'].append({'id': 'calculated_default', 'sheet': 'Inputs', 'label': 'Défaut calculé', 'kind': 'number', 'cells': ['B1']})
        wb = core.Workbook(self.engine.template_path)
        try:
            schema['cells']['Inputs']['B1']['fill'] = wb.fill('Inputs', 'B1')
            schema['signature'] = wb.semantic_signature(schema)
        finally:
            wb.close()
        schema_path.write_text(canonical(schema), encoding='utf-8')
        receipt_path = self.root / 'model' / 'build_receipt.json'
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        receipt['schema_sha256'] = digest(schema_path)
        receipt_path.write_text(canonical(receipt), encoding='utf-8')
        self.app = Application(self.root, self.root / 'data', engine=self.engine)
        self.app.create_case('Entreprise fictive A', 'Cas A', case_id='case_a')
        self.app.create_case('Entreprise fictive B', 'Cas B', case_id='case_b')
        self.work = WebWorkspace(self.app, variant_runner=move_fixture)
        self.d = DecisionWorkspace(self.app, self.work)
        self.api = FastAPI()

        @self.api.exception_handler(ValueError)
        async def invalid(request: Request, exc: ValueError):
            return JSONResponse({'detail': str(exc), 'review_required': isinstance(exc, IntentReviewRequired)}, status_code=409)

        self.cockpit = install_routes(self.api, self.d)
        self.client = TestClient(self.api)
        self.source = self.app.add_source('case_a', text='Hypothèse fictive documentée : montant 25.')
        catalog = self.get('/catalog')
        self.sheet_id = next(s['id'] for s in catalog['sheets'] if s['name'] == 'Inputs')
        self.initial = self.app._row('case_a')

    def tearDown(self):
        self.client.close()
        self.work.close()
        self.tmp.cleanup()

    def get(self, path):
        response = self.client.get('/api/cases/case_a/cockpit' + path)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def entries(self):
        return self.get('/sheets/' + self.sheet_id)['entries']

    def body(self, *, value=25, binding=None, request_id='answer_one', source=None):
        entry = binding or self.entries()[0]
        return {'expected_revision': 0, 'request_id': request_id, 'answers': [
            {'sheet_id': self.sheet_id, 'binding_id': entry['binding_id'], 'value': value,
             'evidence_id': source or self.source['id'], 'status': 'CONFIRME'}]}

    def post(self, body, path='/answers'):
        return self.client.post('/api/cases/case_a/cockpit' + path, json=body)

    def test_catalogue_is_current_model_not_thirty_three_fabricated_sheets(self):
        catalog = self.get('/catalog')
        self.assertEqual(len(SHEET_VIEWS), 33)
        self.assertNotIn('Sensi Scénarios', SHEET_VIEWS)
        self.assertEqual([s['name'] for s in catalog['sheets']], ['Inputs', 'Control', 'Assumptions'])
        self.assertEqual(catalog['revision'], 0)
        self.assertEqual(catalog['model']['model_ref'], self.initial['model_ref'])
        self.assertEqual(catalog['sheets'][0]['group_id'], 'custom')
        self.assertEqual(catalog['sheets'][1]['view_kind'], 'settings')
        self.assertEqual(self.get('/catalog'), catalog)
        self.assertEqual(self.work.jobs.list('case_a'), [])

    def test_bounded_values_keep_null_formula_and_source_status_separate(self):
        detail = self.get('/sheets/' + self.sheet_id + '?offset=0&limit=1')
        self.assertEqual(detail['total'], 2)
        self.assertEqual(len(detail['entries']), 1)
        self.assertIsNone(detail['entries'][0]['value'])
        self.assertTrue(detail['entries'][0]['editable'])
        self.assertEqual(detail['entries'][0]['status'], 'NON_RENSEIGNE')
        formula = self.get('/sheets/' + self.sheet_id + '?offset=1&limit=1')['entries'][0]
        self.assertEqual(formula['formula'], '=A1*2')
        self.assertTrue(formula['calculated'])
        self.assertFalse(formula['editable'])
        for query in ('limit=501', 'offset=-1', 'limit=0'):
            self.assertEqual(self.client.get('/api/cases/case_a/cockpit/sheets/' + self.sheet_id + '?' + query).status_code, 409)
        self.assertEqual(self.client.get('/api/cases/case_a/cockpit/sheets/no_such_sheet').status_code, 409)

    def test_answer_uses_shared_draft_and_replays_without_touching_workbook(self):
        body = self.body()
        response = self.post(body)
        self.assertEqual(response.status_code, 200, response.text)
        draft = response.json()
        self.assertEqual(self.post(body).json(), draft)
        self.assertEqual(len(draft['operations']), 1)
        self.assertEqual(draft['operations'][0]['evidence_id'], self.source['id'])
        shown = self.entries()[0]
        self.assertEqual(shown['value'], 25)
        self.assertIsNone(shown['current_value'])
        self.assertTrue(shown['proposed'])
        self.assertEqual(shown['evidence_id'], self.source['id'])
        self.assertEqual(self.d.intent('case_a', body['request_id'])['result']['id'], draft['id'])
        self.assertEqual(self.app._row('case_a')['revision'], 0)
        self.assertEqual(digest(self.app._workbook(self.app._row('case_a'))), self.initial['sha256'])
        self.assertEqual(self.work.jobs.list('case_a'), [])
        self.assertEqual(self.post({**body, 'answers': [{**body['answers'][0], 'value': 26}]}).status_code, 409)

    def test_free_formula_and_calculated_default_cannot_enter_business_draft(self):
        formula_entry = next(e for e in self.entries() if e['calculated'])
        for index, body in enumerate((self.body(value='=1+1'), self.body(binding=formula_entry),
                                     {**self.body(), 'operations': [{'type': 'set_formula'}]})):
            body['request_id'] = 'formula_' + str(index)
            self.assertEqual(self.post(body).status_code, 409)
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')

    def test_revision_source_and_binding_ownership_are_required(self):
        other = self.app.add_source('case_b', text='Source étrangère au dossier.')
        cases = [self.body(source=other['id']), {**self.body(), 'expected_revision': 1},
                 {**self.body(), 'expected_revision': True}, {**self.body(), 'request_id': None}]
        mismatch = self.body()
        mismatch['answers'][0]['sheet_id'] = next(s['id'] for s in self.get('/catalog')['sheets'] if s['name'] == 'Control')
        cases.append(mismatch)
        for index, body in enumerate(cases):
            if body.get('request_id'):
                body['request_id'] = 'invalid_' + str(index)
            self.assertEqual(self.post(body).status_code, 409)
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')

    def test_corrupted_source_is_rejected_before_any_proposal(self):
        with self.app.store.connection() as db:
            db.execute('UPDATE sources SET text=? WHERE id=?', ('Texte altéré', self.source['id']))
        self.assertEqual(self.post(self.body()).status_code, 409)
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')

    def test_stable_sheet_and_binding_survive_structural_revision(self):
        before = self.entries()[0]['binding_id']
        with patch('tca_bp.web_workspace.excel_lock', nullcontext):
            draft = self.work.add_operations('case_a', [
                {'type': 'insert_rows', 'sheet': 'Inputs', 'index': 1, 'count': 1},
                {'type': 'rename_sheet', 'sheet': 'Inputs', 'name': 'Renamed'}],
                {'sheet': 'Inputs', 'allow_structure': True})
            preview = self.work.preview('case_a', draft['id'])
            self.work.apply('case_a', draft['id'], preview['approval_token'])
        detail = self.get('/sheets/' + self.sheet_id)
        self.assertEqual(detail['revision'], 1)
        self.assertEqual(detail['sheet']['name'], 'Renamed')
        self.assertEqual(detail['entries'][0]['binding_id'], before)
        self.assertEqual(detail['entries'][0]['cell'], 'A2')
        self.assertEqual(detail['entries'][0]['sheet'], 'Renamed')
        stale = self.body()
        self.assertEqual(self.post(stale).status_code, 409)
        current = self.body(request_id='after_rename')
        current['expected_revision'] = 1
        result = self.post(current)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['operations'][0]['cell'], 'A2')
        self.assertEqual(result.json()['operations'][0]['sheet'], 'Renamed')

    def test_added_and_deleted_sheets_follow_profile_without_invented_inputs(self):
        row, engine, profile, _, _ = self.cockpit._context('case_a')
        _, changed = plan_operations(profile, [{'type': 'add_sheet', 'name': 'Analyse', 'role': 'Analyse complémentaire fictive'}])
        added = changed['sheets'][-1]
        changed['sheets'][0]['deleted'] = True
        changed = seal_profile(changed)
        context = (row, engine, changed, [s for s in changed['sheets'] if not s.get('deleted')],
                   [f for f in changed['fields'] if f.get('sheet') != 'Inputs'])
        with patch.object(self.cockpit, '_context', return_value=context):
            catalog = self.get('/catalog')
            self.assertNotIn(self.sheet_id, [s['id'] for s in catalog['sheets']])
            custom = next(s for s in catalog['sheets'] if s['id'] == added['id'])
            self.assertEqual(custom['purpose'], 'Analyse complémentaire fictive')
            self.assertEqual(custom['fields'], [])
            self.assertIsNone(custom['register'])
            self.assertEqual(self.get('/sheets/' + added['id'])['entries'], [])

    def test_semantic_review_blocks_fields_and_duplicate_binding_is_atomic(self):
        context = list(self.cockpit._context('case_a'))
        context[4] = deepcopy(context[4])
        context[4][0]['semantics'] = {'status': 'REEXAMEN_REQUIS', 'can_propose': False}
        with patch.object(self.cockpit, '_context', return_value=tuple(context)):
            self.assertFalse(self.entries()[0]['editable'])
            self.assertEqual(self.post(self.body(request_id='review_blocked')).status_code, 409)
        body = self.body(request_id='duplicate')
        body['answers'].append({**body['answers'][0], 'value': 50})
        self.assertEqual(self.post(body).status_code, 409)
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')

    def test_register_routes_check_contract_then_delegate_existing_questions(self):
        context = list(self.cockpit._context('case_a'))
        schema = deepcopy(context[1].schema)
        schema['registers'] = {'Inputs': {'start_row': 1, 'end_row': 1}}
        context[1] = SimpleNamespace(schema=schema)
        result = {'status': 'NEEDS_INPUT', 'questions': [{'field_id': 'amount', 'question': 'Quelle valeur ?'}]}
        body = {'expected_revision': 0, 'request_id': 'record_one', 'evidence_id': self.source['id'], 'values': {'amount': 25}}
        with patch.object(self.cockpit, '_context', return_value=tuple(context)), \
                patch.object(self.d, 'prepare_record', return_value=result) as prepare:
            response = self.post(body, '/sheets/' + self.sheet_id + '/records')
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json(), result)
            self.assertEqual(self.post(body, '/sheets/' + self.sheet_id + '/records').json(), result)
            self.assertEqual(prepare.call_count, 1)
            self.assertEqual(prepare.call_args.args[1], 'Inputs')
            refused = {**body, 'request_id': 'record_unknown', 'values': {'free_formula': '=SUM(1,2)'}}
            self.assertEqual(self.post(refused, '/sheets/' + self.sheet_id + '/records').status_code, 409)
            self.assertEqual(prepare.call_count, 1)

    def test_maintenance_draft_does_not_masquerade_as_business_coordinates(self):
        self.work.add_operations('case_a', [
            {'type': 'insert_rows', 'sheet': 'Inputs', 'index': 1, 'count': 1},
            {'type': 'set_value', 'sheet': 'Inputs', 'cell': 'A2', 'value': 77}],
            {'sheet': 'Inputs', 'allow_structure': True})
        before = self.work.draft('case_a')
        detail = self.get('/sheets/' + self.sheet_id)
        self.assertTrue(detail['draft']['maintenance'])
        self.assertFalse(detail['entries'][0]['editable'])
        self.assertIsNone(detail['entries'][0]['value'])
        self.assertEqual(self.post(self.body()).status_code, 409)
        self.assertEqual(self.work.draft('case_a'), before)

    def grid_body(self, *, request_id='grid_one', cell='A1', value=25):
        return {'expected_revision': 0, 'request_id': request_id, 'scope': {'sheet': 'Inputs', 'range': 'A1:C2'},
                'operations': [{'type': 'set_value', 'sheet': 'Inputs', 'cell': cell,
                                'value': value, 'evidence_id': self.source['id']}]}

    def test_grid_cells_permissions_are_catalogue_based_and_bounded(self):
        result = self.get('/cells?sheet=Inputs&row=1&column=1&rows=1&columns=3')
        self.assertEqual(result['revision'], 0)
        self.assertEqual([cell['editable'] for cell in result['cells']], [True, False, False])
        self.assertEqual(result['cells'][0]['binding_id'], self.entries()[0]['binding_id'])
        self.assertIn('calculé', result['cells'][1]['read_only_reason'])
        self.assertIn('catalogue', result['cells'][2]['read_only_reason'])
        self.assertEqual(self.client.get('/api/cases/case_a/cockpit/cells?sheet=Inputs&rows=501').status_code, 409)
        self.work.add_operations('case_a', [{'type': 'insert_rows', 'sheet': 'Inputs', 'index': 1, 'count': 1}],
                                 {'sheet': 'Inputs', 'allow_structure': True})
        self.assertFalse(self.get('/cells?sheet=Inputs&rows=1&columns=1')['cells'][0]['editable'])

    def test_grid_operations_use_same_draft_and_durable_intent(self):
        body = self.grid_body(cell='$a$1')
        response = self.post(body, '/operations')
        self.assertEqual(response.status_code, 200, response.text)
        draft = response.json()
        self.assertEqual(draft['operations'][0]['cell'], 'A1')
        self.assertEqual(draft['operations'][0]['evidence_id'], self.source['id'])
        self.assertEqual(self.post(body, '/operations').json(), draft)
        self.assertEqual(self.entries()[0]['value'], 25)
        self.assertEqual(self.app._row('case_a')['sha256'], self.initial['sha256'])
        altered = deepcopy(body)
        altered['operations'][0]['value'] = 30
        self.assertEqual(self.post(altered, '/operations').status_code, 409)

    def test_grid_refuses_invalid_targets_sources_scope_and_mixed_batches_atomically(self):
        bodies = [self.grid_body(cell='B1'), self.grid_body(cell='C1'), self.grid_body(value='=2+2')]
        outside = self.grid_body()
        outside['scope']['range'] = 'A2'
        bodies.append(outside)
        source = self.grid_body()
        source['operations'][0].pop('evidence_id')
        bodies.append(source)
        foreign = self.grid_body()
        foreign['operations'][0]['evidence_id'] = self.app.add_source('case_b', text='Source étrangère')['id']
        bodies.append(foreign)
        structural = self.grid_body()
        structural['operations'] = [{'type': 'insert_rows', 'sheet': 'Inputs', 'index': 1, 'count': 1}]
        bodies.append(structural)
        mixed = self.grid_body()
        mixed['operations'].append({**mixed['operations'][0], 'cell': 'B1'})
        bodies.append(mixed)
        duplicate = self.grid_body()
        duplicate['operations'].append(deepcopy(duplicate['operations'][0]))
        bodies.append(duplicate)
        stale = self.grid_body()
        stale['expected_revision'] = 1
        bodies.append(stale)
        for index, body in enumerate(bodies):
            body['request_id'] = 'invalid_grid_' + str(index)
            with self.subTest(index=index):
                response = self.post(body, '/operations')
                self.assertEqual(response.status_code, 409, response.text)
                self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')
        self.assertEqual(self.app._row('case_a')['sha256'], self.initial['sha256'])

    def test_grid_ambiguous_bindings_are_readonly_and_cannot_be_submitted(self):
        context = list(self.cockpit._context('case_a'))
        context[4] = deepcopy(context[4])
        context[4].append({**context[4][0], 'id': 'second_meaning'})
        with patch.object(self.cockpit, '_context', return_value=tuple(context)):
            self.assertFalse(self.get('/cells?sheet=Inputs&rows=1&columns=1')['cells'][0]['editable'])
            self.assertEqual(self.post(self.grid_body(), '/operations').status_code, 409)
            self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')

    def run_chat_result(self, operations, identifier='chat_fixture'):
        context = {'case_id': 'case_a', 'revision': 0, 'source_sha256': self.initial['sha256'],
                   'sources': [{**self.source, 'case_id': 'case_a'}], 'user_source_id': self.source['id']}
        payload = {'message': 'Hypothèse fictive documentée', 'selection': {'sheet': 'Inputs', 'range': 'A1:C2'},
                   'expected_revision': 0, 'source_sha256': self.initial['sha256'], 'mode': 'cockpit'}
        result = {'message': 'Proposition à examiner', 'operations': operations, 'agents': [], 'questions': []}
        with patch.object(self.work, 'chat_context', return_value=context), patch.object(self.work.chat, 'run', return_value=result):
            returned = self.work.run_job({'id': identifier, 'case_id': 'case_a', 'kind': 'chat'}, payload, lambda value: None)
        self.assertEqual(context['editing_mode'], 'cockpit')
        return returned

    def test_cockpit_chat_preserves_manual_conflict_and_requires_adoption(self):
        self.post(self.body(value=10))
        self.run_chat_result([{'type': 'set_value', 'sheet': 'Inputs', 'cell': 'A1', 'value': 25}])
        draft = self.work.draft('case_a')
        self.assertEqual(draft['operations'][0]['value'], 10)
        self.assertEqual(len(draft['conflicts']), 1)
        self.assertEqual(draft['conflicts'][0]['incoming']['value'], 25)
        self.assertEqual(draft['conflicts'][0]['incoming']['evidence_id'], self.source['id'])
        self.assertEqual(self.app._row('case_a')['revision'], 0)
        self.assertEqual(self.app._row('case_a')['sha256'], self.initial['sha256'])

    def test_cockpit_chat_rejects_entire_ia_batch_outside_business_permissions(self):
        valid = self.grid_body()['operations'][0]
        foreign = self.app.add_source('case_b', text='Source étrangère')['id']
        invalid = [
            {'type': 'set_formula', 'sheet': 'Inputs', 'cell': 'A1', 'formula': '=2+2'},
            {'type': 'insert_rows', 'sheet': 'Inputs', 'index': 1, 'count': 1},
            {**valid, 'cell': 'B1'}, {**valid, 'cell': 'C1'}, {**valid, 'evidence_id': foreign}]
        for index, operation in enumerate(invalid):
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.run_chat_result([valid, operation], 'chat_invalid_' + str(index))
            self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')
        self.assertEqual(self.app._row('case_a')['sha256'], self.initial['sha256'])

    def test_cockpit_chat_http_binds_mode_revision_and_replay(self):
        from tca_bp.web_server import create_app
        client = TestClient(create_app(self.app, workspace=self.work, start_jobs=False), base_url='http://127.0.0.1:8765')
        try:
            body = {'message': 'Saisir une hypothèse', 'selection': {'sheet': 'Inputs'},
                    'mode': 'cockpit', 'request_id': 'chat_bound', 'expected_revision': 0}
            first = client.post('/api/cases/case_a/chat', json=body)
            self.assertEqual(first.status_code, 200, first.text)
            with self.store_connection() as db:
                stored = json.loads(db.execute('SELECT payload FROM web_jobs WHERE id=?', (first.json()['job']['id'],)).fetchone()[0])
                db.execute('UPDATE cases SET revision=1 WHERE id=?', ('case_a',))
            self.assertEqual(stored['mode'], 'cockpit')
            self.assertEqual(stored['expected_revision'], 0)
            replay = client.post('/api/cases/case_a/chat', json=body)
            self.assertEqual(replay.status_code, 200, replay.text)
            self.assertEqual(replay.json()['job']['id'], first.json()['job']['id'])
            for changed in ({'expected_revision': None}, {'expected_revision': 0, 'request_id': 'stale_chat'},
                            {'selection': {'sheet': 'Inputs', 'allow_structure': True}}, {'mode': 'unknown'}):
                response = client.post('/api/cases/case_a/chat', json={**body, **changed})
                self.assertEqual(response.status_code, 409, response.text)
        finally:
            client.close()

    def store_connection(self):
        return self.app.store.connection()

    def test_parallel_catalogue_read_does_not_turn_first_answer_into_uncertain_write(self):
        entered, release, writer_started = threading.Event(), threading.Event(), threading.Event()
        original = self.cockpit._sheets
        body = self.body(request_id='parallel_catalogue_answer')
        def paused_read(*args, **kwargs):
            entered.set()
            if not release.wait(5):
                raise RuntimeError('Test reader was not released')
            return original(*args, **kwargs)
        def answer():
            writer_started.set()
            return self.cockpit.answers('case_a', body)
        with ThreadPoolExecutor(max_workers=2) as pool, patch.object(self.cockpit, '_sheets', side_effect=paused_read):
            reader = pool.submit(self.cockpit.catalog, 'case_a')
            try:
                self.assertTrue(entered.wait(5))
                self.assertFalse((self.app.store.case_dir('case_a') / '.transaction.lock').exists())
                writer = pool.submit(answer)
                self.assertTrue(writer_started.wait(5))
            finally:
                release.set()
            self.assertEqual(reader.result(timeout=5)['revision'], 0)
            self.assertEqual(writer.result(timeout=5)['operations'][0]['value'], 25)
        self.assertEqual(self.d.intent('case_a', body['request_id'])['status'], 'COMPLETE')
        self.assertEqual(self.app._row('case_a')['revision'], 0)

    def test_native_revision_change_never_mixes_catalogue_with_another_window(self):
        original = self.cockpit._context
        def changed_during_context(case_id):
            context = original(case_id)
            with self.app.store.connection() as db:
                db.execute('UPDATE cases SET revision=revision+1 WHERE id=?', (case_id,))
            return context
        for operation in (lambda: self.cockpit.catalog('case_a'),
                          lambda: self.cockpit.sheet('case_a', self.sheet_id),
                          lambda: self.cockpit.cells('case_a', 'Inputs', rows=1, columns=2)):
            with self.subTest(operation=operation), patch.object(self.cockpit, '_context', side_effect=changed_during_context):
                with self.assertRaisesRegex(ValueError, 'changé|révision'):
                    operation()
            with self.app.store.connection() as db:
                db.execute('UPDATE cases SET revision=0 WHERE id=?', ('case_a',))
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')


def theme_fixture(root):
    """Independent tiny catalogue, not a replica or qualification of TCA finance.

    Real sheet names exercise routing and central business guards. Prefixed IDs
    deliberately do not impersonate the separately sealed TCA semantic contract.
    Numeric outputs are fixture observations; this helper never runs Excel.
    """
    root.mkdir()
    names = ['Control', 'Assumptions', 'Effectifs', 'DATA CAPEX', 'DATA Financement',
             'Financement Dette', 'DATA COGS', 'Revenue', 'Modèle financier',
             'Compte de Résultat', 'Valorisation', 'KPI Dashboard', 'Bilan']
    definitions = {
        'Control': [('start', 'C10', 'date'), ('years', 'C59', 'integer')],
        'Assumptions': [('delay', 'D6', 'number'), ('cash_opening', 'D126', 'number')],
        'Effectifs': [('position', 'B17', 'text'), ('recruit_start', 'F17', 'date'), ('salary', 'I17', 'number')],
        'DATA CAPEX': [('asset', 'B13', 'text'), ('asset_amount', 'D13', 'number'), ('asset_date', 'E13', 'date'),
                       ('asset_years', 'F13', 'number'), ('asset_rd', 'G13', 'text'), ('asset_rd_share', 'H13', 'number'),
                       ('asset_funding', 'I13', 'text'), ('asset_nature', 'M13', 'text')],
        'DATA Financement': [('funding', 'B14', 'text'), ('funding_category', 'C14', 'text'), ('funding_amount', 'D14', 'number'), ('funding_date', 'E14', 'date')],
        'Financement Dette': [('debt', 'B3', 'text'), ('debt_amount', 'C3', 'number'), ('debt_date', 'I3', 'date')],
        'DATA COGS': [('material', 'E15', 'number')],
        'Valorisation': [('growth', 'D8', 'number')],
    }
    schema = {'model_id': 'fixture/cockpit-themes', 'cells': {}, 'fields': [], 'registers': {}}
    for sheet, fields in definitions.items():
        schema['cells'][sheet] = {}
        for field, cell, kind in fields:
            schema['fields'].append({'id': 'fixture_' + field, 'sheet': sheet, 'label': field, 'kind': kind, 'cells': [cell]})
            schema['cells'][sheet][cell] = {'kind': kind, 'allow_blank': True}
    for sheet, row, columns in [('Effectifs', 17, ['B', 'F', 'I']), ('DATA CAPEX', 13, ['B', 'D', 'E']),
                                ('DATA Financement', 14, ['B', 'C', 'D', 'E']), ('Financement Dette', 3, ['B', 'C', 'I'])]:
        schema['registers'][sheet] = {'start_row': row, 'end_row': row, 'identity_columns': columns, 'required': columns}
    values = {name: {} for name in names}
    values['Control'] = {'C10': (dt.date(2030, 1, 1) - dt.date(1899, 12, 30)).days, 'C59': 1}
    values['Compte de Résultat'] = {'D7': 1200, 'D25': 600, 'D69': 400, 'D85': 200}
    values['Valorisation'] = {'D40': 1000000, 'D50': 800000}
    for i in range(12):
        for row, first, amount in ((282, 16, 100), (283, 16, 200), (284, 16, 300)):
            values['Revenue'][core.colname(first + i) + str(row)] = amount + i
        for row, amount in ((301, 700), (320, 500), (321, 1000)):
            values['Modèle financier'][core.colname(20 + i) + str(row)] = amount + i
    template = root / 'TCA_BP_Trame_generique.xlsm'
    with zipfile.ZipFile(template, 'w') as archive:
        sheets = ''.join(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>' for i, name in enumerate(names, 1))
        archive.writestr('xl/workbook.xml', f'<workbook xmlns="{core.NS}" xmlns:r="{core.REL}"><sheets>{sheets}</sheets><calcPr calcMode="autoNoTable"/></workbook>')
        relations = ''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="worksheet"/>' for i in range(1, len(names) + 1))
        archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + relations + '</Relationships>')
        for index, name in enumerate(names, 1):
            rows = {}
            for cell in set(values[name]) | set(schema['cells'].get(name, {})):
                payload = f'<v>{values[name][cell]}</v>' if cell in values[name] else ''
                rows.setdefault(core.coord(cell)[2], []).append(f'<c r="{cell}">{payload}</c>')
            body = ''.join(f'<row r="{row}">{"".join(cells)}</row>' for row, cells in sorted(rows.items()))
            archive.writestr(f'xl/worksheets/sheet{index}.xml', f'<worksheet xmlns="{core.NS}"><sheetData>{body}</sheetData></worksheet>')
        archive.writestr('xl/styles.xml', f'<styleSheet xmlns="{core.NS}"><fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0"/></cellXfs></styleSheet>')
        archive.writestr('xl/vbaProject.bin', b'NONEXECUTABLE_FIXTURE')
    schema['template_sha256'] = digest(template)
    workbook = core.Workbook(template)
    try:
        for sheet, cells in schema['cells'].items():
            for cell, spec in cells.items():
                spec['fill'] = workbook.fill(sheet, cell)
        schema['signature'] = workbook.semantic_signature(schema)
    finally:
        workbook.close()
    (root / 'modele.json').write_text(canonical(schema), encoding='utf-8')
    (root / 'build_receipt.json').write_text(canonical({'model_id': schema['model_id'], 'template_sha256': digest(template), 'schema_sha256': digest(root / 'modele.json')}), encoding='utf-8')
    return ModelEngine(root.parent, root)


class CockpitThemeTests(unittest.TestCase):
    """HTTP contract proofs on tiny models; never financial/native acceptance."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='cockpit-themes-')
        self.root = Path(self.tmp.name)
        self.engine = theme_fixture(self.root / 'model')
        self.app = Application(self.root, self.root / 'data', engine=self.engine)
        self.app.create_case('Fictif uniquement', 'Thèmes', case_id='case_a')
        self.work = WebWorkspace(self.app)
        self.d = DecisionWorkspace(self.app, self.work)
        self.api = FastAPI()
        @self.api.exception_handler(ValueError)
        async def invalid(request, exc):
            return JSONResponse({'detail': str(exc)}, status_code=409)
        self.cockpit = install_routes(self.api, self.d)
        self.client = TestClient(self.api)
        self.source = self.app.add_source('case_a', text='Cas fictifs de recrutement, actifs et financement ; aucun résultat financier certifié.')
        self.initial = self.app._row('case_a')
        self.sheets = {s['name']: s for s in self.get('/catalog')['sheets']}

    tearDown = CockpitApiTests.tearDown
    get = CockpitApiTests.get
    post = CockpitApiTests.post

    def outputs(self, name):
        return self.get('/sheets/' + self.sheets[name]['id'] + '/outputs')

    def qualified_fixture(self, *, current=True, ready=True):
        # This is only a unit-test availability witness. No native calculation
        # receipt is inserted or represented as evidence of financial accuracy.
        case = self.app.get_case('case_a')
        case.update(outputs_current=current, qualified_availability={scope: {'scenario_ready': ready, 'status': 'FIXTURE_QUALIFICATION'} for scope in ('CA', 'COGS', 'CASH', 'DCF')})
        return patch.object(self.app, 'get_case', return_value=case)

    def test_output_projection_distinguishes_three_revenue_flows_and_binds_snapshot(self):
        self.assertEqual(self.get('/sheets/' + self.sheets['Revenue']['id'])['total'], 0)
        with self.qualified_fixture():
            result = self.outputs('Revenue')
        self.assertEqual(result['revision'], 0)
        self.assertEqual(result['sha256'], self.initial['sha256'])
        self.assertEqual(result['metrics'], [])
        self.assertEqual(result['annual_metrics'], [])
        by_id = {s['id']: s for s in result['series']}
        self.assertEqual(set(by_id), {'revenue', 'billed_revenue', 'customer_receipts'})
        for key, value, cell in [('revenue', 100, 'P282'), ('billed_revenue', 200, 'P283'), ('customer_receipts', 300, 'P284')]:
            item = by_id[key]
            self.assertEqual(item['values'][0], value)
            self.assertEqual(item['categories'], [f'2030-{m:02d}' for m in range(1, 13)])
            self.assertEqual(item['sources'][0], {'sheet': 'Revenue', 'cell': cell})
            self.assertTrue(item['available'])
            self.assertEqual(item['provenance'], {'case_id': 'case_a', 'revision': 0, 'sha256': self.initial['sha256']})

    def test_unqualified_or_stale_outputs_never_expose_numeric_caches(self):
        # Real service has no recalculation proof, although fixture numeric
        # caches exist. Mock only the separate qualification branch next.
        variants = [nullcontext(), self.qualified_fixture(current=False), self.qualified_fixture(ready=False)]
        for variant in variants:
            with variant:
                for name in ('Revenue', 'Compte de Résultat', 'Valorisation', 'KPI Dashboard'):
                    with self.subTest(sheet=name):
                        result = self.outputs(name)
                        self.assertTrue(result['diagnostics'])
                        for category in ('series', 'metrics', 'annual_metrics'):
                            for item in result[category]:
                                self.assertNotIn('cached_value', item)
                                self.assertFalse(item['available'])
                                self.assertTrue(all(v is None for v in item['values']) if category == 'series' else item['value'] is None)

    def test_output_annual_periods_valuation_and_no_cash_break_are_distinct(self):
        with self.qualified_fixture():
            annual = self.outputs('Compte de Résultat')['annual_metrics']
            valuation = self.outputs('Valorisation')['metrics']
            dashboard = self.outputs('KPI Dashboard')['metrics']
        self.assertEqual([(m['metric'], m['value'], m['period']) for m in annual], [('revenue', 1200, '2030'), ('gross_margin', 600, '2030'), ('ebitda', 400, '2030'), ('net_income', 200, '2030')])
        self.assertEqual([m['value'] for m in valuation], [1000000, 800000])
        self.assertTrue(all(m['period'] == 'horizon' and m['available'] for m in valuation))
        cash_break = next(m for m in dashboard if m['id'] == 'cash_break_date')
        self.assertTrue(cash_break['available'])
        self.assertIsNone(cash_break['value'])
        self.assertEqual(len(cash_break['sources']), 12)

    def test_unmapped_sheet_is_not_reported_empty_and_unknown_id_is_refused(self):
        result = self.outputs('Bilan')
        self.assertEqual(result['series'], [])
        self.assertIn('grille', result['diagnostics'][0])
        self.assertEqual(self.client.get('/api/cases/case_a/cockpit/sheets/unknown/outputs').status_code, 409)
        self.assertEqual(self.work.jobs.list('case_a'), [])

    def test_outputs_reject_revision_change_during_real_reader(self):
        original = self.work._read
        def changed(case_id, action):
            result = original(case_id, action)
            with self.app.store.connection() as db:
                db.execute('UPDATE cases SET revision=revision+1 WHERE id=?', (case_id,))
            return result
        with self.qualified_fixture(), patch.object(self.work, '_read', side_effect=changed):
            response = self.client.get('/api/cases/case_a/cockpit/sheets/' + self.sheets['Revenue']['id'] + '/outputs')
        self.assertEqual(response.status_code, 409, response.text)
        self.assertNotIn('series', response.json())

    def test_outputs_recheck_full_workbook_integrity_after_read(self):
        original = self.work._read
        def changed(case_id, action):
            result = original(case_id, action)
            path = self.app._workbook(self.app._row(case_id))
            # An immutable version altered outside the service must not leak
            # already-parsed observations as current, even without a new head.
            with path.open('ab') as stream:
                stream.write(b'EXTERNAL_MODIFICATION')
            return result
        with self.qualified_fixture(), patch.object(self.work, '_read', side_effect=changed):
            response = self.client.get('/api/cases/case_a/cockpit/sheets/' + self.sheets['Revenue']['id'] + '/outputs')
        self.assertEqual(response.status_code, 409, response.text)
        self.assertNotIn('series', response.json())

    def test_output_identity_follows_renamed_sheet_and_shifted_rows(self):
        def move_revenue(source, output, operations, **kwargs):
            with zipfile.ZipFile(source) as before, zipfile.ZipFile(output, 'w') as after:
                for info in before.infolist():
                    raw = before.read(info.filename)
                    if info.filename == 'xl/workbook.xml':
                        raw = raw.replace(b'name="Revenue"', b'name="Revenue shifted"')
                    if info.filename == 'xl/worksheets/sheet8.xml':
                        node = ET.fromstring(raw)
                        for row in node.findall('.//{' + core.NS + '}row'):
                            row.set('r', str(int(row.get('r')) + 2))
                            for cell in row:
                                _, column, number = core.coord(cell.get('r'))
                                cell.set('r', core.colname(column) + str(number + 2))
                        raw = ET.tostring(node, encoding='utf-8')
                    after.writestr(info, raw)
            return {'status': 'SIMULATED_ONLY', 'macros_enabled': False}
        self.work.variant_runner = move_revenue
        with patch('tca_bp.web_workspace.excel_lock', nullcontext):
            draft = self.work.add_operations('case_a', [{'type': 'insert_rows', 'sheet': 'Revenue', 'index': 1, 'count': 2}, {'type': 'rename_sheet', 'sheet': 'Revenue', 'name': 'Revenue shifted'}], {'sheet': 'Revenue', 'allow_structure': True})
            preview = self.work.preview('case_a', draft['id'])
            self.work.apply('case_a', draft['id'], preview['approval_token'])
        with self.qualified_fixture():
            result = self.outputs('Revenue')
        self.assertEqual(result['sheet_id'], self.sheets['Revenue']['id'])
        self.assertEqual(result['sheet']['name'], 'Revenue shifted')
        self.assertEqual(result['revision'], 1)
        self.assertEqual(result['series'][0]['sources'][0], {'sheet': 'Revenue shifted', 'cell': 'P284'})
        self.assertEqual(result['series'][0]['values'][0], 100)

    def assert_untouched_reference(self):
        current = self.app._row('case_a')
        self.assertEqual((current['revision'], current['sha256']), (0, self.initial['sha256']))
        self.assertEqual(digest(self.app._workbook(current)), self.initial['sha256'])
        self.assertEqual(self.work.jobs.list('case_a'), [])

    def record(self, name, values, request_id):
        body = {'request_id': request_id, 'expected_revision': 0, 'evidence_id': self.source['id'], 'values': {'fixture_' + key: value for key, value in values.items()}}
        path = '/sheets/' + self.sheets[name]['id'] + '/records'
        response = self.post(body, path)
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertIn('operations', result, result)
        self.assertEqual(self.post(body, path).json(), result)
        self.assertEqual(len(result['operations']), len(values))
        self.assertTrue(all(op['sheet'] == name and op['evidence_id'] == self.source['id'] for op in result['operations']))
        self.assert_untouched_reference()
        return result

    def test_c3_recruitment_record_uses_real_coordinator_and_documented_start_date(self):
        draft = self.record('Effectifs', {'position': 'Recrutement fictif', 'recruit_start': '2030-07-01', 'salary': 48000}, 'recruitment')
        self.assertEqual(next(o['value'] for o in draft['operations'] if o['cell'] == 'F17'), '2030-07-01')

    def test_c3_asset_record_uses_real_coordinator_and_documented_acquisition(self):
        draft = self.record('DATA CAPEX', {'asset': 'Equipement fictif', 'asset_amount': 12000, 'asset_date': '2030-09-01',
            'asset_years': 5, 'asset_rd': 'Non', 'asset_rd_share': 0, 'asset_funding': 'Cash', 'asset_nature': 'Corporelle'}, 'asset')
        self.assertEqual(next(o['value'] for o in draft['operations'] if o['cell'] == 'D13'), 12000)

    def test_c3_asset_business_refusal_does_not_bypass_engine_or_create_draft(self):
        body = {'request_id': 'invalid_asset', 'expected_revision': 0, 'evidence_id': self.source['id'],
                'values': {'fixture_asset': 'Actif incomplet', 'fixture_asset_amount': 12000, 'fixture_asset_date': '2030-09-01'}}
        response = self.post(body, '/sheets/' + self.sheets['DATA CAPEX']['id'] + '/records')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['status'], 'REFUSED')
        self.assertTrue(any(q['status'] == 'ENGINE_VALIDATION' for q in response.json()['questions']))
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')
        self.assert_untouched_reference()

    def test_c3_funding_record_uses_real_coordinator_and_own_source(self):
        draft = self.record('DATA Financement', {'funding': 'Apport fictif', 'funding_category': 'FOUNDER', 'funding_amount': 50000, 'funding_date': '2030-06-01'}, 'funding')
        self.assertEqual(next(o['value'] for o in draft['operations'] if o['cell'] == 'D14'), 50000)

    def test_c3_debt_record_uses_real_coordinator(self):
        draft = self.record('Financement Dette', {'debt': 'Dette fictive', 'debt_amount': 20000, 'debt_date': '2030-06-01'}, 'debt')
        self.assertEqual(next(o['value'] for o in draft['operations'] if o['cell'] == 'C3'), 20000)

    def test_c3_missing_recruitment_date_persists_question_and_writes_no_draft(self):
        path = '/sheets/' + self.sheets['Effectifs']['id'] + '/records'
        body = {'request_id': 'incomplete_recruitment', 'expected_revision': 0, 'evidence_id': self.source['id'], 'values': {'fixture_position': 'Recrutement incomplet'}}
        response = self.post(body, path)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['status'], 'NEEDS_INPUT')
        self.assertIn('fixture_recruit_start', [q['field_id'] for q in response.json()['questions']])
        self.assertEqual(len(self.d.objects('case_a', 'record_questions')), 1)
        self.assertEqual(self.post(body, path).json(), response.json())
        self.assertEqual(len(self.d.objects('case_a', 'record_questions')), 1)
        self.assertEqual(self.work.draft('case_a')['status'], 'EMPTY')
        self.assert_untouched_reference()

    def test_c3_costs_cash_calendar_and_valuation_inputs_share_one_safe_draft(self):
        cases = [('DATA COGS', 'fixture_material', 275), ('Assumptions', 'fixture_delay', 45),
                 ('Control', 'fixture_start', '2031-01-01'), ('Assumptions', 'fixture_cash_opening', 15000),
                 ('Valorisation', 'fixture_growth', 0.02)]
        draft_id = None
        for index, (name, field, value) in enumerate(cases):
            detail = self.get('/sheets/' + self.sheets[name]['id'])
            entry = next(e for e in detail['entries'] if e['field_id'] == field)
            body = {'request_id': 'theme_' + str(index), 'expected_revision': 0, 'answers': [
                {'sheet_id': self.sheets[name]['id'], 'binding_id': entry['binding_id'], 'value': value, 'evidence_id': self.source['id'], 'status': 'CONFIRME'}]}
            response = self.post(body)
            self.assertEqual(response.status_code, 200, response.text)
            draft = response.json()
            if draft_id is not None:
                self.assertEqual(draft['id'], draft_id)
            draft_id = draft['id']
            self.assertEqual(len(draft['operations']), index + 1)
            self.assertEqual(self.post(body).json(), draft)
            self.assert_untouched_reference()


if __name__ == '__main__':
    unittest.main()
