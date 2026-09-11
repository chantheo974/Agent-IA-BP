"""Publication centrale des calculs WACC et des tables vérifiées.

Les travailleurs natifs ne déplacent jamais le pointeur d'un dossier. Cette
couche conserve l'ancienne version jusqu'à validation des copies et des sources.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from .calculation_proofs import validate as validate_proof
from .model_registry import model_pin
from .storage import atomic_json, canonical, confined, digest, now, uid


def _preflight(assessment, operation):
    """Une hypothèse sourcée peut être calculée, sans devenir confirmée.

L'absence du résultat WACC est normale avant sa résolution. Ses erreurs de
calcul sont contrôlées à nouveau par Excel avant publication. Les informations
amont et leurs sources restent obligatoires.
"""
    scopes = assessment.get('scopes', {}) if isinstance(assessment, dict) else {}
    required_scopes = ('CA', 'COGS', 'FISCALITE', 'CASH') + (('DCF',) if operation == 'wacc' else ())
    if not isinstance(assessment, dict) or assessment.get('status') != 'EVALUE' or not isinstance(scopes, dict) or any(name not in scopes for name in required_scopes):
        raise ValueError('Évaluer et compléter les qualifications du dossier avant ce calcul.')
    permitted = {'WACC_NON_VERIFIE', 'ERREURS_FORMULES_NON_RESOLUES'} if operation == 'wacc' else set()
    missing = []
    for name in required_scopes:
        scope = scopes[name]
        if (not isinstance(scope, dict) or not isinstance(scope.get('blockers'), list)
                or not isinstance(scope.get('hypotheses'), list)
                or not isinstance(scope.get('scenario_ready'), bool)
                or not scope['scenario_ready'] and not scope['blockers']):
            raise ValueError('Évaluation de qualification incomplète ou incohérente : ' + name)
        for item in scope.get('blockers', []):
            if not isinstance(item, dict) or not item.get('code'):
                raise ValueError('Motif de qualification incomplet : ' + name)
            if name == 'DCF' and item.get('code') in permitted:
                continue
            missing.append(item.get('message', item.get('code', name)))
    if missing:
        raise ValueError('Calcul indisponible : ' + ' ; '.join(dict.fromkeys(missing[:8])))


def _unchanged(app, row, basis):
    current = app._row(row['id'])
    keys = ('client_id', 'model_id', 'model_ref', 'template_sha256', 'schema_sha256',
            'revision', 'workbook', 'sha256', 'field_states', 'calculation_status')
    if any(current.get(key) != row.get(key) for key in keys):
        raise ValueError('Le dossier, ses entrées ou sa version de modèle ont changé ; copie non adoptée.')
    app._verify_case_model(current)
    if app._qualification_basis(current)['fingerprint'] != basis['fingerprint']:
        raise ValueError('Les sources ou les qualifications ont changé ; copie non adoptée.')


def _native_result(result, receipt_path, output, source_sha, expected):
    if (not isinstance(result, dict) or result.get('status') != expected
            or result.get('source_sha256') != source_sha or not output.is_file()
            or result.get('output_sha256') != digest(output) or result.get('adopted') is not False):
        raise ValueError('Le reçu natif ne prouve pas la copie attendue.')
    try:
        receipt_sha = digest(receipt_path)
        disk = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
        if not isinstance(disk, dict) or canonical(disk) != canonical(result) or digest(receipt_path) != receipt_sha:
            raise ValueError('Le reçu natif enregistré diffère du résultat retourné.')
    except (OSError, TypeError, json.JSONDecodeError) as error:
        raise ValueError('Reçu natif absent, illisible ou incomplet.') from error
    if (result.get('macros_enabled') is not False or result.get('iteration_enabled') is not False
            or result.get('source_preserved') is not True or result.get('save_reopen_verified') is not True
            or result.get('calculation_state') != 0 or isinstance(result.get('calculation_state'), bool)):
        raise ValueError('Les contrôles natifs de sauvegarde et de sécurité sont incomplets.')
    if expected == 'TABLES_VERIFIEES' and result.get('passed') is not True:
        raise ValueError('Les tables ne disposent pas de comparaisons validées.')
    return receipt_sha


def execute(app, case_id, operation, timeout):
    if operation not in ('wacc', 'sensitivity'):
        raise ValueError('Opération de calcul inconnue.')
    maximum = 600 if operation == 'wacc' else 3600
    if isinstance(timeout, bool) or not isinstance(timeout, (float, int)) or not math.isfinite(timeout) or not 1 <= timeout <= maximum:
        raise ValueError(f'Le délai doit être compris entre 1 et {maximum} secondes.')
    with app.store.case_lock(case_id):
        row = app._row(case_id)
        engine = app._engine_for_case(row)
        source = app._workbook(row)
        assessment = app._evaluate_qualifications_locked(row, engine, source)
        _preflight(assessment, operation)
        basis = app._qualification_basis(row)
        if assessment.get('basis_sha256') != basis['fingerprint']:
            raise ValueError('Les sources ou les qualifications ont changé depuis leur évaluation ; aucun calcul lancé.')
        old_wacc = app._specific_calculation_proofs(row)['wacc'] if operation == 'sensitivity' else None
        before = engine.context(source)
        if not before.get('input_signature'):
            raise ValueError('Empreinte des entrées absente ; aucun calcul lancé.')
        revision = row['revision'] + 1
        identifier = uid(operation + '_')
        folder = app.store.case_dir(case_id)
        tx = folder / 'transactions' / identifier
        tx.mkdir()
        relative = f'versions/v{revision:04d}_{identifier}.xlsm'
        output = confined(folder, relative)
        receipt_path = output.with_suffix('.native.json')
        report_path = output.with_suffix('.verification.json')
        transaction = {**model_pin(row), 'case_id': case_id, 'client_id': row['client_id'],
                       'operation': operation, 'source_sha256': row['sha256'], 'revision_before': row['revision'],
                       'status': 'EN_COURS', 'started_at': now(), 'output': relative}
        atomic_json(tx / 'transaction.json', transaction)
        committed = False
        try:
            if operation == 'wacc':
                from .wacc_native import solve_native
                result = solve_native(source, output, receipt_path, timeout=timeout)
                required_status = 'CONVERGENCE_LOCALE'
            else:
                from .sensitivity_native import verify_native
                result = verify_native(engine, source, output, receipt_path, timeout=timeout)
                required_status = 'TABLES_VERIFIEES'
            receipt_sha = _native_result(result, receipt_path, output, row['sha256'], required_status)
            output_sha = result['output_sha256']
            _unchanged(app, row, basis)
            after = engine.context(output)
            if after.get('input_signature') != before['input_signature']:
                raise ValueError('Le calcul a changé les entrées ; copie non adoptée.')
            if digest(source) != row['sha256']:
                raise ValueError('La source ou les qualifications ont changé pendant le calcul ; copie non adoptée.')
            native_proof = {'status': 'VERIFIE', 'workbook_sha256': output_sha,
                            'input_signature': after['input_signature'], 'receipt_path': str(receipt_path),
                            'receipt_sha256': receipt_sha, **model_pin(row)}
            if validate_proof(native_proof, operation, folder, row) is None:
                raise ValueError('Le reçu ne prouve pas ce calcul et ses entrées ; copie non adoptée.')
            proof = {**result, **model_pin(row), 'status': 'RECALCULE', 'native_operation_status': required_status,
                     'case_id': case_id, 'client_id': row['client_id'], 'revision': revision,
                     'transaction_id': identifier, 'operation': operation, 'workbook_path': str(output),
                     'input_signature': after['input_signature'], 'inputs_unchanged': True, 'model_verified': True,
                     'completeness': after.get('completeness', {}), 'formula_errors': after.get('formula_errors', {}),
                     'adopted': False, 'qualification_basis_before': basis['fingerprint']}
            proof['wacc_proof' if operation == 'wacc' else 'sensitivity_proof'] = native_proof
            # La vérification des tables atteste aussi la conservation exacte des
            # cinq sorties du solveur. Reporter sa preuve sur cette nouvelle copie
            # exige une preuve WACC déjà courante, pas un simple cache historique.
            if operation == 'sensitivity':
                if app._specific_calculation_proofs(app._row(case_id))['wacc'] != old_wacc:
                    raise ValueError('La preuve WACC a changé pendant les sensibilités ; copie non adoptée.')
                if old_wacc is not None:
                    if old_wacc.get('input_signature') != before['input_signature']:
                        raise ValueError('La preuve WACC ne correspond pas aux entrées de départ.')
                    proof['wacc_proof'] = {'status': 'VERIFIE', 'workbook_sha256': output_sha,
                        'input_signature': after['input_signature'], **model_pin(row),
                        'inherited_wacc_proof': old_wacc, 'preserved_by_sensitivity_receipt': native_proof}
                    if validate_proof(proof['wacc_proof'], 'wacc', folder, row) is None:
                        raise ValueError('La chaîne de conservation du WACC ne peut plus être validée ; résoudre de nouveau le WACC avant cette conservation.')
            atomic_json(report_path, proof)
            _unchanged(app, row, basis)
            if digest(output) != output_sha or digest(receipt_path) != receipt_sha or digest(source) != row['sha256']:
                raise ValueError('Les fichiers du calcul ont changé avant publication ; copie non adoptée.')
            with app.store.connection() as db:
                changed = db.execute("UPDATE cases SET revision=?,workbook=?,sha256=?,calculation_status='RECALCULE',updated_at=? WHERE id=? AND sha256=? AND model_ref=? AND revision=? AND model_id=? AND template_sha256=? AND schema_sha256=? AND client_id=? AND field_states=? AND calculation_status=?",
                                     (revision, relative, output_sha, now(), case_id, row['sha256'], row['model_ref'], row['revision'], row['model_id'], row['template_sha256'], row['schema_sha256'], row['client_id'], row['field_states'], row['calculation_status']))
                if changed.rowcount != 1:
                    raise ValueError('Le dossier a changé pendant la publication ; copie non adoptée.')
                app.store.history(db, case_id, 'RECALCUL_EXCEL', {**proof, 'adopted': True})
                app.store.history(db, case_id, 'WACC_RESOLU' if operation == 'wacc' else 'SENSIBILITES_VERIFIEES', {**proof, 'adopted': True})
            committed = True
            proof['adopted'] = True
            try:
                atomic_json(report_path, proof)
            except OSError as error:
                proof['report_notice'] = 'Version enregistrée ; miroir du reçu à reprendre : ' + str(error)
                with app.store.connection() as db:
                    app.store.history(db, case_id, 'RECU_RECALCUL_MIROIR_INCOMPLET', {
                        'revision': revision, 'transaction_id': identifier, 'operation': operation,
                        'report_path': str(report_path), 'reason': str(error)})
            atomic_json(tx / 'transaction.json', {**transaction, 'status': 'TERMINE', 'output_sha256': output_sha, 'revision': revision})
            try:
                qualified = app._evaluate_qualifications_locked(app._row(case_id), engine, output)
            except (ValueError, OSError) as error:
                from .qualifications import unavailable
                qualified = unavailable('Calcul enregistré ; qualification à reprendre : ' + str(error))
                with app.store.connection() as db:
                    app.store.history(db, case_id, 'QUALIFICATION_ECHOUEE_APRES_RECALCUL', {'revision': revision, 'reason': str(error)})
            app._save_state(case_id)
            return {**proof, 'status': required_status, 'workbook_path': str(output), 'report_path': str(report_path),
                    'qualified_availability': qualified['scopes'], 'qualification_status': qualified['status']}
        except Exception as error:
            atomic_json(tx / 'transaction.json', {**transaction, 'status': 'COMMIT_CONFIRME_MIROIR_INCOMPLET' if committed else 'ECHEC_A_INSPECTER',
                                                 'adopted': committed, 'reason': str(error),
                                                 'created_artifacts': [str(p.relative_to(folder)) for p in (output, receipt_path, report_path) if p.exists()]})
            raise
