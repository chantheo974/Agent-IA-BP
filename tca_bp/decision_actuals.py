"""Monthly actuals ledger, immutable budget and explicit reforecast continuity."""
from __future__ import annotations
import calendar
import csv
import datetime as dt
from decimal import Decimal
import io
import re
import json
import math

from .decision_documents import parse_number
from .storage import canonical, digest

KINDS={'flow','balance','volume'}
KNOWN={'revenue':'flow','net_income':'flow','receipts':'flow','payments':'flow','cash':'balance',
       'receivables':'balance','payables':'balance','inventory':'balance','debt':'balance',
       'assets':'balance','liabilities':'balance','equity':'balance','volume':'volume'}

def preview_actuals(d,case_id,body):
    d.check_revision(case_id,body.get('expected_revision'))
    try: cutoff=dt.date.fromisoformat(body.get('cutoff',''))
    except (TypeError,ValueError): raise ValueError('Une date d’arrêté valide est requise.')
    if cutoff.day!=calendar.monthrange(cutoff.year,cutoff.month)[1]:
        raise ValueError('Le réalisé mensuel utilise un arrêté au dernier jour du mois.')
    incoming=body.get('rows',[])
    if not isinstance(incoming,list) or not incoming or len(incoming)>20000: raise ValueError('Importer entre 1 et 20 000 lignes.')
    current=d.latest(case_id,'actuals',{'rows':[]})
    if any(r['period']>cutoff.strftime('%Y-%m') for r in current['rows']):
        raise ValueError('L’arrêté ne peut pas précéder des mois déjà validés. Corriger les observations sans effacer leur historique.')
    old={(r['period'],r['metric'],r['kind'],r['unit']):r for r in current['rows']}
    rows=dict(old); changes=[]; seen=set(); diagnostics=[]
    for i,raw in enumerate(incoming):
        period=str(raw.get('period',''))[:7]
        if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',period) or period>cutoff.strftime('%Y-%m'): raise ValueError(f'Ligne {i+1} : mois absent ou postérieur à l’arrêté.')
        metric=str(raw.get('metric','')).strip()
        if metric not in KNOWN: raise ValueError(f'Ligne {i+1} : affecter le poste « {metric} » à un indicateur reconnu avant validation.')
        kind=raw.get('kind','flow'); unit=str(raw.get('unit','EUR')).strip()
        if not metric or kind not in KINDS or not unit: raise ValueError(f'Ligne {i+1} : poste, nature et unité requis.')
        if metric!='volume' and unit!='EUR': raise ValueError('Convertir explicitement les montants financiers en EUR avant import.')
        if any(r['period']==period and r['metric']==metric and r['unit']!=unit for r in rows.values()):
            raise ValueError('Un poste ne peut pas porter plusieurs unités pour le même mois.')
        if metric in KNOWN and KNOWN[metric]!=kind: raise ValueError(f'{metric} est de nature {KNOWN[metric]}, pas {kind}.')
        value=raw.get('value')
        if value is None or value=='': raise ValueError(f'Ligne {i+1} : donnée manquante, ne pas la remplacer par zéro.')
        if isinstance(value,bool): raise ValueError('Valeur numérique requise.')
        conversion=parse_number(str(value),body.get('numeric_locale','fr'),typed=type(value) in (int,float))
        if conversion['normalized_value'] is None:
            diagnostics.append({'line':i+1,'code':'CONVERSION_AMBIGUE','raw':value,'message':'Confirmer la valeur en la saisissant explicitement.'})
            continue
        value=str(Decimal(conversion['normalized_value']))
        key=(period,metric,kind,unit)
        if key in seen: raise ValueError(f'La ligne {period} / {metric} figure deux fois dans cet import.')
        seen.add(key)
        evidence=raw.get('evidence_id') or body.get('source_id')
        if evidence: d.source(case_id,evidence)
        new={'period':period,'metric':metric,'kind':kind,'unit':unit,'value':value,'evidence_id':evidence,'raw':raw.get('raw',raw.get('value'))}
        before=old.get(key)
        if before and Decimal(before['value'])==Decimal(value): continue
        changes.append({'period':period,'metric':metric,'old':before['value'] if before else None,'new':value,'kind':'CORRECTION' if before else 'AJOUT'})
        rows[key]=new
    payload={'rows':list(rows.values()),'cutoff':cutoff.isoformat(),'changes':changes,'diagnostics':diagnostics,'numeric_locale':body.get('numeric_locale','fr')}
    if changes and any(not r.get('evidence_id') for key,r in rows.items() if key in seen):
        source=d.app.add_source(case_id,text=canonical({'rows':incoming,'cutoff':cutoff.isoformat(),'numeric_locale':body.get('numeric_locale','fr')}),title='Saisie manuelle du réalisé mensuel')
        for key,r in rows.items():
            if key in seen and not r.get('evidence_id'): r['evidence_id']=source['id']
    return d.preview_object(case_id,'actuals',payload,body.get('expected_revision'))

def apply_actuals(d,case_id,body):
    preview=next((p for p in d.objects(case_id,'actuals_preview') if p.get('approval_token')==body.get('approval_token')),None)
    if not preview: raise ValueError('Aperçu du réalisé requis.')
    if preview.get('diagnostics'): raise ValueError('Résoudre les conversions ambiguës avant validation.')
    def freeze_budget(row,db):
        if db.execute("SELECT 1 FROM decision_objects WHERE case_id=? AND kind='budget' AND status='CONFIRME'",(case_id,)).fetchone(): return
        from .decision_model import read_series
        case=d.app.get_case(case_id)
        if not case.get('outputs_current') or any(not case.get('qualified_availability',{}).get(scope,{}).get('scenario_ready') for scope in ('CA','COGS','CASH','FISCALITE')):
            raise ValueError('Recalculer et qualifier le prévisionnel initial avant de figer le budget.')
        series=read_series(d,case_id)
        if ({s['id'] for s in series}!={'cash','revenue','receipts','payments'} or
            any(not s.get('categories') or len(s.get('values',[]))!=len(s['categories']) or
                any(type(v) not in (int,float) or not math.isfinite(v) for v in s['values']) for s in series)):
            raise ValueError('Compléter les séries mensuelles du prévisionnel avant de figer le budget ; une donnée manquante ne devient pas un zéro.')
        metrics=d.metrics(case_id)
        d.work._snapshot_version(row,db)
        d.save(case_id,'budget',{'source_revision':row['revision'],'source_sha256':row['sha256'],'workbook':row['workbook'],'series':series,'metrics':metrics},db=db)
    result=d.adopt_object(case_id,'actuals',body,before_adopt=freeze_budget)
    return {**result,'reforecast':actuals_view(d,case_id)}

def actuals_view(d,case_id):
    current=d.latest(case_id,'actuals',{'rows':[]})
    budget=d.latest(case_id,'budget',{'series':[]})
    lookup={(r['period'],r['metric']):r for r in current['rows']}
    comparisons=[]
    for series in budget.get('series',[]):
        for period,value in zip(series['categories'],series['values']):
            actual=lookup.get((period,series['id']))
            if actual:
                comparisons.append({'period':period,'metric':series['id'],'budget':value,'actual':actual['value'],'variance':float(Decimal(actual['value'])-Decimal(str(value))) if value is not None else None})
    diagnostics=[]; cutoff=current.get('cutoff','')[:7]
    if cutoff:
        for metric in ('cash','assets','liabilities','equity'):
            if (cutoff,metric) not in lookup: diagnostics.append({'code':'SOLDE_MANQUANT','metric':metric,'message':f'Solde {metric} à l’arrêté nécessaire au raccord.'})
        if all((cutoff,m) in lookup for m in ('assets','liabilities','equity')):
            residual=Decimal(lookup[(cutoff,'assets')]['value'])-Decimal(lookup[(cutoff,'liabilities')]['value'])-Decimal(lookup[(cutoff,'equity')]['value'])
            if abs(residual)>Decimal('0.01'): diagnostics.append({'code':'BILAN_DESEQUILIBRE','difference':str(residual)})
    forecasts=[]
    if cutoff:
        from .decision_model import read_series
        for series in read_series(d,case_id):
            past={p:lookup.get((p,series['id'])) for p in series['categories'] if p<=cutoff}
            missing=[p for p,v in past.items() if v is None]
            if missing: diagnostics.append({'code':'HISTORIQUE_INCOMPLET','metric':series['id'],'periods':missing})
            values=[]
            for period,value in zip(series['categories'],series['values']):
                actual=lookup.get((period,series['id']))
                if period<=cutoff:
                    values.append(float(actual['value']) if actual else None)
                else:
                    # Future values are published only from the adopted and
                    # natively calculated accounting bridge, never an overlay.
                    values.append(None)
            forecasts.append({**series,'values':values})
    calculated={'forecast_series':forecasts,'annual_balance':[],'forecast_status':'A_PREPARER'}
    if d.objects(case_id,'reforecast_preparation'):
        from .decision_reforecast import read_reforecast
        native=read_reforecast(d,case_id)
        diagnostics.extend(native.pop('diagnostics',[]))
        calculated.update(native)
    labels={'revenue':'Chiffre d’affaires','net_income':'Résultat net','receipts':'Encaissements','payments':'Décaissements','cash':'Trésorerie','assets':'Total actif','liabilities':'Dettes et autres passifs hors capitaux propres','equity':'Capitaux propres','receivables':'Créances clients','payables':'Dettes fournisseurs','inventory':'Stock','debt':'Dette financière','volume':'Volume vendu'}
    return {**current,'metrics_catalog':[{'id':k,'label':labels[k],'kind':v,'unit':'unités' if v=='volume' else 'EUR'} for k,v in KNOWN.items()],'budget':budget,'comparisons':comparisons,**calculated,'diagnostics':diagnostics,
            'history':[{'id':o['id'],'cutoff':o.get('cutoff'),'created_at':o['created_at'],'changes':o.get('changes',[])} for o in d.objects(case_id,'actuals')]}

def read_import(path,mapping,locale,encoding='utf-8'):
    """Read only, no macros/formulas executed; column choice is always explicit."""
    if encoding not in ('utf-8','cp1252'): raise ValueError('Choisir l’encodage CSV UTF-8 ou Windows-1252.')
    if path.suffix.lower()=='.csv':
        try: text=path.read_bytes().decode('utf-8-sig' if encoding=='utf-8' else 'cp1252')
        except UnicodeDecodeError:
            label='UTF-8' if encoding=='utf-8' else 'Windows-1252'
            raise ValueError(f'Le CSV ne peut pas être lu en {label}. Choisir son encodage dans le formulaire (UTF-8 ou Windows-1252), puis relire le fichier.') from None
        sample=text[:8192]
        try: dialect=csv.Sniffer().sniff(sample,delimiters=',;\t')
        except csv.Error: dialect=csv.excel
        reader=csv.DictReader(io.StringIO(text),dialect=dialect)
        columns=reader.fieldnames or []
        rows=list(reader)
    elif path.suffix.lower() in ('.xlsx','.xlsm'):
        from .vendor import input_engine as core
        from .decision_documents import extract_document
        extracted=extract_document(path,numeric_locale=locale,max_blocks=100000)
        blocks=[b for b in extracted['blocks'] if b.get('location',{}).get('cell')]
        sheet=blocks[0]['location']['sheet'] if blocks else None
        blocks=[b for b in blocks if b['location']['sheet']==sheet]
        if any(b.get('formula') for b in blocks): raise ValueError('Le réalisé importé doit contenir des valeurs, sans formules ni caches incertains.')
        cells={b['location']['cell']:float(b['text']) if b.get('excel_type')=='n' else b['text'] for b in blocks}
        width=max((core.coord(a)[1] for a in cells),default=0)
        height=max((core.coord(a)[2] for a in cells),default=0)
        if width>200 or height>20001: raise ValueError('Tableau limité à 200 colonnes et 20 000 lignes.')
        columns=[str(cells.get(core.colname(c)+'1') or '') for c in range(1,width+1)]
        rows=[{name:cells.get(core.colname(c)+str(r)) for c,name in enumerate(columns,1)} for r in range(2,height+1)]
    else: raise ValueError('Importer un fichier CSV, XLSX ou XLSM.')
    if len(rows)>20000: raise ValueError('Import limité à 20 000 lignes.')
    if not mapping: return columns,[]
    if any(not mapping.get(k) or mapping[k] not in columns for k in ('period','metric','value')): raise ValueError('Associer les colonnes période, poste et valeur.')
    return columns,[{**{key:row.get(column) for key,column in mapping.items() if column},'kind':row.get(mapping.get('kind')) or 'flow','unit':row.get(mapping.get('unit')) or 'EUR'} for row in rows]
