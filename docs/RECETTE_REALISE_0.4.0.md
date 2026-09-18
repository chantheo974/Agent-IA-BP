# Recette du réalisé et du raccord — 0.4.0

Cette recette utilise exclusivement des données fictives. Les conventions fiscales sont des hypothèses mathématiques sourcées pour le test ; elles ne représentent pas une validation de règles fiscales applicables à une entreprise.

## Périmètre et attentes indépendantes

Le budget initial reste figé. Un prix unitaire porté à 110 EUR donne, dans le modèle courant avant raccord, 11 000 EUR de chiffre d’affaires et 7 000 EUR de résultat en janvier 2026, puis 132 000 EUR de chiffre d’affaires et 84 000 EUR de résultat sur l’année. Le réalisé adopté de janvier reste à 10 000 EUR de chiffre d’affaires, 6 000 EUR de résultat et 106 000 EUR de trésorerie.

Le raccord est construit à partir de ce réalisé, d’un checkpoint documenté du modèle au 31 janvier et de huit politiques explicitement sourcées. Les huit écarts sont conservés ; aucun événement supplémentaire n’est supposé. Les créances, stocks, fournisseurs et dettes du témoin sont explicitement nuls. Les montants attendus sont calculés indépendamment du générateur de formules :

| Contrôle | Attente |
|---|---:|
| Trésorerie réalisée de janvier | 106 000 EUR |
| Trésorerie actualisée de février | 113 000 EUR |
| Chiffre d’affaires actualisé de 2026 | 131 000 EUR |
| Résultat actualisé de 2026 | 83 000 EUR |
| Actif et capitaux propres annuels | Valeur du modèle courant diminuée de 1 000 EUR |
| Passif hors capitaux propres | Identique au modèle courant |
| Contrôles annuels du modèle et du raccord | Écart nul |

Les formules du modèle d’origine restent présentes. Les trois feuilles gérées sont `TCA Réalisé`, `TCA Actualisé` et `TCA Raccord`. Le raccord ajoute uniquement les écarts nets au modèle courant, afin de ne pas reprendre une deuxième fois les flux déjà calculés.

## Preuves et état de la recette

Le programme de recette est `tools/validate_reforecast_service.py`. Il limite son exécution au dossier fictif désigné, exige une révision et une empreinte explicites, conserve chaque tentative et produit un reçu distinct. Son mode de consultation est en lecture seule.

Les 16 tests logiciels de `tests.test_decision_reforecast` et `tests.test_decision_reforecast_bridge` sont passés. Ils couvrent notamment les écritures équilibrées, les échéanciers manquants, le contrôle des sources, l’absence de double comptage, l’obsolescence du checkpoint, la continuité de trésorerie, les dix années et la conservation du budget. Ils ne constituent pas un recalcul Excel.

Le premier aperçu réel a été refusé avant adoption : Excel avait retiré les apostrophes facultatives autour du nom `BFR`. Le reçu `validation_reforecast_service_20260913_033101_543885.json` conserve ce refus et ses 120 diagnostics. La correction de comparaison préserve les chaînes de texte et les références absolues. Le fichier natif exact et sa chaîne d’empreintes ont ensuite été figés pour repasser les contrôles communs ; cette revalidation n’est pas présentée comme une nouvelle écriture Excel.

**Recette TCA réussie : 25 contrôles sur 25.** L’aperçu revalidé est adopté en révision 5, puis le recalcul natif crée la révision 6. `CalculateFullRebuild`, l’état de calcul 0 et la réouverture du fichier sont attestés ; les entrées et la source sont conservées et les macros restent désactivées. Le calcul a duré 120,32 secondes. Les quatre périmètres CA, COGS, trésorerie et fiscalité sont disponibles sur les prérequis fictifs qualifiés, et le lecteur du raccord retourne `EXPLICABLE` sans diagnostic.

Les résultats observés correspondent au tableau ci-dessus. Les actifs et capitaux propres annuels actualisés sont de 183 000, 255 000 et 327 000 EUR pour 2026 à 2028 ; les résultats sont de 83 000, 72 000 et 72 000 EUR. Tous les contrôles de bilan sont nuls. Le budget et le réalisé adoptés sont inchangés. Aucun lien externe n’a été créé.

Les quatre fichiers `TCA_BP.xlsm`, `rapport.pdf`, `rapport.docx` et `presentation.pptx` sont produits à partir de la révision 6 et de son même instantané, dans le livrable `report_3b238b821ef44d089f237730f69c9659`. Le XLSM exporté porte l’identité du dossier, de cette révision et de cet instantané. La correction du prix à 110 EUR constitue le point de départ documenté par `validation_roundtrip_prix_adoption.json` ; le raccord utilise ensuite le réalisé de janvier déjà adopté, sans le réécrire.

Les reçus complets restent dans le dossier privé `runtime/recette_qualifications_service_20260913_013101_ae260a` :

| Reçu | Résultat | SHA-256 |
|---|---|---|
| `validation_reforecast_service_20260913_034617_0d01b3.json` | 25/25 ; natif, restitution et quatre formats | `9b9fea8211fe8d41b6bbd9e2ea26e9287deb57e6e0d3eb98c3746022f8655bc9` |
| `validation_reforecast_restore_20260913_041357_d22ec2.json` | 9/9 ; restauration, rejeu et téléchargement | `4f453d3f239b776184841eaa4cea52a1e35848f28dea04022b6ed1f74fac8944` |

Le classeur calculé de révision 6 a pour empreinte `cf7c669953d3b7dac1bcc59d3ca6f746c8cd7c12563f5a426471e15879839c2d`. Les reçus de refus initiaux sont conservés séparément ; ils n’ont pas été remplacés par le succès.

Un petit témoin distinct couvre des écarts non nuls de créances, fournisseurs, stock et dette, avec encaissement, remboursement et perte de stock explicitement documentés. Ses **17 attentes indépendantes passent après un vrai recalcul Excel et une réouverture**, avec état de calcul 0, aucun lien externe et restitution `EXPLICABLE` : trésorerie de février 218, actif annuel 336, passif 98, capitaux propres 238 et résultat 43. Son reçu est `runtime/recette_bridge_20260913_ordre_corrige/production_invalidated_20260913_035004_8e3b5f/oracle_receipt.json`. Le protocole de calcul est celui de production ; seuls les adaptateurs de preuve du classeur sans macros, des sources et des qualifications sont propres au témoin. Cette preuve de composant ne remplace pas la recette complète du dossier TCA.

Les anciens appels directs du petit témoin omettaient l’invalidation des caches et le réglage avant ouverture appliqués normalement par le parcours de production ; Excel restait dans un état « en attente ». Les refus sont conservés. L’application des helpers de production avant la première ouverture permet le succès natif en 12,53 secondes, sans modifier le worker livré.

## Conditions de restitution et limites

`read_reforecast` relit les cellules calculées de la version effectivement courante. Le statut `EXPLICABLE` exige un recalcul courant, les qualifications CA/COGS/trésorerie/fiscalité, les sources intactes, les mêmes réalisé/budget/checkpoint, les formules gérées attendues, la continuité de trésorerie et les contrôles annuels équilibrés. Une hypothèse manquante reste une question ; une formule indisponible reste `#N/A` puis une valeur non disponible à l’écran.

La restitution fournit un bilan annuel agrégé. Elle ne remplace pas une balance comptable détaillée, des échéanciers de règlement ou une qualification fiscale. Tout événement supplémentaire doit être décrit par des écritures équilibrées et sourcées ; son éventuel effet fiscal doit être explicite.

Cette recette n’a pas exécuté le solveur WACC ni validé les tables de sensibilité. La DCF reste indisponible sur cette variante, avec sa preuve WACC manquante et ses erreurs de valorisation signalées ; cela n’est pas masqué par le succès du raccord.

Les métriques générales, scénarios, objectifs et sensibilités du modèle courant restent distincts de la vue actualisée tant qu’un raccord propre au scénario n’a pas été préparé et recalculé. Une modification ultérieure du modèle invalide le checkpoint du raccord ; elle n’autorise pas sa réutilisation automatique.

Le test `--restore-from-receipt` a restauré le contenu de la révision 4 en créant la **révision 7**, sans Excel. Les 38 fichiers contrôlés des versions, sources, livrables et du reçu précédent sont conservés, ainsi que le budget et le réalisé. Le même identifiant d’opération rejoué ne crée aucune révision supplémentaire. Le téléchargement HTTP renvoie le XLSM exact avec le type attendu. La révision 7 est correctement marquée `A_RECALCULER` : la restauration ne lui attribue pas une nouvelle fraîcheur financière. Le reçu réussi et les quatre livrables du raccord de révision 6 restent disponibles séparément.
