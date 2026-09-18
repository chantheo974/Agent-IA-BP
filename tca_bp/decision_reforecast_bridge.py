"""Sourced double-entry corrections around the existing TCA forecast.

Corrections are NET adjustments to the model, never a second posting of its
scheduled transactions. Monthly cash/AR/AP/inventory/debt and annual balance
sheet remain separate from the model's untouched formulas and frozen budget.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import re

from .web_blocks import compact_setters, expand_operations

SCHEMA = 'tca-reforecast-bridge/1'
MARKER = 'TCA_REFORECAST_BRIDGE_V1'
SHEET = 'TCA Raccord'
ACCOUNTS = {
    'cash': ('Trésorerie', 'asset'),
    'receivables': ('Créances clients TTC', 'asset'),
    'inventory': ('Stocks', 'asset'),
    'other_assets': ('Autres actifs hors cash, créances clients et stocks', 'asset'),
    'payables': ('Dettes fournisseurs', 'liability'),
    'debt': ('Prêts bancaires et avances remboursables', 'liability'),
    'other_liabilities': ('Autres passifs hors fournisseurs, dette et capitaux propres', 'liability'),
    'equity': ('Capitaux propres', 'equity')}
BASELINE_FIELDS = {'assets':'Total actif du modèle à l’arrêté',
    'liabilities':'Passifs du modèle hors capitaux propres à l’arrêté',
    'equity':'Capitaux propres du modèle à l’arrêté',
    'net_income_ytd':'Résultat net du modèle du 1er janvier à l’arrêté'}


def _number(value):
    if value is None or isinstance(value,bool): raise ValueError('Montant numérique explicite requis')
    try: result=Decimal(str(value))
    except InvalidOperation: raise ValueError('Montant numérique explicite requis') from None
    if not result.is_finite() or not math.isfinite(float(result)): raise ValueError('Montant fini requis')
    return result


def _sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def bridge_diagnostics(actuals, bridge, periods, workbook_sha256=None):
    """Pure required-data contract for UI questions, not financial validation."""
    bridge=deepcopy(bridge or {}); questions=[]; diagnostics=[]
    def need(field,message): questions.append({'field':field,'message':message,'question':message,'required':True})
    def source(item,field):
        if not isinstance(item,dict) or not isinstance(item.get('evidence_id'),str) or not item['evidence_id'].strip():
            need(field+'.evidence_id','Citer une source du dossier pour '+field); return False
        return True
    if bridge.get('schema') != SCHEMA: need('schema','Utiliser le contrat '+SCHEMA)
    if bridge.get('basis') != 'NET_ADJUSTMENTS_TO_CURRENT_MODEL':
        need('basis','Confirmer que les écritures sont des corrections NETTES du modèle, sans reprendre ses flux une seconde fois.')
    if not bridge.get('workbook_sha256') or workbook_sha256 and bridge['workbook_sha256'] != workbook_sha256:
        need('workbook_sha256','Rattacher le pont à l’empreinte de la révision courante du modèle.')
    cutoff=actuals.get('cutoff','')[:7]
    lookup={(r.get('period'),r.get('metric')):r for r in actuals.get('rows',[])}
    for metric in ('revenue','receipts','payments','cash','receivables','inventory','payables','debt'):
        missing=[p for p in periods if p<=cutoff and (p,metric) not in lookup]
        if missing:
            need('actuals.history.'+metric,'Compléter le réalisé '+metric+' pour les mois '+', '.join(missing[:12])+('…' if len(missing)>12 else '')+'. Aucun mois absent ne devient zéro.')
    for metric in ('cash','receivables','inventory','payables','debt','assets','liabilities','equity'):
        if (cutoff,metric) not in lookup: need('actuals.'+metric,'Renseigner le solde réel '+metric+' à l’arrêté, zéro explicite si confirmé.')
    if re.fullmatch(r'\d{4}-\d{2}',cutoff):
        for month in range(1,int(cutoff[5:])+1):
            period=cutoff[:4]+f'-{month:02d}'
            if (period,'net_income') not in lookup: need('actuals.net_income.'+period,'Renseigner le résultat net réel du mois '+period+' pour calculer le cumul depuis janvier.')
    baseline=bridge.get('baseline_cutoff',{})
    if not isinstance(baseline,dict): raise ValueError('baseline_cutoff doit être un objet')
    for key in BASELINE_FIELDS:
        item=baseline.get(key)
        if not cutoff.endswith('-12'):
            if source(item,'baseline_cutoff.'+key):
                if item.get('value') is None: need('baseline_cutoff.'+key,BASELINE_FIELDS[key]+' : valeur à fournir sans ventilation mensuelle implicite.')
                else: item['value']=str(_number(item['value']))
    policies=bridge.get('policies',{})
    if not isinstance(policies,dict): raise ValueError('policies doit être un objet')
    if set(policies)-set(ACCOUNTS): raise ValueError('Compte de raccord inconnu')
    for account in ACCOUNTS:
        policy=policies.get(account)
        source(policy,'policies.'+account)
        if not isinstance(policy,dict): policy={}
        if policy.get('treatment') not in ('carry','scheduled'):
            need('policies.'+account+'.treatment','Définir le traitement de l’écart '+account+' : conservation sourcée ou échéancier de corrections.')
        if policy.get('terminal') not in ('zero','carry_remaining'):
            need('policies.'+account+'.terminal','Préciser si l’écart '+account+' doit être soldé ou peut subsister en fin d’horizon.')
        if not isinstance(policy.get('reason'),str) or not policy['reason'].strip(): need('policies.'+account+'.reason','Justifier le traitement et les échéances de '+account+'.')
        if policy.get('treatment')=='carry' and policy.get('terminal')=='zero':
            need('policies.'+account+'.terminal','Une conservation utilise carry_remaining ; zéro terminal exige un échéancier vérifiable.')
    events=bridge.get('events')
    if events is None: need('events','Fournir les corrections mensuelles ; [] signifie explicitement aucun événement supplémentaire.'); events=[]
    if not isinstance(events,list) or len(events)>500: raise ValueError('Échéancier limité à 500 événements explicites')
    seen=set(); assigned=set()
    for event in events:
        if not isinstance(event,dict): raise ValueError('Chaque événement est un objet')
        ident=event.get('id')
        if not isinstance(ident,str) or not ident.strip() or ident in seen: raise ValueError('Identifiant événement non vide et unique requis')
        seen.add(ident)
        if event.get('period') not in periods or event['period']<=cutoff: raise ValueError('Événement après l’arrêté et dans l’horizon requis')
        source(event,'events.'+ident)
        if not isinstance(event.get('reason'),str) or not event['reason'].strip(): need('events.'+ident+'.reason','Justifier la correction '+ident)
        if event.get('kind') not in ('balance_transfer','profit_loss','capital'): raise ValueError('Nature comptable de correction inconnue')
        if event['kind']=='profit_loss' and event.get('tax_treatment') not in ('explicit_in_entries','no_tax_effect_confirmed'):
            need('events.'+ident+'.tax_treatment','Décrire les effets fiscaux de '+ident+' dans les écritures ou confirmer avec source l’absence d’effet fiscal.')
        entries=event.get('entries')
        if not isinstance(entries,list) or not 2<=len(entries)<=20: raise ValueError('Événement avec 2 à 20 lignes débit/crédit requis')
        debit=credit=Decimal(0); equity=Decimal(0)
        for entry in entries:
            account=entry.get('account')
            if account not in ACCOUNTS: raise ValueError('Compte de correction inconnu')
            assigned.add(account)
            dr,cr=_number(entry.get('debit')),_number(entry.get('credit'))
            if dr<0 or cr<0 or (dr>0 and cr>0): raise ValueError('Débit/crédit non négatifs, un seul côté positif par ligne')
            entry.update(debit=str(dr),credit=str(cr));debit+=dr;credit+=cr
            if account=='equity':equity+=cr-dr
            if account=='cash' and entry.get('cash_flow') not in ('receipts','payments'):
                need('events.'+ident+'.cash_flow','Affecter la correction de cash de '+ident+' aux encaissements ou aux décaissements (montant net du modèle).')
        if abs(debit-credit)>Decimal('.01'): raise ValueError('Événement déséquilibré débit/crédit : '+ident)
        if event['kind']=='balance_transfer' and equity: raise ValueError('Un transfert de bilan ne peut masquer une variation de résultat ou de capital')
    for account,policy in policies.items():
        if isinstance(policy,dict):
            if policy.get('treatment')=='carry' and account in assigned: need('policies.'+account,'Le compte '+account+' porte des corrections : choisir scheduled plutôt que carry.')
            if policy.get('treatment')=='scheduled' and account not in assigned: need('events.'+account,'Fournir l’échéancier de '+account+' ou une décision sourcée de conservation de l’écart.')
    bridge.update(baseline_cutoff=baseline,policies=policies,events=events)
    return {'schema':SCHEMA,'questions':questions,'diagnostics':diagnostics,'ready':not questions,
            'required_accounts':[{'id':key,'label':label,'nature':kind} for key,(label,kind) in ACCOUNTS.items()],
            'bridge':bridge}


def _guard(required, expression):
    return '=IF(COUNT('+','.join(required)+')='+str(len(required))+','+expression+',NA())'


def physical_locations(engine, periods):
    from .decision_model import location_resolver
    from .decision_reforecast import _ref, _col
    resolve=location_resolver(engine)
    def ref(sheet,cell): return _ref(*resolve(sheet,cell))
    monthly={}
    for index,period in enumerate(periods):
        mf=_col(20+index); bfr=_col(16+index)
        refs={key:ref('Modèle financier',mf+'321') if key=='cash' else ref('BFR',bfr+str(row))
              for key,row in [('cash',0),('receivables',10),('inventory',11),('payables',17)]}
        monthly[period]={key:{'required':[value],'expression':value} for key,value in refs.items()}
        debt_refs=[ref('Modèle financier',mf+str(row)) for row in (292,299,315,317)]
        debt_expr=debt_refs[0]+'+'+debt_refs[1]+'-'+debt_refs[2]+'-'+debt_refs[3]
        monthly[period]['debt']={'required':debt_refs,'expression':debt_expr,'rollforward':True}
    annual={}
    first=int(periods[0][:4])
    for year in sorted({p[:4] for p in periods}):
        col=_col(4+int(year)-first)
        assets,liabilities,equity=ref('Bilan',col+'4'),ref('Bilan',col+'24'),ref('Bilan',col+'25')
        income=ref('Compte de Résultat',col+'85')
        annual[year]={'assets':{'required':[assets],'expression':assets},
            'liabilities':{'required':[liabilities,equity],'expression':liabilities+'-'+equity},
            'equity':{'required':[equity],'expression':equity},'net_income_ytd':{'required':[income],'expression':income}}
    return {'monthly':monthly,'annual':annual}


def augment_plan(plan, actuals, budget, series, locations, bridge, *, existing=None, source_id=None, workbook_sha256=None):
    from .decision_reforecast import _ref,_col,METRICS
    periods=series[0]['categories']; cutoff=actuals['cutoff'][:7]; future=[p for p in periods if p>cutoff]
    assessment=bridge_diagnostics(actuals,bridge,periods,workbook_sha256)
    bridge=assessment['bridge']; existing=existing or {}
    candidates=[name for name,item in existing.items() if item.get('marker')==MARKER]
    if len(candidates)>1: raise ValueError('Identité de raccord comptable dupliquée')
    name=candidates[0] if candidates else SHEET
    if not candidates and name in existing: raise ValueError('La feuille TCA Raccord existe sans identité gérée')
    ops=list(expand_operations(plan['operations']))
    evidence=source_id or actuals['rows'][0]['evidence_id']
    if name not in existing: ops.append({'type':'add_sheet','name':name,'role':'Pont comptable à double entrée, corrections nettes sourcées du modèle','evidence_id':evidence})
    targets=set()
    def put(sheet,cell,value,formula=False,source=None):
        targets.add((sheet,cell))
        ops.append({'type':'set_formula' if formula else 'set_value','sheet':sheet,'cell':cell,
                    'formula' if formula else 'value':value,'evidence_id':source or evidence,'reason':'Raccord comptable explicite, correction nette du modèle'})
    def here(cell):return _ref(name,cell)
    locations=deepcopy(locations)
    previous=None
    for i,period in enumerate(periods):
        item=locations['monthly'][period]['debt']
        if item.get('rollforward'):
            col=_col(9+i); put(name,col+'49',period)
            required=item['required']+([previous] if previous else [])
            expression=(previous+'+' if previous else '')+'('+item['expression']+')'
            put(name,col+'50',_guard(required,expression),True)
            previous=here(col+'50')
            locations['monthly'][period]['debt']={'required':[previous],'expression':previous}
    actual_name=plan['sheets']['actuals'];forecast_name=plan['sheets']['reforecast']
    all_periods=sorted(set(periods)|{r['period'] for r in actuals['rows']})
    actual_cols={p:_col(i+4) for i,p in enumerate(all_periods)}
    actual_rows={m:i+6 for i,(m,_,_) in enumerate(METRICS)}
    def actual(metric,period=cutoff):return _ref(actual_name,actual_cols[period]+str(actual_rows[metric]))
    for cell,value in {'A1':MARKER,'A2':SCHEMA,'B2':cutoff,'A3':'Corrections nettes du modèle, jamais ses flux comptés deux fois',
        'A4':'Empreinte réalisé','B4':plan['actuals_sha256'],'A5':'Empreinte budget','B5':plan['budget_sha256'],
        'A6':'Empreinte règles du pont','B6':_sha(bridge),'A8':'Contrôle de complétude et d’équilibre','A9':'Pièces et décisions explicitement fournies',
        'B9':1 if assessment['ready'] else None,'A12':'Compte','B12':'Réalisé à l’arrêté','C12':'Modèle à l’arrêté','D12':'Écart initial','E12':'Traitement','F12':'Source politique'}.items():put(name,cell,value)
    account_rows={account:i+14 for i,account in enumerate(ACCOUNTS)}
    # Checkpoint totals: direct December owners, or sourced interim balances.
    for row,key in enumerate(BASELINE_FIELDS,26):
        put(name,'A'+str(row),BASELINE_FIELDS[key])
        if cutoff.endswith('-12'):
            item=locations['annual'][cutoff[:4]][key]
            put(name,'B'+str(row),_guard(item['required'],item['expression']),True)
        else:
            item=bridge['baseline_cutoff'].get(key) or {}
            put(name,'B'+str(row),float(_number(item['value'])) if item.get('value') is not None else None,source=item.get('evidence_id'))
    for row,key in enumerate(('assets','liabilities','equity'),32):put(name,'B'+str(row),_guard([actual(key)],actual(key)),True)
    ni_refs=[actual('net_income',cutoff[:4]+f'-{m:02d}') for m in range(1,int(cutoff[5:])+1)
             if cutoff[:4]+f'-{m:02d}' in actual_cols]
    expected_months=int(cutoff[5:])
    put(name,'B35',_guard(ni_refs,'SUM('+','.join(ni_refs)+')') if len(ni_refs)==expected_months else '=NA()',True)
    for account,row in account_rows.items():
        put(name,'A'+str(row),ACCOUNTS[account][0])
        if account in ('other_assets','other_liabilities'):
            total='B32' if account=='other_assets' else 'B33'
            parts=('B14','B15','B16') if account=='other_assets' else ('B18','B19')
            put(name,'B'+str(row),_guard([here(total),*(here(p) for p in parts)],here(total)+'-'+ '-'.join(here(p) for p in parts)),True)
            total='B26' if account=='other_assets' else 'B27'
            parts=('C14','C15','C16') if account=='other_assets' else ('C18','C19')
            put(name,'C'+str(row),_guard([here(total),*(here(p) for p in parts)],here(total)+'-'+ '-'.join(here(p) for p in parts)),True)
        else:
            put(name,'B'+str(row),_guard([actual(account)],actual(account)),True)
            item=locations['annual'][cutoff[:4]]['equity'] if account=='equity' and cutoff.endswith('-12') else locations['monthly'][cutoff].get(account)
            put(name,'C'+str(row),_guard(item['required'],item['expression']) if item else '='+here('B28'),True)
        put(name,'D'+str(row),_guard([here('B'+str(row)),here('C'+str(row))],here('B'+str(row))+'-'+here('C'+str(row))),True)
        policy=bridge['policies'].get(account) or {}
        code=1 if policy.get('treatment')=='carry' else 2 if policy.get('treatment')=='scheduled' and policy.get('terminal')=='zero' else 3 if policy.get('treatment')=='scheduled' and policy.get('terminal')=='carry_remaining' else None
        put(name,'E'+str(row),code,source=policy.get('evidence_id'));put(name,'F'+str(row),policy.get('evidence_id'))
    # Journal remains editable, explicit and sourced, with one balance control per event.
    for col,label in zip('ABCDEFGHI',('Mois','Compte','Débit','Crédit','Événement','Nature','Source','Contrôle événement','Flux de trésorerie')):put(name,col+'59',label)
    ledger_row=60; controls=[]
    for event in bridge['events']:
        start=ledger_row
        for entry in event['entries']:
            values=[event['period'],entry['account'],float(_number(entry['debit'])),float(_number(entry['credit'])),event['id'],event['kind'],event.get('evidence_id'),None,entry.get('cash_flow')]
            for col,value in zip('ABCDEFGHI',values):
                if col!='H':put(name,col+str(ledger_row),value,source=event.get('evidence_id'))
            ledger_row+=1
        ctrl=here('H'+str(start));controls.append(ctrl)
        put(name,'H'+str(start),'=SUM(C'+str(start)+':C'+str(ledger_row-1)+')-SUM(D'+str(start)+':D'+str(ledger_row-1)+')',True)
    end=max(60,ledger_row-1)
    def area(column):return here(column+'60')+':'+column+str(end)
    def sumif(column,account,period,kind=None,flow=None,exact=False):
        expression='SUMIFS('+area(column)+','+area('B')+',"'+account+'",'+area('A')+','+('"' if exact else '"<=')+period+'"'
        if kind:expression+=','+area('F')+',"'+kind+'"'
        if flow:expression+=','+area('I')+',"'+flow+'"'
        return expression+')'
    delta={}
    for i,period in enumerate(future):
        col=_col(9+i);put(name,col+'12',period);delta[period]={}
        for account,row in account_rows.items():
            sign=1 if ACCOUNTS[account][1]=='asset' else -1
            expression=here('D'+str(row))+('+' if sign==1 else '-')+'('+sumif('C',account,period)+'-'+sumif('D',account,period)+')'
            put(name,col+str(row),_guard([here('D'+str(row))],expression),True);delta[period][account]=here(col+str(row))
    terminal=[]
    for i,(account,row) in enumerate(account_rows.items(),40):
        cell=here('B'+str(i));terminal.append(cell)
        last=delta[future[-1]][account] if future else here('D'+str(row))
        put(name,'A'+str(i),'Écart terminal '+account)
        put(name,'B'+str(i),'=IF('+here('E'+str(row))+'=2,'+last+',IF(COUNT('+here('E'+str(row))+')=1,0,NA()))',True)
    gates=['COUNT(B14:D21)=24','COUNT(E14:E21)=8','COUNT(B26:B29)=4','COUNT(B32:B35)=4','B9=1',
           'ABS(B26-B27-B28)<=0.01','ABS(B32-B33-B34)<=0.01']
    gates += ['COUNT(H60:H'+str(end)+')='+str(len(controls)),
              'IFERROR(SUMPRODUCT(ABS(H60:H'+str(end)+'))<=0.01,FALSE)',
              'COUNT(B40:B47)=8','IFERROR(SUMPRODUCT(ABS(B40:B47))<=0.01,FALSE)']
    put(name,'B8','=IF(AND('+','.join(gates)+'),1,NA())',True)
    # Replace only the new managed forecast formulas, never original owners.
    replacements={}
    for period in future:
        col=_col(periods.index(period)+4)
        for metric,row in (('cash',9),('receipts',7),('payments',8)):
            from .decision_reforecast import _ref as ref
            source_ref=ref(*plan['_model_locations'][metric][period])
            if metric=='cash': correction=delta[period]['cash']
            else:
                a=sumif('C','cash',period,flow=metric,exact=True); b=sumif('D','cash',period,flow=metric,exact=True)
                correction='('+a+'-'+b+')' if metric=='receipts' else '('+b+'-'+a+')'
            replacements[(forecast_name,col+str(row))]='=IF('+here('B8')+'=1,'+_guard([source_ref],source_ref+'+'+correction)[1:]+',NA())'
        for account,row in (('receivables',16),('inventory',17),('payables',18),('debt',19)):
            item=locations['monthly'][period][account]
            put(forecast_name,col+str(row),'=IF('+here('B8')+'=1,'+_guard(item['required'],item['expression']+'+'+delta[period][account])[1:]+',NA())',True)
    for op in ops:
        key=(op.get('sheet'),op.get('cell'))
        if key in replacements:op['formula']=replacements[key]
    for account,row in (('receivables',16),('inventory',17),('payables',18),('debt',19)):
        put(forecast_name,'A'+str(row),ACCOUNTS[account][0]);put(forecast_name,'C'+str(row),'EUR')
        for period in periods:
            if period<=cutoff:put(forecast_name,_col(periods.index(period)+4)+str(row),_guard([actual(account,period)],actual(account,period)),True)
    years=sorted(y for y in locations['annual'] if y>=cutoff[:4])
    for i,year in enumerate(years):
        col=_col(4+i); period=year+'-12'; put(forecast_name,col+'31',year)
        current_delta=delta.get(period,{a:here('D'+str(r)) for a,r in account_rows.items()})
        for metric,row,accounts in [('assets',33,('cash','receivables','inventory','other_assets')),
                                    ('liabilities',34,('payables','debt','other_liabilities')),('equity',35,('equity',))]:
            item=locations['annual'][year][metric]
            expression=item['expression']+'+'+'+'.join(current_delta[a] for a in accounts)
            put(forecast_name,col+str(row),'=IF('+here('B8')+'=1,'+_guard(item['required'],expression)[1:]+',NA())',True)
        item=locations['annual'][year]['net_income_ytd']
        prior=str(int(year)-1)+'-12'
        adjustment='('+sumif('D','equity',period,kind='profit_loss')+'-'+sumif('C','equity',period,kind='profit_loss')+')-('+sumif('D','equity',prior,kind='profit_loss')+'-'+sumif('C','equity',prior,kind='profit_loss')+')'
        income=item['expression']+('-'+here('B29')+'+'+here('B35') if year==cutoff[:4] else '')+'+('+adjustment+')'
        put(forecast_name,col+'36','=IF('+here('B8')+'=1,'+_guard(item['required'],income)[1:]+',NA())',True)
        put(forecast_name,col+'37',_guard([_ref(forecast_name,col+str(r)) for r in (33,34,35)],col+'33-'+col+'34-'+col+'35'),True)
        a=locations['annual'][year]
        put(forecast_name,col+'38',_guard(list(dict.fromkeys(x for key in ('assets','liabilities','equity') for x in a[key]['required'])),a['assets']['expression']+'-('+a['liabilities']['expression']+')-'+a['equity']['expression']),True)
    for row,label in [(31,'Bilan annuel actualisé'),(33,'Total actif'),(34,'Passifs hors capitaux propres'),(35,'Capitaux propres'),(36,'Résultat net annuel actualisé'),(37,'Écart actif-passifs-capitaux propres'),(38,'Contrôle du bilan modèle avant correction')]:put(forecast_name,'A'+str(row),label)
    put(forecast_name,'A4','Pont comptable net : contrôles du journal et du bilan annuel requis. Aucune ventilation fiscale mensuelle implicite.')
    for cell,state in existing.get(name,{}).get('cells',{}).items():
        if (name,cell) not in targets and (state.get('value') is not None or state.get('formula')):put(name,cell,None)
    # The old planner clears managed cells outside its own core; discard those
    # clears when the bridge now owns a destination, retaining the final write.
    dedup={}
    for i,op in enumerate(ops):
        if op['type'] in ('set_value','set_formula'):dedup[(op['sheet'],op['cell'])]=i
    ops=[op for i,op in enumerate(ops) if op['type'] not in ('set_value','set_formula') or dedup[(op['sheet'],op['cell'])]==i]
    # Excel treats a reference to a not-yet-created worksheet as an external
    # workbook link. All managed sheets must exist before the first formula.
    ops=[op for op in ops if op['type']=='add_sheet']+[op for op in ops if op['type']!='add_sheet']
    compact=compact_setters(ops)
    result={k:v for k,v in plan.items() if k not in ('_model_locations','operations')}
    result.update(schema_version='tca-reforecast/2',operations=compact,atomic_operation_count=len(ops),envelope_count=len(compact),
        sheets={**plan['sheets'],'bridge':name},bridge=bridge,bridge_sha256=_sha(bridge),questions=assessment['questions'],
        forecast_balance_status='ANNUEL_A_RECALCULER_ET_CONTROLER',financial_validation='PONT_COMPTABLE_A_RECALCULER_ET_CONTROLER',
        annual_years=years,periods=periods,bridge_control='B8',bridge_source_ids=sorted({evidence}|{p['evidence_id'] for p in bridge['policies'].values() if p.get('evidence_id')}|{e['evidence_id'] for e in bridge['events'] if e.get('evidence_id')}|{p['evidence_id'] for p in bridge['baseline_cutoff'].values() if p.get('evidence_id')}),
        diagnostics=[d for d in plan['diagnostics'] if d['code']!='BFR_ET_BILAN_FUTUR_NON_RECONSTRUITS']+
            [{'code':'PONT_NET_A_RECALCULER','message':'Corrections nettes à double entrée ; bilan annuel et contrôles requis. Le bilan mensuel intégral et une fiscalité recalculée automatiquement sur les corrections ne sont pas déduits.'}])
    result['managed_contract']=[{key:op[key] for key in ('sheet','cell','value','formula') if key in op}
                                for op in ops if op['type'] in ('set_value','set_formula')]
    return result
