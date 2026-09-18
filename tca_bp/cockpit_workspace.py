"""Bounded cockpit projections and catalogue-only commands.

This layer does not calculate financial values or write workbooks. The existing
decision workspace owns proposals, sources, idempotence and adoption. Sheet and
binding identities belong to the pinned business profile, not to UI labels.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from types import SimpleNamespace

from .model_registry import model_pin
from .storage import canonical, check_id
from .web_chat import validate_operations
from .web_model_profile import initial_profile, map_location


GROUPS = [
    ('framework', 'Cadre du projet'), ('sales', 'Ventes et contrats'),
    ('operations', 'Coûts, exploitation et équipe'),
    ('funding', 'Investissements et financements'),
    ('tax', 'Fiscalité et besoin d’exploitation'),
    ('statements', 'Résultats et trésorerie'), ('value', 'Scénarios et valeur'),
    ('checks', 'Tableau de bord et validations'), ('custom', 'Feuilles ajoutées'),
]
THEMES = [('sales', 'Ventes et contrats'), ('costs', 'Coûts et marge'),
          ('team', 'Équipe'), ('investments', 'Investissements et financement'),
          ('cash', 'Trésorerie et fiscalité'), ('synthesis', 'Synthèse et valeur')]

# Presentation only: neither this table nor a sheet's group grants write access.
# Keys are original business names; the profile supplies current physical names.
SHEET_VIEWS = {
    'Légende': ('Conventions et unités', 'framework', [], 'help'),
    'Previsionnel': ('Périmètre du prévisionnel', 'framework', ['synthesis'], 'help'),
    'Control': ('Calendrier et configuration', 'framework', ['cash'], 'settings'),
    'Assumptions': ('Offres et hypothèses communes', 'framework', ['sales', 'costs'], 'settings'),
    'DATA Contrats': ('Contrats et conditions commerciales', 'sales', ['sales'], 'register'),
    'Contrats': ('Calendrier des contrats', 'sales', ['sales'], 'series'),
    'Revenue': ('Revenu reconnu, facturé et encaissé', 'sales', ['sales'], 'series'),
    'DATA COGS': ('Achats et coûts directs', 'operations', ['costs'], 'register'),
    'COGS': ('Coûts directs par période', 'operations', ['costs'], 'series'),
    'Stock': ('Stock et politique de stockage', 'operations', ['costs', 'cash'], 'settings'),
    'Charges_Externes': ('Charges externes', 'operations', ['costs'], 'register'),
    'Effectifs': ('Équipe et recrutements', 'operations', ['team'], 'register'),
    'DATA CAPEX': ('Investissements', 'funding', ['investments'], 'register'),
    'CAPEX': ('Investissements et amortissements', 'funding', ['investments'], 'series'),
    'Financement Dette': ('Emprunts et échéanciers', 'funding', ['investments'], 'register'),
    'DATA Financement': ('Opérations de financement', 'funding', ['investments'], 'register'),
    'Financement E&S': ('Fonds propres et subventions', 'funding', ['investments'], 'series'),
    'SUBVENTION_INVEST': ('Subventions d’investissement', 'funding', ['investments'], 'register'),
    'CALCUL_CIR': ('Crédit d’impôt', 'tax', ['team', 'cash'], 'settings'),
    'ATELIER_CIR_IS': ('Atelier fiscal', 'tax', ['cash'], 'settings'),
    'BFR': ('Besoin d’exploitation', 'tax', ['cash'], 'series'),
    'Modèle financier': ('Trajectoires financières', 'statements', ['synthesis', 'cash'], 'series'),
    'Compte de Résultat': ('Compte de résultat', 'statements', ['synthesis'], 'statements'),
    'Bilan': ('Bilan', 'statements', ['synthesis'], 'statements'),
    'Flux de trésorerie': ('Flux de trésorerie', 'statements', ['cash'], 'series'),
    'Plan de financement': ('Plan de financement', 'statements', ['investments', 'synthesis'], 'statements'),
    'KPI Dashboard': ('Indicateurs', 'checks', ['synthesis'], 'statements'),
    'Contrôles': ('Contrôles et points à compléter', 'checks', ['synthesis'], 'controls'),
    'Sensi TCA': ('Hypothèses de sensibilité', 'value', ['synthesis'], 'sensitivity'),
    'Sensi Analyses': ('Analyses de sensibilité', 'value', ['synthesis'], 'sensitivity'),
    'Sensi Graphiques': ('Graphiques de sensibilité', 'value', ['synthesis'], 'sensitivity'),
    'Valorisation': ('Valorisation', 'value', ['synthesis'], 'valuation'),
    'Comparables': ('Comparables', 'value', ['synthesis'], 'register'),
}

# Display projections of existing, qualified readers. These lists do not define
# formulas, addresses or new financial metrics. Unmapped sheets remain readable
# in the bounded workbook view; an empty projection never means an empty sheet.
OUTPUT_VIEWS = {
    'Revenue': (('revenue', 'billed_revenue', 'customer_receipts'), (), ()),
    'Modèle financier': (('cash', 'receipts', 'payments'), (), ('revenue', 'gross_margin', 'ebitda', 'net_income')),
    'Compte de Résultat': ((), (), ('revenue', 'gross_margin', 'ebitda', 'net_income')),
    'KPI Dashboard': ((), ('cash_min', 'cash_break_date', 'financing_need'), ('revenue', 'gross_margin', 'ebitda', 'net_income')),
    'Valorisation': ((), ('valuation', 'valuation_vc'), ()),
}


def _can_propose(field):
    # Preserve the existing semantic gate. HORS_PERIMETRE is used by independent
    # non-TCA models and test fixtures; their own explicit catalogue still rules.
    semantic = field.get('semantics') or {}
    return not (semantic.get('status') == 'REEXAMEN_REQUIS' or
                semantic.get('status') == 'ETABLI_MODELE' and semantic.get('can_propose') is False)


def _scalar(value):
    if value is not None and not isinstance(value, (str, bool, int, float)):
        raise ValueError('Une valeur scalaire est requise.')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('La valeur doit être finie.')
    if isinstance(value, str) and (len(value) > 32767 or value.lstrip().startswith(('=', '+', '@'))):
        raise ValueError('Une formule ne peut pas être saisie depuis le parcours métier.')


class CockpitWorkspace:
    def __init__(self, decision):
        self.d = decision
        self.app, self.work, self.store = decision.app, decision.work, decision.store

    def _context(self, case_id):
        row = self.app._row(case_id)
        engine = self.app._engine_for_case(row)
        # _workbook verifies the immutable workbook and pinned model. No mtime
        # shortcut or catalogue guessed from the visual prototype is used.
        path = self.app._workbook(row)
        profile = getattr(engine, 'profile', None)
        if not profile:
            profile = initial_profile(engine, path)
        records = [item for item in profile['sheets'] if not item.get('deleted')]
        fields = [f for f in profile['fields'] if not f.get('deleted')]
        return row, engine, profile, records, fields

    def _assert_snapshot(self, row, current=None):
        current = current or self.app._row(row['id'])
        if (row['revision'] != current['revision'] or row['sha256'] != current['sha256']
                or model_pin(row) != model_pin(current)):
            raise ValueError('Le dossier a changé pendant la lecture. Actualiser son état avant de poursuivre.')

    @staticmethod
    def _header(row, profile):
        return {'schema': 'tca-cockpit/1', 'case_id': row['id'], 'revision': row['revision'],
                'calculation_status': row['calculation_status'], 'model': model_pin(row),
                'profile_version': profile['version'], 'profile_sha256': profile['profile_sha256']}

    @staticmethod
    def _bindings(profile, records, fields):
        names = {r['name']: r for r in records}
        for field in fields:
            record = names.get(field.get('sheet'))
            if record is None:
                continue
            for cell in field.get('cells', []):
                if ':' in cell:
                    continue
                logical = map_location(profile, record['name'], cell, reverse=True)
                if not logical:
                    continue
                identity = [record['id'], field['id'], logical['cell']]
                yield {'binding_id': 'binding_' + hashlib.sha256(canonical(identity).encode()).hexdigest()[:24],
                       'field': field, 'record': record, 'cell': cell, 'logical_cell': logical['cell']}

    def _sheets(self, engine, profile, records, fields):
        by_sheet = defaultdict(list)
        for field in fields:
            by_sheet[field.get('sheet')].append(field)
        agents = {a['sheet']: a for a in profile.get('agents', []) if not a.get('deleted')}
        names = {r['name']: r for r in records}
        labels = {r['id']: SHEET_VIEWS.get(r.get('original_name'), (r['name'],))[0] for r in records}
        result = []
        for record in sorted(records, key=lambda r: r.get('index', 0)):
            name = record['name']
            label, group, themes, view = SHEET_VIEWS.get(record.get('original_name'),
                                                       (name, 'custom', [], 'custom'))
            agent = agents.get(name, {})
            register = engine.schema.get('registers', {}).get(name)
            local_fields = by_sheet[name]
            result.append({'id': record['id'], 'name': name, 'original_name': record.get('original_name'),
                           'label': label, 'purpose': agent.get('role') or record.get('role') or name,
                           'role': record.get('role') or agent.get('role') or name,
                           'group_id': group, 'theme_ids': list(themes), 'view_kind': view,
                           'field_count': len(local_fields),
                           'binding_count': sum(len(f.get('cells', [])) for f in local_fields),
                           'dependencies': [{'id': names[n]['id'], 'name': n, 'label': labels[names[n]['id']]}
                                            for n in agent.get('dependencies', []) if n in names],
                           'dependency_basis': 'CONTRAT_METIER_VERSIONNE',
                           'fields': [{'field_id': f['id'], 'label': f.get('label') or f['id'],
                                       'value_type': f.get('kind', 'text'), 'unit': f.get('unit'),
                                       'choices': f.get('choices') or [], 'can_propose': _can_propose(f),
                                       'binding_count': len(f.get('cells', []))} for f in local_fields],
                           'register': {'start_row': register['start_row'], 'end_row': register['end_row'],
                                        'can_add': True} if register else None})
        return result

    def catalog(self, case_id):
        # Read-only HTTP requests must not create an exclusive filesystem
        # transaction lock: catalogue/SSE refreshes otherwise reject a user's
        # first answer as an uncertain write. Local readers share the same
        # coordinator lock; immutable snapshots still guard native changes.
        with self.d.lock:
            row, engine, profile, records, fields = self._context(case_id)
            result = {**self._header(row, profile),
                    'groups': [{'id': key, 'label': label} for key, label in GROUPS],
                    'themes': [{'id': key, 'label': label} for key, label in THEMES],
                    'sheets': self._sheets(engine, profile, records, fields)}
            self._assert_snapshot(row)
            return result

    @staticmethod
    def _find_sheet(records, sheet_id):
        found = next((r for r in records if r['id'] == sheet_id), None)
        if found is None:
            raise ValueError('Feuille inconnue ou supprimée dans ce modèle.')
        return found

    def sheet(self, case_id, sheet_id, offset=0, limit=100):
        if type(offset) is not int or type(limit) is not int or not 0 <= offset <= 1000000 or not 1 <= limit <= 500:
            raise ValueError('Pagination attendue : offset positif et 1 à 500 entrées.')
        with self.d.lock:
            row, engine, profile, records, fields = self._context(case_id)
            record = self._find_sheet(records, sheet_id)
            definitions = list(self._bindings(profile, [record], fields))
            definitions.sort(key=lambda b: (int(''.join(c for c in b['cell'] if c.isdigit())), b['cell']))
            draft = self.work.draft(case_id)
            fresh_draft = draft.get('revision') == row['revision'] and draft.get('source_sha256') == row['sha256']
            maintenance = any(op.get('type') != 'set_value' for op in draft.get('operations', []))
            proposed = {(op.get('sheet'), op.get('cell')): op for op in draft.get('operations', [])
                        if op.get('type') == 'set_value'} if fresh_draft and not maintenance else {}
            states = json.loads(row['field_states'])
            def read(wb, current):
                self._assert_snapshot(row, current)
                entries = []
                for binding in definitions[offset:offset + limit]:
                    field, cell = binding['field'], binding['cell']
                    formula, value = wb.formula(record['name'], cell), wb.value(record['name'], cell)
                    state = states.get(record['name'] + '!' + cell, {})
                    proposal = proposed.get((record['name'], cell))
                    editable = formula is None and _can_propose(field) and not maintenance
                    entries.append({'binding_id': binding['binding_id'], 'field_id': field['id'],
                                    'sheet_id': record['id'], 'sheet': record['name'], 'cell': cell,
                                    'label': field.get('label') or field['id'], 'value': proposal['value'] if proposal else value,
                                    'current_value': value, 'proposed': proposal is not None,
                                    'formula': '=' + formula if formula is not None else None,
                                    'unit': field.get('unit'), 'value_type': field.get('kind', 'text'),
                                    'choices': field.get('choices') or [],
                                    'evidence_id': proposal.get('evidence_id') if proposal else state.get('evidence'),
                                    'status': proposal.get('status', 'HYPOTHESE') if proposal else state.get('status', 'HYPOTHESE' if value is not None else 'NON_RENSEIGNE'),
                                    'calculated': formula is not None, 'editable': editable,
                                    'reason': '' if editable else 'Terminer ou abandonner le brouillon de maintenance avant une saisie métier.' if maintenance else 'Résultat ou défaut calculé protégé.' if formula is not None else 'Signification métier à réexaminer.'})
                return entries
            entries = self.work._read(case_id, read)
            self._assert_snapshot(row)
            sheet = next(s for s in self._sheets(engine, profile, records, fields) if s['id'] == sheet_id)
            return {**self._header(row, profile), 'sheet': sheet, 'entries': entries,
                    'total': len(definitions), 'offset': offset, 'limit': limit,
                    'draft': {'id': draft.get('id'), 'status': draft['status'], 'current': fresh_draft,
                              'maintenance': maintenance}}

    def _ordinary_draft(self, case_id):
        draft = self.work.draft(case_id)
        if any(op.get('type') != 'set_value' for op in draft.get('operations', [])):
            raise ValueError('Terminer ou abandonner le brouillon de maintenance avant une saisie métier.')

    def outputs(self, case_id, sheet_id):
        """Project existing readers from one immutable, qualified snapshot.

        Neither a formula cache nor the presence of a named sheet establishes
        financial availability. The regular engine's qualification and current
        calculation proof remain authoritative, including after model changes.
        """
        from .decision_model import read_annual_metrics, read_metrics, read_series
        with self.d.lock:
            row, engine, profile, records, _ = self._context(case_id)
            record = self._find_sheet(records, sheet_id)
            case = self.app.get_case(case_id)
            self._assert_snapshot(row, case)
            current = case.get('outputs_current') is True
            selection = OUTPUT_VIEWS.get(record.get('original_name'))
            provenance = {'case_id': case_id, 'revision': row['revision'], 'sha256': row['sha256']}
            result = {**self._header(row, profile), 'schema': 'tca-cockpit-outputs/1',
                      'sha256': row['sha256'], 'outputs_current': current, 'sheet_id': sheet_id,
                      'sheet': {key: record.get(key) for key in ('id', 'name', 'original_name')},
                      'calculation_details': case.get('calculation_details'),
                      'series': [], 'metrics': [], 'annual_metrics': [], 'diagnostics': []}
            if not selection:
                result['diagnostics'].append('Cette feuille ne dispose pas encore de projection métier qualifiée. Ses données restent consultables dans la grille du classeur courant.')
            else:
                def read(wb, snapshot):
                    self._assert_snapshot(row, snapshot)
                    # Bind every nested reader to exactly the same workbook,
                    # model and qualification snapshot; do not reopen the head
                    # separately for monthly, annual and scalar observations.
                    view = SimpleNamespace(
                        app=SimpleNamespace(engine_for_case=lambda _: engine, get_case=lambda _: case),
                        work=SimpleNamespace(_read=lambda _, action: action(wb, snapshot)),
                        profile=self.d.profile)
                    series = read_series(view, case_id) if selection[0] or selection[1] else []
                    metrics = read_metrics(view, case_id) if selection[1] else []
                    annual = read_annual_metrics(view, case_id) if selection[2] else []
                    for item in series:
                        if item['id'] not in selection[0]:
                            continue
                        permitted = current and item.get('qualification', {}).get('scenario_ready') is True
                        result['series'].append({**item, 'values': item['values'] if permitted else [None] * len(item['categories']),
                                                 'available': permitted, 'provenance': provenance})
                    for item in metrics:
                        if item['id'] not in selection[1]:
                            continue
                        clean = {key: value for key, value in item.items() if key != 'cached_value'}
                        # A calculated null break date means no negative month;
                        # it must stay distinguishable from an unavailable date.
                        clean['available'] = current and (item.get('status') == 'CALCULE' if item['id'] in ('cash_min', 'cash_break_date', 'financing_need') else item.get('value') is not None and item.get('qualification', {}).get('scenario_ready') is True)
                        if not clean['available']:
                            clean['value'] = None
                        clean.update(period=item.get('period', 'horizon'), provenance=provenance)
                        if item.get('sheet') and item.get('cell'):
                            clean['sources'] = [{'sheet': item['sheet'], 'cell': item['cell']}]
                        else:
                            clean['sources'] = next((s['sources'] for s in series if s['id'] == 'cash'), [])
                        result['metrics'].append(clean)
                    for item in annual:
                        if item['metric'] in selection[2]:
                            result['annual_metrics'].append({**item, 'value': item['value'] if current else None,
                                'available': current and item.get('available') is True, 'provenance': provenance,
                                'sources': [{'sheet': item['sheet'], 'cell': item['cell']}]})
                self.work._read(case_id, read)
                if not current:
                    result['diagnostics'].append('Les résultats de cette révision nécessitent un recalcul ; les valeurs en cache ne sont pas présentées comme résultats actuels.')
                elif not any(item['available'] for key in ('series', 'metrics', 'annual_metrics') for item in result[key]):
                    result['diagnostics'].append('Le calcul courant existe, mais la qualification ou les données nécessaires à cette vue restent à compléter.')
            # Recheck full workbook/model integrity as well as the mutable head.
            self.app._workbook(row)
            self._assert_snapshot(row)
            return result

    def cells(self, case_id, sheet, row=1, column=1, rows=100, columns=26):
        """Bounded workbook window with server-owned business permissions."""
        with self.d.lock:
            snapshot, engine, profile, records, fields = self._context(case_id)
            record = next((r for r in records if r['name'] == sheet), None)
            if record is None:
                raise ValueError('Feuille inconnue ou supprimée dans ce modèle.')
            bindings = defaultdict(list)
            for binding in self._bindings(profile, [record], fields):
                bindings[binding['cell']].append(binding)
            draft = self.work.draft(case_id)
            maintenance = any(op.get('type') != 'set_value' for op in draft.get('operations', []))
            result = self.work.cells(case_id, sheet, row, column, rows, columns)
            if result['revision'] != snapshot['revision']:
                raise ValueError('La fenêtre ne correspond plus à la révision du catalogue. Actualiser la feuille.')
            self._assert_snapshot(snapshot)
            for cell in result['cells']:
                candidates = bindings[cell['cell']]
                known = len(candidates) == 1
                default = engine.schema.get('cells', {}).get(sheet, {}).get(cell['cell'], {}).get('default_formula')
                reason = ('Terminer ou abandonner le brouillon de maintenance.' if maintenance else
                          'Résultat ou défaut calculé protégé.' if cell['formula'] is not None or default else
                          'Entrée hors catalogue ou correspondance ambiguë.' if not known else
                          'Signification métier à réexaminer.' if not _can_propose(candidates[0]['field']) else '')
                cell.update(editable=not bool(reason), sheet_id=record['id'], read_only_reason=reason,
                            binding_id=candidates[0]['binding_id'] if known else None)
            return result

    @staticmethod
    def _command(body, extra):
        if not isinstance(body, dict) or set(body) - ({'expected_revision', 'request_id'} | set(extra)):
            raise ValueError('Commande métier inconnue ou incomplète.')
        if type(body.get('expected_revision')) is not int or body['expected_revision'] < 0:
            raise ValueError('La révision attendue est obligatoire.')
        check_id(body.get('request_id'))

    def answers(self, case_id, body, *, reserve=True, origin='manual'):
        self._command(body, {'answers'})
        answers = body.get('answers')
        if not isinstance(answers, list) or not 1 <= len(answers) <= 500:
            raise ValueError('Préparer entre 1 et 500 réponses métier.')
        def propose():
            with self.store.case_lock(case_id):
                self.d.check_revision(case_id, body['expected_revision'])
                self._ordinary_draft(case_id)
                row, engine, profile, records, fields = self._context(case_id)
                bindings = {b['binding_id']: b for b in self._bindings(profile, records, fields)}
                normalized, seen, source_ids = [], set(), set()
                for answer in answers:
                    allowed = {'sheet_id', 'binding_id', 'value', 'evidence_id', 'status', 'reason'}
                    if not isinstance(answer, dict) or set(answer) - allowed or not {'sheet_id', 'binding_id', 'value', 'evidence_id'} <= set(answer):
                        raise ValueError('Réponse métier incomplète ou contenant une opération interdite.')
                    binding = bindings.get(answer['binding_id'])
                    if not binding or binding['record']['id'] != answer['sheet_id']:
                        raise ValueError('Ce champ ne correspond pas à cette feuille du dossier.')
                    field, record, cell = binding['field'], binding['record'], binding['cell']
                    target = (record['name'], cell)
                    if target in seen:
                        raise ValueError('Une entrée ne peut recevoir deux réponses dans le même lot.')
                    seen.add(target)
                    _scalar(answer['value'])
                    if not _can_propose(field):
                        raise ValueError('La signification métier de ce champ doit être réexaminée.')
                    if not isinstance(answer['evidence_id'], str) or not answer['evidence_id']:
                        raise ValueError('Une source du dossier est obligatoire pour cette réponse.')
                    source_ids.add(answer['evidence_id'])
                    normalized.append({'field_id': field['id'], 'sheet': record['name'], 'cell': cell,
                                       'value': answer['value'], 'evidence_id': answer['evidence_id'],
                                       'status': answer.get('status', 'CONFIRME'),
                                       'reason': answer.get('reason') or 'Réponse documentée dans le cockpit.'})
                for source_id in source_ids:
                    self.d.source(case_id, source_id)
                def verify(wb, current):
                    if any(wb.formula(item['sheet'], item['cell']) is not None or
                           engine.schema.get('cells', {}).get(item['sheet'], {}).get(item['cell'], {}).get('default_formula')
                           for item in normalized):
                        raise ValueError('Les formules et défauts calculés sont protégés dans ce parcours.')
                self.work._read(case_id, verify)
            # add_operations owns its non-reentrant filesystem transaction lock.
            # Its revision/source guards close the interval after this preflight.
            return self.d.answers(case_id, {'expected_revision': row['revision'], 'answers': normalized}, origin=origin)
        return self.d.request(case_id, 'cockpit/answers', body, propose) if reserve else propose()

    def operations(self, case_id, body, *, origin='manual'):
        """Translate physical grid targets to the very same semantic answers.

        Scope restricts the gesture; it never grants permission to an arbitrary
        cell. The durable intent reserves the original request exactly once.
        """
        self._command(body, {'operations', 'scope'})
        operations, scope = body.get('operations'), body.get('scope')
        if not isinstance(operations, list) or not 1 <= len(operations) <= 500:
            raise ValueError('Préparer entre 1 et 500 saisies métier.')
        if not isinstance(scope, dict) or set(scope) - {'sheet', 'range', 'ranges', 'sheets'}:
            raise ValueError('Un périmètre de saisie explicite est requis.')
        for op in operations:
            if not isinstance(op, dict) or op.get('type') != 'set_value':
                raise ValueError('Le cockpit autorise uniquement les valeurs des entrées métier.')
            if not isinstance(op.get('evidence_id'), str) or not op['evidence_id']:
                raise ValueError('Une source du dossier est obligatoire pour chaque saisie.')

        def propose():
            with self.store.case_lock(case_id):
                self.d.check_revision(case_id, body['expected_revision'])
                self._ordinary_draft(case_id)
                _, _, profile, records, fields = self._context(case_id)
                sources = [self.d.source(case_id, source_id) for source_id in {op['evidence_id'] for op in operations}]
                normalized = validate_operations(operations, scope, {'case_id': case_id, 'sources': sources})
                # Even identical duplicate targets are ambiguous as documentary
                # answers (two sources/statuses); do not silently deduplicate.
                if len(normalized) != len(operations):
                    raise ValueError('Une entrée ne peut recevoir deux réponses dans le même lot.')
                bindings = defaultdict(list)
                for binding in self._bindings(profile, records, fields):
                    bindings[(binding['record']['name'], binding['cell'])].append(binding)
                answers = []
                for op in normalized:
                    candidates = bindings[(op['sheet'], op['cell'])]
                    if len(candidates) != 1:
                        raise ValueError('Entrée hors catalogue ou correspondance métier ambiguë.')
                    binding = candidates[0]
                    answers.append({'sheet_id': binding['record']['id'], 'binding_id': binding['binding_id'],
                                    **{key: op[key] for key in ('value', 'evidence_id', 'status', 'reason') if key in op}})
            return self.answers(case_id, {'expected_revision': body['expected_revision'],
                                         'request_id': body['request_id'], 'answers': answers}, reserve=False, origin=origin)
        return self.d.request(case_id, 'cockpit/operations' + ('/chat' if origin == 'chat' else ''), body, propose)

    def record(self, case_id, sheet_id, body):
        self._command(body, {'evidence_id', 'values'})
        values = body.get('values')
        if not isinstance(values, dict) or not values or len(values) > 200:
            raise ValueError('Un registre attend des valeurs indexées par identifiant métier.')
        for value in values.values():
            _scalar(value)
        def propose():
            with self.store.case_lock(case_id):
                self.d.check_revision(case_id, body['expected_revision'])
                self._ordinary_draft(case_id)
                _, engine, profile, records, fields = self._context(case_id)
                record = self._find_sheet(records, sheet_id)
                if record['name'] not in engine.schema.get('registers', {}):
                    raise ValueError('Cette feuille ne possède pas de registre métier.')
                known = {f['id']: f for f in fields if f.get('sheet') == record['name']}
                if any(key not in known or not _can_propose(known[key]) for key in values):
                    raise ValueError('Champ inconnu ou non autorisé dans ce registre.')
                self.d.source(case_id, body.get('evidence_id'))
            return self.d.prepare_record(case_id, record['name'], body)
        return self.d.request(case_id, 'cockpit/records/' + sheet_id, body, propose)
