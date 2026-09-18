"""Explicit private WACC migration and a new fully fictitious qualified case.

Creates a new runtime directory, never edits a source template or an earlier
case, and never transfers an old native proof. Excel runs under the same local
mutex as the application. This is a recipe, not a model publication command.
"""
from __future__ import annotations
import argparse
import datetime as dt
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tca_bp.model_engine import ModelEngine
from tca_bp.storage import atomic_json,digest
from tca_bp.wacc_fingerprint_migration import prepare_fingerprint_variant
from tca_bp.web_lock import serialized_excel
from tools.prepare_qualification_case import prepare,EXPECTED_RELEASE_SHA
from tools.validate_qualified_wacc import run as validate_qualified


@serialized_excel
def run(model_dir,expected_sha256):
    engine=ModelEngine(ROOT,Path(model_dir).resolve());engine.ensure_built()
    if digest(engine.template_path)!=expected_sha256:
        raise ValueError('La trame diffère de la version explicitement attendue.')
    folder=ROOT/'runtime'/('recette_migration_wacc_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir()
    report={'schema':'tca-wacc-fingerprint-native-recipe/1','status':'EN_COURS',
            'source_template_sha256':expected_sha256,'folder':str(folder)}
    atomic_json(folder/'validation.json',report)
    try:
        print('Migration technique native sur copie privée '+str(folder),flush=True)
        migration=prepare_fingerprint_variant(engine,engine.template_path,folder/'variant.xlsm',folder/'model',
            'fixture_fingerprint_migration',timeout=600)
        report['migration_status']=migration.get('status')
        if migration.get('blocked') is not False or not migration.get('model_dir'):
            raise ValueError('La variante technique n’est pas admise.')
        report['migration_receipt_sha256']=digest(folder/'variant.wacc-migration.json')
        print('Préparation de données et déclarations entièrement fictives pour le nouveau modèle',flush=True)
        prepared=prepare(folder/'model',digest(folder/'model'/'TCA_BP_Trame_generique.xlsm'))
        case_folder=Path(prepared['runtime_dir'])
        report['qualified_fixture']=str(case_folder)
        atomic_json(folder/'validation.json',report)
        result=validate_qualified(case_folder)
        report['qualified_receipt_sha256']=digest(case_folder/'validation_service_wacc.json')
        report['checks']=result.get('checks',{});report['oracles']=result.get('oracles',[])
        report['source_preserved']=digest(engine.template_path)==expected_sha256
        report['status']='SUCCES' if result.get('status')=='SUCCES' and report['source_preserved'] else 'ECHEC_RECETTE_QUALIFIEE'
    except BaseException as error:
        report.update(status='ECHEC',error=repr(error));raise
    finally:
        atomic_json(folder/'validation.json',report)
        print(report['status']+' — '+str(folder/'validation.json'),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir',type=Path,default=ROOT/'models'/'generic-v1-release')
    parser.add_argument('--expected-sha256',default=EXPECTED_RELEASE_SHA)
    args=parser.parse_args()
    raise SystemExit(0 if run(args.model_dir,args.expected_sha256)['status']=='SUCCES' else 2)
