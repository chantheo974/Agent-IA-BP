"""HTTP resources for the guided local prototype."""
from pathlib import Path
import json
import tempfile
from fastapi import Body, File, Form, UploadFile
from fastapi.responses import FileResponse
from .storage import confined,digest

def install_routes(api,app,work):
    from .decision_workspace import DecisionWorkspace
    from .decision_model import scenario_list
    from .decision_actuals import preview_actuals,apply_actuals,actuals_view,read_import,KNOWN
    from .decision_exports import report_file,roundtrip
    d=DecisionWorkspace(app,work)
    api.state.decision=d
    app._decision_workspace=d
    prefix='/api/cases/{case_id}'

    @api.get(prefix+'/workshop')
    def workshop(case_id:str): return d.workshop(case_id)
    @api.get(prefix+'/draft/preview-details')
    def preview_details(case_id:str):
        app._row(case_id)
        row=work._draft_row(case_id)
        if not row or row['status'] not in ('READY','BLOCKED'): raise ValueError('Aperçu détaillé indisponible.')
        payload=json.loads(row['payload'])
        details=payload.get('validation',{}).get('preview_details')
        if not details or details.get('filename')!='apercu.variant.json': raise ValueError('Cet aperçu ne possède pas de manifeste supplémentaire.')
        path=confined(d.store.case_dir(case_id),payload['preview_path']).with_suffix('.variant.json')
        if not path.is_file() or path.stat().st_size!=details['size'] or digest(path)!=details['sha256']:
            raise ValueError('Le manifeste a changé. Préparer un nouvel aperçu avant application.')
        return FileResponse(path,filename='TCA_changements_structure.json',media_type='application/json')
    @api.post(prefix+'/model/wacc-fingerprint')
    def wacc_migration(case_id:str,body:dict=Body(default_factory=dict)):
        return d.request(case_id,'model/wacc-fingerprint',body,lambda:d.propose_wacc_migration(case_id,body))
    @api.post(prefix+'/model/dcf-calendar')
    def dcf_calendar_migration(case_id:str,body:dict=Body(default_factory=dict)):
        return d.request(case_id,'model/dcf-calendar',body,lambda:d.propose_dcf_calendar_migration(case_id,body))
    @api.post(prefix+'/model/fiscal-calendar')
    def fiscal_calendar_migration(case_id:str,body:dict=Body(default_factory=dict)):
        return d.request(case_id,'model/fiscal-calendar',body,lambda:d.propose_fiscal_calendar_migration(case_id,body))
    @api.get(prefix+'/accounting/catalog')
    def accounting_catalog(case_id:str):
        app._row(case_id)
        from .decision_accounting import catalog
        return catalog()
    @api.get(prefix+'/accounting/mapping')
    def accounting_mapping(case_id:str,account:str,balance:str,year:int):
        app._row(case_id)
        from .decision_accounting import suggest
        return suggest(account,balance,year)
    @api.get(prefix+'/profile')
    def profile(case_id:str): return {'profile':d.profile(case_id)}
    @api.put(prefix+'/profile')
    def set_profile(case_id:str,body:dict=Body(...)): return d.request(case_id,'profile',body,lambda:d.set_profile(case_id,body))
    @api.post(prefix+'/profile/propose')
    def propose_profile(case_id:str,body:dict=Body(default_factory=dict)): return d.request(case_id,'profile/propose',body,lambda:d.propose_profile(case_id,body))
    @api.get(prefix+'/questionnaire')
    def questionnaire(case_id:str): return d.questionnaire(case_id)
    @api.get(prefix+'/qualifications')
    def qualifications(case_id:str): return d.qualification_view(case_id)
    @api.post(prefix+'/qualifications/preview')
    def qualification_preview(case_id:str,body:dict=Body(...)):
        return d.request(case_id,'qualification/preview',body,lambda:d.qualification_preview(case_id,body))
    @api.post(prefix+'/qualifications/apply')
    def qualification_apply(case_id:str,body:dict=Body(...)):
        return d.request(case_id,'qualification/apply',body,lambda:d.qualification_apply(case_id,body))
    @api.post(prefix+'/answers')
    def answers(case_id:str,body:dict=Body(...)): return d.request(case_id,'answers',body,lambda:d.answers(case_id,body))
    @api.get(prefix+'/intents/{request_id}')
    def intent(case_id:str,request_id:str): return d.intent(case_id,request_id)
    @api.post(prefix+'/intents/{request_id}/review')
    def review_intent(case_id:str,request_id:str,body:dict=Body(...)): return d.review_intent(case_id,request_id,body)
    @api.get(prefix+'/intents/{request_id}/review')
    def intent_review(case_id:str,request_id:str): return d.intent_review(case_id,request_id)
    @api.get(prefix+'/sources/{source_id}/file')
    def source_file(case_id:str,source_id:str):
        source=d.source(case_id,source_id)
        if not source['path']: raise ValueError('Cette source est une réponse textuelle.')
        path=confined(d.store.case_dir(case_id),source['path'])
        return FileResponse(path,filename=Path(source['path']).name)
    @api.get(prefix+'/extractions')
    def extractions(case_id:str): return {'extractions':d.objects(case_id,'extraction')}
    @api.post(prefix+'/extractions')
    def extract(case_id:str,body:dict=Body(...)):
        d.source(case_id,body['source_id'])
        return d.submit(case_id,'extract',body)
    @api.get(prefix+'/extractions/{extraction_id}')
    def extraction(case_id:str,extraction_id:str): return d.get(case_id,extraction_id,'extraction')
    @api.post(prefix+'/extractions/{extraction_id}/propose')
    def extracted_propose(case_id:str,extraction_id:str,body:dict=Body(...)):
        return d.request(case_id,'extraction/'+extraction_id,body,lambda:d.extraction_propose(case_id,extraction_id,body))
    @api.get(prefix+'/scenarios')
    def scenarios(case_id:str): return {'scenarios':scenario_list(d,case_id)}
    @api.post(prefix+'/scenarios')
    def scenario(case_id:str,body:dict=Body(...)): return d.request(case_id,'scenario',body,lambda:d.create_scenario(case_id,body))
    @api.get(prefix+'/scenarios/compare')
    def compare(case_id:str):
        from .decision_model import read_annual_metrics,read_series
        cases=[{'id':case_id,'case_id':case_id,'name':'Référence'},*scenario_list(d,case_id)]
        result=[{**s,'metrics':d.metrics(s['case_id']),'annual_metrics':read_annual_metrics(d,s['case_id']),'series':read_series(d,s['case_id'])} for s in cases]
        calendars=[s['series'][0]['categories'] for s in result]
        return {'scenarios':result,'calendars_identical':all(c==calendars[0] for c in calendars),'notice':'Comparer les périodes communes ; les horizons propres restent explicitement visibles.'}
    @api.get(prefix+'/capitalization')
    def capital(case_id:str): return d.latest(case_id,'capitalization',{'shareholders':[],'rounds':[]})
    @api.post(prefix+'/capitalization')
    def cap_preview(case_id:str,body:dict=Body(...)): return d.request(case_id,'capitalization',body,lambda:d.capitalization(case_id,body))
    @api.post(prefix+'/capitalization/apply')
    def cap_apply(case_id:str,body:dict=Body(...)): return d.request(case_id,'capitalization/apply',body,lambda:d.adopt_object(case_id,'capitalization',body))
    @api.get(prefix+'/actuals')
    def actuals(case_id:str): return actuals_view(d,case_id)
    @api.get(prefix+'/actuals/bridge/questions')
    def bridge_questions(case_id:str):
        from .decision_reforecast import reforecast_requirements
        return reforecast_requirements(d,case_id)
    @api.post(prefix+'/actuals')
    def actuals_preview(case_id:str,body:dict=Body(...)): return d.request(case_id,'actuals',body,lambda:preview_actuals(d,case_id,body))
    @api.post(prefix+'/actuals/apply')
    def actuals_apply(case_id:str,body:dict=Body(...)): return d.request(case_id,'actuals/apply',body,lambda:apply_actuals(d,case_id,body))
    @api.post(prefix+'/actuals/reforecast')
    def actuals_reforecast(case_id:str,body:dict=Body(default_factory=dict)):
        from .decision_reforecast import prepare_reforecast
        return d.request(case_id,'actuals/reforecast',body,lambda:prepare_reforecast(d,case_id,body))

    def upload_path(file):
        root=app.data_dir/'imports'; root.mkdir(exist_ok=True)
        import os
        fd,name=tempfile.mkstemp(dir=root,suffix=Path(file.filename or '').suffix.lower())
        path=Path(name)
        try:
            with os.fdopen(fd,'wb') as stream:
                size=0
                while chunk:=file.file.read(1024*1024):
                    size+=len(chunk)
                    if size>50*1024*1024: raise ValueError('Import limité à 50 Mio.')
                    stream.write(chunk)
            return path
        except Exception:
            path.unlink(missing_ok=True)
            raise
    @api.post(prefix+'/actuals/import')
    def actuals_import(case_id:str,file:UploadFile=File(...),mapping:str=Form('{}'),metric_mapping:str=Form('{}'),numeric_locale:str=Form('fr'),encoding:str=Form('utf-8'),cutoff:str=Form(''),expected_revision:int|None=Form(None),request_id:str|None=Form(None)):
        d.check_revision(case_id,expected_revision)
        path=upload_path(file)
        try:
            columns,rows=read_import(path,json.loads(mapping),numeric_locale,encoding)
            if not rows: return {'columns':columns,'rows':[],'encoding':encoding}
            metric_values=sorted(set(str(row.get('metric','')).strip() for row in rows))
            mapped=json.loads(metric_mapping)
            if not isinstance(mapped,dict) or any(value not in KNOWN for value in mapped.values()): raise ValueError('Correspondance des postes invalide.')
            if any(value not in KNOWN and value not in mapped for value in metric_values):
                return {'columns':columns,'metric_values':metric_values,'metrics_catalog':actuals_view(d,case_id)['metrics_catalog'],'needs_metric_mapping':True,'encoding':encoding}
            for row in rows:
                original=str(row.get('metric','')).strip()
                row['metric']=mapped.get(original,original)
                row['source_metric']=original
                if not json.loads(mapping).get('kind'): row['kind']=KNOWN[row['metric']]
            def propose():
                source=app.add_source(case_id,path=path,title=file.filename or 'Réalisé importé')
                preview=preview_actuals(d,case_id,{'rows':rows,'cutoff':cutoff,'numeric_locale':numeric_locale,'expected_revision':expected_revision,'source_id':source['id']})
                with d.store.connection() as db:
                    d.store.history(db,case_id,'LECTURE_IMPORT_REALISE',{'source_id':source['id'],'source_sha256':digest(path),'format':path.suffix.lower(),'encoding':encoding if path.suffix.lower()=='.csv' else None,'numeric_locale':numeric_locale,'mapping':json.loads(mapping),'metric_mapping':mapped,'preview_id':preview['id']})
                return {'columns':columns,'rows':rows,'preview':preview,'encoding':encoding}
            return d.request(case_id,'actuals/import',{'request_id':request_id,'sha256':digest(path),'mapping':json.loads(mapping),'metric_mapping':mapped,'numeric_locale':numeric_locale,'encoding':encoding,'cutoff':cutoff,'expected_revision':expected_revision},propose)
        finally: path.unlink(missing_ok=True)
    @api.post(prefix+'/goals')
    def goals(case_id:str,body:dict=Body(...)): return d.submit(case_id,'goal',body)
    @api.get(prefix+'/goals')
    def goal_results(case_id:str): return {'goals':d.objects(case_id,'goal')}
    @api.get(prefix+'/sensitivities')
    def sensitivities(case_id:str): return {'campaigns':d.objects(case_id,'sensitivity')}
    @api.post(prefix+'/sensitivities')
    def sensitivity(case_id:str,body:dict=Body(...)): return d.submit(case_id,'sensitivity',body)
    @api.post(prefix+'/jobs/{job_id}/cancel')
    def cancel(case_id:str,job_id:str):
        with d.store.connection() as db:
            row=db.execute('SELECT * FROM web_jobs WHERE id=? AND case_id=?',(job_id,case_id)).fetchone()
            if not row or row['kind']!='decision_sensitivity': raise ValueError('Interruption contrôlée disponible pour les campagnes de sensibilité.')
            if row['status']=='QUEUED':
                db.execute("UPDATE web_jobs SET status='INTERRUPTED',error='Campagne annulée avant démarrage.' WHERE id=?",(job_id,))
            elif row['status']=='RUNNING':
                payload=json.loads(row['payload'])
                if payload.get('campaign_id'):
                    campaign=d.get(case_id,payload['campaign_id'],'sensitivity')
                    d.save(case_id,'sensitivity',{**campaign,'cancel_requested':True},status='RUNNING',object_id=campaign['id'],db=db)
            d.work.jobs.emit(case_id,db=db)
        return {'status':'INTERRUPTION_DEMANDEE'}
    @api.get(prefix+'/reports')
    def reports(case_id:str): return {'reports':d.objects(case_id,'report')}
    @api.post(prefix+'/reports')
    def report(case_id:str,body:dict=Body(default_factory=dict)): return d.submit(case_id,'report',body)
    @api.get(prefix+'/reports/{report_id}/{format}')
    def report_download(case_id:str,report_id:str,format:str):
        path=report_file(d,case_id,report_id,format)
        return FileResponse(path,filename=path.name)
    @api.post(prefix+'/roundtrip')
    def import_export(case_id:str,file:UploadFile=File(...),expected_revision:int|None=Form(None),request_id:str|None=Form(None)):
        path=upload_path(file)
        try: return d.request(case_id,'roundtrip',{'request_id':request_id,'sha256':digest(path),'expected_revision':expected_revision},lambda:roundtrip(d,case_id,path,expected_revision))
        finally: path.unlink(missing_ok=True)
    @api.post(prefix+'/offers')
    def offer(case_id:str,body:dict=Body(...)):
        from .decision_offers import prepare_offer
        return d.request(case_id,'offer',body,lambda:prepare_offer(d,case_id,body))
    @api.get(prefix+'/registers')
    def registers(case_id:str): return d.registers(case_id)
    @api.post(prefix+'/registers/{sheet}/records')
    def record(case_id:str,sheet:str,body:dict=Body(...)): return d.request(case_id,'record/'+sheet,body,lambda:d.prepare_record(case_id,sheet,body))
    @api.post(prefix+'/registers/{sheet}/extend')
    def extend_register(case_id:str,sheet:str,body:dict=Body(...)):
        from .decision_offers import prepare_register_extension
        return d.request(case_id,'register/extend/'+sheet,body,lambda:prepare_register_extension(d,case_id,sheet,body))
    return d
