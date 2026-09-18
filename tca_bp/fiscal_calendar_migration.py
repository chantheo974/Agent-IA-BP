"""Explicit Fiscal/cash calendar repair: selected periods retain their errors.

Only 55 known annual fiscal/cash aggregations and one monthly cash alert may change. Their predicates
and selected values are retained; this is not a general IFERROR or a financial input.
The new model still needs its own declarations, recalculation and WACC proof.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
from pathlib import Path
import re
from types import SimpleNamespace

from .storage import atomic_json,canonical,digest
from .vendor import input_engine as core
from .web_model_profile import initial_profile,map_location,seal_profile,verify_profile
from .web_structure import _formula_key as _serialized_key

MIGRATION_ID='fiscal-calendar/selected-period-aggregation-v1'
REASON=('Correction des agrégats annuels de fiscalité et de trésorerie : sélectionner les périodes avant '
        'addition, en conservant les erreurs des périodes retenues et sans modifier les hypothèses.')
BLOCKS=(('ATELIER_CIR_IS',34),('Modèle financier',310),('Modèle financier',311),
        ('Modèle financier',320),('Modèle financier',321))
OWNERS=tuple(sheet+'!'+column+str(row) for sheet,row in BLOCKS for column in 'CDEFGHIJKLM')+('KPI Dashboard!E68',)



def _hash(value):return hashlib.sha256(canonical(value).encode()).hexdigest()


def _key(formula):
    # Optional OOXML sheet/function spelling only; absolute references and
    # quoted string contents remain significant, including inherited proofs.
    return _serialized_key(formula)


def _reference(profile,sheet,cell,local_sheet):
    target=map_location(profile,sheet,cell)
    if target is None:raise ValueError('Une référence du calendrier fiscal a été supprimée : '+sheet+'!'+cell)
    prefix='' if target['sheet']==local_sheet else (
        target['sheet'] if re.fullmatch(r'[^\W\d]\w*',target['sheet']) else "'"+target['sheet'].replace("'","''")+"'")+'!'
    match=re.fullmatch(r'(\$?)[A-Z]+(\$?)\d+',cell)
    mapped=re.fullmatch(r'([A-Z]+)(\d+)',target['cell'])
    return prefix+match[1]+mapped[1]+match[2]+mapped[2]


def expected_formulas(profile):
    result=[]
    for sheet,row in BLOCKS:
        for column in 'CDEFGHIJKLM':
            target=map_location(profile,sheet,column+str(row))
            if target is None:raise ValueError('Un agrégat annuel a été supprimé.')
            ref=lambda cell:_reference(profile,sheet,cell,target['sheet'])
            span=lambda first,last:ref(first)+':'+ref(last)
            if sheet=='ATELIER_CIR_IS':
                dates=span('$N$50','$EO$50');values=span('$N$52','$EO$52');year=ref(column+'$12')
                condition=f'YEAR({dates})={year}'
                original=f'SUMPRODUCT(({condition})*({values}))'
            else:
                dates=span('$T$3','$QI$3');values=span('$T'+str(row),'$QI'+str(row));year=ref(column+'$3')
                condition=f'YEAR({dates})={year}'
                if row==321:
                    original=f'SUMPRODUCT(({condition})*(MONTH({dates})=12)*{values})'
                    condition=f'({condition})*(MONTH({dates})=12)'
                else:original=f'SUMPRODUCT(({condition})*{values})'
            fixed=f'SUMPRODUCT(IF({condition},{values},0))'
            result.append({**target,'owner':sheet+'!'+column+str(row),'old_formula':original,'new_formula':fixed})
    target=map_location(profile,'KPI Dashboard','E68')
    if target is None:raise ValueError('L’alerte de rupture de trésorerie a été supprimée.')
    ref=lambda sheet,cell:_reference(profile,sheet,cell,target['sheet'])
    def span(first,last):
        end=map_location(profile,'Modèle financier',last)
        if end is None:raise ValueError('Une période mensuelle a été supprimée.')
        tail=_reference(profile,'Modèle financier',last,end['sheet'])
        return ref('Modèle financier',first)+':'+tail
    dates=span('$T$3','$EI$3');cash=span('$T$321','$EI$321')
    start,end=ref('KPI Dashboard','E63'),ref('KPI Dashboard','E64')
    predicate=f'({cash}<0)*({dates}>={start})*({dates}<={end})'
    tail=f',"Non atteint dans le plan",_xlfn.AGGREGATE(15,6,{dates}/({predicate}),1))'
    original=f'IF(SUMPRODUCT({predicate})=0'+tail
    fixed=f'IF(SUMPRODUCT(IF(({dates}>={start})*({dates}<={end}),--({cash}<0),0))=0'+tail
    result.append({**target,'owner':'KPI Dashboard!E68','old_formula':original,'new_formula':fixed})
    return result


def plan_fiscal_calendar_migration(engine,workbook,evidence_id):
    if not isinstance(evidence_id,str) or not evidence_id.strip():raise ValueError('Une source explicite du dossier est requise.')
    workbook=Path(workbook).resolve()
    profile=initial_profile(engine,workbook)
    expected=expected_formulas(profile);changes=[];versions=set()
    actual=engine._open(workbook)
    try:
        for item in expected:
            old=actual.formula(item['sheet'],item['cell'])
            if _key(old)==_key(item['old_formula']):version=0
            elif _key(old)==_key(item['new_formula']):version=1
            else:raise ValueError('Formule annuelle différente du contrat reconnu : '+item['sheet']+'!'+item['cell'])
            versions.add(version)
            changes.append({**item,'old_formula':old})
        if len(versions)!=1:raise ValueError('Migration fiscale partielle : réexaminer les 56 formules avant application.')
    finally:actual.close()
    migrated=versions=={1}
    return {'schema':'tca-fiscal-calendar-migration/1','migration_id':MIGRATION_ID,
        'status':'ALREADY_MIGRATED' if migrated else 'PROPOSED','profile':profile,'changes':changes,
        'source_sha256':digest(workbook),'active_year_errors_preserved':True,'financial_outputs_verified':False,
        'operations':[] if migrated else [{'type':'set_formula','sheet':item['sheet'],'cell':item['cell'],
            'formula':'='+item['new_formula'],'evidence_id':evidence_id,'reason':REASON} for item in changes]}


def certificate_fiscal_calendar_change(old_profile,old_path,new_path,new_profile,operations):
    """Recognize exactly the reviewed 56-formula rule after a controlled preview."""
    verify_profile(old_profile);verify_profile(new_profile)
    if (not isinstance(operations,list) or len(operations)!=56
            or any(not isinstance(op,dict) or op.get('type')!='set_formula' for op in operations)):
        return new_profile
    try:
        targets=[map_location(old_profile,sheet,column+str(row)) for sheet,row in BLOCKS for column in 'CDEFGHIJKLM']
        targets.append(map_location(old_profile,'KPI Dashboard','E68'))
    except (ValueError,KeyError):return new_profile
    if any(target is None for target in targets):return new_profile
    if {(op.get('sheet'),op.get('cell')) for op in operations}!={(target['sheet'],target['cell']) for target in targets}:
        return new_profile
    expected=expected_formulas(old_profile)
    keys={(item['sheet'],item['cell']) for item in expected}
    if {(op.get('sheet'),op.get('cell')) for op in operations}!=keys:return new_profile
    if (old_profile['sheets']!=new_profile['sheets'] or new_profile.get('parent_profile_sha256')!=old_profile['profile_sha256']
            or digest(old_path)!=old_profile['current_workbook_sha256'] or digest(new_path)!=new_profile['current_workbook_sha256']):
        raise ValueError('La correction du calendrier fiscal doit relier deux révisions exactes sans changement de structure.')
    reader=SimpleNamespace(profile=old_profile,_open=core.Workbook)
    try:plan=plan_fiscal_calendar_migration(reader,old_path,operations[0].get('evidence_id'))
    except ValueError:return new_profile
    if plan['status']!='PROPOSED':return new_profile
    proposals={(op['sheet'],op['cell']):op for op in operations}
    if any(_key(proposals[item['sheet'],item['cell']].get('formula'))!=_key(item['new_formula'])
           or not isinstance(proposals[item['sheet'],item['cell']].get('evidence_id'),str)
           or not proposals[item['sheet'],item['cell']]['evidence_id'].strip() for item in expected):return new_profile
    before,after=core.Workbook(Path(old_path)),core.Workbook(Path(new_path))
    changed={}
    try:
        if list(before.sheets)!=list(after.sheets):raise ValueError('Une feuille a changé hors de la correction du calendrier fiscal.')
        for sheet in before.sheets:
            for cell in set(before.sheet(sheet)[1])|set(after.sheet(sheet)[1]):
                a,b=before.formula(sheet,cell),after.formula(sheet,cell)
                if _serialized_key(a)!=_serialized_key(b):changed[sheet,cell]=(_serialized_key(a),_serialized_key(b))
            before._sheet_cache.pop(sheet,None);after._sheet_cache.pop(sheet,None)
        wanted={(item['sheet'],item['cell']):(_serialized_key(item['old_formula']),_serialized_key(item['new_formula'])) for item in plan['changes']}
        if changed!=wanted:raise ValueError('Des formules ont changé hors des 56 cibles du calendrier reconnues.')
    finally:before.close();after.close()
    if digest(old_path)!=old_profile['current_workbook_sha256'] or digest(new_path)!=new_profile['current_workbook_sha256']:
        raise ValueError('Un classeur a changé pendant le contrôle de la correction du calendrier fiscal.')
    certificate={'schema':'tca-fiscal-calendar-certificate/1','migration_id':MIGRATION_ID,
        'source_profile_sha256':old_profile['profile_sha256'],'source_sha256':digest(old_path),'output_sha256':digest(new_path),
        'changes':plan['changes'],'source_ids':list(dict.fromkeys(op['evidence_id'] for op in operations)),
        'qualification_exemptions':list(OWNERS),'rule_scope':'SELECTED_PERIOD_ERRORS_PRESERVED',
        'financial_outputs_verified':False,'native_proof_transfer':False}
    certificate['certificate_sha256']=_hash(certificate)
    result=deepcopy(new_profile);result.setdefault('reviewed_financial_migrations',[]).append(certificate)
    return seal_profile(result)


def verified_fiscal_calendar_exemptions(profile,workbook):
    """Exclude only these known reviewed formula edits from the variant gate.

The effective formula is checked again against current stable references. All
ordinary qualification, active-error and fresh WACC/calculation gates remain.
"""
    verify_profile(profile)
    certificates=profile.get('reviewed_financial_migrations',[])
    valid=[c for c in certificates if isinstance(c,dict) and c.get('schema')=='tca-fiscal-calendar-certificate/1'
        and c.get('migration_id')==MIGRATION_ID and c.get('certificate_sha256')==_hash({k:v for k,v in c.items() if k!='certificate_sha256'})
        and c.get('rule_scope')=='SELECTED_PERIOD_ERRORS_PRESERVED'
        and c.get('native_proof_transfer') is False and c.get('financial_outputs_verified') is False
        and set(c.get('qualification_exemptions',[]))==set(OWNERS) and len(c.get('changes',[]))==56]
    if not valid:return set()
    try:
        expected=expected_formulas(profile)
        if any(_key(workbook.formula(item['sheet'],item['cell']))!=_key(item['new_formula']) for item in expected):return set()
    except (ValueError,KeyError):return set()
    return set(OWNERS)


def prepare_fiscal_calendar_variant(engine,source,output,model_dir,evidence_id,*,runner=None,timeout=600):
    from .web_structure import prepare_variant
    from .web_model import seal_profile_model
    source,output,model_dir=Path(source).resolve(),Path(output).resolve(),Path(model_dir).resolve()
    receipt=output.with_suffix('.fiscal-calendar.json')
    if model_dir.exists() or receipt.exists() or model_dir==output.parent:raise ValueError('Destinations neuves distinctes requises.')
    plan=plan_fiscal_calendar_migration(engine,source,evidence_id)
    if plan['status']=='ALREADY_MIGRATED':return {k:v for k,v in plan.items() if k not in ('profile','operations')}
    prepared=prepare_variant(source,output,plan['profile'],plan['operations'],runner=runner,timeout=timeout)
    if not prepared['blocked']:
        prepared['profile']=certificate_fiscal_calendar_change(plan['profile'],source,output,prepared['profile'],plan['operations'])
        prepared['model_receipt']=seal_profile_model(engine,output,prepared['profile'],model_dir)
        prepared['model_dir']=str(model_dir)
    result={**prepared,'migration':{k:v for k,v in plan.items() if k not in ('profile','operations')}}
    atomic_json(receipt,result)
    return result
