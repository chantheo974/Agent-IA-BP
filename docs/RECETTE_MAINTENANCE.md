# Recette de maintenance du 11 septembre 2026

Le parcours **proposition → construction d'une variante → validation native** a été exécuté réellement par les commandes CLI. L'oracle calendrier est **PASS**. La variante reste **EXPERIMENTALE** : aucune approbation nominative ni publication n'a été exécutée.

## Modification et attente indépendante

Une seule formule existante a été modifiée, `Control!C60` :

```text
Avant : YEAR($C$10)+$C$59-1
Après : YEAR($C$10)+SUM($C$59,-1)
```

Il s'agit d'une réécriture équivalente de la dernière année de l'horizon. Elle vérifie le mécanisme de maintenance sans introduire une nouvelle règle économique. Les tests unitaires distincts vérifient aussi un changement de résultat et la conservation d'une formule partagée voisine.

Le scénario fictif saisit une date de départ au **1er janvier 2030** et un horizon de **trois exercices**. L'attendu indépendant vient de la liste 2030, 2031, 2032 : **2032**. La valeur relue après Excel est exactement **2032**.

Les données et changements reproductibles se trouvent dans [les changements JSON](exemples/maintenance-calendrier-changements.json) et [le scénario JSON](exemples/maintenance-calendrier-scenarios.json).

## Exécution et intégrité

- Modèle de départ : `tca-bp-template/1`.
- Variante : `tca-bp-template/verification-calendrier-1`.
- Microsoft Excel **16.0**, méthode **CalculateFullRebuild**.
- Calcul natif terminé le **11 septembre 2026 à 17:45:28 UTC**, état de calcul **0**.
- Macros désactivées, WACC non exécuté, tables de sensibilité non vérifiées.
- Concordance des empreintes source et sortie, compatibilité de la variante et signature des entrées vérifiées.
- La trame de départ et la variante scellée sont restées inchangées ; le calcul porte sur une copie avec entrées fictives.
- Aucun dossier client n'a été créé ou migré par cette recette. `publication.json` est absent.

| Artefact | SHA-256 |
|---|---|
| Trame de départ | `15815c1062653d72cd7686334a3d080aeb88b9eb8f6f6fa75b6c7195409ed663` |
| Variante scellée | `f00390e67c0a4db05b87e4f1dda362f03b9144e0713182064d4ed0bf0944991f` |
| Manifeste de la variante | `70ba736883e421f03934076467e00321551e5fa0cc66295845b87c4efe558b11` |
| Copie recalculée | `b4ba38f3dfaabb69ee17db6ac06f40777e67cb5f0fdbda78a18cd17a65341438` |
| Rapport de validation | `da80a514905546b3c9029adfdaa98f075fa5c34289fb7a30550fee6ca27bdb40` |

## Preuves locales

- [Proposition CLI](../models/maintenance/recette-calendrier/proposition.json).
- [Construction CLI](../models/maintenance/recette-calendrier/construction.json).
- [Rapport de validation](../models/versions/version_c0a12a923c257b4381af/validation/run_206b008de4f94701a3f0cc24c5606b2e/validation.json).
- [Reçu natif Excel](../models/versions/version_c0a12a923c257b4381af/validation/run_206b008de4f94701a3f0cc24c5606b2e/scenario_001/native.json).

Les classeurs et reçus de travail sont conservés localement dans les répertoires ignorés par Git ; les liens supposent donc la présence de cette recette locale.

## Limites constatées

Le modèle est resté vide de données commerciales, avec ses offres et registres inactifs. Le recalcul révèle **33 erreurs globales hors de l'oracle calendrier** : 3 `#VALUE!`, 29 `#N/A` et 1 `#DIV/0!`, dans Contrôles et Valorisation. Elles sont détaillées dans le rapport. Le résultat `PASS` porte exclusivement sur l'oracle de calendrier et n'efface pas ces erreurs.

Ce constat appartient à la référence de développement antérieure, conservée avec ses preuves. Les quatre erreurs `#VALUE!` et `#DIV/0!` ont ensuite été corrigées et testées séparément dans la génération 1.0.1, sans réécriture de ce reçu historique ; voir la [recette de livraison](RECETTE_VALIDATION.md).

Cette recette ne valide ni les résultats financiers, ni les hypothèses fiscales, ni la valorisation, ni les tables natives ou le WACC. Le rapport garde explicitement `financial_results_verified: false`. Une évolution économique réelle exige ses propres scénarios, contrôles des consommateurs et décision du responsable.

Les **11 tests ciblés de maintenance** et **3 tests de reprise** ont également réussi, y compris l'altération d'un indicateur PASS, la modification d'un scénario, le verrou tronqué et la panne de journal après commit. Ces tests utilisent des fixtures fictives et ne remplacent pas l'exécution Excel décrite ci-dessus.
