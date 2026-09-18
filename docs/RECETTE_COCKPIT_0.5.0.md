# Recette du cockpit local 0.5.0

Cette recette accompagne l'intégration du dossier visuel dans l'application Python/React existante. Les exemples restent isolés sous `runtime`. Aucun dossier client, aucune clé et aucun classeur financier ne sont publiés sur GitHub.

## Périmètre

- `/` : cockpit relié au dossier local, à son modèle versionné, à ses sources et à ses travaux.
- `/demo` : démonstration explicitement fictive, stockage navigateur séparé et résultats préparés. Elle n'est pas un moteur financier.
- `/atelier` : atelier historique conservé pour l'édition détaillée et la maintenance explicite du modèle.

Les parcours ordinaires proposent seulement les entrées métier reconnues. Les formules, résultats calculés et opérations structurelles ne deviennent pas modifiables par la simple présence d'un champ ou d'un message. Le serveur conserve cette limite indépendamment du navigateur.

## Vérifications du socle

La campagne Python complète du 18 septembre a exécuté **702 tests avec succès**. Quatre fichiers ont changé pendant cette campagne pour corriger une concurrence de lecture : ce résultat n'est donc pas présenté comme un contrôle de l'arbre final figé. Les modules concernés et leurs dépendances web, chat, séries, ressources et distribution ont ensuite été rejoués : **72 tests réussis en 65,238 secondes**, empreintes avant/après identiques.

Reçus locaux :

- `runtime/validation_web_20260918_205007_6d74e1/validation.json` : suite complète, code de sortie des tests nul et dérive identifiée.
- `runtime/validation_cockpit_delta_20260918_210616/validation.json` : contrôle complémentaire sur sources figées.

Les vérifications spécifiques couvrent notamment les réponses perdues, le dossier et la révision d'origine d'une intention, les conflits manuel/chat, la source d'un autre dossier, les formules refusées dans le parcours ordinaire, les lectures concurrentes et le changement de modèle pendant une lecture. Une simple lecture du catalogue ne prend plus un verrou transactionnel de fichier qui pouvait faire échouer la première saisie.

Après l'ajout des projections de résultats par feuille et de sept trajets métier supplémentaires, le dernier contrôle ciblé comporte **86 tests réussis en 69,223 secondes**, sur sources figées. Reçu : `runtime/validation_cockpit_delta_20260918_212338/validation.json`, empreinte de sources `bfc477d215bf67f4cdb729379101cc1bf12904e855480312782d5347a679ebd0`. Les campagnes ci-dessus se recouvrent ; leurs nombres ne s'additionnent pas.

## Interface

La suite navigateur de référence comprend **57 tests réussis** : 44 parcours historiques et 13 contrôles du cockpit et de ses protections. Preuve : `runtime/recette_cockpit_front_20260918_2110/playwright57.json`.

La campagne des sorties structurées ajoute huit contrôles : **65 tests réussis**, aucun test ignoré, instable ou en échec (63,985 secondes). Elle comprend les 57 parcours précédents et vérifie notamment la qualification, l'absence de valeur, les trois flux commerciaux et le refus d'afficher des chiffres liés au mauvais dossier, profil, fichier ou numéro de révision.

Le vrai serveur local a aussi été exercé avec un dossier fictif distinct : création d'une source, saisie du calendrier, même proposition retrouvée dans la fiche et la grille après actualisation, formule en lecture seule et dialogue centré. Le classeur et sa révision restent inchangés ; aucun calcul Excel ou appel IA n'est lancé par cette recette. Preuve : `runtime/live_cockpit_ui_20260918_211340/validation.json`, sources et interface compilée inchangées pendant l'essai.

La lecture des résultats C1 a ensuite été contrôlée dans le navigateur avec une **vraie copie recalculée par Excel** : `runtime/live_cockpit_outputs_20260918_212402/validation.json`. L'écran affiche les revenus de 8 000 EUR sur novembre/décembre/janvier, les factures et encaissements distincts, la trésorerie de 100 000/112 000/124 000 EUR et les annuels de 16 000 EUR en 2026 puis 8 000 EUR en 2027. Périodes, unités et cellules sources ont été rapprochées ; zéro requête d'écriture, révision et empreinte conservées, serveur arrêté. Les autres feuilles sans projection structurée affichent cette limite et leur grille réelle reste disponible.

Les contrôles détaillés de la démonstration, des 33 destinations, des six thèmes, des palettes, du clavier, du zoom et des petites largeurs sont décrits dans `RECETTE_COCKPIT_DEMO_2026-09-18.md`. Ils prouvent le comportement de la démonstration, séparément des opérations financières.

## Lecture et calcul financier

Les observations mensuelles sont lues dans le classeur calculé : revenu reconnu, facturation clients et encaissements clients sont trois séries distinctes. Les observations portent leurs cellules sources, périodes, unités et révision ; une valeur manquante ou non qualifiée reste indisponible. Aucun montant n'est calculé dans React pour remplacer une observation Excel.

La recette native utilise un contrat fictif reconnu sur trois mois, une facturation en deux fois et un délai de paiement. Le brouillon double le prix, simule une copie isolée, vérifie des résultats indépendants, conserve cette copie et propose son adoption dans le parent. L'adoption passe de nouveau par l'aperçu et son jeton. Le contrôle du délai fournisseur a fait apparaître une contradiction dans le jeu fictif initial : le stock était déclaré inactif mais son délai fournisseur n'était pas nul. Le jeu a été corrigé par une source explicite ; les diagnostics des tentatives précédentes sont conservés. Aucun contrôle métier n'a été affaibli pour faire passer l'essai.

Outils reproductibles : `tools/validate_cockpit_native.py` puis `tools/validate_cockpit_delivery.py`, à exécuter uniquement sur un dossier fictif nouvellement préparé. Les reçus se trouvent dans ce dossier et détaillent le périmètre effectivement validé.

Résultat du 18 septembre : **12 contrôles et 17 oracles natifs réussis**, puis **37 contrôles de livraison et restauration réussis**. Les 17 observations se retrouvent dans l'instantané des livrables ; les quatre téléchargements correspondent aux empreintes attendues. Tous les composants de l'Excel source sont conservés hormis l'ajout de l'identité d'export et ses déclarations. Word conserve des tableaux éditables ; PowerPoint contient un graphique natif et son classeur embarqué. Le réimport inchangé ne crée aucune modification. La restauration laisse accessibles l'ancienne version adoptée et la copie de simulation ; une réponse perdue ne crée pas une seconde révision.

Reçus : `runtime/recette_qualifications_service_20260918_204234_20b5d2/validation_cockpit_native.json` et `validation_cockpit_delivery.json`. Le contrôle de restauration ne prétend pas être un nouveau recalcul de la version restaurée. Les qualifications et le recalcul requis restent visibles dans son état.

Les recettes de réalisé, de fiscalité, de financement, de WACC, de sensibilités et d'exports de la version 0.4.0 restent des preuves ciblées du moteur conservé. Elles ne sont pas présentées comme une nouvelle exécution de tous ces calculs à travers chaque écran du cockpit.

## Distribution et limites de validation

Les premières exécutions GitHub ont révélé deux défauts supplémentaires, corrigés avant la livraison finale : une comparaison de chemins Windows non canoniques dans le conditionnement, et une réponse de profil tardive qui reprenait le focus de la grille avant un collage. La racine de conditionnement est maintenant résolue avant comparaison, sans modifier le contrôle des liens et des sorties du répertoire autorisé. Les 29 tests de conditionnement passent, dont deux régressions couvrant chemins équivalents et junctions Windows.

La perte de focus a été reproduite trois fois avant correction. La mise à jour du titre est désormais indépendante du changement de page ; les quatre contrôles de protection de saisie passent chacun trois fois après correction, soit 12 cas sans échec. Les preuves sont conservées dans `runtime/ci_clipboard_focus_20260918`. Cette correction ne modifie ni l'API ni le moteur financier. Le pack est recompilé et son installation revérifiée pour inclure ce changement.

La suite navigateur complète après correction comporte **66 tests réussis en 62,892 secondes**, aucun test ignoré, instable ou en échec. Reçu : `runtime/recette_cockpit_front_20260918_214604_focus/validation.json`, avec les empreintes de 210 fichiers frontend et de 103 fichiers compilés. Cette campagne remplace la précédente comme contrôle du frontend livré.

Le pack 0.5.0 est distinct du pack 0.4.0 conservé. Son reçu extérieur doit identifier les octets du ZIP, le manifeste, les scripts PowerShell extraits, le modèle initial et le démarrage dans un nouveau répertoire avec espaces. `tools/validate_web_installation.py` vérifie cette installation et les six espaces du cockpit dans un navigateur réel. Node sert à construire et à tester l'interface, pas à l'utiliser.

La connexion à un fournisseur IA réel reste à exercer avec une clé enregistrée dans les réglages locaux. Les tests du coordinateur, de ses outils et de ses refus avec un fournisseur simulé ne prouvent pas cette connexion. Les sorties indisponibles du modèle et les hypothèses non qualifiées restent signalées dans l'interface et dans les rapports.

Le contrôle C4 en lecture seule est conservé dans `runtime/audit_c4_connected_20260918.json` : huit livrables historiques supplémentaires ont été rapprochés de leurs empreintes. Une nouvelle tentative d'ajout documentaire après perte de réponse peut encore créer deux entrées documentaires ; elle n'applique pas deux écritures financières. Ce point et les recettes natives des cinq autres thèmes via le cockpit restent dans le suivi, sans masquer les vérifications réellement exécutées.
