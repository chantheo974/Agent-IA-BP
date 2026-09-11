"""Refus des qualifications absentes et branches explicites, scénario fictif."""


def cases():
    updates = []
    for col, value in zip('CDEF', (None, 'À confirmer', 'Non', 'Oui')):
        for row in (66, 85):
            updates.append({'sheet': 'ATELIER_CIR_IS', 'cell': col + str(row), 'value': value})
    oracles = []
    for col, capital, surcharge in [('C', '#N/A', '#N/A'), ('D', '#N/A', '#N/A'), ('E', False, 1), ('F', True, 0)]:
        for row, expected in ((67, capital), (86, surcharge)):
            kind = 'boolean' if isinstance(expected, bool) else 'excel_error' if isinstance(expected, str) else 'number'
            oracles.append({'id': col + str(row), 'sheet': 'ATELIER_CIR_IS', 'cell': col + str(row),
                            'expected': expected, 'expected_kind': kind, 'tolerance': 0,
                            'reason': 'Inconnu et à confirmer sont indisponibles ; Non/Oui utilisent la branche explicitement renseignée.'})
    for col in ('H', 'M'):
        for row, expected, kind in ((67, False, 'boolean'), (86, 0, 'number')):
            oracles.append({'id': 'outside_' + col + str(row), 'sheet': 'ATELIER_CIR_IS', 'cell': col + str(row),
                            'expected': expected, 'expected_kind': kind, 'tolerance': 0,
                            'reason': 'Exercice hors horizon de cinq ans : aucun flux fiscal, sans propager une erreur vers une synthèse active.'})
    return [{'id': 'qualification_fiscal_branches', 'title': 'Qualifications inconnues et branches explicites', 'horizon': 5,
             'events': ['Scénario logiciel entièrement fictif, toutes les offres inactives et aucun solde d’ouverture.',
                        'Quatre exercices portent successivement les statuts vide, À confirmer, Non et Oui.',
                        'Les années au-delà des cinq exercices actifs restent inactives, même sans qualification fiscale future.',
                        'Les états inconnus doivent rendre le calcul indisponible ; aucune éligibilité réelle n’est affirmée.'],
             'updates': updates, 'oracles': oracles}]
