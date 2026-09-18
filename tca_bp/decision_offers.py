"""Qualified repeatable business blocks, derived from sealed template owners.

Unlike a free row insertion these operations register additional input owners,
reuse their constraints, and duplicate the calculation block on an isolated
Excel copy. New record contents are empty; client values are never copied.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import re

from .storage import canonical
from .vendor import input_engine as core
from .web_model_profile import (cell_parts, cell_name, sheet_record, map_location,
                               map_between_profiles, refresh_profile)

BUSINESS_TYPES = {'extend_register','extend_offer'}
# A payroll record is one complete calculation row. Other registers have
# companion cohort/tax blocks and require their own qualified recipe.
REGISTER_RECIPES = {'Effectifs': {'row':116,'columns':135}}
OFFER_BLOCKS = {
    'Assumptions':[(27,27)], 'DATA COGS':[(27,27)],
    'Revenue':[(24,24),(255,273)], 'COGS':[(24,24),(231,247)],
    'Contrats':[(48,50),(91,91),(108,108),(137,138),(155,155),(170,170),
                (187,187),(202,202),(219,219),(305,311),(410,417),(433,433),(450,450)],
    'ATELIER_CIR_IS':[(155,155),(364,370)], 'Sensi TCA':[(52,52),(68,68)],
    'KPI Dashboard':[(117,118)],
}


def extended_origin_schema(profile):
    schema=deepcopy(profile['origin_schema'])
    schema['offer_rows']=list(range(15,28))
    for extension in profile.get('business_extensions',[]):
        for owner in extension['owners']:
            sheet=owner['original_sheet'];address=owner['logical_cell']
            schema['cells'].setdefault(sheet,{})[address]=deepcopy(owner['spec'])
            logical_row=cell_parts(address)[1];source_row=cell_parts(owner['source_cell'])[1]
            register=schema.get('registers',{}).get(sheet)
            if register is not None:
                rows=register.setdefault('extra_rows',[])
                if logical_row not in rows:rows.append(logical_row)
            if sheet=='Assumptions' and extension['kind']=='extend_offer' and logical_row not in schema['offer_rows']:
                schema['offer_rows'].append(logical_row)
            for rule in schema.get('business_rules',[]):
                if rule.get('sheet')==sheet and source_row in rule.get('rows',[]) and logical_row not in rule['rows']:
                    rule['rows'].append(logical_row)
    return schema


def business_checks(profile, workbook, schema, changes):
    """Apply the original row contracts to each new, explicitly bound record."""
    if not profile.get('business_extensions'):
        return core.business_checks(workbook,schema,changes)
    schema=deepcopy(schema)
    original_schema=deepcopy(profile['origin_schema'])
    # Catalogue labels are stable owners, not necessarily one contiguous range
    # after qualified additions. Validate that source explicitly before using
    # the original rule engine for its other invariants.
    labels=[workbook.value('Assumptions','B'+str(r)) for r in schema.get('offer_rows',range(15,28))]
    for change in changes:
        spec=schema['cells'][change['sheet']][change['cell']]
        source=spec.get('choices_source',{})
        if source.get('sheet')=='Assumptions' and source.get('range','').replace('$','')=='B15:B27':
            if change['value'] is not None and change['value'] not in labels:
                raise ValueError('Le libellé ne fait pas partie du catalogue courant des offres.')
    for candidate in (schema,original_schema):
        for cells in candidate['cells'].values():
            for spec in cells.values():
                source=spec.get('choices_source',{})
                if source.get('sheet')=='Assumptions' and source.get('range','').replace('$','')=='B15:B27':
                    spec.pop('choices_source',None)
    owner_by_key={(o['original_sheet'],o['logical_cell']):(extension,o)
                  for extension in profile['business_extensions'] for o in extension['owners']}
    ordinary=[c for c in changes if (c['sheet'],c['cell']) not in owner_by_key]
    if ordinary:core.business_checks(workbook,schema,ordinary)
    groups={}
    for change in changes:
        match=owner_by_key.get((change['sheet'],change['cell']))
        if not match:continue
        extension,owner=match
        number=cell_parts(owner['logical_cell'])[1]
        key=(extension['id'],number if extension['kind']=='extend_register' else None)
        groups.setdefault(key,(extension,[]))[1].append(change)
    for (ident,number),(extension,updates) in groups.items():
        row_map={}
        for owner in extension['owners']:
            virtual=cell_parts(owner['logical_cell'])[1]
            if number is None or virtual==number:
                row_map[(owner['original_sheet'],cell_parts(owner['source_cell'])[1])]=virtual
        class RecordView:
            date1904=workbook.date1904
            def address(self,sheet,cell):
                col,row=cell_parts(cell)
                return core.colname(col)+str(row_map.get((sheet,row),row))
            def value(self,sheet,cell):return workbook.value(sheet,self.address(sheet,cell))
            def formula(self,sheet,cell):return workbook.formula(sheet,self.address(sheet,cell))
        translated=[]
        for change in updates:
            owner=owner_by_key[(change['sheet'],change['cell'])][1]
            translated.append({**change,'cell':owner['source_cell']})
        core.business_checks(RecordView(),original_schema,translated)


def extension_location(profile, owner):
    record=sheet_record(profile,owner['sheet_id'],allow_deleted=True)
    if record['deleted']:return None
    prefix=owner['transforms']
    if record['transforms'][:len(prefix)]!=prefix:
        raise ValueError('Historique de propriétaire métier incompatible.')
    from .web_model_profile import _axis
    col,row=cell_parts(owner['physical_cell'])
    for step in record['transforms'][len(prefix):]:
        if step['type'].endswith('_rows'):row=_axis(row,step)
        else:col=_axis(col,step)
        if row is None or col is None:return None
    address=cell_name(col,row)
    return {'sheet':record['name'],'cell':address,'sheet_id':record['id']} if address else None


def _blocks(profile, logical_blocks):
    result=[]
    for sheet,rows in logical_blocks.items():
        for first,last in rows:
            a=map_location(profile,sheet,'A'+str(first));b=map_location(profile,sheet,'EE'+str(last))
            if not a or not b or cell_parts(b['cell'])[1]-cell_parts(a['cell'])[1]!=last-first:
                raise ValueError('Le bloc métier modèle a été supprimé ou déformé : '+sheet)
            result.append({'sheet':a['sheet'],'sheet_id':a['sheet_id'],
                           'original_sheet':sheet,'original_first':first,'original_last':last,
                           'first':cell_parts(a['cell'])[1],'last':cell_parts(b['cell'])[1],
                           'last_column':cell_parts(b['cell'])[0]})
    return result


def plan_extension(profile, operation):
    """Return an expanded server-owned recipe and its additional stable owners."""
    op=deepcopy(operation);kind=op['type'];record=sheet_record(profile,op['sheet'])
    required={'type','sheet','count'} if kind=='extend_register' else {'type','sheet','name','family','sheets'}
    if not required<=set(op) or set(op)-required-{'reason','evidence_id'}:
        raise ValueError('Opération de bloc métier incomplète ou inconnue.')
    if not isinstance(op.get('evidence_id'),str) or not op['evidence_id'].strip():
        raise ValueError('Une source du dossier est requise pour étendre un bloc métier.')
    if kind=='extend_register':
        recipe=REGISTER_RECIPES.get(record['original_name'])
        if recipe is None:raise ValueError('L’extension de ce registre exige encore la qualification de ses blocs de calcul associés.')
        if type(op['count']) is not int or not 1<=op['count']<=50:
            raise ValueError('Étendre le registre de 1 à 50 lignes par lot.')
        blocks=_blocks(profile,{record['original_name']:[(recipe['row'],recipe['row'])]})
        multiplicity=op['count']
    else:
        if record['original_name']!='Assumptions' or op['family']!='produit_libre':
            raise ValueError('L’offre supplémentaire utilise le contrat explicite produit_libre.')
        if not isinstance(op['name'],str) or not 1<=len(op['name'].strip())<=150:
            raise ValueError('Un nom d’offre de 1 à 150 caractères est requis.')
        op['name']=op['name'].strip()
        expected=[sheet_record(profile,s,original=True)['name'] for s in [*OFFER_BLOCKS,'BFR']]
        if not isinstance(op['sheets'],list) or set(op['sheets'])!=set(expected):
            raise ValueError('Toutes les feuilles du bloc offre doivent être explicitement désignées.')
        blocks=_blocks(profile,OFFER_BLOCKS);multiplicity=1
    result=deepcopy(profile)
    ident='extension_'+hashlib.sha256((profile['profile_sha256']+canonical(op)).encode()).hexdigest()[:20]
    geometry=[]
    for block in sorted(blocks,key=lambda b:(b['sheet_id'],-b['first'])):
        step={'type':'insert_rows','index':block['first'],'count':(block['last']-block['first']+1)*multiplicity}
        sheet_record(result,block['sheet_id'])['transforms'].append(step)
        geometry.append({'sheet':block['sheet'],'sheet_id':block['sheet_id'],**step})
    clones=[];owners=[];virtual_base=900000+len(result.get('business_extensions',[]))*100
    if virtual_base+500>1048576:
        raise ValueError('Le profil a atteint sa capacité de propriétaires supplémentaires ; une migration de registre est requise.')
    for block in blocks:
        current=sheet_record(result,block['sheet_id'])
        old_start=map_between_profiles(profile,result,block['sheet'],'A'+str(block['first']))
        first=cell_parts(old_start['cell'])[1]
        size=block['last']-block['first']+1
        for copy_index in range(multiplicity):
            destination=first-size*(multiplicity-copy_index)
            clone={**block,'source_first':first,'source_last':first+size-1,
                   'destination_first':destination,'destination_last':destination+size-1}
            clones.append(clone)
            for address,spec in profile['origin_schema']['cells'].get(block['original_sheet'],{}).items():
                col,row=cell_parts(address)
                if not block['original_first']<=row<=block['original_last']:continue
                physical=map_location(profile,block['original_sheet'],address)
                c,r=cell_parts(physical['cell'])
                # Reserved logical addresses belong to the extension registry,
                # never to the original schema or to an inserted neighbouring cell.
                logical_row=virtual_base+copy_index+1
                if kind=='extend_offer':
                    logical_row+= {'ATELIER_CIR_IS':128,'Sensi TCA':300}.get(block['original_sheet'],0)
                    if block['original_sheet']=='Sensi TCA':logical_row+=block['original_first']
                owners.append({'id':ident+'_'+block['original_sheet']+'_'+address+'_'+str(copy_index),
                    'sheet_id':current['id'],'original_sheet':block['original_sheet'],
                    'logical_cell':core.colname(col)+str(logical_row),
                    'source_cell':address,'physical_cell':core.colname(c)+str(destination+r-block['first']),
                    'transforms':deepcopy(current['transforms']),'spec':deepcopy(spec)})
    extension={'id':ident,'kind':kind,'name':op.get('name'),'family':op.get('family'),
               'original_sheet':record['original_name'],'count':multiplicity,'owners':owners,
               'geometry':geometry,'clones':clones,'evidence_id':op['evidence_id']}
    result.setdefault('business_extensions',[]).append(extension)
    op.update(sheet=record['name'],sheet_id=record['id'],extension_id=ident,
              geometry=geometry,clones=clones)
    return op,result


def _append(d,case_id,operation,body,sheets):
    row=d.check_revision(case_id,body.get('expected_revision'))
    if d.work.draft(case_id).get('operations'):
        raise ValueError('Examiner et adopter le brouillon courant avant cette extension métier.')
    source=d.app.add_source(case_id,text=canonical(operation),title='Extension explicite d’un bloc métier')
    operation['evidence_id']=source['id']
    scope={'sheet':operation['sheet'],'sheets':sheets,'allow_structure':True}
    return d.work.add_operations(case_id,[operation],scope,origin='manual',expected_revision=row['revision'])


def prepare_register_extension(d,case_id,sheet,body):
    operation={'type':'extend_register','sheet':sheet,'count':body.get('count',1)}
    row=d.check_revision(case_id,body.get('expected_revision'))
    engine=d.app._engine_for_case(row)
    from .web_model_profile import initial_profile
    profile=initial_profile(engine,d.app._workbook(row))
    plan_extension(profile,{**operation,'evidence_id':'validation_only'})
    return _append(d,case_id,operation,body,[sheet])


def prepare_offer(d,case_id,body):
    row=d.check_revision(case_id,body.get('expected_revision'))
    from .web_model_profile import initial_profile
    profile=initial_profile(d.app._engine_for_case(row),d.app._workbook(row))
    sheet=sheet_record(profile,'Assumptions',original=True)['name']
    operation={'type':'extend_offer','sheet':sheet,'name':body.get('name'),
               'family':body.get('family','produit_libre'),
               'sheets':[sheet_record(profile,s,original=True)['name'] for s in [*OFFER_BLOCKS,'BFR']]}
    plan_extension(profile,{**operation,'evidence_id':'validation_only'})
    return _append(d,case_id,operation,body,
                   [sheet_record(profile,s,original=True)['name'] for s in [*OFFER_BLOCKS,'BFR']])


def rewrite_clone_formula(formula, sheet, before, after, clones):
    """Map A1 owners, including absolute references, into the cloned block.

    A whole catalogue range still addresses the whole catalogue. A range
    wholly owned by the source block addresses its new business counterpart.
    """
    from .web_model import _REF
    from .formula_bindings import bind_index_literals
    formula=bind_index_literals(formula,sheet,before,after)
    clean=re.sub(r'"(?:[^"]|"")*"',lambda m:' '*len(m[0]),formula)
    edits=[]
    for match in _REF.finditer(clean):
        name=match['sheet'] or sheet
        if name.startswith("'"):name=name[1:-1].replace("''","'")
        name=next((s['name'] for s in before['sheets'] if s['name'].casefold()==name.casefold()),name)
        bounds=match['range'].split(':')
        cols_rows=[cell_parts(a) for a in bounds]
        block=next((b for b in clones if b['sheet']==name and all(b['first']<=r<=b['last'] for c,r in cols_rows)),None)
        mapped=[]
        for address,(col,row) in zip(bounds,cols_rows):
            if block:
                target={'sheet':sheet_record(after,block['sheet_id'])['name'],
                        'cell':core.colname(col)+str(block['destination_first']+row-block['first'])}
            else:target=map_between_profiles(before,after,name,address)
            if not target:raise ValueError('Référence supprimée dans le bloc métier : '+name+'!'+address)
            c,r=cell_parts(target['cell'])
            mapped.append(('$' if address.startswith('$') else '')+core.colname(c)+('$' if '$' in address.lstrip('$') else '')+str(r))
        qualifier=("'"+target['sheet'].replace("'","''")+"'!") if match['sheet'] or target['sheet']!=sheet else ''
        edits.append((match.start(),match.end(),qualifier+':'.join(mapped)))
    for start,end,value in reversed(edits):formula=formula[:start]+value+formula[end:]
    return formula


def materialize_extension(workbook, before, after, operation):
    """Derive the exact contents for native serialization and preview evidence."""
    extension=next(e for e in after['business_extensions'] if e['id']==operation['extension_id'])
    clones=extension['clones'];cells=[]
    owned={(o['original_sheet'],o['source_cell']):o for o in extension['owners']}
    input_locations={(map_location(before,o['original_sheet'],o['source_cell'])['sheet'],
                      map_location(before,o['original_sheet'],o['source_cell'])['cell']) for o in extension['owners']}
    offer_index=13+sum(e['kind']=='extend_offer' for e in after['business_extensions'])
    if operation['type']=='extend_offer':
        for row in extended_origin_schema(before)['offer_rows']:
            for column,value in (('A','OFFRE_'+str(offer_index)),('B',operation['name'])):
                pos=map_location(before,'Assumptions',column+str(row))
                existing=workbook.value(pos['sheet'],pos['cell']) if pos else None
                if isinstance(existing,str) and existing.casefold()==value.casefold():
                    raise ValueError('Le nom ou identifiant de cette offre existe déjà dans le dossier.')
    # Convert the ordinal in the old offer's tax control into a stable ID lookup.
    ordinal_repairs=[]
    if operation['type']=='extend_offer':
        for col in range(16,136):
            position=map_location(before,'ATELIER_CIR_IS',core.colname(col)+'370')
            original=workbook.formula(position['sheet'],position['cell'])
            assumptions=sheet_record(before,'Assumptions',original=True)['name']
            one=map_location(before,'Assumptions','A27')['cell'];start=map_location(before,'Assumptions','A15')['cell']
            lookup="MATCH('"+assumptions.replace("'","''")+"'!"+one+",'"+assumptions.replace("'","''")+"'!"+start+':'+one+',0)'
            # Already bound by an earlier extension: retain its stable lookup.
            changed=re.sub(r'(SUMIF\([^,]+,)13,',lambda m:m[1]+lookup+',',original or '')
            if changed!=original:ordinal_repairs.append({**position,'before':original,'after':changed})
    ordinal={(r['sheet'],r['cell']):r['after'] for r in ordinal_repairs}
    for block in clones:
        live=sheet_record(after,block['sheet_id'])['name']
        merged_followers=set()
        for merged in workbook.sheet(block['sheet'])[0].findall('m:mergeCells/m:mergeCell',core.N):
            bounds=merged.get('ref').split(':');left,top=cell_parts(bounds[0]);right,bottom=cell_parts(bounds[-1])
            if bottom<block['first'] or top>block['last']:continue
            if top<block['first'] or bottom>block['last'] or right>block['last_column']:
                raise ValueError('Une fusion traverse la limite du bloc métier : '+block['sheet']+'!'+merged.get('ref'))
            merged_followers.update(core.colname(c)+str(r) for r in range(top,bottom+1)
                                    for c in range(left,right+1) if (c,r)!=(left,top))
        for address,node in workbook.sheet(block['sheet'])[1].items():
            col,row=cell_parts(address)
            if not block['first']<=row<=block['last'] or col>block['last_column']:continue
            # The native range copy owns and preserves the entire merge. Only
            # its anchor stores content; clearing a follower would clear it too.
            if address in merged_followers:continue
            formula=ordinal.get((block['sheet'],address),workbook.formula(block['sheet'],address))
            target=core.colname(col)+str(block['destination_first']+row-block['first'])
            if formula:
                ordered=[block,*[b for b in clones if b is not block]]
                cells.append({'sheet':live,'cell':target,'formula':rewrite_clone_formula(formula,block['sheet'],before,after,ordered)})
            else:
                value=None if (block['sheet'],address) in input_locations else workbook.value(block['sheet'],address)
                if isinstance(value,str) and operation['type']=='extend_offer':value=value.replace('Offre 13','Offre '+str(offer_index))
                cells.append({'sheet':live,'cell':target,'value':value})
    if operation['type']=='extend_offer':
        def current(sheet,cell):return map_location(after,sheet,cell)
        def cloned(sheet,cell):
            old=map_location(before,sheet,cell);c,r=cell_parts(old['cell'])
            block=next(b for b in clones if b['sheet_id']==old['sheet_id'] and b['first']<=r<=b['last'])
            return {'sheet':sheet_record(after,old['sheet_id'])['name'],'cell':core.colname(c)+str(block['destination_first']+r-block['first'])}
        def ref(target):return "'"+target['sheet'].replace("'","''")+"'!"+target['cell']
        for address,value in [('A27','OFFRE_'+str(offer_index)),('B27',operation['name']),('C27',0)]:
            target=cloned('Assumptions',address)
            cells=[c for c in cells if (c['sheet'],c['cell'])!=(target['sheet'],target['cell'])]
            cells.append({**target,'value':value})
        contributions={'Revenue':{282:264,283:268,284:269,285:270,286:271,287:272,288:259,290:258},
                       'COGS':{253:243,254:244,255:242},
                       'ATELIER_CIR_IS':{184:364,185:365,186:366,208:367,209:368,210:369}}
        for sheet,rows in contributions.items():
            for target_row,source_row in rows.items():
                for col in range(16,136):
                    name=core.colname(col);old=map_location(before,sheet,name+str(target_row))
                    formula=workbook.formula(old['sheet'],old['cell'])
                    if not formula:raise ValueError('Total financier attendu absent : '+sheet+'!'+name+str(target_row))
                    # Existing totals keep existing owners; only the new term
                    # refers to the cloned block.
                    moved=rewrite_clone_formula(formula,old['sheet'],before,after,[])
                    cells.append({**current(sheet,name+str(target_row)), 'formula':moved+'+'+ref(cloned(sheet,name+str(source_row)))})
        for col in range(16,136):
            name=core.colname(col)
            for row in (312,313):
                old=map_location(before,'Contrats',name+str(row));formula=workbook.formula(old['sheet'],old['cell'])
                if not formula or not formula.startswith('MAX(0,') or not formula.endswith(')'):
                    raise ValueError('Contrôle de carnet incompatible avec la recette qualifiée.')
                def cumulative(sheet,r):
                    first=cloned(sheet,'P'+str(r));last=cloned(sheet,name+str(r))
                    return 'SUM('+ref(first)+':'+last['cell']+')'
                if row==312:
                    term='IF(AND('+ref(cloned('Assumptions','C27'))+'=1,'+ref(cloned('Assumptions','E27'))+'<>"Non"),'+cumulative('Contrats',48)+'-'+cumulative('Contrats',308)+',0)'
                else:term=cumulative('Contrats',91)+'-'+cumulative('Revenue',264)
                moved=rewrite_clone_formula(formula,old['sheet'],before,after,[])
                cells.append({**current('Contrats',name+str(row)),'formula':moved[:-1]+'+'+term+')'})
        # The small conditions display is horizontal; extend only its empty
        # cells, without inserting a column through the monthly cash calendar.
        for row in (67,70,74,75,76,77,78):
            origin=map_location(before,'BFR','Q'+str(row))
            c,r=cell_parts(origin['cell']);destination=core.colname(c+offer_index-13)+str(r)
            if workbook.value(origin['sheet'],destination) is not None or workbook.formula(origin['sheet'],destination):
                raise ValueError('La place du nouvel affichage BFR est occupée : '+destination)
            formula=workbook.formula(origin['sheet'],origin['cell'])
            cells.append({'sheet':origin['sheet'],'cell':destination,
                          'formula':rewrite_clone_formula(formula,origin['sheet'],before,after,clones)})
    return {**operation,'cells':cells,'content_sha256':hashlib.sha256(canonical(cells).encode()).hexdigest()},ordinal_repairs
