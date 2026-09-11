# Assumptions

Responsabilité : **Qualifier les offres, prix, volumes, capacités et hypothèses communes.**

Contrat : `AGENT_04`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Est-ce une offre active ou un module explicitement inactif ?
- Quels prix, volumes et capacités sont justifiés pour chaque exercice ?

## Règles et contrôles métier

- Préserver les identifiants techniques.
- Un objectif annuel ne constitue pas un contrat signé.

## Dépendances

Sources métier du contrat : Control.

Sources directes extraites : Control, DATA COGS, Revenue.

Feuilles qui consomment directement cette feuille : ATELIER_CIR_IS, BFR, Bilan, CALCUL_CIR, COGS, Charges_Externes, Contrats, Control, Contrôles, DATA CAPEX, DATA COGS, DATA Contrats, DATA Financement, Effectifs, Financement E&S, KPI Dashboard, Modèle financier, Revenue, Sensi TCA.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Inflation générale annuelle

Identifiant : `inflation_general`. Type : `number`. Zones : `D4`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Variation annuelle des assiettes indexées sur l’inflation générale.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

### Indexation annuelle des prix de vente

Identifiant : `inflation_price`. Type : `number`. Zones : `D5`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Variation annuelle des prix unitaires ; défaut année suivante = prix précédent × (1+taux).

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

### Délai clients industriels de référence

Identifiant : `industrial_receivable_days`. Type : `number`. Zones : `D6`.

Unité explicite : jours conventionnels.

Assiette : Durée de crédit client de référence industrielle.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : conventional_month_days.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Réduction annuelle des coûts directs de transformation

Identifiant : `transformation_cost_reduction`. Type : `number`. Zones : `D7`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Réduction annuelle des composantes de transformation, distincte de l’inflation générale.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Inflation salariale annuelle

Identifiant : `inflation_salary`. Type : `number`. Zones : `D66`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Variation annuelle du salaire brut de référence A1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

### Taux indicatif de charges patronales

Identifiant : `employer_charge_reference`. Type : `number`. Zones : `D67`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Charges patronales divisées par salaire brut ; barème indicatif, pas qualification sociale.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : employee_salary.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Une valeur de référence ne confirme pas le taux applicable à un poste.

Contraintes : `{"min": 0}`.

Référence indicative : les taux individuels Effectifs!J17:J116 sont des saisies indépendantes.

### Effectif cible à terme du plan

Identifiant : `headcount_target`. Type : `number`. Zones : `D90`.

Unité explicite : personnes cibles.

Assiette : Indicateur d’effectif visé ; ne crée aucune ligne ni calendrier de recrutement.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Changer la cible ne crée ni ne supprime de postes. Statut et source historiques non jaunes ne sont pas inclus dans cette liste blanche.

### Trésorerie d’ouverture du modèle

Identifiant : `opening_cash`. Type : `number`. Zones : `D126`.

Unité explicite : EUR.

Assiette : Solde de trésorerie au début du modèle, séparé des apports futurs.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Peut être négative. Ne pas créer une contrepartie comptable arbitraire pour équilibrer le bilan.

### Libellé de l’offre

Identifiant : `offer_label`. Type : `text`. Zones : `B15:B27`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Libellé affiché ; identifiant technique OFFRE stable conservé séparément.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Identifiant A fixe et interdit. Renommer une offre déjà utilisée nécessite la mise à jour coordonnée des libellés DATA Contrats!C, après analyse des dépendances. Ne pas renommer silencieusement.

### Offre active

Identifiant : `offer_active`. Type : `integer`. Zones : `C15:C27`.

Unité explicite : indicateur entier 0 ou 1.

Assiette : Activation technique de la ligne d’offre ; 0 est un choix explicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": [0, 1]}`.

Choix du catalogue : [0, 1].

### Unité

Identifiant : `offer_unit`. Type : `enum`. Zones : `D15:D27`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Dimension commerciale propre à l’offre, reprise par quantités et prix.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_label.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["unité", "vol", "forfait", "unite"]}`.

Choix du catalogue : ["unité", "vol", "forfait", "unite"].

### Inclure au chiffre d’affaires

Identifiant : `offer_in_revenue`. Type : `enum`. Zones : `E15:E27`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Inclusion de l’offre dans le CA ; ne remplace pas le mode de reconnaissance.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non"]}`.

Choix du catalogue : ["Oui", "Non"].

OFFRE_08 est hors CA : utiliser le registre de financement pour les subventions.

### Prix de vente A1

Identifiant : `offer_price_2026`. Type : `number`. Zones : `F15:F27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Le forfait du plan utilise une convention de volume en euros avec prix unitaire 1. Ne pas transposer automatiquement cette convention au montant d’un contrat identifié.

### Prix de vente A2–A5

Identifiant : `offer_price_2027_2030`. Type : `number`. Zones : `G15:J27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["G15", "H15", "I15", "J15", "G16", "H16", "I16", "J16", "G17", "H17", "I17", "J17", "G18", "H18", "I18", "J18", "G19", "H19", "I19", "J19", "G20", "H20", "I20", "J20", "G21", "H21", "I21", "J21", "G22", "H22", "I22", "J22", "G23", "H23", "I23", "J23", "G24", "H24", "I24", "J24", "G25", "H25", "I25", "J25", "G26", "H26", "I26", "J26", "G27", "H27", "I27", "J27"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `G15` : `F15*(1+$D$5)`
  Sources extraites : 'Assumptions'!F15, 'Assumptions'!$D$5.
- `H15` : `G15*(1+$D$5)`
- `I15` : `H15*(1+$D$5)`
- `J15` : `I15*(1+$D$5)`
- `G16` : `F16*(1+$D$5)`
- `H16` : `G16*(1+$D$5)`
- `I16` : `H16*(1+$D$5)`
- `J16` : `I16*(1+$D$5)`
- `G17` : `F17*(1+$D$5)`
- `H17` : `G17*(1+$D$5)`
- `I17` : `H17*(1+$D$5)`
- `J17` : `I17*(1+$D$5)`
- `G18` : `F18*(1+$D$5)`
- `H18` : `G18*(1+$D$5)`
- `I18` : `H18*(1+$D$5)`
- `J18` : `I18*(1+$D$5)`
- `G19` : `F19*(1+$D$5)`
- `H19` : `G19*(1+$D$5)`
- `I19` : `H19*(1+$D$5)`
- `J19` : `I19*(1+$D$5)`
- `G20` : `F20*(1+$D$5)`
- `H20` : `G20*(1+$D$5)`
- `I20` : `H20*(1+$D$5)`
- `J20` : `I20*(1+$D$5)`
- `G21` : `F21*(1+$D$5)`
- `H21` : `G21*(1+$D$5)`
- `I21` : `H21*(1+$D$5)`
- `J21` : `I21*(1+$D$5)`
- `G22` : `F22*(1+$D$5)`
- `H22` : `G22*(1+$D$5)`
- `I22` : `H22*(1+$D$5)`
- `J22` : `I22*(1+$D$5)`
- `G23` : `F23*(1+$D$5)`
- `H23` : `G23*(1+$D$5)`
- `I23` : `H23*(1+$D$5)`
- `J23` : `I23*(1+$D$5)`
- `G24` : `F24*(1+$D$5)`
- `H24` : `G24*(1+$D$5)`
- `I24` : `H24*(1+$D$5)`
- `J24` : `I24*(1+$D$5)`
- `G25` : `F25*(1+$D$5)`
- `H25` : `G25*(1+$D$5)`
- `I25` : `H25*(1+$D$5)`
- `J25` : `I25*(1+$D$5)`
- `G26` : `F26*(1+$D$5)`
- `H26` : `G26*(1+$D$5)`
- `I26` : `H26*(1+$D$5)`
- `J26` : `I26*(1+$D$5)`
- `G27` : `F27*(1+$D$5)`
- `H27` : `G27*(1+$D$5)`
- `I27` : `H27*(1+$D$5)`
- `J27` : `I27*(1+$D$5)`

Défaut : prix de l’année précédente × (1+Assumptions!D5). Remplacement littéral seulement sur instruction/source métier précise ; journaliser la formule d’origine.

### Volume plan A1

Identifiant : `offer_volume_2026`. Type : `number`. Zones : `K15:K27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Commandes/demande du plan ; ne constitue pas une preuve de livraison.

### Volume plan A2

Identifiant : `offer_volume_2027`. Type : `number`. Zones : `L15:L27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Commandes/demande du plan ; ne constitue pas une preuve de livraison.

### Volume plan A3

Identifiant : `offer_volume_2028`. Type : `number`. Zones : `M15:M27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Commandes/demande du plan ; ne constitue pas une preuve de livraison.

### Volume plan A4

Identifiant : `offer_volume_2029`. Type : `number`. Zones : `N15:N27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Commandes/demande du plan ; ne constitue pas une preuve de livraison.

### Volume plan A5

Identifiant : `offer_volume_2030`. Type : `number`. Zones : `O15:O27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Commandes/demande du plan ; ne constitue pas une preuve de livraison.

### Capacité industrielle A1

Identifiant : `offer_capacity_2026`. Type : `number`. Zones : `P15:P27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0}`.

0 signifie aucune contrainte de capacité.

### Capacité industrielle A2

Identifiant : `offer_capacity_2027`. Type : `number`. Zones : `Q15:Q27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0}`.

0 signifie aucune contrainte de capacité.

### Capacité industrielle A3

Identifiant : `offer_capacity_2028`. Type : `number`. Zones : `R15:R27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0}`.

0 signifie aucune contrainte de capacité.

### Capacité industrielle A4

Identifiant : `offer_capacity_2029`. Type : `number`. Zones : `S15:S27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0}`.

0 signifie aucune contrainte de capacité.

### Capacité industrielle A5

Identifiant : `offer_capacity_2030`. Type : `number`. Zones : `T15:T27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0}`.

0 signifie aucune contrainte de capacité.

### Délai d’encaissement clients

Identifiant : `offer_payment_days`. Type : `number`. Zones : `U15:U27`.

Unité explicite : jours conventionnels.

Assiette : Délai d’encaissement des factures de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit, conventional_month_days.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Acompte

Identifiant : `offer_deposit_rate`. Type : `number`. Zones : `V15:V27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part du montant HT facturé ; acompte + jalon + solde doivent former le total.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

V + X + Z doit valoir 1, tolérance 0,0001. AA est calculée et interdite.

### Acompte : anticipation

Identifiant : `offer_deposit_lead`. Type : `integer`. Zones : `W15:W27`.

Unité explicite : mois calendaires.

Assiette : Anticipation de l’acompte ou du jalon avant le solde ; pas un délai en jours.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

V + X + Z doit valoir 1, tolérance 0,0001. AA est calculée et interdite.

### Jalon

Identifiant : `offer_milestone_rate`. Type : `number`. Zones : `X15:X27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part du montant HT facturé ; acompte + jalon + solde doivent former le total.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

V + X + Z doit valoir 1, tolérance 0,0001. AA est calculée et interdite.

### Jalon : anticipation

Identifiant : `offer_milestone_lead`. Type : `integer`. Zones : `Y15:Y27`.

Unité explicite : mois calendaires.

Assiette : Anticipation de l’acompte ou du jalon avant le solde ; pas un délai en jours.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

V + X + Z doit valoir 1, tolérance 0,0001. AA est calculée et interdite.

### Solde

Identifiant : `offer_balance_rate`. Type : `number`. Zones : `Z15:Z27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part du montant HT facturé ; acompte + jalon + solde doivent former le total.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

V + X + Z doit valoir 1, tolérance 0,0001. AA est calculée et interdite.

### Statut / qualité de l’hypothèse

Identifiant : `offer_status_source`. Type : `text`. Zones : `AD15:AD27`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Qualité et provenance commerciales de l’hypothèse d’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_label.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Le texte documentaire ne remplace pas les états et pièces du service.

### Source commerciale

Identifiant : `offer_source`. Type : `text`. Zones : `AE15:AE27`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Qualité et provenance commerciales de l’hypothèse d’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_label.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Le texte documentaire ne remplace pas les états et pièces du service.

### price A6

Identifiant : `offer_price_2031`. Type : `number`. Zones : `AF15:AF27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### price A7

Identifiant : `offer_price_2032`. Type : `number`. Zones : `AG15:AG27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### price A8

Identifiant : `offer_price_2033`. Type : `number`. Zones : `AH15:AH27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### price A9

Identifiant : `offer_price_2034`. Type : `number`. Zones : `AI15:AI27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### price A10

Identifiant : `offer_price_2035`. Type : `number`. Zones : `AJ15:AJ27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, inflation_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### volume A6

Identifiant : `offer_volume_2031`. Type : `number`. Zones : `AK15:AK27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### volume A7

Identifiant : `offer_volume_2032`. Type : `number`. Zones : `AL15:AL27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### volume A8

Identifiant : `offer_volume_2033`. Type : `number`. Zones : `AM15:AM27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### volume A9

Identifiant : `offer_volume_2034`. Type : `number`. Zones : `AN15:AN27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### volume A10

Identifiant : `offer_volume_2035`. Type : `number`. Zones : `AO15:AO27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Objectif commercial annuel ; ne constitue pas une commande signée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.

### capacity A6

Identifiant : `offer_capacity_2031`. Type : `number`. Zones : `AP15:AP27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.
0 signifie aucune contrainte de capacité.

### capacity A7

Identifiant : `offer_capacity_2032`. Type : `number`. Zones : `AQ15:AQ27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.
0 signifie aucune contrainte de capacité.

### capacity A8

Identifiant : `offer_capacity_2033`. Type : `number`. Zones : `AR15:AR27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.
0 signifie aucune contrainte de capacité.

### capacity A9

Identifiant : `offer_capacity_2034`. Type : `number`. Zones : `AS15:AS27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.
0 signifie aucune contrainte de capacité.

### capacity A10

Identifiant : `offer_capacity_2035`. Type : `number`. Zones : `AT15:AT27`.

Unité explicite : unité de l’offre désignée par offer_unit par exercice.

Assiette : Capacité industrielle annuelle de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, industrial_capacity_factor.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1000000000000.0}, "choices": null}`.

Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.

Contraintes : `{"min": 0, "max": 1000000000000.0}`.

À documenter et valider pour le dossier courant.
0 signifie aucune contrainte de capacité.

### CIR : taux - part <= 100 M EUR

Identifiant : `assumptions_d68`. Type : `number`. Zones : `D68`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux CIR de la tranche d’assiette désignée par la carte ; aucune validité légale universelle.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CIR : taux - part > 100 M EUR

Identifiant : `assumptions_d69`. Type : `number`. Zones : `D69`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux CIR de la tranche d’assiette désignée par la carte ; aucune validité légale universelle.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CIR : forfait fonctionnement, % des depenses de personnel

Identifiant : `assumptions_d70`. Type : `number`. Zones : `D70`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Forfait de fonctionnement appliqué aux dépenses de personnel R&D qualifiées.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : employee_rnd_share.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CIR : forfait fonctionnement, % des amortissements

Identifiant : `assumptions_d71`. Type : `number`. Zones : `D71`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Forfait de fonctionnement appliqué aux amortissements R&D qualifiés.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : data_capex_h13_h72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CIR : sous-traitance, plafond en multiple des autres depenses

Identifiant : `assumptions_d72`. Type : `number`. Zones : `D72`.

Unité explicite : multiple sans dimension.

Assiette : Plafond de sous-traitance par rapport aux autres dépenses R&D ; pas un pourcentage.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : calcul_cir_c18_m18.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### CIR : sous-traitance, plafond global

Identifiant : `assumptions_d73`. Type : `number`. Zones : `D73`.

Unité explicite : EUR par exercice.

Assiette : Plafond global de dépenses de sous-traitance retenues dans l’assiette CIR.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : calcul_cir_c18_m18.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### CIR : frais de normalisation, part eligible

Identifiant : `assumptions_d74`. Type : `number`. Zones : `D74`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Fraction éligible des frais de normalisation documentés.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : calcul_cir_c19_m19.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CIR : delai de remboursement

Identifiant : `assumptions_d75`. Type : `integer`. Zones : `D75`.

Unité explicite : années de délai.

Assiette : Décalage annuel du remboursement CIR ; distinct du numéro du mois d’encaissement.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### CIR : mois d encaissement du remboursement

Identifiant : `assumptions_d76`. Type : `integer`. Zones : `D76`.

Unité explicite : numéro de mois 1 à 12.

Assiette : Mois du remboursement CIR dans l’année retenue après délai.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : assumptions_d75.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 1, "max": 12}, "choices": null}`.

Contraintes : `{"min": 1, "max": 12}`.

### IS : seuil du taux reduit PME

Identifiant : `assumptions_d77`. Type : `number`. Zones : `D77`.

Unité explicite : EUR de base imposable par exercice.

Assiette : Seuil de bénéfice concerné par le taux réduit d’IS ; qualification capital/détention distincte.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : atelier_cir_is_c66_m66.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### IS : taux reduit sous le seuil

Identifiant : `assumptions_d78`. Type : `number`. Zones : `D78`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux d’IS de la tranche désignée ; régime et période doivent être qualifiés.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : atelier_cir_is_c66_m66, assumptions_d77.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### IS : taux normal

Identifiant : `assumptions_d79`. Type : `number`. Zones : `D79`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux d’IS de la tranche désignée ; régime et période doivent être qualifiés.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : atelier_cir_is_c66_m66, assumptions_d77.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Taux TVA achats/fournisseurs (libellé historique ventes/achats trop large)

Identifiant : `assumptions_d83`. Type : `number`. Zones : `D83`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : TVA sur achats/fournisseurs HT ; la TVA collectée par offre possède d’autres propriétaires.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### C3S : abattement d assiette

Identifiant : `assumptions_d84`. Type : `number`. Zones : `D84`.

Unité explicite : EUR de chiffre d’affaires.

Assiette : Abattement de base C3S ; valeur sourcée pour période applicable.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### C3S : taux

Identifiant : `assumptions_d85`. Type : `number`. Zones : `D85`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux appliqué à la base C3S après abattement.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : assumptions_d84.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CFE : cotisation minimum annuelle

Identifiant : `assumptions_d86`. Type : `number`. Zones : `D86`.

Unité explicite : EUR par exercice.

Assiette : Cotisation minimum CFE dans la formule conservée ; ne remplace pas la CFE saisie selon avis.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : atelier_cir_is_c91_m91.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### CFE : taux communal applique a la valeur locative

Identifiant : `assumptions_d87`. Type : `number`. Zones : `D87`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux CFE communal appliqué à la valeur locative de la formule conservée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### CVAE : seuil de CA déclenchant une cotisation (distinct du seuil déclaratif)

Identifiant : `assumptions_d88`. Type : `number`. Zones : `D88`.

Unité explicite : EUR de chiffre d’affaires.

Assiette : Seuil de déclenchement de cotisation CVAE implémenté ; distinct d’un seuil déclaratif.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : atelier_cir_is_c111_m111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Taux annuel de crédit-bail par défaut

Identifiant : `assumptions_d91`. Type : `number`. Zones : `D91`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel du crédit-bail, avant conversion au taux mensuel du moteur.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_i13_i72, data_capex_j13_j72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Part R&D de la subvention d'investissement (déduction CIR via la reprise)

Identifiant : `assumptions_d93`. Type : `number`. Zones : `D93`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part R&D de la reprise des aides d’investissement, pour déduction d’assiette CIR.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : subvention_invest_c3_c23, subvention_invest_d3_d23, subvention_invest_e3_e23.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Durées proposées par le catalogue CAPEX

Identifiant : `capex_catalog_years`. Type : `number`. Zones : `C98:C121`.

Unité explicite : années ; conversion en mois selon la règle du modèle.

Assiette : Durée d’amortissement ; un défaut de typologie doit rester explicite et remplaçable seulement sur justification.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_c13_c72, data_capex_e13_e72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Quote-part R&D proposée par le catalogue CAPEX

Identifiant : `capex_catalog_rd_share`. Type : `number`. Zones : `D98:D121`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Quote-part de l’actif affectée à R&D ; aucune éligibilité fiscale automatique.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_g13_g72, data_capex_c13_c72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Quote-part R&D par catégorie de financement

Identifiant : `financing_rd_default`. Type : `number`. Zones : `D130:D145`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part R&D d’une aide d’exploitation de la catégorie désignée ; utilisée pour déduction CIR.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_c14_c413, data_financement_d14_d413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Prix de la deuxième année — `Assumptions!G15`

Unité : EUR/unité. Défaut indexé sur le prix initial et l’inflation de prix ; remplacement seulement sourcé.

```text
F15*(1+$D$5)
```

Sources directes extraites : `'Assumptions'!F15`, `'Assumptions'!$D$5`.

### Écart échéancier offre — `Assumptions!AA15`

Unité : fraction. Acompte, jalon et solde doivent répartir le montant total.

```text
V15+X15+Z15-1
```

Sources directes extraites : `'Assumptions'!V15`, `'Assumptions'!X15`, `'Assumptions'!Z15`.

### Offres à échéancier incohérent — `Assumptions!D28`

Unité : nombre. Compte les répartitions dont l’écart dépasse la tolérance.

```text
SUMPRODUCT((ABS($AA$15:$AA$27)>0.0001)*1)
```

Sources directes extraites : `'Assumptions'!$AA$15:$AA$27`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_04 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Prix initial 100 EUR, inflation 2 %, acompte 20 %, jalon 30 %, solde 50 %.

Attendu : G15 vaut 102 ; AA15 vaut 0. Une répartition totalisant 90 % doit être signalée.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
