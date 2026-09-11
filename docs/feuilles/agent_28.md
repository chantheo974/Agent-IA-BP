# Contrôles

Responsabilité : **Classer les alertes et solliciter les agents de leurs sources.**

Contrat : `AGENT_28`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quelle alerte, quelle période et quelle dernière preuve de recalcul ?

## Règles et contrôles métier

- Ne pas effacer une alerte en modifiant son contrôle.
- Un contrôle vert ne certifie pas les hypothèses.

## Dépendances

Sources métier du contrat : Bilan, BFR, Flux de trésorerie, Compte de Résultat.

Sources directes extraites : ATELIER_CIR_IS, Assumptions, BFR, Bilan, CALCUL_CIR, CAPEX, COGS, Comparables, Compte de Résultat, Contrats, Control, DATA CAPEX, DATA COGS, DATA Contrats, DATA Financement, Effectifs, Financement Dette, Financement E&S, Flux de trésorerie, Modèle financier, Plan de financement, Revenue, SUBVENTION_INVEST, Sensi Analyses, Sensi TCA, Valorisation.

Feuilles qui consomment directement cette feuille : KPI Dashboard.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Bilan contre plan de financement — `Contrôles!C13`

Unité : EUR. Comparer deux lectures de la trésorerie.

```text
IF(C$11>Control!$C$60,0,Bilan!D18-'Plan de financement'!D42)
```

Sources directes extraites : `'Contrôles'!C$11`, `'Control'!$C$60`, `'Bilan'!D18`, `'Plan de financement'!D42`.

### Flux contre plan de financement — `Contrôles!C14`

Unité : EUR. Troisième lecture du cash.

```text
IF(C$11>Control!$C$60,0,'Flux de trésorerie'!D26-'Plan de financement'!D42)
```

Sources directes extraites : `'Contrôles'!C$11`, `'Control'!$C$60`, `'Flux de trésorerie'!D26`, `'Plan de financement'!D42`.

### BFR contre bilan — `Contrôles!C83`

Unité : EUR. Rapprochement des postes circulants.

```text
SUMPRODUCT(ABS(BFR!$E$42:INDEX(BFR!$E$42:$N$42,1,Control!$C$59)))
```

Sources directes extraites : `'BFR'!$E$42`, `'BFR'!$E$42:$N$42`, `'Control'!$C$59`.

### Validité valorisation — `Contrôles!C121`

Unité : diagnostic. Un contrôle exige son périmètre et la qualification de ses entrées.

```text
IF(AND(ISNUMBER(Valorisation!$D$57),ISNUMBER('Financement E&S'!$F$7)),Valorisation!$D$57-'Financement E&S'!$F$7,"Non renseigné")
```

Sources directes extraites : `'Valorisation'!$D$57`, `'Financement E&S'!$F$7`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_28 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Trois lectures de cash concordent à 9 000 ; puis altération fictive de 1 EUR dans une sortie sur une copie de test.

Attendu : Écarts de cash initialement 0 ; anomalie visible et écriture directe refusée en saisie courante. Un contrôle vert ne qualifie pas les hypothèses.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
