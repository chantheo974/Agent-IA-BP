# Control

Responsabilité : **Qualifier le calendrier, les paramètres techniques et les soldes d'ouverture.**

Contrat : `AGENT_03`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quelle date de départ et combien d'exercices actifs ?
- Quels soldes d'ouverture sont justifiés et quand sont-ils réglés ?

## Règles et contrôles métier

- L'horizon ne dépasse pas la capacité technique.
- Un changement de départ nécessite de traiter les soldes antérieurs.

## Dépendances

Sources métier du contrat : aucune dépendance métier déclarée.

Sources directes extraites : Assumptions, Bilan, DATA COGS, Sensi TCA.

Feuilles qui consomment directement cette feuille : ATELIER_CIR_IS, Assumptions, BFR, Bilan, CAPEX, COGS, Charges_Externes, Contrats, Contrôles, DATA COGS, DATA Contrats, Effectifs, Flux de trésorerie, KPI Dashboard, Modèle financier, Plan de financement, Revenue, Sensi Analyses, Sensi TCA, Stock, Valorisation.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Jours conventionnels par mois

Identifiant : `conventional_month_days`. Type : `number`. Zones : `C13`.

Unité explicite : jours par mois conventionnel.

Assiette : Diviseur technique de conversion des délais en mois ; doit être strictement positif.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"exclusive_min": 0}, "choices": null}`.

Contraintes : `{"exclusive_min": 0}`.

Paramètre global : impact sur tous les délais mensuels. Modifier uniquement avec convention explicite.

### Flexeur de capacité industrielle

Identifiant : `industrial_capacity_factor`. Type : `number`. Zones : `C24`.

Unité explicite : coefficient multiplicatif.

Assiette : Multiplicateur de la capacité industrielle documentée, pas un pourcentage saisi sur 100.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Créances clients d’ouverture

Identifiant : `opening_receivables`. Type : `number`. Zones : `C28`.

Unité explicite : EUR de solde comptable.

Assiette : Solde d’ouverture du poste désigné, avec sa ventilation et contrepartie documentées ; ne pas assimiler automatiquement à une base HT.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.

### Acomptes clients/PCA d’ouverture

Identifiant : `opening_customer_advances`. Type : `number`. Zones : `C29`.

Unité explicite : EUR de solde comptable.

Assiette : Solde d’ouverture du poste désigné, avec sa ventilation et contrepartie documentées ; ne pas assimiler automatiquement à une base HT.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.
Non nul : le contrôle C57 demande une allocation historique ; une simple saisie ne complète pas la ventilation.

### Produits à recevoir/FAE d’ouverture

Identifiant : `opening_unbilled_revenue`. Type : `number`. Zones : `C30`.

Unité explicite : EUR de solde comptable.

Assiette : Solde d’ouverture du poste désigné, avec sa ventilation et contrepartie documentées ; ne pas assimiler automatiquement à une base HT.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.
Non nul : le contrôle C57 demande une allocation historique ; une simple saisie ne complète pas la ventilation.

### Stock d’ouverture

Identifiant : `opening_stock`. Type : `number`. Zones : `C31`.

Unité explicite : EUR de solde comptable.

Assiette : Solde d’ouverture du poste désigné, avec sa ventilation et contrepartie documentées ; ne pas assimiler automatiquement à une base HT.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.

### Fournisseurs d’ouverture

Identifiant : `opening_payables`. Type : `number`. Zones : `C32`.

Unité explicite : EUR de solde comptable.

Assiette : Solde d’ouverture du poste désigné, avec sa ventilation et contrepartie documentées ; ne pas assimiler automatiquement à une base HT.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.

### unités installées installés à l’ouverture

Identifiant : `installed_interceptors`. Type : `number`. Zones : `C33`.

Unité explicite : unités installées de la catégorie technique désignée.

Assiette : Parc installé à l’ouverture ; catégorie technique existante à relier explicitement à l’activité du nouveau dossier.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.

### Modules OEM installés à l’ouverture

Identifiant : `installed_oem`. Type : `number`. Zones : `C34`.

Unité explicite : unités installées de la catégorie technique désignée.

Assiette : Parc installé à l’ouverture ; catégorie technique existante à relier explicitement à l’activité du nouveau dossier.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `HORS_CALENDRIER`.

Propriétaires métier : model_start_date, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Donnée historique sourcée ; ne pas calculer un montant de bouclage.

### Date d’encaissement des créances d’ouverture

Identifiant : `opening_receivables_cash_date`. Type : `date`. Zones : `C54`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de règlement du solde d’ouverture correspondant.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, opening_receivables, opening_payables.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Bornes exactes : Control!C10 à EDATE(Control!C10,Control!C12)-1.

### Date de règlement fournisseurs d’ouverture

Identifiant : `opening_payables_cash_date`. Type : `date`. Zones : `C55`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de règlement du solde d’ouverture correspondant.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, opening_receivables, opening_payables.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Bornes exactes : Control!C10 à EDATE(Control!C10,Control!C12)-1.

### Nombre d’années actives

Identifiant : `active_horizon_years`. Type : `integer`. Zones : `C59`.

Unité explicite : nombre entier d’exercices actifs.

Assiette : Horizon actif compris dans la capacité technique de dix exercices ; distinct de la capacité.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["C59"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 1, "max_ref": "Control!C11", "source_max": 10}, "choices": null}`.

Contraintes : `{"min": 1, "max_ref": "Control!C11", "source_max": 10}`.

Ne pas étendre implicitement le plan : disposer des hypothèses futures nécessaires. La capacité structurelle C11 reste inchangée.

### Date de début du modèle

Identifiant : `model_start_date`. Type : `date`. Zones : `C10`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Premier jour du premier exercice ; le modèle accepte le 1er janvier dans ses bornes.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["C10"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"allow_blank": false}, "choices": null}`.

Contraintes : `{"allow_blank": false}`.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Dernier exercice actif — `Control!C60`

Unité : année. Départ plus nombre d’exercices moins un.

```text
YEAR($C$10)+$C$59-1
```

Sources directes extraites : `'Control'!$C$10`, `'Control'!$C$59`.

### Capacité du calendrier en mois — `Control!C12`

Unité : mois. Lire le nombre d’années source et sa conversion en mois.

```text
$B$6*12
```

Sources directes extraites : `'Control'!$B$6`.

### Écart des ouvertures — `Control!C56`

Unité : EUR. Diagnostic renvoyé par Bilan C59 ; une dette ou créance antérieure ne disparaît pas en décalant le calendrier.

```text
Bilan!C59
```

Sources directes extraites : `'Bilan'!C59`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_03 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Départ au 1er janvier 2030 et trois exercices, sans actif ou dette antérieur.

Attendu : C60 vaut 2032. Avec soldes antérieurs, demander leurs échéanciers avant de déplacer la date.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
