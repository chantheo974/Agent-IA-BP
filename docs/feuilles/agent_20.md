# CALCUL_CIR

Responsabilité : **Rapprocher les dépenses R&D et qualifications documentées.**

Contrat : `AGENT_20`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Qui confirme la qualification de la dépense, pour quel exercice et sur quelle pièce ?

## Règles et contrôles métier

- Ne pas déduire deux fois une aide de l'assiette.
- Ne jamais inférer l'éligibilité depuis le nom du projet.

## Dépendances

Sources métier du contrat : Effectifs, DATA CAPEX, DATA Financement.

Sources directes extraites : Assumptions, CAPEX, Effectifs, Financement Dette, Financement E&S, Modèle financier, SUBVENTION_INVEST.

Feuilles qui consomment directement cette feuille : ATELIER_CIR_IS, Contrôles, Sensi TCA.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Sous-traitance R&D documentée euros

Identifiant : `calcul_cir_c18_m18`. Type : `number`. Zones : `C18:M18`.

Unité explicite : EUR par exercice.

Assiette : Dépense ou mouvement d’aide désigné par le champ ; additions et déductions séparées, éligibilité documentée avant taux.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Frais de normalisation euros

Identifiant : `calcul_cir_c19_m19`. Type : `number`. Zones : `C19:M19`.

Unité explicite : EUR par exercice.

Assiette : Dépense ou mouvement d’aide désigné par le champ ; additions et déductions séparées, éligibilité documentée avant taux.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Aides R&D supplémentaires à déduire euros

Identifiant : `calcul_cir_c41_m41`. Type : `number`. Zones : `C41:M41`.

Unité explicite : EUR par exercice.

Assiette : Dépense ou mouvement d’aide désigné par le champ ; additions et déductions séparées, éligibilité documentée avant taux.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Remboursements d’aides à réintégrer euros

Identifiant : `calcul_cir_c42_m42`. Type : `number`. Zones : `C42:M42`.

Unité explicite : EUR par exercice.

Assiette : Dépense ou mouvement d’aide désigné par le champ ; additions et déductions séparées, éligibilité documentée avant taux.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Qualification des aides / affectation R&D

Identifiant : `calcul_cir_c43_m43`. Type : `text`. Zones : `C43:M43`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Qualification et sources des aides R&D de l’exercice ; texte non probant sans pièce et état documentaire.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Sources et explication de la ventilation des aides

Identifiant : `calcul_cir_c44_m44`. Type : `text`. Zones : `C44:M44`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Qualification et sources des aides R&D de l’exercice ; texte non probant sans pièce et état documentaire.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_FISCAUX_ACTIFS`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Dépenses brutes retenues — `CALCUL_CIR!C28`

Unité : EUR/an. Assembler dépenses et forfaits seulement après qualification.

```text
C16+C17+C24+C26+C27+N(C42)
```

Sources directes extraites : `'CALCUL_CIR'!C16`, `'CALCUL_CIR'!C17`, `'CALCUL_CIR'!C24`, `'CALCUL_CIR'!C26`, `'CALCUL_CIR'!C27`, `'CALCUL_CIR'!C42`.

### Aides déduites — `CALCUL_CIR!C29`

Unité : EUR/an. Aides et reprises concernées déduites une seule fois.

```text
-C20
```

Sources directes extraites : `'CALCUL_CIR'!C20`.

### Assiette nette — `CALCUL_CIR!C30`

Unité : EUR/an. Base après déductions, plancher zéro ; aucune éligibilité déduite du nom de projet.

```text
MAX(0,C28+C29)
```

Sources directes extraites : `'CALCUL_CIR'!C28`, `'CALCUL_CIR'!C29`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_20 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Dépenses éligibles brutes explicitement qualifiées 100 000, aides déductibles 20 000.

Attendu : Assiette nette 80 000 ; si déduction 120 000, plancher zéro. Le taux fiscal n’est pas présumé.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
