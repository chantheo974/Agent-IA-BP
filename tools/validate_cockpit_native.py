"""Fictitious native Excel acceptance of the connected cockpit transaction.

The independent oracle separates recognition, invoicing and customer receipts.
No client document or AI provider is involved. A newly prepared qualified
fixture is required; previous receipts and original templates stay intact.
"""
from pathlib import Path
import argparse
import json
import sys
import time
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from tca_bp.service import Application
from tca_bp.storage import atomic_json, digest
from tca_bp.web_model import ProfileEngine
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace
from tools.financial_cases_operations import cases


def run(folder, resume=False, correct_stock=False):
    folder = Path(folder).resolve()
    if folder.parent != ROOT / 'runtime' or not folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('Utiliser un nouveau dossier de recette fictive qualifiée.')
    receipt = folder / 'validation_cockpit_native.json'
    previous = None
    if receipt.exists():
        if not resume:
            raise ValueError('Le reçu précédent doit être conservé ; une reprise explicite est nécessaire.')
        previous = json.loads(receipt.read_text(encoding='utf-8'))
        if previous['status'] == 'PASS':
            raise ValueError('Cette recette est déjà terminée.')
        shutil.copyfile(receipt, receipt.with_name('validation_cockpit_native_attempt_' + uuid.uuid4().hex[:8] + '.json'))
    preparation = json.loads((folder / 'preparation.json').read_text(encoding='utf-8'))
    app = Application(ROOT, folder, engine=ProfileEngine(ROOT, Path(preparation['model_dir'])))
    work = WebWorkspace(app)
    case_id = preparation['case_id']
    result = {'status': 'RUNNING', 'scope': 'FICTITIOUS_NATIVE_COCKPIT', 'provider_exercised': False,
              'case_id': case_id, 'model_sha256': preparation['model_sha256'], 'checks': [], 'oracles': []}

    def check(name, passed, actual=None):
        result['checks'].append({'name': name, 'pass': bool(passed), 'actual': actual})
        atomic_json(receipt, result)
        if not passed:
            raise AssertionError(name + ': ' + str(actual))

    try:
        if resume:
            with app.store.connection() as db:
                source = dict(db.execute("SELECT * FROM sources WHERE case_id=? AND title=?", (case_id, 'Convention fictive : cockpit et chronologie du contrat')).fetchone())
            if not previous or not previous.get('simulation'):
                raise ValueError('Reprise automatique de la recette réservée à une simulation déjà calculée.')
            if app.get_case(case_id)['revision'] != previous['simulation']['base_revision']:
                raise ValueError('La référence a changé ; ne pas rejouer la recette.')
            result['previous_attempt_preserved'] = True
            if correct_stock:
                work.discard(case_id)
                correction = app.add_source(case_id, title='Correction explicite du jeu fictif : stock inactif',
                                            text='RECETTE LOGICIELLE FICTIVE. Aucun stock, achat ni fournisseur dans ce scénario de prestation. Couverture et délai fournisseur explicitement nuls : Stock!E10=0 et E11=0. Le délai CLIENT de 30 jours est conservé. Financement initial 100000 EUR. Aucun changement de règle fiscale ou financière.')
                fix = app.prepare_changes(case_id, [{'sheet': 'Stock', 'cell': 'E11', 'value': 0, 'status': 'CONFIRME',
                    'evidence': correction['id'], 'reason': 'Stock explicitement inactif et aucun achat dans le jeu de test.',
                    'replace_existing': True}], 'cockpit_native_stock_fixture_correction')
                result['fixture_correction'] = app.apply_plan(case_id, fix['id'])
                print('Correction documentée du jeu fictif : délai fournisseur nul pour le stock inactif ; recalcul de la référence.', flush=True)
                app.recalculate(case_id)
        else:
            timing = next(item for item in cases() if item['id'] == 'operations_deposit_pca_fae')
            source = app.add_source(case_id, title='Convention fictive : cockpit et chronologie du contrat',
                                    text='RECETTE FICTIVE UNIQUEMENT. ' + '\n'.join(timing['events']) +
                                    '\nOn conserve les 100000 EUR de financement du jeu initial. Aucun achat ni fournisseur : Stock!E11=0, module stock inactif. Variante : prix doublé à 24000 EUR, toutes autres conditions inchangées.')
            timing['updates'] = [{**item, 'value': 0} if item['sheet'] == 'Stock' and item['cell'] == 'E11' else item for item in timing['updates']]
            updates = [{**item, 'status': 'NON_RENSEIGNE' if item['value'] is None else 'CONFIRME',
                        'evidence': source['id'], 'reason': 'Convention de recette fictive explicitement fixée.',
                        'replace_existing': True, 'override_default': True} for item in timing['updates']]
            plan = app.prepare_changes(case_id, updates, 'cockpit_native_initial_timing')
            app.apply_plan(case_id, plan['id'])
            app.declare_qualification(case_id, {'module': 'DATA Contrats', 'state': 'ACTIF', 'status': 'CONFIRME',
                                               'evidence': source['id'], 'reason': 'Contrat fictif décrit et fixé par le jeu de recette.'})
            print('Recalcul de la référence fictive : contrat reconnu sur trois mois, deux factures et délai de règlement.', flush=True)
            app.recalculate(case_id)
        api = create_app(app, workspace=work)
        prefix = '/api/cases/' + case_id
        with TestClient(api, base_url='http://127.0.0.1:8792') as client:
            def request(method, route, body=None):
                response = client.request(method, prefix + route, json=body)
                if response.status_code != 200:
                    raise ValueError(f'{method} {route}: {response.status_code}: {response.text[:1800]}')
                return response.json()

            def wait(queued):
                ident = queued['job']['id']
                deadline = time.monotonic() + 900
                last = None
                while time.monotonic() < deadline:
                    job = next(item for item in request('GET', '/jobs')['jobs'] if item['id'] == ident)
                    if job.get('progress') != last:
                        last = job.get('progress')
                        print(json.dumps(last, ensure_ascii=False), flush=True)
                    if job['status'] in ('FAILED', 'INTERRUPTED'):
                        raise ValueError(str(job))
                    if job['status'] == 'SUCCEEDED':
                        return job['result']
                    time.sleep(.5)
                raise TimeoutError('Travail natif non terminé dans le délai de recette.')

            before = app.get_case(case_id)
            request_suffix = '_' + str(before['revision'])
            check('baseline_calculated', before['outputs_current'], before['calculation_status'])
            catalog = request('GET', '/cockpit/catalog')
            check('thirty_three_real_sheets', len(catalog['sheets']) == 33, len(catalog['sheets']))
            sheet = next(item for item in catalog['sheets'] if item['name'] == 'DATA Contrats')
            source_sha = digest(Path(before['workbook_path']))
            body = {'expected_revision': before['revision'], 'request_id': 'native_cockpit_price' + request_suffix,
                    'scope': {'sheet': sheet['name'], 'range': 'F14'},
                    'operations': [{'type': 'set_value', 'sheet': sheet['name'], 'cell': 'F14', 'value': 24000,
                                    'evidence_id': source['id'], 'status': 'CONFIRME', 'reason': 'Prix du scénario fictif explicitement fixé.'}]}
            draft = request('POST', '/cockpit/operations', body)
            check('same_request_same_draft', request('POST', '/cockpit/operations', body)['id'] == draft['id'])
            impacts = request('GET', '/cockpit/draft/impacts')
            check('exact_draft_can_simulate', impacts['can_simulate'], impacts['blocking_reasons'])
            submit = {'expected_revision': before['revision'], 'request_id': 'native_cockpit_simulation' + request_suffix,
                      'draft_id': draft['id'], 'draft_fingerprint': impacts['draft_fingerprint'], 'name': 'Contrat fictif 24000 EUR'}
            queued = request('POST', '/cockpit/simulations', submit)
            check('lost_response_reuses_job', request('POST', '/cockpit/simulations', submit)['job']['id'] == queued['job']['id'])
            scenario = wait(queued)
            result['simulation'] = scenario
            check('simulation_ready', scenario['status'] == 'READY', scenario['status'])
            check('reference_untouched', app.get_case(case_id)['revision'] == before['revision']
                  and digest(Path(before['workbook_path'])) == source_sha)
            series = {item['id']: item for item in scenario['series']}
            expected = {'revenue': {10: 8000, 11: 8000, 12: 8000, 15: 0},
                        'billed_revenue': {10: 12000, 11: 0, 12: 0, 15: 12000},
                        'customer_receipts': {10: 0, 11: 12000, 12: 0, 15: 0, 16: 12000},
                        'cash': {10: 100000, 11: 112000, 12: 112000, 16: 124000}}
            for metric, months in expected.items():
                for month, value in months.items():
                    actual = series[metric]['values'][month]
                    result['oracles'].append({'metric': metric, 'period': series[metric]['categories'][month],
                                              'actual': actual, 'expected': value,
                                              'pass': actual is not None and abs(actual - value) <= .01})
            check('independent_recognition_invoice_receipts_cash_oracles', all(item['pass'] for item in result['oracles']), result['oracles'])
            ident = scenario['id']
            kept = request('POST', '/cockpit/simulations/' + ident + '/keep',
                           {'expected_revision': before['revision'], 'request_id': 'native_cockpit_keep' + request_suffix})
            check('kept_same_copy', kept['saved'] and kept['scenario_case_id'] == scenario['scenario_case_id'])
            proposed = request('POST', '/cockpit/simulations/' + ident + '/propose-adoption',
                               {'expected_revision': before['revision'], 'request_id': 'native_cockpit_adopt' + request_suffix})
            check('adoption_remains_a_draft', proposed['id'] == draft['id'] and app.get_case(case_id)['revision'] == before['revision'])
            preview = wait(request('POST', '/draft/preview', {'request_id': 'native_cockpit_preview' + request_suffix}))
            current = request('GET', '/draft')
            check('approval_token_required', current['status'] == 'READY' and bool(current.get('approval_token')), current['status'])
            adopted = wait(request('POST', '/draft/apply', {'request_id': 'native_cockpit_apply' + request_suffix, 'approval_token': current['approval_token']}))
            check('adopted_new_revision', app.get_case(case_id)['revision'] == before['revision'] + 1, adopted)
            result['status'] = 'PASS'
    except Exception as error:
        result.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        atomic_json(receipt, result)
        work.close()
    print(json.dumps({'status': result['status'], 'checks': len(result['checks']), 'oracles': len(result['oracles']), 'receipt': str(receipt)}), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--correct-stock', action='store_true', help='Corriger explicitement le seul délai fournisseur contradictoire de la première recette fictive.')
    args = parser.parse_args()
    if args.correct_stock and not args.resume:
        parser.error('--correct-stock exige --resume')
    raise SystemExit(0 if run(args.folder, args.resume, args.correct_stock)['status'] == 'PASS' else 2)
