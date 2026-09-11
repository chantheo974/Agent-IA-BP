# Recette TCA BP 0.2.0 — 11 septembre 2026

Les campagnes utilisent exclusivement des dossiers fictifs. Les attentes sont déduites d'événements simples, puis comparées aux valeurs sauvegardées par Microsoft Excel 16.0. Les reçus identifient modèle, source, copie et périmètre. Une recette historique n'est pas présentée comme un nouveau calcul du modèle livré.

## Modèle courant

| Artefact | Version ou SHA256 |
|---|---|
| Application | 0.2.0 — Python 3.14.3 |
| Trame | `tca-bp-template/1`, build 1.1.2 |
| XLSM | `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12` |
| Schéma | `f0da6d7da5df3fda899adc23ec33b5d40f413821481dced7a11f46d78d8867eb` |

Les sept artefacts copiés vers `models/generic-v1` sont identiques au candidat 1.1.2. Les versions antérieures sont conservées. Les 33 fiches et les 33 contrats ont été régénérés ; aucun dossier en cours n'a été migré.

## Contrôles natifs du modèle courant

| Campagne | État du reçu | Périmètre |
|---|---|---|
| Branches fiscales | **12/12 attentes réussies** | Oui/Non/inconnu dans les années actives ; neutralité hors horizon. Source conservée, entrées identiques après sauvegarde/réouverture. |
| Sensibilités | **57/57 comparaisons et 14/14 attentes réussies** | 24 copies scalaires, trois tables, écart maximal nul. Entrées, formules, protections et instruments préservés ; quatre critères d'effet réel des axes réussis. |
| WACC via service qualifié | **Préparé** | 229 valeurs sourcées, 12 déclarations, 8 attentes dont WACC 9 % et DCF de 992 383,998460928 €. Adoption et affichage qualifié à vérifier. |
| Opérations commerciales | **Préparé** | Trois dossiers, 197 attentes et six refus : capacité/FIFO/prix signé, acomptes/PCA/FAE, stocks/fournisseurs/TVA/BFR. |

Les gardes fiscales corrigent un défaut réellement observé : des `#N/A` d'années hors horizon contaminaient une consolidation de cash active via `SUMPRODUCT`. La correction neutralise les seules années inactives et conserve l'indisponibilité d'une année active non qualifiée.

La base de sensibilité donne un cash minimal de −48 000 € et un cash final de 305 400 €. Le reçu final est `TABLES_VERIFIEES`, après 2 316,58 secondes. Cette recette exerce le calcul natif directement : elle ne constitue pas une adoption par un dossier métier qualifié. Ses 44 erreurs `#N/A` sont limitées au DCF non qualifié ; aucune n'appartient aux autres périmètres. Le protocole d'adoption du service est testé séparément.

## Recettes natives antérieures conservées

| Version exacte | Résultat | Attentes indépendantes |
|---|---|---|
| `17623a7947cd…` | **123/123 attentes, huit refus** | Sept cas d'actifs et aides : crédit-bail, services en fin de bail, taux positif, échéance d'un mois, aide accordée/base, tranches différées et aide d'exploitation. |
| `6c3e37153aa7…` | **WACC réussi** | Taux 0,09000000008806794 ; DCF 992 383,9972167194 €, contre 992 383,998460928 € attendu. 108 évaluations, résidu inférieur à 10⁻¹⁰, sauvegarde/réouverture et entrées préservées. |
| `6c3e37153aa7…` | **191/197 puis six adresses d'oracles corrigées** | Quatre attentes FIFO visaient une ligne inexistante ; deux stocks visaient la mauvaise ligne du bilan. Les bonnes adresses satisfont les six attentes. Le reçu initial reste en échec ; une campagne neuve est préparée sur 1.1.2. |
| `ff5ad2f940c5…` | **15 oracles sur trois dossiers** | Services : CA/coûts/recrutement daté ; fabrication : CA/coûts/CAPEX cash/amortissement ; recherche : dette/intérêts/apport. |
| Variante calendrier antérieure | **Oracle 2032 réussi** | Trois exercices à partir du 1er janvier 2030. Changement de formule, scellement et calcul natif ; aucune approbation nominative ou migration fabriquée. |

Exemples indépendants : un bail de 12 000 € sur douze mois au taux annuel de 12 % donne une mensualité de 1 066,185464 € ; un actif cash de 12 000 € amorti sur trois ans donne 4 000 € annuels. Les aides sont testées avec leurs montants accordés et tranches, sans seconde application d'un taux.

## Tests logiciels

La suite complète sur la trame finale a exécuté **381 tests : 381 réussites, aucun test ignoré**, en 540,98 secondes. Les sept artefacts du modèle et le code applicatif sont restés inchangés pendant cette exécution. Seul le test de qualification du modèle a reçu entre-temps un saut explicite lorsque la trame est absente d'un checkout ; ce test a ensuite été réexécuté avec succès sur son fichier actuel.

La campagne précédente reste conservée avec ses 348 réussites et son erreur de fixture sans feuille BFR. La correction renvoie une valeur indisponible, et ses 106 tests ciblés avaient réussi avant la suite complète finale. Aucun ancien rapport en échec n'a été réécrit.

Ces tests couvrent qualifications, versions exactes, signatures, transactions, preuves natives, sources étrangères, invalidation, reprise et interfaces. Le recalcul est simulé lorsque l'objet du test est le protocole ; seuls les reçus natifs attestent Excel. Les suites complémentaires restent distinguées de la suite complète, sans addition trompeuse des tests communs.

Les trois parcours fictifs sur le vrai service et la trame finale réussissent **74/74 contrôles**, sans Excel. Ils couvrent les créations, zéros explicites, activations progressives, calendriers, reprises, doublons, mauvais modèle, source étrangère et plan périmé. La relecture finale des 11 lots et 201 écritures avec le contrat sémantique courant réussit sans mutation des dossiers.

Les corrections finales du diagnostic de maintenance ont passé 20 tests ciblés. Les deux tests du protocole de recette WACC et de qualification du modèle ont aussi réussi. Le diagnostic d'installation a été vérifié après retrait des noms exacts des fichiers de référence.

La copie autonome finale du code, sans trame ni sources, a exécuté 360 tests : **338 réussites et 22 sauts explicites liés à l'absence de modèle**, puis neuf étapes de la fenêtre cachée. Aucun fichier source n'a changé pendant ce contrôle. Python et ses dépendances proviennent du poste ; ce contrôle ne prouve ni une nouvelle installation ni une exécution distante GitHub. Le serveur MCP est exercé par son entrée stdio.

## Conservation et confidentialité

Les dix documents initiaux conservent leurs tailles et SHA256. Leur audit détaillé reste interne. La comparaison exhaustive avec la trame documentaire précédente retrouve uniquement trois libellés et 45 gardes/diagnostics modifiés ; entrées, nombres, autres formules et styles effectifs restent conformes.

Le scanner de résidus privés contrôle 62 composants XML, leurs attributs et objets. Les macros sont inspectées et scellées, sans être exécutées. Les anciens identifiants de protection ne sont pas réemployés. Le pack possède une liste exacte de fichiers et d'empreintes ; références client, générateur et maintenance n'y sont pas distribués.

## Reçus internes et reproduction

Ces preuves locales sont exclues de Git et du pack :

- `runtime/verification_sources_release.json` : conservation des dix sources ;
- `runtime/verification_revision_release_1_1_2.json` : différences et confidentialité ;
- `runtime/promotion_release_1_1_2.json` : sept copies identiques et guides ;
- `runtime/recette_financiere_20260911_215558_e1b6d173/validation.json` : douze branches fiscales ;
- `runtime/recette_sensitivity_20260911_215958_4b26e5cb/` : tables ;
- `runtime/recette_qualifications_service_20260911_215456_eec175/` : WACC qualifié ;
- `runtime/recette_financiere_20260911_220351_6af76492/` : opérations ;
- `runtime/recette_financiere_20260911_204344_49b83e5a/validation.json` : actifs/aides antérieurs ;
- `runtime/tests_final_0_2_0_20260911_222545.json` : suite complète sur la trame finale ;
- `runtime/recette_cycle_20260911_221745_c828b4/cycle_recette.json` : 74 contrôles de parcours ;
- `runtime/recette_cycle_20260911_221745_c828b4/relecture_semantique_finale.json` : 11 lots et 201 écritures ;
- `runtime/code_checkout_20260911_224602_19f04099/validation.json` : code final isolé sans modèle ;
- `runtime/tests_release_0_2_0.json` et `runtime/tests_release_0_2_0_corrections.json` : suite et corrections.

Depuis le dépôt équipé de sa trame locale :

```powershell
py -3.14 -m unittest discover -s tests -v
py -3.14 -m tca_bp.gui --smoke
py -3.14 tools/validate_financial_cases.py --model-dir models/generic-v1 --group qualification
py -3.14 tools/validate_financial_cases.py --model-dir models/generic-v1 --group operations
py -3.14 tools/validate_financial_cases.py --model-dir models/generic-v1 --group assets
```

Exécuter les campagnes Excel successivement. Elles créent des dossiers fictifs et ne recalculent aucun original. La qualification juridique, fiscale et économique de chaque nouveau dossier reste distincte de ces preuves logicielles et arithmétiques.
