"""Qualification documentaire et disponibilité de périmètres financiers.

Aucune loi, aucun taux fiscal et aucune écriture Excel dans ce module. Le service
vérifie d'abord modèle, classeur et appartenance/empreintes des sources. Les
qualifications sont ensuite fondées sur les valeurs propriétaires effectivement
lues ; une cellule calculée ou un cache favorable ne confirme jamais sa source.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
import math
import re
import unicodedata

SCOPES = ('CA', 'COGS', 'CASH', 'FISCALITE', 'DCF')
DEPENDENCIES = {'CA': (), 'COGS': ('CA',), 'FISCALITE': (),
                'CASH': ('CA', 'COGS', 'FISCALITE'), 'DCF': ('CASH', 'FISCALITE')}
_UNDECIDED = {'a confirmer', 'a completer', 'non renseigne', 'inconnu', 'inconnue',
              'unknown', 'non determine', 'a qualifier'}
_REGISTER_SCOPES = {'DATA Contrats': ('CA',), 'Effectifs': ('CASH',),
                    'DATA CAPEX': ('CASH',), 'DATA Financement': ('CASH',),
                    'Financement Dette': ('CASH',), 'SUBVENTION_INVEST': ('CASH',)}
MODULES = ('CA', 'COGS', 'STOCK', 'CIR', 'REGLES_FISCALES', 'BFR_TERMINAL', *_REGISTER_SCOPES)


def scope_for_output(sheet: str, address: str) -> str | None:
    """Périmètre conservateur d'une sortie ; les entrées ne sont pas masquées."""
    if sheet == 'Revenue':
        match = re.fullmatch(r'[A-Z]+(\d+)', address)
        return 'CA' if match and int(match[1]) == 282 else 'CASH'
    if sheet in ('Contrats', 'DATA Contrats'):
        return 'CA'
    if sheet in ('COGS', 'DATA COGS'):
        return 'COGS'
    if sheet in ('ATELIER_CIR_IS', 'CALCUL_CIR'):
        return 'FISCALITE'
    if sheet in ('Valorisation', 'Comparables'):
        return 'DCF'
    if sheet in ('Sensi TCA', 'Sensi Analyses', 'Sensi Graphiques'):
        return 'CASH'
    if sheet == 'Compte de Résultat' and re.fullmatch(r'[C-M]7', address):
        return 'CA'
    if sheet == 'Compte de Résultat' and re.fullmatch(r'[D-M]23', address):
        return 'COGS'
    if sheet in ('Légende', 'Manuel', 'Previsionnel'):
        return None
    return 'CASH'


def error_perimeter(sheet: str, address: str, years: int) -> tuple[str, bool]:
    """Périmètre d'erreur et appartenance à un rectangle annuel documenté.

    Seuls les rectangles connus sont exclus au-delà de l'horizon. Une adresse
    non reconnue reste active : on ne déduit pas son innocuité d'un cache vide.
    """
    scope = scope_for_output(sheet, address) or 'CASH'
    match = re.fullmatch(r'([A-Z]+)(\d+)', address)
    if not match:
        return scope, True
    letters, row = match[1], int(match[2])
    col = 0
    for letter in letters:
        col = col * 26 + ord(letter) - 64
    if not isinstance(years, int) or isinstance(years, bool) or not 1 <= years <= 10:
        return scope, True
    annual = None
    if sheet == 'Valorisation' and 19 <= row <= 33:
        annual = (4, 13)
    elif sheet == 'ATELIER_CIR_IS' and 14 <= row <= 134:
        annual = (3, 13)
    elif sheet == 'CALCUL_CIR' and 16 <= row <= 46:
        annual = (3, 13)
    elif sheet == 'Compte de Résultat' and 7 <= row <= 85:
        annual = (4, 13)
    elif sheet in ('Revenue', 'Contrats') and row >= 7:
        annual = (5, 14)
    elif sheet == 'Modèle financier' and row >= 4:
        annual = (3, 12)
        if 20 <= col <= 151:
            return scope, col - 20 < years * 12
    if annual and annual[0] <= col <= annual[1]:
        return scope, col - annual[0] < years
    return scope, True


def unavailable(message='Évaluer les qualifications de cette version et de ses sources.') -> dict:
    return {'schema': 'tca-bp-qualifications/1', 'status': 'A_EVALUER', 'questions': [],
            'scopes': {scope: {'qualification_ready': False, 'scenario_ready': False,
                'available': False, 'calculation_fresh': False, 'status': 'INDISPONIBLE',
                'blockers': [{'code': 'QUALIFICATION_NON_COURANTE', 'field': None, 'message': message,
                              'provisional': False}], 'hypotheses': []} for scope in SCOPES}}


def _norm(value):
    text = unicodedata.normalize('NFKD', str(value)).casefold()
    return ' '.join(''.join(c for c in text if not unicodedata.combining(c)).split())


def _blank(value):
    return value is None or isinstance(value, str) and not value.strip()


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _as_date(value, date1904=False):
    try:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if _number(value):
            return date(1904, 1, 1) + timedelta(days=value) if date1904 else date(1899, 12, 30) + timedelta(days=value)
        return date.fromisoformat(value) if isinstance(value, str) else None
    except (ValueError, TypeError, OverflowError):
        return None


def _equal(actual, recorded, kind, date1904):
    if kind == 'date':
        left, right = _as_date(actual, date1904), _as_date(recorded, date1904)
        return left is not None and left == right
    if isinstance(actual, bool) != isinstance(recorded, bool):
        return False
    return actual == recorded


def collect_snapshot(workbook, schema: dict) -> dict:
    """Lecture sur Workbook déjà reconnu par ModelEngine._open ; aucune mutation.

    À appeler dans l'ouverture du contexte/recalcul, pas depuis une lecture légère
    de liste de dossiers. Les états/source_id ne sont pas lus dans les caches.
    """
    cells = {}
    for sheet, entries in schema.get('cells', {}).items():
        for address, spec in entries.items():
            cells[sheet + '!' + address] = {
                'sheet': sheet, 'cell': address, 'value': workbook.value(sheet, address),
                'formula': workbook.formula(sheet, address),
                **{key: deepcopy(spec[key]) for key in ('kind', 'label', 'field_id', 'classification', 'initial_state',
                    'default_formula', 'choices', 'min', 'max', 'min_exclusive', 'max_exclusive') if key in spec}}
        workbook._sheet_cache.pop(sheet, None)
    registers = {}
    for sheet, spec in schema.get('registers', {}).items():
        occupied = []
        for row in range(spec['start_row'], spec['end_row'] + 1):
            if any(not _blank(cells.get(f'{sheet}!{col}{row}', {}).get('value'))
                   and cells.get(f'{sheet}!{col}{row}', {}).get('formula') is None
                   for col in spec['identity_columns']):
                occupied.append(row)
        registers[sheet] = {'occupied_rows': occupied, 'required_columns': list(spec.get('required', []))}
    default_owners = {}
    # Résolution des propriétaires de défauts, pas calcul d'un montant Excel.
    catalog_rows = {workbook.value('Assumptions', 'B' + str(row)): row for row in range(98, 122)}
    for row in registers.get('DATA CAPEX', {}).get('occupied_rows', []):
        category = cells.get(f'DATA CAPEX!C{row}', {}).get('value')
        catalog_row = catalog_rows.get(category)
        if catalog_row:
            default_owners[f'DATA CAPEX!F{row}'] = [f'DATA CAPEX!C{row}', f'Assumptions!C{catalog_row}']
            default_owners[f'DATA CAPEX!H{row}'] = [f'DATA CAPEX!G{row}'] if cells.get(f'DATA CAPEX!G{row}', {}).get('value') == 'Non' else [f'DATA CAPEX!G{row}', f'Assumptions!D{catalog_row}']
        default_owners[f'DATA CAPEX!M{row}'] = [f'DATA CAPEX!B{row}', f'DATA CAPEX!C{row}']
    for row in range(15, 28):
        for col in ('G', 'H', 'I', 'J', 'AF', 'AG', 'AH', 'AI', 'AJ'):
            default_owners[f'Assumptions!{col}{row}'] = [f'Assumptions!F{row}', 'Assumptions!D5']
    closing_type = workbook.value('Assumptions', 'B134')
    closing_rows = [row for row in registers.get('DATA Financement', {}).get('occupied_rows', [])
                    if cells.get(f'DATA Financement!C{row}', {}).get('value') == closing_type]
    # Une ancienne version ou un moteur de test reconnu peut ne pas exposer ce
    # diagnostic. Son absence reste inconnue et ne vaut jamais validation BFR.
    diagnostics = {'BFR!E49': workbook.value('BFR', 'E49') if 'BFR' in workbook.sheets else None}
    return {'schema': 'tca-bp-qualification-snapshot/1', 'model_id': schema.get('model_id'),
            'template_sha256': schema.get('template_sha256'), 'source_sha256': workbook.hash,
            'input_signature': workbook.input_signature(schema), 'date1904': workbook.date1904,
            'cells': cells, 'registers': registers, 'default_owners': default_owners,
            'closing': {'category': closing_type, 'rows': closing_rows}, 'diagnostics': diagnostics}


def classify_cell(cell: dict, recorded: dict | None, verified_source_ids: set[str], *, date1904=False) -> dict:
    """Ne confondre ni valeur héritée, défaut reconnu, hypothèse, ni confirmation."""
    recorded = recorded if isinstance(recorded, dict) else None
    value, formula = cell.get('value'), cell.get('formula')
    result = {'value': deepcopy(value), 'document_status': recorded.get('status') if recorded else None,
              'evidence': recorded.get('evidence') if recorded else None, 'confirmed': False, 'scenario_ready': False}
    if formula is not None:
        result['state'] = 'DEFAUT_CALCULE_MODELE' if cell.get('default_formula') == formula else 'FORMULE_NON_QUALIFIANTE'
        return result
    if _blank(value):
        result['state'] = 'DONNEE_ABSENTE'
        return result
    if isinstance(value, str) and _norm(value) in _UNDECIDED:
        result['state'] = 'A_CONFIRMER'
        return result
    if not recorded:
        result['state'] = 'VALEUR_HERITEE_NON_QUALIFIEE'
        return result
    if not _equal(value, recorded.get('value'), cell.get('kind'), date1904):
        result['state'] = 'ETAT_DOCUMENTAIRE_PERIME'
        return result
    if not isinstance(recorded.get('evidence'), str) or recorded['evidence'] not in verified_source_ids:
        result['state'] = 'SOURCE_NON_VERIFIEE'
        return result
    status = recorded.get('status')
    if status == 'CONFIRME':
        result.update(state='CONFIRME', confirmed=True, scenario_ready=True)
    elif status == 'HYPOTHESE':
        result.update(state='HYPOTHESE', scenario_ready=True)
    elif status == 'INACTIF':
        result['state'] = 'INACTIF_NE_NEUTRALISE_PAS_UNE_VALEUR'
    else:
        result['state'] = 'ETAT_NON_QUALIFIE'
    return result


def evaluate(snapshot: dict, field_states: dict, verified_source_ids, *, module_declarations=None, calculation=None) -> dict:
    """Retourner des gardes CA/COGS/CASH/FISCALITE/DCF liées à cet état exact.

    module_declarations[name] = {state:ACTIF|INACTIF, status:CONFIRME|HYPOTHESE,
    evidence:source_id}. REGLES_FISCALES exige aussi juridiction, valid_from,
    valid_to, model_id et template_sha256. Cette déclaration atteste une revue
    externe sourcée, elle ne certifie pas la loi. Les registres ne sont inactifs
    que si aucune ligne n'est présente. Une hypothèse permet uniquement un
    scénario explicitement provisoire, jamais available=True.
    """
    if snapshot.get('schema') != 'tca-bp-qualification-snapshot/1':
        raise ValueError('Snapshot de qualification reconnu requis.')
    if not isinstance(field_states, dict) or not isinstance(snapshot.get('cells'), dict):
        raise ValueError('États documentaires et cellules doivent être des objets.')
    if isinstance(verified_source_ids, (str, bytes, dict)):
        raise ValueError('Fournir une collection explicite des identifiants de sources vérifiées.')
    verified = set(verified_source_ids)
    if any(not isinstance(v, str) or not v for v in verified):
        raise ValueError('Identifiant de source vérifiée invalide.')
    declarations = module_declarations or {}
    if not isinstance(declarations, dict):
        raise ValueError('Les déclarations de modules doivent être un objet.')
    if any(name not in MODULES or not isinstance(record, dict) for name, record in declarations.items()):
        raise ValueError('Déclaration de module inconnue ou mal formée.')
    cells, states, modules = snapshot['cells'], {}, {}
    needs = {scope: {} for scope in SCOPES}
    calc = calculation or {}

    def value(sheet, address):
        cell = cells.get(sheet + '!' + address, {})
        return cell.get('value') if cell.get('formula') is None else None

    def reason(scope, code, message, key=None, provisional=False):
        token = code + ':' + (key or message)
        needs[scope][token] = {'code': code, 'field': key, 'message': message, 'provisional': provisional}

    def require(scope, sheet, address, *, choices=None, allow_default=False):
        key = sheet + '!' + address
        cell = cells.get(key, {})
        if cell.get('semantic_status') == 'REEXAMEN_REQUIS':
            reason(scope, 'SEMANTIQUE_NON_ETABLIE',
                   'Unité, assiette ou propriétaire à réexaminer : ' + key + ' — ' + ', '.join(cell.get('semantic_issues', [])), key)
        if key not in states:
            states[key] = classify_cell(cell, field_states.get(key), verified, date1904=snapshot.get('date1904', False))
        state = states[key]
        if allow_default and state['state'] == 'DEFAUT_CALCULE_MODELE':
            owners = snapshot.get('default_owners', {}).get(key)
            if owners:
                for owner in owners:
                    owner_sheet, owner_cell = owner.rsplit('!', 1)
                    require(scope, owner_sheet, owner_cell)
                return
        if not state['confirmed']:
            reason(scope, state['state'], 'Information ou source à qualifier : ' + key, key, state['scenario_ready'])
        current = cell.get('value')
        choices = choices if choices is not None else cell.get('choices')
        if choices is not None and current not in choices:
            reason(scope, 'CHOIX_NON_QUALIFIE', 'Choix explicite requis : ' + ', '.join(map(str, choices)), key)
        if cell.get('kind') in ('number', 'integer', 'percent') and not _blank(current):
            valid = _number(current)
            valid = valid and (cell['kind'] != 'integer' or int(current) == current)
            valid = valid and all(current >= cell[k] for k in ('min',) if k in cell)
            valid = valid and all(current <= cell[k] for k in ('max',) if k in cell)
            valid = valid and all(current > cell[k] for k in ('min_exclusive',) if k in cell)
            valid = valid and all(current < cell[k] for k in ('max_exclusive',) if k in cell)
            if not valid:
                reason(scope, 'VALEUR_HORS_DOMAINE', 'La valeur ne respecte pas le domaine du modèle.', key)

    def declaration(scope, name, *, inactive_allowed=False, has_activity=False):
        record = declarations.get(name)
        if not isinstance(record, dict) or record.get('state') not in ('ACTIF', 'INACTIF'):
            reason(scope, 'MODULE_NON_DECLARE', 'Déclarer explicitement le périmètre ' + name, 'module:' + name)
            modules[name] = 'NON_RENSEIGNE'
            return None
        state = record['state']
        modules[name] = state
        valid_source = isinstance(record.get('evidence'), str) and record['evidence'] in verified
        confirmed = record.get('status') == 'CONFIRME' and valid_source
        if not confirmed:
            provisional = record.get('status') == 'HYPOTHESE' and valid_source
            reason(scope, 'DECLARATION_A_QUALIFIER', 'Décision de module sourcée à confirmer.', 'module:' + name, provisional)
        if state == 'INACTIF' and (not inactive_allowed or has_activity):
            reason(scope, 'INACTIVITE_CONTRADICTOIRE', 'La déclaration ne neutralise pas les données ou formules de ' + name, 'module:' + name)
        return record

    years = value('Control', 'C59')
    start = _as_date(value('Control', 'C10'), snapshot.get('date1904', False))
    valid_years = _number(years) and int(years) == years and 1 <= years <= 10
    for scope in SCOPES:
        require(scope, 'Control', 'C10')
        require(scope, 'Control', 'C59')
        if not valid_years or start is None or (start.month, start.day) != (1, 1):
            reason(scope, 'CALENDRIER_NON_QUALIFIE', 'Départ au 1er janvier et durée entière de 1 à 10 exercices requis.')
    scenario = value('Sensi TCA', 'C15')
    for scope in SCOPES:
        if scenario != 'Central' or 'Sensi TCA!C15' in field_states:
            require(scope, 'Sensi TCA', 'C15')
    shock_scopes = {8: 'CA', 9: 'CA', 10: 'COGS', 11: 'CASH', 12: 'CASH', 13: 'CASH', 14: 'CASH', 15: 'CASH', 16: 'CASH'}
    for row, scope in shock_scopes.items():
        key = f'Sensi Analyses!F{row}'
        if value('Sensi Analyses', f'F{row}') != 0 or key in field_states:
            require(scope, 'Sensi Analyses', f'F{row}')
    if scenario == 'Manuel':
        for col, scope in zip('CDEFGHIJK', ('CA', 'CA', 'COGS', 'CASH', 'CASH', 'CASH', 'CASH', 'CASH', 'CASH')):
            require(scope, 'Sensi TCA', col + '77')
    count = int(years) if valid_years else 0
    year_columns = 'CDEFGHIJKL'[:count]
    offers = [row for row in range(15, 28) if value('Assumptions', 'C' + str(row)) == 1]
    registers = snapshot.get('registers', {})
    contract_rows = registers.get('DATA Contrats', {}).get('occupied_rows', [])
    if not offers and not contract_rows:
        empty_ca = declaration('CA', 'CA', inactive_allowed=True)
        if empty_ca and empty_ca['state'] == 'ACTIF':
            reason('CA', 'MODULE_ACTIF_SANS_DONNEES', 'Renseigner les offres ou contrats annoncés actifs.', 'module:CA')
    else:
        modules['CA'] = 'ACTIF'
        if declarations.get('CA', {}).get('state') == 'INACTIF':
            declaration('CA', 'CA', has_activity=True)
    for row in range(15, 28):
        flag = value('Assumptions', 'C' + str(row))
        if flag not in (0, 1) or isinstance(flag, bool):
            reason('CA', 'ACTIVATION_OFFRE_INCONNUE', 'Activation de l’offre à renseigner.', f'Assumptions!C{row}')
    for row in offers:
        for column in ('C', 'D', 'E', 'F', 'U', 'V', 'W', 'X', 'Y', 'Z'):
            require('CA', 'Assumptions', column + str(row))
        for column in ('K', 'L', 'M', 'N', 'O', 'AK', 'AL', 'AM', 'AN', 'AO')[:count]:
            require('CA', 'Assumptions', column + str(row))
        for column in ('P', 'Q', 'R', 'S', 'T', 'AP', 'AQ', 'AR', 'AS', 'AT')[:count]:
            require('CA', 'Assumptions', column + str(row))
        for column in ('F', 'G', 'H', 'I', 'J', 'AF', 'AG', 'AH', 'AI', 'AJ')[:count]:
            require('CA', 'Assumptions', column + str(row), allow_default=True)
        require('CA', 'Assumptions', 'D5')
        require('COGS', 'DATA COGS', 'D' + str(row), choices=('Manuel', 'Cible', 'Detaille'))
        method = value('DATA COGS', 'D' + str(row))
        if method == 'Manuel':
            require('COGS', 'DATA COGS', 'L' + str(row))
        elif method == 'Cible':
            for column in ('M', 'N', 'O', 'P', 'Q', 'X', 'Y', 'Z', 'AA', 'AB')[:count]:
                require('COGS', 'DATA COGS', column + str(row))
            for column in ('J', 'K'):
                require('COGS', 'DATA COGS', column + str(row))
        elif method == 'Detaille':
            for column in ('E', 'F', 'G', 'H', 'J', 'K'):
                require('COGS', 'DATA COGS', column + str(row))
        require('COGS', 'Assumptions', 'D7')
    if not offers:
        empty_cogs = declaration('COGS', 'COGS', inactive_allowed=not contract_rows, has_activity=bool(contract_rows))
        if empty_cogs and empty_cogs['state'] == 'ACTIF' and not contract_rows:
            reason('COGS', 'MODULE_ACTIF_SANS_DONNEES', 'Renseigner les coûts annoncés actifs.', 'module:COGS')

    for sheet, scopes in _REGISTER_SCOPES.items():
        rows = registers.get(sheet, {}).get('occupied_rows', [])
        modules[sheet] = 'ACTIF' if rows else 'NON_RENSEIGNE'
        for scope in scopes:
            if not rows:
                empty_register = declaration(scope, sheet, inactive_allowed=True)
                if empty_register and empty_register['state'] == 'ACTIF':
                    reason(scope, 'MODULE_ACTIF_SANS_DONNEES', 'Renseigner au moins une ligne du registre actif.', 'module:' + sheet)
            elif declarations.get(sheet, {}).get('state') == 'INACTIF':
                declaration(scope, sheet, has_activity=True)
            for row in rows:
                for col in registers[sheet].get('required_columns', []):
                    require(scope, sheet, col + str(row), allow_default=True)
                if sheet == 'DATA Contrats' and _norm(value(sheet, 'R' + str(row))) not in ('signe',):
                    require(scope, sheet, 'S' + str(row))
                if sheet == 'DATA CAPEX':
                    for col in ('F', 'H', 'M'):
                        require(scope, sheet, col + str(row), allow_default=True)
                    if value(sheet, 'I' + str(row)) == 'Crédit-bail':
                        for col in ('J', 'K', 'N', 'O'):
                            require(scope, sheet, col + str(row))
    for address in ('D4', 'D126'):
        require('CASH', 'Assumptions', address)
    for address in ('C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34'):
        require('CASH', 'Control', address)
    for row in range(32, 45):
        for column in ('E', 'F', 'G', 'H', 'K', 'L'):
            require('CASH', 'Charges_Externes', column + str(row))
        if _number(value('Charges_Externes', 'H' + str(row))) and value('Charges_Externes', 'H' + str(row)) > 0:
            require('CASH', 'Charges_Externes', 'J' + str(row))
        if row in (36, 37, 44) and _number(value('Charges_Externes', 'E' + str(row))) and value('Charges_Externes', 'E' + str(row)) > 0:
            require('CASH', 'Charges_Externes', 'I' + str(row))
    stock_activity = any(_number(value('Stock', cell)) and value('Stock', cell) != 0 for cell in ('E10', 'E11'))
    stock_activity = stock_activity or (_number(value('Control', 'C31')) and value('Control', 'C31') != 0)
    stock = declaration('CASH', 'STOCK', inactive_allowed=not stock_activity, has_activity=stock_activity)
    if stock and stock['state'] == 'ACTIF':
        for cell in ('E10', 'E11'):
            require('CASH', 'Stock', cell)
    if registers.get('Effectifs', {}).get('occupied_rows'):
        require('CASH', 'Assumptions', 'D66')

    # La case "À confirmer" reste bloquante même quand elle porte un état
    # documentaire CONFIRME : elle n'exprime aucune décision fiscale.
    fiscal = declaration('FISCALITE', 'REGLES_FISCALES')
    if fiscal:
        valid_from = _as_date(fiscal.get('valid_from'))
        valid_to = _as_date(fiscal.get('valid_to'))
        period_ok = start is not None and valid_years and valid_from is not None and valid_to is not None
        period_ok = period_ok and valid_from <= start and valid_to >= date(start.year + count - 1, 12, 31)
        model_ok = fiscal.get('model_id') == snapshot.get('model_id') and fiscal.get('template_sha256') == snapshot.get('template_sha256') and bool(snapshot.get('template_sha256'))
        if not period_ok or not model_ok or not isinstance(fiscal.get('jurisdiction'), str) or not fiscal['jurisdiction'].strip():
            reason('FISCALITE', 'REGLES_FISCALES_NON_QUALIFIEES', 'Revue sourcée du modèle, de la juridiction et de tous les exercices actifs requise.', 'module:REGLES_FISCALES')
    for col in year_columns:
        require('FISCALITE', 'ATELIER_CIR_IS', col + '66', choices=('Oui', 'Non'))
        require('FISCALITE', 'ATELIER_CIR_IS', col + '85', choices=('Oui', 'Non'))
        for row in (89, 91, 110, 111):
            require('FISCALITE', 'ATELIER_CIR_IS', col + str(row))
    require('FISCALITE', 'ATELIER_CIR_IS', 'C93')
    for address in ('D77', 'D78', 'D79', 'D83', 'D84', 'D85', 'D86', 'D87', 'D88'):
        require('FISCALITE', 'Assumptions', address)
    rd_active = any(value('DATA CAPEX', 'G' + str(row)) == 'Oui' for row in registers.get('DATA CAPEX', {}).get('occupied_rows', []))
    rd_active = rd_active or any(_number(value('Effectifs', 'E' + str(row))) and value('Effectifs', 'E' + str(row)) > 0 for row in registers.get('Effectifs', {}).get('occupied_rows', []))
    rd_active = rd_active or any(key.startswith('CALCUL_CIR!') and item.get('formula') is None and item.get('kind') == 'number' and _number(item.get('value')) and item['value'] > 0 for key, item in cells.items())
    cir = declaration('FISCALITE', 'CIR', inactive_allowed=not rd_active, has_activity=rd_active)
    if rd_active or cir and cir['state'] == 'ACTIF':
        for row in range(68, 77):
            require('FISCALITE', 'Assumptions', 'D' + str(row))
        for col in year_columns:
            for row in (18, 19, 41, 42, 43):
                require('FISCALITE', 'CALCUL_CIR', col + str(row))
    for row in offers:
        for col in ('D', 'E'):
            require('FISCALITE', 'ATELIER_CIR_IS', col + str(row + 128))
        require('FISCALITE', 'ATELIER_CIR_IS', 'F' + str(row + 128), choices=('Confirmé',))
    for row in contract_rows:
        for col in ('AL', 'AM'):
            require('FISCALITE', 'DATA Contrats', col + str(row))
    for row in range(160, 167):
        require('FISCALITE', 'ATELIER_CIR_IS', 'D' + str(row), choices=('Confirmé',) if row == 166 else None)

    for address in ('D8', 'D9', 'D107'):
        require('DCF', 'Valorisation', address)
    declaration('DCF', 'BFR_TERMINAL')
    closing_rows = snapshot.get('closing', {}).get('rows', [])
    if not closing_rows:
        reason('DCF', 'CLOSING_NON_QUALIFIE', 'Renseigner une date sourcée pour la catégorie de financement utilisée par le closing DCF.', 'module:DATA Financement')
    for row in closing_rows:
        require('DCF', 'DATA Financement', f'C{row}')
        require('DCF', 'DATA Financement', f'E{row}')
        closing_date = _as_date(value('DATA Financement', f'E{row}'), snapshot.get('date1904', False))
        if closing_date is None or start is None or not valid_years or not start <= closing_date <= date(start.year + count - 1, 12, 31):
            reason('DCF', 'CLOSING_HORS_HORIZON', 'Date de closing propriétaire dans les exercices actifs requise.', f'DATA Financement!E{row}')
    mode = value('Valorisation', 'D107')
    if mode == 'Manuel':
        require('DCF', 'Valorisation', 'D108')
        rate, growth = value('Valorisation', 'D108'), value('Valorisation', 'D8')
        if not _number(rate) or not _number(growth) or rate <= growth:
            reason('DCF', 'TAUX_TERMINAL_INVALIDE', 'Le taux documenté doit dépasser la croissance terminale ; aucune valeur n’est proposée.')
    elif mode in ('Structure cible', 'Itération'):
        for row in (111, 112, 113, 116, 117, 118, 119, 120, 121, 122, 123):
            require('DCF', 'Valorisation', 'D' + str(row))
        for row in (112, 113, 116):
            require('DCF', 'Valorisation', 'E' + str(row))
        for row in (117, 118, 119):
            premium = value('Valorisation', 'D' + str(row))
            if _number(premium) and premium > 0:
                require('DCF', 'Valorisation', 'E' + str(row))
        selected = [row for row in range(117, 137) if value('Comparables', 'C' + str(row)) == 'Oui']
        if not selected:
            reason('DCF', 'PANEL_NON_QUALIFIE', 'Sélection de comparables sourcés requise.')
        for row in selected:
            for col in ('B', 'C', 'D', 'E', 'F', 'G', 'J', 'K', 'L', 'M'):
                require('DCF', 'Comparables', col + str(row))
        if mode == 'Structure cible':
            require('DCF', 'Valorisation', 'D124')
        else:
            wacc = calc.get('wacc_proof', {})
            if not (isinstance(wacc, dict) and wacc.get('status') == 'VERIFIE' and wacc.get('workbook_sha256') == snapshot.get('source_sha256') and wacc.get('input_signature') == snapshot.get('input_signature')):
                reason('DCF', 'WACC_NON_VERIFIE', 'Preuve de convergence locale liée aux entrées et à cette copie requise.')
    else:
        reason('DCF', 'MODE_WACC_NON_QUALIFIE', 'Choisir explicitement Manuel, Structure cible ou Itération.')

    errors = calc.get('formula_errors', {})
    if errors.get('count', 0):
        attribution = errors.get('active_by_scope')
        if not isinstance(attribution, dict) or errors.get('attribution_complete') is not True:
            listed = errors.get('cells', [])
            attribution = dict.fromkeys(SCOPES, 0)
            if len(listed) == errors.get('count') and not errors.get('truncated'):
                for item in listed:
                    scope, active = error_perimeter(item.get('sheet', ''), item.get('cell', ''), count)
                    if active:
                        attribution[scope] += 1
            else:
                # Un ancien reçu tronqué ne permet pas d'attribuer ses erreurs.
                attribution = dict.fromkeys(SCOPES, 1)
        for scope in SCOPES:
            if attribution.get(scope, 0):
                reason(scope, 'ERREURS_FORMULES_NON_RESOLUES', 'Résoudre les erreurs actives du périmètre ' + scope + '.')

    fresh = (calc.get('status') == 'RECALCULE' and calc.get('model_verified') is True
             and calc.get('inputs_unchanged') is True and calc.get('model_id') == snapshot.get('model_id')
             and bool(snapshot.get('source_sha256')) and calc.get('output_sha256') == snapshot['source_sha256']
             and bool(snapshot.get('input_signature')) and calc.get('input_signature') == snapshot['input_signature'])
    if fresh and snapshot.get('diagnostics', {}).get('BFR!E49') != 'OK':
        reason('DCF', 'BFR_TERMINAL_NON_VALIDE', 'Le diagnostic courant BFR E49 doit valider la normalisation terminale ; la déclaration seule ne suffit pas.', 'BFR!E49')
    scopes = {}
    for scope in ('CA', 'COGS', 'FISCALITE', 'CASH', 'DCF'):
        reasons = list(needs[scope].values())
        for upstream in DEPENDENCIES[scope]:
            if not scopes[upstream]['qualification_ready']:
                reasons.append({'code': 'PERIMETRE_AMONT_NON_QUALIFIE', 'field': None,
                                'message': upstream + ' doit être qualifié.', 'scope': upstream,
                                'provisional': scopes[upstream]['scenario_ready']})
        blocked = [r for r in reasons if not r['provisional']]
        hypotheses = [r for r in reasons if r['provisional']]
        ready = not reasons
        scopes[scope] = {'qualification_ready': ready, 'scenario_ready': not blocked,
                         'available': ready and fresh, 'calculation_fresh': fresh,
                         'status': 'DISPONIBLE_SUR_PREREQUIS_QUALIFIES' if ready and fresh else
                                   'A_RECALCULER' if ready else 'HYPOTHESES_A_CONFIRMER' if not blocked else 'INDISPONIBLE',
                         'blockers': blocked, 'hypotheses': hypotheses, 'dependencies': list(DEPENDENCIES[scope]),
                         'economic_oracles_verified': False}
    questions = {}
    for scope, outcome in scopes.items():
        for item in outcome['blockers'] + outcome['hypotheses']:
            spec = cells.get(item['field'], {})
            key = spec.get('field_id') or item['field'] or item['code']
            message = 'Qualifier avec une source : ' + spec['label'] if spec.get('label') else item['message']
            q = questions.setdefault(key, {'field': item['field'], 'field_id': spec.get('field_id'),
                'fields': [], 'question': message, 'codes': [], 'scopes': []})
            if item['field'] and item['field'] not in q['fields']:
                q['fields'].append(item['field'])
            if item['code'] not in q['codes']:
                q['codes'].append(item['code'])
            if scope not in q['scopes']:
                q['scopes'].append(scope)
    return {'schema': 'tca-bp-qualifications/1', 'model_id': snapshot.get('model_id'),
            'source_sha256': snapshot.get('source_sha256'), 'input_signature': snapshot.get('input_signature'),
            'template_sha256': snapshot.get('template_sha256'), 'scopes': scopes, 'cells': states, 'modules': modules,
            'questions': list(questions.values()), 'status': 'EVALUE',
            'policy': 'Aucune hypothèse fiscale héritée, aucun diagnostic calculé ni cache ne confirme une source manquante.',
            'limitations': ['Ces gardes ne remplacent pas la revue des lois applicables ou les oracles financiers indépendants.',
                            'Une déclaration INACTIF ne modifie jamais les formules Excel.',
                            'L’appelant contrôle avant évaluation les sources du dossier, leurs empreintes et le modèle.']}


def require_available(assessment: dict, scope: str) -> dict:
    """Garde à appeler avant d'exposer une NOUVELLE valeur financière à l'utilisateur."""
    if assessment.get('schema') != 'tca-bp-qualifications/1' or scope not in SCOPES:
        raise ValueError('Périmètre ou qualification inconnu.')
    result = assessment.get('scopes', {}).get(scope, {})
    if result.get('available') is not True:
        raise ValueError('Résultat indisponible pour ' + scope + ' : ' + str(result.get('status', 'NON_QUALIFIE')))
    return deepcopy(result)
