# Sensi Analyses

Responsabilité : **Expliquer les sensibilités natives et comparer leurs scénarios.**

Contrat : `AGENT_30`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quels axes et amplitudes de choc faut-il comparer ?

## Règles et contrôles métier

- La table native exige une preuve de recalcul propre.
- Comparer une cellule à un scénario scalaire indépendant.

## Dépendances

Sources métier du contrat : Sensi TCA, Valorisation.

Sources directes extraites : Compte de Résultat, Control, Flux de trésorerie, Sensi TCA.

Feuilles qui consomment directement cette feuille : Contrôles, Sensi Graphiques, Sensi TCA.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Choc d’analyse volume

Identifiant : `analysis_shock_volume`. Type : `number`. Zones : `F8`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur volumes ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse price

Identifiant : `analysis_shock_price`. Type : `number`. Zones : `F9`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur prix unitaires ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse direct_costs

Identifiant : `analysis_shock_direct_costs`. Type : `number`. Zones : `F10`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur coûts directs ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse external_costs

Identifiant : `analysis_shock_external_costs`. Type : `number`. Zones : `F11`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur charges externes ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse payroll

Identifiant : `analysis_shock_payroll`. Type : `number`. Zones : `F12`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur masse salariale ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse client_delay

Identifiant : `analysis_shock_client_delay`. Type : `number`. Zones : `F13`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur délai client ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse subsidies

Identifiant : `analysis_shock_subsidies`. Type : `number`. Zones : `F14`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur subventions ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Choc d’analyse capex

Identifiant : `analysis_shock_capex`. Type : `number`. Zones : `F15`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur investissements ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Paramètre de l’analyse de sensibilité ; ne pas le confondre avec une donnée opérationnelle.

### Retard de financement de l’analyse

Identifiant : `analysis_financing_delay`. Type : `integer`. Zones : `F16`.

Unité explicite : mois calendaires.

Assiette : Décalage des dates de financement, sans changer le montant acquis.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_e14_e413, active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Aucune validation Excel existante.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Choc combiné — `Sensi Analyses!E10`

Unité : fraction. Levier de base combiné au choc isolé de tornado.

```text
(1+C10)*(1+D10)-1
```

Sources directes extraites : `'Sensi Analyses'!C10`, `'Sensi Analyses'!D10`.

### Table tornado — `Sensi Analyses!D25`

Unité : sortie native. Ancre D25:G33 : ne pas confondre absence de formule textuelle et entrée saisissable.

Formule native de table : ses paramètres sont dans le composant Excel ; aucun texte scalaire n'est inventé.

### Table volume — `Sensi Analyses!C40`

Unité : sortie native. Ancre C40:D45, entrée C8.

Formule native de table : ses paramètres sont dans le composant Excel ; aucun texte scalaire n'est inventé.

### Table deux leviers — `Sensi Analyses!D50`

Unité : sortie native. Ancre D50:F52, entrées C14 et C8.

Formule native de table : ses paramètres sont dans le composant Excel ; aucun texte scalaire n'est inventé.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_30 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Choisir un choc volume et un couple volume/subvention ; recalculer chaque scénario scalaire sur copie dédiée.

Attendu : Chaque valeur native concorde au scalaire avec tolérance documentée ; restituer exactement les entrées initiales. Cas non exécuté par ces fiches.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
