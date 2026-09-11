"""Recette native WACC sur l'unique scénario mathématique fictif désigné."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.storage import atomic_json, digest
from tca_bp.vendor.input_engine import Workbook
from tca_bp.wacc_native import solve_native
from tools.validate_financial_cases import resume
from tools.financial_cases_wacc import cases


def run(folder, attempt='wacc'):
    if not attempt.replace('_', '').isalnum():
        raise ValueError('Identifiant de tentative alphanumérique requis.')
    folder = Path(folder).resolve()
    if folder.parent != ROOT / 'runtime' or not folder.name.startswith('recette_financiere_'):
        raise ValueError('Espace de recette financière fictive requis.')
    state = json.loads((folder / 'validation.json').read_text(encoding='utf-8-sig'))
    if state.get('group') != 'wacc' or [c['id'] for c in state['cases']] != ['wacc_unlevered']:
        raise ValueError('Seul le cas WACC fictif désigné est autorisé.')
    if state['status'] == 'PREPARE':
        state = resume(folder)
    if state['status'] != 'SUCCES' or not state.get('native'):
        raise ValueError('Le dossier fictif doit avoir passé ses premiers oracles natifs.')
    proof_path = folder / f'{attempt}_validation.json'
    if proof_path.exists():
        raise ValueError('Une campagne WACC existe déjà ; aucune preuve antérieure remplacée.')
    engine = ModelEngine(ROOT, model_dir=Path(state['model_dir']))
    app = Application(ROOT, folder, engine=engine)
    current = app.get_case('wacc_unlevered')
    source = Path(current['workbook_path'])
    expected_case = cases()[0]
    if current['sha256'] != state['cases'][0]['native']['output_sha256'] or digest(source) != current['sha256']:
        raise ValueError('Le cas a changé depuis la première recette.')
    proof = {'schema': 'tca-bp-wacc-recipe/1', 'status': 'EN_COURS', 'fictional': True,
             'source_sha256': current['sha256'], 'model_template_sha256': state['template_sha256'],
             'model_schema_sha256': state['schema_sha256'], 'checks': [], 'adopted_as_case': False}
    atomic_json(proof_path, proof)
    try:
        before = engine.context(source)
        output, receipt = folder / f'{attempt}_resolution.xlsm', folder / f'{attempt}_resolution.json'
        print('Résolution locale Excel sans macro : dossier WACC fictif.', flush=True)
        native = solve_native(source, output, receipt, timeout=600)
        proof['native'] = native
        after = engine.context(output)
        proof['checks'].append({'name': 'inputs_preserved', 'passed': before['input_signature'] == after['input_signature']})
        wb = Workbook(output)
        try:
            for address, expected, tolerance in [('D136', expected_case['wacc_expected'], 1e-9),
                                                  ('D40', expected_case['equity_expected'], 0.01)]:
                value = wb.value('Valorisation', address)
                passed = isinstance(value, (int, float)) and not isinstance(value, bool) and abs(value - expected) <= tolerance
                proof['checks'].append({'name': 'oracle_' + address, 'actual': value, 'expected': expected,
                                        'tolerance': tolerance, 'passed': passed})
            proof['checks'].append({'name': 'freshness_saved', 'passed': wb.value('Valorisation','D155') == wb.value('Valorisation','D156')})
        finally:
            wb.close()
        proof['checks'].append({'name': 'source_preserved', 'passed': digest(source) == current['sha256']})
        proof['status'] = 'SUCCES' if all(c['passed'] for c in proof['checks']) else 'ECHEC_ORACLES'
    except Exception as error:
        proof.update(status='ECHEC_EXECUTION', error=type(error).__name__ + ': ' + str(error))
        atomic_json(proof_path, proof)
        raise
    atomic_json(proof_path, proof)
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--attempt', default='wacc')
    args = parser.parse_args()
    result = run(args.folder, args.attempt)
    print(json.dumps({'status': result['status'], 'checks': result['checks']}, ensure_ascii=False))
    raise SystemExit(0 if result['status'] == 'SUCCES' else 2)
