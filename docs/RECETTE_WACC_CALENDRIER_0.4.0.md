# Recette WACC et calendrier — 13 septembre 2026

Cette recette utilise uniquement des copies identifiées et des conventions entièrement fictives. Les chiffres qui suivent ne constituent ni une valorisation client ni une validation de règles fiscales. Les modèles sources restent conservés par empreinte et toute migration crée un modèle distinct.

**La recette complète de livraison est réussie sur la trame historique 1.1.2**, avec ses 44 gardes fiscales conservées et les 71 corrections explicites. Son reçu est `runtime/recette_calendrier_fiscal_20260913_070638_631217/validation.json`. La première recette complète, `runtime/recette_calendrier_fiscal_20260913_035018_8c346e/validation.json`, reste un succès sur sa base 1.1.1 ; elle ne constitue pas la filiation du modèle finalement livré. Les tentatives et leurs verdicts d’origine restent conservés.

## Preuve native acquise

Reçu : `runtime/recette_qualifications_service_20260913_031354_e10b99/validation_service_wacc.json`.

Le solveur de production a exécuté 108 observations, avec son maillage complet et sa bissection. Il a convergé, sauvegardé, rouvert et adopté une nouvelle révision. Le WACC vaut **0,09000000008806794**, pour un oracle indépendant de **0,09** ; le résidu vaut **−8,806794182802946×10⁻¹¹**, dans la tolérance conservée de 10⁻¹⁰. Le DCF vaut **992 383,9972167194 €**, pour **992 383,998460928 €** attendus, dans la tolérance de 0,02 €.

Les huit oracles passent : CA de 120 000 € et COGS de 48 000 € pour chacune des trois années 2026–2028, WACC et DCF. L’empreinte de la copie adoptée est `588c5e0c56543fc3fcd7d0987be4c66ea15f335fb10cb027c6095b182e408271`. Le modèle privé employé porte l’empreinte `1f7bd630adeea4641afeb03beac5eda6abf8418a7bc71c0f90f286a09f393615`.

**Cette tentative reste en échec de recette globale** : le service masque correctement le DCF, car des erreurs actives de fiscalité et de trésorerie demeurent dans ses dépendances. Le reçu original n’est pas réécrit en succès. La convergence numérique ne remplace pas les qualifications des autres calculs.

## Défauts distincts reproduits et corrections explicites

1. Les cinq helpers d’empreinte WACC propageaient les erreurs des flux hors horizon. La migration technique sérialise leur type d’erreur et conserve les 263 propriétaires, sans transformer un montant financier en zéro.
2. Les dix valeurs actualisées DCF multipliaient des flux inactifs `#N/A` par zéro. La migration DCF sélectionne l’année avant d’évaluer le terme ; le terme d’une année active et ses erreurs restent conservés.
3. Cinquante-cinq agrégats annuels et l’alerte mensuelle de rupture de trésorerie sélectionnaient leurs périodes par multiplication. Une erreur dans une autre année contaminait ainsi une année active. La migration fiscale prépare **56 formules** : `ATELIER_CIR_IS!C34:M34`, `Modèle financier!C310:M310`, `C311:M311`, `C320:M320`, `C321:M321`, et `KPI Dashboard!E68`. Les dates sélectionnées, le critère de décembre pour les soldes et tous les ancrages `$` sont conservés. Aucun `IFERROR` global n’est ajouté ; une erreur dans une période sélectionnée demeure une erreur.

Chaque migration utilise le brouillon, l’aperçu, le jeton d’approbation et le scellement d’un nouveau modèle. Son certificat compare exhaustivement les formules avant/après ; modifier ailleurs un texte, un ancrage absolu ou une formule fait refuser le certificat. Il ne transfère aucune preuve native ni qualification fiscale au nouveau modèle.

## Recalcul des candidats

Les sondes privées ont mesuré environ 19 secondes par candidat avec `Application.Calculate`. Cette instruction actualise aussi les tables de données en mode automatique hors tables, comme décrit par [Microsoft](https://learn.microsoft.com/en-us/office/client-developer/excel/excel-recalculation). Une nouvelle saisie du candidat dans ce mode actualise les dépendances ordinaires sans relancer les tables.

La sonde `runtime/sonde_wacc_calcul_20260913_025917_7b498f/validation.json` a mesuré 187,5 puis 150,1 ms sur deux candidats, avec contrôle des flux, facteurs, valeurs présentes et état de calcul. Le worker livré conserve les reconstructions complètes initiale, finale et après réouverture. Il attend la fin du calcul après chaque saisie et conserve les contrôles de fraîcheur, les bornes et le résidu du solveur. Les nouveaux reçus de progression décrivent les phases et observations, sans recopier l’empreinte contenant les entrées brutes.

## Attribution des erreurs au calendrier

Les erreurs ne sont exclues de la période active que dans les rectangles documentés par leurs en-têtes : mensuel fiscal `N:EO` sur 132 mois, annuel fiscal et modèle financier `C:M`, compte de résultat `D:N` lignes 7–87, bilan `D:N` lignes 4–59, flux `D:N` lignes 5–47, financement `D:N` lignes 7–44, contrôles `C:M` lignes 12–24. Le tableau comparatif `Sensi TCA!C19:H23` porte un exercice par ligne. L’ancienne onzième année reste visible dans le diagnostic, mais est hors de l’horizon autorisé maximal de dix ans.

Un règlement fiscal tardif reste actif lorsque son **mois de paiement** appartient à l’horizon, même s’il concerne un exercice précédent. Les soldes d’ouverture, totaux, diagnostics et adresses inconnues restent actifs. Cette attribution n’efface aucune cellule et ne remplace pas la correction des 56 formules.

## Recette fiscale complémentaire

La première copie à 55 agrégats (`runtime/recette_calendrier_fiscal_20260913_033958_9d08e5`) a été interrompue après fermeture de son worker, avant scellement et adoption, lorsque le défaut de `KPI Dashboard!E68` a été identifié. Son fichier et son reçu d’interruption restent conservés.

La recette complète à 56 formules porte le statut **SUCCES**. Deux observations séparées ont d’abord confirmé, aux candidats 8 % et 10 %, le WACC calculé de 9 % et les DCF indépendants de 1 157 201,6460905347 € et 868 760,3305785122 €, en 166,2 et 177,8 ms. Le maillage complet a ensuite exécuté 108 observations, suivi des reconstructions complètes, de la sauvegarde et de la réouverture vérifiées.

Les huit oracles WACC/DCF et quinze oracles fiscaux et de trésorerie passent. Le service a adopté une nouvelle révision, conservé les sources et le modèle, puis affiché effectivement les valeurs de `Valorisation!D7` et `D40` sous leurs qualifications courantes. La relecture de l’ensemble des cellules ne trouve aucune erreur dans la période active. Les erreurs des périodes inactives restent dans les diagnostics.

Les oracles supplémentaires sont : impôts nuls selon la convention fictive, décaissements de 48 000 €/an et trésorerie de clôture de 172 000 €, 244 000 € et 316 000 € après l’apport initial de 100 000 €. Les **36 clôtures mensuelles** passent aussi une comparaison indépendante de 106 000 € à 316 000 €, par incréments de 6 000 € ; le point bas est 106 000 € et l’alerte indique « Non atteint dans le plan ». Ce complément est lié au même XLSM par empreinte dans `additional_monthly_diagnostics.json`.

La copie calculée de ce premier dossier fictif porte l’empreinte `a59e97bddd1bf7fd0276e7832dc66bae8170f358dba696b4ecb0679b8c076ccb`. Le modèle propre utilisé avant les 229 saisies fictives porte l’empreinte `1e67bf31a17f216bfe4a0a12d3ceb85c75880e41d0b8e274fe5c22795687e698`. Son contrôle `original_model_diff.json` prouve exactement les **71 formules** attendues par rapport à `models/generic-v1-release`, version **1.1.1**, d’empreinte `3ce93e17fdad0f9a41f1c1830fb1f8c64aff0291b04ef772362c81f7883d47b9`, les mêmes 33 feuilles et les sources VBA préservées. Aucune hypothèse métier n’a changé ; seul l’état natif `D141` a été vidé pour invalider les anciennes preuves.

Les 73 tests ciblés des migrations, qualifications, périmètres d’erreurs, comparaisons de formules, structures et protocole WACC passent. Ces tests hors Excel ne remplacent pas la recette native ci-dessus.

## Première préparation portable, exclue de la livraison

Après le succès de la recette, une copie distincte a été préparée pour les nouveaux dossiers. Seule la métadonnée locale `x15ac:absPath`, réintroduite par Excel, a été retirée de `xl/workbook.xml`. La comparaison exhaustive confirme les mêmes formules, valeurs et composants VBA que le modèle testé ; les JSON, profils et certificats ne contiennent aucun chemin personnel. Le modèle est à nouveau scellé sous une identité distincte et archivé au format v2, sans dépendance à la présence des anciens modèles.

Le reçu de préparation est `runtime/initial_web_model_0.4.0/validation.json`. Ce candidat porte l’identifiant `tca-bp-web/0bfb83e40adabd96ef90a221`, la référence d’archive `f66762ded8063f2fb22522b8eacdb007db38ada16d49ea772b0d67e6c3949116` et l’empreinte XLSM `b530cd8a722970ba4bc653448272cbf9f8165805d2d75682fd9053a1c83fbd8c`. Il contient les 71 corrections validées et aucune des 229 hypothèses saisies dans le dossier fictif. **Ce candidat b530 est exclu de la livraison**, car sa base 1.1.1 ne reprend pas les 44 gardes ajoutées dans la trame historique 1.1.2.

La sélection d’un modèle initial pour un **nouveau** dossier ne transfère ni sources, ni qualifications, ni preuve de calcul d’un dossier de recette. L’utilisateur doit encore décrire son entreprise, confirmer ou documenter ses hypothèses, puis recalculer sa propre copie. Les dossiers existants conservent leur ancien modèle jusqu’à une migration explicite.

## Reprise certifiée depuis la trame 1.1.2

La trame conservée `models/generic-v1/TCA_BP_Trame_generique.xlsm` porte l’empreinte `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12` et la version de construction **1.1.2**. Les deux trames historiques partagent la même source amont. Leur seule différence de contenu ZIP est `xl/worksheets/sheet21.xml` : 44 formules de `ATELIER_CIR_IS!C67:M68`, `C86:M86` et `C90:M90` ajoutent des gardes de calendrier. Leurs valeurs, caches, autres composants ZIP et binaires VBA sont identiques.

La nouvelle préparation repart explicitement de cette 1.1.2 et applique les migrations existantes de 5, 10 puis 56 formules, chacune sur une nouvelle copie avec son certificat et son profil. Le modèle propre obtenu porte l’empreinte `a3341b2c964fc7b3f3031647e6dbf081ff38f89cf6f8a0f3a59852ab0580f2f9`. Le profil conserve bien l’origine e4c1. Dans `runtime/recette_calendrier_fiscal_20260913_070638_631217/original_model_diff.json`, la comparaison exhaustive vérifie exactement **71 changements de formule**, les **44 gardes historiques strictement identiques**, les mêmes 33 feuilles et les mêmes hypothèses. Seul `Valorisation!D141` passe de `NON_EXECUTE` à vide pour invalider les anciennes preuves. Les sources VBA sont vérifiées et préservées ; les flux compilés et métadonnées binaires réécrits par Excel ne sont pas identiques.

Un premier essai natif a été interrompu par la veille du poste. Windows Power-Troubleshooter, événement 1, et Kernel-Power 42 attestent une veille du 13 septembre à `02:41:05.504232200Z`, puis un réveil à `05:03:48.011790300Z`, motif `System Idle`. Le reçu `runtime/sonde_wacc_calcul_20260913_044033_2d1bc7/validation.json` reste en échec ; son annexe `environment_interruption.json` relie ce verdict à l’interruption. La durée monotone de 8 652 secondes dépasse le délai de 300 secondes. Aucune régression financière n’est déduite de cet essai et aucun code de calcul n’a été modifié pour le rejouer.

La reprise a utilisé une copie du même modèle a3341 et exactement le même classeur avant calcul, dans un nouveau dossier fictif `runtime/recette_qualifications_service_20260913_070702_4c1053`. Les deux observations préalables passent en **169,3 et 154,4 ms**. La recette complète passe ses **23 oracles**, avec 108 observations du solveur, WACC `0,09000000008806794`, résidu `−8,806794182802946×10⁻¹¹` et DCF `992 383,9972167194 €`. L’adoption, la réouverture, la fraîcheur des preuves et l’affichage qualifié du WACC/DCF sont vérifiés par le service.

Le classeur calculé adopté porte l’empreinte `12e08a70b25f5d9dbaa933c56a0c58dc19220b1382b1173aea78ee822787ea9b`. Sur cette même copie, `additional_monthly_diagnostics.json` vérifie **44 résultats de gardes** — 12 en années actives et 32 hors horizon — ainsi que les **36 clôtures mensuelles** de 106 000 € à 316 000 €, par incréments de 6 000 €. Tous passent, et l’alerte de trésorerie indique « Non atteint dans le plan ».

## Archive portable retenue

Le reçu `runtime/initial_web_model_0.4.0_112/validation.json` confirme la nouvelle préparation portable. Seul `x15ac:absPath` a été retiré d’une copie du modèle a3341. Les formules, les valeurs et les sources VBA restent identiques au modèle éprouvé ; aucune des 229 saisies fictives n’est incorporée à la trame. Le modèle a été scellé puis archivé au format v2 sous une identité distincte :

- Identifiant : `tca-bp-web/eda1142bede89210fc7f9f5d`.
- Référence d’archive : `600b94dba37046704742b1cce802a9aeefbe3ab1cb897063bbe4bdaf73dfdacc`.
- Empreinte XLSM : `a34426619c1515a470e92db4fcf10f70bb1a173c0b35e04349ab69bdddae6cb9`.
- Empreinte du schéma : `2c9f8ad3317f66c8981865e9f6493d78970389ce8c7de6dd2fe483c169c128f3`.

La chaîne est donc **trame historique 1.1.2 e4c1 → 71 corrections certifiées, 44 gardes conservées → modèle éprouvé a3341 → suppression de la seule métadonnée locale → modèle portable a344**. L’archive est autonome et vérifiée par empreintes complètes. Les anciens modèles et reçus restent conservés. Le préparateur n’écrit pas la sélection : `runtime/initial_web_model_0.4.0_112/initial-web.json` fournit le pin exact pour une sélection explicite lors de la distribution.

La sélection explicite est désormais effectuée et vérifiée : `runtime/initial_web_model_0.4.0_112/selection.json` porte le statut `SELECTED`, pour la configuration `models/initial-web.json` d’empreinte `7653fde90460207807d5049fe238646e2a75a6b67d608abd64b113ad1dc46209`. L’ancienne configuration est conservée dans `previous-initial-web.json` du même répertoire de préparation. Aucun ancien dossier n’a été migré et aucune ancienne archive n’a été remplacée.
