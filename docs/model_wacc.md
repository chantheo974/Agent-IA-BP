# Résolution locale du WACC

Le bouton **Résoudre le WACC**, la commande `solve-wacc` et l'outil MCP `bp_solve_wacc` utilisent le même service. Ils produisent une nouvelle version du dossier, après vérification du modèle exact, des entrées, des sources et des qualifications. Ils n'exécutent aucune macro du classeur.

Le mode **Itération** doit être choisi explicitement dans Valorisation. Les modes Manuel et Structure cible restent des modes de calcul ordinaires. Le solveur ne choisit ni méthode, ni prime, ni hypothèse de marché pour le dossier. Le taux d'IS propriétaire D9 doit être renseigné ; son relais calculé ne suffit pas à établir cette donnée.

Le contrôle documentaire vérifie les sources du calendrier, du closing, du BFR terminal, du panel de comparables, des données de marché et des primes. Excel vérifie aussi les diagnostics du modèle et la cohérence du WACC. Une hypothèse sourcée reste provisoire après un calcul réussi.

La recherche locale teste le résidu « taux calculé moins taux candidat » dans un domaine borné. Elle parcourt 80 intervalles logarithmiques, puis utilise la bissection sur un encadrement admissible. Le seuil inférieur dépasse la croissance terminale de 0,000002 ; le taux maximal recherché est 5 en unité décimale. Le budget est de 180 évaluations et 600 secondes. La valeur 0,25 utilisée comme point technique de recherche n'est jamais enregistrée comme hypothèse de marché.

Une observation doit conserver une equity positive et l'empreinte des données du modèle. Le solveur refuse une absence d'encadrement, plusieurs solutions détectées, un état invalide, des entrées modifiées ou un budget dépassé. Le statut **CONVERGENCE_LOCALE** exige un résidu absolu au plus égal à 10⁻¹⁰ et une nouvelle observation de contrôle. Ce statut ne démontre pas l'unicité mathématique sur tous les taux possibles.

Seules cinq sorties sont écrites : D136, D141, D142, D143 et D156. La cellule D136 reçoit le taux calculé ; les autres enregistrent le statut, le nombre d'évaluations, la date et l'empreinte de fraîcheur. Le calcul circulaire global d'Excel reste désactivé. L'instance Excel dédiée est identifiée avant toute action et n'est jamais confondue avec un Excel déjà ouvert par l'utilisateur.

Après le recalcul complet, le travailleur sauvegarde une copie, la rouvre et vérifie à nouveau la solution. Le service compare ensuite les signatures des entrées, des formules et des protections avant de déplacer le pointeur du dossier. Si le calcul échoue, les artefacts de diagnostic restent disponibles et la version courante reste préservée.

Le reçu JSON accompagne la copie. Toute saisie ultérieure invalide la preuve ; un changement de source ou de qualification invalide la disponibilité financière. Une vérification des sensibilités peut conserver une preuve WACC courante seulement si elle démontre la conservation des cinq sorties et de la même signature d'entrée.

La recette logicielle comporte des fonctions synthétiques pour les limites de recherche et un dossier Excel fictif sans dette : taux sans risque de 3 %, bêta de 1,2, prime de marché de 5 % et primes additionnelles nulles, soit un WACC attendu de 9 %. L'equity attendue est calculée séparément depuis trois flux de 72 000 euros et une croissance terminale fictive de 2 %. Ces données ne sont pas des valeurs par défaut du modèle distribué.
