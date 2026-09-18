"""Strict bounded cell blocks for large, reviewable monthly financial matrices.

No block authorizes an additional operation kind. Expansion produces ordinary
set_value/set_formula operations, which still require the existing source,
scope, formula, profile and approval checks at every execution boundary.
"""
from __future__ import annotations

from copy import deepcopy
import math
import re

MAX_ENVELOPES = 2000
MAX_BLOCK_CELLS = 10000
MAX_TOTAL_CELLS = 20000
MAX_ROWS = 1048576
MAX_COLS = 16384


class ExpandedOperations(list):
    """Runtime-only marker for a previously validated bounded block expansion.

JSON cannot supply this type. Repeated validation retains the original envelope
count; it never confers authorization for values, formulas or source access.
"""
    envelope_count: int
    contains_blocks: bool

    def __init__(self, values=(), *, envelope_count=0, contains_blocks=False):
        super().__init__(values)
        self.envelope_count = envelope_count
        self.contains_blocks = contains_blocks


def _coord(address):
    match = re.fullmatch(r"([A-Za-z]{1,3})([1-9]\d{0,6})", address) if isinstance(address, str) else None
    if not match:
        raise ValueError("Adresse de début A1 explicite requise")
    column = 0
    for letter in match[1].upper():
        column = column * 26 + ord(letter) - 64
    row = int(match[2])
    if row > MAX_ROWS or column > MAX_COLS:
        raise ValueError("Adresse hors limites Excel")
    return row, column


def _address(row, column):
    letters = ""
    while column:
        column, remainder = divmod(column - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters + str(row)


def _source(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000 or any(ord(c) < 32 for c in value):
        raise ValueError("Identifiant de source explicite requis pour chaque cellule du bloc")
    return value


def _reason(value):
    if not isinstance(value, str) or len(value) > 4000:
        raise ValueError("Justification textuelle limitée à 4 000 caractères")
    return value


def _block(operation):
    required = {"type", "sheet", "start_cell", "rows", "evidence_id"}
    if not required <= set(operation) or set(operation) - required - {"reason"}:
        raise ValueError("Clés manquantes ou inconnues dans set_block")
    sheet = operation["sheet"]
    if (not isinstance(sheet, str) or not 1 <= len(sheet) <= 31 or sheet != sheet.strip()
            or any(c in sheet for c in ':\\/?*[]') or sheet.startswith("'") or sheet.endswith("'")
            or any(ord(c) < 32 for c in sheet)):
        raise ValueError("Feuille de bloc invalide")
    source = _source(operation["evidence_id"])
    reason = _reason(operation["reason"]) if "reason" in operation else None
    top, left = _coord(operation["start_cell"])
    rows = operation["rows"]
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], list) or not rows[0]:
        raise ValueError("Une matrice rectangulaire non vide est requise")
    width = len(rows[0])
    if len(rows) * width > MAX_BLOCK_CELLS or any(not isinstance(row, list) or len(row) != width for row in rows):
        raise ValueError("Bloc rectangulaire limité à 10 000 positions")
    if top + len(rows) - 1 > MAX_ROWS or left + width - 1 > MAX_COLS:
        raise ValueError("Le bloc dépasse les limites Excel")
    result = []
    for row_index, row in enumerate(rows):
        for col_index, item in enumerate(row):
            if item is None:
                continue  # hole, unlike {value: None}, which explicitly clears.
            if not isinstance(item, dict) or ("value" in item) == ("formula" in item):
                raise ValueError("Chaque cellule doit préciser exactement value ou formula")
            kind = "set_formula" if "formula" in item else "set_value"
            key = "formula" if kind == "set_formula" else "value"
            permitted = {key, "evidence_id", "reason"} | ({"status"} if kind == "set_value" else set())
            if set(item) - permitted:
                raise ValueError("Clé inconnue ou opération imbriquée interdite dans un bloc")
            value = item[key]
            if kind == "set_formula":
                if not isinstance(value, str) or not value.startswith("=") or not 2 <= len(value) <= 8192:
                    raise ValueError("Formule explicite commençant par = et limitée à 8 192 caractères requise")
            elif value is not None and not isinstance(value, (str, int, float, bool)):
                raise ValueError("Une cellule de bloc accepte seulement une valeur JSON scalaire")
            elif isinstance(value, float) and not math.isfinite(value):
                raise ValueError("Valeur numérique non finie interdite")
            elif isinstance(value, str) and (len(value) > 32767 or value.lstrip().startswith(("=", "+", "@"))):
                raise ValueError("Valeur textuelle trop longue ou assimilable à une formule")
            atom = {"type": kind, "sheet": sheet, "cell": _address(top + row_index, left + col_index),
                    key: value, "evidence_id": _source(item.get("evidence_id", source))}
            if "reason" in item or reason is not None:
                atom["reason"] = _reason(item.get("reason", reason))
            if "status" in item:
                if item["status"] not in {"CONFIRME", "HYPOTHESE", "NON_RENSEIGNE"}:
                    raise ValueError("Qualification de cellule inconnue")
                if (item["value"] is None) != (item["status"] == "NON_RENSEIGNE"):
                    raise ValueError("Une cellule effacée utilise NON_RENSEIGNE")
                atom["status"] = item["status"]
            result.append(atom)
    if not result:
        raise ValueError("Un bloc doit contenir au moins une écriture explicite")
    return result


def expand_operations(operations: list[dict]) -> ExpandedOperations:
    """Expand compact cell blocks in order; ordinary operations are unchanged.

The envelope count remains <=2,000; each block has <=10,000 positions and the
whole batch <=20,000 cell writes. The normal pipeline validates every expanded
operation. A raw flat list of >2,000 operations is still refused.
"""
    if not isinstance(operations, list) or not operations:
        raise ValueError("Un lot non vide est requis")
    repeated = isinstance(operations, ExpandedOperations)
    count = operations.envelope_count if repeated else len(operations)
    if type(count) is not int or not 1 <= count <= MAX_ENVELOPES:
        raise ValueError("Lot limité à 2 000 opérations ou blocs explicites")
    expanded, cells, structures = [], 0, 0
    contains_blocks = repeated and operations.contains_blocks
    for operation in operations:
        if not isinstance(operation, dict) or not isinstance(operation.get("type"), str):
            raise ValueError("Chaque opération est un objet typé")
        if operation["type"] == "set_block":
            items = _block(operation)
            contains_blocks = True
        else:
            items = [deepcopy(operation)]
        for item in items:
            if item["type"] in {"set_value", "set_formula"}:
                cells += 1
            else:
                structures += 1
            if cells > MAX_TOTAL_CELLS or structures > MAX_ENVELOPES:
                raise ValueError("Lot développé supérieur à 20 000 cellules ou 2 000 opérations structurelles")
            expanded.append(item)
    if repeated and not contains_blocks and len(expanded) > MAX_ENVELOPES:
        raise ValueError("Un lot développé volumineux doit provenir de blocs validés")
    return ExpandedOperations(expanded, envelope_count=count, contains_blocks=contains_blocks)


def compact_setters(operations: list[dict], *, minimum_cells=8) -> list[dict]:
    """Compact independent consecutive setters, retaining structural barriers.

Duplicate destinations flush the block so sequential replacements remain
visible. A block expands in row-major order; setters in one block address
distinct cells, with events/macros disabled by the native editing worker.
"""
    if not isinstance(operations, list) or not operations or not 2 <= minimum_cells <= 10000:
        raise ValueError("Liste d’opérations et seuil de compaction valides requis")
    output, run, seen = [], [], set()
    bounds = None
    def flush():
        nonlocal run, seen, bounds
        if not run:
            return
        if len(run) < minimum_cells:
            output.extend(deepcopy(run))
        else:
            top, bottom, left, right = bounds
            matrix = [[None] * (right - left + 1) for _ in range(bottom - top + 1)]
            default_source = run[0]["evidence_id"]
            for operation in run:
                row, column = _coord(operation["cell"])
                item = {k: deepcopy(v) for k, v in operation.items() if k not in {"type", "sheet", "cell"}}
                if item.get("evidence_id") == default_source:
                    item.pop("evidence_id")
                matrix[row - top][column - left] = item
            output.append({"type": "set_block", "sheet": run[0]["sheet"], "start_cell": _address(top, left),
                           "rows": matrix, "evidence_id": default_source})
        run, seen, bounds = [], set(), None
    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError("Chaque opération est un objet")
        if operation.get("type") not in {"set_value", "set_formula"}:
            flush()
            output.append(deepcopy(operation))
            continue
        row, column = _coord(operation.get("cell"))
        _source(operation.get("evidence_id"))
        candidate = (min(bounds[0], row), max(bounds[1], row), min(bounds[2], column), max(bounds[3], column)) if bounds else (row, row, column, column)
        if run and (operation.get("sheet") != run[0].get("sheet") or (row, column) in seen
                    or (candidate[1] - candidate[0] + 1) * (candidate[3] - candidate[2] + 1) > MAX_BLOCK_CELLS):
            flush()
            candidate = (row, row, column, column)
        run.append(operation)
        seen.add((row, column))
        bounds = candidate
    flush()
    # Validate the compact form before returning it to a caller.
    expand_operations(output)
    return output
