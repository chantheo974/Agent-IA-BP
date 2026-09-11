"""Révision explicite des défauts fiscaux favorables du modèle hérité.

Ces gardes ne qualifient aucune éligibilité fiscale : elles rendent le calcul
indisponible lorsque la condition propriétaire manque ou reste à confirmer.
La réglementation et les sources restent à qualifier dans le dossier.
"""
from __future__ import annotations
import re


def guard_formula(sheet, address, formula):
    if sheet == 'ATELIER_CIR_IS':
        match = re.fullmatch(r'([C-M])(67|68|86|90)', address)
        if match:
            col, row = match.groups()
            if row == '67':
                expected = f'AND({col}80<=10000000,{col}66<>"Non")'
                replacement = f'IF({col}66="Oui",{col}80<=10000000,IF({col}66="Non",FALSE,NA()))'
            elif row == '86':
                expected = f'IF({col}85="Non",1,0)'
                replacement = f'IF({col}85="Non",1,IF({col}85="Oui",0,NA()))'
            elif row == '90':
                expected = (f'IF({col}85="À confirmer","À confirmer : taxe additionnelle omise comme historiquement ; potentiel "&TEXT({col}114,"0")&" EUR ; ventiler les autres loyers",'
                            '"Valider les loyers corporels > 6 mois et la VA fiscale")')
                replacement = (f'IF(OR({col}85="Oui",{col}85="Non"),"Valider les loyers corporels > 6 mois et la VA fiscale",'
                               '"NON_RENSEIGNE : qualifier le statut fiscal avant de calculer la taxe additionnelle")')
            else:
                expected = (f'IF(NOT(OR({col}66="Oui",{col}66="Non",{col}66="À confirmer")),"ERREUR : statut capital invalide",'
                            f'IF({col}66="À confirmer","À confirmer : capital/détention ; hypothèse historique conservée",'
                            f'IF({col}67,"Taux réduit admissible selon saisie","Taux normal")))')
                replacement = (f'IF(NOT(OR({col}66="Oui",{col}66="Non")),"NON_RENSEIGNE : qualifier capital et détention",'
                               f'IF({col}67,"Taux réduit admissible selon saisie qualifiée","Taux normal"))')
            if formula != expected:
                raise ValueError('Formule fiscale de référence inattendue : ' + sheet + '!' + address)
            # Les synthèses héritées utilisent SUMPRODUCT : zéro multiplié par
            # #N/A reste une erreur. Une année effectivement hors horizon est
            # inactive ; elle ne représente pas une qualification fiscale absente.
            # La borne vient du calendrier et de l'année de cette colonne.
            inactive = 'FALSE' if row == '67' else '0' if row == '86' else '"INACTIF_HORS_HORIZON"'
            calendar = ('AND(ISNUMBER(Control!$C$10),ISNUMBER(Control!$C$59),'
                        'Control!$C$59>=1,Control!$C$59<=10,ISNUMBER(Control!$C$60))')
            return f'IF({calendar},IF({col}$12>Control!$C$60,{inactive},{replacement}),NA())'
    if sheet == 'Valorisation' and address == 'D138':
        expected = 'IF(NOT(ISNUMBER(D115)),"IS manquant"'
        if formula.count(expected) != 1:
            raise ValueError('Garde IS du WACC différente de la référence attendue.')
        return formula.replace(expected, 'IF(NOT(ISNUMBER(D9)),"IS normatif DCF à renseigner"', 1)
    return formula


def remove_inherited_protection_credentials(raw):
    """Conserver les drapeaux de protection, retirer tout secret hérité.

    La nouvelle trame n'utilise pas de mot de passe de feuille. L'intégrité des
    fichiers gérés dépend du moteur et de leurs empreintes, pas d'un secret
    d'ouverture Excel. Aucun mot de passe source n'est décodé ou réemployé.
    """
    names = (b'password|algorithmName|hashValue|saltValue|spinCount|workbookPassword|revisionsPassword|'
             b'workbookAlgorithmName|workbookHashValue|workbookSaltValue|workbookSpinCount|'
             b'revisionsAlgorithmName|revisionsHashValue|revisionsSaltValue|revisionsSpinCount')
    def clean(match):
        return re.sub(rb'\s+(?:' + names + rb')="[^"]*"', b'', match[0])
    return re.sub(rb'<(?:\w+:)?(?:sheetProtection|workbookProtection)\b[^>]*>', clean, raw)
