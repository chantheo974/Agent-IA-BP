"""Verify real exports and a traceable restore after the fictitious cockpit recipe.

Run only after validate_cockpit_native.py has succeeded. The calculated scenario
is retained and exported; its parent is restored to the recorded baseline as a
new revision. No new financial calculation or provider call is performed.
"""
import argparse
import io
import json
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from tca_bp.decision_exports import read_identity
from tca_bp.service import Application
from tca_bp.storage import atomic_json, confined, digest
from tca_bp.web_model import ProfileEngine
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace


def run(folder):
    folder = Path(folder).resolve(strict=True)
    if folder.parent != ROOT / 'runtime' or not folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('Utiliser le dossier fictif de la recette cockpit native.')
    output = folder / 'validation_cockpit_delivery.json'
    if output.exists():
        raise ValueError('Conserver la précédente recette de livraison.')
    native = json.loads((folder / 'validation_cockpit_native.json').read_text(encoding='utf-8'))
    if native['status'] != 'PASS':
        raise ValueError('La recette financière doit avoir réussi avant les exports.')
    prepared = json.loads((folder / 'preparation.json').read_text(encoding='utf-8'))
    app = Application(ROOT, folder, engine=ProfileEngine(ROOT, Path(prepared['model_dir'])))
    work = WebWorkspace(app)
    api = create_app(app, workspace=work)
    parent_id, child_id = native['case_id'], native['simulation']['scenario_case_id']
    result = {'status': 'RUNNING', 'scope': 'FICTITIOUS_COCKPIT_EXPORTS_AND_RESTORE',
              'case_id': parent_id, 'scenario_case_id': child_id, 'checks': [],
              'native_recalculation_performed_here': False, 'provider_exercised': False}

    def check(name, valid, actual=None):
        result['checks'].append({'name': name, 'pass': bool(valid), 'actual': actual})
        atomic_json(output, result)
        if not valid:
            raise AssertionError(name + ': ' + str(actual))

    try:
        with TestClient(api, base_url='http://127.0.0.1:8793') as client:
            def request(case_id, method, route, body=None):
                response = client.request(method, '/api/cases/' + case_id + route, json=body)
                response.raise_for_status()
                return response.json()

            def wait(case_id, queued):
                deadline = time.monotonic() + 300
                while time.monotonic() < deadline:
                    job = next(j for j in request(case_id, 'GET', '/jobs')['jobs'] if j['id'] == queued['job']['id'])
                    if job['status'] == 'SUCCEEDED':
                        return job['result']
                    if job['status'] in ('FAILED', 'INTERRUPTED'):
                        raise ValueError(str(job))
                    time.sleep(.5)
                raise TimeoutError('Le travail de livraison ne se termine pas.')

            child = app.get_case(child_id)
            parent = app.get_case(parent_id)
            check('scenario_remains_calculated', child['outputs_current'])
            print('Génération des quatre formats depuis la copie calculée et conservée.', flush=True)
            report = wait(child_id, request(child_id, 'POST', '/reports', {
                'expected_revision': child['revision'], 'request_id': 'cockpit_delivery_four_formats'}))
            result['report'] = report
            check('four_formats', set(report['files']) == {'xlsm', 'pdf', 'docx', 'pptx'})
            snapshot_path = confined(app.store.case_dir(child_id), report['snapshot'])
            snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
            check('single_snapshot_matches_calculated_scenario', snapshot['case_id'] == child_id
                  and snapshot['revision'] == child['revision'] and snapshot['workbook_sha256'] == child['sha256']
                  and digest(snapshot_path) == report['snapshot_sha256'])
            series = {s['id']: s for s in snapshot['series']}
            for oracle in native['oracles']:
                current = series[oracle['metric']]
                index = current['categories'].index(oracle['period'])
                check('snapshot_' + oracle['metric'] + '_' + oracle['period'],
                      abs(current['values'][index] - oracle['expected']) < .01)
            downloads = {}
            for kind, descriptor in report['files'].items():
                response = client.get(f'/api/cases/{child_id}/reports/{report["id"]}/{kind}')
                response.raise_for_status()
                path = confined(app.store.case_dir(child_id), descriptor['path'])
                check('download_' + kind, response.content == path.read_bytes()
                      and digest(path) == descriptor['sha256'] and len(response.content) > 1000)
                downloads[kind] = response.content
            with zipfile.ZipFile(io.BytesIO(downloads['xlsm'])) as exported, zipfile.ZipFile(child['workbook_path']) as source:
                check('xlsm_identity_matches_snapshot', read_identity(exported) == report['identity'])
                altered = [name for name in source.namelist()
                           if name not in {'docProps/custom.xml', '_rels/.rels', '[Content_Types].xml'}
                           and (name not in exported.namelist() or exported.read(name) != source.read(name))]
                check('every_workbook_component_preserved', not altered, altered)
            with zipfile.ZipFile(io.BytesIO(downloads['docx'])) as word:
                check('word_has_editable_tables', b'<w:tbl>' in word.read('word/document.xml'))
            with zipfile.ZipFile(io.BytesIO(downloads['pptx'])) as slides:
                names = slides.namelist()
                check('powerpoint_has_editable_chart_and_workbook',
                      any(name.startswith('ppt/charts/chart') and name.endswith('.xml') for name in names)
                      and any(name.startswith('ppt/embeddings/') and name.endswith('.xlsx') for name in names))
            check('pdf_file', downloads['pdf'].startswith(b'%PDF-'))
            reimport = client.post(f'/api/cases/{child_id}/roundtrip',
                                  data={'expected_revision': str(child['revision']), 'request_id': 'cockpit_delivery_roundtrip'},
                                  files={'file': ('TCA_BP.xlsm', downloads['xlsm'], 'application/vnd.ms-excel.sheet.macroEnabled.12')})
            reimport.raise_for_status()
            check('unchanged_export_reimport_is_noop', reimport.json()['status'] == 'IDENTIQUE', reimport.json()['status'])
            check('exports_leave_both_workbooks_unchanged', app.get_case(child_id)['sha256'] == child['sha256']
                  and app.get_case(parent_id)['sha256'] == parent['sha256'])

            print('Restauration de la référence historique sous une nouvelle révision.', flush=True)
            versions = request(parent_id, 'GET', '/versions')['versions']
            target = next(v for v in versions if v['revision'] == native['simulation']['base_revision'])
            before_versions = {v['id']: v for v in versions}
            restored = wait(parent_id, request(parent_id, 'POST', '/versions/' + target['id'] + '/restore',
                                               {'request_id': 'cockpit_delivery_restore'}))
            after = app.get_case(parent_id)
            check('restore_creates_new_revision', after['revision'] == parent['revision'] + 1)
            check('restored_exact_historical_bytes', after['sha256'] == target['sha256'])
            check('adopted_version_still_available', digest(Path(parent['workbook_path'])) == parent['sha256'])
            check('older_versions_retained', before_versions.keys() <= {v['id'] for v in request(parent_id, 'GET', '/versions')['versions']})
            check('saved_scenario_still_available', app.get_case(child_id)['sha256'] == child['sha256'])
            replay = wait(parent_id, request(parent_id, 'POST', '/versions/' + target['id'] + '/restore',
                                             {'request_id': 'cockpit_delivery_restore'}))
            check('restore_lost_response_no_duplicate_revision', app.get_case(parent_id)['revision'] == after['revision']
                  and replay == restored)
            result['restore'] = restored
            result['status'] = 'PASS'
    except Exception as error:
        result.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        atomic_json(output, result)
        work.close()
    print(json.dumps({'status': result['status'], 'checks': len(result['checks']), 'receipt': str(output)}), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.folder)['status'] == 'PASS' else 2)
