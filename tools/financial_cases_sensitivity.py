"""Événements entièrement fictifs pour une grille de sensibilité non dégénérée."""
import math
from tools.financial_cases_common import merge_updates
from tools.financial_cases_operations import _isolated_taxes, _offer, _updates
from tools.financial_cases_assets import _grant


def cash_schedule(volume=0, aid=0):
    """Grand livre fictif indépendant : dates de paiement, achats et stock.

    Aucune formule ou lecture de classeur : les hypothèses proviennent des
    événements décrits ci-dessous. Les stocks augmentent à chaque exercice.
    """
    if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v < -1
           for v in (volume,aid)):
        raise ValueError('Choc fini supérieur ou égal à -100 % requis.')
    cash=0; previous_revenue=0; inventory=0; months=[]
    for month in range(36):
        units=(1200,1440,1800)[month//12]/12*(1+volume)
        revenue=units*100; consumption=units*40
        target_inventory=consumption
        purchases=consumption+target_inventory-inventory
        cash+=previous_revenue-purchases
        if month==0:cash+=-100000+60000*(1+aid)
        if month==6:cash+=100000
        months.append({'month':month,'sales':revenue,'customer_receipts':previous_revenue,
                       'purchases_paid':purchases,'inventory':target_inventory,'closing_cash':cash})
        previous_revenue=revenue;inventory=target_inventory
    return months


def cash_minimum(volume=0, aid=0):
    return min(0,*(month['closing_cash'] for month in cash_schedule(volume,aid)))


def cases():
    changes = merge_updates(
        _isolated_taxes(),
        _offer(reference_price=100, material_cost=40, supplier_days=0, coverage_days=30),
        _updates('Assumptions', {'G15': 100, 'H15': 100, 'K15': 1200, 'L15': 1440, 'M15': 1800,
                                 'U15': 30, 'D126': 0}),
        _updates('DATA CAPEX', {'B13': 'Équipement fictif de la recette de sensibilité',
                               'C13': "Machines-outils et équipements d'atelier", 'D13': 100000,
                               'E13': '2026-01-01', 'F13': 5, 'G13': 'Non', 'H13': 0,
                               'I13': 'Cash', 'M13': 'Corporelle'}),
        _grant(support=60000, years=3, deposit_date='2026-01-15', title='Aide fictive à l’investissement de recette'),
        _updates('DATA Financement', {'B14': 'Fonds propres fictifs reçus après le point bas', 'C14': 'SERIE A',
                                     'D14': 100000, 'E14': '2026-07-01', 'G14': 0}),
        _updates('Sensi Analyses', {'F8': -.2, 'F9': -.15, 'F10': .25, 'F11': .2,
                                   'F12': .1, 'F13': 1, 'F14': -1, 'F15': .3, 'F16': 2}),
    )
    return [{'id': 'sensitivity_active', 'title': 'Sensibilités sur volumes, CAPEX, aides et point bas de cash',
             'events': [
                 'Dossier exclusivement fictif, trois exercices 2026–2028. Objectifs de 1 200, 1 440 puis 1 800 unités ; prix 100 euros, coût matière 40 euros.',
                 'Clients réglant à 30 jours, fournisseurs payés immédiatement, stock cible de 30 jours : les volumes affectent le besoin de cash.',
                 'Équipement payé 100 000 euros en janvier 2026 ; amortissement linéaire sur cinq ans, aucune affectation R&D.',
                 'Aide de 60 000 euros déjà accordée, reçue en janvier 2026, reprise sur trois ans ; taux de saisie 100 % du montant accordé.',
                 'Apport de 100 000 euros en juillet 2026 ; trésorerie d’ouverture nulle. En janvier : aucun encaissement client, 8 000 euros d’achats dont 4 000 de stock, 100 000 d’équipement et 60 000 d’aide, soit un point bas de -48 000 euros.',
                 'Chaque mois suivant dégage un flux commercial positif ; le point bas reste janvier pour les axes étudiés. Réduire les volumes réduit le besoin de stock initial ; supprimer l’aide dégrade le point bas de 60 000 euros.',
                 'Neuf chocs distincts saisis ; les axes de subvention incluent une suppression à -100 %. Les activités absentes peuvent avoir un effet nul au Tornado.',
                 'Convention fiscale fictive : taux explicitement nuls selon les paramètres de recette, sans assertion de droit ou d’éligibilité réelle.',
             ], 'updates': changes,
             'oracles': [{'id': f'base_revenue_{column}', 'sheet': 'Revenue', 'cell': f'{column}282',
                          'expected': quantity*100, 'tolerance': .01,
                          'reason': 'Quantité annuelle indépendante multipliée par le prix fictif de 100 euros.'}
                         for column, quantity in zip('EFG', (1200, 1440, 1800))]
                        + [{'id':'base_cash_minimum','sheet':'Sensi Analyses','cell':'G24','expected':cash_minimum(),
                            'tolerance':.01,'reason':'Grand livre mensuel indépendant : janvier est le point bas.'},
                           {'id':'base_cash_close','sheet':'Sensi Analyses','cell':'F24',
                            'expected':cash_schedule()[-1]['closing_cash'],'tolerance':.01,
                            'reason':'444 000 de ventes moins 15 000 non encaissés, 183 600 d’achats, équipement100 000, aide60 000, apport100 000.'}]
                        + [{'id':f'matrix_cash_{col}{row}','sheet':'Sensi Analyses','cell':f'{col}{row}',
                            'expected':cash_minimum(volume,aid),'tolerance':.01,
                            'reason':'Même grand livre indépendant avec volumes et aide modifiés ; aucune table Excel utilisée pour l’attente.'}
                           for row,volume in zip(range(50,53),(0,-.1,-.2)) for col,aid in zip('DEF',(0,-.5,-1))]}]


def rejection_cases():
    return []
