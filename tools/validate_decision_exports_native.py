"""Recette locale des quatre livrables et du retour Excel sur dossier fictif."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tca_bp.storage import atomic_json,digest
from tca_bp.service import Application
from tca_bp.model_engine import ModelEngine
from tca_bp.web_workspace import WebWorkspace
from tca_bp.decision_workspace import DecisionWorkspace
from tca_bp.decision_exports import report_file,roundtrip,read_identity
from tca_bp.web_structure import _run_native
from tca_bp.web_lock import excel_lock


def run(folder):
    folder=Path(folder).resolve()
    if folder.parent!=ROOT/'runtime' or not folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('Dossier fictif préparé sous runtime requis.')
    receipt=folder/'validation_exports_native.json'
    if receipt.exists(): raise ValueError('Conserver la recette précédente ; utiliser un nouveau dossier fictif.')
    prepared=json.loads((folder/'preparation.json').read_text(encoding='utf8'))
    app=Application(ROOT,folder,engine=ModelEngine(ROOT,Path(prepared['model_dir'])))
    work=WebWorkspace(app);app._web_workspace=work
    d=DecisionWorkspace(app,work);case_id=prepared['case_id']
    result={'status':'EN_COURS','case_id':case_id,'checks':{},'provider_exercised':False}
    atomic_json(receipt,result)
    try:
        before=app.get_case(case_id)
        if before['sha256']!=prepared['source_sha256']: raise ValueError('La préparation a changé.')
        print('Recalcul Excel de la recette fictive.',flush=True)
        result['recalculation']=app.recalculate(case_id)
        case=app.get_case(case_id)
        d.set_profile(case_id,{'profile':{'company_name':'Entreprise fictive de recette','activity':'Services','start_year':2026,'years':3,'activity_start_month':1}})
        capital=d.capitalization(case_id,{'shareholders':[{'name':'Fondatrice fictive','shares':1000}],
            'rounds':[{'name':'Amorçage','pre_money':4000000,'investment':1000000,'pool_percent':10,'pool_timing':'before'},
                      {'name':'Développement','pre_money':8000000,'investment':2000000,'pool_percent':10,'pool_timing':'before'}]})
        d.adopt_object(case_id,'capitalization',{'approval_token':capital['approval_token']})
        report=d.build_report(case_id,{'expected_revision':case['revision']},lambda p:print(p.get('message'),flush=True))
        result['report']=report
        result['metrics']=d.metrics(case_id)
        result['checks']['four_formats']=set(report['files'])=={'xlsm','pdf','docx','pptx'}
        result['checks']['qualified_revenue']=next(m for m in result['metrics'] if m['id']=='revenue')['value']==120000
        exported=report_file(d,case_id,report['id'],'xlsm')
        result['checks']['identical_roundtrip']=roundtrip(d,case_id,exported,case['revision'])['status']=='IDENTIQUE'
        edited=folder/'export_modifie_dans_Excel.xlsm'
        print('Modification et sauvegarde du livrable dans Excel natif, macros désactivées.',flush=True)
        with excel_lock():
            result['native_edit']=_run_native(exported,edited,[{'type':'set_value','sheet':'Assumptions','cell':'F15','value':110}])
        with zipfile.ZipFile(edited) as z:
            result['checks']['identity_survives_excel_save']=read_identity(z)==report['identity']
        draft=roundtrip(d,case_id,edited,case['revision'])
        result['roundtrip']=draft
        result['checks']['one_recognized_change']=len(draft['operations'])==1 and draft['operations'][0]['cell']=='F15' and draft['operations'][0]['value']==110
        result['checks']['no_write_before_preview']=app.get_case(case_id)['sha256']==case['sha256']
        preview=work.preview(case_id,draft['id'],lambda p:print(p.get('message'),flush=True))
        result['preview']=preview
        work.apply(case_id,draft['id'],preview['approval_token'])
        result['recalculation_after_roundtrip']=app.recalculate(case_id)
        final=d.metrics(case_id)
        result['checks']['updated_revenue']=next(m for m in final if m['id']=='revenue')['value']==132000
        result['checks']['original_preserved']=digest(Path(before['workbook_path']))==before['sha256']
        result['status']='SUCCES' if all(result['checks'].values()) else 'ECHEC_ORACLES'
    except Exception as error:
        result.update(status='ECHEC_EXECUTION',error=type(error).__name__+': '+str(error))
        raise
    finally:
        atomic_json(receipt,result)
        work.close()
    print(json.dumps({'status':result['status'],'checks':result['checks']},ensure_ascii=False),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path)
    raise SystemExit(0 if run(parser.parse_args().folder)['status']=='SUCCES' else 2)
