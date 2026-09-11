# ATELIER_CIR_IS

Responsabilité : **Qualifier fiscalité, TVA et calendriers de paiement.**

Contrat : `AGENT_21`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel régime, taux et calendrier sont confirmés, pour quelle période ?
- Quelles qualifications restent à faire valider ?

## Règles et contrôles métier

- Une hypothèse favorable non confirmée reste signalée.
- Ne pas universaliser un régime hérité.

## Dépendances

Sources métier du contrat : CALCUL_CIR, Revenue, Control.

Sources directes extraites : Assumptions, CALCUL_CIR, Compte de Résultat, Contrats, Control, DATA Contrats, Modèle financier, Revenue, Stock.

Feuilles qui consomment directement cette feuille : BFR, Bilan, Compte de Résultat, Contrôles, KPI Dashboard, Modèle financier, Plan de financement.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Conditions capital libéré / détention admissible

Identifiant : `atelier_cir_is_c66_m66`. Type : `enum`. Zones : `C66:M66`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Qualification annuelle explicite des conditions de capital/détention ou exonération désignées ; À confirmer ne vaut ni Oui ni Non.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non", "À confirmer"]}`.

Choix du catalogue : ["Oui", "Non", "À confirmer"].

### Mois restitution trop-versés IS/contribution

Identifiant : `atelier_cir_is_c79_m79`. Type : `integer`. Zones : `C79:M79`.

Unité explicite : numéro de mois 1 à 12.

Assiette : Mois de restitution des trop-versés IS/contribution ; distinct d’un délai.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 5, "max": 12}, "choices": null}`.

Contraintes : `{"min": 5, "max": 12}`.

### Exonération taxe additionnelle CVAE

Identifiant : `atelier_cir_is_c85_m85`. Type : `enum`. Zones : `C85:M85`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Qualification annuelle explicite des conditions de capital/détention ou exonération désignées ; À confirmer ne vaut ni Oui ni Non.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non", "À confirmer"]}`.

Choix du catalogue : ["Oui", "Non", "À confirmer"].

### Autres loyers corporels longs à réintégrer CVAE

Identifiant : `atelier_cir_is_c89_m89`. Type : `number`. Zones : `C89:M89`.

Unité explicite : EUR par exercice.

Assiette : Montant annuel désigné : loyers à réintégrer, CFE selon avis ou CA de groupe de l’assiette fiscale ; aucun montant implicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### CFE selon avis annuel

Identifiant : `atelier_cir_is_c91_m91`. Type : `number`. Zones : `C91:M91`.

Unité explicite : EUR par exercice.

Assiette : Montant annuel désigné : loyers à réintégrer, CFE selon avis ou CA de groupe de l’assiette fiscale ; aucun montant implicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "optional": true}`.

### CA de groupe pour IS et contribution

Identifiant : `atelier_cir_is_c110_m110`. Type : `number`. Zones : `C110:M110`.

Unité explicite : EUR par exercice.

Assiette : Montant annuel désigné : loyers à réintégrer, CFE selon avis ou CA de groupe de l’assiette fiscale ; aucun montant implicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "optional": true}`.

### CA de groupe pour CVAE

Identifiant : `atelier_cir_is_c111_m111`. Type : `number`. Zones : `C111:M111`.

Unité explicite : EUR par exercice.

Assiette : Montant annuel désigné : loyers à réintégrer, CFE selon avis ou CA de groupe de l’assiette fiscale ; aucun montant implicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "optional": true}`.

### CFE exercice précédant le plan

Identifiant : `atelier_cir_is_c93`. Type : `number`. Zones : `C93`.

Unité explicite : EUR.

Assiette : CFE de l’exercice précédant le début du plan ; source d’antériorité explicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICE_PRECEDANT_A1`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Commentaire sur l’antériorité fiscale

Identifiant : `atelier_cir_is_c117_m117`. Type : `text`. Zones : `C117:M117`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Commentaires d’antériorité fiscale ; aucun effet d’éligibilité à inférer.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Régime TVA par offre

Identifiant : `atelier_cir_is_d143_d155`. Type : `enum`. Zones : `D143:D155`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Régime de TVA de l’offre ; détermine les dates d’exigibilité, pas une règle universelle.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Biens", "Services encaissements", "Services débits", "Exonéré / hors champ"]}`.

Choix du catalogue : ["Biens", "Services encaissements", "Services débits", "Exonéré / hors champ"].

### Taux TVA client par offre

Identifiant : `atelier_cir_is_e143_e155`. Type : `number`. Zones : `E143:E155`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : TVA collectée appliquée à la base HT de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : offer_active, offer_unit, atelier_cir_is_d143_d155.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Confirmation régime TVA par offre

Identifiant : `atelier_cir_is_f143_f155`. Type : `enum`. Zones : `F143:F155`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Confirmation documentaire du régime/taux ou des paramètres TVA ; À confirmer bloque la qualification.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["À confirmer", "Confirmé"]}`.

Choix du catalogue : ["À confirmer", "Confirmé"].

### Périodicité de déclaration implémentée

Identifiant : `atelier_cir_is_d160`. Type : `enum`. Zones : `D160`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Périodicité implémentée de déclaration TVA ; vérifier correspondance avec le régime réel.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Mensuelle"]}`.

Choix du catalogue : ["Mensuelle"].

### Délai paiement TVA mois

Identifiant : `atelier_cir_is_d161`. Type : `integer`. Zones : `D161`.

Unité explicite : mois calendaires.

Assiette : Délai entre constatation/déclaration et paiement ou remboursement TVA.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 1, "max": 12}, "choices": null}`.

Contraintes : `{"min": 1, "max": 12}`.

### Demande remboursement crédit TVA

Identifiant : `atelier_cir_is_d162`. Type : `enum`. Zones : `D162`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Choix explicite de demande de remboursement du crédit TVA.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non"]}`.

Choix du catalogue : ["Oui", "Non"].

### Délai encaissement remboursement mois

Identifiant : `atelier_cir_is_d163`. Type : `integer`. Zones : `D163`.

Unité explicite : mois calendaires.

Assiette : Délai entre constatation/déclaration et paiement ou remboursement TVA.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 1, "max": 12}, "choices": null}`.

Contraintes : `{"min": 1, "max": 12}`.

### Seuil demande mensuelle euros

Identifiant : `atelier_cir_is_d164`. Type : `number`. Zones : `D164`.

Unité explicite : EUR de crédit TVA.

Assiette : Seuil de demande mensuelle ou de décembre ; paramètre à sourcer, pas un seuil légal présumé.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 760, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 760, "max": 1000000000000.0}`.

### Seuil demande décembre euros

Identifiant : `atelier_cir_is_d165`. Type : `number`. Zones : `D165`.

Unité explicite : EUR de crédit TVA.

Assiette : Seuil de demande mensuelle ou de décembre ; paramètre à sourcer, pas un seuil légal présumé.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 150, "max": 1000000000000.0}, "choices": null}`.

Contraintes : `{"min": 150, "max": 1000000000000.0}`.

### Confirmation paramètres TVA

Identifiant : `atelier_cir_is_d166`. Type : `enum`. Zones : `D166`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Confirmation documentaire du régime/taux ou des paramètres TVA ; À confirmer bloque la qualification.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["À confirmer", "Confirmé"]}`.

Choix du catalogue : ["À confirmer", "Confirmé"].

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Rapprochement produit/charge fiscale — `ATELIER_CIR_IS!C30`

Unité : EUR. Effet net rapproché du CIR, IS et contributions.

```text
C29-(C20-C19-C69)
```

Sources directes extraites : `'ATELIER_CIR_IS'!C29`, `'ATELIER_CIR_IS'!C20`, `'ATELIER_CIR_IS'!C19`, `'ATELIER_CIR_IS'!C69`.

### Rapprochement CIR résultat/bilan/cash — `ATELIER_CIR_IS!C55`

Unité : EUR. Produit, variation de créance et encaissement se réconcilient.

```text
C28-(C40-C37)-C33
```

Sources directes extraites : `'ATELIER_CIR_IS'!C28`, `'ATELIER_CIR_IS'!C40`, `'ATELIER_CIR_IS'!C37`, `'ATELIER_CIR_IS'!C33`.

### Rapprochement IS résultat/bilan/cash — `ATELIER_CIR_IS!C56`

Unité : EUR. Charge, solde fiscal et paiements se réconcilient.

```text
-C27-(C45-C42)-C34
```

Sources directes extraites : `'ATELIER_CIR_IS'!C27`, `'ATELIER_CIR_IS'!C45`, `'ATELIER_CIR_IS'!C42`, `'ATELIER_CIR_IS'!C34`.

### Diagnostic régime fiscal — `ATELIER_CIR_IS!C68`

Unité : diagnostic. Absence de qualification doit être visible avant toute interprétation favorable.

```text
IF(AND(ISNUMBER(Control!$C$10),ISNUMBER(Control!$C$59),Control!$C$59>=1,Control!$C$59<=10,ISNUMBER(Control!$C$60)),IF(C$12>Control!$C$60,"INACTIF_HORS_HORIZON",IF(NOT(OR(C66="Oui",C66="Non")),"NON_RENSEIGNE : qualifier capital et détention",IF(C67,"Taux réduit admissible selon saisie qualifiée","Taux normal"))),NA())
```

Sources directes extraites : `'Control'!$C$10`, `'Control'!$C$59`, `'Control'!$C$60`, `'ATELIER_CIR_IS'!C$12`, `'ATELIER_CIR_IS'!C66`, `'ATELIER_CIR_IS'!C67`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_21 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : CIR documenté 30 000, aucun encaissement cette année, créance initiale zéro.

Attendu : Produit 30 000, créance finale 30 000, cash 0, rapprochement C55 nul ; sans qualification, résultat non certifiable.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
