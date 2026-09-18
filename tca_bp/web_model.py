"""Runtime adapter for a distinct, explicitly adopted structural variant.

The real workbook is verified against its new seal. Legacy business rules read
an original-coordinate view; no old signature or former physical address is
silently accepted. Native proofs and financial qualification never migrate.
"""
from __future__ import annotations

from copy import deepcopy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile

from .model_engine import ModelEngine
from .model_components import read_component
from .model_runtime import invalidate_caches, invalidate_chart
from .storage import canonical, digest
from .vendor import input_engine as core
from .web_model_profile import (initial_profile, verify_profile, seal_profile, refresh_profile,
    map_location, map_range, map_between_profiles, remap_field_states, cell_parts, LogicalWorkbook, PROFILE_FILE, RUNTIME_PROFILE)


def _write(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        handle.write(canonical(value))


def _mapped_schema(profile, workbook):
    from .decision_offers import extended_origin_schema
    logical_schema=extended_origin_schema(profile)
    schema = deepcopy(logical_schema)
    schema['cells'] = {}
    for sheet, cells in logical_schema.get('cells', {}).items():
        for address, original in cells.items():
            target = map_location(profile, sheet, address)
            if not target:
                continue
            spec = deepcopy(original)
            spec['fill'] = workbook.fill(target['sheet'], target['cell'])
            formula = workbook.formula(target['sheet'], target['cell'])
            if formula is not None:
                spec['default_formula'] = formula
            else:
                spec.pop('default_formula', None)
            if spec.get('choices_source'):
                source = spec['choices_source']
                mapped = map_range(profile, source['sheet'], source['range'])
                if mapped:
                    spec['choices_source'] = mapped
                else:
                    spec['choices_source_unavailable'] = True
            schema['cells'].setdefault(target['sheet'], {})[target['cell']] = spec
    schema['fields'] = [deepcopy(f) for f in profile['fields'] if not f['deleted']]
    for key in ('native_outputs', 'native_table_outputs'):
        schema[key] = {}
        for sheet, addresses in profile['origin_schema'].get(key, {}).items():
            for address in addresses:
                target = map_location(profile, sheet, address)
                if target:
                    schema[key].setdefault(target['sheet'], []).append(target['cell'])
    schema['registers'] = {}
    for sheet, old in logical_schema.get('registers', {}).items():
        first = map_location(profile, sheet, 'A' + str(old['start_row']))
        last = map_location(profile, sheet, 'A' + str(old['end_row']))
        if not first or not last:
            continue
        reg = deepcopy(old)
        reg['start_row'], reg['end_row'] = core.coord(first['cell'])[2], core.coord(last['cell'])[2]
        for key in ('required', 'identity_columns'):
            reg[key] = [core.coord(target['cell'])[0][2] for column in old.get(key, [])
                        if (target := map_location(profile, sheet, column + str(old['start_row'])))]
        # An inserted row is not silently treated as a new contractual record.
        reg['mapped_rows'] = [core.coord(target['cell'])[2] for row in [*range(old['start_row'], old['end_row'] + 1),*old.get('extra_rows',[])]
                              if (target := map_location(profile, sheet, 'A' + str(row)))]
        # Column A is not necessarily an input owner; resolve an owned identity
        # column when a registered extension has no column-A input.
        for row in old.get('extra_rows',[]):
            for column in old.get('identity_columns',[]):
                target=map_location(profile,sheet,column+str(row))
                if target:
                    number=core.coord(target['cell'])[2]
                    if number not in reg['mapped_rows']:reg['mapped_rows'].append(number)
                    break
        reg['mapped_rows'].sort()
        reg.pop('extra_rows',None)
        schema['registers'][first['sheet']] = reg
    schema.pop('native_vba_variants', None)
    schema['forbid_tca_filename'] = False
    return schema


def _logical_schema(profile, physical_schema):
    from .decision_offers import extended_origin_schema
    result = extended_origin_schema(profile)
    result['model_id'] = physical_schema['model_id']
    result['template_sha256'] = physical_schema['template_sha256']
    # A moved, unmodified default has Excel's current formula spelling. Its
    # provenance remains the original owner, not a formula-cache value.
    for sheet, cells in result.get('cells', {}).items():
        for address, spec in cells.items():
            target = map_location(profile, sheet, address)
            physical = physical_schema['cells'].get(target['sheet'], {}).get(target['cell'], {}) if target else {}
            if 'default_formula' in physical:
                spec['default_formula'] = physical['default_formula']
            else:
                spec.pop('default_formula', None)
    return result


def seal_profile_model(base_engine, workbook, profile, output_dir):
    """Create an immutable private variant bundle; never publish or adopt it."""
    from .web_structure import workbook_diagnostics, vba_preservation
    profile = refresh_profile(verify_profile(profile))
    base_profile = getattr(base_engine, 'profile', None)
    origin_schema = base_profile['origin_schema'] if base_profile else base_engine.schema
    origin_catalogue = base_profile['origin_catalogue'] if base_profile else base_engine.catalog()
    if profile['origin_schema'] != origin_schema or profile['origin_catalogue'] != origin_catalogue:
        raise ValueError('Les contrats métier d’origine ont changé ; préparer explicitement une nouvelle variante.')
    workbook, folder = Path(workbook).resolve(), Path(output_dir).resolve()
    if folder.exists():
        raise ValueError('La version de destination existe déjà.')
    if digest(workbook) != profile['current_workbook_sha256']:
        raise ValueError('Le classeur ne correspond plus au profil préparé.')
    if profile['deleted_owners']:
        raise ValueError('Des propriétaires métier supprimés doivent être redéfinis avant adoption.')
    if profile.get('deleted_native_anchors'):
        raise ValueError('Des ancrages de calcul natif supprimés doivent être rétablis avant adoption.')
    diagnostics = workbook_diagnostics(workbook)
    if diagnostics['errors']:
        raise ValueError('Une référence rompue empêche le scellement de la variante.')
    source = core.Workbook(base_engine.template_path)
    current = core.Workbook(workbook)
    try:
        vba = vba_preservation(source.z.read('xl/vbaProject.bin'), current.z.read('xl/vbaProject.bin'))
        if not vba['preserved']:
            raise ValueError('Les sources VBA ont changé ; variante refusée.')
        profile = seal_profile({**profile, 'validation': {'vba': vba, 'financial_outputs_verified': False}})
        schema = _mapped_schema(profile, current)
        ident = 'tca-bp-web/' + profile['profile_sha256'][:24]
        schema.update(model_id=ident, source_model_id=base_engine.model_id,
                      source_template_sha256=digest(base_engine.template_path), template_sha256=current.hash,
                      runtime_profile=RUNTIME_PROFILE, web_profile_sha256=profile['profile_sha256'],
                      qualification_status='VARIANTE_A_QUALIFIER', native_results_valid=False)
        schema['signature'] = current.semantic_signature(schema)
        core.verify_model(current, schema)
        folder.mkdir(parents=True, exist_ok=False)
        with (folder / 'TCA_BP_Trame_generique.xlsm').open('xb') as handle:
            handle.write(current.bytes)
        _write(folder / PROFILE_FILE, profile)
        _write(folder / 'modele.json', schema)
        _write(folder / 'catalogue_champs.json', schema['fields'])
        _write(folder / 'classification_cellules.json', {'schema': 'tca-bp-web-classification/1',
               'model_id': ident, 'cells': schema['cells'], 'new_cells': 'A_QUALIFIER_EXPLICITEMENT'})
        _write(folder / 'migrations.json', {'schema': 'tca-bp-web-migration/1', 'source_model_id': base_engine.model_id,
               'profile_sha256': profile['profile_sha256'], 'parent_profile_sha256': profile.get('parent_profile_sha256'),
               'qualification_transfer': False, 'native_proof_transfer': False, 'automatic_adoption': False})
        graph = _graph(current, schema, profile)
        _write(folder / 'graphe_dependances.json', graph)
        receipt = {'schema': 'tca-bp-build/v1', 'model_id': ident, 'source_model_id': base_engine.model_id,
                   'template_sha256': current.hash, 'schema_sha256': digest(folder / 'modele.json'),
                   'web_profile_sha256': profile['profile_sha256'], 'qualification_status': 'VARIANTE_A_QUALIFIER',
                   'counts': {'sheets': len(current.sheets), 'fields': len(schema['fields']),
                              'inputs': sum(map(len, schema['cells'].values())),
                              'protected_formulas': schema['signature']['protected_formula_count'],
                              'formula_nodes': len(graph['cells'])},
                   'native_calculation': 'NOT_EXECUTED', 'financial_results_status': 'UNAVAILABLE',
                   'private_case_variant': True, 'created_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        _write(folder / 'build_receipt.json', receipt)
        if digest(workbook) != current.hash:
            raise ValueError('Le classeur a changé pendant le scellement.')
        return receipt
    finally:
        source.close(); current.close()


_REF = re.compile(r"(?<![\w.])(?:(?P<sheet>'(?:[^']|'')+'|[A-Za-z_][\w ]*)!)?(?P<range>\$?[A-Z]{1,3}\$?[1-9]\d*(?::\$?[A-Z]{1,3}\$?[1-9]\d*)?)(?![\w]|\s*\()")


def formula_references(formula, sheet):
    """Audited literal A1 index; intentionally not an Excel expression parser."""
    clean = re.sub(r'"(?:[^"]|"")*"', '""', formula)
    result = []
    for match in _REF.finditer(clean):
        span = match['range']
        try:
            _, col, row = core.coord(span.split(':')[0])
            if col > 16384 or row > 1048576:
                continue
        except ValueError:
            continue
        target = match['sheet'] or sheet
        if target.startswith("'"):
            target = target[1:-1].replace("''", "'")
        value = "'" + target.replace("'", "''") + "'!" + span
        if value not in result:
            result.append(value)
    return result


def _graph(workbook, schema, profile):
    names = [dict(n.attrib, text=n.text or '') for n in workbook.wb.findall('m:definedNames/m:definedName', core.N)]
    named = {n['name'] for n in names}
    records, edges, tables, dynamic = [], {}, [], []
    for sheet in workbook.sheets:
        dependencies = set()
        for address, node in workbook.sheet(sheet)[1].items():
            element = node.find('m:f', core.N)
            if element is None:
                continue
            formula = workbook.formula(sheet, address)
            refs = formula_references(formula, sheet)
            for reference in refs:
                target = reference.split('!', 1)[0][1:-1].replace("''", "'")
                if target != sheet and target in workbook.sheets:
                    dependencies.add(target)
            clean = re.sub(r'"(?:[^"]|"")*"', '""', formula)
            if re.search(r'\b(?:INDIRECT|OFFSET)\s*\(', clean, re.I):
                dynamic.append({'sheet': sheet, 'cell': address})
            records.append({'sheet': sheet, 'cell': address, 'formula_sha256': core.sha(formula.encode()),
                            'references': refs, 'defined_names': sorted(set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9.]*\b', clean)) & named),
                            'kind': element.get('t', 'normal')})
            if element.get('t') == 'dataTable':
                tables.append({'sheet': sheet, 'cell': address, **element.attrib})
        edges[sheet] = sorted(dependencies)
        workbook._sheet_cache.pop(sheet, None)
    return {'schema': 'tca-bp-dependencies/v1', 'model_id': schema['model_id'], 'sheets': edges, 'cells': records,
            'defined_names': names, 'native_tables': tables, 'dynamic_references': dynamic,
            'macro': {'preserved': True, 'sha256': core.sha(workbook.z.read('xl/vbaProject.bin')),
                      'outputs': schema['native_outputs'], 'executed': False},
            'runtime_native_mapping': profile['native'], 'native_validation': 'NOT_EXECUTED',
            'limits': ['Literal A1 and names indexed; dynamic references, whole-column references and VBA need explicit review.'],
            'source_template_sha256': workbook.hash, 'coverage_complete': False}


class ProfileEngine(ModelEngine):
    def __init__(self, project_root, model_dir):
        super().__init__(project_root, model_dir)
        self._profile = None

    def ensure_built(self):
        receipt = super().ensure_built()
        if self._profile is not None:
            return receipt
        profile = verify_profile(json.loads(read_component(self.model_dir / PROFILE_FILE)))
        if self._schema.get('runtime_profile') != RUNTIME_PROFILE or self._schema.get('web_profile_sha256') != profile['profile_sha256']:
            raise ValueError('Le profil ne correspond pas au manifeste épinglé.')
        if self._profile is not None and profile != self._profile:
            raise ValueError('Le profil chargé a changé.')
        self._profile = profile
        return receipt

    def _open(self, path):
        self.ensure_built()
        current = verify_profile(json.loads(read_component(self.model_dir / PROFILE_FILE)))
        if current != self._profile:
            raise ValueError('Le profil épinglé a changé depuis son chargement.')
        return super()._open(path)

    @property
    def profile(self):
        self.ensure_built()
        return deepcopy(self._profile)

    def catalog(self):
        return [deepcopy(f) for f in self.profile['fields'] if not f['deleted']]

    def remap_states_from(self, base_engine, states):
        old = getattr(base_engine, 'profile', None)
        profile = self.profile; result = {}; removed = []
        for key, state in states.items():
            if not isinstance(key,str) or '!' not in key:
                removed.append(key);continue
            sheet, address = key.rsplit('!', 1)
            try:cell_parts(address)
            except ValueError:
                removed.append(key);continue
            target = map_between_profiles(old, profile, sheet, address) if old else map_location(profile, sheet, address)
            if target is None: removed.append(key)
            else: result[target['sheet'] + '!' + target['cell']] = deepcopy(state)
        self.last_state_remap = {'removed_current_bindings': removed, 'previous_evidence_must_remain_in_history': True,
                                'qualification_transferred': False}
        return result

    def scope_for_output(self, sheet, address):
        from .qualifications import scope_for_output
        logical = map_location(self.profile, sheet, address, reverse=True)
        return scope_for_output(logical['sheet'], logical['cell']) if logical else None

    def qualification_snapshot(self, workbook):
        from .qualifications import collect_snapshot
        from .field_semantics import summary
        actual = self._open(workbook)
        try:
            profile = self.profile
            snapshot = collect_snapshot(LogicalWorkbook(actual, profile), _logical_schema(profile, self.schema))
            snapshot['input_signature'] = actual.input_signature(self.schema)
            snapshot['profile_sha256'] = profile['profile_sha256']
            from .wacc_fingerprint_migration import verified_fingerprint_exemptions
            snapshot['technical_formula_exemptions']=sorted(verified_fingerprint_exemptions(profile,actual))
            from .dcf_calendar_migration import verified_calendar_exemptions
            snapshot['calendar_formula_exemptions']=sorted(verified_calendar_exemptions(profile,actual))
            from .fiscal_calendar_migration import verified_fiscal_calendar_exemptions
            snapshot['fiscal_calendar_formula_exemptions']=sorted(verified_fiscal_calendar_exemptions(profile,actual))
            snapshot['field_semantics'] = summary(self.catalog())
            for field in self.catalog():
                semantics = field.get('semantics', {})
                for binding in field['bindings']:
                    key = binding['original_sheet'] + '!' + binding['original_cell']
                    if key in snapshot['cells']:
                        snapshot['cells'][key]['semantic_status'] = semantics.get('status')
                        snapshot['cells'][key]['semantic_issues'] = semantics.get('blocking_reasons', [])
            return snapshot
        finally:
            actual.close()

    def evaluate_qualifications(self, snapshot, field_states, verified_source_ids, *, module_declarations=None, calculation=None):
        from .qualifications import evaluate
        profile = self.profile
        if snapshot.get('profile_sha256') != profile['profile_sha256']:
            raise ValueError('Le snapshot appartient à un autre profil métier.')
        logical = remap_field_states(profile, field_states, reverse=True)
        renames = {s['name']: s['original_name'] for s in profile['sheets'] if s.get('original_name')}
        declarations = {renames.get(key, key): deepcopy(value) for key, value in (module_declarations or {}).items()}
        result = evaluate(snapshot, logical['states'], verified_source_ids, module_declarations=declarations, calculation=calculation)
        from .qualifications import scope_for_output, DEPENDENCIES
        helper_owners={'Valorisation!'+cell for cell in ('J155','J156','J157','J158','D155')}
        exempt=set(snapshot.get('technical_formula_exemptions',[])) & helper_owners
        from .dcf_calendar_migration import OWNERS as CALENDAR_OWNERS
        exempt|=set(snapshot.get('calendar_formula_exemptions',[])) & set(CALENDAR_OWNERS)
        from .fiscal_calendar_migration import OWNERS as FISCAL_CALENDAR_OWNERS
        exempt|=set(snapshot.get('fiscal_calendar_formula_exemptions',[])) & set(FISCAL_CALENDAR_OWNERS)
        affected={scope_for_output(*key.rsplit('!',1)) for key in profile.get('mechanical_owner_changes',[]) if key not in exempt}-{None}
        for _ in range(len(DEPENDENCIES)):
            affected|={scope for scope,dependencies in DEPENDENCIES.items() if affected & set(dependencies)}
        for scope in affected:
            if scope not in result['scopes']:continue
            outcome=result['scopes'][scope]
            outcome.update(available=False,scenario_ready=False,qualification_ready=False,status='VARIANTE_METIER_A_REEXAMINER')
            outcome['blockers'].append({'code':'FORMULE_METIER_MODIFIEE','field':None,
                'message':'Une formule ou constante protégée a été changée : revoir le contrat métier et les oracles de ce périmètre.'})
        if affected:
            result['questions'].append({'field':None,'field_id':None,'fields':[],
                'question':'Valider les nouveaux calculs et leurs hypothèses par des oracles indépendants avant de qualifier leurs résultats.',
                'codes':['FORMULE_METIER_MODIFIEE'],'scopes':sorted(affected)})
        result['profile_sha256'] = profile['profile_sha256']
        result['unmapped_states'] = logical['unmapped']
        result['coordinate_system'] = 'ORIGINAL_LOGICAL_OWNERS_WITH_PHYSICAL_BINDINGS'
        result['physical_bindings'] = profile['qualification_refs']
        return result

    def context(self, workbook):
        from .qualifications import SCOPES, error_perimeter
        actual = self._open(workbook)
        try:
            profile = self.profile; logical = LogicalWorkbook(actual, profile)
            snapshot = self.qualification_snapshot(workbook)
            registers = {}
            for sheet, spec in _logical_schema(profile,self.schema).get('registers', {}).items():
                occupied = set(snapshot['registers'][sheet]['occupied_rows'])
                column=spec['identity_columns'][0]
                mapped = [(row, map_location(profile, sheet, column + str(row)))
                          for row in [*range(spec['start_row'], spec['end_row'] + 1),*spec.get('extra_rows',[])]]
                used = [core.coord(pos['cell'])[2] for row, pos in mapped if pos and row in occupied]
                free = [core.coord(pos['cell'])[2] for row, pos in mapped if pos and row not in occupied]
                if mapped and mapped[0][1]:
                    name = mapped[0][1]['sheet']
                    registers[name] = {'occupied_rows': used, 'first_free_row': free[0] if free else None,
                                       'free_count': len(free), 'required_columns': self.schema['registers'][name]['required'],
                                       'inserted_rows_require_explicit_business_binding': True}
            raw_years = logical.value('Control', 'C59')
            years = int(raw_years) if isinstance(raw_years, (int, float)) and not isinstance(raw_years, bool) and int(raw_years) == raw_years else 0
            errors = []; counts = {}; perimeters = dict.fromkeys(SCOPES, 0); inactive = 0; total = 0; unassigned = 0
            for sheet in actual.sheets:
                for address, node in actual.sheet(sheet)[1].items():
                    if node.get('t') != 'e' or actual.value(sheet, address) is None:
                        continue
                    value = actual.value(sheet, address); total += 1; counts[value] = counts.get(value, 0) + 1
                    original = map_location(profile, sheet, address, reverse=True)
                    if original:
                        scope, active = error_perimeter(original['sheet'], original['cell'], years)
                        if active: perimeters[scope] += 1
                        else: inactive += 1
                    else: unassigned += 1
                    if len(errors) < 100: errors.append({'sheet': sheet, 'cell': address, 'error': value})
                actual._sheet_cache.pop(sheet, None)
            has_activity = any(r['occupied_rows'] for r in registers.values()) or any(logical.value('Assumptions', 'C' + str(r)) == 1 for r in range(15, 28))
            modules = {sheet: 'ACTIF' if reg['occupied_rows'] else 'INACTIF' for sheet, reg in registers.items()}
            completeness = {'state': 'PARTIAL' if has_activity else 'EMPTY', 'modules': modules,
                            'missing': [], 'qualification_required': True, 'profile_version': profile['version']}
            return {'schema': 'tca-bp-context/v1', 'model_id': self.model_id, 'source_name': actual.path.name,
                    'source_sha256': actual.hash, 'input_signature': actual.input_signature(self.schema),
                    'cell_protection_signature': deepcopy(self._protection_signature), 'date1904': actual.date1904,
                    'sheets': len(actual.sheets), 'protected_formulas': self.schema['signature']['protected_formula_count'],
                    'active_years': raw_years, 'start_excel_date': logical.value('Control', 'C10'),
                    'input_count': sum(map(len, self.schema['cells'].values())), 'registers': registers,
                    'formula_errors': {'count': total, 'by_error': counts, 'cells': errors, 'truncated': total > len(errors),
                       'active_by_scope': perimeters, 'inactive_horizon_count': inactive, 'unassigned_count': unassigned,
                       'attribution_complete': unassigned == 0, 'status': 'CACHED_VALUES_ONLY'},
                    'completeness': completeness, 'modules': modules, 'status': completeness['state'],
                    'financial_results_available': False, 'calculation_status': 'NATIVE_VERIFICATION_REQUIRED',
                    'profile_sha256': profile['profile_sha256'], 'native_mapping': profile['native']}
        finally:
            actual.close()

    def prepare(self, workbook, updates):
        from .field_semantics import validate_updates, contract_digest
        actual = self._open(workbook)
        try:
            if not isinstance(updates, list) or not 1 <= len(updates) <= 2000:
                raise ValueError('Prévoir de 1 à 2 000 écritures par lot.')
            if not all(isinstance(u, dict) for u in updates):
                raise ValueError('Une écriture doit être un objet.')
            validate_updates(self.catalog(), updates)
            normalized = []; logical_changes = []; profile = self.profile
            for update in updates:
                allowed = {'sheet','cell','value','reason','evidence','evidence_id','expected','replace_existing','override_default'}
                if set(update) - allowed or not {'sheet','cell','value','reason'} <= set(update):
                    raise ValueError('Clés de saisie incomplètes ou non autorisées.')
                evidence = update.get('evidence', update.get('evidence_id'))
                if not isinstance(evidence, str) or not evidence:
                    raise ValueError('Une source documentaire est requise.')
                if isinstance(update['value'], str) and update['value'].lstrip().startswith(('=', '+', '@')):
                    raise ValueError('Formule libre réservée à une proposition de variante explicite.')
                change = {k:v for k,v in update.items() if k not in ('expected','evidence_id')}
                change.update(expected=actual.snapshot(update['sheet'], update['cell']), evidence=evidence)
                if 'expected' in update and core.packed(update['expected']) != core.packed(change['expected']):
                    raise ValueError('La cellule a changé depuis la préparation.')
                item = core.normalize_change(actual, self.schema, change)
                original = map_location(profile, item['sheet'], item['cell'], reverse=True)
                if not original:
                    raise ValueError('Une nouvelle cellule nécessite un contrat métier avant saisie par agent.')
                normalized.append(item)
                logical_changes.append({**item, 'sheet': original['sheet'], 'cell': original['cell']})
            if len({(x['sheet'], x['cell']) for x in normalized}) != len(normalized):
                raise ValueError('Une cellule ne peut être écrite deux fois dans un lot.')
            if 'Control' in profile['origin_schema'].get('cells', {}):
                from .decision_offers import business_checks
                business_checks(profile,LogicalWorkbook(actual, profile), _logical_schema(profile, self.schema), logical_changes)
                for item in logical_changes:
                    if (item['sheet'], item['cell']) == ('Control', 'C10') and item['value'] is not None:
                        date = dt.date.fromisoformat(item['value'])
                        if (date.month, date.day) != (1, 1):
                            raise ValueError('La date de début doit être le 1er janvier.')
            return {'schema': 'tca-bp-plan/v1', 'model_id': self.model_id, 'source_sha256': actual.hash,
                    'source_name': actual.path.name, 'source_input_signature': actual.input_signature(self.schema),
                    'changes': normalized, 'updates': deepcopy(normalized), 'valid': True,
                    'semantics_sha256': contract_digest(), 'profile_sha256': profile['profile_sha256'],
                    'calculation_status': 'RECALCULATION_REQUIRED_AFTER_APPLY',
                    'prepared_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        except (KeyError, TypeError, OverflowError) as error:
            raise ValueError('Saisie invalide : ' + str(error)) from error
        finally:
            actual.close()

    def apply(self, workbook, plan, output):
        from .field_semantics import contract_digest
        output = Path(output).resolve(); workbook = Path(workbook).resolve()
        journal = output.with_suffix('.journal.json')
        if output.exists() or journal.exists() or output in (workbook, self.template_path.resolve()) or output.suffix.lower() != '.xlsm':
            raise ValueError('La sortie XLSM et son journal doivent être neufs.')
        if not output.parent.is_dir():
            raise ValueError('Le dossier de sortie doit exister.')
        if plan.get('schema') != 'tca-bp-plan/v1' or plan.get('model_id') != self.model_id or plan.get('profile_sha256') != self.profile['profile_sha256']:
            raise ValueError('Le plan appartient à une autre version du profil.')
        if plan.get('semantics_sha256') != contract_digest() or plan.get('source_sha256') != digest(workbook):
            raise ValueError('Plan périmé : source ou catalogue modifié.')
        validated = self.prepare(workbook, [{k:v for k,v in c.items() if k != 'kind'} for c in plan['changes']])
        if validated['source_input_signature'] != plan.get('source_input_signature'):
            raise ValueError('Plan périmé : saisies modifiées.')
        actual = self._open(workbook); temporary = None; published = []
        try:
            changes = validated['changes']; replacements = {}
            for sheet in {c['sheet'] for c in changes}:
                replacements[actual.sheets[sheet]['part']] = core.patch_sheet(actual, sheet, [c for c in changes if c['sheet'] == sheet])[0]
            for sheet, meta in actual.sheets.items():
                raw = replacements.get(meta['part'], actual.z.read(meta['part']))
                native = set(self.schema.get('native_table_outputs', {}).get(sheet, [])) | set(self.schema.get('native_outputs', {}).get(sheet, []))
                def clear(match):
                    return core.xml_cell(match[0], None, 'text') if match[1].decode() in native and not re.search(rb'<f(?:\s|>)', match[0]) else match[0]
                replacements[meta['part']] = invalidate_caches(core.CELL_RX.sub(clear, raw))
            replacements['xl/workbook.xml'] = core.mark_for_native_calculation(actual.z.read('xl/workbook.xml'))
            chain, _ = core.patch_calculation_chain(actual, changes)
            if chain is not None: replacements['xl/calcChain.xml'] = chain
            fd, name = tempfile.mkstemp(prefix='.web-input-', suffix='.xlsm', dir=output.parent); os.close(fd); temporary = Path(name)
            with zipfile.ZipFile(temporary, 'w') as archive:
                for info in actual.z.infolist():
                    raw = replacements.get(info.filename, actual.z.read(info.filename))
                    if info.filename.startswith('xl/charts/') and info.filename.endswith('.xml'): raw = invalidate_chart(raw)
                    archive.writestr(info, raw)
            after = self._open(temporary)
            try:
                for change in changes:
                    value = core.excel_serial(change['value'], after.date1904) if change['kind'] == 'date' and change['value'] is not None else change['value']
                    if after.value(change['sheet'], change['cell']) != value or after.formula(change['sheet'], change['cell']) is not None:
                        raise ValueError('La valeur écrite ne correspond pas au plan.')
                receipt = {'schema': 'tca-bp-receipt/v1', 'model_id': self.model_id,
                           'source_sha256': actual.hash, 'source_name': workbook.name, 'source_unchanged': digest(workbook) == actual.hash,
                           'output_sha256': after.hash, 'output_name': output.name, 'output_path': str(output),
                           'output_input_signature': after.input_signature(self.schema), 'changes': changes,
                           'native_calculation': 'PENDING_EXCEL', 'calculation_status': 'RECALCULATION_REQUIRED',
                           'financial_results_available': False, 'formula_and_chart_caches_invalidated': True,
                           'profile_sha256': self.profile['profile_sha256'], 'checks': {'macros_executed': False}}
            finally: after.close()
            if not receipt['source_unchanged']: raise ValueError('La source a changé pendant la transaction.')
            os.link(temporary, output); published.append(output)
            _write(journal, receipt); published.append(journal)
            return {**receipt, 'journal_path': str(journal)}
        except Exception:
            for path in reversed(published): path.unlink(missing_ok=True)
            raise
        finally:
            actual.close()
            if temporary: temporary.unlink(missing_ok=True)
