"""Recette fictive des scénarios, objectif et sensibilité via le service réel."""
from pathlib import Path
import argparse, json, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tca_bp.storage import atomic_json,digest
from tca_bp.service import Application
from tca_bp.model_engine import ModelEngine
from tca_bp.web_workspace import WebWorkspace
from tca_bp.decision_workspace import DecisionWorkspace
from tca_bp.decision_model import create_scenario,run_goal,run_sensitivity


def run(folder):
    folder=Path(folder).resolve()
    if folder.parent!=ROOT/'runtime' or not folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('Utiliser uniquement la recette fictive qualifiée.')
    receipt=folder/'validation_decision_campaigns_native.json'
    if receipt.exists():raise ValueError('Conserver le reçu précédent.')
    p=json.loads((folder/'preparation.json').read_text(encoding='utf8'))
    app=Application(ROOT,folder,engine=ModelEngine(ROOT,Path(p['model_dir'])))
    work=WebWorkspace(app);app._web_workspace=work;d=DecisionWorkspace(app,work)
    result={'status':'EN_COURS','checks':{},'provider_exercised':False}
    def progress(item):print(item.get('message','Calcul en cours'),flush=True)
    atomic_json(receipt,result)
    try:
        parent=app.get_case(p['case_id'])
        base=create_scenario(d,p['case_id'],{'name':'Référence fictive — recette des décisions','purpose':'native_recipe','expected_revision':parent['revision']})
        case=base['case_id'];result['base']=base
        print('Recalcul de la référence isolée de recette.',flush=True)
        app.recalculate(case)
        before=app.get_case(case)
        result['base_sha256']=before['sha256']
        price=next(b for b in d.bindings(case) if b['sheet']=='Assumptions' and b['cell']=='F15')
        volume=next(b for b in d.bindings(case) if b['sheet']=='Assumptions' and b['cell']=='K15')
        goal={'field_id':price['field_id'],'sheet':price['sheet'],'cell':price['cell'],'metric':'revenue',
            'target':132000,'lower':100,'upper':120,'max_evaluations':3,'tolerance':0.01,'expected_revision':before['revision']}
        result['goal']=run_goal(d,case,goal,progress)
        result['checks']['goal_converged']=result['goal']['result']['status']=='CONVERGED'
        result['checks']['goal_price_110']=float(result['goal']['result']['candidate']['lever'])==110
        result['checks']['goal_not_applied']=app.get_case(case)['sha256']==before['sha256']
        body={'metric':'revenue','axes':[{k:price[k] for k in ('field_id','sheet','cell')}|{'values':[100,110]},
             {k:volume[k] for k in ('field_id','sheet','cell')}|{'values':[1200,1320]}]}
        interrupted=[False]
        def cancel_after_first(item):
            progress(item)
            if item.get('campaign_id') and not interrupted[0]:
                current=d.get(case,item['campaign_id'],'sensitivity')
                d.save(case,'sensitivity',{**current,'cancel_requested':True},status='RUNNING',object_id=current['id'])
                interrupted[0]=True
        first=run_sensitivity(d,case,body,cancel_after_first)
        result['interrupted']=first
        result['checks']['one_completed_point_retained']=first['status']=='INTERRUPTED' and len(first['points'])==1
        d.save(case,'sensitivity',{**first,'cancel_requested':False},status='RUNNING',object_id=first['id'])
        final=run_sensitivity(d,case,{**body,'campaign_id':first['id']},progress)
        result['sensitivity']=final
        result['checks']['resume_completed_four_unique_points']=final['status']=='COMPLETE' and len(final['points'])==4 and len({p['case_id'] for p in final['points']})==4 and final['points'][0]['case_id']==first['points'][0]['case_id']
        result['oracles']=[]
        for point in final['points']:
            unit_price,quantity=point['values'];expected={'revenue':unit_price*quantity,'net_income':(unit_price-40)*quantity,'cash_min':100000+(unit_price-40)*quantity/12}
            metrics={m['id']:m['value'] for m in point['metrics']}
            for metric,value in expected.items():
                actual=metrics[metric]
                result['oracles'].append({'point':point['values'],'metric':metric,'expected':value,'actual':actual,'pass':actual is not None and abs(actual-value)<=0.01})
        result['checks']['independent_financial_oracles']=all(o['pass'] for o in result['oracles'])
        result['checks']['reference_preserved']=app.get_case(case)['sha256']==before['sha256'] and digest(Path(before['workbook_path']))==before['sha256']
        result['status']='SUCCES' if all(result['checks'].values()) else 'ECHEC_ORACLES'
    except Exception as error:
        result.update(status='ECHEC_EXECUTION',error=type(error).__name__+': '+str(error));raise
    finally:
        atomic_json(receipt,result);work.close()
    print(json.dumps({'status':result['status'],'checks':result['checks']},ensure_ascii=False),flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path)
    raise SystemExit(0 if run(parser.parse_args().folder)['status']=='SUCCES' else 2)
