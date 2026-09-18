"""Explicit DCF calendar repair: inactive years contribute no present value.

Only the ten known present-value formulas may change. Active-year formulas and
their errors are retained; this is not a general IFERROR or a financial input.
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

MIGRATION_ID='dcf-calendar/inactive-present-values-v1'
REASON=('Correction du calendrier DCF de 1 à 10 ans : exclure uniquement les années hors horizon '
        'du total des valeurs actualisées, sans masquer les erreurs des années actives.')
OWNERS=tuple('Valorisation!'+column+'33' for column in 'DEFGHIJKLM')


def _hash(value):return hashlib.sha256(canonical(value).encode()).hexdigest()


def _key(formula):
    # Optional OOXML sheet/function spelling only; absolute references and
    # quoted string contents remain significant, including inherited proofs.
    return _serialized_key(formula)


def _reference(profile,sheet,cell,local_sheet):
    target=map_location(profile,sheet,cell)
    if target is None:raise ValueError('Une référence du calendrier DCF a été supprimée : '+sheet+'!'+cell)
    prefix='' if target['sheet']==local_sheet else (
        target['sheet'] if re.fullmatch(r'[^\W\d]\w*',target['sheet']) else "'"+target['sheet'].replace("'","''")+"'")+'!'
    return prefix+target['cell']


def expected_formulas(profile):
    result=[]
    for column in 'DEFGHIJKLM':
        target=map_location(profile,'Valorisation',column+'33')
        if target is None:raise ValueError('Une valeur actualisée DCF a été supprimée.')
        ref=lambda sheet,cell:_reference(profile,sheet,cell,target['sheet'])
        flow,discount,fraction=(ref('Valorisation',column+str(row)) for row in (26,32,31))
        active=f'{flow}*{discount}*MAX(0,MIN(1,{fraction}))'
        fixed=f'IF({ref("Valorisation",column+"19")}>{ref("Control","C60")},0,{active})'
        result.append({**target,'owner':'Valorisation!'+column+'33','old_formula':active,'new_formula':fixed})
    return result


def plan_calendar_migration(engine,workbook,evidence_id):
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
            else:raise ValueError('Formule DCF différente du contrat reconnu : '+item['sheet']+'!'+item['cell'])
            versions.add(version)
            changes.append({**item,'old_formula':old})
        if len(versions)!=1:raise ValueError('Migration DCF partielle : réexaminer les dix formules avant application.')
    finally:actual.close()
    migrated=versions=={1}
    return {'schema':'tca-dcf-calendar-migration/1','migration_id':MIGRATION_ID,
        'status':'ALREADY_MIGRATED' if migrated else 'PROPOSED','profile':profile,'changes':changes,
        'source_sha256':digest(workbook),'active_year_errors_preserved':True,'financial_outputs_verified':False,
        'operations':[] if migrated else [{'type':'set_formula','sheet':item['sheet'],'cell':item['cell'],
            'formula':'='+item['new_formula'],'evidence_id':evidence_id,'reason':REASON} for item in changes]}


def certificate_calendar_change(old_profile,old_path,new_path,new_profile,operations):
    """Recognize exactly the reviewed ten-formula rule after a controlled preview."""
    verify_profile(old_profile);verify_profile(new_profile)
    if (not isinstance(operations,list) or len(operations)!=10
            or any(not isinstance(op,dict) or op.get('type')!='set_formula' for op in operations)):
        return new_profile
    try:
        targets=[map_location(old_profile,'Valorisation',column+'33') for column in 'DEFGHIJKLM']
    except (ValueError,KeyError):return new_profile
    if any(target is None for target in targets):return new_profile
    if {(op.get('sheet'),op.get('cell')) for op in operations}!={(target['sheet'],target['cell']) for target in targets}:
        return new_profile
    expected=expected_formulas(old_profile)
    keys={(item['sheet'],item['cell']) for item in expected}
    if {(op.get('sheet'),op.get('cell')) for op in operations}!=keys:return new_profile
    if (old_profile['sheets']!=new_profile['sheets'] or new_profile.get('parent_profile_sha256')!=old_profile['profile_sha256']
            or digest(old_path)!=old_profile['current_workbook_sha256'] or digest(new_path)!=new_profile['current_workbook_sha256']):
        raise ValueError('La correction DCF doit relier deux révisions exactes sans changement de structure.')
    reader=SimpleNamespace(profile=old_profile,_open=core.Workbook)
    try:plan=plan_calendar_migration(reader,old_path,operations[0].get('evidence_id'))
    except ValueError:return new_profile
    if plan['status']!='PROPOSED':return new_profile
    proposals={(op['sheet'],op['cell']):op for op in operations}
    if any(_key(proposals[item['sheet'],item['cell']].get('formula'))!=_key(item['new_formula'])
           or not isinstance(proposals[item['sheet'],item['cell']].get('evidence_id'),str)
           or not proposals[item['sheet'],item['cell']]['evidence_id'].strip() for item in expected):return new_profile
    before,after=core.Workbook(Path(old_path)),core.Workbook(Path(new_path))
    changed={}
    try:
        if list(before.sheets)!=list(after.sheets):raise ValueError('Une feuille a changé hors de la correction DCF.')
        for sheet in before.sheets:
            for cell in set(before.sheet(sheet)[1])|set(after.sheet(sheet)[1]):
                a,b=before.formula(sheet,cell),after.formula(sheet,cell)
                if _serialized_key(a)!=_serialized_key(b):changed[sheet,cell]=(_serialized_key(a),_serialized_key(b))
            before._sheet_cache.pop(sheet,None);after._sheet_cache.pop(sheet,None)
        wanted={(item['sheet'],item['cell']):(_serialized_key(item['old_formula']),_serialized_key(item['new_formula'])) for item in plan['changes']}
        if changed!=wanted:raise ValueError('Des formules ont changé hors des dix valeurs actualisées du calendrier DCF.')
    finally:before.close();after.close()
    if digest(old_path)!=old_profile['current_workbook_sha256'] or digest(new_path)!=new_profile['current_workbook_sha256']:
        raise ValueError('Un classeur a changé pendant le contrôle de la correction DCF.')
    certificate={'schema':'tca-dcf-calendar-certificate/1','migration_id':MIGRATION_ID,
        'source_profile_sha256':old_profile['profile_sha256'],'source_sha256':digest(old_path),'output_sha256':digest(new_path),
        'changes':plan['changes'],'source_ids':list(dict.fromkeys(op['evidence_id'] for op in operations)),
        'qualification_exemptions':list(OWNERS),'rule_scope':'INACTIVE_CALENDAR_ONLY_ACTIVE_FORMULAS_UNCHANGED',
        'financial_outputs_verified':False,'native_proof_transfer':False}
    certificate['certificate_sha256']=_hash(certificate)
    result=deepcopy(new_profile);result.setdefault('reviewed_financial_migrations',[]).append(certificate)
    return seal_profile(result)


def verified_calendar_exemptions(profile,workbook):
    """Exclude only these known reviewed formula edits from the variant gate.

The effective formula is checked again against current stable references. All
ordinary qualification, active-error and fresh WACC/calculation gates remain.
"""
    verify_profile(profile)
    certificates=profile.get('reviewed_financial_migrations',[])
    valid=[c for c in certificates if isinstance(c,dict) and c.get('schema')=='tca-dcf-calendar-certificate/1'
        and c.get('migration_id')==MIGRATION_ID and c.get('certificate_sha256')==_hash({k:v for k,v in c.items() if k!='certificate_sha256'})
        and c.get('rule_scope')=='INACTIVE_CALENDAR_ONLY_ACTIVE_FORMULAS_UNCHANGED'
        and c.get('native_proof_transfer') is False and c.get('financial_outputs_verified') is False
        and set(c.get('qualification_exemptions',[]))==set(OWNERS) and len(c.get('changes',[]))==10]
    if not valid:return set()
    try:
        expected=expected_formulas(profile)
        if any(_key(workbook.formula(item['sheet'],item['cell']))!=_key(item['new_formula']) for item in expected):return set()
    except (ValueError,KeyError):return set()
    return set(OWNERS)


def prepare_calendar_variant(engine,source,output,model_dir,evidence_id,*,runner=None,timeout=600):
    from .web_structure import prepare_variant
    from .web_model import seal_profile_model
    source,output,model_dir=Path(source).resolve(),Path(output).resolve(),Path(model_dir).resolve()
    receipt=output.with_suffix('.dcf-calendar.json')
    if model_dir.exists() or receipt.exists() or model_dir==output.parent:raise ValueError('Destinations neuves distinctes requises.')
    plan=plan_calendar_migration(engine,source,evidence_id)
    if plan['status']=='ALREADY_MIGRATED':return {k:v for k,v in plan.items() if k not in ('profile','operations')}
    prepared=prepare_variant(source,output,plan['profile'],plan['operations'],runner=runner,timeout=timeout)
    if not prepared['blocked']:
        prepared['profile']=certificate_calendar_change(plan['profile'],source,output,prepared['profile'],plan['operations'])
        prepared['model_receipt']=seal_profile_model(engine,output,prepared['profile'],model_dir)
        prepared['model_dir']=str(model_dir)
    result={**prepared,'migration':{k:v for k,v in plan.items() if k not in ('profile','operations')}}
    atomic_json(receipt,result)
    return result
