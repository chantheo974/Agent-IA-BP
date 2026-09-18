"""Native acceptance on a previously prepared fictitious qualification case.

The supplied folder must be a named runtime fixture. Every attempt creates a
new directory and new XLSM files; source cases and template files are preserved.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.storage import atomic_json,digest
from tca_bp.web_model import ProfileEngine,seal_profile_model
from tca_bp.web_model_profile import initial_profile,map_location
from tca_bp.web_structure import prepare_variant
from tca_bp.decision_offers import OFFER_BLOCKS
from tca_bp.vendor.input_engine import Workbook
from tca_bp.native_excel import recalculate
from tca_bp.web_lock import serialized_excel


@serialized_excel
def run(prepared_folder,kind,resume_variant=None):
    prepared_folder=Path(prepared_folder).resolve()
    if prepared_folder.parent!=ROOT/'runtime' or not prepared_folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('Une préparation fictive identifiée est requise.')
    fixture=json.loads((prepared_folder/'preparation.json').read_text(encoding='utf-8'))
    if fixture['case_id']!='test_qualifications_wacc':raise ValueError('Dossier fictif inattendu.')
    engine=ModelEngine(ROOT,model_dir=Path(fixture['model_dir']))
    app=Application(ROOT,prepared_folder,engine=engine)
    row=app._row(fixture['case_id']);source=app._workbook(row)
    before=digest(source)
    folder=ROOT/'runtime'/('recette_bloc_'+kind+'_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir()
    report={'schema':'tca-repeatable-native/1','kind':kind,'status':'EN_COURS','source_sha256':before}
    atomic_json(folder/'validation.json',report)
    try:
        profile=initial_profile(engine,source)
        if kind=='register':operation={'type':'extend_register','sheet':'Effectifs','count':1,'evidence_id':'fixture'}
        else:operation={'type':'extend_offer','sheet':'Assumptions','name':'Offre fictive 14','family':'produit_libre','evidence_id':'fixture','sheets':[*OFFER_BLOCKS,'BFR']}
        variant_path=folder/'variant.xlsm';model_dir=folder/'model'
        if resume_variant is None:
            print('Variante native '+str(folder),flush=True)
            variant=prepare_variant(source,variant_path,profile,[operation],timeout=900)
        else:
            previous=Path(resume_variant).resolve()
            if previous.parent!=ROOT/'runtime' or not previous.name.startswith('recette_bloc_'+kind+'_'):
                raise ValueError('Une variante de recette fictive du même type est requise.')
            variant_path=previous/'variant.xlsm';model_dir=previous/'model'
            variant=json.loads((previous/'variant.variant.json').read_text(encoding='utf-8'))
            if variant.get('blocked') is not False or variant.get('source_sha256')!=before or digest(variant_path)!=variant.get('output_sha256'):
                raise ValueError('La variante précédente a changé ou n’est pas validée.')
            report['resumed_variant']={'folder':str(previous),'receipt_sha256':digest(previous/'variant.variant.json'),
                                       'variant_sha256':digest(variant_path)}
            print('Reprise financière de la variante vérifiée '+str(previous)+' dans '+str(folder),flush=True)
        report['variant']={'blocked':variant['blocked'],'diagnostics':variant['diagnostics'],
                           'reference_repairs':variant.get('reference_repairs_count',len(variant['reference_repairs']))}
        if variant['blocked']:raise ValueError('Diagnostic de variante bloquant.')
        print('Scellement et contrat des nouvelles entrées',flush=True)
        if resume_variant is None:seal_profile_model(engine,variant_path,variant['profile'],model_dir)
        adapted=ProfileEngine(ROOT,model_dir);adapted.ensure_built()
        if digest(adapted.template_path)!=digest(variant_path):raise ValueError('Le modèle scellé ne correspond pas à la variante reprise.')
        extension=adapted.profile['business_extensions'][-1]
        by_source={(o['original_sheet'],o['source_cell']):o for o in extension['owners']}
        values=[]
        if kind=='register':
            records={'B116':'Poste fictif supplémentaire','C116':'Administration et Finance','D116':'G&A','E116':0,
                     'F116':'2026-01-01','G116':'2026-12-31','H116':1,'I116':60000,'J116':.4,'L116':'Recrute'}
            values=[('Effectifs',c,v) for c,v in records.items()]
        else:
            records={'C27':1,'D27':'unité','E27':'Oui','F27':100,'K27':120,'L27':120,'M27':120,
                     'P27':0,'Q27':0,'R27':0,'U27':0,'V27':0,'W27':0,'X27':0,'Y27':0,'Z27':1}
            values=[('Assumptions',c,v) for c,v in records.items()]
            values += [('DATA COGS','D27','Manuel'),('DATA COGS','L27',40),('DATA COGS','J27',0),('DATA COGS','K27',0),
                       ('ATELIER_CIR_IS','D155','Biens'),('ATELIER_CIR_IS','E155',.2)]
        updates=[]
        for sheet,cell,value in values:
            owner=by_source[(sheet,cell)]
            location=map_location(adapted.profile,sheet,owner['logical_cell'])
            updates.append({k:v for k,v in {**location,'value':value,'reason':'Convention fictive de recette native',
                            'evidence':'fixture','replace_existing':True,'override_default':True}.items() if k!='sheet_id'})
        plan=adapted.prepare(variant_path,updates)
        adapted.apply(variant_path,plan,folder/'inputs.xlsm')
        print('Recalcul natif et oracles indépendants',flush=True)
        native=recalculate(folder/'inputs.xlsm',folder/'calculated.xlsm',folder/'calculation.json',timeout=900)
        wb=Workbook(folder/'calculated.xlsm')
        try:
            # Existing employee_end contract: an exit on month-end excludes
            # that month. Jan-Nov = 60,000 * 1.4 * 11 / 12 = 77,000, no prorata.
            oracles=[('Effectifs','E162',77000)] if kind=='register' else [('Revenue','E282',132000),('COGS','E253',52800)]
            results=[]
            for sheet,cell,expected in oracles:
                target=map_location(adapted.profile,sheet,cell);value=wb.value(target['sheet'],target['cell'])
                results.append({'sheet':target['sheet'],'cell':target['cell'],'expected':expected,'actual':value,
                                'passed':isinstance(value,(int,float)) and abs(value-expected)<.01})
            report['oracles']=results
            if kind=='offer':
                checks=[]
                for row_number in (184,185,186):
                    target=map_location(adapted.profile,'ATELIER_CIR_IS','AA'+str(row_number))
                    value=wb.value(target['sheet'],target['cell'])
                    checks.append({'cell':target,'value':value,'passed':isinstance(value,(int,float)) and abs(value)<.01})
                report['tax_reconciliations']=checks
            report['source_preserved']=digest(source)==before
            report['vba_preserved']=variant['validation']['vba']['preserved']
            report['native']=native
            report['status']='SUCCES' if report['source_preserved'] and all(o['passed'] for o in results+report.get('tax_reconciliations',[])) else 'ECHEC_ORACLE'
        finally:wb.close()
    except BaseException as error:
        report.update(status='ECHEC',error=repr(error));raise
    finally:
        atomic_json(folder/'validation.json',report)
        print(json.dumps({'status':report['status'],'folder':str(folder),'oracles':report.get('oracles')}),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared_folder',type=Path);parser.add_argument('--kind',choices=('register','offer'),required=True)
    parser.add_argument('--resume-variant',type=Path)
    args=parser.parse_args()
    raise SystemExit(0 if run(args.prepared_folder,args.kind,args.resume_variant)['status']=='SUCCES' else 2)
