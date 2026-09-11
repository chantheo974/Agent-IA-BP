"""Qualification fermée des trois tables natives par 24 copies scalaires.

Les copies instrumentales ne sont jamais adoptables par le service. Aucune
cellule ni procédure arbitraire n'est acceptée par cette opération.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import subprocess
import threading
import time
import zipfile
import uuid

from .native_excel import available
from .storage import atomic_json, canonical, digest
from .wacc_native import OwnedExcelProcess, existing_excel_pids

SHEET = 'Sensi Analyses'
DRIVERS = ('C8', 'C14', 'C18')
BASE_REFS = ('D24', 'E24', 'F24', 'G24', 'C39', 'D39', 'C49')
ALGORITHM = 'tca-native-tables-vs-isolated-scalars/1'
TOLERANCE = 0.01
MAX_NATIVE_SECONDS = 3600


def _implementation_sha():
    """Une reprise ne mélange pas deux versions de calcul ou de validation."""
    h = hashlib.sha256()
    for path in (Path(__file__), Path(__file__).with_name('sensitivity_worker.ps1')):
        h.update(path.read_bytes())
    return h.hexdigest()


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def scenarios():
    """Axes fixes de la trame ; aucun dictionnaire d'écriture externe."""
    result = []
    for index in range(1, 10):
        result.append({'id': f'tornado_{index}', 'table': 'tornado',
                       'drivers': dict(zip(DRIVERS, (0, 0, index))),
                       'targets': dict(zip((f'{col}{24+index}' for col in 'DEFG'), BASE_REFS[:4]))})
    for row, volume in enumerate((-.3, -.2, -.1, 0, .1, .2), 40):
        result.append({'id': f'volume_{row}', 'table': 'volume',
                       'drivers': dict(zip(DRIVERS, (volume, 0, 0))),
                       'targets': {f'C{row}': 'C39', f'D{row}': 'D39'}})
    for row, volume in enumerate((0, -.1, -.2), 50):
        for col, aid in zip('DEF', (0, -.5, -1)):
            result.append({'id': f'matrix_{col}{row}', 'table': 'volume_aides',
                           'drivers': dict(zip(DRIVERS, (volume, aid, 0))),
                           'targets': {f'{col}{row}': 'C49'}})
    return result


def _preconditions(wb):
    value = lambda cell: wb.value(SHEET, cell)
    for cell in DRIVERS:
        if wb.formula(SHEET, cell) is not None or not _finite(value(cell)) or value(cell) != 0:
            raise ValueError('Pilote technique de base non neutre : ' + cell)
    expected_axes = {**{f'C{24+i}': i for i in range(1, 10)},
                     **dict(zip((f'B{r}' for r in range(40, 46)), (-.3, -.2, -.1, 0, .1, .2))),
                     **dict(zip(('D49', 'E49', 'F49'), (0, -.5, -1))),
                     **dict(zip(('C50', 'C51', 'C52'), (0, -.1, -.2)))}
    for cell, expected in expected_axes.items():
        if wb.formula(SHEET, cell) is not None or not _finite(value(cell)) or value(cell) != expected:
            raise ValueError('Axe de table incompatible : ' + cell)
    shocks = {f'F{row}': value(f'F{row}') for row in range(8, 17)}
    if any(not _finite(v) or v == 0 for v in shocks.values()):
        raise ValueError('Les neuf chocs F8:F16 doivent être explicitement non nuls et numériques.')
    for anchor, attributes in {
        'D25': {'t': 'dataTable', 'ref': 'D25:G33', 'r1': 'C18'},
        'C40': {'t': 'dataTable', 'ref': 'C40:D45', 'r1': 'C8'},
        'D50': {'t': 'dataTable', 'ref': 'D50:F52', 'r1': 'C14', 'r2': 'C8', 'dt2D': '1', 'dtr': '1'},
    }.items():
        node = wb.sheet(SHEET)[1][anchor].find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
        if node is None or any(node.get(k) != v for k, v in attributes.items()):
            raise ValueError('Définition native de table incompatible : ' + anchor)
    return {'drivers': {c: value(c) for c in DRIVERS}, 'axes': expected_axes, 'shocks': shocks,
            'scenario': wb.value('Sensi TCA', 'C15'), 'horizon': wb.value('Control', 'C59'),
            'wacc_outputs': {cell: wb.value('Valorisation', cell) for cell in ('D136','D141','D142','D143','D156')}}


def _patch_literals(raw, drivers):
    """Remplace seulement trois contenus v ; les octets XML voisins restent exacts."""
    if set(drivers) != set(DRIVERS) or any(not _finite(v) for v in drivers.values()):
        raise ValueError('Périmètre instrumental limité aux trois pilotes techniques.')
    for address in DRIVERS:
        pattern = rb'(<(?:\w+:)?c\b[^>]*\br="' + address.encode() + rb'"[^>]*>)(.*?)(</(?:\w+:)?c>)'
        hits = list(re.finditer(pattern, raw, re.DOTALL))
        if len(hits) != 1:
            raise ValueError('Cellule instrumentale absente ou dupliquée : ' + address)
        hit = hits[0]
        if re.search(rb'<(?:\w+:)?f\b', hit[2]):
            raise ValueError('Une formule ne peut pas être instrumentée.')
        values = list(re.finditer(rb'(<(?:\w+:)?v>)(.*?)(</(?:\w+:)?v>)', hit[2], re.DOTALL))
        if len(values) != 1:
            raise ValueError('Littéral numérique requis : ' + address)
        node = values[0]
        encoded = format(drivers[address], '.17g').encode('ascii')
        body = hit[2][:node.start(2)] + encoded + hit[2][node.end(2):]
        raw = raw[:hit.start(2)] + body + raw[hit.end(2):]
    return raw


def _zip_hashes(path):
    with zipfile.ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('Parties ZIP dupliquées.')
        return {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}


def prepare_campaign(engine, source: Path, directory: Path):
    """Prépare des instruments neufs ; ne lance aucune application native."""
    source, directory = Path(source).resolve(), Path(directory).resolve()
    if directory.exists():
        raise ValueError('La préparation exige un répertoire neuf.')
    before = engine.context(source)
    wb = engine._open(source)
    try:
        initial = _preconditions(wb)
        part = wb.sheets[SHEET]['part']
    finally:
        wb.close()
    definitions = scenarios()
    source_sha = digest(source)
    if source_sha != before['source_sha256']:
        raise ValueError('Source modifiée pendant le précontrôle.')
    directory.mkdir(parents=True)
    with zipfile.ZipFile(source) as original:
        names = original.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Parties ZIP dupliquées.')
        payloads = {n: original.read(n) for n in names}
        original_hashes = {n: hashlib.sha256(data).hexdigest() for n, data in payloads.items()}
        for item in definitions:
            destination = directory / (item['id'] + '.xlsm')
            patched = _patch_literals(payloads[part], item['drivers'])
            # Réversibilité octet pour octet, y compris formules/protections/styles.
            if _patch_literals(patched, initial['drivers']) != payloads[part]:
                raise ValueError('Le delta instrumental déborde les trois littéraux autorisés.')
            with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as target:
                for info in original.infolist():
                    target.writestr(info, patched if info.filename == part else payloads[info.filename])
            actual = _zip_hashes(destination)
            changed = [name for name in names if actual[name] != original_hashes[name]]
            if set(actual) != set(original_hashes) or set(changed) - {part}:
                raise ValueError('Partie non autorisée modifiée dans une copie instrumentale.')
            item.update(path=str(destination), sha256=digest(destination), changed_parts=changed)
    if digest(source) != source_sha:
        raise ValueError('Source modifiée pendant la préparation.')
    plan = {'schema': 'tca-sensitivity-plan/1', 'algorithm': ALGORITHM,
            'source': str(source), 'source_sha256': source_sha, 'model_id': engine.model_id,
            'template_sha256': engine.ensure_built()['template_sha256'],
            'input_signature': before['input_signature'], 'initial': initial, 'scenarios': definitions,
            'scope': {'tables': 3, 'scalars': 24, 'comparisons': 57, 'technical_cells': list(DRIVERS)},
            'isolation': 'COPIES_DISTINCTES_NON_ADOPTABLES', 'native_executed': False,
            'prepared_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
    atomic_json(directory / 'plan.json', plan)
    return plan


def _verify_plan(engine, source, directory):
    directory = Path(directory).resolve()
    plan = json.loads((directory / 'plan.json').read_text(encoding='utf-8-sig'))
    if (plan.get('schema') != 'tca-sensitivity-plan/1' or plan.get('algorithm') != ALGORITHM
            or plan.get('source') != str(source) or plan.get('source_sha256') != digest(source)
            or plan.get('model_id') != engine.model_id
            or plan.get('template_sha256') != engine.ensure_built()['template_sha256']):
        raise ValueError('Préparation de sensibilité périmée ou incompatible.')
    expected = scenarios()
    if len(plan.get('scenarios', [])) != len(expected):
        raise ValueError('Campagne incomplète.')
    source_hashes = _zip_hashes(source)
    with zipfile.ZipFile(source) as z:
        wb = engine._open(source)
        try:
            initial = _preconditions(wb)
            part = wb.sheets[SHEET]['part']
            if initial != plan.get('initial') or wb.input_signature(engine.schema) != plan.get('input_signature'):
                raise ValueError('Entrées ou scénario modifiés depuis la préparation.')
        finally:
            wb.close()
        original_xml = z.read(part)
    for actual, wanted in zip(plan['scenarios'], expected):
        path = directory / (wanted['id'] + '.xlsm')
        if (any(actual.get(k) != v for k, v in wanted.items()) or actual.get('path') != str(path)
                or actual.get('sha256') != digest(path)):
            raise ValueError('Copie scalaire inconnue, altérée ou hors campagne.')
        hashes = _zip_hashes(path)
        if set(hashes) != set(source_hashes) or any(hashes[n] != h for n, h in source_hashes.items() if n != part):
            raise ValueError('Une copie scalaire a changé hors des pilotes autorisés.')
        with zipfile.ZipFile(path) as z:
            if z.read(part) != _patch_literals(original_xml, wanted['drivers']):
                raise ValueError('Une copie scalaire a changé hors des trois littéraux autorisés.')
    return plan


def _validate_base(native):
    if (native.get('macros_enabled') is not False or native.get('iteration_enabled') is not False
            or native.get('source_preserved') is not True or native.get('save_reopen_verified') is not True
            or native.get('calculation_state') != 0 or isinstance(native.get('calculation_state'), bool)
            or native.get('restoration') != 'ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE'
            or native.get('scalar_copies_saved') is not False or native.get('technical_writes_to_base') != []):
        raise ValueError('Les preuves natives de sécurité ou de persistance sont incomplètes.')
    tables = native.get('tables', {})
    persisted = native.get('persisted_tables', {})
    base, persisted_base = native.get('base_outputs', {}), native.get('persisted_base_outputs', {})
    targets = {cell for s in scenarios() for cell in s['targets']}
    if set(tables) != targets or set(persisted) != targets or set(base) != set(BASE_REFS) or set(persisted_base) != set(BASE_REFS):
        raise ValueError('Périmètre des tables ou de la base incomplet.')
    if any(not _finite(v) for data in (tables, persisted, base, persisted_base) for v in data.values()):
        raise ValueError('Valeur de table ou de base vide, textuelle, booléenne ou non finie.')
    if any(abs(tables[c]-persisted[c]) > TOLERANCE for c in targets) or any(abs(base[c]-persisted_base[c]) > TOLERANCE for c in BASE_REFS):
        raise ValueError('Les tables ou la base ne persistent pas après sauvegarde et réouverture.')
    return tables, base


def _validate_scalar(spec, observed):
    if (observed.get('sha256') != spec['sha256'] or observed.get('drivers') != spec['drivers']
            or any(not _finite(v) for v in observed.get('drivers', {}).values())
            or observed.get('calculation_state') != 0 or isinstance(observed.get('calculation_state'), bool)
            or observed.get('calculation_mode') != 'AUTO_NO_TABLE' or observed.get('copy_preserved') is not True):
        raise ValueError('Identité, entrées ou isolation scalaire non vérifiées.')
    values = observed.get('outputs', {})
    if set(values) != set(spec['targets'].values()) or any(not _finite(v) for v in values.values()):
        raise ValueError('Une sortie scalaire est absente, booléenne, erronée ou non finie.')
    return values


def compare_results(plan, native):
    """Comparer strictement les 57 nombres, puis exclure les tables dégénérées."""
    tables, base = _validate_base(native)
    observations = native.get('scalars', [])
    if len(observations) != 24 or [x.get('id') for x in observations] != [x['id'] for x in scenarios()]:
        raise ValueError('Les 24 scénarios scalaires ne sont pas tous présents exactement une fois.')
    comparisons, effects = [], {}
    for spec, observed in zip(plan['scenarios'], observations):
        values = _validate_scalar(spec, observed)
        effects[spec['id']] = any(abs(v-base[c]) > TOLERANCE for c, v in values.items())
        for target, ref in spec['targets'].items():
            delta = tables[target] - values[ref]
            comparisons.append({'scenario': spec['id'], 'table': spec['table'], 'cell': target,
                                'scalar_ref': ref, 'native': tables[target], 'scalar': values[ref],
                                'difference': delta, 'tolerance': TOLERANCE, 'passed': abs(delta) <= TOLERANCE})
    tornado_varies = any(effects[f'tornado_{i}'] for i in range(1, 10))
    volume_varies = any(max(tables[f'{col}{r}'] for r in range(40, 46)) - min(tables[f'{col}{r}'] for r in range(40, 46)) > TOLERANCE for col in 'CD')
    matrix_volume = any(max(tables[f'{c}{r}'] for r in range(50, 53)) - min(tables[f'{c}{r}'] for r in range(50, 53)) > TOLERANCE for c in 'DEF')
    matrix_aid = any(max(tables[f'{c}{r}'] for c in 'DEF') - min(tables[f'{c}{r}'] for c in 'DEF') > TOLERANCE for r in range(50, 53))
    diversity = {'tornado': tornado_varies, 'volume': volume_varies,
                 'matrix_volume_axis': matrix_volume, 'matrix_aid_axis': matrix_aid}
    passed = all(x['passed'] for x in comparisons) and all(diversity.values())
    return {'status': 'TABLES_VERIFIEES' if passed else 'ECHEC_COMPARAISON_OU_DEGENERESCENCE',
            'comparisons': comparisons, 'non_degeneracy': diversity, 'tornado_effects': effects,
            'passed': passed, 'financial_model_globally_validated': False}


def _load_checkpoints(folder, binding, plan, output):
    """Réutiliser seulement un préfixe contigu, scellé aux mêmes fichiers/code."""
    ledger = json.loads((folder/'ledger.json').read_text(encoding='utf-8-sig'))
    if ledger.get('binding') != binding or ledger.get('schema') != 'tca-sensitivity-checkpoints/1':
        raise ValueError('Points de contrôle périmés : source, plan ou implémentation différents.')
    records = ledger.get('records', [])
    expected = ['base'] + [item['id'] for item in plan['scenarios']]
    if not records or len(records) > 25 or [item.get('id') for item in records] != expected[:len(records)]:
        raise ValueError('Points de contrôle manquants, dupliqués ou désordonnés.')
    values = []
    for record in records:
        path = folder/(record['id']+'.json')
        if digest(path) != record.get('sha256'):
            raise ValueError('Un point de contrôle a été altéré.')
        item = json.loads(path.read_text(encoding='utf-8-sig'))
        if item.get('binding') != binding or item.get('id') != record['id']:
            raise ValueError('Point de contrôle d’une autre campagne.')
        values.append(item['data'])
    base = values[0]
    _validate_base(base)
    if (not output.is_file() or base.get('output_sha256') != digest(output)
            or base.get('source_sha256') != plan['source_sha256']):
        raise ValueError('La base persistée du point de reprise a changé ou manque.')
    for spec, observed in zip(plan['scenarios'], values[1:]):
        if observed.get('id') != spec['id']:
            raise ValueError('Scénario du point de contrôle incompatible.')
        _validate_scalar(spec, observed)
    return {'base': base, 'scalars': values[1:]}, ledger


def _record_checkpoint(folder, ledger, binding, plan, output, identifier, data):
    expected = ['base'] + [item['id'] for item in plan['scenarios']]
    position = len(ledger['records'])
    if position >= len(expected) or identifier != expected[position]:
        raise ValueError('Point de contrôle natif inattendu ou dupliqué.')
    if position == 0:
        _validate_base(data)
        if data.get('source_sha256') != plan['source_sha256'] or data.get('output_sha256') != digest(output):
            raise ValueError('Empreinte de base incohérente au point de contrôle.')
    else:
        if data.get('id') != identifier:
            raise ValueError('Identifiant du scénario incohérent.')
        _validate_scalar(plan['scenarios'][position-1], data)
    path = folder/(identifier+'.json')
    if path.exists():
        raise ValueError('Un point de contrôle existant ne peut pas être remplacé.')
    atomic_json(path, {'binding': binding, 'id': identifier, 'data': data})
    ledger['records'].append({'id': identifier, 'sha256': digest(path)})
    atomic_json(folder/'ledger.json', ledger)


def verify_native(engine, source: Path, output: Path, receipt: Path, *, timeout=MAX_NATIVE_SECONDS,
                  prepared: Path | None = None, progress=None, resume=False):
    """Une instance dédiée, ouvertures séquentielles ; le service décide l'adoption."""
    if not _finite(timeout) or not 1 <= timeout <= MAX_NATIVE_SECONDS:
        raise ValueError('Délai de sensibilité requis entre 1 et 3 600 secondes.')
    if not isinstance(resume, bool):
        raise ValueError('La reprise doit être explicitement booléenne.')
    source, output, receipt = (Path(p).resolve() for p in (source, output, receipt))
    if len({source, output, receipt}) != 3 or output.exists() != resume or receipt.exists() or output.suffix.lower() != '.xlsm':
        raise ValueError('Source, nouvelle copie XLSM et nouveau reçu doivent être distincts.')
    if not available():
        raise ValueError('Excel est requis pour vérifier les tables natives.')
    prepared = Path(prepared).resolve() if prepared else receipt.parent / (receipt.stem + '_instruments')
    if not prepared.exists():
        prepare_campaign(engine, source, prepared)
    plan = _verify_plan(engine, source, prepared)
    plan_sha = digest(prepared / 'plan.json')
    binding = {'source_sha256': plan['source_sha256'], 'plan_sha256': plan_sha,
               'implementation_sha256': _implementation_sha(), 'output_path': str(output),
               'model_id': plan['model_id'], 'template_sha256': plan['template_sha256']}
    checkpoint_dir = receipt.with_name(receipt.stem+'_checkpoints')
    if resume:
        resumed, ledger = _load_checkpoints(checkpoint_dir, binding, plan, output)
    else:
        if checkpoint_dir.exists():
            raise ValueError('Points de contrôle déjà présents : reprise explicite ou nouvelle campagne requise.')
        checkpoint_dir.mkdir(parents=True)
        resumed = {'base': None, 'scalars': []}
        ledger = {'schema': 'tca-sensitivity-checkpoints/1', 'binding': binding, 'records': []}
        atomic_json(checkpoint_dir/'ledger.json', ledger)
    attempt = uuid.uuid4().hex[:12]
    resume_request = checkpoint_dir/('request_'+attempt+'.json')
    atomic_json(resume_request, resumed)
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    native_path = receipt.with_name(receipt.stem + ('.native.'+attempt if resume else '.native') + '.json')
    if native_path.exists() or native_path in (source, output):
        raise ValueError('Le reçu natif doit être neuf et distinct.')
    windows = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0'
    environment = os.environ.copy()
    environment['PSModulePath'] = os.pathsep.join((str(windows / 'Modules'),
        str(Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'WindowsPowerShell/Modules')))
    args = [str(windows / 'powershell.exe'), '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
            '-File', str(Path(__file__).with_name('sensitivity_worker.ps1')), '-PlanPath', str(prepared / 'plan.json'),
            '-PlanSha256', plan_sha, '-OutputPath', str(output), '-ReceiptPath', str(native_path),
            '-ResumePath', str(resume_request), '-ResumeSha256', digest(resume_request)]
    previous = existing_excel_pids()
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding='utf-8', env=environment,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    messages = queue.Queue()
    def reader():
        try:
            for line in process.stdout:
                message = json.loads(line.lstrip('\ufeff'))
                messages.put(message if isinstance(message, dict) else {'event': 'error', 'error': 'Message natif invalide.'})
        except (ValueError, OSError) as exc:
            messages.put({'event': 'error', 'error': str(exc)})
        finally:
            messages.put({'event': 'closed'})
    def drain():
        for _ in process.stderr:
            pass
    threading.Thread(target=reader, daemon=True).start()
    threading.Thread(target=drain, daemon=True).start()
    started, owned, complete = time.monotonic(), None, False
    try:
        while True:
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError('Délai de vérification des sensibilités dépassé.')
            try:
                message = messages.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError('Délai de vérification des sensibilités dépassé.') from exc
            if time.monotonic() - started >= timeout:
                raise TimeoutError('Délai de vérification des sensibilités dépassé.')
            event = message.get('event')
            if event == 'owned_process':
                pid = message.get('pid')
                if owned is not None or not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 or pid in previous:
                    raise ValueError('Instance Excel préexistante ou non identifiable : aucune modification autorisée.')
                owned = OwnedExcelProcess(pid)
                process.stdin.write('{"operation":"ownership_confirmed"}\n'); process.stdin.flush()
            elif event == 'progress' and owned is not None:
                if progress:
                    progress(message)
            elif event == 'checkpoint' and owned is not None:
                _record_checkpoint(checkpoint_dir, ledger, binding, plan, output, message.get('id'), message.get('data', {}))
            elif event == 'saved' and owned is not None:
                break
            else:
                raise ValueError(message.get('error', 'Réponse native inattendue : ' + str(event)))
        process.stdin.close()
        process.wait(timeout=max(.01, timeout - (time.monotonic() - started)))
        if process.returncode != 0 or not output.is_file() or not native_path.is_file():
            raise ValueError('Campagne native non terminée.')
        native = json.loads(native_path.read_text(encoding='utf-8-sig'))
        completed, completed_ledger = _load_checkpoints(checkpoint_dir, binding, plan, output)
        if (len(completed_ledger['records']) != 25 or native.get('scalars') != completed['scalars']
                or native.get('tables') != completed['base'].get('tables')):
            raise ValueError('Le reçu final ne correspond pas aux 25 points de contrôle complets.')
        if (native.get('source_sha256') != plan['source_sha256'] or digest(source) != plan['source_sha256']
                or native.get('output_sha256') != digest(output)):
            raise ValueError('Empreintes natives incompatibles avec les fichiers.')
        # La source et chacun des instruments doivent rester strictement identiques.
        _verify_plan(engine, source, prepared)
        if digest(prepared / 'plan.json') != plan_sha:
            raise ValueError('Le plan de la campagne a changé pendant le calcul.')
        after = engine.context(output)
        if after['input_signature'] != plan['input_signature']:
            raise ValueError('Les entrées métier ont changé pendant la vérification.')
        wb = engine._open(output)
        try:
            if _preconditions(wb) != plan['initial']:
                raise ValueError('Les pilotes, chocs, axes, scénario ou horizon ont changé.')
            disk_tables = {cell: wb.value(SHEET, cell) for s in scenarios() for cell in s['targets']}
            disk_base = {cell: wb.value(SHEET, cell) for cell in BASE_REFS}
        finally:
            wb.close()
        if disk_tables != native.get('persisted_tables') or disk_base != native.get('persisted_base_outputs'):
            raise ValueError('Les caches enregistrés ne correspondent pas aux valeurs relues dans Excel.')
        comparison = compare_results(plan, native)
        result = {**native, **comparison, 'schema': 'tca-sensitivity-receipt/1', 'algorithm': ALGORITHM,
                  'model_id': engine.model_id, 'template_sha256': plan['template_sha256'],
                  'input_signature_before': plan['input_signature'], 'input_signature_after': after['input_signature'],
                  'scope': plan['scope'], 'initial': plan['initial'], 'plan_sha256': plan_sha,
                  'formula_and_protection_signatures_verified': True, 'adopted': False,
                  'formula_errors': after.get('formula_errors'), 'elapsed_seconds': time.monotonic()-started,
                  'resumed_scalars': len(resumed['scalars']), 'checkpoints_sha256': digest(checkpoint_dir/'ledger.json'),
                  'implementation_sha256': binding['implementation_sha256'], 'attempt_id': attempt,
                  'timeout_seconds': timeout}
        atomic_json(receipt, result)
        if not comparison['passed']:
            raise ValueError('Tables non qualifiées : écarts scalaires ou axes sans effet. Consulter le reçu.')
        complete = True
        return result
    except BaseException as exc:
        atomic_json(receipt.with_name(receipt.stem + ('.echec.'+attempt if resume else '.echec') + '.json'), {
            'schema': 'tca-sensitivity-failure/1', 'status': 'NON_ADOPTE', 'error': str(exc),
            'source_sha256': plan['source_sha256'], 'source_preserved': digest(source) == plan['source_sha256'],
            'output_exists': output.exists(), 'adopted': False,
            'completed_scalars': max(0, len(ledger['records'])-1), 'attempt_id': attempt,
            'resume_available': bool(ledger['records']), 'checkpoint_directory': str(checkpoint_dir),
            'restoration': 'ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE'})
        raise
    finally:
        try:
            if not complete and owned:
                owned.terminate()
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
        finally:
            if owned:
                owned.close()
