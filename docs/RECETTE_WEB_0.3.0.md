# Recette de TCA BP Web 0.3.0 — 12 septembre 2026

L’atelier est une interface React/TypeScript servie localement par FastAPI, devant le service Python 3.14 existant. Les essais ci-dessous utilisent des dossiers fictifs et des copies isolées. Ils ne certifient pas les hypothèses économiques d’un dossier client.

## Vérifications réalisées

| Vérification | Résultat constaté |
|---|---|
| Suite complète du logiciel | 489 tests réussis. |
| Suite web après les corrections finales | 99 tests réussis, couvrant API, agents, sources, migrations, reprise, jeton d’aperçu, MCP et caches graphiques. Ce total recoupe la suite complète. |
| Interface dans Chromium | 10 scénarios réussis ; compilation TypeScript/Vite réussie. |
| Navigateur avec serveur réel | Création d’un dossier fictif, ajout d’une source, date au format ISO, brouillon conservé après rechargement et téléchargement exact du XLSM. |
| Parcours API avec Excel natif | 19 contrôles réussis : brouillon manuel complété par un coordinateur simulé, recrutement documenté, insertion/renommage, nouveau rôle de feuille, aperçu, adoption, recalcul, téléchargement et restauration. |
| Charges de personnel après déplacement | 63 000 euros la première année et 84 000 euros la suivante, conformes aux calculs indépendants de la recette. |
| Formule dans une feuille ajoutée | Valeur calculée de 24, après saisie de 12 et formule de doublement. |
| Valorisation après déplacement des cibles | 8 oracles financiers et 12 contrôles techniques réussis dans Excel. |
| Sensibilités après renommage et insertion d’une ligne/colonne | 2 scénarios exécutés dans le vrai worker : 4 oracles et 5 contrôles réussis. Chiffres d’affaires de 75 600 / 118 800 euros et points bas de trésorerie de −45 600 / −48 800 euros. |
| Préservation des sources | Les 10 documents d’origine, les 3 fichiers fournisseur gelés et les éléments déjà préparés dans Git restent identiques. |
| Connexion au fournisseur réel | Non exécutée : aucune clé API enregistrée. Les essais IA valident le protocole HTTP/SSE, les appels aux spécialistes, les erreurs et la reprise avec un fournisseur simulé. |

Les recettes natives prouvent les sources VBA conservées et l’absence d’exécution des macros. Excel peut réenregistrer les flux compilés du projet VBA ; l’identité binaire complète n’est donc pas confondue avec la préservation du code et des composants.

## Limites et interprétation

- Un déplacement conserve l’identité métier. Une formule ou une constante métier modifiée exige une nouvelle qualification ; un simple recalcul ne renouvelle pas les preuves financières antérieures.
- Une ligne créée est éditable, mais n’étend pas automatiquement le contrat d’un registre. Une nouvelle feuille possède un rôle d’agent explicite.
- Une suppression d’un propriétaire indispensable, une référence cassée ou une protection non reproductible bloque le lot. Le brouillon reste inspectable.
- La recette ciblée des sensibilités vérifie les nouvelles coordonnées ; elle ne constitue pas une nouvelle qualification de l’ensemble des 57 sorties des trois tables.
- Fermer le navigateur conserve les travaux du serveur. Une coupure du fournisseur n’applique aucune proposition partielle. Après un arrêt brutal du serveur, les travaux sont marqués interrompus ; un verrou de dossier résiduel reste à diagnostiquer, sans suppression automatique.
- Les changements de formule/structure et les anciennes versions restent locaux. Les extraits utiles à la conversation sont transmis au fournisseur configuré.
- Le workflow GitHub est configuré pour Python, TypeScript et Playwright ; aucune exécution distante n’est revendiquée pour cette livraison locale.

## Preuves locales et commandes

Les reçus détaillés restent hors du pack : `runtime/validation_web_20260912_010834`, `runtime/validation_web_20260912_013016`, `runtime/tests_web_integrity_final.json`, `runtime/recette_web_api_20260912_011835` et `runtime/recette_web_wacc_20260911_230804_f9e2994a`. Les résultats de navigateur restent sous `frontend/test-results/`.

La preuve des deux scénarios de sensibilité est conservée sous `runtime/recette_web_sensi_worker_20260911_233002_75c29e16/validation.json`.

Pour répéter les tests : `python tools/verify_web_release.py --all`, puis `npm test` dans `frontend`. `python tools/validate_web_native.py` crée une nouvelle recette fictive utilisant Excel ; son coordinateur est volontairement simulé. Tester le vrai fournisseur depuis les réglages, puis une conversation dans un dossier de test, après avoir enregistré sa clé.
