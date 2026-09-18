"""Controlled Excel edits on exclusive copies; no adoption and no VBA execution."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import io
import json
import math
import os
import posixpath
from pathlib import Path
import queue
import re
import subprocess
import threading
import time
import uuid
import zipfile
from xml.etree import ElementTree as ET

from .storage import atomic_json, canonical, digest
from .vendor import input_engine as core
from .web_model_profile import (MAX_COL, MAX_ROW, cell_parts, initial_profile, map_location,
                                refresh_profile, seal_profile, sheet_record, verify_profile)

STRUCTURAL = {'insert_rows','delete_rows','insert_columns','delete_columns','add_sheet','rename_sheet','move_sheet','delete_sheet', 'extend_register','extend_offer'}
SETTERS = {'set_value','set_formula'}


def _name(value):
    if (not isinstance(value, str) or not 1 <= len(value) <= 31 or value != value.strip()
            or any(c in value for c in ':\\/?*[]') or value.startswith("'") or value.endswith("'")
            or any(ord(c) < 32 for c in value)):
        raise ValueError('Nom de feuille Excel invalide (1 à 31 caractères).')
    return value


def _integer(value, maximum, label):
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError(label + ' : entier 1-based hors limites.')
    return value


def plan_operations(profile, operations):
    verify_profile(profile)
    from .web_blocks import expand_operations, ExpandedOperations
    operations=expand_operations(operations)
    if len(operations)>1 and any(isinstance(o,dict) and o.get('type') in ('extend_register','extend_offer') for o in operations):
        raise ValueError('Examiner et adopter l’extension métier seule avant de saisir les nouvelles entrées.')
    result, normalized = deepcopy(profile), ExpandedOperations(envelope_count=operations.envelope_count, contains_blocks=operations.contains_blocks)
    result['parent_profile_sha256'] = profile['profile_sha256']
    result['version'] += 1
    for raw in operations:
        if not isinstance(raw, dict) or raw.get('type') not in STRUCTURAL | SETTERS:
            raise ValueError('Type d’opération inconnu.')
        if raw['type'] in ('extend_register','extend_offer'):
            from .decision_offers import plan_extension
            operation,result=plan_extension(result,raw)
            normalized.append(operation)
            continue
        operation = deepcopy(raw)
        kind = operation['type']
        keys = {'type'} | ({'name','role'} if kind == 'add_sheet' else {'sheet'})
        if kind in SETTERS:
            keys |= {'cell','value' if kind == 'set_value' else 'formula','evidence_id'}
        elif kind.endswith('_rows') or kind.endswith('_columns'):
            keys |= {'index','count'}
        elif kind == 'rename_sheet': keys.add('name')
        elif kind == 'move_sheet': keys.add('index')
        optional = {'reason', 'evidence_id'}
        if kind == 'set_value':
            optional.add('status')
            if 'status' in operation and operation['status'] not in ('CONFIRME','HYPOTHESE','NON_RENSEIGNE'):
                raise ValueError('État documentaire invalide.')
        if not keys <= set(operation) or set(operation) - keys - optional:
            raise ValueError('Clés manquantes ou inconnues pour ' + kind)
        if 'reason' in operation and (not isinstance(operation['reason'], str) or len(operation['reason']) > 4000):
            raise ValueError('Justification textuelle limitée à 4 000 caractères.')
        if 'evidence_id' in operation and (not isinstance(operation['evidence_id'], str) or not operation['evidence_id'].strip()):
            raise ValueError('Identifiant de source invalide.')
        live = [s for s in result['sheets'] if not s['deleted']]
        if kind == 'add_sheet':
            name = _name(operation['name'])
            if any(s['name'].casefold() == name.casefold() for s in live):
                raise ValueError('Le nom de feuille existe déjà.')
            if not isinstance(operation['role'], str) or not 3 <= len(operation['role'].strip()) <= 2000:
                raise ValueError('Un rôle métier explicite est requis pour la nouvelle feuille.')
            ident = 'sheet_' + hashlib.sha256((profile['profile_sha256'] + canonical(normalized) + canonical(operation)).encode()).hexdigest()[:20]
            result['sheets'].append({'id':ident,'name':name,'original_name':None,'index':len(live)+1,
                                     'deleted':False,'transforms':[],'role':operation['role']})
            operation['sheet_id'] = ident
        else:
            record = sheet_record(result, operation['sheet'])
            operation.update(sheet=record['name'], sheet_id=record['id'])
            if kind in SETTERS:
                col, row = cell_parts(operation['cell'])
                operation['cell'] = core.colname(col) + str(row)
                if not isinstance(operation['evidence_id'], str) or not operation['evidence_id'].strip():
                    raise ValueError('Une preuve du dossier est requise pour chaque valeur ou formule.')
                if kind == 'set_formula':
                    formula = operation['formula']
                    if not isinstance(formula, str) or not 1 <= len(formula) <= 8192:
                        raise ValueError('Formule Excel requise, au plus 8 192 caractères.')
                    formula = formula.strip().removeprefix('=')
                    if (not formula or any(ord(c) < 32 for c in formula)
                            or any(c in formula for c in '[]|')
                            or re.search(r'\b(?:WEBSERVICE|HYPERLINK|RTD|CALL|EXEC|REGISTER|DDE)\s*\(', formula, re.I)):
                        raise ValueError('Référence externe, service ou code exécutable interdit dans une formule.')
                    clean=re.sub(r'"(?:[^\"]|\"\")*"','""',formula)
                    qualifiers=re.findall(r"('(?:[^']|'')+'|[\w.]+(?::[\w.]+)?)!",clean)
                    current_names={s['name'].casefold() for s in live}
                    for qualifier in qualifiers:
                        name=qualifier[1:-1].replace("''", "'") if qualifier.startswith("'") else qualifier
                        if any(part.casefold() not in current_names for part in name.split(':')):
                            raise ValueError('Créer ou renommer la feuille référencée avant cette formule : '+name)
                    operation['formula'] = formula
                    result['formula_changes'].append({'sheet_id':record['id'],'cell':operation['cell'],
                                                       'formula':formula,'evidence_id':operation['evidence_id'],
                                                       'profile_version':result['version']})
                else:
                    value = operation['value']
                    if (value is not None and type(value) not in (str, int, float, bool)
                            or type(value) is float and not math.isfinite(value)
                            or isinstance(value, str) and (len(value) > 32767 or any(ord(c) < 32 and c not in '\t\n\r' for c in value))):
                        raise ValueError('Valeur Excel scalaire finie requise.')
                    # Leading '=' remains literal data, never an implicit formula.
                    result['value_changes'].append({'sheet_id':record['id'],'cell':operation['cell'],
                                                     'evidence_id':operation['evidence_id'],'profile_version':result['version']})
            elif kind.endswith('_rows') or kind.endswith('_columns'):
                maximum = MAX_ROW if kind.endswith('_rows') else MAX_COL
                index = _integer(operation['index'], maximum, 'Position')
                count = _integer(operation['count'], min(maximum, 10000), 'Nombre')
                if index + count - 1 > maximum:
                    raise ValueError('La bande dépasse les limites Excel.')
                record['transforms'].append({'type':kind,'index':index,'count':count})
            elif kind == 'rename_sheet':
                name = _name(operation['name'])
                if any(s['id'] != record['id'] and s['name'].casefold() == name.casefold() for s in live):
                    raise ValueError('Le nom de feuille existe déjà.')
                record['name'] = name
            elif kind == 'delete_sheet':
                if len(live) == 1:
                    raise ValueError('La dernière feuille ne peut être supprimée.')
                record['deleted'] = True
            elif kind == 'move_sheet':
                destination = _integer(operation['index'], len(live), 'Ordre de feuille')
                ordered = sorted(live, key=lambda s:s['index'])
                ordered.remove(record); ordered.insert(destination-1, record)
                for index, item in enumerate(ordered, 1): item['index'] = index
        # Normalize order after deletion; deleted identities remain in the audit.
        for index, record in enumerate(sorted((s for s in result['sheets'] if not s['deleted']), key=lambda s:s['index']), 1):
            record['index'] = index
        normalized.append(operation)
    # Geometry/audit identifiers are reusable metadata; literal answers remain
    # in the case transaction, never in the business-profile history.
    result['operations'].extend({k:v for k,v in op.items() if k not in ('value', 'formula', 'reason')} for op in normalized)
    result['qualification_status'] = 'VARIANTE_A_QUALIFIER'
    result['native_results_valid'] = False
    return normalized, refresh_profile(result)


def validate_operations(operations, profile):
    return plan_operations(profile, operations)[0]


def operation_targets(profile, operations):
    """Final location of each setter after ALL subsequent operations.

    Return [{operation_index, type, sheet, cell, deleted, superseded}]. Index
    is zero-based in the supplied operation list; all Excel indexes are 1-based.
    Works also for newly added sheets/cells, which have no original owner.
    """
    from .web_model_profile import _axis, cell_name
    normalized, final = plan_operations(profile, operations)
    result=[]; subsequent={}; deleted_sheets=set(); seen=set()
    for index in range(len(normalized)-1,-1,-1):
        operation=normalized[index];kind=operation['type'];ident=operation.get('sheet_id')
        if kind in SETTERS:
            col,row=cell_parts(operation['cell']);deleted=ident in deleted_sheets
            for step in reversed(subsequent.get(ident,[])):
                if deleted:break
                if step['type'].endswith('_rows'):row=_axis(row,step)
                else:col=_axis(col,step)
                if row is None or col is None:deleted=True
            record=sheet_record(final,ident,allow_deleted=True)
            address=cell_name(col,row) if not deleted else None
            key=(ident,address)
            result.append({'operation_index':index,'type':kind,'sheet_id':ident,
                           'sheet':record['name'] if address else None,'cell':address,
                           'deleted':address is None,'superseded':address is not None and key in seen})
            if address:seen.add(key)
        elif kind in ('extend_register','extend_offer'):
            for step in reversed(operation['geometry']):subsequent.setdefault(step['sheet_id'],[]).append(step)
        elif kind=='delete_sheet':deleted_sheets.add(ident)
        elif kind.endswith('_rows') or kind.endswith('_columns'):subsequent.setdefault(ident,[]).append(operation)
    return list(reversed(result))


def _vba_sources(data):
    from .vendor.vba_fingerprint import _vendor
    result = {}
    with _vendor().OleFileIO(io.BytesIO(data)) as ole:
        for path in ole.listdir(streams=True, storages=False):
            if len(path) != 2 or path[0] != 'VBA' or path[1].startswith(('_','dir')):
                continue
            stream = ole.openstream(path).read()
            for offset, char in enumerate(stream):
                if char != 1: continue
                try: source = _vba_decompress(stream[offset:])
                except (ValueError, IndexError, OverflowError): continue
                if b'Attribute VB_Name' not in source: continue
                body = b'\n'.join(line.strip() for line in source.splitlines()
                                  if line.strip() and not line.lstrip().startswith(b'Attribute '))
                result[path[1]] = {'sha256':hashlib.sha256(source).hexdigest(),'empty':not bool(body)}
                break
            else:
                raise ValueError('Source VBA illisible : ' + path[1])
    return result


def _vba_decompress(data):
    """Bounded MS-OVBA source reader, copied from the audited build reader."""
    if not data or data[0] != 1: raise ValueError('Not compressed VBA')
    out = bytearray(); pos = 1
    while pos + 2 <= len(data):
        header = int.from_bytes(data[pos:pos+2], 'little'); size = (header & 0xfff) + 3
        if ((header >> 12) & 7) != 3: raise ValueError('Invalid VBA chunk')
        end = min(pos + size, len(data)); pos += 2; start = len(out)
        if not header & 0x8000:
            out.extend(data[pos:end]); pos = end; continue
        while pos < end:
            flags = data[pos]; pos += 1
            for bit in range(8):
                if pos >= end: break
                if flags & (1 << bit):
                    if pos + 2 > end: raise ValueError('Truncated VBA token')
                    token = int.from_bytes(data[pos:pos+2], 'little'); pos += 2
                    bits = max(4, (len(out)-start-1).bit_length()); mask = 0xffff >> bits
                    length = (token & mask)+3; offset = (token >> (16-bits))+1
                    if offset > len(out)-start: raise ValueError('Invalid VBA offset')
                    for _ in range(length): out.append(out[-offset])
                else: out.append(data[pos]); pos += 1
                if len(out) > 2_000_000: raise ValueError('VBA source bound exceeded')
    return bytes(out)


def _invalidate_variant(path, profile, targets):
    """Discard old cached financial results after native serialization."""
    import tempfile
    from .model_runtime import invalidate_caches, invalidate_chart
    wb = core.Workbook(path); temp = None
    preserve = {(t['sheet'],t['cell']) for t in targets if not t['deleted'] and not t['superseded']}
    native = {}
    for kind in ('native_outputs','native_table_outputs'):
        for sheet, cells in profile['origin_schema'].get(kind,{}).items():
            for cell in cells:
                target = map_location(profile,sheet,cell)
                if target and (target['sheet'],target['cell']) not in preserve:
                    native.setdefault(target['sheet'],set()).add(target['cell'])
    try:
        fd, name = tempfile.mkstemp(prefix='.web-cache-',suffix='.xlsm',dir=path.parent);os.close(fd);temp=Path(name)
        parts = {meta['part']:sheet for sheet,meta in wb.sheets.items()}
        with zipfile.ZipFile(temp,'w') as archive:
            for info in wb.z.infolist():
                raw=wb.z.read(info.filename)
                if info.filename in parts:
                    addresses=native.get(parts[info.filename],set())
                    def clear(match):
                        return core.xml_cell(match[0],None,'text') if match[1].decode() in addresses and not re.search(rb'<f(?:\s|>)',match[0]) else match[0]
                    raw=invalidate_caches(core.CELL_RX.sub(clear,raw))
                elif info.filename.startswith('xl/charts/') and info.filename.endswith('.xml'):raw=invalidate_chart(raw)
                elif info.filename=='xl/workbook.xml':raw=core.mark_for_native_calculation(raw)
                archive.writestr(info,raw)
        wb.close(); os.replace(temp,path)
    finally:
        wb.close()
        if temp:temp.unlink(missing_ok=True)


def vba_preservation(before, after):
    if before == after:
        return {'preserved':True,'binary_identical':True,'source_verified':True,'empty_module_changes':[]}
    try:
        left, right = _vba_sources(before), _vba_sources(after)
    except (ValueError, OSError) as error:
        return {'preserved':False,'binary_identical':False,'source_verified':False,'error':str(error)}
    changed = [name for name in left.keys() | right.keys()
               if left.get(name) != right.get(name) and not (left.get(name,{}).get('empty',True) and right.get(name,{}).get('empty',True))]
    return {'preserved':not changed,'binary_identical':False,'source_verified':not changed,
            'changed_code_modules':changed,'empty_module_changes':sorted(left.keys() ^ right.keys()),
            'compiled_streams_identical':False,'macros_executed':False,
            'notice':'Comparaison des sources VBA ; les métadonnées/modules de feuille vides peuvent changer avec Excel.'}


def workbook_diagnostics(path):
    """Inspect native saved references without claiming financial correctness."""
    wb = core.Workbook(Path(path)); errors=[]; names=[]; validations=[]; tables=[]; protections={}
    edges = {name:set() for name in wb.sheets}; formula_count=0; ref_count=0; dynamic=[]
    owned={name:{'defined_names':0,'validations':[],'native_tables':[],'charts':0} for name in wb.sheets}
    owned['__workbook__']={'defined_names':0,'validations':[],'native_tables':[],'charts':0}
    from .web_model import formula_references
    def check_references(formula, location):
        clean=re.sub(r'"(?:[^"]|"")*"','""',formula)
        if '#REF!' in clean.upper():
            errors.append({'severity':'ERROR','code':'FORMULA_REF',**location})
        qualifiers=re.findall(r"('(?:[^']|'')+'|[\w.]+)!",clean)
        existing={name.casefold() for name in wb.sheets}
        for qualifier in qualifiers:
            target=qualifier[1:-1].replace("''", "'") if qualifier.startswith("'") else qualifier
            # A literal reference must name an existing sheet. A 3D range
            # validates both endpoints; dynamic INDIRECT remains a warning.
            for part in target.split(':'):
                if part.casefold() not in existing:
                    errors.append({'severity':'ERROR','code':'MISSING_SHEET_REFERENCE','referenced_sheet':part,**location})
    def related(part, kind):
        rel=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
        if rel not in wb.z.namelist():return []
        return [posixpath.normpath(posixpath.join(posixpath.dirname(part),node.get('Target',''))).lstrip('/')
                if not node.get('Target','').startswith('/') else node.get('Target','').lstrip('/')
                for node in ET.fromstring(wb.z.read(rel)) if node.get('Type','').endswith('/'+kind) and node.get('TargetMode')!='External']
    try:
        for name, meta in wb.sheets.items():
            tree,cells,_ = wb.sheet(name)
            groups={}
            for address,node in cells.items():
                f=node.find('m:f',core.N)
                if f is not None and f.get('t')=='shared':groups.setdefault(f.get('si'),[]).append((address,f))
            invalid_shared=set()
            for ident,members in groups.items():
                anchors=[(a,f) for a,f in members if f.text]
                broken=ident is None or len(anchors)!=1
                if not broken:
                    area=anchors[0][1].get('ref','')
                    try:
                        start,end=(area.split(':')*2)[:2] if ':' not in area else area.split(':')
                        left,top=cell_parts(start);right,bottom=cell_parts(end)
                        broken=any(not(left<=cell_parts(a)[0]<=right and top<=cell_parts(a)[1]<=bottom) for a,_ in members)
                    except (ValueError,TypeError):broken=True
                if broken:
                    invalid_shared.update(a for a,_ in members)
                    errors.append({'severity':'ERROR','code':'INVALID_SHARED_FORMULA_GROUP','sheet':name,'group':ident,'cells':[a for a,_ in members]})
            protection=tree.find('m:sheetProtection',core.N)
            protections[name]=dict(protection.attrib) if protection is not None else None
            for address,node in cells.items():
                if address in invalid_shared:continue
                formula=wb.formula(name,address)
                if formula is None: continue
                formula_count+=1
                check_references(formula,{'sheet':name,'cell':address})
                refs=formula_references(formula,name); ref_count+=len(refs)
                for ref in refs:
                    match=re.match(r"'((?:[^']|'')*)'!",ref)
                    if match and match[1].replace("''", "'") in edges: edges[name].add(match[1].replace("''", "'"))
                if re.search(r'\b(?:INDIRECT|OFFSET)\s*\(',formula,re.I):
                    if len(dynamic)<100:dynamic.append({'sheet':name,'cell':address})
                f=node.find('m:f',core.N)
                if f.get('t')=='dataTable':
                    tables.append({'sheet':name,'cell':address,**f.attrib})
                    owned[name]['native_tables'].append(address)
            for dv in tree.findall('m:dataValidations/m:dataValidation',core.N):
                formulas=[c.text or '' for c in dv if c.tag.rsplit('}',1)[-1] in ('formula1','formula2')]
                validations.append({'sheet':name,'range':dv.get('sqref'),'type':dv.get('type'),'formulas':formulas})
                owned[name]['validations'].append(dv.get('sqref',''))
                for formula in formulas:check_references(formula,{'sheet':name,'range':dv.get('sqref')})
                if any('#REF!' in x for x in formulas):errors.append({'severity':'ERROR','code':'VALIDATION_REF','sheet':name,'range':dv.get('sqref')})
            owned[name]['charts']=sum(len(related(drawing,'chart')) for drawing in related(meta['part'],'drawing'))
            wb._sheet_cache.pop(name,None)
        for node in wb.wb.findall('m:definedNames/m:definedName',core.N):
            item={'name':node.get('name'),'localSheetId':node.get('localSheetId'),'text':node.text or ''};names.append(item)
            scope=list(wb.sheets)[int(item['localSheetId'])] if str(item['localSheetId']).isdigit() and int(item['localSheetId'])<len(wb.sheets) else '__workbook__'
            owned[scope]['defined_names']+=1
            check_references(item['text'],{'name':item['name']})
            if '#REF!' in item['text']:errors.append({'severity':'ERROR','code':'DEFINED_NAME_REF','name':item['name']})
        external_parts=[];external_relationships=[]
        for name in wb.z.namelist():
            if name.startswith('xl/externalLinks/') and name.endswith('.xml'):
                external_parts.append(name)
            if name.endswith('.rels'):
                for node in ET.fromstring(wb.z.read(name)):
                    kind=node.get('Type','')
                    if kind.rsplit('/',1)[-1] in ('externalLink','externalLinkPath'):
                        # Relationship IDs may change during Excel serialization;
                        # the component, type and target identify the actual link.
                        external_relationships.append({'part':name,'type':kind,
                            'target':node.get('Target',''),'target_mode':node.get('TargetMode','Internal')})
            if name.startswith('xl/charts/') and name.endswith('.xml') and b'#REF!' in wb.z.read(name):
                errors.append({'severity':'ERROR','code':'CHART_REF','component':name})
            if re.fullmatch(r'xl/charts/chart\d+\.xml',name):
                for node in ET.fromstring(wb.z.read(name)).iter():
                    if node.tag.rsplit('}',1)[-1]=='f':check_references(node.text or '',{'component':name})
        return {'errors':errors,'defined_names':names,'validations':validations,'native_tables':tables,
                'protections':protections,'workbook_protection':core.canonical_xml(wb.wb.find('m:workbookProtection',core.N)),
                'component_owners':owned,
                'external_links':{'parts':sorted(external_parts),
                                  'relationships':sorted(external_relationships,key=canonical)},
                'component_counts':{'defined_names':len(names),'validations':len(validations),'native_tables':len(tables),
                    'charts':sum(bool(re.fullmatch(r'xl/charts/chart\d+\.xml',name)) for name in wb.z.namelist())},
                'graph':{'sheets':{k:sorted(v) for k,v in edges.items()},'formula_count':formula_count,'reference_count':ref_count,
                         'dynamic_references':dynamic,'coverage_complete':False},
                'sheet_names':list(wb.sheets),'vba':wb.z.read('xl/vbaProject.bin') if 'xl/vbaProject.bin' in wb.z.namelist() else b''}
    finally:wb.close()


def _protection_flags(attributes):
    if attributes is None:return None
    denied={'formatCells','formatColumns','formatRows','insertColumns','insertRows','insertHyperlinks',
            'deleteColumns','deleteRows','sort','autoFilter','pivotTables'}
    flags=denied|{'sheet','objects','scenarios','selectLockedCells','selectUnlockedCells'}
    return {key:attributes.get(key,'1' if key in denied else '0') in ('1','true') for key in sorted(flags)}


def _range_survives(area, transforms):
    """Track a rectangular owner without expanding a million-cell validation."""
    for part in area.split():
        ends=part.split(':'); left,top=cell_parts(ends[0]);right,bottom=cell_parts(ends[-1])
        axes=[[left,right],[top,bottom]]
        for op in transforms:
            axis=axes[1 if op['type'].endswith('_rows') else 0]
            first,last=axis;index,count=op['index'],op['count']
            if op['type'].startswith('insert_'):
                if index<=first:axis[0]+=count
                if index<=last:axis[1]+=count
            elif index<=last:
                end=index+count-1
                if index<=first and end>=last:
                    axes=None;break
                axis[0]=first-count if first>end else min(first,index)
                axis[1]=last-count if last>end else index-1
        if axes is not None:return True
    return False


def _repair_groups(repairs):
    """Contiguous runs only: a native matrix never overwrites a gap or neighbour."""
    groups=[];previous=None
    for index,repair in enumerate(repairs):
        col,row=cell_parts(repair['cell']);key=(repair['sheet'],row,col)
        if previous and key==(previous[0],previous[1],previous[2]+1):groups[-1].append(index)
        else:groups.append([index])
        previous=key
    return groups


def _run_native(source, output, operations, *, timeout=600, reference_repairs=None):
    from .wacc_native import OwnedExcelProcess, existing_excel_pids
    folder=output.parent/('.web-structure-'+uuid.uuid4().hex);folder.mkdir()
    request=folder/'request.json';receipt=folder/'receipt.json'
    atomic_json(request,{'source':str(source),'output':str(output),'receipt':str(receipt),
                         'source_sha256':digest(source),'operations':operations,
                         'reference_repairs':reference_repairs or [],
                         'reference_repair_groups':_repair_groups(reference_repairs or [])})
    windows=Path(os.environ.get('SystemRoot',r'C:\Windows'))
    ps=windows/'System32/WindowsPowerShell/v1.0'
    env=os.environ.copy();env['PSModulePath']=os.pathsep.join((str(ps/'Modules'),str(Path(os.environ.get('ProgramFiles',r'C:\Program Files'))/'WindowsPowerShell/Modules')))
    args=[str(ps/'powershell.exe'),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(Path(__file__).with_name('web_structure_worker.ps1')),'-RequestPath',str(request)]
    previous=existing_excel_pids();owned=None;complete=False
    process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,encoding='utf8',env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    messages=queue.Queue()
    def read():
        try:
            for line in process.stdout:messages.put(json.loads(line.lstrip('\ufeff')))
        except Exception as error:messages.put({'event':'error','error':str(error)})
        finally:messages.put({'event':'closed'})
    threading.Thread(target=read,daemon=True).start()
    threading.Thread(target=lambda:list(process.stderr),daemon=True).start()
    start=time.monotonic()
    try:
        while True:
            try: message=messages.get(timeout=max(.01,timeout-(time.monotonic()-start)))
            except queue.Empty:raise ValueError('Délai maximal de modification Excel dépassé.')
            if time.monotonic()-start>timeout:raise ValueError('Délai maximal de modification Excel dépassé.')
            if message.get('event')=='owned_process':
                pid=message.get('pid')
                if owned or type(pid) is not int or pid<=0 or pid in previous:raise ValueError('Instance Excel non dédiée.')
                owned=OwnedExcelProcess(pid);process.stdin.write('{"operation":"ownership_confirmed"}\n');process.stdin.flush()
            elif message.get('event')=='saved' and owned:break
            elif message.get('event')=='progress' and owned:continue
            else:raise ValueError(message.get('error','Réponse Excel inattendue.'))
        process.stdin.close();process.wait(timeout=max(.01,timeout-(time.monotonic()-start)))
        result=json.loads(receipt.read_text(encoding='utf-8-sig'))
        if process.returncode or result.get('source_sha256')!=digest(source) or result.get('output_sha256')!=digest(output) or result.get('macros_enabled') is not False:
            raise ValueError('Reçu de modification Excel incohérent.')
        complete=True;return result
    finally:
        from .native_cleanup import finish_native_process
        finish_native_process(process, owned, complete)


def _formula_key(formula):
    """Normalize optional simple-sheet quotes, never string values or $ refs."""
    parts=re.split(r'("(?:[^"]|"")*")',(formula or '').strip().removeprefix('='))
    for index in range(0,len(parts),2):
        parts[index]=re.sub(r"'([^\W\d]\w*)'!",r'\1!',parts[index])
        # OOXML future-function spelling of the same built-in Excel function.
        parts[index]=parts[index].replace('_xlfn.AGGREGATE(', 'AGGREGATE(')
    return ''.join(parts)


def prepare_variant(source:Path, output:Path, profile:dict, operations:list[dict], *, runner=None, timeout=600):
    source,output=Path(source).resolve(),Path(output).resolve()
    verify_profile(profile)
    if source==output or output.exists() or output.with_suffix('.variant.json').exists() or not source.is_file() or source.suffix.lower()!='.xlsm' or output.suffix.lower()!='.xlsm':
        raise ValueError('Une source XLSM et une destination XLSM neuve distincte sont requises.')
    if not output.parent.is_dir():raise ValueError('Le répertoire de destination doit exister.')
    if type(timeout) is not int or not 1<=timeout<=3600:raise ValueError('Délai natif hors bornes.')
    source_sha=digest(source)
    if source_sha!=profile.get('current_workbook_sha256'):
        raise ValueError('Le profil ne correspond pas à cette révision du classeur.')
    normalized,new_profile=plan_operations(profile,operations)
    before=workbook_diagnostics(source)
    targets = operation_targets(profile, operations)
    altered=set(profile.get('mechanical_owner_changes',[]))
    for target in targets:
        if target['deleted'] or target['superseded']:continue
        operation=normalized[target['operation_index']]
        logical=map_location(new_profile,target['sheet'],target['cell'],reverse=True)
        if logical and (operation['type']=='set_formula' or logical['cell'] not in profile['origin_schema'].get('cells',{}).get(logical['sheet'],{})):
            altered.add(logical['sheet']+'!'+logical['cell'])
    new_profile=refresh_profile({**new_profile,'mechanical_owner_changes':sorted(altered)})
    reference_repairs=[]
    if any(op['type'] in STRUCTURAL for op in normalized):
        from .formula_bindings import structural_index_repairs
        original=core.Workbook(source)
        try:reference_repairs=structural_index_repairs(original,profile,new_profile)
        finally:original.close()
    business_cells=[]
    if any(op['type'] in ('extend_register','extend_offer') for op in normalized):
        from .decision_offers import materialize_extension
        original=core.Workbook(source)
        try:
            for index,op in enumerate(normalized):
                if op['type'] not in ('extend_register','extend_offer'):continue
                normalized[index],repairs=materialize_extension(original,profile,new_profile,op)
                reference_repairs.extend(repairs)
                business_cells.extend(normalized[index]['cells'])
        finally:original.close()
    native=(runner(source,output,normalized,timeout=timeout) if runner else
            _run_native(source,output,normalized,timeout=timeout,reference_repairs=reference_repairs))
    if not output.is_file() or digest(source)!=source_sha:raise ValueError('La source a changé ou la variante est absente.')
    serialized_hash=digest(output)
    _invalidate_variant(output,new_profile,targets)
    native={**native,'native_serialized_output_sha256':serialized_hash,'output_sha256':digest(output),
            'formula_chart_and_native_caches_invalidated':True,
            'post_serialization_cache_invalidation':True}
    after=workbook_diagnostics(output)
    vba=vba_preservation(before.pop('vba'),after.pop('vba'))
    expected_names=[s['name'] for s in sorted(new_profile['sheets'],key=lambda s:s['index']) if not s['deleted']]
    diagnostics=list(after['errors'])
    old_links=before['external_links'];new_links=after['external_links']
    added_parts=sorted(set(new_links['parts'])-set(old_links['parts']))
    old_relationships={canonical(item) for item in old_links['relationships']}
    added_relationships=[item for item in new_links['relationships'] if canonical(item) not in old_relationships]
    if added_parts or added_relationships:
        diagnostics.append({'severity':'ERROR','code':'NEW_EXTERNAL_LINK',
                            'parts':added_parts,'relationships':added_relationships})
    if business_cells:
        extension=new_profile['business_extensions'][-1]
        diagnostics.append({'severity':'INFO','code':'BUSINESS_BLOCK_EXTENDED',
            'message':str(len(extension['owners']))+' entrées métier supplémentaires, '+str(len(business_cells))+
                      ' cellules préparées. Les nouvelles hypothèses sont à compléter après adoption de cette version.',
            'extension_id':extension['id'],'kind':extension['kind'],'family':extension.get('family'),
            'sheets':sorted({c['sheet'] for c in business_cells}),
            'content_sha256':normalized[0]['content_sha256']})
    if reference_repairs:
        verified=native.get('reference_repairs',[])
        if verified!=reference_repairs:
            diagnostics.append({'severity':'ERROR','code':'POSITIONAL_REFERENCE_REPAIRS_UNVERIFIED'})
        else:
            diagnostics.append({'severity':'INFO','code':'POSITIONAL_REFERENCES_BOUND',
                                'count':len(reference_repairs), 'sample':reference_repairs[:10]})
    # Attribute each legitimate loss to its deleted owner. A deleted row never
    # grants permission to remove charts/names elsewhere (or on the same sheet).
    allowances=dict.fromkeys(before['component_counts'],0)
    for sheet,owned in before['component_owners'].items():
        if sheet=='__workbook__':
            mapped_sheet=sheet;deleted=False
        else:
            record=sheet_record(profile,sheet)
            current=sheet_record(new_profile,record['id'],allow_deleted=True)
            deleted=current['deleted'];mapped_sheet=current['name']
        if deleted:
            for kind,items in owned.items():allowances[kind]+=len(items) if isinstance(items,list) else items
            continue
        allowed={kind:0 for kind in owned}
        for kind in ('validations','native_tables'):
            for area in owned[kind]:
                if area and not _range_survives(area,current['transforms'][len(record['transforms']):]):
                    allowed[kind]+=1
                    allowances[kind]+=1
        after_owned=after['component_owners'].get(mapped_sheet,{})
        for kind,items in owned.items():
            old_count=len(items) if isinstance(items,list) else items
            remaining=after_owned.get(kind,[] if isinstance(items,list) else 0)
            new_count=len(remaining) if isinstance(remaining,list) else remaining
            if new_count<old_count-allowed[kind]:
                diagnostics.append({'severity':'ERROR','code':'COMPONENT_LOST','component':kind,
                                    'sheet':mapped_sheet,'before':old_count,'after':new_count,'allowed_deleted':allowed[kind]})
    for kind,count in before['component_counts'].items():
        if after['component_counts'][kind]<count-allowances[kind]:
            diagnostics.append({'severity':'ERROR','code':'COMPONENT_LOST',
                                'component':kind,'before':count,'after':after['component_counts'][kind],
                                'allowed_deleted':allowances[kind]})
    if before['workbook_protection']!=after['workbook_protection']:
        diagnostics.append({'severity':'ERROR','code':'WORKBOOK_PROTECTION_CHANGED'})
    for original in profile['sheets']:
        if original['deleted']:continue
        current=sheet_record(new_profile,original['id'],allow_deleted=True)
        if not current['deleted'] and _protection_flags(before['protections'].get(original['name']))!=_protection_flags(after['protections'].get(current['name'])):
            diagnostics.append({'severity':'ERROR','code':'SHEET_PROTECTION_CHANGED','sheet':current['name']})
    checked = core.Workbook(output)
    try:
        if reference_repairs:
            from .web_model_profile import map_between_profiles
            for repair in reference_repairs:
                target=map_between_profiles(profile,new_profile,repair['sheet'],repair['cell'])
                repair['final']={**target,**checked.snapshot(target['sheet'],target['cell'])} if target else None
        if business_cells:
            for cell in business_cells:
                actual=checked.snapshot(cell['sheet'],cell['cell'])
                if 'formula' in cell:
                    same=_formula_key(actual.get('formula'))==_formula_key(cell['formula'])
                else:
                    expected=cell['value'];value=actual.get('value')
                    same=actual.get('formula') is None and value==expected and (type(value) is type(expected) or type(value) in (int,float) and type(expected) in (int,float))
                if not same:
                    diagnostics.append({'severity':'ERROR','code':'BUSINESS_BLOCK_CONTENT_DIFFERS',
                                        'sheet':cell['sheet'],'cell':cell['cell'],'expected':cell,'actual':actual})
        for target in targets:
            if target['deleted'] or target['superseded']:
                continue
            operation = normalized[target['operation_index']]
            value = checked.value(target['sheet'], target['cell'])
            formula = checked.formula(target['sheet'], target['cell'])
            expected=operation.get('value')
            same_value=value==expected and (type(value) is type(expected) or type(value) in (int,float) and type(expected) in (int,float))
            if operation['type'] == 'set_value' and (formula is not None or not same_value):
                diagnostics.append({'severity':'ERROR','code':'VALUE_NOT_PERSISTED','target':target})
            if operation['type'] == 'set_formula' and formula is None:
                diagnostics.append({'severity':'ERROR','code':'FORMULA_NOT_PERSISTED','target':target})
            if operation['type']=='set_formula':
                snapshots=native.get('changes',[])
                immediate=snapshots[target['operation_index']].get('after',{}).get('formula') if len(snapshots)==len(normalized) else None
                subsequent_structural=any(op['type'] in STRUCTURAL for op in normalized[target['operation_index']+1:])
                observed=immediate if immediate is not None else formula if not subsequent_structural else None
                if observed is not None and _formula_key(observed)!=_formula_key(operation['formula']):
                    diagnostics.append({'severity':'ERROR','code':'FORMULA_DIFFERS_FROM_PROPOSAL','target':target})
    finally:
        checked.close()
    if after['sheet_names']!=expected_names:diagnostics.append({'severity':'ERROR','code':'SHEET_MAPPING_MISMATCH'})
    if not vba['preserved']:diagnostics.append({'severity':'ERROR','code':'VBA_CHANGED','detail':vba})
    if new_profile['deleted_owners']:
        diagnostics.append({'severity':'ERROR','code':'BUSINESS_OWNERS_DELETED','owners':new_profile['deleted_owners']})
    if new_profile.get('deleted_native_anchors'):
        diagnostics.append({'severity':'ERROR','code':'NATIVE_ANCHOR_DELETED','anchors':new_profile['deleted_native_anchors']})
    if after['graph']['dynamic_references'] and any(op['type'] in STRUCTURAL for op in normalized):
        diagnostics.append({'severity':'WARNING','code':'DYNAMIC_REFERENCES_REQUIRE_REVIEW','cells':after['graph']['dynamic_references']})
    if any(op['type'] in STRUCTURAL-{'add_sheet','move_sheet'} for op in normalized):
        diagnostics.append({'severity':'WARNING','code':'PRESERVED_VBA_ADDRESSES_REQUIRE_REVIEW',
            'message':'Le code VBA conservé peut contenir des noms/adresses fixes. Il reste désactivé ; ses routines manuelles ne sont pas qualifiées par cette variante.'})
    output_sha=digest(output)
    new_profile.update(source_workbook_sha256=source_sha,current_workbook_sha256=output_sha,
                       native_results_valid=False,workbook_diagnostics=after,
                       manual_vba_execution_qualified=False)
    new_profile=seal_profile(new_profile)
    blocked=any(item['severity']=='ERROR' for item in diagnostics)
    changes = native.get('changes')
    if not isinstance(changes,list) or len(changes)!=len(normalized):
        changes=[]
        original=core.Workbook(source); final=core.Workbook(output)
        try:
            for index,operation in enumerate(normalized):
                target=next((t for t in targets if t['operation_index']==index),None)
                before_value=original.snapshot(operation['sheet'],operation['cell']) if operation['type'] in SETTERS and operation['sheet'] in original.sheets else None
                after_value=final.snapshot(target['sheet'],target['cell']) if target and not target['deleted'] and not target['superseded'] else None
                changes.append({**operation,'operation_index':index,'before':before_value,'after':after_value,
                                'snapshot_scope':'SOURCE_AND_FINAL_ONLY;INTERMEDIATE_NOT_OBSERVED'})
        finally:original.close();final.close()
    result={'schema':'tca-bp-web-variant/1','status':'BLOQUEE_DIAGNOSTIC' if blocked else 'VARIANTE_PREPAREE',
            'source_sha256':source_sha,'output_sha256':output_sha,'profile':new_profile,'changes':changes,
            'diagnostics':diagnostics,'reference_repairs':reference_repairs,'blocked':blocked,'validation':{'source_preserved':True,'vba':vba,
            'sheet_mapping_matches':after['sheet_names']==expected_names,'native':native,
            'financial_outputs_verified':False},'operation_targets':targets,'adopted':False}
    result['reference_repairs_count']=len(reference_repairs)
    # One complete manifest on disk; only bounded samples travel through the
    # interactive draft/SSE response. Its hash is bound into the approval token.
    native.pop('reference_repairs',None)
    native['reference_repairs_count']=len(reference_repairs)
    native['reference_repairs_sha256']=hashlib.sha256(canonical(reference_repairs).encode()).hexdigest()
    if business_cells:
        from .web_model_profile import _axis, cell_name
        original=core.Workbook(source)
        detailed=[]
        try:
            for cell in business_cells:
                old_record=sheet_record(profile,cell['sheet']);new_record=sheet_record(new_profile,old_record['id'])
                col,row=cell_parts(cell['cell'])
                for step in reversed(new_record['transforms'][len(old_record['transforms']):]):
                    if step['type'].endswith('_rows'):row=_axis(row,step,True)
                    else:col=_axis(col,step,True)
                    if col is None or row is None:break
                previous=original.snapshot(old_record['name'],cell_name(col,row)) if col is not None and row is not None else {'value':None,'formula':None}
                detailed.append({'sheet':cell['sheet'],'cell':cell['cell'],'before':previous,
                    'after':{'formula':cell.get('formula'),'value':cell.get('value')}})
        finally:original.close()
        result['business_changes']=detailed
        result['business_changes_count']=len(detailed)
        result['changes'][0]['business_cells_count']=len(detailed)
        result['changes'][0]['business_cells']=detailed[:25]
    details_path=output.with_suffix('.variant.json')
    atomic_json(details_path,{k:v for k,v in result.items() if k!='profile'})
    if business_cells or len(reference_repairs)>25:
        result['preview_details']={'filename':details_path.name,'sha256':digest(details_path),'size':details_path.stat().st_size,
                                   'cell_writes':len(business_cells),'index_repairs':len(reference_repairs),
                                   'total_changes':len(business_cells)+len(reference_repairs)+len(normalized)}
        result['reference_repairs']=reference_repairs[:10]
        if business_cells:result['business_changes']=result['business_changes'][:25]
    return result
