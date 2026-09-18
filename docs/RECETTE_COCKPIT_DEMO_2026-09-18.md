# Recette du cockpit de démonstration — 18 septembre 2026

Périmètre : copie de travail `frontend/src/cockpit`, accessible sous `/demo`. Les essais utilisent des profils Chromium neufs. Le stockage du navigateur de l’utilisateur et les documents clients ne sont pas lus. Le dossier original `visuel web test` est conservé ; le contrôle de son empreinte appartient à la recette d’intégration.

## État des lots F0 à F5

| Lot | Réalisé dans la démo | Limite explicite |
| --- | --- | --- |
| F0 | État partagé et commandes ; identifiants dossier/feuille/élément/brouillon/source/scénario/version ; migration v1 vers v2 ; ancien stockage conservé ; brouillons, préférences, logo et historiques persistants ; résultats invalidés après changement. | Les commandes démo restent indépendantes du service financier connecté. Un stockage JSON illisible n’est pas écrasé automatiquement. |
| F1 | Catalogue de 33 feuilles, huit groupes, URL stable, contenu par rôle, modes métier/grille/liens, destinations de dépendances et entrées d’origine ; résultats protégés. | Ce sont des exemples de consultation. La série mensuelle de trésorerie reprend celle du cas Atlas ; les autres séries absentes affichent « À compléter ». Ce catalogue ne remplace pas la grille Excel réelle. |
| F2 | Cas Atlas : offre/forfait, dates, TVA, probabilité/statut et sources ; même brouillon dans fiche et vues détaillées ; délai partagé avec Trésorerie ; annulation/abandon ; impacts ; comparaison, sauvegarde, adoption et versions. | Deux combinaisons préparées : 480 000 EUR, probable à 75 %, octobre 2026 sur quatre mois, TVA 20 %, puis 20 % / 60 jours ou 40 % / 30 jours. Les autres entrées n’obtiennent aucun résultat extrapolé. |
| F3 | Cinq autres décisions indépendantes : coût du composant 120/130 EUR ; recrutement octobre/janvier ; équipement octobre/janvier ; délai 60/30 jours ; multiple 4/5. Chaque thème possède source, brouillon, impacts, scénario nommé, version et restauration. | Les conséquences viennent de cas préparés. Elles ne constituent pas des états financiers consolidés, ni un moteur financier TypeScript. Aucun calcul fiscal ou WACC ajouté. |
| F4 | Métadonnées et faits fictifs confirmables/corrigeables/retirables ; protection des sorties d’installation ; réalisé mensuel avec correspondances, aperçu puis confirmation ; quatre aperçus documentaires ; compagnon contextuel. | Aucun contenu financier réel importé ou analysé. Seul août 2026 possède un réalisé d’exemple. Les quatre formats sont annoncés comme **aperçus web**, sans faux téléchargement Excel/PDF/Word/PowerPoint. |
| F5 | Atlas conservé visuellement ; graphiques comparables sur une même échelle ; contrôles TypeScript, état pur et navigateur ; palettes, largeurs, garde d’historique, clavier, zoom, mouvement réduit et branche sans flou. | La recette responsive couvre sept vues représentatives, pas chaque route dans chaque état. Ce n’est pas une certification d’accessibilité complète ni une validation financière Excel/API. |

## Résultats vérifiés

- `node --test tests/cockpit-state.test.mjs` depuis `frontend` : **15 tests réussis**. Migration, deux cas Atlas, cinq cycles thématiques, invalidation, restauration, réalisé, refus d’une source d’un autre dossier, confirmation répétée sans invalidation et refus d’un scénario fondé sur une ancienne version.
- `node tests/cockpit-demo-browser.mjs` : **44 contrôles réussis**, sans erreur JavaScript. Les 33 feuilles sont ouvertes par URL puis par leurs onglets ; les cinq cycles thématiques sont adoptés et relus après rechargement ; Atlas, réalisé et quatre aperçus sont exercés.
- `node tests/cockpit-demo-ui.mjs` : **48 contrôles réussis**, sans débordement ni erreur JavaScript. Migration v1 avec logo et quatre variantes ; trois palettes ; navigation d’installation par liens et historique ; conservation/abandon/enregistrement à destination ; sept vues à 1440, 1024, 768, 390 et 320 px, avec réalisé rempli ; saisie clavier puis Tab ; zoom CSS 200 % ; mouvement réduit ; application explicite des règles `@supports not` sans flou.
- `node tests/cockpit-demo-guards.mjs` : **3 contrôles réussis** après la dernière correction. Probabilité Atlas 76 % sans comparaison disponible, retour à 75 % permettant la simulation, description des six thèmes dans le compagnon.
- `tsc --noEmit -p tsconfig.json` : **réussi** après les dernières modifications.

Le premier test UI avait révélé un dépassement de 11 px du sélecteur de fichier à 320 px. Sa largeur est désormais bornée et les tableaux mensuels défilent dans leur propre conteneur. La recette a été rejouée avec les tableaux remplis.

## Reçus et captures

Les chemins suivants sont relatifs à la racine du projet et restent locaux dans `runtime` :

- `cockpit-demo-browser-2026-09-18T18-50-29-732Z/receipt.json` : 44 contrôles ; `livrables.png`.
- `cockpit-demo-ui-2026-09-18T18-56-46-471Z/receipt.json` : 48 contrôles, zéro modification de source pendant cette exécution.
- Dans ce même dossier : `palette-indigo.png`, `palette-lagoon.png`, `palette-copper.png`, `width-1440home.png`, `width-1024home.png`, `width-768home.png`, `width-390home.png`, `width-320home.png`, `width-320cashflow.png`, `zoom200.png`, `fallback-solid.png`.
- `cockpit-demo-guards-2026-09-18T18-59-13-057Z/receipt.json` et `unsupported-atlas.png` : garde ciblée finale.
- `cockpit_demo_sources_20260918.json` : empreintes SHA-256 finales des pages, du catalogue, de l’état, des composants modifiés et des scripts de recette de ce lot.

La branche CSS de repli est appliquée explicitement dans Chromium pour vérifier son rendu ; ce test n’affirme pas qu’un navigateur ancien sans prise en charge de `backdrop-filter` a été utilisé. La garde `beforeunload` est contrôlée par son annulation d’événement ; la boîte native de fermeture n’est pas automatisée.

## Contrats pour le raccord

Les routes ajoutées sont `/expert/feuilles/:sheetId`, `/travail/couts`, `/travail/equipe`, `/travail/investissements`, `/travail/tresorerie`, `/travail/synthese` et `/simulations/:scenarioId`. `lib/catalog.ts` exporte le catalogue et `demoRoutePatterns`. `DemoProvider.command` et `reduceSharedState` regroupent les mutations de démonstration. Les identifiants Excel sont exacts, dont `Sensi TCA` ; l’alias historique `Sensi Scénarios` est résolu explicitement.

Les documents, données, calculs, emplois Excel natifs, propositions liées à un jeton d’approbation et exports réels appartiennent au raccord au backend. Leurs résultats ne doivent jamais être remplacés par les exemples Atlas en cas d’indisponibilité.
