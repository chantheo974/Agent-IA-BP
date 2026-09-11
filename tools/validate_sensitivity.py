"""Préparer sans Excel, puis lancer explicitement une campagne native bornée.

La préparation d'une fixture crée un nouveau dossier fictif via Application.
Aucune copie scalaire n'est une version de dossier et aucun résultat n'est adopté.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.sensitivity_native import prepare_campaign, verify_native
from tca_bp.storage import atomic_json, canonical, uid
from tools.financial_cases_common import common_updates, merge_updates
from tools.financial_cases_sensitivity import cases


def prepare_fixture(engine, directory):
    """Fictif seulement ; aucun dossier courant n'est modifié."""
    directory = Path(directory).resolve()
    if directory.exists() or directory.parent != (ROOT/'runtime').resolve() or not directory.name.startswith('recette_sensitivity_'):
        raise ValueError('Répertoire fictif neuf requis directement sous runtime/recette_sensitivity_*.')
    fixture = cases()[0]
    app = Application(ROOT, directory, engine=engine)
    state = app.create_case('Recette fictive de sensibilité', fixture['title'], case_id=fixture['id'])
    source = app.add_source(fixture['id'], text='SCENARIO LOGICIEL FICTIF. AUCUN CLIENT REEL.\n'+canonical(fixture),
                            title='Événements fictifs de sensibilité')
    updates = [{**item, 'reason': 'Événements fictifs indépendants de sensibilité', 'evidence': source['id'],
                'status': 'NON_RENSEIGNE' if item['value'] is None else 'CONFIRME',
                'override_default': True, 'replace_existing': True}
               for item in merge_updates(common_updates(), fixture['updates'])]
    plan = app.prepare_changes(fixture['id'], updates, 'sensitivity_fixture')
    app.apply_plan(fixture['id'], plan['id'])
    state = app.get_case(fixture['id'])
    manifest = prepare_campaign(engine, Path(state['workbook_path']), directory/'instruments')
    report = {'schema': 'tca-sensitivity-fixture/1', 'status': 'PREPARE_SANS_EXCEL',
              'model_dir': str(engine.model_dir), 'case_id': fixture['id'], 'case_revision': state['revision'],
              'source_path': state['workbook_path'], 'source_sha256': state['sha256'],
              'events': fixture['events'], 'business_oracles': fixture['oracles'],
              'plan_path': str(directory/'instruments/plan.json'), 'plan': manifest}
    atomic_json(directory/'fixture.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--prepare-fixture', action='store_true')
    parser.add_argument('--native', action='store_true', help='Lancement Excel explicite, après coordination du créneau natif.')
    parser.add_argument('--timeout', type=float, default=3600)
    parser.add_argument('--resume', action='store_true', help='Reprendre uniquement les points de contrôle complets d’une tentative interrompue.')
    parser.add_argument('--attempt', default='', help='Suffixe court créant une copie et des reçus neufs sur les mêmes instruments scellés.')
    args = parser.parse_args()
    if args.attempt and not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',args.attempt):
        parser.error('--attempt accepte seulement 1 à40 lettres, chiffres, tirets ou soulignements.')
    engine = ModelEngine(ROOT, model_dir=Path(args.model_dir).resolve())
    engine.ensure_built()
    if args.prepare_fixture:
        if args.native or args.source or args.resume or args.attempt:
            parser.error('--prepare-fixture est une préparation seule, sans --native ni --source.')
        directory = args.directory or ROOT/'runtime'/('recette_sensitivity_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uid()[:8])
        report = prepare_fixture(engine, directory)
        print(json.dumps({'status': report['status'], 'directory': str(directory), 'source': report['source_path']}, ensure_ascii=False))
        return
    if args.directory is None:
        parser.error('--directory requis pour une préparation ou une campagne explicite.')
    directory = args.directory.resolve()
    if args.source:
        source = args.source.resolve()
    else:
        fixture = json.loads((directory/'fixture.json').read_text(encoding='utf-8-sig'))
        source = Path(fixture['source_path'])
    if not args.native:
        if args.resume:
            parser.error('--resume exige --native ; une reprise peut lancer Excel.')
        report = prepare_campaign(engine, source, directory/'instruments')
        print(json.dumps({'status': 'PREPARE_SANS_EXCEL', 'scalars': len(report['scenarios']), 'directory': str(directory)}, ensure_ascii=False))
        return
    suffix=('_'+args.attempt) if args.attempt else ''
    output=directory/('tables_verifiees'+suffix+'.xlsm')
    receipt=directory/('verification'+suffix+'.json')
    result = verify_native(engine, source, output, receipt,
                           prepared=directory/'instruments', timeout=args.timeout,
                           resume=args.resume,
                           progress=lambda event: print(json.dumps(event, ensure_ascii=False), flush=True))
    fixture_path=directory/'fixture.json'
    if fixture_path.is_file():
        from tca_bp.vendor.input_engine import Workbook
        from tools.validate_financial_cases import oracle_results
        fixture=json.loads(fixture_path.read_text(encoding='utf-8-sig'))
        if fixture['source_sha256'] != result['source_sha256']:
            raise ValueError('Les événements économiques ne sont pas liés à cette source.')
        workbook=Workbook(output)
        try:business=oracle_results(workbook.value,fixture['business_oracles'])
        finally:workbook.close()
        atomic_json(directory/('business_oracle_verification'+suffix+'.json'),{'source_sha256':result['source_sha256'],
                    'output_sha256':result['output_sha256'],'oracles':business,'passed':all(x['passed'] for x in business)})
        if not all(x['passed'] for x in business):
            raise ValueError('Les tables concordent avec le modèle, mais un oracle économique de la fixture échoue.')
    print(json.dumps({'status': result['status'], 'comparisons': len(result['comparisons']),
                      'receipt': str(receipt), 'adopted': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
