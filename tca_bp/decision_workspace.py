"""Persistent guided workspace. Financial workbook changes always become drafts."""
from __future__ import annotations

import copy
from contextlib import closing
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import threading

from .storage import atomic_json, canonical, check_id, confined, digest, now, uid


class IntentReviewRequired(ValueError):
    pass


class DecisionWorkspace:
    SCHEMA_VERSION = 1

    def __init__(self, app, work):
        self.app, self.work, self.store = app, work, app.store
        self.lock = threading.RLock()
        with self.store.connection() as db:
            exists = db.execute("SELECT name FROM sqlite_master WHERE name='decision_migrations'").fetchone()
            version = db.execute('SELECT MAX(version) FROM decision_migrations').fetchone()[0] if exists else 0
        if not version:
            backup = self.app.data_dir / 'backups' / ('before-decision-v1-' + uid() + '.sqlite3')
            backup.parent.mkdir(parents=True, exist_ok=True)
            with self.store.connection() as source, closing(sqlite3.connect(backup)) as target:
                source.backup(target)
            with self.store.connection() as db:
                db.executescript('''
                  CREATE TABLE IF NOT EXISTS decision_migrations(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL,backup TEXT NOT NULL);
                  CREATE TABLE IF NOT EXISTS decision_objects(
                    id TEXT PRIMARY KEY,case_id TEXT NOT NULL REFERENCES cases(id),kind TEXT NOT NULL,
                    status TEXT NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
                  CREATE INDEX IF NOT EXISTS decision_objects_case ON decision_objects(case_id,kind,created_at);
                  CREATE TABLE IF NOT EXISTS decision_requests(
                    case_id TEXT NOT NULL REFERENCES cases(id),request_id TEXT NOT NULL,operation TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,status TEXT NOT NULL,result TEXT,created_at TEXT NOT NULL,
                    PRIMARY KEY(case_id,request_id));
                ''')
                db.execute('INSERT OR IGNORE INTO decision_migrations VALUES(?,?,?)', (1,now(),str(backup.relative_to(self.app.data_dir))))
        original_handler = work.jobs.handler
        def handler(job, payload, progress):
            if job['kind'].startswith('decision_'):
                return self.run_job(job, payload, progress)
            return original_handler(job,payload,progress)
        work.jobs.handler = handler

    def check_revision(self, case_id, expected):
        row = self.app._row(case_id)
        if expected is not None and (isinstance(expected,bool) or expected != row['revision']):
            raise ValueError('Le dossier a changé. Actualiser puis examiner une nouvelle proposition.')
        return row

    def objects(self, case_id, kind):
        self.app._row(case_id)
        with self.store.connection() as db:
            rows = db.execute('SELECT * FROM decision_objects WHERE case_id=? AND kind=? ORDER BY rowid DESC',(case_id,kind)).fetchall()
        return [self.public(row) for row in rows]

    @staticmethod
    def public(row):
        return {**json.loads(row['payload']), **{k:row[k] for k in ('id','case_id','kind','status','revision','created_at','updated_at')}}

    def get(self, case_id, object_id, kind=None):
        self.app._row(case_id)
        with self.store.connection() as db:
            row = db.execute('SELECT * FROM decision_objects WHERE case_id=? AND id=?',(case_id,check_id(object_id))).fetchone()
        if row is None or kind is not None and row['kind'] != kind:
            raise ValueError('Cet élément n’appartient pas à ce dossier.')
        return self.public(row)

    def save(self, case_id, kind, payload, *, status='CONFIRME', object_id=None, db=None):
        if db is None:
            with self.store.connection() as conn:
                return self.save(case_id,kind,payload,status=status,object_id=object_id,db=conn)
        row = self.app._row(case_id,db)
        object_id = check_id(object_id or uid(kind+'_'))
        previous = db.execute('SELECT case_id,kind FROM decision_objects WHERE id=?',(object_id,)).fetchone()
        if previous and (previous['case_id'] != case_id or previous['kind'] != kind):
            raise ValueError('Identifiant déjà utilisé.')
        db.execute('INSERT INTO decision_objects VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,revision=excluded.revision,payload=excluded.payload,updated_at=excluded.updated_at',
                   (object_id,case_id,kind,status,row['revision'],canonical(payload),now(),now()))
        self.work.jobs.emit(case_id,db=db)
        return self.public(db.execute('SELECT * FROM decision_objects WHERE id=?',(object_id,)).fetchone())

    def latest(self, case_id, kind, default=None):
        return next((o for o in self.objects(case_id,kind) if o['status']=='CONFIRME'),default)

    def intent(self, case_id, request_id):
        self.app._row(case_id)
        job = self.work.jobs.lookup(case_id,request_id)
        if job:
            return {'found':True,'result':{'job':job},'status':job['status']}
        with self.store.connection() as db:
            row = db.execute('SELECT * FROM decision_requests WHERE case_id=? AND request_id=?',(case_id,check_id(request_id))).fetchone()
        if not row:
            return {'found':False}
        return {'found':True,'status':row['status'],'result':json.loads(row['result']) if row['result'] else None,
                'message':'L’intention est conservée. Aucune seconde écriture ne sera lancée automatiquement.'}

    def intent_review(self,case_id,request_id):
        with self.store.connection() as db:
            row=self.app._row(case_id,db)
            intent=db.execute('SELECT * FROM decision_requests WHERE case_id=? AND request_id=?',(case_id,check_id(request_id))).fetchone()
            if not intent: raise ValueError('Intention inconnue de ce dossier.')
            draft=self.work._draft_row(case_id,db)
            objects=[dict(r) for r in db.execute('SELECT id,kind,status,updated_at FROM decision_objects WHERE case_id=? ORDER BY rowid DESC LIMIT 10',(case_id,))]
        self.app._workbook(row)
        binding={'revision':row['revision'],'sha256':row['sha256'],'intent':dict(intent),'draft':dict(draft) if draft else None,'objects':objects}
        token=hashlib.sha256(canonical(binding).encode()).hexdigest()
        count=len(json.loads(draft['payload']).get('operations',[])) if draft else 0
        summary=f"Dossier {row['name']}, révision {row['revision']}, calcul {row['calculation_status']}. Brouillon : {count} opérations ({draft['status'] if draft else 'vide'})."
        if objects: summary+=' Derniers éléments : '+', '.join(o['kind']+' — '+o['status'] for o in objects)+'.'
        return {'approval_token':token,'operation':intent['operation'],'status':intent['status'],'summary':summary,'current_revision':row['revision'],'result_available':bool(intent['result'])}

    def review_intent(self,case_id,request_id,body):
        """Acknowledge the inspected state; never replay an uncertain operation."""
        if not body.get('approval_token') or type(body.get('expected_revision')) is not int:
            raise ValueError('Examiner la révision courante et confirmer sa lecture.')
        with self.lock,self.store.case_lock(case_id),self.store.connection() as db:
            row=self.check_revision(case_id,body['expected_revision'])
            self.app._workbook(row)
            reviewed=self.intent_review(case_id,request_id)
            if body['approval_token']!=reviewed['approval_token']:
                raise ValueError('L’état à examiner a changé. Relire le dossier avant de clôturer l’intention.')
            intent=db.execute('SELECT * FROM decision_requests WHERE case_id=? AND request_id=?',(case_id,check_id(request_id))).fetchone()
            if not intent or intent['status'] not in ('PENDING','REVIEW_REQUIRED','REVIEWED'):
                raise ValueError('Cette intention ne nécessite pas de clôture manuelle. Consulter son résultat ou le travail associé.')
            self.store.history(db,case_id,'INTENTION_EXAMINEE',{'request_id':request_id,'operation':intent['operation'],'revision':row['revision'],'sha256':row['sha256'],'prior_status':intent['status'],'reexecuted':False})
            db.execute("UPDATE decision_requests SET status='REVIEWED' WHERE case_id=? AND request_id=?",(case_id,request_id))
        return {'status':'REVIEWED','request_id':request_id,'revision':row['revision'],'reexecuted':False,'message':'Intention clôturée et conservée dans l’historique. Aucune opération relancée.'}

    def request(self, case_id, operation, body, action):
        """Reserve intent before work; a crash never silently runs it again."""
        request_id = body.get('request_id')
        if not request_id:
            return action()
        check_id(request_id)
        fingerprint = hashlib.sha256(canonical([operation,{k:v for k,v in body.items() if k!='request_id'}]).encode()).hexdigest()
        with self.lock:
            with self.store.connection() as db:
                self.app._row(case_id,db)
                old = db.execute('SELECT * FROM decision_requests WHERE case_id=? AND request_id=?',(case_id,request_id)).fetchone()
                if old:
                    if old['fingerprint'] != fingerprint:
                        raise ValueError('Cet identifiant correspond à une autre opération ou à un contenu différent.')
                    if old['result']:
                        return json.loads(old['result'])
                    raise IntentReviewRequired('Intention non acquittée : examiner l’état courant avant toute nouvelle écriture.')
                if db.execute('SELECT 1 FROM web_jobs WHERE case_id=? AND request_id=?',(case_id,request_id)).fetchone():
                    raise ValueError('Cet identifiant appartient déjà à un travail.')
                db.execute('INSERT INTO decision_requests VALUES(?,?,?,?,?,?,?)',(case_id,request_id,operation,fingerprint,'PENDING',None,now()))
            try:
                result = action()
            except Exception as exc:
                with self.store.connection() as db:
                    db.execute("UPDATE decision_requests SET status='REVIEW_REQUIRED' WHERE case_id=? AND request_id=?",(case_id,request_id))
                message=str(exc) if isinstance(exc,ValueError) else 'Le traitement a été interrompu.'
                raise IntentReviewRequired(message+' L’intention reste conservée ; examiner l’état courant avant de recommencer.') from exc
            with self.store.connection() as db:
                db.execute("UPDATE decision_requests SET status='COMPLETE',result=? WHERE case_id=? AND request_id=?",(canonical(result),case_id,request_id))
            return result

    def profile(self, case_id):
        saved = self.latest(case_id,'profile')
        return saved.get('profile',{}) if saved else {'activity':'','business_model':'services','start_year':dt.date.today().year,'years':5,'activity_start_month':1,'objectives':'','modules':[]}

    def set_profile(self, case_id, body):
        profile = body.get('profile')
        if not isinstance(profile,dict):
            raise ValueError('Profil requis.')
        years,month,year = profile.get('years',5),profile.get('activity_start_month',1),profile.get('start_year',dt.date.today().year)
        if not all(type(v) is int for v in (years,month,year)) or not 1<=years<=10 or not 1<=month<=12 or not 1900<=year<=2200:
            raise ValueError('Calendrier : 1 à 10 ans, mois de démarrage entre janvier et décembre.')
        with self.store.case_lock(case_id):
            self.check_revision(case_id,body.get('expected_revision'))
            saved = self.save(case_id,'profile',{'profile':profile})
        return {'profile':profile,'saved':saved,'calendar_status':'A_APPLIQUER_AU_PREVISIONNEL'}

    def bindings(self, case_id):
        engine = self.app.engine_for_case(case_id)
        catalog = engine.catalog()
        if isinstance(catalog,dict): catalog=catalog.get('fields',[])
        bindings=[]
        for f in catalog:
            cells=f.get('cells') or [a for a,p in getattr(engine,'schema',{}).get('cells',{}).get(f['sheet'],{}).items() if p.get('field_id')==f['id']]
            for cell in cells:
                if ':' in cell: continue
                bindings.append({**f,'field_id':f['id'],'cell':cell,'value_type':f.get('kind','text')})
        return bindings

    def questionnaire(self, case_id):
        row=self.app._row(case_id)
        states=json.loads(row['field_states'])
        profile=self.profile(case_id)
        module_sheets={'sales':['Assumptions','DATA Contrats','DATA COGS','ATELIER_CIR_IS'],'staff':['Effectifs'],'investments':['DATA CAPEX'],'debt':['Financement Dette'],'grants':['SUBVENTION_INVEST'],'equity':['DATA Financement']}
        modules=[sheet for module in (profile.get('modules') or ['sales']) for sheet in module_sheets.get(module,[module])]
        engine=self.app.engine_for_case(case_id)
        fields=self.bindings(case_id)
        schema=getattr(engine,'schema',{})
        from .vendor import input_engine as core
        def read(wb,current):
            selected_rows={}
            required=set()
            for sheet,reg in schema.get('registers',{}).items():
                if sheet not in modules: continue
                occupied=[]
                for r in range(reg['start_row'],reg['end_row']+1):
                    if any(not core.blank(wb.value(sheet,c+str(r))) and wb.formula(sheet,c+str(r)) is None for c in reg['identity_columns']):
                        occupied.append(r)
                        required.update((sheet,c+str(r)) for c in reg.get('required',[]))
                free=next((r for r in range(reg['start_row'],reg['end_row']+1) if r not in occupied),None)
                selected_rows[sheet]=set(occupied+([free] if free else []))
            questions=[]
            for f in fields:
                sheet,cell=f['sheet'],f['cell']
                if sheet not in modules and sheet not in ('Control','Previsionnel'): continue
                cellrow=core.coord(cell)[2]
                if sheet in selected_rows and cellrow not in selected_rows[sheet]: continue
                value=wb.value(sheet,cell)
                formula=wb.formula(sheet,cell)
                state=states.get(sheet+'!'+cell,{})
                if formula is not None and not state: continue
                if sheet=='Assumptions' and 15<=cellrow<=27 and not cell.startswith('C'):
                    flag=wb.value(sheet,'C'+str(cellrow))
                    if flag==0 or flag is None and cellrow!=15: continue
                if sheet=='ATELIER_CIR_IS' and not state and not (143<=cellrow<=155 or cellrow==66): continue
                item={k:f.get(k) for k in ('field_id','label','sheet','cell','value_type','unit','choices','constraints')}
                item.update(value=value,status=state.get('status','HYPOTHESE' if value is not None else 'NON_RENSEIGNE'),evidence_id=state.get('evidence'),required=(sheet,cell) in required,
                            explanation=f.get('basis',''),calculated=formula is not None)
                questions.append(item)
            return questions
        questions=self.work._read(case_id,read)
        confirmed=sum(q['status']=='CONFIRME' for q in questions)
        hypotheses=sum(q['status']=='HYPOTHESE' for q in questions)
        return {'questions':questions,'progress':{'total':len(questions),'confirmed':confirmed,'hypotheses':hypotheses,'missing':len(questions)-confirmed-hypotheses}}

    def answers(self, case_id, body, *, origin='manual'):
        self.check_revision(case_id,body.get('expected_revision'))
        bindings=self.bindings(case_id)
        updates=[]
        for answer in body.get('answers',[]):
            candidates=[b for b in bindings if b['field_id']==answer.get('field_id') and (not answer.get('cell') or b['cell']==answer['cell']) and (not answer.get('sheet') or b['sheet']==answer['sheet'])]
            if len(candidates)!=1:
                raise ValueError('Choisir une cellule précise pour ce champ ou ce registre.')
            field=candidates[0]
            value=answer.get('value')
            if field.get('kind')=='date' and isinstance(value,str) and value:
                try: date=dt.date.fromisoformat(value)
                except ValueError: raise ValueError('Date attendue au format AAAA-MM-JJ.')
                value=date.isoformat()  # native preparation performs the 1900/1904 conversion once.
            update={'type':'set_value','sheet':field['sheet'],'cell':field['cell'],'value':value,'status':answer.get('status','CONFIRME'),'reason':answer.get('reason','Réponse au questionnaire')}
            if answer.get('evidence_id'): update['evidence_id']=answer['evidence_id']
            updates.append(update)
        return self.propose(case_id,updates,body.get('expected_revision'),origin=origin)

    def propose_profile(self,case_id,body):
        profile=self.profile(case_id)
        source=self.app.add_source(case_id,text=canonical(profile),title='Profil et calendrier confirmés')
        return self.answers(case_id,{'expected_revision':body.get('expected_revision'),'answers':[
            {'field_id':'model_start_date','value':f"{profile['start_year']:04d}-01-01",'evidence_id':source['id']},
            {'field_id':'active_horizon_years','value':profile['years'],'evidence_id':source['id']}]})

    def propose_wacc_migration(self,case_id,body):
        from .wacc_fingerprint_migration import plan_fingerprint_migration,REASON
        row=self.check_revision(case_id,body.get('expected_revision'))
        if self.work.draft(case_id).get('operations'):
            raise ValueError('Terminer le brouillon courant avant la migration des contrôles WACC.')
        source=self.app.add_source(case_id,text=REASON,title='Migration des contrôles de fraîcheur WACC')
        plan=plan_fingerprint_migration(self.app.engine_for_case(case_id),self.app._workbook(row),source['id'])
        if plan['status']=='ALREADY_MIGRATED': return {'status':'ALREADY_MIGRATED','operations':[]}
        return self.propose(case_id,plan['operations'],row['revision'])

    def propose_dcf_calendar_migration(self,case_id,body):
        from .dcf_calendar_migration import plan_calendar_migration,REASON
        row=self.check_revision(case_id,body.get('expected_revision'))
        if self.work.draft(case_id).get('operations'):
            raise ValueError('Terminer le brouillon courant avant la migration du calendrier de valorisation.')
        source=self.app.add_source(case_id,text=REASON,title='Migration explicite du calendrier DCF')
        plan=plan_calendar_migration(self.app.engine_for_case(case_id),self.app._workbook(row),source['id'])
        if plan['status']=='ALREADY_MIGRATED': return {'status':'ALREADY_MIGRATED','operations':[]}
        return self.propose(case_id,plan['operations'],row['revision'])

    def propose_fiscal_calendar_migration(self,case_id,body):
        from .fiscal_calendar_migration import plan_fiscal_calendar_migration,REASON
        row=self.check_revision(case_id,body.get('expected_revision'))
        if self.work.draft(case_id).get('operations'):
            raise ValueError('Terminer le brouillon courant avant la migration des agrégats de fiscalité et de trésorerie.')
        source=self.app.add_source(case_id,text=REASON,title='Migration explicite des agrégats annuels fiscaux et de trésorerie')
        plan=plan_fiscal_calendar_migration(self.app.engine_for_case(case_id),self.app._workbook(row),source['id'])
        if plan['status']=='ALREADY_MIGRATED': return {'status':'ALREADY_MIGRATED','operations':[]}
        return self.propose(case_id,plan['operations'],row['revision'])

    def qualification_preview(self,case_id,body):
        declaration=self.app.normalize_qualification(body.get('declaration'))
        self.source(case_id,declaration['evidence'])
        return self.preview_object(case_id,'qualification',{'declaration':declaration},body.get('expected_revision'))

    def qualification_apply(self,case_id,body):
        previews=self.objects(case_id,'qualification_preview')
        preview=next((p for p in previews if p.get('approval_token')==body.get('approval_token')),None)
        if not preview: raise ValueError('Aperçu de qualification requis.')
        def record(row,db):
            from .model_registry import model_pin
            declaration=self.app.normalize_qualification(preview['binding']['value']['declaration'])
            self.source(case_id,declaration['evidence'])
            item={**declaration,**model_pin(row),'case_id':case_id,'client_id':row['client_id'],'recorded_at':now()}
            self.store.history(db,case_id,'QUALIFICATION_DECLAREE',item)
        adopted=self.adopt_object(case_id,'qualification',body,before_adopt=record)
        assessment=self.app.qualifications(case_id)
        return {**adopted,'assessment':assessment}

    def qualification_view(self,case_id):
        from .qualifications import MODULES
        row=self.app._row(case_id)
        basis=self.app._qualification_basis(row)
        case=self.app.get_case(case_id)
        labels={'CA':'Ventes et chiffre d’affaires','COGS':'Coûts directs','STOCK':'Stocks','CIR':'Crédit d’impôt recherche','REGLES_FISCALES':'Règles fiscales applicables','BFR_TERMINAL':'Besoin en fonds de roulement terminal','DATA Contrats':'Contrats clients','Effectifs':'Salariés','DATA CAPEX':'Investissements','DATA Financement':'Apports en capital','Financement Dette':'Dette financière','SUBVENTION_INVEST':'Subventions d’investissement'}
        scopes=case.get('qualified_availability',{})
        questions=[q for scope in scopes.values() for q in scope.get('blockers',[])+scope.get('hypotheses',[])]
        return {'modules':[{'id':m,'label':labels.get(m,m)} for m in MODULES],'declarations':basis['declarations'],'scopes':scopes,'questions':questions}

    def registers(self,case_id):
        engine=self.app.engine_for_case(case_id)
        fields=self.bindings(case_id)
        schema=getattr(engine,'schema',{})
        from .vendor import input_engine as core
        def read(wb,row):
            result=[]
            for sheet,reg in schema.get('registers',{}).items():
                free=next((r for r in [*range(reg['start_row'],reg['end_row']+1),*reg.get('extra_rows',[])] if not any(not core.blank(wb.value(sheet,c+str(r))) and wb.formula(sheet,c+str(r)) is None for c in reg['identity_columns'])),None)
                if free is None:
                    first=reg['start_row']
                else: first=free
                row_fields=[{**{k:f.get(k) for k in ('field_id','label','value_type','choices','unit')},'required':core.coord(f['cell'])[0] in reg.get('required',[]),'default':wb.value(sheet,f['cell']),'calculated':wb.formula(sheet,f['cell']) is not None} for f in fields if f['sheet']==sheet and core.coord(f['cell'])[2]==first]
                logical=getattr(engine,'profile',{}).get('sheets',[])
                original=next((r.get('original_name') for r in logical if r.get('name')==sheet),sheet)
                questions=[question for saved in self.objects(case_id,'record_questions') if saved.get('sheet')==sheet and saved.get('status')!='RESOLVED' for question in saved.get('questions',[])][:100]
                result.append({'id':sheet,'sheet':sheet,'label':sheet,'first_free_row':free,'fields':row_fields,'can_extend':original=='Effectifs','questions':questions})
            return {'registers':result}
        return self.work._read(case_id,read)

    def prepare_record(self,case_id,sheet,body):
        row=self.check_revision(case_id,body.get('expected_revision'))
        source=body.get('evidence_id'); self.source(case_id,source)
        planned=self.app._coordinator_for_case(case_id).plan_record(self.app._workbook(row),sheet,body.get('values',{}),source)
        if planned.get('questions') or planned.get('status')!='READY':
            self.save(case_id,'record_questions',planned,status='A_COMPLETER')
            return planned
        updates=[{'type':'set_value','sheet':u['sheet'],'cell':u['cell'],'value':u['value'],'evidence_id':u.get('evidence',source),'reason':u.get('reason','Ligne métier documentée'),'status':u.get('status','HYPOTHESE')} for u in planned['updates']]
        dates={(f['sheet'],f['cell']) for f in self.bindings(case_id) if f.get('kind')=='date'}
        for update in updates:
            if (update['sheet'],update['cell']) in dates and isinstance(update['value'],str) and update['value']:
                try: date=dt.date.fromisoformat(update['value'])
                except ValueError: raise ValueError('Date de ligne métier attendue au format AAAA-MM-JJ.')
                update['value']=date.isoformat()
        # The coordinator validates business completeness; the native preview
        # remains the only path to adopt the proposed row in the workbook.
        draft=self.propose(case_id,updates,body.get('expected_revision'))
        with self.store.connection() as db:
            for saved in self.objects(case_id,'record_questions'):
                if saved.get('sheet')==sheet:
                    db.execute("UPDATE decision_objects SET status='RESOLVED' WHERE id=?",(saved['id'],))
        return draft

    def propose(self, case_id, updates, expected_revision=None, *, origin='manual'):
        if not updates: raise ValueError('Aucune modification à proposer.')
        sheets=list(dict.fromkeys(op.get('sheet',op.get('name')) for op in updates))
        return self.work.add_operations(case_id,updates,{'sheet':sheets[0],'sheets':sheets,'allow_structure':any(op['type'] not in ('set_value','set_formula') for op in updates)},expected_revision=expected_revision,origin=origin)

    def source(self, case_id, source_id):
        self.app.source_text(case_id,source_id)  # verifies ownership and full digest
        with self.store.connection() as db:
            row=db.execute('SELECT * FROM sources WHERE id=? AND case_id=?',(source_id,case_id)).fetchone()
        return dict(row)

    def extract(self, case_id, payload, progress):
        from .decision_documents import extract_document
        source=self.source(case_id,payload['source_id'])
        progress({'message':'Lecture locale du document et de ses tableaux.'})
        if source['path']:
            result=extract_document(confined(self.store.case_dir(case_id),source['path']),numeric_locale=payload.get('numeric_locale','fr'))
        else:
            result={'source_sha256':source['sha256'],'blocks':[{'text':source['text']}],'facts':[],'warnings':[],'status':'A_CONFIRMER'}
        if result['source_sha256']!=source['sha256']:
            raise ValueError('Le document a changé pendant la lecture.')
        text='\n'.join(b.get('text','') for b in result.get('blocks',[]))[:500000]
        saved=self.save(case_id,'extraction',{**result,'text':text,'source_id':source['id'],'source_title':source['title']},status='A_CONFIRMER')
        with self.store.connection() as db:
            db.execute('UPDATE sources SET text=? WHERE id=? AND case_id=?',(text,source['id'],case_id))
            self.store.history(db,case_id,'EXTRACTION_DOCUMENT',{'extraction_id':saved['id'],'source_id':source['id'],'source_sha256':source['sha256']})
        return saved

    def extraction_propose(self,case_id,object_id,body):
        extraction=self.get(case_id,object_id,'extraction')
        self.source(case_id,extraction['source_id'])
        updates=[]
        facts=extraction.get('facts',[])
        for selected in body.get('facts',[]):
            fact=next((f for i,f in enumerate(facts) if str(f.get('id',i))==str(selected.get('id',selected.get('fact_id')))),None)
            if fact is None: raise ValueError('Donnée extraite inconnue.')
            value=selected.get('value',fact.get('normalized_value',fact.get('value')))
            if 'value' not in selected and fact.get('normalized_value') is not None:
                from decimal import Decimal
                value=float(Decimal(fact['normalized_value']))
            updates.append({'type':'set_value','sheet':selected['sheet'],'cell':selected['cell'],'value':value,'evidence_id':extraction['source_id'],'status':'CONFIRME','reason':'Donnée extraite confirmée : '+str(fact.get('location',fact.get('locator',fact.get('cell',fact.get('page','')))))})
        return self.propose(case_id,updates,body.get('expected_revision'))

    def preview_object(self,case_id,kind,payload,expected_revision=None):
        row=self.check_revision(case_id,expected_revision)
        prior=self.latest(case_id,kind)
        binding={'revision':row['revision'],'sha256':row['sha256'],'previous_id':prior['id'] if prior else None,'value':payload}
        token=hashlib.sha256(canonical([case_id,kind,binding]).encode()).hexdigest()
        return self.save(case_id,kind+'_preview',{**payload,'approval_token':token,'binding':binding},status='READY')

    def adopt_object(self,case_id,kind,body,*,before_adopt=None):
        token=body.get('approval_token')
        previews=self.objects(case_id,kind+'_preview')
        preview=next((p for p in previews if token and p.get('approval_token')==token),None)
        if not preview: raise ValueError('Aperçu approuvé requis.')
        with self.store.case_lock(case_id), self.store.connection() as db:
            already=db.execute('SELECT * FROM decision_objects WHERE case_id=? AND kind=? AND id=?',(case_id,kind,preview['id']+'_adopted')).fetchone()
            if already: return self.public(already)
            row=self.check_revision(case_id,preview['binding']['revision'])
            self.app._workbook(row)
            prior=self.latest(case_id,kind)
            if row['sha256']!=preview['binding']['sha256'] or (prior['id'] if prior else None)!=preview['binding']['previous_id']:
                raise ValueError('Aperçu périmé : préparer une nouvelle comparaison.')
            if before_adopt is not None:
                before_adopt(row,db)
            result=self.save(case_id,kind,preview['binding']['value'],object_id=preview['id']+'_adopted',db=db)
            self.store.history(db,case_id,'ADOPTION_'+kind.upper(),{'object_id':result['id'],'approval_token':token,'previous_id':preview['binding']['previous_id']})
        return result

    def capitalization(self,case_id,body):
        from .decision_finance import calculate_cap_table
        shareholders=body.get('shareholders',[])
        rounds=body.get('rounds',[])
        from decimal import Decimal
        normalized=[{**r,'pool_percent':str(Decimal(str(r.get('pool_percent',0)))/100)} for r in rounds]
        result=calculate_cap_table(shareholders,normalized,initial_pool_shares=body.get('initial_pool_shares',0))
        return self.preview_object(case_id,'capitalization',{'shareholders':shareholders,'rounds':rounds,'initial_pool_shares':body.get('initial_pool_shares',0),'result':result},body.get('expected_revision'))

    def storage(self,case_id):
        root=self.store.case_dir(case_id)
        used=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
        free=shutil.disk_usage(root).free
        return {'used_bytes':used,'free_bytes':free,'retention':'Versions, sources et preuves conservées.'}

    def require_space(self,case_id,copies=1):
        row,path=self.work._workbook(case_id)
        free=shutil.disk_usage(path.parent).free
        required=path.stat().st_size*(copies+3)+256*1024*1024
        if free<required: raise ValueError('Espace disque insuffisant pour ce traitement et ses preuves.')
        return {'required_bytes':required,'free_bytes':free}

    def submit(self,case_id,kind,body):
        supplied={k:v for k,v in body.items() if k!='request_id'}
        if body.get('request_id'):
            with self.store.connection() as db:
                previous=db.execute('SELECT * FROM web_jobs WHERE case_id=? AND request_id=?',(case_id,body['request_id'])).fetchone()
            if previous:
                original=json.loads(previous['payload'])
                if previous['kind']!='decision_'+kind or original.get('request_body')!=supplied:
                    raise ValueError('Cette demande existe avec un contenu différent.')
                return {'job':self.work.jobs.public(previous),'replayed':True}
        row=self.check_revision(case_id,body.get('expected_revision'))
        self.require_space(case_id,1)
        payload={**supplied,'expected_revision':row['revision'],'source_sha256':row['sha256'],'request_body':supplied}
        return self.work.jobs.submit(case_id,'decision_'+kind,payload,body.get('request_id'))

    def run_job(self,job,payload,progress):
        case_id=job['case_id']
        if job['kind']=='decision_extract': return self.extract(case_id,payload,progress)
        if job['kind']=='decision_cockpit_simulation':
            from .cockpit_simulations import CockpitSimulations
            return CockpitSimulations(self).run(job,payload,progress)
        current=self.check_revision(case_id,payload.get('expected_revision'))
        if payload.get('source_sha256') and current['sha256']!=payload['source_sha256']:
            raise ValueError('La copie de référence du traitement a changé.')
        if job['kind']=='decision_report': return self.build_report(case_id,payload,progress)
        if job['kind']=='decision_goal': return self.goal(case_id,payload,progress)
        if job['kind']=='decision_sensitivity':
            campaign_id=payload.get('campaign_id') or 'campaign_'+job['id']
            if not payload.get('campaign_id'):
                self.save(case_id,'sensitivity',{'axes':payload.get('axes',[]),'metric':payload.get('metric','cash_min'),'points':[],'base_sha256':self.app._row(case_id)['sha256']},status='RUNNING',object_id=campaign_id)
                payload={**payload,'campaign_id':campaign_id}
                with self.store.connection() as db:
                    db.execute('UPDATE web_jobs SET payload=? WHERE id=?',(canonical(payload),job['id']))
            else:
                campaign=self.get(case_id,campaign_id,'sensitivity')
                self.save(case_id,'sensitivity',{**campaign,'cancel_requested':False},status='RUNNING',object_id=campaign_id)
            return self.sensitivity(case_id,payload,progress)
        raise ValueError('Traitement métier inconnu.')

    def workshop(self,case_id):
        row=self.app._row(case_id)
        return {'profile':self.profile(case_id),'progress':self.questionnaire(case_id)['progress'],'revision':row['revision'],'calculation_status':row['calculation_status'],'metrics':self.metrics(case_id),'storage':self.storage(case_id)}

    # Financial and export operations live separately to keep the transaction
    # primitives auditable and reusable by HTTP and MCP.
    def metrics(self,case_id,period=None):
        from .decision_model import read_metrics
        return read_metrics(self,case_id,period)

    def create_scenario(self,case_id,body):
        from .decision_model import create_scenario
        return create_scenario(self,case_id,body)

    def goal(self,case_id,payload,progress):
        from .decision_model import run_goal
        return run_goal(self,case_id,payload,progress)

    def sensitivity(self,case_id,payload,progress):
        from .decision_model import run_sensitivity
        return run_sensitivity(self,case_id,payload,progress)

    def build_report(self,case_id,payload,progress):
        from .decision_exports import build_report
        return build_report(self,case_id,payload,progress)
