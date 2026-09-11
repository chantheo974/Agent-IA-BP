"""Dossier WACC entièrement fictif, avec coût des fonds propres indépendant."""
from tools.financial_cases_common import merge_updates
from tools.financial_cases_operations import _isolated_taxes, _offer, _updates


def cases():
    updates = merge_updates(
        _isolated_taxes(),
        _offer(supplier_days=0, material_cost=40, reference_price=100),
        _updates('Assumptions', {'G15': 100, 'H15': 100, 'K15': 1200, 'L15': 1200, 'M15': 1200, 'U15': 0}),
        _updates('DATA Financement', {'B14': 'Closing fictif pour la recette WACC', 'C14': 'SERIE A',
                                     'D14': 100000, 'E14': '2026-01-01', 'G14': 0}),
        _updates('Valorisation', {'D8': 0.02, 'D9': 0, 'D12': 1, 'D13': 0.2, 'D107': 'Itération',
                                 'D111': '2026-01-01', 'D112': 0.03, 'D113': 0.05, 'D116': 0,
                                 'D117': 0, 'D118': 0, 'D119': 0, 'D120': 'Taux', 'D121': 'Non',
                                 'D122': 'Non', 'D123': 'Non', 'E112': 'Taux fictif de recette 3 pour cent',
                                 'E113': 'Prime fictive de recette 5 pour cent', 'E116': 'Aucune dette dans la recette'}),
        _updates('Comparables', {'B117': 'Comparable exclusivement fictif', 'C117': 'Oui', 'D117': 1.2,
                                'E117': 1000000, 'F117': 0, 'G117': 0, 'J117': '2026-01-01',
                                'K117': 'Jeu mathématique indépendant : bêta1,2 sans dette.',
                                'L117': 'Mensuelle', 'M117': 3}),
    )
    return [{'id': 'wacc_unlevered', 'title': 'WACC fictif sans dette et DCF indépendant', 'updates': updates,
             'events': ['Offre fictive : 1200 unités par an à100EUR, coût matière40EUR, paiement immédiat, sans stock ni dette.',
                        'Trois exercices2026–2028, flux annuels attendus72000EUR hors impôt dans cette convention de recette.',
                        'Taux sans risque3%, bêta1,2 sans dette, prime marché5%, aucune prime additionnelle : WACC attendu9%.',
                        'Croissance terminale2%, closing1janvier2026. Le fluxterminal attendu est72000*1,02EUR.',
                        'Les valeurs et les qualifications sont fictives ; aucune source réelle de marché ni qualification fiscale ne sont revendiquées.'],
             'oracles': [{'id': f'{sheet}_{column}{row}', 'sheet': sheet, 'cell': f'{column}{row}',
                          'expected': expected, 'tolerance': 0.01, 'reason': reason}
                         for column in 'EFG' for sheet, row, expected, reason in
                         [('Revenue', 282, 120000, '1200 unités à100EUR.'), ('COGS', 253, 48000, '1200 unités coûtant40EUR.')]],
             'wacc_expected': 0.03 + 1.2 * 0.05,
             'equity_expected': sum(72000 / 1.09**year for year in range(1, 4)) + (72000 * 1.02 / (0.09-0.02)) / 1.09**3}]


def rejection_cases():
    return []
