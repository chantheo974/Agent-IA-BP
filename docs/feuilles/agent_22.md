# Modèle financier

Responsabilité : **Expliquer la consolidation mensuelle de tous les modules.**

Contrat : `AGENT_22`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel flux et quel mois faut-il retracer jusqu'aux entrées ?

## Règles et contrôles métier

- Rapprocher les modules en conservant leurs unités et calendriers.

## Dépendances

Sources métier du contrat : Revenue, COGS, Charges_Externes, Effectifs, CAPEX, Financement Dette, Financement E&S, ATELIER_CIR_IS.

Sources directes extraites : ATELIER_CIR_IS, Assumptions, CAPEX, COGS, Charges_Externes, Control, Effectifs, Financement Dette, Financement E&S, KPI Dashboard, Revenue, SUBVENTION_INVEST, Sensi TCA, Stock.

Feuilles qui consomment directement cette feuille : ATELIER_CIR_IS, BFR, Bilan, CALCUL_CIR, Charges_Externes, Compte de Résultat, Contrôles, Effectifs, Financement Dette, Financement E&S, Flux de trésorerie, KPI Dashboard, Plan de financement, Previsionnel, SUBVENTION_INVEST, Sensi TCA, Valorisation.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Encaissements clients — `Modèle financier!C268`

Unité : EUR/an. Consolider le cash du module Revenue.

```text
SUMPRODUCT((YEAR($T$3:$QI$3)=C$3)*$T268:$QI268)
```

Sources directes extraites : `'Modèle financier'!$T$3:$QI$3`, `'Modèle financier'!C$3`, `'Modèle financier'!$T268:$QI268`.

### Encaissements totaux — `Modèle financier!C301`

Unité : EUR/an. Activité, fiscalité et financements sont des flux distincts.

```text
SUMPRODUCT((YEAR($T$3:$QI$3)=C$3)*$T301:$QI301)
```

Sources directes extraites : `'Modèle financier'!$T$3:$QI$3`, `'Modèle financier'!C$3`, `'Modèle financier'!$T301:$QI301`.

### Décaissements totaux — `Modèle financier!C320`

Unité : EUR/an. Consolider sans doubler investissements, loyers ou capital de dette.

```text
SUMPRODUCT((YEAR($T$3:$QI$3)=C$3)*$T320:$QI320)
```

Sources directes extraites : `'Modèle financier'!$T$3:$QI$3`, `'Modèle financier'!C$3`, `'Modèle financier'!$T320:$QI320`.

### Trésorerie mensuelle — `Modèle financier!T321`

Unité : EUR fin mois. Ouverture plus encaissements moins décaissements, puis report au mois suivant.

```text
N321+T301-T320
```

Sources directes extraites : `'Modèle financier'!N321`, `'Modèle financier'!T301`, `'Modèle financier'!T320`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_22 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Ouverture 10 000, encaissements 2 000, décaissements 3 000 dans un mois fictif.

Attendu : Clôture mensuelle 9 000 ; ouverture du mois suivant 9 000. Rapprocher les modules des deux flux.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
