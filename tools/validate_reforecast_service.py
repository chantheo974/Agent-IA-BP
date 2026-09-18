"""Explicit, bounded integration recipe on the designated fictitious TCA case.

Default is read-only preflight. --run requires the reviewed current revision
and SHA; it preserves all old versions and creates a distinct receipt. No LLM
or macros are invoked. This is a mathematical fixture, not a tax opinion.
"""
from __future__ import annotations
import argparse,datetime as dt,json,sqlite3,sys,uuid,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
FOLDER=ROOT/'runtime/recette_qualifications_service_20260913_013101_ae260a'
CASE='test_qualifications_wacc'


def preflight():
    with sqlite3.connect((FOLDER/'tca_bp.sqlite3').resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        row=db.execute('SELECT * FROM cases WHERE id=?',(CASE,)).fetchone()
        if row is None:raise ValueError('Designated fictitious case absent')
        objects={}
        for kind in ('actuals','budget'):
            item=db.execute('SELECT id,payload FROM decision_objects WHERE case_id=? AND kind=? AND status=? ORDER BY rowid DESC LIMIT 1',(CASE,kind,'CONFIRME')).fetchone()
            if item is None:raise ValueError('Adopted '+kind+' fixture absent')
            objects[kind]={'id':item['id'],**json.loads(item['payload'])}
    actuals=objects['actuals'];lookup={(r['period'],r['metric']):r['value'] for r in actuals['rows']}
    if actuals.get('cutoff')!='2026-01-31':raise ValueError('Fixture cutoff changed')
    for metric,expected in {'revenue':10000,'net_income':6000,'receipts':10000,'payments':4000,'cash':106000,'assets':106000,'liabilities':0,'equity':106000,'receivables':0,'inventory':0,'payables':0,'debt':0}.items():
        if float(lookup.get(('2026-01',metric),'nan'))!=expected:raise ValueError('Fictitious actual changed: '+metric)
    return {'case_id':CASE,'revision':row['revision'],'sha256':row['sha256'],'calculation_status':row['calculation_status'],
            'model_ref':row['model_ref'],'actuals_id':actuals['id'],'budget_id':objects['budget']['id'],
            'budget_sha256':objects['budget']['source_sha256'],'mutated':False}


def restore_from_receipt(receipt_path):
    """Restore the pre-bridge revision only after its separate successful receipt."""
    import hashlib
    from fastapi.testclient import TestClient
    from tca_bp.storage import atomic_json,digest,canonical
    from tca_bp.service import Application
    from tca_bp.model_engine import ModelEngine
    from tca_bp.web_model import ProfileEngine
    from tca_bp.web_workspace import WebWorkspace
    from tca_bp.web_server import create_app
    from tca_bp.decision_workspace import DecisionWorkspace
    receipt_path=Path(receipt_path).resolve()
    if receipt_path.parent!=FOLDER or not receipt_path.name.startswith('validation_reforecast_service_'):
        raise ValueError('An explicit receipt from the designated fictitious bridge is required')
    bridge=json.loads(receipt_path.read_text(encoding='utf8'))
    if (bridge.get('status')!='SUCCES' or bridge.get('before',{}).get('case_id')!=CASE
            or not bridge.get('checks') or not all(bridge['checks'].values())):
        raise ValueError('The complete successful bridge receipt is required before restoration')
    checked=preflight();after=bridge['after']
    if checked['revision']!=after['revision'] or checked['sha256']!=after['sha256']:
        raise ValueError('The reviewed bridge revision is no longer current')
    prepared=json.loads((FOLDER/'preparation.json').read_text(encoding='utf8'))
    model_dir=Path(prepared['model_dir']);cls=ProfileEngine if (model_dir/'web_profile.json').exists() else ModelEngine
    app=Application(ROOT,FOLDER,engine=cls(ROOT,model_dir=model_dir));work=WebWorkspace(app);d=DecisionWorkspace(app,work)
    output=FOLDER/('validation_reforecast_restore_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]+'.json')
    result={'status':'EN_COURS','bridge_receipt':receipt_path.name,'bridge_receipt_sha256':digest(receipt_path),
            'before':checked,'checks':{},'excel_executed':False,'provider_exercised':False}
    def check(name,value):
        result['checks'][name]=bool(value)
        if not value:raise ValueError('Restoration oracle failed: '+name)
    try:
        versions=work.versions(CASE)['versions']
        target=next(v for v in versions if v['revision']==bridge['before']['revision'])
        check('target_exact_pre_bridge',target['sha256']==bridge['before']['sha256'])
        case_dir=app.store.case_dir(CASE)
        protected={str(p):digest(p) for folder in ('versions','livrables','sources') for p in (case_dir/folder).rglob('*') if p.is_file()}
        protected[str(receipt_path)]=digest(receipt_path)
        actuals_before=canonical(d.latest(CASE,'actuals',{}));budget_before=canonical(d.latest(CASE,'budget',{}))
        arguments={'operation_id':'restore_bridge_'+uuid.uuid4().hex,'expected_revision':checked['revision'],'source_sha256':checked['sha256']}
        restored=work.restore(CASE,target['id'],**arguments);result['restoration']=restored
        current=app.get_case(CASE)
        check('new_revision',current['revision']==checked['revision']+1)
        check('restored_workbook_hash',current['sha256']==target['sha256'])
        check('all_previous_files_preserved',all(Path(path).is_file() and digest(Path(path))==sha for path,sha in protected.items()))
        check('actuals_and_budget_unchanged',canonical(d.latest(CASE,'actuals',{}))==actuals_before and canonical(d.latest(CASE,'budget',{}))==budget_before)
        replay=work.restore(CASE,target['id'],**arguments)
        check('replay_without_new_revision',replay.get('replayed') is True and app.get_case(CASE)['revision']==current['revision'])
        with TestClient(create_app(app,workspace=work,start_jobs=False),base_url='http://127.0.0.1') as client:
            response=client.get('/api/cases/'+CASE+'/download')
            check('http_download_200',response.status_code==200)
            check('http_download_exact_xlsm',hashlib.sha256(response.content).hexdigest()==target['sha256'])
            check('http_download_xlsm_type','macroEnabled.12' in response.headers.get('content-type',''))
        result.update(status='SUCCES',after=current,preserved_file_count=len(protected),
                      scope='Restoration and real local HTTP download on the designated fictitious case; no additional calculation and no claim of renewed financial freshness.')
    except Exception as error:
        result.update(status='ECHEC',error=type(error).__name__+': '+str(error));raise
    finally:
        atomic_json(output,result);work.close();print('Reçu restauration : '+str(output),flush=True)
    return result


def _saved_preview_runner(d, old_receipt, expected_sha, result):
    """Freeze the exact earlier native artifact; common validation runs again."""
    import shutil
    from copy import deepcopy
    from tca_bp.storage import canonical,digest,confined,atomic_json
    from tca_bp.web_structure import _formula_key
    old_path=Path(old_receipt).resolve()
    if old_path.parent!=FOLDER or not old_path.name.startswith('validation_reforecast_service_'):
        raise ValueError('Explicit prior receipt from this fictitious case required')
    old=json.loads(old_path.read_text(encoding='utf8'));preview=old.get('preview',{})
    errors=preview.get('diagnostics',[])
    if (old.get('status')!='ECHEC' or old.get('before',{}).get('sha256')!=expected_sha
            or preview.get('status')!='BLOCKED' or not errors
            or any(e.get('code')!='FORMULA_DIFFERS_FROM_PROPOSAL' for e in errors)):
        raise ValueError('Only the preserved optional-quote diagnostic can be revalidated here')
    with d.store.connection() as db:
        row=db.execute('SELECT * FROM web_drafts WHERE case_id=? AND id=?',(CASE,preview['id'])).fetchone()
        if row is None or row['status']!='BLOCKED' or row['source_sha256']!=expected_sha:
            raise ValueError('Original blocked draft has changed')
        payload=json.loads(row['payload'])
    source=confined(d.store.case_dir(CASE),payload['preview_path'])
    if source.name!='apercu.xlsm' or not source.parent.name.startswith('web_preview_') or digest(source)!=payload['preview_sha256']:
        raise ValueError('Original native preview absent or changed')
    frozen=FOLDER/('revalidation_native_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    shutil.copytree(source.parent,frozen)
    atomic_json(frozen/'blocked_payload.json',payload)
    receipts=list(frozen.rglob('receipt.json'))
    if len(receipts)!=1:raise ValueError('Exactly one native receipt required')
    native_path=receipts[0];request_path=native_path.with_name('request.json')
    serialized_native=json.loads(native_path.read_text(encoding='utf-8-sig'));request=json.loads(request_path.read_text(encoding='utf8'))
    native=payload['validation']['validation']['native']
    artifact=frozen/'apercu.xlsm';expected_output=payload['preview_sha256']
    if (native.get('status')!='MODIFIE_RECALCUL_NON_CERTIFIE' or native.get('source_sha256')!=expected_sha
            or native.get('output_sha256')!=expected_output or request.get('source_sha256')!=expected_sha
            or native.get('macros_enabled') is not False or native.get('events_enabled') is not False
            or native.get('source_preserved') is not True or native.get('save_reopen_verified') is not True
            or native.get('post_serialization_cache_invalidation') is not True
            or native.get('native_serialized_output_sha256')!=serialized_native.get('output_sha256')
            or any(native.get(k)!=serialized_native.get(k) for k in ('status','source_sha256','changes','macros_enabled','events_enabled','save_reopen_verified','source_preserved'))):
        raise ValueError('Preserved native proof incomplete')
    observed=native.get('changes',[]);operations=request['operations']
    if len(observed)!=len(operations):raise ValueError('Native intermediate observations incomplete')
    for error in errors:
        i=error['target']['operation_index']
        if _formula_key(observed[i]['after']['formula'])!=_formula_key(operations[i]['formula']):
            raise ValueError('A refused formula differs beyond optional sheet quotes')
    hashes={str(p):digest(p) for p in (old_path,artifact,native_path,request_path,frozen/'blocked_payload.json')}
    result['native_artifact_revalidation']={'status':'FIGEE_A_REVALIDER','frozen_folder':str(frozen.relative_to(FOLDER)),
        'files_sha256':hashes,'optional_quote_diagnostics_verified':len(errors),'new_excel_write':False,
        'original_native_output_sha256':serialized_native['output_sha256'],'post_cache_invalidation_sha256':expected_output}
    def reuse(source_path,output,normalized,*,timeout):
        if (digest(source_path)!=expected_sha or any(digest(Path(p))!=h for p,h in hashes.items())
                or canonical(normalized)!=canonical(operations) or output.exists()):
            raise ValueError('Source, operations or native proof changed before revalidation')
        shutil.copyfile(artifact,output)
        if digest(output)!=expected_output:raise ValueError('Frozen native artifact copy differs')
        result['native_artifact_revalidation']['status']='COPIE_FIGEE_TRANSMISE_AUX_CONTROLES'
        return {**deepcopy(native),'reused_native_artifact':True,'original_receipt_sha256':hashes[str(native_path)],
                'original_native_output_sha256':serialized_native['output_sha256'],'new_native_execution':False}
    return old['draft'],old['draft']['reforecast']['bridge']['policies']['cash']['evidence_id'],reuse


def run(expected_revision,expected_sha256,resume_receipt=None):
    from tca_bp.storage import atomic_json,digest,canonical
    from tca_bp.service import Application
    from tca_bp.model_engine import ModelEngine
    from tca_bp.web_model import ProfileEngine
    from tca_bp.web_workspace import WebWorkspace
    from tca_bp.decision_workspace import DecisionWorkspace
    from tca_bp.decision_reforecast import prepare_reforecast,read_reforecast
    from tca_bp.decision_reforecast_bridge import ACCOUNTS,SCHEMA
    from tca_bp.decision_model import location
    from tca_bp.decision_exports import report_file,read_identity
    from tca_bp.vendor.input_engine import Workbook
    from tca_bp.web_lock import excel_lock
    checked=preflight()
    if checked['revision']!=expected_revision or checked['sha256']!=expected_sha256:
        raise ValueError('Reviewed fictitious revision/SHA no longer current')
    if checked['calculation_status']!='RECALCULE':raise ValueError('Recalculated revised-price fixture required')
    prepared=json.loads((FOLDER/'preparation.json').read_text(encoding='utf8'))
    if prepared.get('case_id')!=CASE:raise ValueError('Fixture identity changed')
    model_dir=Path(prepared['model_dir']);cls=ProfileEngine if (model_dir/'web_profile.json').exists() else ModelEngine
    app=Application(ROOT,FOLDER,engine=cls(ROOT,model_dir=model_dir))
    work=WebWorkspace(app);app._web_workspace=work;d=DecisionWorkspace(app,work)
    output=FOLDER/('validation_reforecast_service_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]+'.json')
    result={'status':'EN_COURS','before':checked,'checks':{},'provider_exercised':False,'macros_executed':False,'scope':'Explicit fictitious TCA actuals bridge; no real fiscal qualification.'}
    atomic_json(output,result)
    def progress(message):print(message if isinstance(message,str) else message.get('message',str(message)),flush=True)
    def check(key,condition):
        result['checks'][key]=bool(condition)
        if not condition:raise ValueError('Oracle failed: '+key)
    try:
        before=app.get_case(CASE);engine=app.engine_for_case(CASE)
        original=Path(before['workbook_path']);source_hash=digest(original)
        wb=Workbook(original)
        try:
            def value(sheet,cell):return wb.value(*location(engine,sheet,cell))
            observed={'jan_cash':value('Modèle financier','T321'),'feb_cash':value('Modèle financier','U321'),
                      'jan_revenue':value('Modèle financier','T88'),'year_income':value('Compte de Résultat','D85')}
            check('revised_price_source_is_expected',observed=={'jan_cash':107000,'feb_cash':114000,'jan_revenue':11000,'year_income':84000})
            years=int(value('Control','C59'));first=int(str(d.profile(CASE).get('start_year',2026)))
            if years!=3 or first!=2026:raise ValueError('Expected three-year fictitious horizon changed')
            annual_before=[]
            for i in range(years):
                col=chr(ord('D')+i);assets=value('Bilan',col+'4');total=value('Bilan',col+'24');equity=value('Bilan',col+'25');income=value('Compte de Résultat',col+'85')
                if any(type(v) not in (int,float) for v in (assets,total,equity,income)):raise ValueError('Original annual balance unavailable')
                annual_before.append({'period':str(2026+i),'assets':assets,'liabilities':total-equity,'equity':equity,'net_income':income})
            check('no_external_link_before',not any(name.startswith('xl/externalLinks/') for name in wb.z.namelist()))
        finally:wb.close()
        result['source_observations']=observed;result['annual_before']=annual_before
        old_budget=d.latest(CASE,'budget',{});old_actuals=d.latest(CASE,'actuals',{})
        budget_identity=canonical(old_budget);actuals_identity=canonical(old_actuals)
        if resume_receipt:
            draft,sid,reuse=_saved_preview_runner(d,resume_receipt,source_hash,result)
            d.source(CASE,sid)
            from tca_bp.decision_reforecast_bridge import _sha
            check('resumed_actuals_and_budget_exact',draft['reforecast']['actuals_sha256']==_sha(old_actuals['rows'])
                  and draft['reforecast']['budget_sha256']==old_budget['source_sha256']
                  and draft['reforecast']['actuals_id']==old_actuals['id'])
        else:
            source=app.add_source(CASE,text=canonical({'fixture':'FICTIVE uniquement — raccord après prix unitaire 110 EUR','original_model_sha256':source_hash,
            'checkpoint_2026_01':{'assets':107000,'liabilities':0,'equity':107000,'net_income_ytd':7000},
            'policy':'Les huit écarts restent explicitement conservés jusqu’à la fin du modèle. Aucun nouvel événement ; aucune reprise des flux déjà calculés. Convention fiscale fictive inchangée, pas de droit réel revendiqué.'}),title='Recette fictive — checkpoint et conservation des écarts du réalisé')
            sid=source['id']
            bridge={'schema':SCHEMA,'basis':'NET_ADJUSTMENTS_TO_CURRENT_MODEL','workbook_sha256':source_hash,
                'baseline_cutoff':{key:{'value':v,'evidence_id':sid} for key,v in [('assets',107000),('liabilities',0),('equity',107000),('net_income_ytd',7000)]},
                'policies':{key:{'treatment':'carry','terminal':'carry_remaining','evidence_id':sid,
                    'reason':'Conservation explicite de cet écart net pour le témoin fictif, sans nouvel encaissement/règlement ni effet fiscal automatique.'} for key in ACCOUNTS},'events':[]}
            progress('Préparation sourcée des trois feuilles gérées sur le vrai modèle TCA fictif.')
            draft=prepare_reforecast(d,CASE,{'expected_revision':before['revision'],'actuals_id':old_actuals['id'],'bridge':bridge})
        result['draft']=draft;check('no_open_bridge_question',draft['reforecast']['questions']==[])
        check('unchanged_before_preview',app.get_case(CASE)['sha256']==source_hash)
        if resume_receipt:work.variant_runner=reuse
        try:preview=work.preview(CASE,draft['id'],progress)
        finally:work.variant_runner=None
        result['preview']=preview
        check('reviewable_preview_token',bool(preview.get('approval_token')) and not preview.get('blocked',False))
        if resume_receipt:result['native_artifact_revalidation']['status']='VALIDEE_PAR_CONTROLES_COMMUNS'
        adopted=work.apply(CASE,draft['id'],preview['approval_token']);result['adoption']=adopted
        fiscal={'module':'REGLES_FISCALES','state':'ACTIF','status':'CONFIRME','evidence':sid,
                'reason':'Revue explicite fictive de la nouvelle variante : seuls les trois onglets du raccord ont été ajoutés ; conventions fiscales mathématiques de la recette conservées, aucune qualification légale réelle.',
                'jurisdiction':'Convention mathématique fictive — aucun droit fiscal réel revendiqué','valid_from':'2026-01-01','valid_to':'2028-12-31'}
        result['fiscal_declaration']=app.declare_qualification(CASE,fiscal)
        qualification=app.qualifications(CASE);result['qualification_before_native']={k:v for k,v in qualification['scopes'].items() if k!='DCF'}
        check('documentary_scopes_ready',all(qualification['scopes'][s]['scenario_ready'] for s in ('CA','COGS','CASH','FISCALITE')))
        progress('Recalcul natif de la version adoptée, macros désactivées.')
        with excel_lock():result['native_recalculation']=app.recalculate(CASE)
        view=read_reforecast(d,CASE);result['reader']=view
        check('managed_reader_explicable',view['forecast_status']=='EXPLICABLE')
        series={s['id']:s for s in view['forecast_series']}
        def number(metric,period):return series[metric]['values'][series[metric]['categories'].index(period)]
        check('actual_january_cash_106000',number('cash','2026-01')==106000)
        check('future_february_cash_113000',number('cash','2026-02')==113000)
        check('actual_january_revenue_10000',number('revenue','2026-01')==10000)
        check('future_february_revenue_11000',number('revenue','2026-02')==11000)
        check('actualized_revenue_2026_131000',sum(v for p,v in zip(series['revenue']['categories'],series['revenue']['values']) if p.startswith('2026-'))==131000)
        for actual,base in zip(view['annual_balance'],annual_before):
            year=actual['period'];expected_income=base['net_income']-1000 if year=='2026' else base['net_income']
            check('annual_'+year,actual['assets']==base['assets']-1000 and actual['liabilities']==base['liabilities'] and actual['equity']==base['equity']-1000 and actual['net_income']==expected_income and actual['balance_check']==0 and actual['model_balance_check']==0)
        check('actualized_net_income_2026_83000',view['annual_balance'][0]['net_income']==83000)
        check('budget_object_unchanged',canonical(d.latest(CASE,'budget',{}))==budget_identity)
        check('actuals_object_unchanged',canonical(d.latest(CASE,'actuals',{}))==actuals_identity)
        check('original_workbook_unchanged',digest(original)==source_hash)
        current=app.get_case(CASE)
        with zipfile.ZipFile(current['workbook_path']) as archive:
            check('no_external_link_after',not any(name.startswith('xl/externalLinks/') for name in archive.namelist()))
        report=d.build_report(CASE,{'expected_revision':current['revision']},progress);result['report']=report
        check('four_formats',set(report['files'])=={'xlsm','pdf','docx','pptx'})
        snapshot_path=d.store.case_dir(CASE)/report['snapshot'];snapshot=json.loads(snapshot_path.read_text(encoding='utf8'))
        check('snapshot_contains_explicable_bridge',snapshot['actuals']['forecast_status']=='EXPLICABLE' and snapshot['actuals']['annual_balance'][0]['net_income']==83000)
        check('all_four_artifacts_readable',all(report_file(d,CASE,report['id'],kind).stat().st_size>0 for kind in ('xlsm','pdf','docx','pptx')))
        with zipfile.ZipFile(report_file(d,CASE,report['id'],'xlsm')) as archive:check('export_identity_bound',read_identity(archive)==report['identity'])
        result.update(status='SUCCES',after=app.get_case(CASE))
    except Exception as error:
        result.update(status='ECHEC',error=type(error).__name__+': '+str(error));raise
    finally:
        atomic_json(output,result);work.close();print('Reçu : '+str(output),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--run',action='store_true');modes.add_argument('--restore-from-receipt',type=Path)
    modes.add_argument('--resume-from-receipt',type=Path)
    parser.add_argument('--expected-revision',type=int);parser.add_argument('--expected-sha256')
    args=parser.parse_args()
    if args.restore_from_receipt:
        print(json.dumps({'status':restore_from_receipt(args.restore_from_receipt)['status']},ensure_ascii=False))
    elif args.run or args.resume_from_receipt:
        if args.expected_revision is None or not args.expected_sha256:parser.error('Explicit reviewed revision and SHA required for --run')
        print(json.dumps({'status':run(args.expected_revision,args.expected_sha256,args.resume_from_receipt)['status']},ensure_ascii=False))
    else:print(json.dumps(preflight(),ensure_ascii=False))
