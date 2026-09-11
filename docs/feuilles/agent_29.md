# Sensi TCA

Responsabilité : **Préparer les scénarios et leurs leviers autorisés.**

Contrat : `AGENT_29`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel scénario et quels chocs explicitement choisis ?

## Règles et contrôles métier

- Conserver la composition des scénarios.
- Le décalage manuel se saisit dans le champ du catalogue, jamais dans un levier calculé.

## Dépendances

Sources métier du contrat : Assumptions, Control.

Sources directes extraites : Assumptions, Bilan, CALCUL_CIR, Compte de Résultat, Control, DATA Financement, Flux de trésorerie, Modèle financier, Sensi Analyses.

Feuilles qui consomment directement cette feuille : CAPEX, Contrats, Control, Contrôles, DATA Contrats, Effectifs, Financement E&S, KPI Dashboard, Modèle financier, SUBVENTION_INVEST, Sensi Analyses, Valorisation.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Scénario actif

Identifiant : `active_scenario`. Type : `enum`. Zones : `C15`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Preset ou scénario manuel ; le choix ne modifie pas les règles de composition.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Central", "Prudent", "Dégradé", "Sans subventions", "Choc combiné", "Manuel", "Sans equity"]}`.

Choix du catalogue : ["Central", "Prudent", "Dégradé", "Sans subventions", "Choc combiné", "Manuel", "Sans equity"].

### Choc manuel volume

Identifiant : `manual_shock_volume`. Type : `number`. Zones : `C77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur volumes ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel price

Identifiant : `manual_shock_price`. Type : `number`. Zones : `D77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur prix unitaires ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel direct_costs

Identifiant : `manual_shock_direct_costs`. Type : `number`. Zones : `E77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur coûts directs ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel external_costs

Identifiant : `manual_shock_external_costs`. Type : `number`. Zones : `F77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur charges externes ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel payroll

Identifiant : `manual_shock_payroll`. Type : `number`. Zones : `G77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur masse salariale ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel client_delay

Identifiant : `manual_shock_client_delay`. Type : `number`. Zones : `H77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur délai client ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel subsidies

Identifiant : `manual_shock_subsidies`. Type : `number`. Zones : `I77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur subventions ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Choc manuel capex

Identifiant : `manual_shock_capex`. Type : `number`. Zones : `J77`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif sur investissements ; composition multiplicative (1+a)×(1+b)−1.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Actif pour le scénario Manuel ; ne pas remettre à zéro les autres réglages sans demande.

### Retard de financement manuel

Identifiant : `manual_financing_delay`. Type : `integer`. Zones : `K77`.

Unité explicite : mois calendaires.

Assiette : Décalage des dates de financement, sans changer le montant acquis.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_e14_e413, active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Aucune validation Excel existante. Saisir des mois entiers de retard.

### Enveloppe Equity manuelle

Identifiant : `manual_equity_envelope`. Type : `number`. Zones : `C83`.

Unité explicite : EUR.

Assiette : Enveloppe d’equity du scénario manuel ; distincte de la trésorerie d’ouverture.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_scenario, data_financement_d14_d413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Appliquée seulement en scénario Manuel. 0 est une valeur valide. Une enveloppe positive nécessite des montants et dates Equity dans le registre pour être répartie. Sans equity coupe tous les apports Equity, fondateurs inclus ; cash initial, dette, CCA et subventions restent distincts.

### Choc de volume par offre / année A1–A10

Identifiant : `offer_volume_shock`. Type : `number`. Zones : `D40:M52`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif spécifique à l’offre et à l’exercice A1–A10 ; composition protégée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["D40", "E40", "F40", "G40", "H40", "I40", "J40", "K40", "L40", "M40", "D41", "E41", "F41", "G41", "H41", "I41", "J41", "K41", "L41", "M41", "D42", "E42", "F42", "G42", "H42", "I42", "J42", "K42", "L42", "M42", "D43", "E43", "F43", "G43", "H43", "I43", "J43", "K43", "L43", "M43", "D44", "E44", "F44", "G44", "H44", "I44", "J44", "K44", "L44", "M44", "D45", "E45", "F45", "G45", "H45", "I45", "J45", "K45", "L45", "M45", "D46", "E46", "F46", "G46", "H46", "I46", "J46", "K46", "L46", "M46", "D47", "E47", "F47", "G47", "H47", "I47", "J47", "K47", "L47", "M47", "D48", "E48", "F48", "G48", "H48", "I48", "J48", "K48", "L48", "M48", "D49", "E49", "F49", "G49", "H49", "I49", "J49", "K49", "L49", "M49", "D50", "E50", "F50", "G50", "H50", "I50", "J50", "K50", "L50", "M50", "D51", "E51", "F51", "G51", "H51", "I51", "J51", "K51", "L51", "M51", "D52", "E52", "F52", "G52", "H52", "I52", "J52", "K52", "L52", "M52"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `D40` : `$C$6`
- `E40` : `$C$6`
- `F40` : `$C$6`
- `G40` : `$C$6`
- `H40` : `$C$6`
- `I40` : `$C$6`
- `J40` : `$C$6`
- `K40` : `$C$6`
- `L40` : `$C$6`
- `M40` : `$C$6`
- `D41` : `$C$6`
- `E41` : `$C$6`
- `F41` : `$C$6`
- `G41` : `$C$6`
- `H41` : `$C$6`
- `I41` : `$C$6`
- `J41` : `$C$6`
- `K41` : `$C$6`
- `L41` : `$C$6`
- `M41` : `$C$6`
- `D42` : `$C$6`
- `E42` : `$C$6`
- `F42` : `$C$6`
- `G42` : `$C$6`
- `H42` : `$C$6`
- `I42` : `$C$6`
- `J42` : `$C$6`
- `K42` : `$C$6`
- `L42` : `$C$6`
- `M42` : `$C$6`
- `D43` : `$C$6`
- `E43` : `$C$6`
- `F43` : `$C$6`
- `G43` : `$C$6`
- `H43` : `$C$6`
- `I43` : `$C$6`
- `J43` : `$C$6`
- `K43` : `$C$6`
- `L43` : `$C$6`
- `M43` : `$C$6`
- `D44` : `$C$6`
- `E44` : `$C$6`
- `F44` : `$C$6`
- `G44` : `$C$6`
- `H44` : `$C$6`
- `I44` : `$C$6`
- `J44` : `$C$6`
- `K44` : `$C$6`
- `L44` : `$C$6`
- `M44` : `$C$6`
- `D45` : `$C$6`
- `E45` : `$C$6`
- `F45` : `$C$6`
- `G45` : `$C$6`
- `H45` : `$C$6`
- `I45` : `$C$6`
- `J45` : `$C$6`
- `K45` : `$C$6`
- `L45` : `$C$6`
- `M45` : `$C$6`
- `D46` : `$C$6`
- `E46` : `$C$6`
- `F46` : `$C$6`
- `G46` : `$C$6`
- `H46` : `$C$6`
- `I46` : `$C$6`
- `J46` : `$C$6`
- `K46` : `$C$6`
- `L46` : `$C$6`
- `M46` : `$C$6`
- `D47` : `$C$6`
- `E47` : `$C$6`
- `F47` : `$C$6`
- `G47` : `$C$6`
- `H47` : `$C$6`
- `I47` : `$C$6`
- `J47` : `$C$6`
- `K47` : `$C$6`
- `L47` : `$C$6`
- `M47` : `$C$6`
- `D48` : `$C$6`
- `E48` : `$C$6`
- `F48` : `$C$6`
- `G48` : `$C$6`
- `H48` : `$C$6`
- `I48` : `$C$6`
- `J48` : `$C$6`
- `K48` : `$C$6`
- `L48` : `$C$6`
- `M48` : `$C$6`
- `D49` : `$C$6`
- `E49` : `$C$6`
- `F49` : `$C$6`
- `G49` : `$C$6`
- `H49` : `$C$6`
- `I49` : `$C$6`
- `J49` : `$C$6`
- `K49` : `$C$6`
- `L49` : `$C$6`
- `M49` : `$C$6`
- `D50` : `$C$6`
- `E50` : `$C$6`
- `F50` : `$C$6`
- `G50` : `$C$6`
- `H50` : `$C$6`
- `I50` : `$C$6`
- `J50` : `$C$6`
- `K50` : `$C$6`
- `L50` : `$C$6`
- `M50` : `$C$6`
- `D51` : `$C$6`
- `E51` : `$C$6`
- `F51` : `$C$6`
- `G51` : `$C$6`
- `H51` : `$C$6`
- `I51` : `$C$6`
- `J51` : `$C$6`
- `K51` : `$C$6`
- `L51` : `$C$6`
- `M51` : `$C$6`
- `D52` : `$C$6`
- `E52` : `$C$6`
- `F52` : `$C$6`
- `G52` : `$C$6`
- `H52` : `$C$6`
- `I52` : `$C$6`
- `J52` : `$C$6`
- `K52` : `$C$6`
- `L52` : `$C$6`
- `M52` : `$C$6`

À documenter et valider pour le dossier courant.

### Choc de prix par offre / année A1–A10

Identifiant : `offer_price_shock`. Type : `number`. Zones : `D56:M68`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Choc relatif spécifique à l’offre et à l’exercice A1–A10 ; composition protégée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["D56", "E56", "F56", "G56", "H56", "I56", "J56", "K56", "L56", "M56", "D57", "E57", "F57", "G57", "H57", "I57", "J57", "K57", "L57", "M57", "D58", "E58", "F58", "G58", "H58", "I58", "J58", "K58", "L58", "M58", "D59", "E59", "F59", "G59", "H59", "I59", "J59", "K59", "L59", "M59", "D60", "E60", "F60", "G60", "H60", "I60", "J60", "K60", "L60", "M60", "D61", "E61", "F61", "G61", "H61", "I61", "J61", "K61", "L61", "M61", "D62", "E62", "F62", "G62", "H62", "I62", "J62", "K62", "L62", "M62", "D63", "E63", "F63", "G63", "H63", "I63", "J63", "K63", "L63", "M63", "D64", "E64", "F64", "G64", "H64", "I64", "J64", "K64", "L64", "M64", "D65", "E65", "F65", "G65", "H65", "I65", "J65", "K65", "L65", "M65", "D66", "E66", "F66", "G66", "H66", "I66", "J66", "K66", "L66", "M66", "D67", "E67", "F67", "G67", "H67", "I67", "J67", "K67", "L67", "M67", "D68", "E68", "F68", "G68", "H68", "I68", "J68", "K68", "L68", "M68"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": -1}, "choices": null}`.

Contraintes : `{"min": -1}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `D56` : `$C$7`
- `E56` : `$C$7`
- `F56` : `$C$7`
- `G56` : `$C$7`
- `H56` : `$C$7`
- `I56` : `$C$7`
- `J56` : `$C$7`
- `K56` : `$C$7`
- `L56` : `$C$7`
- `M56` : `$C$7`
- `D57` : `$C$7`
- `E57` : `$C$7`
- `F57` : `$C$7`
- `G57` : `$C$7`
- `H57` : `$C$7`
- `I57` : `$C$7`
- `J57` : `$C$7`
- `K57` : `$C$7`
- `L57` : `$C$7`
- `M57` : `$C$7`
- `D58` : `$C$7`
- `E58` : `$C$7`
- `F58` : `$C$7`
- `G58` : `$C$7`
- `H58` : `$C$7`
- `I58` : `$C$7`
- `J58` : `$C$7`
- `K58` : `$C$7`
- `L58` : `$C$7`
- `M58` : `$C$7`
- `D59` : `$C$7`
- `E59` : `$C$7`
- `F59` : `$C$7`
- `G59` : `$C$7`
- `H59` : `$C$7`
- `I59` : `$C$7`
- `J59` : `$C$7`
- `K59` : `$C$7`
- `L59` : `$C$7`
- `M59` : `$C$7`
- `D60` : `$C$7`
- `E60` : `$C$7`
- `F60` : `$C$7`
- `G60` : `$C$7`
- `H60` : `$C$7`
- `I60` : `$C$7`
- `J60` : `$C$7`
- `K60` : `$C$7`
- `L60` : `$C$7`
- `M60` : `$C$7`
- `D61` : `$C$7`
- `E61` : `$C$7`
- `F61` : `$C$7`
- `G61` : `$C$7`
- `H61` : `$C$7`
- `I61` : `$C$7`
- `J61` : `$C$7`
- `K61` : `$C$7`
- `L61` : `$C$7`
- `M61` : `$C$7`
- `D62` : `$C$7`
- `E62` : `$C$7`
- `F62` : `$C$7`
- `G62` : `$C$7`
- `H62` : `$C$7`
- `I62` : `$C$7`
- `J62` : `$C$7`
- `K62` : `$C$7`
- `L62` : `$C$7`
- `M62` : `$C$7`
- `D63` : `$C$7`
- `E63` : `$C$7`
- `F63` : `$C$7`
- `G63` : `$C$7`
- `H63` : `$C$7`
- `I63` : `$C$7`
- `J63` : `$C$7`
- `K63` : `$C$7`
- `L63` : `$C$7`
- `M63` : `$C$7`
- `D64` : `$C$7`
- `E64` : `$C$7`
- `F64` : `$C$7`
- `G64` : `$C$7`
- `H64` : `$C$7`
- `I64` : `$C$7`
- `J64` : `$C$7`
- `K64` : `$C$7`
- `L64` : `$C$7`
- `M64` : `$C$7`
- `D65` : `$C$7`
- `E65` : `$C$7`
- `F65` : `$C$7`
- `G65` : `$C$7`
- `H65` : `$C$7`
- `I65` : `$C$7`
- `J65` : `$C$7`
- `K65` : `$C$7`
- `L65` : `$C$7`
- `M65` : `$C$7`
- `D66` : `$C$7`
- `E66` : `$C$7`
- `F66` : `$C$7`
- `G66` : `$C$7`
- `H66` : `$C$7`
- `I66` : `$C$7`
- `J66` : `$C$7`
- `K66` : `$C$7`
- `L66` : `$C$7`
- `M66` : `$C$7`
- `D67` : `$C$7`
- `E67` : `$C$7`
- `F67` : `$C$7`
- `G67` : `$C$7`
- `H67` : `$C$7`
- `I67` : `$C$7`
- `J67` : `$C$7`
- `K67` : `$C$7`
- `L67` : `$C$7`
- `M67` : `$C$7`
- `D68` : `$C$7`
- `E68` : `$C$7`
- `F68` : `$C$7`
- `G68` : `$C$7`
- `H68` : `$C$7`
- `I68` : `$C$7`
- `J68` : `$C$7`
- `K68` : `$C$7`
- `L68` : `$C$7`
- `M68` : `$C$7`

Défaut connu =$C$7. La validation Excel ne couvre que D:H, appliquer néanmoins la même borne -1 à I:M.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Choc coûts composé — `Sensi TCA!C8`

Unité : fraction. Composition multiplicative du preset et du choc, non somme arbitraire.

```text
(1+INDEX($E$72:$E$78,MATCH($C$15,$B$72:$B$78,0)))*(1+'Sensi Analyses'!$E$10)-1
```

Sources directes extraites : `'Sensi TCA'!$E$72:$E$78`, `'Sensi TCA'!$C$15`, `'Sensi TCA'!$B$72:$B$78`, `'Sensi Analyses'!$E$10`.

### Décalage composé — `Sensi TCA!C14`

Unité : mois. Levier calculé protégé ; demande manuelle dans K77 via catalogue.

```text
INDEX($K$72:$K$78,MATCH($C$15,$B$72:$B$78,0))+'Sensi Analyses'!$E$16
```

Sources directes extraites : `'Sensi TCA'!$K$72:$K$78`, `'Sensi TCA'!$C$15`, `'Sensi TCA'!$B$72:$B$78`, `'Sensi Analyses'!$E$16`.

### Equity du scénario — `Sensi TCA!C85`

Unité : EUR. Montant de référence modulé sans confondre trésorerie initiale et nouveaux apports.

```text
C82*C84
```

Sources directes extraites : `'Sensi TCA'!C82`, `'Sensi TCA'!C84`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_29 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Choc preset +10 % et choc additionnel +20 % sur même assiette.

Attendu : Choc composé +32 %. Le défaut calculé C14 reste protégé ; un scénario sans equity ne retire pas la trésorerie initiale.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
