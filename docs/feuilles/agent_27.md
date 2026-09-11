# KPI Dashboard

Responsabilité : **Expliquer les indicateurs et le runway à une date donnée.**

Contrat : `AGENT_27`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel événement et quel mois souhaitez-vous étudier ?

## Règles et contrôles métier

- Restituer avec et sans financements futurs.
- Vérifier aussi les ruptures antérieures à l'apport.

## Dépendances

Sources métier du contrat : Flux de trésorerie, Financement E&S, Compte de Résultat.

Sources directes extraites : ATELIER_CIR_IS, Assumptions, BFR, Bilan, Charges_Externes, Compte de Résultat, Contrats, Control, Contrôles, Effectifs, Modèle financier, Revenue, Sensi TCA, Valorisation.

Feuilles qui consomment directement cette feuille : Modèle financier.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Date de l’événement de liquidité étudié

Identifiant : `runway_event_date`. Type : `date`. Zones : `E72`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de consultation de la liquidité ; ne crée ni encaissement ni financement.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `EXERCICES_ACTIFS_A1_A10`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["E72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `E72` : `Valorisation!$D$15`

Défaut connu =Valorisation!$D$15. Le runway part de la clôture du mois choisi. Le mois doit être dans E63:E64 ; vérifier le financement effectivement agrégé ce mois. La modification de cette date ne crée pas de financement.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Point bas mensuel — `KPI Dashboard!E65`

Unité : EUR. Un solde annuel positif peut masquer un trou de trésorerie.

```text
_xlfn.AGGREGATE(15,6,'Modèle financier'!$T$321:$EI$321/(('Modèle financier'!$T$3:$EI$3>=E63)*('Modèle financier'!$T$3:$EI$3<=E64)),1)
```

Sources directes extraites : `'Modèle financier'!$T$321:$EI$321`, `'Modèle financier'!$T$3:$EI$3`, `'KPI Dashboard'!E63`, `'KPI Dashboard'!E64`.

### Premier mois négatif — `KPI Dashboard!E68`

Unité : date. Chercher dans la fenêtre d’analyse.

```text
IF(SUMPRODUCT(('Modèle financier'!$T$321:$EI$321<0)*('Modèle financier'!$T$3:$EI$3>=E63)*('Modèle financier'!$T$3:$EI$3<=E64))=0,"Non atteint dans le plan",_xlfn.AGGREGATE(15,6,'Modèle financier'!$T$3:$EI$3/(('Modèle financier'!$T$321:$EI$321<0)*('Modèle financier'!$T$3:$EI$3>=E63)*('Modèle financier'!$T$3:$EI$3<=E64)),1))
```

Sources directes extraites : `'Modèle financier'!$T$321:$EI$321`, `'Modèle financier'!$T$3:$EI$3`, `'KPI Dashboard'!E63`, `'KPI Dashboard'!E64`.

### Mois pleins avant rupture — `KPI Dashboard!E69`

Unité : mois. Durée calendaire avant premier solde négatif, distincte d’une moyenne annuelle.

```text
IF(ISNUMBER(E68),MAX(0,(YEAR(E68)-YEAR(E63))*12+MONTH(E68)-MONTH(E63)),"Non atteinte sur "&Control!$C$12&" mois")
```

Sources directes extraites : `'KPI Dashboard'!E68`, `'KPI Dashboard'!E63`, `'Control'!$C$12`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_27 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Soldes mensuels +1 000 en janvier, -500 en février, +2 000 en mars ; fenêtre débute en janvier.

Attendu : Point bas -500 ; premier mois négatif février ; un mois plein avant rupture. Tester séparément sans financements futurs.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
