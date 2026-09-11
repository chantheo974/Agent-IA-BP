# Charges_Externes

Responsabilité : **Qualifier les charges fixes, variables et services contractuels.**

Contrat : `AGENT_11`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Montant annuel fixe ou coût lié aux effectifs, volumes ou chiffre d'affaires ?
- Cette dépense est-elle déjà incluse dans un bail ou un autre poste ?

## Règles et contrôles métier

- Ne pas dupliquer les services inclus pendant un bail.
- Documenter assiette et indexation.

## Dépendances

Sources métier du contrat : Assumptions, Effectifs, DATA CAPEX.

Sources directes extraites : Assumptions, CAPEX, Control, DATA CAPEX, Modèle financier, Revenue, Stock.

Feuilles qui consomment directement cette feuille : Compte de Résultat, KPI Dashboard, Modèle financier.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Base annuelle fixe

Identifiant : `external_fixed`. Type : `number`. Zones : `E32:E44`.

Unité explicite : EUR HT par exercice de base.

Assiette : Base annuelle fixe de la nature de charges, avant indexation.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : inflation_general, external_local_inflation.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.

### Coût par ETP

Identifiant : `external_per_fte`. Type : `number`. Zones : `F32:F44`.

Unité explicite : EUR HT par ETP et par exercice de base.

Assiette : Coût appliqué aux ETP de l’exercice puis indexé.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : employee_fte, inflation_general, external_local_inflation.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.

### Coût par unité

Identifiant : `external_per_unit`. Type : `number`. Zones : `G32:G44`.

Unité explicite : EUR HT par unité produite.

Assiette : Coût appliqué à la production retenue par le modèle, puis indexé.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, inflation_general, external_local_inflation.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.
L’inducteur intitulé unités produites agrège Modèle financier lignes 5:9, donc la demande/commande retenue des cinq offres produit ; il ne prouve pas une livraison.

### Coût en part du CA

Identifiant : `external_revenue_share`. Type : `number`. Zones : `H32:H44`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part du CA dont l’assiette est choisie par external_revenue_base.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : external_revenue_base.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.

### Assiette du CA

Identifiant : `external_revenue_base`. Type : `enum`. Zones : `J32:J44`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Choix du CA reconnu ou de l’autre assiette nommée dans la validation du modèle.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : external_revenue_share.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["CA facture", "CA reconnu"]}`.

Choix du catalogue : ["CA facture", "CA reconnu"].

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.

### Coût en part des immobilisations brutes

Identifiant : `external_fixed_assets_share`. Type : `number`. Zones : `K32:K44`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part des immobilisations brutes retenues par la feuille de charges.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : data_capex_d13_d72, data_capex_i13_i72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.

### Coût en part des stocks

Identifiant : `external_stock_share`. Type : `number`. Zones : `L32:L44`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part de l’assiette de stock retenue par la feuille de charges.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : stock_coverage, opening_stock.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

13 natures fixes ; les différents inducteurs d’une ligne se cumulent.

### Inflation propre à la nature de charges

Identifiant : `external_local_inflation`. Type : `number`. Zones : `I36`, `I37`, `I44`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Indexation annuelle propre aux seules natures explicitement cartographiées.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Les autres I32:I44 sont des formules non jaunes liées à Assumptions!D4 et restent interdites.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Charge récurrente première catégorie — `Charges_Externes!E15`

Unité : EUR/an. Part fixe, ETP, surface, CA et autres assiettes ont des unités distinctes.

```text
($E32+$F32*E$10+$G32*E$12)*(1+$I32)^(E$5-$E$5)+$H32*IF($J32="CA reconnu",E$13,E$11)+$K32*E$47+$L32*E$48
```

Sources directes extraites : `'Charges_Externes'!$E32`, `'Charges_Externes'!$F32`, `'Charges_Externes'!E$10`, `'Charges_Externes'!$G32`, `'Charges_Externes'!E$12`, `'Charges_Externes'!$I32`, `'Charges_Externes'!E$5`, `'Charges_Externes'!$E$5`, `'Charges_Externes'!$H32`, `'Charges_Externes'!$J32`, `'Charges_Externes'!E$13`, `'Charges_Externes'!E$11`, `'Charges_Externes'!$K32`, `'Charges_Externes'!E$47`, `'Charges_Externes'!$L32`, `'Charges_Externes'!E$48`.

### Loyers de crédit-bail — `Charges_Externes!E28`

Unité : EUR/an. Relais du module CAPEX, sans ajouter un second décaissement d’actif Cash.

```text
CAPEX!P81
```

Sources directes extraites : `'CAPEX'!P81`.

### Total charges externes — `Charges_Externes!E29`

Unité : EUR/an. Somme des catégories et loyers ; vérifier couverture entretien/assurance.

```text
SUM(E15:E28)
```

Sources directes extraites : `'Charges_Externes'!E15:E28`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_11 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Charge fixe 1 200 EUR annuelle, toutes parts variables explicitement nulles ; puis fin d’une couverture entretien.

Attendu : Charge fixe 1 200 ; coût de service absent pendant couverture puis repris après, selon le contrat. Tester chaque mois frontière.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
