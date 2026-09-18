"""Shared Excel workspace: drafts, migration receipts, versions and conversations.

The browser and MCP call this service. Only Apply adopts a prepared workbook.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import threading
from xml.etree import ElementTree as ET

from .storage import canonical, check_id, confined, digest, now, uid, atomic_json
from .model_registry import model_pin
from .vendor import input_engine as core
from .web_jobs import JobQueue
from .web_lock import excel_lock


class WebWorkspace:
    def __init__(self, app, *, settings=None, chat=None, variant_runner=None):
        self.app, self.store = app, app.store
        self._lock = threading.RLock()
        self._cache = {}
        self.variant_runner = variant_runner
        from .web_settings import WebSettings
        from .web_chat import ChatCoordinator
        self.settings = settings or WebSettings(app.data_dir / 'web_settings.json')
        self.chat = chat or ChatCoordinator(self.settings)
        self.jobs = JobQueue(self.store, self.run_job, self._recover_interrupted_previews)
        with self.store.connection() as db:
            db.executescript('''
              CREATE TABLE IF NOT EXISTS web_drafts(
                id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id),
                revision INTEGER NOT NULL, source_sha256 TEXT NOT NULL,
                status TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS web_versions(
                id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), revision INTEGER NOT NULL,
                workbook TEXT NOT NULL, sha256 TEXT NOT NULL, pin TEXT NOT NULL, field_states TEXT NOT NULL,
                kind TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(case_id,revision));
              CREATE TABLE IF NOT EXISTS web_messages(
                id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), job_id TEXT,
                role TEXT NOT NULL, content TEXT NOT NULL, agents TEXT NOT NULL DEFAULT '[]',
                private_context TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS web_tool_runs(
                id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id),
                job_id TEXT NOT NULL, agent_id TEXT NOT NULL, task TEXT NOT NULL,
                transcript_sha256 TEXT NOT NULL, private_context TEXT NOT NULL,
                created_at TEXT NOT NULL, UNIQUE(job_id,agent_id,transcript_sha256));
              CREATE TABLE IF NOT EXISTS web_adoptions(
                case_id TEXT NOT NULL REFERENCES cases(id), operation_id TEXT NOT NULL,
                kind TEXT NOT NULL, input_sha256 TEXT NOT NULL, result TEXT NOT NULL,
                created_at TEXT NOT NULL, PRIMARY KEY(case_id,operation_id));
            ''')

    def _recover_interrupted_previews(self, db, jobs):
        """Release the draft UI state, never steal or delete a case lock."""
        for job in jobs:
            if job['kind'] != 'preview':
                continue
            payload = json.loads(job['payload'])
            row = db.execute("SELECT * FROM web_drafts WHERE id=? AND case_id=? AND status='PREPARING'",
                             (payload.get('draft_id'), job['case_id'])).fetchone()
            if row is None:
                continue
            draft = json.loads(row['payload'])
            # The worker may still hold its dedicated Excel process. Preserve
            # the registered path; discard/retry cleans it under the case lock.
            draft['interruption'] = {'job_id': job['id'], 'message': 'Aperçu interrompu. Le lot et ses contrôles sont conservés ; relancer la vérification avant application.'}
            self._save_draft(db, row['id'], draft, 'DRAFT')
            self.jobs.emit(job['case_id'], db=db)

    @staticmethod
    def _approval_token(row, payload):
        reviewed = {key: payload.get(key) for key in ('operations', 'conflicts', 'preview_sha256', 'profile', 'validation', 'changes', 'diagnostics')}
        reviewed.update(draft_id=row['id'], revision=row['revision'], source_sha256=row['source_sha256'])
        return hashlib.sha256(canonical(reviewed).encode()).hexdigest()

    def _workbook(self, case_id):
        row = self.app._row(case_id)
        return row, self.app._workbook(row)

    def _read(self, case_id, action):
        row, path = self._workbook(case_id)
        # Immutable versions make a small parsed workbook cache safe. Bound it
        # to two versions; don't retain one XML tree for every client workbook.
        with self._lock:
            key = (case_id, row['sha256'])
            if key not in self._cache:
                while len(self._cache) >= 2:
                    first = next(iter(self._cache))
                    self._cache.pop(first).close()
                self._cache[key] = core.Workbook(path)
            return action(self._cache[key], row)

    def close(self):
        self.jobs.close()
        with self._lock:
            for wb in self._cache.values():
                wb.close()
            self._cache.clear()

    def sheets(self, case_id):
        def read(wb, row):
            result = []
            for name, item in wb.sheets.items():
                # Stream only to dimension; a navigation list must not parse
                # several hundred thousand cells on every SSE refresh.
                with wb.z.open(item['part']) as stream:
                    dimension = None
                    for _, node in ET.iterparse(stream, events=('start',)):
                        if node.tag.endswith('}dimension'):
                            dimension = node.get('ref', 'A1')
                            break
                        if node.tag.endswith('}sheetData'):
                            break
                _, column, line = core.coord((dimension or 'A1').split(':')[-1])
                result.append({'name': name, 'rows': max(line, 100), 'columns': max(column, 26), 'state': item['state']})
            return {'sheets': result, 'revision': row['revision']}
        return self._read(case_id, read)

    def cells(self, case_id, sheet, row=1, column=1, rows=100, columns=26):
        from .web_cells import cell_display
        if any(type(x) is not int for x in (row,column,rows,columns)) or not (1 <= row <= 1048576 and 1 <= column <= 16384 and 1 <= rows <= 500 and 1 <= columns <= 100 and rows*columns <= 20000):
            raise ValueError('Fenêtre de cellules hors limites.')
        def read(wb, case):
            cells = []
            states = json.loads(case['field_states'])
            sheet_cells = wb.sheet(sheet)[1]
            for r in range(row, min(row+rows,1048577)):
                for c in range(column,min(column+columns,16385)):
                    address = core.colname(c)+str(r)
                    value, formula = wb.value(sheet,address), wb.formula(sheet,address)
                    node = sheet_cells.get(address)
                    state = states.get(sheet+'!'+address, {})
                    cells.append({'cell':address,'row':r,'column':c,'value':value,
                                  'formula': '='+formula if formula is not None else None,
                                  'display': '' if value is None else str(value),
                                  'source':state.get('evidence'),'state':state.get('status','NON_RENSEIGNE'),
                                  **cell_display(wb,sheet,address),
                                  'calculation_status':case['calculation_status']})
            return {'sheet':sheet,'cells':cells,'revision':case['revision'],'row':row,'column':column,'rows':rows,'columns':columns}
        return self._read(case_id, read)

    def agents(self, case_id):
        engine = self.app.engine_for_case(case_id)
        if hasattr(engine, 'profile'):
            agents = engine.profile.get('agents')
            if isinstance(agents,list):
                return agents
        return self.app.agents(case_id)

    def _draft_row(self, case_id, db=None):
        if db is None:
            with self.store.connection() as conn:
                return self._draft_row(case_id, conn)
        return db.execute("SELECT * FROM web_drafts WHERE case_id=? AND status NOT IN ('APPLIED','DISCARDED') ORDER BY rowid DESC LIMIT 1", (case_id,)).fetchone()

    @staticmethod
    def _public_draft(row):
        if not row:
            return {'id':None,'operations':[],'changes':[],'conflicts':[],'diagnostics':[],'status':'EMPTY'}
        payload = json.loads(row['payload'])
        result = {key: value for key,value in {**dict(row),**payload}.items()
                if key not in ('payload','preview_path','preview_sha256','profile','source_states')}
        result['approval_token'] = WebWorkspace._approval_token(row, payload) if row['status'] == 'READY' and payload.get('preview_sha256') and not payload.get('conflicts') else None
        return result

    def draft(self, case_id):
        self.app._row(case_id)
        return self._public_draft(self._draft_row(case_id))

    def _save_draft(self, db, draft_id, payload, status='DRAFT'):
        db.execute('UPDATE web_drafts SET payload=?,status=?,updated_at=? WHERE id=?', (canonical(payload),status,now(),draft_id))

    def _validate_draft_operations(self, case_id, payload):
        """Recheck persisted source integrity, scope and schema at each boundary."""
        from .web_chat import validate_operations
        from .web_blocks import expand_operations, ExpandedOperations
        operations = payload.get('operations')
        if payload.get('bounded_blocks') is True and isinstance(operations,list):
            operations=ExpandedOperations(operations,envelope_count=1,contains_blocks=True)
        operations=expand_operations(operations)
        with self.store.connection() as db:
            sources = [dict(source) for source in db.execute('SELECT id,case_id FROM sources WHERE case_id=?', (case_id,))]
        context = {'case_id': case_id, 'sources': sources}
        grouped, result, checked_sources = {}, [], set()
        for operation in operations:
            if not isinstance(operation, dict) or not isinstance(operation.get('_scope'), dict):
                raise ValueError('Le périmètre enregistré de cette opération est absent ou invalide.')
            safe = {key: value for key, value in operation.items() if not key.startswith('_')}
            if safe.get('evidence_id') and safe['evidence_id'] not in checked_sources:
                self.app.source_text(case_id, safe['evidence_id'])
                checked_sources.add(safe['evidence_id'])
            validated = validate_operations([safe], operation['_scope'], context)[0]
            scope_key = canonical(operation['_scope'])
            grouped.setdefault(scope_key, []).append(validated)
            result.append(validated)
        for scope, group in grouped.items():
            validate_operations(ExpandedOperations(group,envelope_count=1,contains_blocks=operations.contains_blocks), json.loads(scope), context)
        return ExpandedOperations(result,envelope_count=operations.envelope_count,contains_blocks=operations.contains_blocks)

    def add_operations(self, case_id, operations, scope=None, *, origin='manual', expected_revision=None):
        from .web_chat import validate_operations
        from .web_blocks import expand_operations, ExpandedOperations
        operations=expand_operations(operations)
        if any(not isinstance(op,dict) for op in operations):
            raise ValueError('Chaque modification doit être un objet structuré.')
        # Validation is repeated during preview and apply; model output is data.
        checked_sources=set()
        for op in operations:
            if op.get('evidence_id') and op['evidence_id'] not in checked_sources:
                self.app.source_text(case_id,op['evidence_id'])
                checked_sources.add(op['evidence_id'])
        scope=scope or {'sheet':operations[0].get('sheet') or operations[0].get('name'),'allow_structure':True}
        sources=self.app.get_case(case_id)['sources']
        validation_context={'case_id':case_id,'sources':sources}
        if origin=='manual':
            validation_context['sources']=sources+[{'id':'manual_preview','case_id':case_id}]
            validation_context['user_source_id']='manual_preview'
        operations=validate_operations(operations,scope,validation_context)
        if any(op.get('evidence_id')=='manual_preview' for op in operations):
            source=self.app.add_source(case_id,text=canonical({'saisie_manuelle':operations}),title='Saisie manuelle dans le tableur')
            for op in operations:
                if op.get('evidence_id')=='manual_preview':
                    op['evidence_id']=source['id']
        with self.store.case_lock(case_id):
            row = self.app._row(case_id)
            if expected_revision is not None and expected_revision != row['revision']:
                raise ValueError('La proposition est périmée. Relire le dossier.')
            self.app._workbook(row)
            with self.store.connection() as db:
                existing = self._draft_row(case_id,db)
                if existing and (existing['revision'] != row['revision'] or existing['source_sha256'] != row['sha256']):
                    raise ValueError('Le brouillon est périmé. Conserver ou abandonner ce lot avant une nouvelle demande.')
                if existing and existing['status'] == 'PREPARING':
                    raise ValueError('Un aperçu est en cours ; attendre sa fin avant de modifier le brouillon.')
                payload = json.loads(existing['payload']) if existing else {'operations':[],'conflicts':[],'changes':[],'diagnostics':[]}
                extensions={'extend_offer','extend_register'}
                if payload['operations'] and (any(op['type'] in extensions for op in payload['operations']) or any(op['type'] in extensions for op in operations)):
                    raise ValueError('Terminer le brouillon courant avant une extension de bloc métier. Les modifications existantes sont conservées.')
                payload['bounded_blocks']=payload.get('bounded_blocks') is True or operations.contains_blocks
                destinations={(old.get('sheet'),old.get('cell')):i for i,old in enumerate(payload['operations']) if old['type'] in ('set_value','set_formula')}
                for incoming in copy.deepcopy(operations):
                    incoming['_origin'] = origin
                    incoming['_scope'] = scope
                    target=(incoming.get('sheet'),incoming.get('cell'))
                    match = destinations.get(target) if incoming['type'] in ('set_value','set_formula') else None
                    if match is not None:
                        old = payload['operations'][match]
                        a,b = ({k:obj.get(k) for k in ('type','value','formula')} for obj in (old,incoming))
                        if a == b:
                            continue
                        if origin == 'manual':
                            payload['operations'][match] = incoming
                        else:
                            next_index = max(payload.get('next_conflict_index', 0), max((item['index'] + 1 for item in payload['conflicts']), default=0))
                            payload['conflicts'].append({'index':next_index,'operation_index':match,'existing':old,'incoming':incoming})
                            payload['next_conflict_index'] = next_index + 1
                    else:
                        if incoming['type'] in ('set_value','set_formula'):
                            destinations[target]=len(payload['operations'])
                        payload['operations'].append(incoming)
                # Bound the entire shared draft, including successive requests.
                expand_operations(ExpandedOperations(payload['operations'],envelope_count=1,contains_blocks=True) if payload['bounded_blocks'] else payload['operations'])
                payload['changes'],payload['diagnostics'] = [],[]
                superseded={'preview_path':payload.get('preview_path')}
                for key in ('preview_path','preview_sha256','profile','validation'):
                    payload.pop(key,None)
                if existing:
                    self._save_draft(db,existing['id'],payload)
                else:
                    db.execute('INSERT INTO web_drafts VALUES(?,?,?,?,?,?,?,?)', (uid('draft_'),case_id,row['revision'],row['sha256'],'DRAFT',canonical(payload),now(),now()))
                self.jobs.emit(case_id,db=db)
            self._drop_preview(case_id,superseded)
        return self.draft(case_id)

    def resolve(self,case_id,index,choice):
        if choice not in ('existing','incoming'):
            raise ValueError('Choisir la proposition à conserver.')
        with self.store.case_lock(case_id), self.store.connection() as db:
            draft = self._draft_row(case_id,db)
            if not draft or draft['status']=='PREPARING':
                raise ValueError('Brouillon indisponible.')
            payload=json.loads(draft['payload'])
            matches=[x for x in payload['conflicts'] if x['index']==index]
            if len(matches)!=1:
                raise ValueError('Conflit inconnu.')
            conflict=matches[0]
            payload['operations'][conflict['operation_index']]=conflict[choice]
            payload['conflicts'].remove(conflict)
            self._save_draft(db,draft['id'],payload)
        return self.draft(case_id)

    def discard(self,case_id):
        with self.store.case_lock(case_id):
            with self.store.connection() as db:
                draft=self._draft_row(case_id,db)
                if draft:
                    if draft['status']=='PREPARING':
                        raise ValueError('Attendre la préparation du lot.')
                    db.execute("UPDATE web_drafts SET status='DISCARDED' WHERE id=?",(draft['id'],))
                    self.store.history(db,case_id,'BROUILLON_ABANDONNE',{'draft_id':draft['id']})
            if draft:
                self._drop_preview(case_id,json.loads(draft['payload']))
        return self.draft(case_id)

    def _drop_preview(self,case_id,payload):
        """Effacer une copie d'aperçu adoptée, abandonnée ou remplacée.

        Chaque aperçu laisse une copie complète du classeur et, après
        application, la variante scellée du modèle : plusieurs centaines de
        mégaoctets par lot si rien ne les retire. La version publiée sous
        versions/ et son reçu ne sont jamais touchés.
        """
        relative=payload.get('preview_path')
        if not relative:
            return
        try:
            folder=confined(self.store.case_dir(case_id),relative).parent
            root=self.store.case_dir(case_id).resolve()
            if folder.parent==root/'transactions' and folder.name.startswith('web_preview_') and folder.resolve().is_relative_to(root/'transactions'):
                # Preserve the complete reviewed manifest and receipts. The
                # native request duplicates their literals: retain only its
                # digest/count, never a second raw financial request. Never
                # follow a link while removing temporary workbook/model copies.
                diagnostics=root/'transactions'/'preview_diagnostics'/folder.name
                for candidate in sorted(folder.rglob('*'), key=lambda item:len(item.parts), reverse=True):
                    if candidate.is_symlink() or (hasattr(candidate,'is_junction') and candidate.is_junction()):
                        continue
                    if not candidate.resolve().is_relative_to(folder.resolve()):
                        continue
                    if candidate.is_file():
                        model_component=any(p.name.startswith('modele_') for p in candidate.parents if p!=folder)
                        if candidate.suffix.lower()!='.xlsm' and not model_component:
                            saved=diagnostics/candidate.relative_to(folder)
                            saved.parent.mkdir(parents=True,exist_ok=True)
                            if candidate.name=='request.json':
                                request_sha=digest(candidate)
                                try:
                                    request=json.loads(candidate.read_text(encoding='utf-8-sig'))
                                    if not isinstance(request,dict):request={}
                                except (ValueError,OSError):request={}
                                operations=request.get('operations')
                                source_sha=request.get('source_sha256')
                                if not isinstance(source_sha,str) or not re.fullmatch(r'[0-9a-f]{64}',source_sha):source_sha=None
                                output_name=Path(request['output']).name if isinstance(request.get('output'),str) else None
                                atomic_json(saved,{'schema':'tca-bp-preview-request-summary/1','sha256':request_sha,
                                    'operation_count':len(operations) if isinstance(operations,list) else None,
                                    'source_sha256':source_sha,'outputbasename':output_name})
                            elif not saved.exists():shutil.copyfile(candidate,saved)
                        candidate.unlink(missing_ok=True)
                    elif candidate.is_dir():
                        try:candidate.rmdir()
                        except OSError:pass
                try:folder.rmdir()
                except OSError:pass
        except (ValueError,OSError):
            # Un aperçu résiduel gêne moins qu'une adoption transformée en échec.
            pass

    def _snapshot_version(self,row,db,kind='EXISTANTE'):
        db.execute('INSERT OR IGNORE INTO web_versions VALUES(?,?,?,?,?,?,?,?,?)',
                   (uid('version_'),row['id'],row['revision'],row['workbook'],row['sha256'],canonical(model_pin(row)),row['field_states'],kind,now()))

    def versions(self,case_id):
        row=self.app._row(case_id)
        with self.store.connection() as db:
            # Import old service revisions from their recorded output hashes.
            # Files alone do not constitute an authenticated historical version.
            events=[{**dict(x),'details':json.loads(x['details'])} for x in db.execute('SELECT * FROM history WHERE case_id=? ORDER BY rowid',(case_id,))]
            origin=next((x['details'] for x in events if x['kind']=='CREATION'),{})
            known_pin=model_pin(origin)
            states={}
            candidates={p.name:p for p in (self.store.case_dir(case_id)/'versions').glob('*.xlsm')}
            existing={x[0] for x in db.execute('SELECT revision FROM web_versions WHERE case_id=?',(case_id,))}
            for event in events:
                details=event['details']
                if event['kind']=='MIGRATION_MODELE':
                    known_pin=model_pin(details['new_model'])
                if not isinstance(details.get('revision'),int) or details['revision'] in existing:
                    continue
                if model_pin(details).get('model_ref'):
                    known_pin=model_pin(details)
                for change in details.get('changes',[]):
                    if isinstance(change,dict) and all(k in change for k in ('sheet','cell','value')):
                        states[change['sheet']+'!'+change['cell']]={'status':change.get('status','HYPOTHESE'),'evidence':change.get('evidence'),'value':change['value']}
                expected=details.get('output_sha256') or (known_pin['template_sha256'] if details['revision']==0 else None)
                if not expected or not known_pin['model_ref']:
                    continue
                prefix=f'v{details["revision"]:04d}'
                file=next((path for name,path in candidates.items() if name.startswith(prefix) and digest(path)==expected),None)
                if file:
                    historical={**row,'revision':details['revision'],'workbook':str(file.relative_to(self.store.case_dir(case_id))),
                                'sha256':expected,'field_states':canonical(states),**known_pin}
                    self._snapshot_version(historical,db,event['kind'])
                    existing.add(details['revision'])
            self._snapshot_version(row,db)
            items=[{**dict(x),'current':x['revision']==row['revision']} for x in db.execute('SELECT * FROM web_versions WHERE case_id=? ORDER BY revision DESC',(case_id,))]
        return {'versions':[{k:v for k,v in item.items() if k not in ('field_states','pin','workbook')} for item in items]}

    def preview(self,case_id,draft_id,progress=lambda x:None):
        from .web_structure import prepare_variant
        from .web_model import initial_profile
        with self.store.case_lock(case_id):
            row,path=self._workbook(case_id)
            with self.store.connection() as db:
                draft=db.execute('SELECT * FROM web_drafts WHERE id=? AND case_id=?',(draft_id,case_id)).fetchone()
                if not draft or draft['status'] in ('APPLIED','DISCARDED'):
                    raise ValueError('Brouillon indisponible.')
                if draft['revision']!=row['revision'] or draft['source_sha256']!=row['sha256']:
                    raise ValueError('Lot périmé : la version du classeur a changé.')
                payload=json.loads(draft['payload'])
                if payload['conflicts']:
                    raise ValueError('Résoudre les conflits avant de préparer le lot.')
                superseded={'preview_path':payload.get('preview_path')}
                self._save_draft(db,draft_id,payload,'PREPARING')
            try:
                engine=self.app.engine_for_case(case_id)
                profile=initial_profile(engine,path)
                folder=self.store.case_dir(case_id)/'transactions'/uid('web_preview_')
                output=folder/'apercu.xlsm'
                # Persist the destination before creating even an empty folder.
                # A hard stop or a failing serializer must not orphan its XLSM.
                payload['preview_path']=str(output.relative_to(self.store.case_dir(case_id)))
                for key in ('preview_sha256','profile','validation'):
                    payload.pop(key,None)
                with self.store.connection() as db:
                    self._save_draft(db,draft_id,payload,'PREPARING')
                folder.mkdir(parents=True)
                self._drop_preview(case_id,superseded)
                ops=self._validate_draft_operations(case_id,payload)
                from .web_validation import prepare_native_operations
                ops=prepare_native_operations(engine,path,profile,ops)
                progress({'message':'Préparation de la copie et contrôle des références'})
                kwargs={'runner':self.variant_runner} if self.variant_runner else {}
                with excel_lock():
                    result=prepare_variant(path,output,profile,ops,**kwargs)
                if not result.get('blocked'):
                    from .wacc_fingerprint_migration import certificate_fingerprint_change
                    result['profile']=certificate_fingerprint_change(profile,path,output,result['profile'],ops)
                    from .dcf_calendar_migration import certificate_calendar_change
                    result['profile']=certificate_calendar_change(profile,path,output,result['profile'],ops)
                    from .fiscal_calendar_migration import certificate_fiscal_calendar_change
                    result['profile']=certificate_fiscal_calendar_change(profile,path,output,result['profile'],ops)
                payload.update(changes=result.get('changes',ops),diagnostics=result.get('diagnostics',[]),
                               profile=result['profile'],validation={k:v for k,v in result.items() if k not in ('profile','changes')})
                if output.is_file():
                    payload.update(preview_path=str(output.relative_to(self.store.case_dir(case_id))),preview_sha256=digest(output))
                with self.store.connection() as db:
                    self._save_draft(db,draft_id,payload,'BLOCKED' if result.get('blocked') else 'READY')
                if superseded['preview_path']!=payload.get('preview_path'):
                    self._drop_preview(case_id,superseded)
            except Exception:
                with self.store.connection() as db:
                    self._save_draft(db,draft_id,payload,'DRAFT')
                self._drop_preview(case_id,payload)
                raise
        return self.draft(case_id)

    def _adopt(self,row,source,pin,states,kind,details,db):
        source_sha=digest(source)
        current=confined(self.store.case_dir(row['id']),row['workbook'])
        if digest(current)!=row['sha256']:
            raise ValueError('La version courante a changé hors de l’outil.')
        revision=row['revision']+1
        relative=f'versions/v{revision:04d}_{uid()[:10]}.xlsm'
        final=confined(self.store.case_dir(row['id']),relative)
        with source.open('rb') as src,final.open('xb') as dst:
            shutil.copyfileobj(src,dst)
            dst.flush()
            os.fsync(dst.fileno())
        output_sha=digest(final)
        if output_sha!=source_sha or digest(source)!=source_sha or digest(current)!=row['sha256']:
            raise ValueError('Les fichiers ont changé pendant la publication ; copie non adoptée.')
        receipt={**details,'case_id':row['id'],'revision':revision,'old_model':model_pin(row),'new_model':pin,
                 'source_sha256':row['sha256'],'output_sha256':output_sha,'workbook':relative,'kind':kind,'created_at':now()}
        receipt_path=relative.replace('.xlsm','.web.json')
        atomic_json(confined(self.store.case_dir(row['id']),receipt_path),receipt)
        public_receipt={k:v for k,v in receipt.items() if k!='mapping'}
        public_receipt.update(receipt_path=receipt_path,
                              profile_sha256=details.get('mapping',{}).get('profile_sha256'))
        self._snapshot_version(row,db)
        if pin!=model_pin(row):
            self.store.history(db,row['id'],'MIGRATION_MODELE',{'old_model':model_pin(row),'new_model':pin,
                               'receipt_path':receipt_path,'receipt_sha256':digest(confined(self.store.case_dir(row['id']),receipt_path))})
        result=db.execute('UPDATE cases SET revision=?,workbook=?,sha256=?,model_id=?,model_ref=?,template_sha256=?,schema_sha256=?,field_states=?,calculation_status=?,updated_at=? WHERE id=? AND revision=? AND sha256=?',
                    (revision,relative,output_sha,pin['model_id'],pin['model_ref'],pin['template_sha256'],pin['schema_sha256'],canonical(states),'A_RECALCULER',now(),row['id'],row['revision'],row['sha256']))
        if result.rowcount!=1:
            raise ValueError('La version courante a changé pendant la publication.')
        self.store.history(db,row['id'],kind,public_receipt)
        self._snapshot_version(self.app._row(row['id'],db),db,kind)
        self.jobs.emit(row['id'],db=db)
        return public_receipt

    def _save_state_after_commit(self, case_id, receipt):
        try:
            self.app._save_state(case_id)
        except Exception:
            # SQLite and the version receipt already committed. A failed mirror
            # must not turn a successful adoption into a retryable mutation.
            receipt = {**receipt, 'state_mirror_warning': 'Version enregistrée ; le miroir local du dossier reste à reconstruire.'}
        return receipt

    def apply(self,case_id,draft_id,approval_token=None):
        from .web_model import seal_profile_model,ProfileEngine,initial_profile
        from .web_structure import operation_targets
        with self.store.case_lock(case_id):
            row,path=self._workbook(case_id)
            with self.store.connection() as db:
                draft=db.execute('SELECT * FROM web_drafts WHERE id=? AND case_id=?',(draft_id,case_id)).fetchone()
            if not draft:
                raise ValueError('Brouillon inconnu.')
            payload=json.loads(draft['payload'])
            if not isinstance(approval_token, str) or approval_token != self._approval_token(draft, payload):
                raise ValueError('L’aperçu approuvé est absent ou a changé. Examiner le nouvel aperçu avant application.')
            if draft['status']=='APPLIED':
                return {**payload['receipt'],'replayed':True}
            if draft['status']!='READY' or payload['conflicts']:
                raise ValueError('Examiner un aperçu valide et résoudre les conflits avant application.')
            if draft['revision']!=row['revision'] or draft['source_sha256']!=row['sha256']:
                raise ValueError('Lot périmé : préparer un nouveau brouillon.')
            output=confined(self.store.case_dir(case_id),payload['preview_path'])
            if not output.is_file() or digest(output)!=payload['preview_sha256']:
                raise ValueError('La copie préparée a changé ; application refusée.')
            self._validate_draft_operations(case_id,payload)
            engine=self.app.engine_for_case(case_id)
            profile_before=initial_profile(engine,path)
            ops=[{k:v for k,v in op.items() if not k.startswith('_')} for op in payload['operations']]
            known=getattr(engine,'schema',{}).get('cells',{})
            inputs_only=all(op['type']=='set_value' and op['cell'] in known.get(op['sheet'],{}) for op in ops)
            if inputs_only:
                # An ordinary input revision does not change the template's
                # fiscal contract. Verify the prepared file against its exact
                # existing seal before retaining that model pin.
                engine.context(output)
                candidate=engine
                pin=model_pin(row)
                adopted_profile=profile_before
            else:
                model_dir=output.parent/uid('modele_')
                seal_profile_model(engine,output,payload['profile'],model_dir)
                candidate=ProfileEngine(self.app.project_root,model_dir)
                pin=self.app.registry.register(candidate)
                adopted_profile=payload['profile']
            states=json.loads(row['field_states'])
            # Profile engine owns coordinate migration, retaining source IDs.
            if not inputs_only and hasattr(candidate,'remap_states_from'):
                states=candidate.remap_states_from(engine,states)
            for target in operation_targets(profile_before,ops):
                if not target.get('deleted') and not target.get('superseded'):
                    op=ops[target['operation_index']]
                    states[target['sheet']+'!'+target['cell']]={'status':op.get('status','HYPOTHESE'),'evidence':op.get('evidence_id'),
                        'value':op.get('value',op.get('formula')),'draft_id':draft_id}
            if digest(output)!=payload['preview_sha256']:
                raise ValueError('La copie préparée a changé avant adoption.')
            with self.store.connection() as db:
                receipt=self._adopt(row,output,pin,states,'LOT_WEB_APPLIQUE',{'draft_id':draft_id,'operations':payload['operations'],'mapping':adopted_profile,'validation':payload.get('validation'),'model_unchanged':inputs_only},db)
                payload['receipt']=receipt
                self._save_draft(db,draft_id,payload,'APPLIED')
            self._drop_preview(case_id,payload)
            receipt = self._save_state_after_commit(case_id, receipt)
        return receipt

    def restore(self,case_id,version_id,*,operation_id=None,expected_revision=None,source_sha256=None):
        with self.store.case_lock(case_id):
            row,_=self._workbook(case_id)
            with self.store.connection() as db:
                request_sha = hashlib.sha256(canonical({'version_id': version_id, 'expected_revision': expected_revision, 'source_sha256': source_sha256}).encode()).hexdigest()
                if operation_id:
                    check_id(operation_id)
                    previous = db.execute('SELECT * FROM web_adoptions WHERE case_id=? AND operation_id=?', (case_id,operation_id)).fetchone()
                    if previous:
                        if previous['kind'] != 'restore' or previous['input_sha256'] != request_sha:
                            raise ValueError('Cette restauration existe avec un contenu différent.')
                        return {**json.loads(previous['result']), 'replayed': True}
                if (expected_revision is not None and expected_revision != row['revision'] or
                        source_sha256 is not None and source_sha256 != row['sha256']):
                    raise ValueError('Le dossier a changé depuis la demande de restauration. Examiner ses versions avant une nouvelle demande.')
                version=db.execute('SELECT * FROM web_versions WHERE id=? AND case_id=?',(version_id,case_id)).fetchone()
                if not version:
                    raise ValueError('Cette version ne fait pas partie du dossier.')
                source=confined(self.store.case_dir(case_id),version['workbook'])
                if not source.is_file() or digest(source)!=version['sha256']:
                    raise ValueError('La copie historique est absente ou modifiée.')
                pin=json.loads(version['pin'])
                self.app.registry.verify(pin)
                result=self._adopt(row,source,pin,json.loads(version['field_states']),'VERSION_RESTAUREE',{'restored_version_id':version_id},db)
                if operation_id:
                    db.execute('INSERT INTO web_adoptions VALUES(?,?,?,?,?,?)', (case_id,operation_id,'restore',request_sha,canonical(result),now()))
            result = self._save_state_after_commit(case_id, result)
        return result

    def messages(self,case_id):
        self.app._row(case_id)
        with self.store.connection() as db:
            return [{'id':x['id'],'role':x['role'],'content':x['content'],'agents':json.loads(x['agents']),
                     'status':x['status'],'created_at':x['created_at']} for x in db.execute('SELECT * FROM web_messages WHERE case_id=? ORDER BY rowid',(case_id,))]

    def chat_context(self,case_id,selection,message):
        from .web_chat import normalize_selection, _bounds
        scope=normalize_selection(selection)
        row,_=self._workbook(case_id)
        sheet=scope['sheet']
        areas=scope['ranges'] or ['A1:Z80']
        bounds=[_bounds(area) for area in areas]
        if sum((right-left+1)*(bottom-top+1) for left,top,right,bottom in bounds)>10000:
            raise ValueError('Sélection trop grande pour un message. Choisir au plus 10 000 cellules.')
        # Read the actual selected windows, in bounded API chunks. Prefer useful
        # cells in the provider excerpt while explicitly reporting every omission.
        seen={}
        for left,top,right,bottom in bounds:
            for r in range(top,bottom+1,200):
                for c in range(left,right+1,100):
                    window=self.cells(case_id,sheet,r,c,min(bottom-r+1,200),min(right-c+1,100))
                    if window['revision']!=row['revision']:
                        raise ValueError('Le classeur a changé pendant la préparation du contexte.')
                    for cell in window['cells']:
                        seen[cell['cell']]=cell
        populated=[cell for cell in seen.values() if cell.get('value') is not None or cell.get('formula') is not None or cell.get('source')]
        cells=(populated or list(seen.values()))[:500]
        selection_summary={'sheet':sheet,'ranges_read':areas,'whole_sheet_scope':not bool(scope['ranges']),
                           'scanned_cell_count':len(seen),'populated_cell_count':len(populated),
                           'included_cell_count':len(cells),'omitted_cell_count':len(seen)-len(cells),
                           'note':'Ces cellules sont des extraits. Lire les autres cellules avec read_cells; ne pas supposer leur contenu.'}
        cited_sources={cell.get('source') for cell in cells if isinstance(cell.get('source'),str)}
        terms={word.casefold() for word in re.findall(r'[\wÀ-ÿ]+',message+' '+sheet) if len(word)>3}
        available=self.app.get_case(case_id)['sources']
        # Relevant referenced sources first, then title relevance and recency.
        ranked=sorted(enumerate(available),key=lambda pair:(pair[1]['id'] in cited_sources,
                      sum(term in pair[1]['title'].casefold() for term in terms),pair[0]),reverse=True)
        sources=[]
        for _,source in ranked[:12]:
            item=self.app.source_text(case_id,source['id'])
            sources.append({k:item[k] for k in ('id','title','kind','sha256')})
            sources[-1]['case_id']=case_id
            text=item['text']
            positions=[text.casefold().find(term) for term in terms if term in text.casefold()]
            start=max(0,min(positions)-700) if positions else 0
            sources[-1].update(text=text[start:start+3000],excerpt_start=start,
                               total_characters=len(text),excerpt_only=len(text)>3000)
        source=self.app.add_source(case_id,text=message,title='Demande au chat')
        sources.insert(0,{'id':source['id'],'case_id':case_id,'title':source['title'],'text':message})
        contracts=self.agents(case_id)
        engine=self.app.engine_for_case(case_id)
        catalog=engine.catalog()
        if isinstance(catalog,dict):
            catalog=catalog.get('fields',[])
        fields=[]
        for field in catalog:
            if field.get('sheet') not in scope.get('sheets',[sheet]):
                continue
            item={key:field[key] for key in ('id','sheet','label','kind','unit','ranges','choices','constraints','notes','semantics') if key in field}
            if not item.get('ranges'):
                item['cells']=field.get('cells',[])
            fields.append(item)
        register=copy.deepcopy(getattr(engine,'schema',{}).get('registers',{}).get(sheet))
        dependencies=[]
        try:
            dependencies=self.app.sheet_info(sheet,case_id).get('dependencies',[])
        except (ValueError,KeyError):
            pass
        return {'case_id':case_id,'revision':row['revision'],'source_sha256':row['sha256'],'selection':selection,
                'cells':cells,'sources':sources,'agents':contracts,'dependencies':dependencies,
                'selection_summary':selection_summary,'source_summary':{'available_sources':len(available)+1,'included_sources':len(sources),'note':'Extraits utiles; les pièces complètes restent dans le dossier local.'},
                'fields':fields,'register':register,
                'draft':self.draft(case_id),'user_source_id':source['id'],'calculation_status':row['calculation_status']}

    def charts(self,case_id):
        from .web_charts import cached_points
        def read(wb,row):
            ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
            charts=[]
            for name in wb.z.namelist():
                if not name.startswith('xl/charts/chart') or not name.endswith('.xml'):
                    continue
                root=ET.fromstring(wb.z.read(name))
                title=' '.join(x.text or '' for x in root.findall('.//c:title//{http://schemas.openxmlformats.org/drawingml/2006/main}t',ns))
                series=[]
                for s in root.findall('.//c:ser',ns):
                    values=cached_points(s.find('c:val',ns),numeric=True)
                    categories=cached_points(s.find('c:cat',ns))
                    label=s.find('.//c:tx//c:v',ns)
                    series.append({'name':label.text if label is not None else 'Série','categories':categories,'values':values[:1000]})
                charts.append({'name':Path(name).stem,'title':title or Path(name).stem,'series':series})
            return {'revision':row['revision'],'sha256':row['sha256'],'calculation_status':row['calculation_status'],'charts':charts}
        return self._read(case_id,read)

    def run_job(self,job,payload,progress):
        case_id=job['case_id']
        kind=job['kind']
        if kind=='preview':
            return self.preview(case_id,payload['draft_id'],progress)
        if kind=='apply':
            return self.apply(case_id,payload['draft_id'],payload.get('approval_token'))
        if kind=='restore':
            if not all(key in payload for key in ('operation_id','expected_revision','source_sha256')):
                raise ValueError('Ancienne restauration sans contexte de reprise. Examiner les versions avant une nouvelle demande explicite.')
            return self.restore(case_id,payload['version_id'],operation_id=payload['operation_id'],expected_revision=payload['expected_revision'],source_sha256=payload['source_sha256'])
        if kind=='recalculate':
            with self.store.connection() as db:
                self._snapshot_version(self.app._row(case_id),db)
            result=self.app.recalculate(case_id,include_tables=payload.get('include_tables',False))
            self.versions(case_id)
            return result
        if kind!='chat':
            raise ValueError('Travail inconnu.')
        current=self.app._row(case_id)
        if (payload.get('expected_revision') is not None and payload['expected_revision']!=current['revision'] or
                payload.get('source_sha256') is not None and payload['source_sha256']!=current['sha256']):
            raise ValueError('Le classeur a changé depuis l’envoi du message. Relire la sélection avant de relancer.')
        message,selection=payload['message'],payload['selection']
        cockpit_mode = payload.get('mode') == 'cockpit'
        if cockpit_mode and (type(payload.get('expected_revision')) is not int or selection.get('allow_structure')):
            raise ValueError('Le chat métier exige une révision et ne permet pas les changements de structure.')
        context=self.chat_context(case_id,selection,message)
        if cockpit_mode:
            context['editing_mode']='cockpit'
            context['editing_rules']='Valeurs des entrées métier cataloguées uniquement, avec source. Formules, résultats calculés et structure protégés.'
        with self.store.connection() as db:
            history=[json.loads(x['private_context']) for x in db.execute("SELECT private_context FROM web_messages WHERE case_id=? AND role='assistant' AND status='COMPLETE' AND private_context IS NOT NULL ORDER BY rowid DESC LIMIT 1",(case_id,))]
            if payload.get('resume_job_id'):
                resumed=db.execute("SELECT private_context FROM web_messages WHERE case_id=? AND job_id=? AND role='assistant' AND private_context IS NOT NULL ORDER BY rowid DESC LIMIT 1",(case_id,payload['resume_job_id'])).fetchone()
                if resumed:
                    history=[json.loads(resumed['private_context'])]
            db.execute('INSERT INTO web_messages VALUES(?,?,?,?,?,?,?,?,?)',(uid('msg_'),case_id,job['id'],'user',message,'[]',None,'COMPLETE',now()))
            assistant_id=uid('msg_')
            db.execute('INSERT INTO web_messages VALUES(?,?,?,?,?,?,?,?,?)',(assistant_id,case_id,job['id'],'assistant','','[]',None,'RUNNING',now()))
            self.jobs.emit(case_id,'chat',{'status':'RUNNING'},db)
        def checkpoint(provider_messages):
            with self.store.connection() as db:
                db.execute('UPDATE web_messages SET private_context=? WHERE id=?',(canonical(provider_messages),assistant_id))
        def tool_checkpoint(transcript):
            private=canonical(transcript.get('provider_messages',[]))
            fingerprint=hashlib.sha256(private.encode()).hexdigest()
            with self.store.connection() as db:
                db.execute('INSERT OR IGNORE INTO web_tool_runs VALUES(?,?,?,?,?,?,?,?)',
                           (uid('tool_'),case_id,job['id'],transcript['agent_id'],transcript.get('task',''),fingerprint,private,now()))
        def context_reader(sheet,area):
            current=self.app._row(case_id)
            if current['revision']!=context['revision'] or current['sha256']!=context['source_sha256']:
                raise ValueError('Le classeur a changé pendant la discussion. Relancer sur la version courante.')
            bounds=area.split(':')
            _,c,r=core.coord(bounds[0]);_,c2,r2=core.coord(bounds[-1])
            if (c2-c+1)*(r2-r+1)>200:
                raise ValueError('Lecture de dépendance limitée à 200 cellules.')
            return self.cells(case_id,sheet,r,c,r2-r+1,c2-c+1)
        try:
            result=self.chat.run(message,selection,context,history=history[0] if history else [],emit=progress,checkpoint=checkpoint,context_reader=context_reader,tool_checkpoint=tool_checkpoint)
            for transcript in result.get('tool_runs',[]):
                tool_checkpoint(transcript)
            if result.get('operations'):
                if cockpit_mode:
                    from .web_chat import validate_operations
                    cockpit = getattr(self, 'cockpit', None)
                    if cockpit is None:
                        raise ValueError('Le service de saisie métier est indisponible.')
                    operations = validate_operations(result['operations'], selection, context)
                    cockpit.operations(case_id, {
                        'expected_revision': context['revision'],
                        'request_id': 'chat_' + payload.get('cockpit_origin_job_id', job['id']),
                        'operations': operations,
                        'scope': {key: selection[key] for key in ('sheet', 'range', 'ranges', 'sheets') if key in selection}}, origin='chat')
                else:
                    self.add_operations(case_id,result['operations'],selection,origin='chat',expected_revision=context['revision'])
            public={k:result.get(k) for k in ('message','agents','questions')}
            with self.store.connection() as db:
                db.execute("UPDATE web_messages SET content=?,agents=?,private_context=?,status='COMPLETE' WHERE id=?",(result['message'],canonical(result.get('agents',[])),canonical(result.get('provider_messages',[])),assistant_id))
            return public
        except Exception as error:
            if getattr(error,'provider_messages',None):
                checkpoint(error.provider_messages)
            for transcript in getattr(error,'tool_runs',[]):
                tool_checkpoint(transcript)
            with self.store.connection() as db:
                db.execute("UPDATE web_messages SET status='FAILED',content=? WHERE id=?",('La réponse a été interrompue. Aucune modification de ce message n’a été appliquée.',assistant_id))
            raise
