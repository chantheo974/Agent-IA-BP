"""Vérification des reçus persistants, y compris la conservation du WACC."""
from __future__ import annotations
import json
from .model_registry import model_pin
from .storage import confined, digest


def validate(proof, kind, folder, pin, *, depth=0):
    """Retourne le reçu natif reconnu, ou None ; aucune confiance dans un chemin seul."""
    if (kind not in ('wacc', 'sensitivity') or depth > 128 or not isinstance(proof, dict) or proof.get('status') != 'VERIFIE'
            or model_pin(proof) != model_pin(pin) or not proof.get('input_signature')
            or not proof.get('workbook_sha256')):
        return None
    if kind == 'wacc' and 'inherited_wacc_proof' in proof:
        inherited = proof['inherited_wacc_proof']
        preservation = proof.get('preserved_by_sensitivity_receipt')
        original = validate(inherited, 'wacc', folder, pin, depth=depth+1)
        preserved = validate(preservation, 'sensitivity', folder, pin, depth=depth+1)
        if (original is None or preserved is None
                or preservation['workbook_sha256'] != proof['workbook_sha256']
                or preserved.get('source_sha256') != inherited['workbook_sha256']
                or proof['input_signature'] != inherited['input_signature']
                or proof['input_signature'] != preservation['input_signature']):
            return None
        if original.get('profile_sha256') or preserved.get('profile_sha256'):
            if (not original.get('profile_sha256') or original['profile_sha256']!=preserved.get('profile_sha256')
                    or proof.get('profile_sha256')!=original['profile_sha256']
                    or proof.get('native_mapping_sha256')!=original.get('native_mapping_sha256')):
                return None
        return original
    try:
        path = confined(folder, proof['receipt_path'])
        if digest(path) != proof['receipt_sha256']:
            return None
        receipt = json.loads(path.read_text(encoding='utf-8-sig'))
    except (KeyError, TypeError, OSError, ValueError):
        return None
    expected = 'CONVERGENCE_LOCALE' if kind == 'wacc' else 'TABLES_VERIFIEES'
    if (not isinstance(receipt, dict) or receipt.get('status') != expected or receipt.get('output_sha256') != proof['workbook_sha256']
            or receipt.get('source_preserved') is not True or receipt.get('macros_enabled') is not False
            or receipt.get('save_reopen_verified') is not True or receipt.get('iteration_enabled') is not False
            or receipt.get('calculation_state') != 0 or isinstance(receipt.get('calculation_state'), bool)):
        return None
    if kind == 'sensitivity' and (receipt.get('passed') is not True
            or receipt.get('input_signature_before') != proof['input_signature']
            or receipt.get('input_signature_after') != proof['input_signature']):
        return None
    if any(key in proof or key in receipt for key in ('profile_sha256','native_mapping_sha256')):
        if any(not isinstance(proof.get(key),str) or len(proof[key])!=64 or receipt.get(key)!=proof[key]
               for key in ('profile_sha256','native_mapping_sha256')):
            return None
    return receipt
