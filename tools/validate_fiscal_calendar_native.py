"""Private DCF calendar migration followed by a fresh qualified WACC recipe."""
from __future__ import annotations
import argparse
import datetime as dt
from pathlib import Path
import sys
import uuid
import shutil

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tca_bp.fiscal_calendar_migration import prepare_fiscal_calendar_variant
from tca_bp.storage import atomic_json,digest
from tca_bp.web_lock import serialized_excel
from tca_bp.web_model import ProfileEngine
from tools.prepare_qualification_case import prepare
from tools.validate_qualified_wacc import run as validate
from tools.probe_wacc_calculation import run as probe_calculation


@serialized_excel
def run(model_dir,expected_sha256,*,already_migrated=False):
    model_dir=Path(model_dir).resolve()
    if not model_dir.is_relative_to(ROOT/'runtime'):raise ValueError('La recette attend un modèle privé déjà préparé.')
    engine=ProfileEngine(ROOT,model_dir);engine.ensure_built()
    if digest(engine.template_path)!=expected_sha256:raise ValueError('L’empreinte du modèle privé diffère de celle attendue.')
    folder=ROOT/'runtime'/('recette_calendrier_fiscal_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir()
    report={'schema':'tca-fiscal-calendar-native-recipe/1','status':'EN_COURS','source_sha256':expected_sha256}
    atomic_json(folder/'validation.json',report)
    try:
        if already_migrated:
            from tca_bp.fiscal_calendar_migration import plan_fiscal_calendar_migration
            plan=plan_fiscal_calendar_migration(engine,engine.template_path,'fixture_fiscal_resume')
            if plan['status']!='ALREADY_MIGRATED':raise ValueError('La reprise exige les 56 corrections déjà présentes.')
            print('Nouvelle recette du modèle déjà migré, sans modification : '+str(folder),flush=True)
            shutil.copytree(model_dir,folder/'model')
            report.update(migration_performed=False,resumed_from_model_sha256=expected_sha256)
        else:
            print('Correction native des 56 formules du calendrier fiscal et cash sur copie '+str(folder),flush=True)
            migration=prepare_fiscal_calendar_variant(engine,engine.template_path,folder/'variant.xlsm',folder/'model','fixture_fiscal_calendar',timeout=600)
            if migration.get('blocked') is not False or not migration.get('model_dir'):raise ValueError('La variante calendrier est bloquée.')
            report['migration_receipt_sha256']=digest(folder/'variant.fiscal-calendar.json')
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
        from tca_bp.service import Application
        from tca_bp.vendor.input_engine import Workbook
        current_engine=ProfileEngine(ROOT,folder/'model')
        app=Application(ROOT,Path(prepared['runtime_dir']),engine=current_engine)
        current=app.get_case(prepared['case_id']);wb=Workbook(Path(current['workbook_path']))
        report['fiscal_cash_oracles']=[]
        try:
            for index,column in enumerate('CDE'):
                for sheet,row,expected_value in [('ATELIER_CIR_IS',34,0),('Modèle financier',310,0),
                        ('Modèle financier',311,0),('Modèle financier',320,48000),
                        ('Modèle financier',321,100000+72000*(index+1))]:
                    value=wb.value(sheet,column+str(row))
                    report['fiscal_cash_oracles'].append({'sheet':sheet,'cell':column+str(row),'actual':value,
                        'expected':expected_value,'passed':type(value) in (int,float) and abs(value-expected_value)<.01})
        finally:wb.close()
        report['checks']['fiscal_cash_oracles']=all(x['passed'] for x in report['fiscal_cash_oracles'])
        report['source_preserved']=digest(engine.template_path)==expected_sha256
        report['status']='SUCCES' if result.get('status')=='SUCCES' and report['source_preserved'] and report['checks']['fiscal_cash_oracles'] else 'ECHEC_RECETTE'
    except BaseException as error:
        report.update(status='ECHEC',error=repr(error));raise
    finally:
        atomic_json(folder/'validation.json',report)
        print(report['status']+' — '+str(folder/'validation.json'),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir',type=Path,required=True);parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--already-migrated',action='store_true',help='Nouvelle recette sur copie du modèle exact déjà corrigé ; ne réécrit aucun ancien reçu.')
    args=parser.parse_args()
    raise SystemExit(0 if run(args.model_dir,args.expected_sha256,already_migrated=args.already_migrated)['status']=='SUCCES' else 2)
