"""Pinned scenario copies and financial observations from the current workbook."""
from __future__ import annotations
import copy
import datetime as dt
from decimal import Decimal
import json
import math
from pathlib import Path
import shutil

from .model_registry import model_pin
from .storage import canonical, confined, digest, now, uid

ANCHORS={
    'revenue':('Chiffre d’affaires','Compte de Résultat','D7'),
    'gross_margin':('Marge brute','Compte de Résultat','D25'),
    'ebitda':('EBE','Compte de Résultat','D69'),
    'net_income':('Résultat net','Compte de Résultat','D85'),
    'valuation':('Valorisation DCF avant investissement','Valorisation','D40'),
    'valuation_vc':('Valorisation VC avant investissement','Valorisation','D50'),
}

def location_resolver(engine):
    """Use one isolated profile snapshot for a financial read operation.

    ProfileEngine.profile defensively copies the complete business profile.
    Taking that copy per cell made a monthly comparison prohibitively slow.
    Resolution still uses the public profile and the normal verified engine;
    no shared mutable profile or file-integrity cache is introduced.
    """
    from .web_model_profile import map_location
    profile=getattr(engine,'profile',None)
    def resolve(sheet,cell):
        if profile:
            mapped=map_location(profile,sheet,cell)
            if not mapped: raise ValueError('Une référence financière indispensable a été supprimée.')
            return mapped['sheet'],mapped['cell']
        return sheet,cell
    return resolve


def location(engine,sheet,cell):
    return location_resolver(engine)(sheet,cell)

def read_series(d,case_id):
    engine=d.app.engine_for_case(case_id)
    case=d.app.get_case(case_id)
    resolve=location_resolver(engine)
    from .vendor import input_engine as core
    def read(wb,row):
        def value(sheet,cell):
            s,c=resolve(sheet,cell)
            try: return wb.value(s,c)
            except (KeyError,ValueError): return None
        start=value('Control','C10')
        years=value('Control','C59')
        years=int(years) if isinstance(years,(int,float)) and 1<=years<=10 else d.profile(case_id).get('years',5)
        year=((dt.datetime(1904,1,1) if wb.date1904 else dt.datetime(1899,12,30))+dt.timedelta(days=start)).year if isinstance(start,(int,float)) else d.profile(case_id).get('start_year',dt.date.today().year)
        periods=[f'{year+i//12:04d}-{i%12+1:02d}' for i in range(years*12)]
        series=[]
        # Revenue's three totals distinguish recognition, invoices and customer
        # cash. Consolidated row 88 is invoicing, not recognised revenue.
        specs=[('cash','Trésorerie mensuelle','Modèle financier',321,20,'CASH'),
               ('revenue','Chiffre d’affaires reconnu','Revenue',282,16,'CA'),
               ('receipts','Encaissements totaux','Modèle financier',301,20,'CASH'),
               ('payments','Décaissements totaux','Modèle financier',320,20,'CASH'),
               ('billed_revenue','Facturation clients','Revenue',283,16,'CA'),
               ('customer_receipts','Encaissements clients','Revenue',284,16,'CASH')]
        for key,label,sheet,cellrow,first_column,qualification in specs:
            addresses=[resolve(sheet,core.colname(first_column+i)+str(cellrow)) for i in range(len(periods))]
            values=[value(sheet,core.colname(first_column+i)+str(cellrow)) for i in range(len(periods))]
            scope=case.get('qualified_availability',{}).get(qualification,{})
            usable=case.get('outputs_current',False) and scope.get('scenario_ready',False)
            series.append({'id':key,'label':label,'unit':'EUR','categories':periods,'values':[v if usable and type(v) in (int,float) and math.isfinite(v) else None for v in values],
                           'status':scope.get('status','INDISPONIBLE'),'qualification':scope,
                           'case_id':case_id,'revision':case.get('revision'),
                           'sources':[{'sheet':s,'cell':c} for s,c in addresses]})
        return series
    return d.work._read(case_id,read)

def read_metrics(d,case_id,period=None):
    engine=d.app.engine_for_case(case_id)
    case=d.app.get_case(case_id)
    resolve=location_resolver(engine)
    current=case.get('outputs_current',False)
    series=read_series(d,case_id)
    periods=series[0]['categories']
    if period is not None and period not in periods: raise ValueError('La période cible sort du calendrier du dossier.')
    year=period[:4] if period else periods[0][:4]
    year_offset=int(year)-int(periods[0][:4])
    def read(wb,row):
        results=[]
        for key,(label,sheet,cell) in ANCHORS.items():
            if not key.startswith('valuation'):
                from .vendor import input_engine as core
                cell=core.colname(4+year_offset)+str(core.coord(cell)[2])
            s,c=resolve(sheet,cell)
            try: value=wb.value(s,c)
            except (KeyError,ValueError): value=None
            numeric=type(value) in (int,float) and math.isfinite(value)
            scope=case.get('qualified_availability',{}).get('DCF' if key.startswith('valuation') else 'CA' if key=='revenue' else 'COGS' if key=='gross_margin' else 'CASH',{})
            usable=current and numeric and scope.get('scenario_ready',False)
            results.append({'id':key,'label':label+(' — '+year if not key.startswith('valuation') else ''),'period':year if not key.startswith('valuation') else 'horizon','value':value if usable else None,'cached_value':value if numeric else None,'unit':'EUR','status':scope.get('status','A_COMPLETER_OU_RECALCULER'),'qualification':scope,'sheet':s,'cell':c})
        return results
    metrics=d.work._read(case_id,read)
    cash=next(s for s in series if s['id']=='cash')
    count=periods.index(period)+1 if period else len(periods)
    values=cash['values'][:count]
    complete=current and bool(values) and all(v is not None for v in values)
    low=min(values) if complete else None
    first=next((p for p,v in zip(cash['categories'][:count],values) if v is not None and v<0),None) if complete else None
    metrics.extend([{'id':'cash_min','label':'Point bas mensuel de trésorerie','value':low,'unit':'EUR','status':'CALCULE' if complete else 'A_COMPLETER_OU_RECALCULER'},
                    {'id':'cash_break_date','label':'Premier mois de trésorerie négative','value':first,'unit':'mois','status':'CALCULE' if complete else 'A_COMPLETER_OU_RECALCULER'},
                    {'id':'financing_need','label':'Besoin supplémentaire au point bas','value':max(0,-low) if complete else None,'unit':'EUR','status':'CALCULE' if complete else 'A_COMPLETER_OU_RECALCULER'}])
    return metrics


def read_annual_metrics(d,case_id):
    """Read all active financial years in one workbook pass, without extrapolation."""
    engine=d.app.engine_for_case(case_id)
    case=d.app.get_case(case_id)
    resolve=location_resolver(engine)
    series=read_series(d,case_id)
    years=list(dict.fromkeys(p[:4] for p in series[0]['categories']))
    from .vendor import input_engine as core
    def read(wb,row):
        output=[]
        for index,year in enumerate(years):
            for key,(label,sheet,anchor) in ANCHORS.items():
                if key.startswith('valuation'): continue
                target=core.colname(4+index)+str(core.coord(anchor)[2])
                s,c=resolve(sheet,target)
                try: value=wb.value(s,c)
                except (ValueError,KeyError): value=None
                qualification=case.get('qualified_availability',{}).get('CA' if key=='revenue' else 'COGS' if key=='gross_margin' else 'CASH',{})
                available=case.get('outputs_current',False) and qualification.get('scenario_ready',False) and type(value) in (int,float) and math.isfinite(value)
                output.append({'id':key+'_'+year,'metric':key,'label':label+' — '+year,'period':year,'value':value if available else None,'unit':'EUR','available':available,'status':qualification.get('status','INDISPONIBLE'),'sheet':s,'cell':c})
        return output
    return d.work._read(case_id,read)

def create_scenario(d,case_id,body):
    name=body.get('name','').strip()
    if not name or len(name)>160: raise ValueError('Nom de scénario requis (160 caractères maximum).')
    d.require_space(case_id,1)
    child_id=uid('scenario_')
    folder=d.store.case_dir(child_id)
    with d.store.case_lock(case_id):
        parent=d.check_revision(case_id,body.get('expected_revision'))
        source=d.app._workbook(parent)
        pin=model_pin(parent)
        folder.mkdir(parents=True,exist_ok=False)
        try:
            (folder/'versions').mkdir()
            target=folder/'versions'/'v0000.xlsm'
            shutil.copyfile(source,target)
            if digest(target)!=parent['sha256']: raise ValueError('La copie du scénario ne correspond pas à sa révision de départ.')
            with d.store.connection() as db:
                db.execute('BEGIN IMMEDIATE')
                db.execute('INSERT INTO cases(id,client_id,name,model_id,revision,workbook,sha256,calculation_status,created_at,updated_at,model_ref,template_sha256,schema_sha256,field_states) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (child_id,parent['client_id'],name,pin['model_id'],0,'versions/v0000.xlsm',parent['sha256'],'A_RECALCULER',now(),now(),pin['model_ref'],pin['template_sha256'],pin['schema_sha256'],'{}'))
                source_map={}
                for src in db.execute('SELECT * FROM sources WHERE case_id=?',(case_id,)).fetchall():
                    d.app.source_text(case_id,src['id'])
                    new_id=uid('source_'); source_map[src['id']]=new_id
                    relative=None
                    if src['path']:
                        relative='sources/'+new_id+Path(src['path']).suffix
                        dest=confined(folder,relative); dest.parent.mkdir(exist_ok=True)
                        shutil.copyfile(confined(d.store.case_dir(case_id),src['path']),dest)
                        if digest(dest)!=src['sha256']: raise ValueError('Une source a changé pendant la duplication.')
                    db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?)',(new_id,child_id,src['title'],relative,src['text'],src['sha256'],src['kind'],src['created_at']))
                states=json.loads(parent['field_states'])
                for state in states.values():
                    for key in ('evidence','evidence_id','source'):
                        if state.get(key) in source_map: state[key]=source_map[state[key]]
                db.execute('UPDATE cases SET field_states=? WHERE id=?',(canonical(states),child_id))
                provenance={'case_id':case_id,'revision':parent['revision'],'sha256':parent['sha256'],'sources':source_map}
                d.store.history(db,child_id,'CREATION',{**pin,'revision':0,'output_sha256':parent['sha256'],'origin':provenance})
                declarations={}
                for event in db.execute("SELECT details FROM history WHERE case_id=? AND kind='QUALIFICATION_DECLAREE' ORDER BY rowid",(case_id,)).fetchall():
                    declaration=json.loads(event['details'])
                    declarations[declaration['module']]=declaration
                for declaration in declarations.values():
                    # Documentary decisions follow their exact model and copied
                    # evidence. A calculation/convergence proof never follows.
                    if any(declaration.get(k)!=v for k,v in pin.items()): continue
                    if declaration.get('case_id')!=case_id or declaration.get('client_id')!=parent['client_id']: continue
                    if declaration.get('evidence') not in source_map: continue
                    inherited={**declaration,'case_id':child_id,'evidence':source_map[declaration['evidence']],
                               'recorded_at':now(),'origin':provenance}
                    d.store.history(db,child_id,'QUALIFICATION_DECLAREE',inherited)
                d.work._snapshot_version(d.app._row(child_id,db),db,'SCENARIO')
                d.save(child_id,'profile',{'profile':d.profile(case_id)},db=db)
                scenario=d.save(case_id,'scenario',{'name':name,'scenario_case_id':child_id,'purpose':body.get('purpose','user'),'base_revision':parent['revision'],'base_sha256':parent['sha256'],'hypotheses':body.get('hypotheses',[]),'origin':provenance},db=db)
            return {**scenario,'case_id':child_id,'parent_case_id':case_id}
        except Exception:
            with d.store.connection() as db:
                exists=db.execute('SELECT 1 FROM cases WHERE id=?',(child_id,)).fetchone()
            if not exists and folder.resolve().is_relative_to((d.app.data_dir/'dossiers').resolve()): shutil.rmtree(folder)
            raise

def scenario_list(d,case_id):
    return [{**s,'parent_case_id':case_id,'case_id':s['scenario_case_id']} for s in d.objects(case_id,'scenario') if s.get('purpose','user')=='user']

def _lever(d,case_id,payload):
    candidates=[f for f in d.bindings(case_id) if f['field_id']==payload.get('field_id') and (not payload.get('sheet') or f['sheet']==payload['sheet']) and (not payload.get('cell') or f['cell']==payload['cell'])]
    if len(candidates)!=1: raise ValueError('Choisir un champ et une cellule non ambigus pour le levier.')
    lever=candidates[0]
    if lever.get('kind',lever.get('value_type')) not in ('number','integer','percent'):
        raise ValueError('Le levier doit être une entrée numérique, sans date ni choix fermé.')
    if d.work._read(case_id,lambda wb,row:wb.formula(lever['sheet'],lever['cell'])) is not None:
        raise ValueError('Choisir une entrée du modèle ; une formule ne peut pas être remplacée par le solveur.')
    if 'wacc' in (lever['field_id']+lever.get('label','')).lower(): raise ValueError('Le WACC ne peut pas être ajusté par une recherche d’objectif.')
    if payload.get('metric') not in ('cash_min','net_income','valuation','revenue'): raise ValueError('Indicateur cible inconnu.')
    return lever

def evaluate_copy(d,case_id,lever,value,name,progress,period=None,base_revision=None,target_metric=None):
    scenario=create_scenario(d,case_id,{'name':name,'purpose':'goal_trial','expected_revision':base_revision})
    child=scenario['case_id']
    draft=d.propose(child,[{'type':'set_value','sheet':lever['sheet'],'cell':lever['cell'],'value':float(value),'reason':name,'status':'HYPOTHESE'}],0)
    preview=d.work.preview(child,draft['id'],progress)
    d.work.apply(child,draft['id'],preview['approval_token'])
    d.app.recalculate(child)
    if target_metric=='valuation':
        progress({'message':'Résolution WACC et vérification de la valorisation du scénario.'})
        d.app.solve_wacc(child)
    return scenario,d.metrics(child,period)

def run_goal(d,case_id,payload,progress):
    from .decision_finance import solve_single_lever
    lever=_lever(d,case_id,payload)
    if payload.get('period') and payload['metric']=='valuation': raise ValueError('La valorisation porte sur l’horizon et le closing du modèle. Laisser la période vide.')
    initial=d.metrics(case_id,payload.get('period'))
    if next((m.get('value') for m in initial if m['id']==payload['metric']),None) is None:
        raise ValueError('Qualifier et calculer l’indicateur cible avant la recherche d’objectif.')
    base=d.check_revision(case_id,payload.get('expected_revision'))
    limit=min(30,max(3,int(payload.get('max_evaluations',16))))
    d.require_space(case_id,limit*4)
    trials=[]
    def evaluate(value):
        if d.work.jobs.stop.is_set(): raise ValueError('Recherche interrompue. Les scénarios calculés restent conservés.')
        progress({'message':f'Recherche : essai {len(trials)+1}/{limit}','lever':str(value)})
        current=d.check_revision(case_id,base['revision'])
        if current['sha256']!=base['sha256']: raise ValueError('La référence a changé pendant la recherche. Les essais sont conservés.')
        scenario,metrics=evaluate_copy(d,case_id,lever,value,'Objectif — '+str(value),progress,payload.get('period'),base['revision'],payload['metric'])
        metric=next(m for m in metrics if m['id']==payload['metric'])
        if metric['value'] is None: raise ValueError('Cible non calculable avec les informations actuelles. Compléter et recalculer le scénario.')
        trial={'lever':str(value),'value':metric['value'],'case_id':scenario['case_id'],'metrics':metrics}
        trials.append(trial)
        d.save(case_id,'goal_trial',trial)
        return trial
    result=solve_single_lever(evaluate,payload['target'],payload['lower'],payload['upper'],tolerance=payload.get('tolerance',1),max_evaluations=limit,
                             integer_lever=lever.get('kind',lever.get('value_type'))=='integer')
    return d.save(case_id,'goal',{'request':payload,'result':result,'trials':trials,'applied':False})

def run_sensitivity(d,case_id,payload,progress):
    axes=payload.get('axes',[])
    if not 1<=len(axes)<=2: raise ValueError('Choisir un ou deux axes de sensibilité.')
    import itertools
    levers=[_lever(d,case_id,{**axis,'metric':payload.get('metric','cash_min')}) for axis in axes]
    values=[axis.get('values',[]) for axis in axes]
    if any(not isinstance(v,list) or not 2<=len(v)<=20 for v in values) or math.prod(map(len,values))>100: raise ValueError('Campagne limitée à 100 points, avec 2 à 20 valeurs par axe.')
    if any(type(v) not in (int,float) or not math.isfinite(v) for axis in values for v in axis):
        raise ValueError('Chaque valeur d’axe doit être un nombre JSON fini.')
    if any(lever.get('kind',lever.get('value_type'))=='integer' and any(v!=int(v) for v in axis)
           for lever,axis in zip(levers,values)):
        raise ValueError('Un axe portant sur une entrée entière exige des valeurs entières.')
    if len({(f['sheet'],f['cell']) for f in levers})!=len(levers):
        raise ValueError('Deux axes doivent agir sur deux entrées distinctes.')
    if next((m.get('value') for m in d.metrics(case_id) if m['id']==payload.get('metric','cash_min')),None) is None:
        raise ValueError('Qualifier et calculer l’indicateur cible avant la campagne.')
    d.require_space(case_id,math.prod(map(len,values))*4)
    metric=payload.get('metric','cash_min')
    campaign=d.get(case_id,payload['campaign_id'],'sensitivity') if payload.get('campaign_id') else d.save(case_id,'sensitivity',{'axes':axes,'metric':metric,'points':[],'base_sha256':d.app._row(case_id)['sha256']},status='RUNNING')
    if campaign.get('axes')!=axes or campaign.get('metric','cash_min')!=metric:
        raise ValueError('Les axes et l’indicateur d’une campagne sont immuables. Créer une nouvelle campagne pour les modifier.')
    if campaign['base_sha256']!=d.app._row(case_id)['sha256']: raise ValueError('La révision de départ de cette campagne a changé.')
    points=campaign['points']
    for values_at_point in itertools.product(*values):
        if any(p['values']==list(values_at_point) for p in points): continue
        current=d.get(case_id,campaign['id'],'sensitivity')
        if current.get('cancel_requested') or d.work.jobs.stop.is_set():
            return d.save(case_id,'sensitivity',{**campaign,'points':points},status='INTERRUPTED',object_id=campaign['id'])
        if d.app._row(case_id)['sha256']!=campaign['base_sha256']: raise ValueError('La référence a changé pendant la campagne. Les points précédents sont conservés.')
        scenario=create_scenario(d,case_id,{'name':'Sensibilité '+', '.join(map(str,values_at_point)),'purpose':'sensitivity_trial','expected_revision':campaign['revision']})
        child=scenario['case_id']
        updates=[{'type':'set_value','sheet':lever['sheet'],'cell':lever['cell'],'value':float(v),'status':'HYPOTHESE','reason':'Campagne de sensibilité'} for lever,v in zip(levers,values_at_point)]
        draft=d.propose(child,updates,0)
        preview=d.work.preview(child,draft['id'],progress)
        d.work.apply(child,draft['id'],preview['approval_token']); d.app.recalculate(child)
        if payload.get('metric')=='valuation':
            progress({'message':'Résolution WACC et valorisation du point de sensibilité.'})
            d.app.solve_wacc(child)
        points.append({'values':list(values_at_point),'case_id':child,'metrics':d.metrics(child)})
        current=d.get(case_id,campaign['id'],'sensitivity')
        d.save(case_id,'sensitivity',{**campaign,'points':points,'cancel_requested':current.get('cancel_requested',False)},status='RUNNING',object_id=campaign['id'])
        progress({'message':f'{len(points)} points calculés','campaign_id':campaign['id']})
    return d.save(case_id,'sensitivity',{**campaign,'points':points},status='COMPLETE',object_id=campaign['id'])
