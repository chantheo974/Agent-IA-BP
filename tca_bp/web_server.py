"""Loopback-only HTTP application serving the compiled React workspace."""
from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import tempfile
import threading
from urllib.parse import urlsplit
import webbrowser

from fastapi import FastAPI, Request, UploadFile, File, Form, Body, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .service import Application
from .storage import canonical, confined, check_id
from .web_workspace import WebWorkspace
from .web_lock import ServerLease
from .web_settings import ProviderError


def create_app(application=None, *, workspace=None, start_jobs=True, frontend_dir=None, dev=False):
    service=application or Application()
    work=workspace or WebWorkspace(service)
    service._web_workspace=work
    @asynccontextmanager
    async def lifespan(api):
        lease=ServerLease(service.data_dir/'.web-server.lock')
        if start_jobs:
            lease.acquire()
        if start_jobs:
            work.jobs.start()
        yield
        work.close()
        lease.close()
    api=FastAPI(title='TCA BP Web',version=__version__,lifespan=lifespan,docs_url=None,redoc_url=None)
    api.state.workspace=work

    @api.middleware('http')
    async def local_only(request,call_next):
        host=request.headers.get('host','')
        try:
            hostname=urlsplit('//'+host).hostname
        except ValueError:
            hostname=None
        if hostname not in ('127.0.0.1','localhost','::1'):
            return JSONResponse({'detail':'Serveur réservé à cet ordinateur.'},status_code=403)
        origin=request.headers.get('origin')
        if origin:
            parsed=urlsplit(origin)
            dev_allowed=dev and origin in ('http://127.0.0.1:5173','http://localhost:5173')
            if not dev_allowed and (parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost','::1') or parsed.netloc!=host):
                return JSONResponse({'detail':'Origine de la requête refusée.'},status_code=403)
        if request.headers.get('sec-fetch-site')=='cross-site':
            return JSONResponse({'detail':'Origine de la requête refusée.'},status_code=403)
        try:
            length=int(request.headers.get('content-length','0'))
            if length<0: raise ValueError('Longueur négative')
            if length>52*1024*1024:
                return JSONResponse({'detail':'Requête trop volumineuse.'},status_code=413)
        except ValueError:
            return JSONResponse({'detail':'Taille de requête invalide.'},status_code=400)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; object-src 'none'"
        return response

    @api.exception_handler(ValueError)
    async def invalid(request,exc):
        return JSONResponse({'detail':str(exc)},status_code=409)

    @api.exception_handler(ProviderError)
    async def provider_error(request,exc):
        return JSONResponse({'detail':str(exc),'code':exc.code,'retryable':exc.retryable},status_code=502)

    @api.exception_handler(RequestValidationError)
    async def invalid_body(request,exc):
        # Pydantic's default includes the submitted value; settings contain a
        # secret and must never be echoed by validation errors.
        return JSONResponse({'detail':'Paramètres manquants ou invalides.'},status_code=422)

    @api.get('/api/health')
    def health():
        return {'status':'READY','version':__version__,'application':'TCA BP Web'}

    @api.get('/api/settings')
    def settings():
        return work.settings.public()

    @api.put('/api/settings')
    def update_settings(body:dict=Body(...)):
        if set(body)-{'base_url','model','api_key','clear_api_key'}:
            raise ValueError('Réglage inconnu.')
        return work.settings.update(**body)

    @api.post('/api/settings/test')
    def test_settings():
        return work.settings.test_connection()

    @api.get('/api/cases')
    def cases():
        return {'cases':service.list_cases()}

    @api.post('/api/cases')
    def create_case(body:dict=Body(...)):
        return service.create_case(client_name=body.get('client_name',''),name=body.get('name',''))

    @api.get('/api/cases/{case_id}')
    def case(case_id:str):
        return service.get_case(case_id)

    @api.get('/api/cases/{case_id}/sheets')
    def sheets(case_id:str):
        return work.sheets(case_id)

    @api.get('/api/cases/{case_id}/cells')
    def cells(case_id:str,sheet:str,row:int=1,column:int=1,rows:int=100,columns:int=26):
        return work.cells(case_id,sheet,row,column,rows,columns)

    @api.get('/api/cases/{case_id}/agents')
    def agents(case_id:str):
        return {'agents':work.agents(case_id)}

    @api.get('/api/cases/{case_id}/charts')
    def charts(case_id:str):
        return work.charts(case_id)

    @api.get('/api/cases/{case_id}/sources')
    def sources(case_id:str):
        return {'sources':service.get_case(case_id)['sources']}

    @api.get('/api/cases/{case_id}/sources/{source_id}')
    def source(case_id:str,source_id:str):
        return service.source_text(case_id,source_id)

    @api.post('/api/cases/{case_id}/sources')
    def add_source(case_id:str,body:dict=Body(...)):
        result=service.add_source(case_id,title=body.get('title','Réponse utilisateur'),text=body.get('text'))
        work.jobs.emit(case_id)
        return result

    @api.post('/api/cases/{case_id}/sources/upload')
    def upload(case_id:str,file:UploadFile=File(...),title:str=Form('')):
        service._row(case_id)
        suffix=Path(file.filename or '').suffix.lower()
        upload_root=service.data_dir/'imports'
        upload_root.mkdir(exist_ok=True)
        fd,name=tempfile.mkstemp(suffix=suffix,dir=upload_root)
        path=Path(name)
        try:
            total=0
            with os.fdopen(fd,'wb') as dst:
                while chunk:=file.file.read(1024*1024):
                    total+=len(chunk)
                    if total>50*1024*1024:
                        raise ValueError('Pièce limitée à 50 Mo.')
                    dst.write(chunk)
            result=service.add_source(case_id,path=path,title=(title.strip() or Path(file.filename or 'Pièce jointe').name)[:240])
            work.jobs.emit(case_id)
            return result
        finally:
            path.unlink(missing_ok=True)

    @api.get('/api/cases/{case_id}/draft')
    def draft(case_id:str):
        return work.draft(case_id)

    @api.post('/api/cases/{case_id}/draft/operations')
    def draft_operations(case_id:str,body:dict=Body(...)):
        return api.state.decision.request(case_id,'draft/operations',body,lambda:work.add_operations(case_id,body.get('operations'),body.get('scope'),expected_revision=body.get('revision',body.get('expected_revision'))))

    @api.post('/api/cases/{case_id}/draft/resolve')
    def resolve(case_id:str,body:dict=Body(...)):
        return work.resolve(case_id,body.get('index'),body.get('choice'))

    @api.delete('/api/cases/{case_id}/draft')
    def discard(case_id:str):
        return work.discard(case_id)

    def draft_job(case_id,kind,body):
        if kind == 'apply' and body.get('request_id'):
            with service.store.connection() as db:
                previous = db.execute('SELECT * FROM web_jobs WHERE case_id=? AND request_id=?', (case_id,body['request_id'])).fetchone()
            if previous:
                old = json.loads(previous['payload'])
                if (previous['kind'] != kind or
                        body.get('draft_id', old.get('draft_id')) != old.get('draft_id') or
                        body.get('approval_token', old.get('approval_token')) != old.get('approval_token')):
                    raise ValueError('Cette demande existe avec un contenu différent.')
                # Returning an existing receipt never executes a new mutation.
                return {'job':work.jobs.public(previous),'replayed':True}
        draft=work.draft(case_id)
        draft_id=body.get('draft_id') or draft.get('id')
        if not draft_id:
            raise ValueError('Le brouillon est vide.')
        payload = {'draft_id':draft_id}
        if kind == 'apply':
            token = body.get('approval_token')
            if not token or draft['status'] != 'READY' or draft_id != draft.get('id') or token != draft.get('approval_token'):
                raise ValueError('L’aperçu approuvé est absent ou a changé. Examiner le nouvel aperçu avant application.')
            payload['approval_token'] = token
        return work.jobs.submit(case_id,kind,payload,body.get('request_id'))

    @api.post('/api/cases/{case_id}/draft/preview')
    def preview(case_id:str,body:dict=Body(default_factory=dict)):
        return draft_job(case_id,'preview',body)

    @api.post('/api/cases/{case_id}/draft/apply')
    def apply(case_id:str,body:dict=Body(default_factory=dict)):
        return draft_job(case_id,'apply',body)

    @api.post('/api/cases/{case_id}/recalculate')
    def recalculate(case_id:str,body:dict=Body(default_factory=dict)):
        service._row(case_id)
        return work.jobs.submit(case_id,'recalculate',{'include_tables':body.get('include_tables',False)},body.get('request_id'))

    @api.get('/api/cases/{case_id}/versions')
    def versions(case_id:str):
        return work.versions(case_id)

    @api.post('/api/cases/{case_id}/versions/{version_id}/restore')
    def restore(case_id:str,version_id:str,body:dict=Body(default_factory=dict)):
        return work.jobs.submit(case_id,'restore',{'version_id':version_id},body.get('request_id'))

    @api.get('/api/cases/{case_id}/download')
    def download(case_id:str):
        row,path=work._workbook(case_id)
        return FileResponse(path,media_type='application/vnd.ms-excel.sheet.macroEnabled.12',filename=f'TCA_BP_{case_id}_v{row["revision"]:04d}.xlsm')

    @api.get('/api/cases/{case_id}/jobs')
    def jobs(case_id:str):
        service._row(case_id)
        return {'jobs':work.jobs.list(case_id)}

    @api.post('/api/cases/{case_id}/jobs/{job_id}/retry')
    def retry(case_id:str,job_id:str,body:dict=Body(default_factory=dict)):
        service._row(case_id)
        with service.store.connection() as db:
            job=db.execute('SELECT * FROM web_jobs WHERE id=? AND case_id=?',(job_id,case_id)).fetchone()
        if not job or job['status'] not in ('FAILED','INTERRUPTED'):
            raise ValueError('Seul un travail échoué ou interrompu peut être repris.')
        payload=json.loads(job['payload'])
        if job['kind']=='chat':
            if payload.get('mode') == 'cockpit':
                payload.setdefault('cockpit_origin_job_id', payload.get('resume_job_id', job_id))
            payload['resume_job_id']=job_id
        if job['kind']=='restore' and not all(key in payload for key in ('operation_id','expected_revision','source_sha256')):
            raise ValueError('Ancienne restauration sans contexte de reprise. Examiner les versions avant une nouvelle demande explicite.')
        return work.jobs.submit(case_id,job['kind'],payload,body.get('request_id'))

    @api.get('/api/cases/{case_id}/chat')
    def chat(case_id:str):
        return {'messages':work.messages(case_id)}

    @api.post('/api/cases/{case_id}/chat')
    def send_chat(case_id:str,body:dict=Body(...)):
        row=service._row(case_id)
        message=body.get('message')
        if not isinstance(message,str) or not message.strip() or len(message)>20000:
            raise ValueError('Message requis, au plus 20 000 caractères.')
        if not isinstance(body.get('selection'),dict):
            raise ValueError('Choisir un périmètre pour la discussion.')
        mode=body.get('mode')
        if mode not in (None, 'maintenance', 'cockpit'):
            raise ValueError('Mode de discussion inconnu.')
        if mode == 'cockpit':
            check_id(body.get('request_id'))
            if type(body.get('expected_revision')) is not int or body['expected_revision'] < 0:
                raise ValueError('La révision attendue est obligatoire pour le chat métier.')
            if body['selection'].get('allow_structure'):
                raise ValueError('Les changements de structure relèvent du parcours de maintenance.')
        # Replays keep their original binding even after the case advances.
        request_id=body.get('request_id')
        if request_id:
            with service.store.connection() as db:
                previous=db.execute('SELECT payload FROM web_jobs WHERE case_id=? AND request_id=?',(case_id,request_id)).fetchone()
            if previous:
                old=json.loads(previous['payload'])
                row={**row,'revision':old.get('expected_revision',row['revision']),'sha256':old.get('source_sha256',row['sha256'])}
        payload={'message':message,'selection':body['selection'],'expected_revision':row['revision'],'source_sha256':row['sha256']}
        if mode == 'cockpit':
            if body['expected_revision'] != row['revision']:
                raise ValueError('Le dossier a changé. Actualiser la sélection avant de discuter.')
            payload['mode']='cockpit'
        return work.jobs.submit(case_id,'chat',payload,request_id)

    @api.get('/api/cases/{case_id}/events')
    async def events(case_id:str,request:Request,after:int=0):
        service._row(case_id)
        try:
            cursor=max(after,int(request.headers.get('last-event-id','0')))
        except ValueError:
            cursor=after
        async def stream():
            nonlocal cursor
            idle=0
            while not await request.is_disconnected():
                replay=await asyncio.to_thread(work.jobs.replay_status,case_id,cursor)
                if replay['resync_required']:
                    cursor=replay['latest_event_id']
                    yield f'id: {cursor}\nevent: resync\ndata: {canonical(replay)}\n\n'
                events=await asyncio.to_thread(work.jobs.events,case_id,cursor)
                for event in events:
                    cursor=event['id']
                    yield f'id: {cursor}\nevent: {event["event"]}\ndata: {canonical(event["data"])}\n\n'
                idle+=1
                if idle%15==0:
                    yield ': heartbeat\n\n'
                await asyncio.sleep(1)
        return StreamingResponse(stream(),media_type='text/event-stream',headers={'X-Accel-Buffering':'no'})

    from .decision_api import install_routes
    from .decision_workspace import IntentReviewRequired
    install_routes(api,service,work)
    from .cockpit_api import install_routes as install_cockpit_routes
    install_cockpit_routes(api,api.state.decision)
    @api.exception_handler(IntentReviewRequired)
    async def uncertain_intent(request,exc):
        return JSONResponse({'detail':str(exc),'review_required':True},status_code=409)
    frontend=Path(frontend_dir or service.project_root/'frontend'/'dist')
    if (frontend/'assets').is_dir():
        api.mount('/assets',StaticFiles(directory=frontend/'assets'),name='assets')
    if (frontend/'icone').is_dir():
        api.mount('/icone',StaticFiles(directory=frontend/'icone'),name='cockpit-icons')
    @api.get('/favicon.svg')
    def favicon():
        icon=frontend/'favicon.svg'
        if not icon.is_file():
            raise HTTPException(404,'Icône indisponible.')
        return FileResponse(icon,media_type='image/svg+xml')
    @api.get('/{path:path}')
    def index(path:str):
        if path.startswith('api/'):
            raise HTTPException(404,'Route inconnue.')
        if not (frontend/'index.html').is_file():
            return JSONResponse({'detail':'Interface à compiler : cd frontend puis npm ci et npm run build.'},status_code=503)
        return FileResponse(frontend/'index.html')
    return api


def main():
    parser=argparse.ArgumentParser(description='Atelier TCA BP dans le navigateur')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--data-dir',type=Path)
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--dev',action='store_true',help='Autoriser le proxy Vite local sur le port 5173')
    args=parser.parse_args()
    import uvicorn
    service=Application(data_dir=args.data_dir)
    api=create_app(service,dev=args.dev)
    if not args.no_browser:
        threading.Timer(1.5,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    uvicorn.run(api,host='127.0.0.1',port=args.port,access_log=False,log_level='warning')


if __name__=='__main__':
    main()
