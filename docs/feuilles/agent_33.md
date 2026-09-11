# Comparables

Responsabilité : **Qualifier le panel de sociétés, transactions et sources de marché.**

Contrat : `AGENT_33`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quelles sociétés ou transactions, quelles dates, quelles unités et quelles sources ?

## Règles et contrôles métier

- Séparer données observées et hypothèses.
- Contrôler la couverture et la méthode de pondération.

## Dépendances

Sources métier du contrat : aucune dépendance métier déclarée.

Sources directes extraites : aucune.

Feuilles qui consomment directement cette feuille : Contrôles, Valorisation.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Marge EBITDA minimale admissible

Identifiant : `comparables_h9`. Type : `number`. Zones : `H9`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Marge EBITDA/CA minimum du filtre de comparables.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

### Plafond multiple EV/EBITDA

Identifiant : `comparables_h10`. Type : `number`. Zones : `H10`.

Unité explicite : multiple sans dimension.

Assiette : Multiple EV/EBITDA plafond ou multiple EV/CA/EV/EBITDA observé selon le champ ; mêmes périmètres économiques au numérateur et dénominateur.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Poids des statistiques par source CA/EBITDA

Identifiant : `comparables_s14_ad16`. Type : `number`. Zones : `S14:AD16`.

Unité explicite : poids relatif sans dimension.

Assiette : Poids des statistiques CA/EBITDA par source ; normalisation par les sommes de poids du modèle.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Libellé indice

Identifiant : `comparables_b25_b32`. Type : `text`. Zones : `B25:B32`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Multiple EV/CA

Identifiant : `comparables_c25_c32`. Type : `number`. Zones : `C25:C32`.

Unité explicite : multiple sans dimension.

Assiette : Multiple EV/EBITDA plafond ou multiple EV/CA/EV/EBITDA observé selon le champ ; mêmes périmètres économiques au numérateur et dénominateur.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "optional": true}`.

### Multiple EV/EBITDA

Identifiant : `comparables_d25_d32`. Type : `number`. Zones : `D25:D32`.

Unité explicite : multiple sans dimension.

Assiette : Multiple EV/EBITDA plafond ou multiple EV/CA/EV/EBITDA observé selon le champ ; mêmes périmètres économiques au numérateur et dénominateur.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "optional": true}`.

### Score pertinence CA

Identifiant : `comparables_e25_e32`. Type : `number`. Zones : `E25:E32`.

Unité explicite : score de pertinence sans dimension.

Assiette : Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 5}, "choices": null}`.

Contraintes : `{"min": 0, "max": 5}`.

### Score pertinence EBITDA

Identifiant : `comparables_f25_f32`. Type : `number`. Zones : `F25:F32`.

Unité explicite : score de pertinence sans dimension.

Assiette : Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 5}, "choices": null}`.

Contraintes : `{"min": 0, "max": 5}`.

### Source indice

Identifiant : `comparables_i25_i32`. Type : `text`. Zones : `I25:I32`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Hypothèses indice

Identifiant : `comparables_j25_j32`. Type : `text`. Zones : `J25:J32`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### société : Société / acquéreur

Identifiant : `comparables_b47_b61`. Type : `text`. Zones : `B47:B61`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### société : Pays / cible

Identifiant : `comparables_c47_c61`. Type : `text`. Zones : `C47:C61`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### société : Statut / activité de la cible

Identifiant : `comparables_d47_d61`. Type : `text`. Zones : `D47:D61`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### société : CA en M EUR

Identifiant : `comparables_e47_e61`. Type : `number`. Zones : `E47:E61`.

Unité explicite : millions d’EUR (M EUR).

Assiette : CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "optional": true}`.

### société : EBITDA en M EUR

Identifiant : `comparables_f47_f61`. Type : `number`. Zones : `F47:F61`.

Unité explicite : millions d’EUR (M EUR).

Assiette : CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"optional": true}, "choices": null}`.

Contraintes : `{"optional": true}`.

### société : Valeur entreprise en M EUR

Identifiant : `comparables_g47_g61`. Type : `number`. Zones : `G47:G61`.

Unité explicite : millions d’EUR (M EUR).

Assiette : CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "optional": true}`.

### société : Score pertinence CA

Identifiant : `comparables_j47_j61`. Type : `number`. Zones : `J47:J61`.

Unité explicite : score de pertinence sans dimension.

Assiette : Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 5}, "choices": null}`.

Contraintes : `{"min": 0, "max": 5}`.

### société : Score pertinence EBITDA

Identifiant : `comparables_k47_k61`. Type : `number`. Zones : `K47:K61`.

Unité explicite : score de pertinence sans dimension.

Assiette : Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 5}, "choices": null}`.

Contraintes : `{"min": 0, "max": 5}`.

### société : Sources, date, périmètre et hypothèses

Identifiant : `comparables_n47_n61`. Type : `text`. Zones : `N47:N61`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### transaction : Société / acquéreur

Identifiant : `comparables_b76_b103`. Type : `text`. Zones : `B76:B103`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### transaction : Pays / cible

Identifiant : `comparables_c76_c103`. Type : `text`. Zones : `C76:C103`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### transaction : Statut / activité de la cible

Identifiant : `comparables_d76_d103`. Type : `text`. Zones : `D76:D103`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### transaction : CA en M EUR

Identifiant : `comparables_e76_e103`. Type : `number`. Zones : `E76:E103`.

Unité explicite : millions d’EUR (M EUR).

Assiette : CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "optional": true}`.

### transaction : EBITDA en M EUR

Identifiant : `comparables_f76_f103`. Type : `number`. Zones : `F76:F103`.

Unité explicite : millions d’EUR (M EUR).

Assiette : CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"optional": true}, "choices": null}`.

Contraintes : `{"optional": true}`.

### transaction : Valeur entreprise en M EUR

Identifiant : `comparables_g76_g103`. Type : `number`. Zones : `G76:G103`.

Unité explicite : millions d’EUR (M EUR).

Assiette : CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "optional": true}`.

### transaction : Score pertinence CA

Identifiant : `comparables_j76_j103`. Type : `number`. Zones : `J76:J103`.

Unité explicite : score de pertinence sans dimension.

Assiette : Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 5}, "choices": null}`.

Contraintes : `{"min": 0, "max": 5}`.

### transaction : Score pertinence EBITDA

Identifiant : `comparables_k76_k103`. Type : `number`. Zones : `K76:K103`.

Unité explicite : score de pertinence sans dimension.

Assiette : Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 5}, "choices": null}`.

Contraintes : `{"min": 0, "max": 5}`.

### transaction : Sources, date, périmètre et hypothèses

Identifiant : `comparables_n76_n103`. Type : `text`. Zones : `N76:N103`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, périmètre, source ou hypothèses de l’observation comparable désignée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Identifiant société cotée

Identifiant : `comparables_b117_b136`. Type : `text`. Zones : `B117:B136`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identifiant et preuve de l’observation de bêta, périmètre de dette et unité monétaire commune.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Inclure dans médiane bêta

Identifiant : `comparables_c117_c136`. Type : `enum`. Zones : `C117:C136`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Inclusion explicite dans la médiane bêta ; données complètes requises.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_d117_d136, comparables_e117_e136, comparables_f117_f136, comparables_g117_g136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non"]}`.

Choix du catalogue : ["Oui", "Non"].

### Bêta endetté

Identifiant : `comparables_d117_d136`. Type : `number`. Zones : `D117:D136`.

Unité explicite : coefficient bêta sans dimension.

Assiette : Bêta endetté observé selon fréquence/fenêtre et source.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_l117_l136, comparables_m117_m136, comparables_j117_j136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Equity de marché

Identifiant : `comparables_e117_e136`. Type : `number`. Zones : `E117:E136`.

Unité explicite : même unité monétaire documentée pour equity et dette.

Assiette : Montants utilisés uniquement ensemble en ratio dette/equity ; monnaie et facteur d’échelle identiques exigés, aucune conversion implicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_e117_e136, comparables_f117_f136, comparables_k117_k136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Dette financière brute

Identifiant : `comparables_f117_f136`. Type : `number`. Zones : `F117:F136`.

Unité explicite : même unité monétaire documentée pour equity et dette.

Assiette : Montants utilisés uniquement ensemble en ratio dette/equity ; monnaie et facteur d’échelle identiques exigés, aucune conversion implicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_e117_e136, comparables_f117_f136, comparables_k117_k136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Taux marginal IS

Identifiant : `comparables_g117_g136`. Type : `number`. Zones : `G117:G136`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux marginal d’IS utilisé pour désendetter le bêta de la société ; pas le taux normatif du nouveau client.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_d117_d136, comparables_e117_e136, comparables_f117_f136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max_exclusive": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max_exclusive": 1}`.

### Date des données

Identifiant : `comparables_j117_j136`. Type : `date`. Zones : `J117:J136`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date des données de l’observation bêta.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Sources et périmètre dette

Identifiant : `comparables_k117_k136`. Type : `text`. Zones : `K117:K136`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identifiant et preuve de l’observation de bêta, périmètre de dette et unité monétaire commune.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Fréquence du bêta

Identifiant : `comparables_l117_l136`. Type : `enum`. Zones : `L117:L136`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Fréquence d’observation des rendements utilisés pour le bêta.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_m117_m136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Hebdomadaire", "Mensuelle"]}`.

Choix du catalogue : ["Hebdomadaire", "Mensuelle"].

### Fenêtre du bêta en années

Identifiant : `comparables_m117_m136`. Type : `number`. Zones : `M117:M136`.

Unité explicite : années de fenêtre historique.

Assiette : Longueur de la fenêtre d’estimation du bêta ; distincte du calendrier du BP.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATE_DES_OBSERVATIONS`.

Propriétaires métier : comparables_l117_l136.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 2, "max": 5}, "choices": null}`.

Contraintes : `{"min": 2, "max": 5}`.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Multiple de sortie pondéré — `Comparables!L18`

Unité : multiple. Pondération des observations retenues ; zéro faute de panel n’est pas une source marché.

```text
IFERROR(SUMPRODUCT($L$14:$Q$16,$Y$14:$AD$16)/SUMPRODUCT(($L$14:$Q$16>0)*$Y$14:$AD$16),0)
```

Sources directes extraites : `'Comparables'!$L$14:$Q$16`, `'Comparables'!$Y$14:$AD$16`.

### Bêta désendetté de première ligne — `Comparables!I117`

Unité : coefficient. Beta levier corrigé de dette/equity et taux normatif qualifié.

```text
IF(N117="OK",D117/(1+(1-G117)*H117),"")
```

Sources directes extraites : `'Comparables'!N117`, `'Comparables'!D117`, `'Comparables'!G117`, `'Comparables'!H117`.

### Bêta médian retenu — `Comparables!D139`

Unité : coefficient. Une sélection incomplète reste non disponible.

```text
IF(COUNTIF(C117:C136,"Oui")=0,"",IF(COUNTIF(N117:N136,"OK")<>COUNTIF(C117:C136,"Oui"),"",MEDIAN(I117:I136)))
```

Sources directes extraites : `'Comparables'!C117:C136`, `'Comparables'!N117:N136`, `'Comparables'!I117:I136`.

### Validité de la sélection — `Comparables!D141`

Unité : diagnostic. Dates, sources, fréquence et fenêtre doivent être documentées.

```text
IF(COUNTIF(C117:C136,"Oui")=0,"Sélectionner des comparables TCA BP",IF(COUNTIF(N117:N136,"OK")<>COUNTIF(C117:C136,"Oui"),"Compléter toutes les lignes retenues","OK"))
```

Sources directes extraites : `'Comparables'!C117:C136`, `'Comparables'!N117:N136`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_33 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Comparable retenu : bêta1,2, equity100, dette50, taux normatif25 %, date et source complètes.

Attendu : Bêta désendetté = 1,2 / 1,375 ≈ 0,872727 ; retirer une source doit invalider la sélection, pas conserver une médiane présentée confirmée.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
