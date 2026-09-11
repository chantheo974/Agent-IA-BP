"""Utilitaires du modèle distribué, sans générateur ni référence de dossier."""
from __future__ import annotations

import re
from .vendor import input_engine as core

MODEL_ID = 'tca-bp-template/1'


def invalidate_caches(raw: bytes) -> bytes:
    """Retirer les résultats enregistrés sans modifier les formules natives."""
    def one(match):
        cell = match[0]
        if re.search(rb'<f(?:\s|>)', cell):
            cell = re.sub(rb'<v\b[^>]*?(?:/>|>.*?</v>)', b'', cell, flags=re.S)
            cell = re.sub(rb'<is\b[^>]*?(?:/>|>.*?</is>)', b'', cell, flags=re.S)
        return cell
    return core.CELL_RX.sub(one, raw)


def invalidate_chart(raw: bytes) -> bytes:
    """Conserver les séries et références ; Excel repeuplera leurs caches."""
    return re.sub(rb'<(?:\w+:)?(?:numCache|strCache)\b[^>]*>.*?</(?:\w+:)?(?:numCache|strCache)>',
                  b'', raw, flags=re.S)
