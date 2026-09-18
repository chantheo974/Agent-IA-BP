"""Replay the three certified migrations on exactly historical model 1.1.2.

Never replaces an initial selection or an existing model. All native phases
use the application's Excel mutex and all outputs are new private copies.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tca_bp.model_engine import ModelEngine
from tca_bp.storage import atomic_json, digest
from tca_bp.web_lock import serialized_excel
from tca_bp.web_model import ProfileEngine
from tca_bp.wacc_fingerprint_migration import prepare_fingerprint_variant
from tca_bp.dcf_calendar_migration import prepare_calendar_variant
from tools.validate_fiscal_calendar_native import run as fiscal_recipe

EXPECTED = 'e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12'


@serialized_excel
def migrate(engine, folder, operation, evidence):
    folder.mkdir(exist_ok=False)
    result = operation(engine, engine.template_path, folder/'variant.xlsm',
                       folder/'model', evidence, timeout=600)
    if result.get('blocked') is not False or not result.get('model_dir'):
        raise ValueError('Une migration certifiée a été refusée.')
    new_engine = ProfileEngine(ROOT, folder/'model')
    new_engine.ensure_built()
    return new_engine


def run():
    engine = ModelEngine(ROOT, ROOT/'models'/'generic-v1')
    if digest(engine.template_path) != EXPECTED:
        raise ValueError('Seule la trame historique 1.1.2 explicitement épinglée est admissible.')
    engine.ensure_built()
    folder = ROOT/'runtime'/('initial_rebase_112_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir(exist_ok=False)
    report = {'schema':'tca-initial-model-rebase/1', 'status':'EN_COURS',
              'source_template_sha256':EXPECTED, 'source_model_id':engine.schema['model_id'],
              'source_build_version':'1.1.2', 'initial_selection_changed':False}
    try:
        atomic_json(folder/'validation.json', report)
        print('Migration 5 helpers depuis la trame 1.1.2 — '+str(folder), flush=True)
        engine = migrate(engine, folder/'fingerprint', prepare_fingerprint_variant, 'fixture_initial_112_fingerprint')
        report['fingerprint_model_sha256'] = digest(engine.template_path)
        atomic_json(folder/'validation.json', report)
        print('Migration 10 valeurs actualisées, gardes 1.1.2 conservées', flush=True)
        engine = migrate(engine, folder/'dcf', prepare_calendar_variant, 'fixture_initial_112_dcf')
        report['dcf_model_sha256'] = digest(engine.template_path)
        atomic_json(folder/'validation.json', report)
        print('Migration 56 agrégats et recette native complète sur cette filiation', flush=True)
        result = fiscal_recipe(engine.model_dir, digest(engine.template_path))
        report['fiscal_recipe'] = result
        report['source_preserved'] = digest(ROOT/'models'/'generic-v1'/'TCA_BP_Trame_generique.xlsm') == EXPECTED
        report['status'] = 'SUCCES' if result['status']=='SUCCES' and report['source_preserved'] else 'ECHEC_RECETTE'
    except BaseException as error:
        report.update(status='ECHEC', error=repr(error))
        raise
    finally:
        atomic_json(folder/'validation.json', report)
        print(report['status']+' — '+str(folder/'validation.json'), flush=True)
    return report


if __name__ == '__main__':
    raise SystemExit(0 if run()['status']=='SUCCES' else 2)
