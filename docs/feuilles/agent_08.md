# DATA COGS

Responsabilité : **Qualifier les coûts directs et la méthode de calcul par offre.**

Contrat : `AGENT_08`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Coût détaillé, coût manuel ou marge cible ?
- Les coûts incluent-ils déjà des salaires ou d'autres charges comptés ailleurs ?

## Règles et contrôles métier

- Assiettes et unités cohérentes.
- Pas de coût négatif involontaire ni double compte.

## Dépendances

Sources métier du contrat : Assumptions.

Sources directes extraites : Assumptions, COGS, Control, Revenue.

Feuilles qui consomment directement cette feuille : Assumptions, BFR, COGS, Control, Contrôles.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Mode COGS

Identifiant : `cogs_mode`. Type : `enum`. Zones : `D15:D27`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Sélection de la méthode de coût ; seuls les paramètres de la méthode retenue qualifient le résultat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Detaille", "Cible", "Manuel"]}`.

Choix du catalogue : ["Detaille", "Cible", "Manuel"].

### Matière et achats

Identifiant : `cogs_material`. Type : `number`. Zones : `E15:E27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Composante de coût direct unitaire ; manuel remplace le coût unitaire selon la méthode choisie.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Ne pas doubler les salaires déjà comptés dans Effectifs. Pour une offre forfait, ne pas utiliser des coûts en €/unité sans objet ; utiliser % du CA ou marge.

### Intégration interne

Identifiant : `cogs_integration`. Type : `number`. Zones : `F15:F27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Composante de coût direct unitaire ; manuel remplace le coût unitaire selon la méthode choisie.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Ne pas doubler les salaires déjà comptés dans Effectifs. Pour une offre forfait, ne pas utiliser des coûts en €/unité sans objet ; utiliser % du CA ou marge.

### Essais et qualification

Identifiant : `cogs_testing`. Type : `number`. Zones : `G15:G27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Composante de coût direct unitaire ; manuel remplace le coût unitaire selon la méthode choisie.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Ne pas doubler les salaires déjà comptés dans Effectifs. Pour une offre forfait, ne pas utiliser des coûts en €/unité sans objet ; utiliser % du CA ou marge.

### Autres coûts directs

Identifiant : `cogs_other`. Type : `number`. Zones : `H15:H27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Composante de coût direct unitaire ; manuel remplace le coût unitaire selon la méthode choisie.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Ne pas doubler les salaires déjà comptés dans Effectifs. Pour une offre forfait, ne pas utiliser des coûts en €/unité sans objet ; utiliser % du CA ou marge.

### COGS manuel

Identifiant : `cogs_manual`. Type : `number`. Zones : `L15:L27`.

Unité explicite : EUR HT par unité de l’offre.

Assiette : Composante de coût direct unitaire ; manuel remplace le coût unitaire selon la méthode choisie.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Ne pas doubler les salaires déjà comptés dans Effectifs. Pour une offre forfait, ne pas utiliser des coûts en €/unité sans objet ; utiliser % du CA ou marge.
Strictement positif lorsque le mode est Manuel.

### Logistique et sous-traitance

Identifiant : `cogs_logistics`. Type : `number`. Zones : `J15:J27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Logistique/sous-traitance ou garantie/retours en part du CA de l’offre, pas EUR par unité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Garantie et retours

Identifiant : `cogs_warranty`. Type : `number`. Zones : `K15:K27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Logistique/sous-traitance ou garantie/retours en part du CA de l’offre, pas EUR par unité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Marge cible A1

Identifiant : `cogs_margin_2026`. Type : `number`. Zones : `M15:M27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A2

Identifiant : `cogs_margin_2027`. Type : `number`. Zones : `N15:N27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A3

Identifiant : `cogs_margin_2028`. Type : `number`. Zones : `O15:O27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A4

Identifiant : `cogs_margin_2029`. Type : `number`. Zones : `P15:P27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A5

Identifiant : `cogs_margin_2030`. Type : `number`. Zones : `Q15:Q27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A6

Identifiant : `cogs_margin_2031`. Type : `number`. Zones : `X15:X27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A7

Identifiant : `cogs_margin_2032`. Type : `number`. Zones : `Y15:Y27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A8

Identifiant : `cogs_margin_2033`. Type : `number`. Zones : `Z15:Z27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A9

Identifiant : `cogs_margin_2034`. Type : `number`. Zones : `AA15:AA27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Marge cible A10

Identifiant : `cogs_margin_2035`. Type : `number`. Zones : `AB15:AB27`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : offer_active, offer_unit, model_start_date, active_horizon_years, cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Renseigner une marge justifiée pour chaque année active avec CA en mode Cible. Marge + J + K ≤ 1. Les années futures sont vierges dans Pilotage.

### Statut / source du coût

Identifiant : `cogs_source`. Type : `text`. Zones : `W15:W27`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source et qualité du coût ; distinctes des valeurs et de leur qualification.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : cogs_mode.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Validité de la méthode de coût — `DATA COGS!V15`

Unité : diagnostic. Manuel exige une valeur numérique positive ou nulle ; vide ne signifie pas coût nul.

```text
IF(COUNTIF($AC15:$AG15,"⚠*")>0,"⚠ voir marges futures",IF($A15="","",IF(COUNTIF($D15,"Cible")+COUNTIF($D15,"Detaille")+COUNTIF($D15,"Manuel")=0,"⚠ mode COGS non reconnu",IF(OR(MIN($M15:$Q15,$X15:$AB15)<0,MAX($M15:$Q15,$X15:$AB15)>1),"⚠ marge cible hors [0 ; 100 %]",IF((1-MIN($M15:$Q15,$X15:$AB15)-$J15-$K15)<-0.000000001,"⚠ marge cible + % du CA > 100 %",IF(AND($D15="Detaille",$I15=0,$J15=0,$K15=0),"⚠ mode Detaille sans aucun cout saisi",IF(AND($D15="Manuel",OR(NOT(ISNUMBER($L15)),$L15<0)),"⚠ mode Manuel sans COGS saisi",IF(AND($D15="Detaille",$C15="forfait",$I15>0),"⚠ forfait : cout en €/unite sans objet, chiffrer en % du CA","OK"))))))))
```

Sources directes extraites : `'DATA COGS'!$AC15:$AG15`, `'DATA COGS'!$A15`, `'DATA COGS'!$D15`, `'DATA COGS'!$M15:$Q15`, `'DATA COGS'!$X15:$AB15`, `'DATA COGS'!$J15`, `'DATA COGS'!$K15`, `'DATA COGS'!$I15`, `'DATA COGS'!$L15`, `'DATA COGS'!$C15`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_08 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Choisir Manuel avec un coût explicitement égal à 0, puis refaire avec champ absent.

Attendu : Zéro est une saisie valide ; absent exige une question et ne doit pas être présenté comme gratuit.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
