"""Trois scénarios commerciaux fictifs : FIFO, facturation et stocks/TVA/BFR.

Entrées et attentes dérivent d'événements décrits ici, sans lecture de formule
ou de cache Excel. Le runner ajoute common_updates(3, '2026-01-01'), preuves et
statuts explicites, puis recalcule des copies isolées. Ce module n'ouvre pas Excel.

Les taux nuls hors TVA sont des conventions EXPLICITES de recette logicielle
pour isoler les flux. Ils ne décrivent ni un régime fiscal réel ni une exonération
à proposer à un dossier. Les opérations et montants sont entièrement fictifs.
"""
from __future__ import annotations

import copy
import math

from tools.financial_cases_common import merge_updates


def _updates(sheet, values):
    return [{"sheet": sheet, "cell": cell, "value": value} for cell, value in values.items()]


def _col(number):
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _m(first_column, month, row):
    return _col(first_column + month) + str(row)


def _oracle(sheet, cell, expected, reason):
    return {"id": sheet + "_" + cell, "sheet": sheet, "cell": cell,
            "expected": expected, "tolerance": 0.01, "reason": reason}


def fifo_schedule(cohorts, monthly_capacity, months):
    """Livre un carnet par ordre d'arrivée ; chaque unité conserve son prix.

    Les cohortes sont des événements {month, quantity, price}. Cette petite
    simulation indépendante ne connaît aucune adresse ou formule du classeur.
    """
    if (not isinstance(months, int) or isinstance(months, bool) or months < 1
            or not isinstance(monthly_capacity, (int, float)) or isinstance(monthly_capacity, bool)
            or not math.isfinite(monthly_capacity) or monthly_capacity <= 0):
        raise ValueError("Nombre de mois et capacité positive requis.")
    arrivals = []
    for index, event in enumerate(cohorts):
        month, quantity, price = event["month"], event["quantity"], event["price"]
        if (not isinstance(month, int) or isinstance(month, bool) or month < 0
                or any(not isinstance(v, (int, float)) or isinstance(v, bool)
                       or not math.isfinite(v) or v < 0 for v in (quantity, price))):
            raise ValueError("Cohorte invalide.")
        arrivals.append({"month": month, "remaining": quantity, "price": price, "order": index})
    arrivals.sort(key=lambda event: (event["month"], event["order"]))
    result = []
    for month in range(months):
        capacity, quantity, revenue = monthly_capacity, 0, 0
        for cohort in arrivals:
            if cohort["month"] > month:
                continue
            shipped = min(capacity, cohort["remaining"])
            quantity += shipped
            revenue += shipped * cohort["price"]
            cohort["remaining"] -= shipped
            capacity -= shipped
        present = [event for event in arrivals if event["month"] <= month]
        result.append({"month": month, "delivered": quantity, "revenue": revenue,
                       "backlog_quantity": sum(event["remaining"] for event in present),
                       "backlog_value": sum(event["remaining"] * event["price"] for event in present)})
    return result


def _isolated_taxes(vat=0, regime="Exonéré / hors champ"):
    # Tous les zéros sont explicitement décrits dans les événements de recette.
    assumptions = {f"D{row}": 0 for row in (68, 69, 70, 71, 72, 73, 74, 75,
                                            77, 78, 79, 84, 85, 86, 87, 93)}
    assumptions.update({"D76": 1, "D83": vat, "D88": 1_000_000})
    fiscal = {f"{col}{row}": value for col in "CDE" for row, value in
              ((66, "Non"), (85, "Non"), (89, 0), (91, 0), (110, 0), (111, 0),
               (117, "Société fictive créée au début du plan ; aucun solde fiscal antérieur."))}
    fiscal.update({"C93": 0, "D143": regime, "E143": vat, "F143": "Confirmé",
                   "D160": "Mensuelle", "D161": 1, "D162": "Non", "D163": 3,
                   "D164": 760, "D165": 150, "D166": "Confirmé"})
    return _updates("Assumptions", assumptions) + _updates("ATELIER_CIR_IS", fiscal)


def _offer(*, unit="unité", capacity=0, supplier_days=30, coverage_days=0,
           material_cost=40, mode="Detaille", reference_price=777):
    values = {"C15": 1, "D15": unit, "E15": "Oui", "F15": reference_price,
              "K15": 0, "L15": 0, "M15": 0,
              "P15": capacity * 12, "Q15": capacity * 12, "R15": capacity * 12,
              "U15": 30, "V15": 0, "W15": 0, "X15": 0, "Y15": 0, "Z15": 1}
    return (_updates("Assumptions", values)
            + _updates("DATA COGS", {"D15": mode, "E15": material_cost, "F15": 0, "G15": 0,
                                       "H15": 0, "J15": 0, "K15": 0, "L15": 0})
            + _updates("Stock", {"E10": coverage_days, "E11": supplier_days}))


def _contract(row, *, title, quantity, price, start, end, recognition="Fin de contrat",
              invoicing="Au fil de l'eau", deposit=0, deposit_date=None,
              balance_date=None, regime="Exonéré / hors champ", vat=0):
    values = {"B": title, "C": "Offre 01", "E": quantity, "F": price, "H": start, "I": end,
              "J": recognition, "K": invoicing, "L": deposit, "M": deposit_date,
              "N": 0, "O": None, "Q": balance_date, "R": "Signe", "S": 1,
              "AL": regime, "AM": vat}
    return _updates("DATA Contrats", {f"{col}{row}": value for col, value in values.items()})


def _tax_event():
    return ("Convention de recette : zéro IS, CIR, C3S et CFE explicitement saisi, aucune CVAE sous le seuil fictif de 1 million ; "
            "aucun autre coût, personnel, financement ou solde d'ouverture. Ce choix logiciel n'est pas une qualification fiscale réelle.")


def cases():
    fifo = {
        "id": "operations_fifo_two_prices", "title": "Deux cohortes à prix distincts sous capacité mensuelle",
        "events": [
            "Contrat A signé : 150 unités à 100 euros, demandé en janvier 2026. Contrat B signé : 150 unités à 200 euros, demandé en février 2026.",
            "Capacité de livraison de 100 unités par mois ; aucune commande prévisionnelle supplémentaire. Livraison FIFO, prix du contrat conservé, grille de référence volontairement différente à 777 euros.",
            "Janvier livre 100 unités A (10 000 euros) ; février livre 50 A puis 50 B (15 000 euros) ; mars livre 100 B (20 000 euros).",
            "Facturation à la livraison, paiement client à 30 jours conventionnels, donc le mois suivant ; régime client et fournisseur fictivement hors TVA.",
            "Matière de 40 euros par unité livrée, aucun autre coût direct, stock cible nul. Achats au mois de consommation et paiement fournisseur le mois suivant.",
            "Cash attendu : zéro fin janvier, 6 000 fin février, 17 000 fin mars, 33 000 fin avril et à la clôture. Carnet restant : 50 A puis 100 B puis zéro.",
            _tax_event(),
        ],
        "updates": merge_updates(_isolated_taxes(), _offer(capacity=100),
            _contract(14, title="Commande A fictive", quantity=150, price=100, start="2026-01-01", end="2026-01-31"),
            _contract(15, title="Commande B fictive", quantity=150, price=200, start="2026-02-01", end="2026-02-28")),
        "oracles": [],
    }
    schedule = fifo_schedule([{"month": 0, "quantity": 150, "price": 100},
                              {"month": 1, "quantity": 150, "price": 200}], 100, 4)
    for event, cash, receivable, supplier_payment, cash_balance in zip(
            schedule, (0, 10000, 15000, 20000), (10000, 15000, 20000, 0),
            (0, 4000, 4000, 4000), (0, 6000, 17000, 33000)):
        month = event["month"]
        for row, expected, reason in (
            (29, 100, "Capacité annuelle de 1 200 unités, soit 100 unités par mois."),
            (30, event["delivered"], "Quantité physiquement livrée selon le carnet FIFO."),
            (31, event["backlog_quantity"], "Unités commandées restant à livrer."),
            (36, event["revenue"], "Prix propres aux unités de chaque cohorte, sans réévaluation au prix courant."),
            (40, event["revenue"], "Facturation au rythme des livraisons."),
            (41, cash, "Factures clients réglées le mois suivant."),
            (42, receivable, "Facturé moins encaissé cumulé."),
            (43, 0, "Aucune facture avant reconnaissance : pas de PCA."),
            (44, 0, "Facturation simultanée à la reconnaissance : pas de FAE.")):
            fifo["oracles"].append(_oracle("Revenue", _m(16, month, row), expected, reason))
        fifo["oracles"] += [
            _oracle("Contrats", _m(16, month, 312), event["backlog_value"], "Carnet signé restant valorisé aux prix contractuels d'origine ; ligne 312 mensuelle (434 est annuelle)."),
            _oracle("Stock", _m(17, month, 14), event["delivered"] * 40, "Quarante euros de matière consommée par unité livrée."),
            _oracle("Stock", _m(17, month, 15), 0, "Stock cible explicitement nul et achats égaux à la consommation."),
            _oracle("Stock", _m(17, month, 19), supplier_payment, "Les achats matériels sont payés le mois suivant."),
            _oracle("Modèle financier", _m(20, month, 321), cash_balance, "Solde du compte bancaire indépendant : règlements clients moins fournisseurs."),
        ]
    fifo["oracles"] += [
        _oracle("Revenue", "E282", 45000, "150 unités à 100 euros et 150 à 200 euros, intégralement livrées."),
        _oracle("COGS", "E253", 12000, "Trois cents unités à 40 euros de matière, sans double main-d'œuvre."),
        _oracle("Compte de Résultat", "D85", 33000, "45 000 de ventes moins 12 000 de matière ; autres postes explicitement nuls."),
        _oracle("Bilan", "D18", 33000, "Tous les règlements sont terminés en avril."),
        _oracle("Bilan", "D59", 0, "À la clôture, cash de 33 000 et résultat de 33 000 équilibrent le bilan."),
        _oracle("Flux de trésorerie", "D11", 33000, "CAF égale au résultat, aucun BFR restant en fin d'exercice."),
    ]

    timing = {
        "id": "operations_deposit_pca_fae", "title": "Acompte, FAE et règlement au-delà de la clôture",
        "events": [
            "Prestation fictive signée de 12 000 euros, reconnue à raison de 4 000 euros par mois de novembre 2026 à janvier 2027 inclus.",
            "Acompte facturé de 6 000 euros en novembre 2026 ; solde de 6 000 euros facturé en avril 2027. Chaque facture est réglée le mois suivant ; aucun jalon intermédiaire.",
            "En novembre, facture 6 000 moins produit 4 000 : PCA de 2 000 euros et créance client de 6 000. En décembre, produits cumulés 8 000 moins factures 6 000 : FAE de 2 000 euros ; acompte encaissé 6 000.",
            "Janvier 2027 porte la FAE à 6 000 ; la facture d'avril transforme la FAE en créance de 6 000, soldée par le paiement de mai.",
            "À fin 2026 : cash 6 000 + FAE 2 000 = résultat 8 000. À fin 2027 : cash 12 000 = résultat reporté 8 000 + résultat de l'année 4 000.",
            "Aucun coût direct, aucune TVA dans ce scénario logiciel ; offre au forfait et capacité non limitante.",
            _tax_event(),
        ],
        "updates": merge_updates(_isolated_taxes(), _offer(unit="forfait", mode="Manuel", material_cost=0, reference_price=1),
            _contract(14, title="Prestation pluriannuelle fictive", quantity=1, price=12000,
                      start="2026-11-01", end="2027-01-31", recognition="Etalee sur la duree",
                      invoicing="Acompte et solde", deposit=0.5, deposit_date="2026-11-15", balance_date="2027-04-15")),
        "oracles": [],
    }
    # Chronologie indépendante : mois, produit, facture, cash, créance, PCA, FAE, cash cumulé.
    timing_events = [(9, 0, 0, 0, 0, 0, 0, 0), (10, 4000, 6000, 0, 6000, 2000, 0, 0),
                     (11, 4000, 0, 6000, 0, 0, 2000, 6000), (12, 4000, 0, 0, 0, 0, 6000, 6000),
                     (14, 0, 0, 0, 0, 0, 6000, 6000), (15, 0, 6000, 0, 6000, 0, 0, 6000),
                     (16, 0, 0, 6000, 0, 0, 0, 12000)]
    for month, revenue, invoice, cash, receivable, pca, fae, balance in timing_events:
        for row, expected, reason in ((36, revenue, "Produit mensuel de la prestation de trois mois."),
                                      (40, invoice, "Deux factures de 6 000, en novembre puis avril."),
                                      (41, cash, "Règlement un mois après la facture."),
                                      (42, receivable, "Facturation cumulée moins cash client cumulé."),
                                      (43, pca, "Facturation précédant le produit : montant restant à reconnaître."),
                                      (44, fae, "Produit reconnu non encore facturé.")):
            timing["oracles"].append(_oracle("Revenue", _m(16, month, row), expected, reason))
        timing["oracles"].append(_oracle("Modèle financier", _m(20, month, 321), balance,
                                          "Seuls les règlements de décembre et mai modifient le cash."))
    for sheet, cell, expected, reason in [
        ("Revenue", "E282", 8000, "Deux mois de prestation en 2026."),
        ("Revenue", "F282", 4000, "Dernier mois de prestation en 2027."),
        ("Bilan", "D13", 2000, "FAE à la clôture 2026 : produit 8 000 moins factures 6 000."),
        ("Bilan", "D14", 0, "L'acompte facturé a été réglé en décembre."),
        ("Bilan", "D18", 6000, "Seul acompte reçu en 2026."),
        ("Bilan", "D49", 0, "Le produit cumulé dépasse la facturation à fin 2026 : aucune PCA."),
        ("Bilan", "D34", 8000, "Résultat 2026 sans coûts ni impôts dans la convention de recette."),
        ("Bilan", "D59", 0, "Cash 6 000 + FAE 2 000 = résultat 8 000."),
        ("Bilan", "E13", 0, "Toutes les prestations sont facturées et encaissées en 2027."),
        ("Bilan", "E18", 12000, "Deux règlements de 6 000 au total."),
        ("Bilan", "E59", 0, "Cash 12 000 = résultats cumulés 12 000."),
        ("Flux de trésorerie", "D5", 8000, "CAF 2026 égale au produit sans coût."),
        ("Flux de trésorerie", "D6", 2000, "Hausse de FAE de 2 000, déduite de la CAF dans le flux."),
        ("Flux de trésorerie", "D11", 6000, "CAF 8 000 moins FAE 2 000."),
        ("Flux de trésorerie", "E6", -2000, "La FAE de clôture disparaît entre les deux clôtures."),
        ("Flux de trésorerie", "E11", 6000, "CAF 4 000 plus libération du BFR2 000."),
    ]:
        timing["oracles"].append(_oracle(sheet, cell, expected, reason))

    vat = {
        "id": "operations_inventory_vat_bfr", "title": "Stock de sécurité, TVA et paiements après clôture",
        "events": [
            "Cent biens fictifs vendus et livrés en décembre 2026 à 100 euros HT : facture 10 000 HT, TVA 20 %, soit12 000 TTC, encaissée en janvier 2027.",
            "Matière 40 euros par bien, soit4 000 consommés. Constituer en décembre un stock de sécurité équivalent à un mois de consommation, soit4 000 ; achats8 000 HT.",
            "Facture fournisseur de 9 600 TTC en décembre (8 000 HT +1 600 TVA déductible), réglée en janvier 2027. Le stock non consommé de 4 000 reste détenu ; aucune vente, dépréciation ou acquisition après décembre.",
            "TVA des biens exigible à la livraison :2 000. TVA déductible sur facture :1 600. Déclaration mensuelle, paiement du solde 400 au Trésor en janvier 2027 ; aucun remboursement demandé.",
            "À fin 2026 : actifs stock 4 000 + clients12 000 ; passif fournisseurs 9 600 + TVA 400 + résultat 6 000. Cash nul et BFR 6 000.",
            "En janvier 2027 : cash 12 000 moins 9 600 moins 400 =2 000. À fin 2027 : cash 2 000 + stock 4 000, sans dette résiduelle ; BFR 4 000.",
            _tax_event(),
        ],
        "updates": merge_updates(_isolated_taxes(vat=0.2, regime="Biens"), _offer(coverage_days=30),
            _contract(14, title="Vente biens décembre fictive", quantity=100, price=100,
                      start="2026-12-01", end="2026-12-31", regime="Biens", vat=0.2)),
        "oracles": [],
    }
    # Décembre2026, janvier 2027 puis février2027 : stock physique restant4 000.
    for month, consumed, purchases, supplier_payment, supplier_debt in (
            (10, 0, 0, 0, 0), (11, 4000, 8000, 0, 8000), (12, 0, 0, 8000, 0), (13, 0, 0, 0, 0)):
        stock = 0 if month == 10 else 4000
        for row, expected, reason in ((14, consumed, "Matière consommée par les biens livrés."),
                                      (15, stock, "Stock de sécurité physiquement détenu, conservé après l'arrêt des ventes."),
                                      (17, purchases, "Achats =4 000 consommés +4 000 de stock à constituer."),
                                      (18, purchases, "Facture fournisseur HT à réception des matières."),
                                      (19, supplier_payment, "Règlement fournisseur HT le mois suivant."),
                                      (20, supplier_debt, "Solde fournisseur HT de la feuille Stock.")):
            vat["oracles"].append(_oracle("Stock", _m(17, month, row), expected, reason))
    for sheet, first_column, row, expected_dec, expected_jan, reason in [
        ("Revenue", 16, 36, 10000, 0, "Produit HT reconnu à la livraison de décembre."),
        ("Revenue", 16, 40, 10000, 0, "Facture HT de décembre, sans seconde facture."),
        ("Revenue", 16, 41, 0, 10000, "Encaissement HT en janvier."),
        ("Revenue", 16, 42, 10000, 0, "Créance HT avant ajout de la TVA au bilan."),
        ("ATELIER_CIR_IS", 14, 189, 2000, 0, "TVA exigible à la livraison des biens."),
        ("ATELIER_CIR_IS", 14, 192, 1600, 0, "TVA déductible des achats facturés."),
        ("ATELIER_CIR_IS", 14, 194, 400, 0, "TVA nette de la déclaration de décembre."),
        ("ATELIER_CIR_IS", 14, 198, 0, 400, "TVA payée au Trésor avec un mois de décalage."),
        ("ATELIER_CIR_IS", 14, 204, 400, 0, "TVA restant due à la clôture du mois."),
        ("Modèle financier", 20, 287, 0, 2000, "TVA clients effectivement encaissée avec la facture."),
        ("Modèle financier", 20, 307, 0, 1600, "TVA fournisseurs effectivement payée avec la facture."),
        ("Modèle financier", 20, 308, 0, 400, "Décaissement fiscal distinct du paiement fournisseur."),
        ("Modèle financier", 20, 321, 0, 2000, "Mouvement bancaire TTC :12 000 -9 600 -400."),
        ("BFR", 16, 24, 6000, 4000, "Stock + clients TTC - fournisseurs TTC - TVA nette due."),
    ]:
        vat["oracles"] += [_oracle(sheet, _m(first_column, 11, row), expected_dec, reason),
                            _oracle(sheet, _m(first_column, 12, row), expected_jan, reason)]
    for sheet, cell, expected, reason in [
        ("Bilan", "D11", 4000, "Matières physiquement détenues à fin 2026, incluses dans le stock total ligne 11."),
        ("Bilan", "D14", 12000, "Créance client TTC non réglée."),
        ("Bilan", "D18", 0, "Aucun encaissement ou paiement avant janvier 2027."),
        ("Bilan", "D50", 9600, "Dette fournisseur TTC non réglée."),
        ("Bilan", "D53", 400, "TVA nette de décembre à payer en janvier."),
        ("Bilan", "D34", 6000, "10 000 de ventes moins 4 000 de matières consommées ; stock non passé en charge."),
        ("Bilan", "D59", 0, "16 000 d'actifs =10 000 de dettes +6 000 de résultat."),
        ("Bilan", "E11", 4000, "Le stock reste détenu après règlement des factures, ligne 11 du bilan."),
        ("Bilan", "E18", 2000, "Solde bancaire après règlement clients, fournisseurs et TVA."),
        ("Bilan", "E50", 0, "Fournisseur payé en janvier 2027."),
        ("Bilan", "E53", 0, "TVA payée en janvier 2027."),
        ("Bilan", "E59", 0, "Cash 2 000 + stock 4 000 = résultat reporté 6 000."),
        ("BFR", "E24", 6000, "BFR de clôture 2026."),
        ("BFR", "F24", 4000, "Seul le stock reste dans le BFR de clôture 2027."),
        ("Flux de trésorerie", "D11", 0, "CAF 6 000 absorbée par la hausse du BFR 6 000."),
        ("Flux de trésorerie", "E11", 2000, "BFR réduit de 6 000 à 4 000, sans autre résultat ou flux."),
        ("Flux de trésorerie", "D26", 0, "Cash de clôture 2026."),
        ("Flux de trésorerie", "E26", 2000, "Cash de clôture 2027 rapproché du bilan."),
    ]:
        vat["oracles"].append(_oracle(sheet, cell, expected, reason))
    return [fifo, timing, vat]


def rejection_cases():
    """Six lots invalides, chacun associé à un motif attendu explicite."""
    originals = {case["id"]: case for case in cases()}
    definitions = [
        ("end_before_start", "operations_fifo_two_prices", "DATA Contrats", {"I14": "2025-12-31"},
         ["fin antérieure au début"], "Un contrat ne peut finir avant sa date de début."),
        ("forecast_in_real_register", "operations_fifo_two_prices", "DATA Contrats", {"R14": "Previsionnel"},
         ["un objectif commercial va dans Assumptions"], "Les objectifs prévisionnels ne sont pas des contrats réels."),
        ("negative_capacity", "operations_fifo_two_prices", "Assumptions", {"P15": -1},
         ["minimum : Assumptions!P15"], "Une capacité de livraison négative est impossible."),
        ("milestones_above_total", "operations_deposit_pca_fae", "DATA Contrats", {"L14": 0.7, "N14": 0.4, "O14": "2026-12-15"},
         ["acomptes et jalons au-dessus de 100 %"], "Acompte 70 % plus jalon 40 % dépassent le prix du contrat."),
        ("exempt_with_positive_vat", "operations_inventory_vat_bfr", "DATA Contrats", {"AL14": "Exonéré / hors champ"},
         ["TVA exonérée incompatible avec un taux positif"], "Une exemption explicite ne peut conserver un taux client 20 %."),
        ("negative_material_cost", "operations_inventory_vat_bfr", "DATA COGS", {"E15": -1},
         ["minimum : DATA COGS!E15"], "Un coût unitaire matière négatif n'est pas une dépense valide."),
    ]
    result = []
    for key, source, sheet, values, fragments, reason in definitions:
        fixture = originals[source]
        result.append({"id": "operations_reject_" + key, "title": reason,
                       "events": fixture["events"] + [reason],
                       "updates": merge_updates(copy.deepcopy(fixture["updates"]), _updates(sheet, values)),
                       "expected_exception": "ValueError", "expected_error_any": fragments,
                       "reason": reason, "mutations": _updates(sheet, values)})
    return result
