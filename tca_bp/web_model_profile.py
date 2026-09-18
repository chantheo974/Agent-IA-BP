"""Versioned business identities and reversible coordinate mappings.

Coordinates are Excel A1; row/column/sheet indexes are one-based. A structural
operation applies to the coordinates produced by preceding operations.
Profiles contain model metadata, never values copied from a client workbook.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path

from .storage import canonical, digest
from .vendor import input_engine as core

PROFILE_SCHEMA = 'tca-bp-web-profile/1'
RUNTIME_PROFILE = 'web-profile/1'
PROFILE_FILE = 'web_profile.json'
MAX_ROW, MAX_COL = 1048576, 16384


def profile_digest(profile):
    return hashlib.sha256(canonical({k: v for k, v in profile.items() if k != 'profile_sha256'}).encode()).hexdigest()


def seal_profile(profile):
    result = deepcopy(profile)
    result['profile_sha256'] = profile_digest(result)
    return result


def verify_profile(profile):
    if (not isinstance(profile, dict) or profile.get('schema') != PROFILE_SCHEMA
            or profile.get('profile_sha256') != profile_digest(profile)):
        raise ValueError('Profil métier absent, incompatible ou modifié.')
    return profile


def cell_parts(cell):
    if not isinstance(cell, str) or not re.fullmatch(r'\$?[A-Za-z]{1,3}\$?[1-9][0-9]{0,6}', cell):
        raise ValueError('Adresse Excel A1 requise.')
    _, col, row = core.coord(cell)
    if not 1 <= col <= MAX_COL or not 1 <= row <= MAX_ROW:
        raise ValueError('Adresse hors limites Excel.')
    return col, row


def cell_name(col, row):
    if not 1 <= col <= MAX_COL or not 1 <= row <= MAX_ROW:
        return None
    return core.colname(col) + str(row)


def _axis(value, operation, reverse=False):
    index, count = operation['index'], operation['count']
    insert = operation['type'].startswith('insert_') != reverse
    if insert:
        return value + count if value >= index else value
    if index <= value < index + count:
        return None
    return value - count if value >= index + count else value


def sheet_record(profile, sheet, *, original=False, allow_deleted=False):
    key = 'original_name' if original else 'name'
    match = next((s for s in profile['sheets'] if s['id'] == sheet or s.get(key) == sheet), None)
    if not match or match.get('deleted') and not allow_deleted:
        raise ValueError('Feuille inconnue ou supprimée : ' + str(sheet))
    return match


def map_location(profile, sheet, cell, *, reverse=False):
    """Map an original logical owner to current Excel, or current to original.

None means a deleted owner / an inserted cell with no previous identity. It
never means zero and does not silently bind the owner to an adjacent cell.
"""
    try:
        record = sheet_record(profile, sheet, original=not reverse, allow_deleted=True)
    except ValueError:
        return None
    if record.get('deleted') or record.get('original_name') is None:
        return None
    if profile.get('business_extensions'):
        from .decision_offers import extension_location
        requested_col,requested_row=cell_parts(cell)
        known_extra=False
        for extension in profile['business_extensions']:
            for owner in extension['owners']:
                if owner['sheet_id']!=record['id']:continue
                if not reverse and cell_parts(owner['logical_cell'])[1]==requested_row:known_extra=True
                target=extension_location(profile,owner)
                if not target:continue
                logical_row=cell_parts(owner['logical_cell'])[1]
                if (reverse and target and cell_parts(target['cell'])[1]==requested_row
                        or not reverse and logical_row==requested_row):
                    col=requested_col
                    for step in reversed(record['transforms']) if reverse else record['transforms']:
                        if step['type'].endswith('_columns'):col=_axis(col,step,reverse)
                        if col is None:return None
                    if not target:return None
                    row=logical_row if reverse else cell_parts(target['cell'])[1]
                    return {'sheet':owner['original_sheet'] if reverse else target['sheet'],
                            'cell':cell_name(col,row),'sheet_id':record['id']}
        if known_extra:return None
    col, row = cell_parts(cell)
    steps = reversed(record['transforms']) if reverse else record['transforms']
    for operation in steps:
        if operation['type'].endswith('_rows'):
            row = _axis(row, operation, reverse)
        else:
            col = _axis(col, operation, reverse)
        if row is None or col is None:
            return None
    address = cell_name(col, row)
    if address is None:
        return None
    return {'sheet': record['original_name'] if reverse else record['name'], 'cell': address,
            'sheet_id': record['id']}


def map_range(profile, sheet, area, *, reverse=False):
    bounds = area.replace('$', '').split(':')
    if len(bounds) not in (1, 2):
        raise ValueError('Plage A1 bornée requise.')
    first, last = [map_location(profile, sheet, value, reverse=reverse) for value in (bounds[0], bounds[-1])]
    if first is None or last is None:
        return None
    return {'sheet': first['sheet'], 'range': first['cell'] if len(bounds) == 1 else first['cell'] + ':' + last['cell']}


def initial_profile(engine, workbook):
    workbook = Path(workbook)
    if getattr(engine, 'profile', None):
        profile = deepcopy(engine.profile)
        checked = engine._open(workbook)
        try:
            profile['source_workbook_sha256'] = checked.hash
            profile['current_workbook_sha256'] = checked.hash
        finally:
            checked.close()
        return seal_profile(profile)
    checked = engine._open(workbook)
    try:
        sheets = []
        for index, name in enumerate(checked.sheets, 1):
            sheets.append({'id': 'sheet_' + hashlib.sha256((engine.model_id + '\0' + name).encode()).hexdigest()[:20],
                           'name': name, 'original_name': name, 'index': index, 'deleted': False,
                           'transforms': [], 'role': name})
        source_sha = checked.hash
    finally:
        checked.close()
    catalogue = engine.catalog()
    if isinstance(catalogue, dict):
        catalogue = catalogue['fields']
    from .knowledge import contracts
    profile = {'schema': PROFILE_SCHEMA, 'version': 1, 'origin_model_id': engine.model_id,
               'origin_template_sha256': digest(engine.template_path),
               'origin_schema': deepcopy(engine.schema), 'origin_catalogue': deepcopy(catalogue),
               'source_workbook_sha256': source_sha, 'current_workbook_sha256': source_sha,
               'sheets': sheets, 'operations': [], 'base_agents': contracts(),
               'formula_changes': [], 'value_changes': [], 'deleted_owners': [],
               'qualification_status': 'PROFIL_REFERENCE', 'native_results_valid': False}
    return refresh_profile(profile)


def refresh_profile(profile):
    """Regenerate physical bindings from stable original identities."""
    result = deepcopy(profile)
    fields, deleted = [], []
    for field in result['origin_catalogue']:
        current = deepcopy(field)
        bindings = []
        addresses=list(field.get('cells', []))
        for extension in result.get('business_extensions',[]):
            addresses.extend(o['logical_cell'] for o in extension['owners']
                             if o['original_sheet']==field['sheet'] and o['source_cell'] in field.get('cells',[]))
        for address in addresses:
            mapped = map_location(result, field['sheet'], address)
            bindings.append({'original_sheet': field['sheet'], 'original_cell': address, 'current': mapped})
            if mapped is None:
                deleted.append({'field_id': field['id'], 'sheet': field['sheet'], 'cell': address})
        active = [b['current'] for b in bindings if b['current']]
        current.update(original_sheet=field['sheet'], sheet=active[0]['sheet'] if active else None,
                       cells=[m['cell'] for m in active], ranges=[m['cell'] for m in active],
                       bindings=bindings, deleted=not bool(active))
        if current.get('semantics'):
            current['semantics']['binding_status'] = 'PROPRIETAIRE_SUPPRIME' if len(active) != len(bindings) else 'IDENTITE_CONSERVEE'
            current['semantics']['profile_version'] = result['version']
            if len(active) != len(bindings):
                current['semantics']['status'] = 'REEXAMEN_REQUIS'
            changed = set(result.get('mechanical_owner_changes', []))
            own = {field['sheet'] + '!' + cell for cell in field.get('cells', [])}
            witnesses = {w.get('address') for w in current['semantics'].get('evidence', {}).get('witnesses', [])}
            if changed & (own | witnesses):
                current['semantics'].update(status='REEXAMEN_REQUIS', can_propose=False)
                current['semantics'].setdefault('blocking_reasons', []).append('FORMULE_OU_PREUVE_METIER_MODIFIEE_EXPLICITEMENT')
            downstream=current['semantics'].get('dependencies',{}).get('downstream')
            if downstream:
                downstream.update(sheet=current['sheet'],cells=list(current['cells']))
            policy=current['semantics'].get('policy',{})
            for key in ('default_cells','required_cells_when_record_active'):
                if key in policy:
                    policy[key]=[m['cell'] for address in policy[key] if (m:=map_location(result,field['sheet'],address))]
        fields.append(current)
    # A changed owner's dependent field cannot inherit an established meaning.
    for _ in range(len(fields)):
        invalid={f['id'] for f in fields if f.get('semantics',{}).get('status')=='REEXAMEN_REQUIS'}
        updated=False
        for field in fields:
            semantic=field.get('semantics',{})
            owners={o.get('field_id') for o in semantic.get('dependencies',{}).get('business_owners',[])}
            if owners & invalid and semantic.get('status')!='REEXAMEN_REQUIS':
                semantic.update(status='REEXAMEN_REQUIS',can_propose=False)
                semantic.setdefault('blocking_reasons',[]).append('PROPRIETAIRE_METIER_A_REEXAMINER');updated=True
        if not updated:break
    result['fields'], result['deleted_owners'] = fields, deleted
    agents = []
    for agent in result['base_agents']:
        try:
            record = sheet_record(result, agent['sheet'], original=True, allow_deleted=True)
        except ValueError:
            continue
        current = deepcopy(agent)
        current.update(sheet_id=record['id'], original_sheet=agent['sheet'], sheet=record['name'], deleted=record['deleted'])
        current['dependencies'] = [s['name'] for s in result['sheets'] if not s['deleted'] and s['original_name'] in agent.get('dependencies', [])]
        for point in current.get('key_calculations', []):
            mapped = map_location(result, agent['sheet'], point['cell'])
            point['original_cell'] = point['cell']
            point['cell'] = mapped['cell'] if mapped else None
            point['binding_status'] = 'IDENTITE_CONSERVEE' if mapped else 'PROPRIETAIRE_SUPPRIME'
        agents.append(current)
    for record in result['sheets']:
        if record['original_name'] is None and not record['deleted']:
            agents.append({'id': 'AGENT_' + record['id'], 'sheet': record['name'], 'sheet_id': record['id'],
                           'role': record['role'], 'dependencies': [], 'key_calculations': [],
                           'qualification_status': 'NOUVELLE_FEUILLE_A_QUALIFIER', 'deleted': False})
    result['agents'] = agents
    qualification_refs = []
    for sheet, cells in result['origin_schema'].get('cells', {}).items():
        for address in cells:
            qualification_refs.append({'logical': sheet + '!' + address, 'current': map_location(result, sheet, address)})
    for extension in result.get('business_extensions',[]):
        for owner in extension['owners']:
            qualification_refs.append({'logical':owner['original_sheet']+'!'+owner['logical_cell'],
                                       'current':map_location(result,owner['original_sheet'],owner['logical_cell']),
                                       'extension_id':extension['id']})
    result['qualification_refs'] = qualification_refs
    wacc = ['D7','D8','D9','D40','D107','D108','D124','D135','D136','D137','D138','D141','D142','D143','D155','D156']
    table_refs = ['C8','C14','C18','D24','E24','F24','G24','C39','D39','C49']
    result['native'] = {
        'wacc': {'locations': {a: map_location(result, 'Valorisation', a) for a in wacc},
                 'written_outputs': {a: map_location(result, 'Valorisation', a) for a in ('D136','D141','D142','D143','D156')}},
        'sensitivity': {'locations': {a: map_location(result, 'Sensi Analyses', a) for a in table_refs},
                        'tables': {a: map_range(result, 'Sensi Analyses', a) for a in ('D25:G33','C40:D45','D50:F52')}}}
    native_losses=[]
    original_names={s.get('original_name') for s in result['sheets']}
    for kind,original_name in (('wacc','Valorisation'),('sensitivity','Sensi Analyses')):
        if original_name not in original_names:continue
        for group,locations in result['native'][kind].items():
            for address,target in locations.items():
                if target is None:native_losses.append({'kind':kind,'group':group,'sheet':original_name,'cell':address})
    for group in ('native_outputs','native_table_outputs'):
        for name,addresses in result['origin_schema'].get(group,{}).items():
            for address in addresses:
                if map_location(result,name,address) is None:
                    native_losses.append({'kind':'schema','group':group,'sheet':name,'cell':address})
    result['deleted_native_anchors']=native_losses
    return seal_profile(result)


def remap_field_states(profile, states, *, reverse=False):
    result, missing = {}, []
    for key, state in states.items():
        if '!' not in key:
            missing.append(key); continue
        sheet, address = key.rsplit('!', 1)
        mapped = map_location(profile, sheet, address, reverse=reverse)
        if mapped is None:
            missing.append(key)
        else:
            result[mapped['sheet'] + '!' + mapped['cell']] = deepcopy(state)
    return {'states': result, 'unmapped': missing}


def map_between_profiles(before, after, sheet, cell):
    """Follow stable sheet ID and only the new geometric operations.

    Unlike reverse-to-origin mapping this preserves locally created cells and
    sheets. A deletion returns None; its previous evidence remains in history.
    """
    try:
        old = sheet_record(before, sheet, allow_deleted=True)
        new = sheet_record(after, old['id'], allow_deleted=True)
    except ValueError:
        return None
    if new['deleted']:
        return None
    prefix = old['transforms']
    if new['transforms'][:len(prefix)] != prefix:
        raise ValueError('Les profils ne partagent pas la même chaîne de transformations.')
    col, row = cell_parts(cell)
    for operation in new['transforms'][len(prefix):]:
        if operation['type'].endswith('_rows'): row = _axis(row, operation)
        else: col = _axis(col, operation)
        if row is None or col is None: return None
    address = cell_name(col, row)
    return {'sheet': new['name'], 'cell': address, 'sheet_id': new['id']} if address else None


class LogicalWorkbook:
    """Read-only view for legacy business rules; coordinates are original IDs.

    Verification remains on the real workbook and its current schema. This
    view never fakes verify_model or substitutes a former model signature.
    """
    def __init__(self, workbook, profile):
        self.actual, self.profile = workbook, profile
        self.path, self.hash, self.date1904 = workbook.path, workbook.hash, workbook.date1904
        self.sheets = {s['original_name']: workbook.sheets[s['name']] for s in profile['sheets']
                       if s.get('original_name') and not s['deleted']}
        self._sheet_cache = {}

    def value(self, sheet, cell):
        mapped = map_location(self.profile, sheet, cell)
        return self.actual.value(mapped['sheet'], mapped['cell']) if mapped else None

    def formula(self, sheet, cell):
        mapped = map_location(self.profile, sheet, cell)
        return self.actual.formula(mapped['sheet'], mapped['cell']) if mapped else None

    def snapshot(self, sheet, cell):
        return {'value': self.value(sheet, cell), 'formula': self.formula(sheet, cell)}

    def input_signature(self, schema):
        # Signature of the physical, versioned input snapshot, not a simulated
        # legacy signature. Qualification binds it to the current model pin.
        value = [(s, a, self.snapshot(s, a)) for s, cells in schema.get('cells', {}).items() for a in cells]
        return hashlib.sha256(canonical(value).encode()).hexdigest()

    def close(self):
        self.actual.close()
