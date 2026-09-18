"""Isolated HTTP/Excel acceptance run; the provider is explicitly simulated.

No client files or provider credentials are used. Run only on Windows/Excel.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from tca_bp.service import Application
from tca_bp.storage import atomic_json, digest
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace
from tca_bp.vendor.input_engine import Workbook


def main():
    folder = ROOT / 'runtime' / ('recette_web_api_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
    app = Application(ROOT, folder)
    checks = []
    receipt = {'status': 'EN_COURS', 'provider': 'SIMULE', 'excel': 'NATIF', 'checks': checks}

    def check(name, passed, actual=None, expected=None):
        checks.append({'name': name, 'passed': bool(passed), 'actual': actual, 'expected': expected})
        receipt['status'] = 'EN_COURS' if passed else 'ECHEC'
        atomic_json(folder / 'validation.json', receipt)
        if not passed:
            raise AssertionError(name + ': ' + repr(actual))

    class FictitiousChat:
        operations = []

        def run(self, message, selection, context, **kwargs):
            check('chat_lit_le_brouillon_manuel', len(context['draft']['operations']) == 2)
            check('chat_lit_le_registre_courant', bool(context['register']))
            return {'message': 'Recrutement fictif proposé pour examen.', 'questions': [],
                    'agents': ['agent_effectifs'], 'operations': self.operations, 'provider_messages': []}

    chat = FictitiousChat()
    work = WebWorkspace(app, chat=chat)
    with TestClient(create_app(app, workspace=work), base_url='http://127.0.0.1:8769') as client:
        def request(method, route, body=None):
            response = client.request(method, route, json=body)
            if response.status_code != 200:
                raise AssertionError(f'{method} {route}: {response.status_code}: {response.text[:2000]}')
            return response.json()

        case = request('POST', '/api/cases', {'client_name': 'RECETTE FICTIVE WEB', 'name': 'Recrutement et variante'})
        case_id = case['id']
        receipt['case_id'] = case_id
        prefix = '/api/cases/' + case_id
        original = app._workbook(app._row(case_id))
        original_sha = digest(original)
        source = request('POST', prefix + '/sources', {'title': 'Hypothèses fictives de recrutement',
            'text': 'RECETTE LOGICIELLE FICTIVE. Début 2026, horizon 3 ans. Un consultant Operations/G&A recruté au 1 avril 2026, salaire annuel 60000 euros, 1 ETP, charges 40 %, aucune R&D. Aucun client réel.'})
        plan = app.prepare_record(case_id, 'Effectifs', {
            'employee_position': 'Consultant fictif', 'employee_department': 'Operations',
            'employee_analytic': 'G&A', 'employee_rnd_share': 0, 'employee_start': '2026-04-01',
            'employee_fte': 1, 'employee_salary': 60000, 'employee_charges': 0.4,
            'employee_status': 'Recrute'}, source['id'], 'fixture_recruitment_contract')
        check('contrat_recrutement_valide', plan['status'] == 'PRET_A_APPLIQUER', plan['status'])
        chat.operations = [{'type': 'set_value', 'sheet': item['sheet'], 'cell': item['cell'],
                            'value': item['value'], 'evidence_id': source['id']} for item in plan['changes']]
        draft = request('POST', prefix + '/draft/operations', {'scope': {'sheet': 'Control'}, 'revision': 0,
            'operations': [{'type': 'set_value', 'sheet': 'Control', 'cell': 'C10', 'value': '2026-01-01'},
                           {'type': 'set_value', 'sheet': 'Control', 'cell': 'C59', 'value': 3}]})

        def job(route, body, timeout=900):
            queued = request('POST', prefix + route, body)
            job_id = queued['job']['id']
            started = time.monotonic()
            last = None
            while time.monotonic() - started < timeout:
                item = next(x for x in request('GET', prefix + '/jobs')['jobs'] if x['id'] == job_id)
                progress = str(item.get('progress'))
                if progress != last:
                    print(route + ': ' + progress[:200], flush=True)
                    last = progress
                if item['status'] == 'SUCCEEDED':
                    return item['result']
                if item['status'] in ('FAILED', 'INTERRUPTED'):
                    raise AssertionError(route + ': ' + str(item['error']))
                time.sleep(1)
            raise TimeoutError(route)

        job('/chat', {'message': 'Ajoute le recrutement documenté dans les sources.',
                     'selection': {'sheet': 'Effectifs'}, 'request_id': 'fixture_chat'})
        merged = request('GET', prefix + '/draft')
        check('brouillon_commun_chat_grille', merged['id'] == draft['id'] and len(merged['operations']) == 2 + len(chat.operations))
        request('POST', prefix + '/draft/operations', {'scope': {'sheet': 'Effectifs', 'allow_structure': True},
            'operations': [{'type': 'insert_rows', 'sheet': 'Effectifs', 'index': 1, 'count': 1},
                           {'type': 'rename_sheet', 'sheet': 'Effectifs', 'name': 'Equipe recette'},
                           {'type': 'add_sheet', 'name': 'Notes recette', 'role': 'Vérifier les hypothèses et calculs fictifs de recette.'}]})
        request('POST', prefix + '/draft/operations', {'scope': {'sheet': 'Notes recette'},
            'operations': [{'type': 'set_value', 'sheet': 'Notes recette', 'cell': 'A1', 'value': 12},
                           {'type': 'set_formula', 'sheet': 'Notes recette', 'cell': 'B1', 'formula': '=A1*2'}]})
        preview = job('/draft/preview', {'draft_id': draft['id'], 'request_id': 'fixture_preview'})
        check('apercu_pret_sans_mutation', preview['status'] == 'READY' and app._row(case_id)['revision'] == 0,
              {'status': preview['status'], 'diagnostics': preview.get('diagnostics')})
        check('apercu_avant_apres', bool(preview['changes']))
        apply_body = {'draft_id': draft['id'], 'approval_token': preview['approval_token'], 'request_id': 'fixture_apply'}
        applied = job('/draft/apply', apply_body)
        check('adoption_revision_1', applied['revision'] == 1)
        engine = app.engine_for_case(case_id)
        field = next(x for x in engine.catalog() if x['id'] == 'employee_salary')
        check('champ_et_agent_suivent_feuille', field['sheet'] == 'Equipe recette' and
              any(x.get('sheet') == 'Equipe recette' for x in work.agents(case_id)))
        check('nouveau_contrat_agent', any(x.get('sheet') == 'Notes recette' for x in work.agents(case_id)))
        calculated = job('/recalculate', {'request_id': 'fixture_calculate'})
        check('recalcul_revision_2_entrees_preservees', calculated['revision'] == 2 and calculated['inputs_unchanged'])
        wb = Workbook(app._workbook(app._row(case_id)))
        try:
            for cell, expected in [('E163', 60000 * 1.4 * 9 / 12), ('F163', 60000 * 1.4)]:
                actual = wb.value('Equipe recette', cell)
                check('oracle_RH_' + cell, isinstance(actual, (int, float)) and abs(actual - expected) < .01, actual, expected)
            check('formule_nouvelle_feuille', wb.value('Notes recette', 'B1') == 24, wb.value('Notes recette', 'B1'), 24)
        finally:
            wb.close()
        replay = request('POST', prefix + '/draft/apply', apply_body)
        check('rejeu_application_sans_doublon', replay['replayed'] and app._row(case_id)['revision'] == 2)
        downloaded = client.get(prefix + '/download')
        path = folder / 'export_calcule.xlsm'
        path.write_bytes(downloaded.content)
        with zipfile.ZipFile(path) as archive:
            check('download_xlsm_composants', downloaded.status_code == 200 and not archive.testzip() and 'xl/vbaProject.bin' in archive.namelist())
        check('download_copie_exacte', digest(path) == app._row(case_id)['sha256'])
        versions = request('GET', prefix + '/versions')['versions']
        first = next(x for x in versions if x['revision'] == 0)
        restored = job('/versions/' + first['id'] + '/restore', {'request_id': 'fixture_restore'})
        check('restauration_nouvelle_revision', restored['revision'] == 3 and app._row(case_id)['sha256'] == original_sha)
        check('sources_conservees', any(x['id'] == source['id'] for x in request('GET', prefix + '/sources')['sources']))
        check('original_inchange', digest(original) == original_sha)
        receipt.update(status='SUCCES', final_revision=3, source_sha256=original_sha,
                       exported_sha256=digest(path), data_dir=str(folder))
        atomic_json(folder / 'validation.json', receipt)
        print(json.dumps({'status': receipt['status'], 'checks': len(checks), 'data_dir': str(folder)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
