"""Cadre explicitement fictif des recettes financières, sans hypothèse héritée.

Zéro signifie ici un choix documenté du scénario logiciel. Ces valeurs ne sont
jamais proposées comme valeurs par défaut d'un vrai dossier.
"""
from __future__ import annotations


def common_updates(horizon=3, start="2026-01-01") -> list[dict]:
    values = {
        "Control": {"C10": start, "C59": horizon, "C13": 30, "C24": 1,
                    **{f"C{row}": 0 for row in (28, 29, 30, 31, 32, 33, 34)}},
        "Assumptions": {**{f"D{row}": 0 for row in (4, 5, 7, 66, 83, 126)},
                        **{f"C{row}": 0 for row in range(15, 28)}},
        "Stock": {"E10": 0, "E11": 0},
        "Sensi TCA": {"C15": "Central"},
    }
    return [{"sheet": sheet, "cell": cell, "value": value}
            for sheet, cells in values.items() for cell, value in cells.items()]


def merge_updates(*groups: list[dict]) -> list[dict]:
    """Les événements du cas remplacent intentionnellement son cadre commun.

    Un doublon au sein d'un même groupe reste une erreur de fixture.
    """
    result = {}
    for group in groups:
        seen = set()
        for item in group:
            key = item["sheet"], item["cell"]
            if key in seen:
                raise ValueError("Doublon dans une définition de scénario : " + "!".join(key))
            seen.add(key)
            result[key] = dict(item)
    return list(result.values())
