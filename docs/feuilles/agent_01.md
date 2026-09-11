# Légende

Responsabilité : **Expliquer les conventions, unités et droits de saisie.**

Contrat : `AGENT_01`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quelle convention ou unité souhaitez-vous comprendre ?

## Règles et contrôles métier

- La couleur ne remplace jamais la liste des entrées autorisées.

## Dépendances

Sources métier du contrat : aucune dépendance métier déclarée.

Sources directes extraites : aucune.

Feuilles qui consomment directement cette feuille : aucune.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Saisie et défaut modifiable — `Légende!B6`

Unité : convention. La couleur décrit un usage ; seul le catalogue accorde un droit.

Cellule documentaire ou de saisie sans formule ; aucun calcul n'est supposé.

### Lien interfeuille — `Légende!B8`

Unité : convention. Remonter à la feuille source sans modifier le résultat.

Cellule documentaire ou de saisie sans formule ; aucun calcul n'est supposé.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_01 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Présenter une cellule colorée hors catalogue.

Attendu : La proposition est refusée ; couleur et protection ne remplacent pas la liste blanche.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
