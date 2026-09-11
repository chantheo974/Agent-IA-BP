"""Exercer le service WACC réel sur une préparation fictive explicitement figée."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tca_bp.model_engine import ModelEngine
from tca_bp.model_registry import model_pin
from tca_bp.service import Application
from tca_bp.storage import atomic_json, digest
from tca_bp.vendor.input_engine import Workbook
from tools.validate_financial_cases import oracle_results


def validate_prepared_identity(prepared, before, described, folder):
    """La recette doit calculer exactement le cas et les artefacts annoncés."""
    if prepared.get('case_id') != 'test_qualifications_wacc':
        raise ValueError('Identifiant de dossier fictif WACC inattendu.')
    if Path(prepared.get('runtime_dir', '')).resolve() != folder.resolve():
        raise ValueError('La préparation appartient à un autre répertoire de recette.')
    expected = model_pin(described)
    if not all(expected.values()) or model_pin(before) != expected:
        raise ValueError('Le modèle épinglé au dossier diffère du modèle de la recette.')
    if prepared.get('model_sha256') != expected['template_sha256']:
        raise ValueError('La trame préparée diffère du modèle de la recette.')


def run(folder: Path):
    folder = folder.resolve()
    if folder.parent != ROOT / 'runtime' or not folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('La préparation doit être un dossier fictif identifié sous runtime/.')
    prepared = json.loads((folder / 'preparation.json').read_text(encoding='utf8'))
    output_report = folder / 'validation_service_wacc.json'
    if output_report.exists():
        raise ValueError('Cette tentative possède déjà un reçu ; conserver ses preuves et préparer un nouveau dossier.')
    if (prepared.get('schema') != 'tca-bp-qualified-fixture/1'
            or prepared.get('native_executed') is not False or prepared.get('status') != 'PRET_AVANT_WACC_NATIF'):
        raise ValueError('Préparation WACC qualifiée requise.')
    if prepared.get('case_id') != 'test_qualifications_wacc':
        raise ValueError('Identifiant de dossier fictif WACC inattendu.')
    engine = ModelEngine(ROOT, model_dir=Path(prepared['model_dir']))
    build = engine.ensure_built()
    if build['template_sha256'] != prepared['model_sha256']:
        raise ValueError('Le modèle a changé depuis la préparation.')
    app = Application(ROOT, folder, engine=engine)
    case_id = prepared['case_id']
    before = app.get_case(case_id)
    validate_prepared_identity(prepared, before, app.registry.describe(engine), folder)
    if before['sha256'] != prepared['source_sha256'] or before['revision'] != prepared['case_revision']:
        raise ValueError('Le dossier a changé depuis la préparation.')
    source = Path(before['workbook_path'])
    report = {'schema': 'tca-bp-qualified-wacc-validation/1', 'status': 'EN_COURS',
              'case_id': case_id, 'template_sha256': build['template_sha256'],
              'schema_sha256': build['schema_sha256'], 'source_sha256': before['sha256'],
              'model_pin': model_pin(before),
              'preparation_sha256': digest(folder / 'preparation.json')}
    atomic_json(output_report, report)
    try:
        print('Résolution native puis adoption par le service du dossier qualifié.', flush=True)
        native = app.solve_wacc(case_id, timeout=600)
        report['native_service_receipt'] = native
        current = app.get_case(case_id)
        workbook = Workbook(Path(current['workbook_path']))
        try:
            report['oracles'] = oracle_results(workbook.value, prepared['oracles_after_wacc'])
        finally:
            workbook.close()
        inspection = app.inspect(case_id, 'Valorisation', ['D7', 'D40'])
        report['inspection'] = inspection
        # Tester le vrai chemin de lecture avec ses qualifications et preuves,
        # en plus du cache natif. Un résultat masqué échoue à cette recette.
        inspected = inspection.get('cells', {})
        display_checks = {}
        for oracle in prepared['oracles_after_wacc']:
            if oracle['sheet'] != 'Valorisation':
                continue
            cell = inspected.get(oracle['cell'], {})
            value = cell.get('current', cell).get('value')
            display_checks[oracle['id']] = (type(value) in (int, float)
                and abs(value - oracle['expected']) <= oracle['tolerance'])
        scopes = current.get('qualified_availability', {})
        report['checks'] = {
            'native_adopted': native.get('adopted') is True,
            'new_revision': current['revision'] == before['revision'] + 1,
            'source_preserved': digest(source) == before['sha256'],
            'model_preserved': digest(engine.template_path) == build['template_sha256'],
            'wacc_proof_current': current.get('wacc_verified') is True,
            'outputs_current': current.get('outputs_current') is True,
            'all_oracles_pass': all(item['passed'] for item in report['oracles']),
            'qualified_outputs_displayed': len(display_checks) == 2 and all(display_checks.values()),
        }
        report['qualified_availability'] = scopes
        report['display_checks'] = display_checks
        report['status'] = 'SUCCES' if all(report['checks'].values()) else 'ECHEC_ORACLES_OU_SERVICE'
        print(json.dumps({'status': report['status'], 'checks': report['checks'], 'display_checks': display_checks}), flush=True)
    except Exception as error:
        report.update(status='ECHEC_EXECUTION', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        atomic_json(output_report, report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared_folder', type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.prepared_folder)['status'] == 'SUCCES' else 2)
