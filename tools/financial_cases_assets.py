"""Événements fictifs et oracles indépendants : actifs, crédit-bail et aides.

Ce module ne lit aucune formule ni donnée de client et ne lance pas Excel.
Le runner applique common_updates(horizon=3, start='2026-01-01') avant chaque
cas, dans un dossier neuf. Il ajoute les preuves, statuts et autorisations
de remplacement aux écritures ci-dessous. Les sorties ne valent preuve qu'après
un recalcul natif dont les signatures d'entrée et de modèle sont vérifiées.

Conventions testées du modèle : bail comptabilisé en charges, sans activation
ni amortissement de l'actif ; échéances mensuelles à terme échu, mois entier ;
frais de services au prorata des mois d'utilisation hors couverture ; reprise
linéaire des aides d'investissement plafonnée aux encaissements cumulés.
Ces conventions sont des hypothèses de recette, pas des règles comptables
universelles ni une qualification d'éligibilité à une aide.
"""
from __future__ import annotations

import copy
import math
from collections.abc import Callable


def _updates(sheet: str, values: dict) -> list[dict]:
    return [{"sheet": sheet, "cell": cell, "value": value}
            for cell, value in values.items()]


def _oracle(sheet: str, cell: str, expected: float, reason: str) -> dict:
    return {"id": sheet + "_" + cell, "sheet": sheet, "cell": cell,
            "expected": expected, "tolerance": 0.01, "reason": reason}


def _col(number: int) -> str:
    """Adressage seulement ; janvier 2026 est le mois d'indice zéro."""
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _month(first_column: int, offset: int, row: int) -> str:
    return _col(first_column + offset) + str(row)


def lease_payment(principal: float, annual_rate: float, months: int) -> float:
    """Résoudre un solde par échéances, sans reprendre PMT/formule Excel.

    À chaque mois : intérêt sur le solde, puis paiement. La dichotomie cherche
    le paiement constant qui rembourse exactement le solde au dernier mois.
    Aucun arrondi au centime n'est imposé avant la comparaison des sorties.
    """
    if (isinstance(months, bool) or not isinstance(months, int) or months < 1
            or not all(isinstance(x, (int, float)) and not isinstance(x, bool)
                       and math.isfinite(x) for x in (principal, annual_rate))
            or principal <= 0 or annual_rate < 0):
        raise ValueError("Capital positif, taux non négatif et mois entiers requis.")
    lower, upper = 0.0, principal * (1 + annual_rate / 12)
    for _ in range(90):
        payment = (lower + upper) / 2
        balance = principal
        for _month_index in range(months):
            balance += balance * annual_rate / 12
            balance -= payment
        if balance > 0:
            lower = payment
        else:
            upper = payment
    return (lower + upper) / 2


def assert_oracles(read_value: Callable[[str, str], object], oracles: list[dict]) -> list[dict]:
    """Échec fermé : un cache absent/texte/erreur/NaN/booléen n'est jamais zéro.

    Le runner reste responsable de la preuve du recalcul natif et des signatures.
    Cette fonction ne peut pas transformer des caches anciens en preuve actuelle.
    """
    if not oracles:
        raise ValueError("Aucun oracle financier : succès interdit.")
    result = []
    for oracle in oracles:
        expected, tolerance = oracle["expected"], oracle.get("tolerance", 0.01)
        if any(not isinstance(x, (int, float)) or isinstance(x, bool)
               or not math.isfinite(x) for x in (expected, tolerance)) or tolerance < 0:
            raise ValueError("Oracle numérique ou tolérance invalide.")
        actual = read_value(oracle["sheet"], oracle["cell"])
        passed = (isinstance(actual, (int, float)) and not isinstance(actual, bool)
                  and math.isfinite(actual) and abs(actual - expected) <= tolerance)
        result.append({**oracle, "actual": actual, "passed": passed})
        if not passed:
            raise AssertionError(f"{oracle['id']}: {actual!r}, attendu {expected!r}")
    return result


def _neutral_scenario() -> list[dict]:
    # Les axes I72/J72 et E14/E15 des analyses sont des constantes techniques
    # protégées à zéro dans la trame. Seul le sélecteur est une vraie entrée.
    return _updates("Sensi TCA", {"C15": "Central"})


def _asset(*, amount=12000, start="2026-11-01", months=2, rate=0,
           covered="Oui", stop="2027-03-31") -> list[dict]:
    # Les huit défauts sont explicitement qualifiés dans cette fixture.
    return _updates("DATA CAPEX", {
        "B13": "Machine de recette fictive", "C13": "Machines-outils et équipements d'atelier",
        "D13": amount, "E13": start, "F13": 3, "G13": "Non", "H13": 0,
        "I13": "Crédit-bail", "J13": months / 12, "K13": rate,
        "M13": "Corporelle", "N13": covered, "O13": covered, "P13": stop})


def _service_costs(maintenance=0.12, insurance=0.06) -> list[dict]:
    values = {f"{col}{row}": 0 for row in (36, 38) for col in "EFGHL"}
    values.update({"J36": "CA reconnu", "J38": "CA reconnu", "I36": 0,
                   "K36": maintenance, "K38": insurance})
    return _updates("Charges_Externes", values)


def _no_asset_double_count(annual_columns=("P", "Q", "R")) -> list[dict]:
    result = []
    for column in annual_columns:
        for row, label in ((75, "amortissement"), (77, "décaissement d'acquisition"),
                           (80, "valeur nette comptable")):
            result.append(_oracle("CAPEX", f"{column}{row}", 0,
                                  f"Le bail passé en charges ne crée aucun {label}."))
    result.append(_oracle("Financement Dette", "M86", 0,
                          "Aucun emprunt distinct : ne pas compter une seconde fois les intérêts du loyer."))
    return result


def _grant(row=3, *, support=120000, rate=1, years=3, deposit=1,
           deposit_date="2026-01-15", balance=0, balance_date=None,
           recognition_start="2026-01-01", title="Aide accordée fictive") -> list[dict]:
    values = {"A": title, "B": "Montant accordé" if rate == 1 else "Assiette et taux documentés",
              "C": support, "D": rate, "E": years, "F": "Linéaire", "G": deposit,
              "H": deposit_date, "I": balance, "J": balance_date, "K": recognition_start,
              "M": "Notification fictive de recette, aucune aide réelle"}
    return _updates("SUBVENTION_INVEST", {f"{col}{row}": v for col, v in values.items()})


def cases() -> list[dict]:
    """Sept cas isolés, à exécuter chacun après le cadre commun explicite."""
    covered = {
        "id": "assets_lease_services_end", "title": "Fin du bail puis fin des services hors couverture",
        "events": [
            "Machine fictive de 12 000 euros disponible le 1er novembre 2026 ; deux loyers mensuels sans intérêt de 6 000 euros.",
            "Entretien et assurance inclus pendant novembre et décembre. La machine reste utilisée jusqu'au 31 mars 2027 inclus.",
            "Hors couverture, entretien annuel de 12 % et assurance annuelle de 6 % de la valeur de 12 000 euros, proratisés par mois ; aucune autre charge.",
            "Attendu : janvier à mars, entretien 120 euros/mois et assurance 60 euros/mois ; plus aucun frais lié à cet actif en avril.",
        ],
        "updates": _neutral_scenario() + _asset() + _service_costs(),
        "oracles": _no_asset_double_count() + [
            _oracle("CAPEX", "P81", 12000, "Deux loyers de 6 000 euros en 2026."),
            _oracle("CAPEX", "Q81", 0, "Le contrat de location s'achève en décembre 2026."),
            _oracle("Modèle financier", "C138", 12000, "Les deux loyers sont repris une fois en charges externes."),
            _oracle("Charges_Externes", "E19", 0, "Entretien inclus dans les loyers de 2026."),
            _oracle("Charges_Externes", "E21", 0, "Assurance incluse dans les loyers de 2026."),
            _oracle("Charges_Externes", "F19", 360, "Trois mois d'entretien à 120 euros."),
            _oracle("Charges_Externes", "F21", 180, "Trois mois d'assurance à 60 euros."),
            _oracle("Modèle financier", "D138", 0, "Aucun loyer après l'échéance contractuelle."),
        ],
    }
    for month, rent in ((9, 0), (10, 6000), (11, 6000), (12, 0)):
        covered["oracles"].append(_oracle("CAPEX", _month(28, month, 88), rent,
                                           "Échéances du contrat : novembre et décembre uniquement."))
    for month, maintenance, insurance in ((10, 0, 0), (11, 0, 0), (12, 120, 60),
                                           (13, 120, 60), (14, 120, 60), (15, 0, 0)):
        for row, expected in ((19, maintenance), (21, insurance)):
            covered["oracles"].append(_oracle("Charges_Externes", _month(16, month, row), expected,
                "Facturation mensuelle hors couverture, jusqu'au dernier mois d'utilisation inclus."))

    payment = lease_payment(12000, 0.12, 12)
    interest = {
        "id": "assets_lease_positive_rate", "title": "Intérêts inclus dans un loyer sans double compte",
        "events": [
            "Machine de 12 000 euros, bail du 1er janvier au 31 décembre 2026, douze paiements constants à terme échu.",
            "Taux nominal annuel 12 %, soit 1 % par mois sur le solde avant paiement ; aucun frais ni option de rachat.",
            "Entretien et assurance inclus ; fin d'utilisation le 31 décembre. Aucun emprunt supplémentaire ni actif payé comptant.",
            "L'échéance attendue rembourse un solde de 12 000 euros par douze opérations intérêt puis paiement ; aucun arrondi intermédiaire.",
        ],
        "updates": _neutral_scenario() + _asset(start="2026-01-01", months=12, rate=0.12,
                       stop="2026-12-31") + _service_costs(),
        "oracles": _no_asset_double_count() + [
            _oracle("CAPEX", "M13", payment, "Paiement constant calculé par extinction du solde, indépendamment d'Excel."),
            _oracle("CAPEX", "P81", payment * 12, "Douze loyers, intérêts inclus dans chaque paiement."),
            _oracle("CAPEX", "AN88", 0, "Aucun treizième paiement en janvier 2027."),
            _oracle("Modèle financier", "C138", payment * 12, "Total des loyers comptabilisé une seule fois."),
            _oracle("Modèle financier", "C319", 0, "Aucun intérêt de dette distinct des loyers."),
            _oracle("Compte de Résultat", "D71", 0, "Le bien loué ne génère pas de dotation dans cette convention."),
        ],
    }
    minimum = {
        "id": "assets_lease_one_month_horizon", "title": "Un mois de bail au dernier mois de l'horizon",
        "events": [
            "Bail fictif d'un seul mois, décembre 2028, dernière année du plan de trois ans commencé en 2026.",
            "Machine de 900 euros, taux nul, utilisation du 1er au 31 décembre 2028 ; services inclus.",
            "Un paiement de 900 euros en décembre et aucun paiement en novembre 2028 ou janvier 2029.",
        ],
        "updates": _neutral_scenario() + _asset(amount=900, start="2028-12-01", months=1,
                       stop="2028-12-31") + _service_costs(),
        "oracles": _no_asset_double_count() + [
            _oracle("CAPEX", "P81", 0, "Aucun bail avant décembre 2028."),
            _oracle("CAPEX", "Q81", 0, "Aucun bail en 2027."),
            _oracle("CAPEX", "R81", 900, "Une échéance au dernier mois de l'horizon."),
            _oracle("CAPEX", _month(28, 34, 88), 0, "Novembre : le contrat n'a pas commencé."),
            _oracle("CAPEX", _month(28, 35, 88), 900, "Décembre : unique mois contractuel."),
            _oracle("CAPEX", _month(28, 36, 88), 0, "Janvier suivant : le contrat est terminé, même sur la grille technique."),
        ],
    }
    awarded = {
        "id": "assets_grants_awarded_vs_base", "title": "Montant accordé et assiette : deux aides indépendantes",
        "events": [
            "Aide A fictive déjà accordée : 120 000 euros. La notification mentionne un programme à 40 %, mais le montant accordé est déjà net de ce calcul.",
            "Aide B indépendante : assiette éligible de 300 000 euros et taux de 40 %, soit également 120 000 euros.",
            "Les deux aides sont intégralement payées en janvier 2026 et reprises linéairement sur 36 mois à compter du 1er janvier.",
            "Encoder A avec montant support 120 000 et multiplicateur 1 ; B avec assiette 300 000 et multiplicateur 0,4. Total encaissé 240 000, reprise annuelle totale 80 000.",
        ],
        "updates": _neutral_scenario() + _grant(title="Aide A déjà accordée fictive")
                   + _grant(row=4, support=300000, rate=0.4, title="Aide B assiette distincte fictive"),
        "oracles": [
            _oracle("SUBVENTION_INVEST", "N3", 120000, "Montant accordé A non réduit une seconde fois par 40 %."),
            _oracle("SUBVENTION_INVEST", "N4", 120000, "Assiette B indépendante : 300 000 × 40 %."),
            _oracle("SUBVENTION_INVEST", "N24", 240000, "Deux notifications distinctes de 120 000 euros."),
            _oracle("Modèle financier", "C297", 240000, "Encaissement exact des deux aides d'investissement."),
            _oracle("SUBVENTION_INVEST", "N48", 80000, "Deux reprises annuelles de 40 000 euros."),
            _oracle("SUBVENTION_INVEST", "O48", 80000, "Deuxième année de reprise."),
            _oracle("SUBVENTION_INVEST", "P48", 80000, "Troisième et dernière année de reprise."),
            _oracle("SUBVENTION_INVEST", "N72", 160000, "240 000 reçus moins 80 000 repris à fin 2026."),
            _oracle("SUBVENTION_INVEST", "O72", 80000, "Solde à reprendre après deux années."),
            _oracle("SUBVENTION_INVEST", "P72", 0, "Les deux aides sont entièrement reprises à fin 2028."),
            _oracle("Compte de Résultat", "D71", 80000, "Reprise des aides au résultat, aucune dotation d'actif dans cette fixture."),
            _oracle("SUBVENTION_INVEST", _month(25, 36, 48), 0, "Pas de quatrième année de reprise."),
        ],
    }
    tranches = {
        "id": "assets_grant_delayed_tranches", "title": "Aide payée par tranches et plafond de reprise",
        "events": [
            "Aide fictive déjà accordée de 120 000 euros, paiement de 25 % le 15 mars 2026 et de 75 % le 15 janvier 2027.",
            "Convention de recette : reprise théorique de 5 000 euros par mois de janvier 2026 à décembre 2027, limitée au cash reçu cumulé.",
            "Janvier-février 2026 : zéro reçu et zéro reprise. Mars : reçu 30 000, rattrapage de reprise de 15 000. Avril à juin : 5 000/mois, puis plafond atteint.",
            "Janvier 2027 : encaissement 90 000 et reprise de 35 000 pour rattraper le calendrier. Février à décembre : 5 000/mois. Reprises annuelles 30 000 puis 90 000.",
        ],
        "updates": _neutral_scenario() + _grant(years=2, deposit=0.25, deposit_date="2026-03-15",
                    balance=0.75, balance_date="2027-01-15"),
        "oracles": [
            _oracle("SUBVENTION_INVEST", "N24", 30000, "Première tranche 120 000 × 25 %."),
            _oracle("SUBVENTION_INVEST", "O24", 90000, "Solde accordé 120 000 × 75 %."),
            _oracle("SUBVENTION_INVEST", "N48", 30000, "Reprise limitée à la première tranche reçue."),
            _oracle("SUBVENTION_INVEST", "O48", 90000, "Rattrapage 35 000 plus onze mois de 5 000."),
            _oracle("SUBVENTION_INVEST", "P48", 0, "La durée de 24 mois est terminée."),
            _oracle("Modèle financier", "C297", 30000, "Cash d'investissement 2026, indépendant de la reprise au résultat."),
            _oracle("Modèle financier", "D297", 90000, "Cash du solde en 2027."),
        ],
    }
    for month, release, residual in ((0, 0, 0), (1, 0, 0), (2, 15000, 15000),
                                       (3, 5000, 10000), (5, 5000, 0), (6, 0, 0),
                                       (11, 0, 0), (12, 35000, 55000), (23, 5000, 0), (24, 0, 0)):
        tranches["oracles"] += [
            _oracle("SUBVENTION_INVEST", _month(25, month, 27), release,
                    "Reprise mensuelle selon le calendrier indépendant et le plafond d'encaissement."),
            _oracle("SUBVENTION_INVEST", _month(25, month, 51), residual,
                    "Solde reçu mais non encore repris à la clôture du mois."),
        ]
    grant_minimum = {
        "id": "assets_grant_one_month_horizon", "title": "Aide reprise sur un mois à la borne de l'horizon",
        "events": [
            "Aide accordée fictive de 1 200 euros reçue le 31 décembre 2028, affectée conventionnellement à décembre 2028.",
            "Reprise d'un mois à partir du 1er décembre 2028 ; dates regroupées par mois, sans prorata journalier.",
            "Décembre porte 1 200 euros de cash et de reprise ; rien en novembre ou janvier suivant. Le 31 décembre reste dans la troisième année.",
        ],
        "updates": _neutral_scenario() + _grant(support=1200, years=1 / 12,
                       deposit_date="2028-12-31", recognition_start="2028-12-01"),
        "oracles": [
            _oracle("SUBVENTION_INVEST", "N24", 0, "Pas de paiement en 2026."),
            _oracle("SUBVENTION_INVEST", "O24", 0, "Pas de paiement en 2027."),
            _oracle("SUBVENTION_INVEST", "P24", 1200, "Le dernier jour de 2028 appartient au dernier mois actif."),
            _oracle("SUBVENTION_INVEST", "P48", 1200, "Une reprise d'un mois exactement."),
            _oracle("SUBVENTION_INVEST", "P72", 0, "Aucun solde après la reprise intégrale."),
            _oracle("SUBVENTION_INVEST", _month(25, 34, 27), 0, "Aucune reprise avant décembre."),
            _oracle("SUBVENTION_INVEST", _month(25, 35, 27), 1200, "Décembre porte toute la reprise."),
            _oracle("SUBVENTION_INVEST", _month(25, 36, 27), 0, "Aucun second mois de reprise."),
        ],
    }
    operating = {
        "id": "assets_operating_grant_awarded", "title": "Aide d'exploitation accordée sans nouveau taux",
        "events": [
            "Notification fictive d'une aide d'exploitation de 30 000 euros, versée le 15 juillet 2026.",
            "Le montant est déjà accordé ; aucun nouveau pourcentage n'est appliqué et aucune part R&D n'est attribuée.",
            "L'aide est enregistrée une seule fois dans DATA Financement, sans double saisie dans les aides d'investissement.",
            "Attendu : 30 000 euros de produit d'exploitation et de cash en juillet/2026, zéro aide d'investissement et zéro en 2027.",
        ],
        "updates": _neutral_scenario() + _updates("DATA Financement", {
            "B14": "Aide exploitation fictive", "C14": "SUBVENTION EXPLOITATION", "D14": 30000,
            "E14": "2026-07-15", "G14": 0, "H14": "Montant déjà accordé de recette, aucune aide réelle"}),
        "oracles": [
            _oracle("Financement E&S", "D12", 30000, "Le registre totalise le montant déjà accordé une seule fois."),
            _oracle("Modèle financier", "C294", 30000, "Ligne issue du registre de financement."),
            _oracle("Modèle financier", "C293", 30000, "Total cash d'aide d'exploitation, sans autre aide."),
            _oracle("Modèle financier", "D293", 0, "Versement unique en 2026."),
            _oracle("Modèle financier", _month(20, 5, 293), 0, "Juin : aucun versement."),
            _oracle("Modèle financier", _month(20, 6, 293), 30000, "Juillet : date effective de réception."),
            _oracle("Modèle financier", _month(20, 7, 293), 0, "Août : aucun doublon de paiement."),
            _oracle("Compte de Résultat", "D67", 30000, "Produit d'exploitation de la seule aide reçue."),
            _oracle("Modèle financier", "C297", 0, "Une aide d'exploitation ne crée pas d'encaissement d'aide d'investissement."),
            _oracle("SUBVENTION_INVEST", "N48", 0, "Aucune reprise d'aide d'investissement pour ce registre."),
        ],
    }
    return [covered, interest, minimum, awarded, tranches, grant_minimum, operating]


def rejection_cases() -> list[dict]:
    """Mutations invalides à préparer sur une trame neuve, jamais à appliquer.

    Chaque objet fournit un lot complet modifié ; un runner exige ValueError,
    aucune publication de version et aucun changement de SHA de la source.
    Les mois fractionnaires de reprise d'aide ne sont pas présentés comme refus
    garanti : cette contrainte n'existe actuellement que pour le crédit-bail.
    """
    originals = {case["id"]: case for case in cases()}
    mutations = [
        ("lease_zero_duration", "assets_lease_services_end", "DATA CAPEX", "J13", 0, "Durée du bail strictement positive."),
        ("lease_fractional_month", "assets_lease_services_end", "DATA CAPEX", "J13", 0.1, "1,2 mois n'est pas une durée contractuelle en mois entiers."),
        ("lease_negative_rate", "assets_lease_services_end", "DATA CAPEX", "K13", -0.01, "Le taux nominal négatif sort du contrat de cette trame."),
        ("lease_end_before_start", "assets_lease_services_end", "DATA CAPEX", "P13", "2026-10-31", "Fin d'utilisation antérieure au début du bail."),
        ("grant_zero_duration", "assets_grant_delayed_tranches", "SUBVENTION_INVEST", "E3", 0, "La durée de reprise doit être strictement positive."),
        ("grant_tranches_above_award", "assets_grant_delayed_tranches", "SUBVENTION_INVEST", "I3", 0.8, "25 % plus 80 % dépasse le montant accordé."),
        ("grant_positive_tranche_without_date", "assets_grant_delayed_tranches", "SUBVENTION_INVEST", "J3", None, "Le versement positif de 75 % exige une date explicite."),
        ("grant_rate_above_one", "assets_grants_awarded_vs_base", "SUBVENTION_INVEST", "D3", 1.01, "Le taux appliqué au montant support ne peut pas dépasser 100 %."),
    ]
    result = []
    error_fragments = {
        "lease_zero_duration": ["borne exclusive : DATA CAPEX!J13"],
        "lease_fractional_month": ["nombre entier de mois : DATA CAPEX!J13"],
        "lease_negative_rate": ["minimum : DATA CAPEX!K13"],
        "lease_end_before_start": ["operating_end_before_start", "fin antérieure au début"],
        "grant_zero_duration": ["borne exclusive : SUBVENTION_INVEST!E3"],
        "grant_tranches_above_award": ["acompte + solde doivent faire 100 %"],
        "grant_positive_tranche_without_date": ["date J manquante"],
        "grant_rate_above_one": ["maximum : SUBVENTION_INVEST!D3"],
    }
    for key, original, sheet, cell, value, reason in mutations:
        updates = copy.deepcopy(originals[original]["updates"])
        matches = [update for update in updates if (update["sheet"], update["cell"]) == (sheet, cell)]
        if len(matches) != 1:
            raise ValueError("Mutation de recette absente ou ambiguë.")
        matches[0]["value"] = value
        result.append({"id": "assets_reject_" + key, "title": reason,
                       "events": originals[original]["events"] + [reason],
                       "updates": updates, "expected_exception": "ValueError",
                       "expected_error_any": error_fragments[key],
                       "reason": reason, "mutation": {"sheet": sheet, "cell": cell, "value": value}})
    return result
