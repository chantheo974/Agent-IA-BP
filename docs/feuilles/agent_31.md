# Sensi Graphiques

Responsabilité : **Expliquer les séries, unités et légendes des sensibilités.**

Contrat : `AGENT_31`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quelle série, quelle unité et quel scénario souhaitez-vous représenter ?

## Règles et contrôles métier

- La série présentée doit correspondre à des résultats recalculés.

## Dépendances

Sources métier du contrat : Sensi Analyses.

Sources directes extraites : Sensi Analyses.

Feuilles qui consomment directement cette feuille : aucune.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Scénario affiché — `Sensi Graphiques!B4`

Unité : texte. Relais de Sensi Analyses ; les séries sont extraites des composants graphiques, pas de ce seul titre.

```text
'Sensi Analyses'!B4
```

Sources directes extraites : `'Sensi Analyses'!B4`.

## Séries des graphiques

Références XML liées à cette feuille ; leurs caches ne constituent pas une preuve de recalcul.

- `xl/charts/chart3.xml` : `'Sensi Analyses'!$J$25:$J$33`, `'Sensi Analyses'!$K$25:$K$33`
- `xl/charts/chart2.xml` : `'Sensi Analyses'!$D$49`, `'Sensi Analyses'!$C$50:$C$52`, `'Sensi Analyses'!$D$50:$D$52`, `'Sensi Analyses'!$E$49`, `'Sensi Analyses'!$C$50:$C$52`, `'Sensi Analyses'!$E$50:$E$52`, `'Sensi Analyses'!$F$49`, `'Sensi Analyses'!$C$50:$C$52`, `'Sensi Analyses'!$F$50:$F$52`
- `xl/charts/chart1.xml` : `'Sensi Analyses'!$B$40:$B$45`, `'Sensi Analyses'!$C$40:$C$45`, `'Sensi Analyses'!$B$40:$B$45`, `'Sensi Analyses'!$D$40:$D$45`
- `xl/charts/chart4.xml` : `'Sensi Analyses'!$N$25:$N$33`, `'Sensi Analyses'!$O$25:$O$33`

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_31 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Après scénario vérifié, comparer points et catégories du graphique aux cellules de sa série.

Attendu : Chaque point représente sa source native actuelle, unités et axes cohérents ; pas de cache graphique hérité. Les références XML exactes sont listées dans la fiche.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
