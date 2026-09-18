"""Private DCF calendar migration followed by a fresh qualified WACC recipe."""
from __future__ import annotations
import argparse
import datetime as dt
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tca_bp.dcf_calendar_migration import prepare_calendar_variant
from tca_bp.storage import atomic_json,digest
from tca_bp.web_lock import serialized_excel
from tca_bp.web_model import ProfileEngine
from tools.prepare_qualification_case import prepare
from tools.validate_qualified_wacc import run as validate
from tools.probe_wacc_calculation import run as probe_calculation


@serialized_excel
def run(model_dir,expected_sha256):
    model_dir=Path(model_dir).resolve()
    if not model_dir.is_relative_to(ROOT/'runtime'):raise ValueError('La recette attend un modèle privé déjà préparé.')
    engine=ProfileEngine(ROOT,model_dir);engine.ensure_built()
    if digest(engine.template_path)!=expected_sha256:raise ValueError('L’empreinte du modèle privé diffère de celle attendue.')
    folder=ROOT/'runtime'/('recette_calendrier_dcf_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir()
    report={'schema':'tca-dcf-calendar-native-recipe/1','status':'EN_COURS','source_sha256':expected_sha256}
    atomic_json(folder/'validation.json',report)
    try:
        print('Correction native du calendrier DCF sur copie '+str(folder),flush=True)
        migration=prepare_calendar_variant(engine,engine.template_path,folder/'variant.xlsm',folder/'model','fixture_calendar',timeout=600)
        if migration.get('blocked') is not False or not migration.get('model_dir'):raise ValueError('La variante calendrier est bloquée.')
        report['migration_receipt_sha256']=digest(folder/'variant.dcf-calendar.json')
        prepared=prepare(folder/'model',digest(folder/'model'/'TCA_BP_Trame_generique.xlsm'))
        report['qualified_fixture']=prepared['runtime_dir'];atomic_json(folder/'validation.json',report)
        probe=probe_calculation(Path(prepared['runtime_dir']),automatic_inputs=True)
        observations=probe.get('observations',[])
        for item in observations:
            candidate=item['candidate']
            expected=sum(72000/(1+candidate)**year for year in (1,2,3))+73440/(candidate-.02)/(1+candidate)**3
            if (type(item.get('calculated')) not in (int,float) or abs(item['calculated']-.09)>1e-10
                    or type(item.get('equity')) not in (int,float) or abs(item['equity']-expected)>.02):
                raise ValueError('Les deux observations natives préalables ne correspondent pas aux oracles indépendants.')
        if len(observations)!=2:raise ValueError('Deux observations natives préalables sont requises.')
        report['native_preflight']=observations;atomic_json(folder/'validation.json',report)
        result=validate(Path(prepared['runtime_dir']))
        report['qualified_receipt_sha256']=digest(Path(prepared['runtime_dir'])/'validation_service_wacc.json')
        report['checks']=result.get('checks',{});report['oracles']=result.get('oracles',[])
        report['source_preserved']=digest(engine.template_path)==expected_sha256
        report['status']='SUCCES' if result.get('status')=='SUCCES' and report['source_preserved'] else 'ECHEC_RECETTE'
    except BaseException as error:
        report.update(status='ECHEC',error=repr(error));raise
    finally:
        atomic_json(folder/'validation.json',report)
        print(report['status']+' — '+str(folder/'validation.json'),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir',type=Path,required=True);parser.add_argument('--expected-sha256',required=True)
    args=parser.parse_args()
    raise SystemExit(0 if run(args.model_dir,args.expected_sha256)['status']=='SUCCES' else 2)
