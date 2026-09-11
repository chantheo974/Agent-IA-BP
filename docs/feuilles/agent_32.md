# Valorisation

Responsabilité : **Qualifier les méthodes de valorisation et leurs hypothèses sourcées.**

Contrat : `AGENT_32`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quelle méthode, quelle date et quelles sources de taux ou multiples ?
- Quelles données et qualifications manquent pour rendre le calcul utilisable ?

## Règles et contrôles métier

- Aucune calibration cachée vers une valeur cible.
- Distinguer recalcul Excel et résolution locale WACC.
- Ne pas cumuler des risques déjà traités dans les flux.

## Dépendances

Sources métier du contrat : BFR, Compte de Résultat, Bilan, Comparables.

Sources directes extraites : BFR, Bilan, CAPEX, Comparables, Compte de Résultat, Control, Financement E&S, Modèle financier, Sensi TCA.

Feuilles qui consomment directement cette feuille : BFR, Contrôles, KPI Dashboard.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Croissance terminale g

Identifiant : `valorisation_d8`. Type : `number`. Zones : `D8`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Croissance annuelle terminale des flux ; doit être compatible avec le taux d’actualisation.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d9.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": -1}, "choices": null}`.

Contraintes : `{"min_exclusive": -1}`.

### IS normatif DCF

Identifiant : `valorisation_d9`. Type : `number`. Zones : `D9`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : IS normatif propriétaire du DCF ; aucun héritage d’un zéro calculé ne le qualifie.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max_exclusive": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max_exclusive": 1}`.

### Poids EBE dans le mix EBE/CA

Identifiant : `valorisation_d12`. Type : `number`. Zones : `D12`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Poids EBE dans le mix EBE/CA ; le complément pondère le CA.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : comparables_s14_ad16.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Taux actualisation VC

Identifiant : `valorisation_d13`. Type : `number`. Zones : `D13`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": -1}, "choices": null}`.

Contraintes : `{"min_exclusive": -1}`.

### Pre-money proposé pour négociation euros

Identifiant : `valorisation_d57`. Type : `number`. Zones : `D57`.

Unité explicite : EUR de valeur des fonds propres pré-money.

Assiette : Proposition ou cible indicative de négociation ; ne vaut pas oracle, marché ou autorisation de calibrage caché.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : data_financement_d14_d413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Mode WACC

Identifiant : `valorisation_d107`. Type : `enum`. Zones : `D107`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Mode de WACC ; Itération exige un reçu local propre, jamais le calcul circulaire global.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Manuel", "Structure cible", "Itération"]}`.

Choix du catalogue : ["Manuel", "Structure cible", "Itération"].

### WACC manuel

Identifiant : `valorisation_d108`. Type : `number`. Zones : `D108`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": -1}, "choices": null}`.

Contraintes : `{"min_exclusive": -1}`.

### Date de référence des données de marché

Identifiant : `valorisation_d111`. Type : `date`. Zones : `D111`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de référence commune des données de marché justifiées.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Prime de risque actions

Identifiant : `valorisation_d113`. Type : `number`. Zones : `D113`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Coût de la dette avant IS

Identifiant : `valorisation_d116`. Type : `number`. Zones : `D116`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Prime de taille

Identifiant : `valorisation_d117`. Type : `number`. Zones : `D117`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Prime spécifique exécution

Identifiant : `valorisation_d118`. Type : `number`. Zones : `D118`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Prime illiquidité

Identifiant : `valorisation_d119`. Type : `number`. Zones : `D119`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Traitement risque exécution

Identifiant : `valorisation_d120`. Type : `enum`. Zones : `D120`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Déclarations explicites de traitement des risques ; éviter primes/décotes/abattements portant deux fois sur le même risque.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Flux", "Taux"]}`.

Choix du catalogue : ["Flux", "Taux"].

### Flux déjà abattus pour même risque

Identifiant : `valorisation_d121`. Type : `enum`. Zones : `D121`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Déclarations explicites de traitement des risques ; éviter primes/décotes/abattements portant deux fois sur le même risque.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non", "À confirmer"]}`.

Choix du catalogue : ["Oui", "Non", "À confirmer"].

### Décote taille appliquée aux multiples

Identifiant : `valorisation_d122`. Type : `enum`. Zones : `D122`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Déclarations explicites de traitement des risques ; éviter primes/décotes/abattements portant deux fois sur le même risque.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non", "À confirmer"]}`.

Choix du catalogue : ["Oui", "Non", "À confirmer"].

### DLOM appliquée à cette même valeur

Identifiant : `valorisation_d123`. Type : `enum`. Zones : `D123`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Déclarations explicites de traitement des risques ; éviter primes/décotes/abattements portant deux fois sur le même risque.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non", "À confirmer"]}`.

Choix du catalogue : ["Oui", "Non", "À confirmer"].

### Levier cible dette brute / equity

Identifiant : `valorisation_d124`. Type : `number`. Zones : `D124`.

Unité explicite : ratio dette financière brute / equity.

Assiette : Levier cible exprimé en quotient, pas en part dette/(dette+equity).

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d116, valorisation_d9.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "optional": true}`.

### Cible indicative de pre-money euros

Identifiant : `valorisation_d161`. Type : `number`. Zones : `D161`.

Unité explicite : EUR de valeur des fonds propres pré-money.

Assiette : Proposition ou cible indicative de négociation ; ne vaut pas oracle, marché ou autorisation de calibrage caché.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : data_financement_d14_d413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Année de sortie VC

Identifiant : `valorisation_d16`. Type : `integer`. Zones : `D16`.

Unité explicite : année civile de sortie.

Assiette : Année comprise dans le calendrier actif ; défaut = dernière année active, pas nombre d’années.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["D16"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_dynamic": "YEAR(Valorisation!D15)", "max_dynamic": "Control!C60"}, "choices": null}`.

Contraintes : `{"min_dynamic": "YEAR(Valorisation!D15)", "max_dynamic": "Control!C60"}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `D16` : `Control!$C$60`

### Taux sans risque justifié

Identifiant : `valorisation_d112`. Type : `number`. Zones : `D112`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : valorisation_d107, valorisation_d120, valorisation_d121, valorisation_d122, valorisation_d123.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Source / justification 112

Identifiant : `valorisation_e112`. Type : `text`. Zones : `E112`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Source / justification 113

Identifiant : `valorisation_e113`. Type : `text`. Zones : `E113`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Source / justification 116

Identifiant : `valorisation_e116`. Type : `text`. Zones : `E116`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Source / justification 117

Identifiant : `valorisation_e117`. Type : `text`. Zones : `E117`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Source / justification 118

Identifiant : `valorisation_e118`. Type : `text`. Zones : `E118`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Source / justification 119

Identifiant : `valorisation_e119`. Type : `text`. Zones : `E119`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Source / justification 125

Identifiant : `valorisation_e125`. Type : `text`. Zones : `E125`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : valorisation_d111.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### WACC retenu — `Valorisation!D7`

Unité : fraction annuelle. Mode manuel/cible/itération explicite ; résultat macro exige sa preuve propre.

```text
IF($D$107="Manuel",$D$108,IF($D$107="Structure cible",IF($D$138="OK",$D$135,""),IF($D$107="Itération",$D$136,"")))
```

Sources directes extraites : `'Valorisation'!$D$107`, `'Valorisation'!$D$108`, `'Valorisation'!$D$138`, `'Valorisation'!$D$135`, `'Valorisation'!$D$136`.

### Validité dates/taux — `Valorisation!D17`

Unité : diagnostic. Closing, sortie et taux doivent être compatibles avant interprétation.

```text
IF(NOT(ISNUMBER($D$7)),"⚠ WACC à compléter",IF(NOT(ISNUMBER($D$15)),"⚠ closing invalide",IF(OR($D$15<Control!$C$10,$D$15>=DATE(Control!$C$60+1,1,1)),"⚠ closing hors horizon",IF(NOT(ISNUMBER($D$16)),"⚠ sortie VC invalide",IF(OR($D$16<>INT($D$16),$D$16<YEAR($D$15),$D$16>Control!$C$60),"⚠ sortie VC hors horizon",IF(OR($D$7<=$D$8,$D$7<=-1,$D$8<=-1,$D$13<=-1),"⚠ taux de valorisation invalides",IF(OR(NOT(ISNUMBER($D$12)),$D$12<0,$D$12>1),"⚠ pondération VC hors [0 ; 1]","OK")))))))
```

Sources directes extraites : `'Valorisation'!$D$7`, `'Valorisation'!$D$15`, `'Control'!$C$10`, `'Control'!$C$60`, `'Valorisation'!$D$16`, `'Valorisation'!$D$8`, `'Valorisation'!$D$13`, `'Valorisation'!$D$12`.

### Valeur entreprise DCF — `Valorisation!D38`

Unité : EUR. Somme des flux actualisés et terminal ; préciser BFR permanent.

```text
IF(AND(ISNUMBER(D34),ISNUMBER(D37)),D34+D37,"n.a.")
```

Sources directes extraites : `'Valorisation'!D34`, `'Valorisation'!D37`.

### Valeur des fonds propres — `Valorisation!D40`

Unité : EUR. Passage EV vers equity après dette nette selon date de closing.

```text
IF(AND(ISNUMBER(D38),ISNUMBER(D39)),D38-D39,"n.a.")
```

Sources directes extraites : `'Valorisation'!D38`, `'Valorisation'!D39`.

### Pré-money retenu — `Valorisation!D59`

Unité : EUR. Ne pas présenter une absence comme zéro ni calibrer tacitement un taux.

```text
IF(AND(ISNUMBER($D$57),ISNUMBER($D$14),$D$14>0),IF(D58>0,$D$14/D58,"Non déterminé"),"Non renseigné")
```

Sources directes extraites : `'Valorisation'!$D$57`, `'Valorisation'!$D$14`, `'Valorisation'!D58`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_32 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Pré-money sourcé 1 000 000 EUR, apport 250 000, aucune autre dilution ; puis retirer la source de pré-money.

Attendu : Dilution économique attendue 20 % dans le premier cas ; dans le second valeur indisponible. DCF/WACC requièrent leurs oracles natifs distincts.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
