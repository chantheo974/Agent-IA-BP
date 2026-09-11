# Plan de financement

Responsabilité : **Expliquer besoins, ressources et déficits dans le temps.**

Contrat : `AGENT_26`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel besoin, quel horizon et quelles ressources sont réellement documentés ?

## Règles et contrôles métier

- Présenter le déficit sans inventer une ressource compensatrice.

## Dépendances

Sources métier du contrat : Flux de trésorerie, Financement Dette, Financement E&S.

Sources directes extraites : ATELIER_CIR_IS, Compte de Résultat, Control, Modèle financier, Revenue.

Feuilles qui consomment directement cette feuille : Bilan, Contrôles, Flux de trésorerie.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Total emplois — `Plan de financement!D22`

Unité : EUR/an. Besoins d’exploitation et d’investissement selon signe de présentation.

```text
SUM(D9:D21)
```

Sources directes extraites : `'Plan de financement'!D9:D21`.

### Total ressources — `Plan de financement!D38`

Unité : EUR/an. Ressources réellement documentées.

```text
D29+SUM(D30:D36)
```

Sources directes extraites : `'Plan de financement'!D29`, `'Plan de financement'!D30:D36`.

### Trésorerie finale — `Plan de financement!D42`

Unité : EUR fin année. Ouverture et solde ressources/emplois, sans apport automatique d’équilibrage.

```text
D41+D40
```

Sources directes extraites : `'Plan de financement'!D41`, `'Plan de financement'!D40`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_26 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Ouverture 10 000, emplois 15 000, ressources 2 000.

Attendu : Clôture -3 000 et besoin visible ; aucune nouvelle dette de 3 000 ne doit être inventée.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
