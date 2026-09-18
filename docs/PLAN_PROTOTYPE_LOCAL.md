# TCA BP Web 0.4.0 — plan d'implémentation approuvé

Le 13 septembre 2026, l'utilisateur a autorisé la réalisation complète du prototype local. Le plan original d'agents et les audits sont conservés comme historiques.

## Contrat de livraison

Windows, Python 3.14, Excel natif, FastAPI, React et Glide Data Grid. Parcours : entreprise → documents → prévisionnel → scénarios → réalisé → livrables. Le tableur et le chat restent accessibles. Aucun hébergement ou compte commercial n'est requis.

Toutes les modifications financières : proposition, aperçu, approbation liée à cet aperçu, adoption d'une nouvelle révision et recalcul. Les sources et versions précédentes restent conservées. Les inconnues ne valent pas zéro ; les hypothèses ne deviennent pas confirmées du fait d'un calcul.

## Fonctions comprises

- Profil et questionnaire persistants dérivés du catalogue existant ; orchestration sélective des agents et lots explicitement multifeuilles.
- Documents PDF, Word, PowerPoint, CSV, Excel et images ; OCR Tesseract local français/anglais ; chaque fait extrait garde sa provenance et reste à confirmer.
- Calendrier civil, 1 à 10 ans ; catalogue d'offres extensible et registres qualifiés ; migrations explicites de modèle.
- Scénarios nommés, comparaisons financières, sensibilités à un ou deux axes et recherche d'objectif à un levier borné.
- Table de capitalisation, plusieurs levées en numéraire, pool pleinement dilué avant/après tour (avant par défaut).
- Réalisé mensuel importé Excel/CSV ou saisi ; budget figé, arrêté et prévision actualisée séparés ; raccord bilan/cash contrôlé.
- Instantané commun alimentant XLSM, PDF, DOCX et PPTX avec tableaux et graphiques éditables ; réimport des seules entrées reconnues d'un export.
- Compression des gros JSON pour nouvelles archives, lecture des versions précédentes, conservation des preuves.

## Ordre et contrôles

1. Corrections des audits : doubles demandes, intégrité forte, événements par dossier, aperçus échoués, propriété des processus Excel, pertes de composants, nombres ambigus. Retirer uniquement l'indexation Git des exemples privés.
2. Parcours et données ; nouveaux objets et migrations SQLite avec sauvegarde.
3. Scénarios et évolution de trame ; aucun changement silencieux de modèle ou de calcul métier.
4. Capitalisation, objectifs et réalisé ; tests financiers indépendants.
5. Livrables et stockage ; concordance exacte des chiffres entre formats.
6. Recette avec serveur réel, Excel natif et fournisseur IA configuré ; construction d'un nouveau ZIP et essai d'installation dans un chemin avec espaces. Node n'est nécessaire qu'au développement.

Le suivi d'exécution est dans `TASKS.md`. Un test simulé ne remplace ni un essai API réel ni une recette Excel. Aucune limite restant ouverte ne sera présentée comme une fonction validée.
