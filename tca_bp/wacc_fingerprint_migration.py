"""Explicit, bounded migration of WACC freshness serialization, never finance.

The audited legacy protocol fingerprints 263 owners through four existing
helpers. An error in any owner used to erase the entire fingerprint. Version 2
encodes that owner's Excel ERROR.TYPE instead, preserving all other owners.
Only five technical formulas may change. No source or dossier is adopted here.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import re
from types import SimpleNamespace

from .storage import atomic_json, canonical, digest
from .vendor import input_engine as core
from .web_model_profile import initial_profile, map_location, seal_profile, verify_profile

MIGRATION_ID = 'wacc-fingerprint/error-types-v2'
FORMULA_LIMIT = 8000  # margin below Excel's 8192-character limit
HELPERS = ('J155', 'J156', 'J157', 'J158')
PREFIX = 'WACC-FP2:'
REASON = ('Migration technique de fraîcheur WACC : sérialiser chaque erreur Excel '
          'par son type et conserver les 263 propriétaires, sans modifier les flux financiers.')
SEPARATOR = '&"|"&'
SAFE_SEPARATOR = '&CHAR(124)&'
REFERENCE = r"(?:(?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z_0-9 ]*)!)?\$?[A-Z]{1,3}\$?[1-9]\d{0,6}"


def logical_owners():
    owners = [('Valorisation', f'D{row}') for row in [*range(111, 125), 126, 127]]
    owners += [('Valorisation', cell) for cell in ('D15', 'D8', 'D35')]
    owners += [('Valorisation', f'{column}{row}') for row in (19, 26, 31) for column in 'DEFGHIJKLM']
    owners += [('Control', cell) for cell in ('C10', 'C11', 'C59', 'C60')]
    owners += [('BFR', cell) for cell in ('E46', 'E48')]
    owners += [('Valorisation', f'E{row}') for row in (112, 113, 116, 117, 118, 119, 125)]
    owners += [('Comparables', f'{column}{row}') for row in range(117, 137) for column in 'BCDEFGJKLM']
    owners += [('BFR', 'E50')]
    return owners


def _hash(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _reference(sheet, cell, current_sheet):
    if sheet == current_sheet:
        return cell
    prefix = sheet if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', sheet) else "'" + sheet.replace("'", "''") + "'"
    return prefix + '!' + cell


def _owner(reference, sheet):
    if not re.fullmatch(REFERENCE, reference):
        raise ValueError('Référence non scalaire ou non reconnue dans l’empreinte WACC.')
    if '!' in reference:
        sheet, reference = reference.rsplit('!', 1)
        if sheet.startswith("'"):
            sheet = sheet[1:-1].replace("''", "'")
    return sheet, reference.replace('$', '')


def legacy_element(reference):
    return f'TYPE({reference})&":"&LEN({reference})&":"&{reference}'


def error_typed_element(reference):
    # TYPE(error)=16. Only this text fingerprint receives "E:<type>";
    # the originating Excel cell and its financial error remain unchanged.
    return f'TYPE({reference})&":"&IFERROR(LEN({reference})&":"&{reference},"E:"&ERROR.TYPE({reference}))'


def _parse_helpers(formulas):
    references, versions = [], set()
    for formula in formulas:
        if formula == '""':
            continue
        if not isinstance(formula, str) or len(formula) > 8192:
            raise ValueError('Helper WACC absent ou hors limite Excel.')
        separator = SAFE_SEPARATOR if SAFE_SEPARATOR in formula else SEPARATOR
        for token in formula.split(separator):
            match = re.match(r'TYPE\((' + REFERENCE + r')\)', token)
            if not match:
                raise ValueError('Helper WACC personnalisé : migration automatique refusée.')
            ref = match[1]
            if token == legacy_element(ref):
                versions.add(1)
            elif token == error_typed_element(ref):
                versions.add(2)
            else:
                raise ValueError('Helper WACC personnalisé : migration automatique refusée.')
            references.append(ref)
    if len(versions) != 1:
        raise ValueError('Helpers WACC mélangés, vides ou partiellement migrés.')
    return references, versions.pop()


def _chunks(references):
    chunks = ['']
    for reference in references:
        token = error_typed_element(reference)
        addition = (SAFE_SEPARATOR if chunks[-1] else '') + token
        if len(chunks[-1]) + len(addition) > FORMULA_LIMIT:
            chunks.append(token)
        else:
            chunks[-1] += addition
    if len(chunks) > len(HELPERS):
        raise ValueError('Les quatre helpers existants ne suffisent pas : évolution structurelle explicite requise.')
    return chunks + ['""'] * (len(HELPERS) - len(chunks))


def _aggregate(validity, helpers, *, version):
    joined = (SAFE_SEPARATOR if version == 2 else SEPARATOR).join(helpers)
    if version == 2:
        joined = '"' + PREFIX + '"&' + joined
    return f'IF({validity}="OK",{joined},"")'


def plan_fingerprint_migration(engine, workbook, evidence_id):
    """Read a pinned workbook and return an explicit five-formula proposal.

The source evidence ID must subsequently pass the dossier's usual ownership
checks. This standalone planner does not access SQLite or confer approval.
Renames/relocations use stable profile identities; deleted owners are refused.
"""
    if not isinstance(evidence_id, str) or not evidence_id.strip() or any(ord(c) < 32 for c in evidence_id):
        raise ValueError('Source documentaire explicite requise pour la migration.')
    workbook = Path(workbook).resolve()
    source_sha = digest(workbook)
    profile = initial_profile(engine, workbook)
    locations = {cell: map_location(profile, 'Valorisation', cell) for cell in ('D138', 'D155', 'D156', *HELPERS)}
    owners = [map_location(profile, sheet, cell) for sheet, cell in logical_owners()]
    if any(value is None for value in [*locations.values(), *owners]):
        raise ValueError('Un propriétaire de l’empreinte WACC a été supprimé.')
    sheet = locations['D155']['sheet']
    if any(value['sheet'] != sheet for value in locations.values()):
        raise ValueError('Les helpers WACC doivent rester sur une même feuille.')
    physical_helpers = [locations[cell]['cell'] for cell in HELPERS]
    checked = engine._open(workbook)
    try:
        old_helpers = [checked.formula(sheet, cell) for cell in physical_helpers]
        old_aggregate = checked.formula(sheet, locations['D155']['cell'])
        references, version = _parse_helpers(old_helpers)
        if [_owner(ref, sheet) for ref in references] != [(p['sheet'], p['cell']) for p in owners]:
            raise ValueError('Les 263 propriétaires et leur ordre ne correspondent plus au contrat audité.')
        expected = _aggregate(locations['D138']['cell'], physical_helpers, version=version)
        if old_aggregate is None or old_aggregate.replace('$', '') != expected:
            raise ValueError('La garde ou l’agrégateur WACC a changé : migration ciblée refusée.')
        # Never convert a macro's saved output into a formula as a side effect.
        if checked.formula(sheet, locations['D156']['cell']) is not None:
            raise ValueError('La sortie sauvegardée WACC possède une formule inattendue.')
    finally:
        checked.close()
    if digest(workbook) != source_sha:
        raise ValueError('La source a changé pendant la préparation de migration.')
    new_helpers = _chunks(references)
    new_aggregate = _aggregate(locations['D138']['cell'], physical_helpers, version=2)
    changes = []
    if version == 1:
        for logical, old, new in zip((*HELPERS, 'D155'), (*old_helpers, old_aggregate), (*new_helpers, new_aggregate)):
            if old != new:
                changes.append({'logical_sheet': 'Valorisation', 'logical_cell': logical,
                                'sheet': sheet, 'cell': locations[logical]['cell'],
                                'old_formula': old, 'new_formula': new})
    metadata = {'schema': 'tca-wacc-fingerprint-migration/1', 'migration_id': MIGRATION_ID,
                'source_model_id': engine.model_id, 'source_template_sha256': digest(engine.template_path),
                'source_workbook_sha256': source_sha, 'source_profile_sha256': profile['profile_sha256'],
                'reference_count': len(references), 'ordered_owners_sha256': _hash(logical_owners()),
                'physical_owners_sha256': _hash(owners), 'changes': changes,
                'helper_formula_lengths': [len(value) for value in (old_helpers if version == 2 else new_helpers)],
                'evidence_id': evidence_id,
                'status': 'ALREADY_MIGRATED' if version == 2 else 'PROPOSED',
                'error_policy': 'EXCEL_TYPE_16_AND_ERROR_TYPE_CODE; NO_FINANCIAL_ZERO',
                'financial_outputs_verified': False, 'native_proof_transfer': False, 'adopted': False}
    metadata['proposal_sha256'] = _hash(metadata)
    operations = [{'type': 'set_formula', 'sheet': change['sheet'], 'cell': change['cell'],
                   'formula': '=' + change['new_formula'], 'evidence_id': evidence_id, 'reason': REASON} for change in changes]
    return {**metadata, 'profile': profile, 'operations': operations}


def prepare_fingerprint_variant(engine, source, output, model_dir, evidence_id, *, runner=None, timeout=600):
    """Prepare and seal a private variant through the shared native engine.

The caller coordinates Excel access. No auto-adoption, publication, source
replacement, qualification transfer or native WACC convergence is performed.
"""
    from .web_structure import prepare_variant
    from .web_model import seal_profile_model
    source, output, model_dir = Path(source).resolve(), Path(output).resolve(), Path(model_dir).resolve()
    receipt_path = output.with_suffix('.wacc-migration.json')
    if model_dir.exists() or receipt_path.exists() or model_dir == output.parent:
        raise ValueError('Destinations neuves distinctes requises pour la variante et son reçu.')
    plan = plan_fingerprint_migration(engine, source, evidence_id)
    if plan['status'] == 'ALREADY_MIGRATED':
        return {key: value for key, value in plan.items() if key not in ('profile', 'operations')}
    prepared = prepare_variant(source, output, plan['profile'], plan['operations'], runner=runner, timeout=timeout)
    migration = {key: deepcopy(value) for key, value in plan.items() if key not in ('profile', 'operations')}
    if not prepared['blocked']:
        prepared['profile'] = certificate_fingerprint_change(plan['profile'], source, output, prepared['profile'], plan['operations'])
        atomic_json(output.with_suffix('.variant.json'), prepared)
        prepared['model_receipt'] = seal_profile_model(engine, output, prepared['profile'], model_dir)
        prepared['model_dir'] = str(model_dir)
    result = {**prepared, 'migration': migration}
    atomic_json(receipt_path, result)
    return result


def certificate_fingerprint_change(old_profile, old_path, new_path, new_profile, operations):
    """Certify only an exact five-formula technical migration after a preview.

Ordinary drafts return the unchanged profile. This adds no financial result or
native proof. All effective formula differences are compared, not just the
five claimed writes. Existing workbook/source/approval guards still apply.
"""
    verify_profile(old_profile); verify_profile(new_profile)
    if (not isinstance(operations, list) or len(operations) != 5
            or any(not isinstance(op, dict) or op.get('type') != 'set_formula' for op in operations)):
        return new_profile
    target_keys = {(p['sheet'], p['cell']) for cell in (*HELPERS, 'D155')
                   if (p := map_location(old_profile, 'Valorisation', cell))}
    if len(target_keys) != 5 or {(op.get('sheet'), op.get('cell')) for op in operations} != target_keys:
        return new_profile
    old_path, new_path = Path(old_path), Path(new_path)
    if (digest(old_path) != old_profile['current_workbook_sha256']
            or digest(new_path) != new_profile['current_workbook_sha256']
            or new_profile.get('parent_profile_sha256') != old_profile['profile_sha256']
            or old_profile['sheets'] != new_profile['sheets']):
        raise ValueError('La migration technique ne correspond pas aux deux révisions du profil.')
    # This adapter performs reads only. It does not masquerade as a financial
    # engine: all authorization and admission belong to the shared preview.
    reader = SimpleNamespace(profile=old_profile, template_path=old_path,
                             model_id=old_profile['origin_model_id'], _open=core.Workbook)
    try:
        plan = plan_fingerprint_migration(reader, old_path, operations[0].get('evidence_id'))
    except ValueError:
        return new_profile  # custom helpers remain ordinary unqualified edits
    expected = {(c['sheet'], c['cell']): c['new_formula'] for c in plan['changes']}
    if plan['status'] != 'PROPOSED' or len(expected) != 5:
        return new_profile
    for op in operations:
        if (not isinstance(op.get('formula'), str)
                or op['formula'].strip().removeprefix('=') != expected[(op['sheet'], op['cell'])]
                or not isinstance(op.get('evidence_id'), str) or not op['evidence_id'].strip()):
            return new_profile
    before, after = core.Workbook(old_path), core.Workbook(new_path)
    observed = {}
    try:
        if list(before.sheets) != list(after.sheets):
            raise ValueError('Une feuille a changé hors de la migration technique.')
        for sheet in before.sheets:
            a, b = before.sheet(sheet)[1], after.sheet(sheet)[1]
            for cell in set(a) | set(b):
                old, new = before.formula(sheet, cell), after.formula(sheet, cell)
                if old != new:
                    observed[sheet, cell] = (old, new)
            before._sheet_cache.pop(sheet, None); after._sheet_cache.pop(sheet, None)
        wanted = {(c['sheet'], c['cell']): (c['old_formula'], c['new_formula']) for c in plan['changes']}
        if observed != wanted:
            raise ValueError('Des formules diffèrent du lot technique exact de cinq helpers.')
    finally:
        before.close(); after.close()
    if digest(old_path) != old_profile['current_workbook_sha256'] or digest(new_path) != new_profile['current_workbook_sha256']:
        raise ValueError('Un classeur a changé pendant la certification technique.')
    certificate = {'schema': 'tca-wacc-fingerprint-certificate/1', 'migration_id': MIGRATION_ID,
        'source_profile_sha256': old_profile['profile_sha256'], 'prepared_profile_sha256': new_profile['profile_sha256'],
        'source_workbook_sha256': old_profile['current_workbook_sha256'], 'output_workbook_sha256': new_profile['current_workbook_sha256'],
        'ordered_owners_sha256': _hash(logical_owners()), 'reference_count': 263,
        'source_ids': list(dict.fromkeys(op['evidence_id'] for op in operations)),
        'changes': [{**c, 'old_formula_sha256': hashlib.sha256(c['old_formula'].encode()).hexdigest(),
                     'new_formula_sha256': hashlib.sha256(c['new_formula'].encode()).hexdigest()} for c in plan['changes']],
        'qualification_exemptions': ['Valorisation!' + c for c in (*HELPERS, 'D155')],
        'qualification_scope': 'TECHNICAL_FRESHNESS_SERIALIZATION_ONLY',
        'financial_outputs_verified': False, 'native_proof_transfer': False}
    certificate['certificate_sha256'] = _hash(certificate)
    profile = deepcopy(new_profile)
    profile.setdefault('technical_migrations', []).append(certificate)
    return seal_profile(profile)


def verified_fingerprint_exemptions(profile, workbook):
    """Return five technical owners only when certificate AND live rules match.

Call with the already verified workbook in qualification_snapshot. The native
WACC receipt remains required independently. Merely adding metadata cannot
exempt a different formula or a changed DCF guard/financial calculation.
"""
    verify_profile(profile)
    exempt = {'Valorisation!' + cell for cell in (*HELPERS, 'D155')}
    certificates = profile.get('technical_migrations', [])
    valid = [c for c in certificates if isinstance(c, dict)
        and c.get('schema') == 'tca-wacc-fingerprint-certificate/1'
        and c.get('migration_id') == MIGRATION_ID
        and c.get('certificate_sha256') == _hash({k:v for k,v in c.items() if k != 'certificate_sha256'})
        and c.get('ordered_owners_sha256') == _hash(logical_owners())
        and c.get('reference_count') == 263
        and set(c.get('qualification_exemptions', [])) == exempt
        and len(c.get('changes', [])) == 5]
    if not valid:
        return set()
    locations = {cell: map_location(profile, 'Valorisation', cell) for cell in ('D138', 'D155', *HELPERS)}
    owners = [map_location(profile, sheet, cell) for sheet, cell in logical_owners()]
    if any(p is None for p in [*locations.values(), *owners]):
        return set()
    sheet = locations['D155']['sheet']
    if any(p['sheet'] != sheet for p in locations.values()):
        return set()
    try:
        formulas = [workbook.formula(sheet, locations[cell]['cell']) for cell in HELPERS]
        refs, version = _parse_helpers(formulas)
        if version != 2 or [_owner(ref,sheet) for ref in refs] != [(p['sheet'],p['cell']) for p in owners]:
            return set()
        aggregate = workbook.formula(sheet, locations['D155']['cell'])
        if aggregate is None or aggregate.replace('$','') != _aggregate(locations['D138']['cell'],[locations[c]['cell'] for c in HELPERS],version=2):
            return set()
    except (ValueError, KeyError):
        return set()
    return exempt
