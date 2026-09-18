# TCA BP Web

Atelier web local pour décrire une entreprise, exploiter ses documents, construire son prévisionnel, comparer ses décisions, intégrer son réalisé et exporter ses livrables. La grille Excel et le chat restent accessibles dans le navigateur. Le backend Python 3.14 conserve les dossiers, sources, versions et contrôles du moteur existant. Microsoft Excel est nécessaire aux transformations et calculs natifs.

## Démarrer

1. Installer Python 3.14 et disposer de Microsoft Excel sur Windows.
2. Exécuter `Installer_TCA_BP_Web.ps1`. Le pack web inclut l’interface compilée ; depuis le dépôt, Node sert à la compiler.
3. Le pack distribué inclut la trame générique et une variante initiale corrigée, sélectionnée explicitement dans `models/initial-web.json`. Il s'utilise sans dossier d'exemple. Les anciens dossiers conservent leur modèle exact et leurs preuves ; leur ouverture ne provoque aucune migration.
4. Double-cliquer sur **Lancer_TCA_BP_Web.cmd** : l’atelier s’ouvre sur `http://127.0.0.1:8765`.
5. Créer ou ouvrir un dossier dans le **cockpit connecté**, puis suivre **Parcours**, ses six thèmes, **Simulations**, **Décisions**, **Suivi mensuel** et **Livrables**. Les modifications manuelles et celles du chat alimentent le même brouillon : proposition, aperçu, approbation, application, puis recalcul.
6. Pour connecter le chat, enregistrer la clé API dans Réglages. Le fournisseur et le modèle sont configurables ; les modèles disponibles sont interrogés auprès du fournisseur sans remplacer silencieusement une configuration enregistrée.

Les pièces et dossiers restent sous `%LOCALAPPDATA%/TCA_BP/<identifiant du projet>/`, comme dans le service existant. Les extraits nécessaires au chat sont envoyés au fournisseur choisi ; la clé reste protégée côté serveur par Windows DPAPI. La saisie manuelle fonctionne sans clé. Voir le [guide de l’atelier web](docs/ATELIER_WEB.md).

La [recette du cockpit 0.5.0](docs/RECETTE_COCKPIT_0.5.0.md) distingue les tests réussis, les calculs Excel natifs et la connexion au fournisseur restant à tester avec une clé. La [recette web 0.4.0](docs/RECETTE_WEB_0.4.0.md) conserve les preuves du socle. Le [suivi des deux audits](docs/SUIVI_AUDITS_0.4.0.md) donne un état, une preuve ou une justification de report à chaque constat.

L’[audit du code du 12 septembre 2026](docs/AUDIT_CODE_2026-09-12.md) recense les défauts corrigés, les points appelant une décision et les constats écartés avec leur raison.

Le cockpit ouvre les feuilles par identifiant stable, avec leurs entrées métier autorisées, sources et dépendances. Ses résultats et formules sont protégés. Une simulation capture le brouillon exact, travaille sur une copie et exige un nouvel aperçu approuvé avant adoption dans la référence. L’espace `/demo` contient uniquement des exemples fictifs, clairement signalés et conservés séparément dans le navigateur.

L’atelier de maintenance reste accessible à `/atelier`. Sa grille permet de proposer valeurs, formules, insertions et suppressions de lignes/colonnes, ainsi que l’ajout, le renommage, le déplacement et la suppression de feuilles. Un profil métier versionné fait suivre les identités, les sources et les opérations natives. Une suppression incompatible reste au brouillon avec son diagnostic. Restaurer crée une nouvelle révision, sans effacer les précédentes.

## Développement depuis GitHub

Le dépôt public contient le code, les tests et les ressources graphiques. Les classeurs et archives de modèle, documents clients, dossiers d’exécution et clés API restent locaux. Un clone seul ne contient donc pas le modèle Excel nécessaire au serveur métier. Reprendre le modèle du pack local autorisé et son fichier `models/initial-web.json`, sans substituer une autre trame ni changer son empreinte. Les versions anciennes d’un dossier restent liées à leur archive exacte.

Pour compiler l’interface : `cd frontend`, `npm ci`, puis `npm run build`. Pour travailler sur l’interface sans modèle Excel, `npm run dev` donne accès à `/demo`. Le [suivi d’intégration du cockpit](docs/INTEGRATION_COCKPIT.md) précise les parcours et le périmètre des vérifications.

## Socle métier conservé

La [recette du moteur historique](docs/RECETTE_VALIDATION.md), son [ancien périmètre](docs/ETAT_LIVRAISON.md) et le [guide de distribution historique](docs/DISTRIBUTION.md) restent disponibles. Pour cette version web, suivre le [guide de l’atelier](docs/ATELIER_WEB.md) et la [recette du cockpit](docs/RECETTE_COCKPIT_0.5.0.md).

- Dossiers clients séparés, versions immuables, empreintes et état persistant SQLite.
- Version exacte du modèle archivée avec chaque dossier ; rattachement d'un ancien dossier sur preuve, sans migration automatique.
- Import de réponses, textes, tableaux Excel/CSV, PDF, Word et PowerPoint ; OCR local Tesseract français/anglais pour les scans. Les extraits conservent leur document, empreinte et localisation ; les données incertaines restent à confirmer.
- 33 contrats d'agents : rôle de chaque feuille, dépendances, questions, sources et limites. Le coordinateur local route une demande française vers les modules concernés.
- Catalogue de 297 champs définis explicitement : unités, base de calcul, calendrier et propriétaires métier ; formulaires de registres, questions de complétude et distinction entre valeur manquante et zéro explicite.
- Propositions liées à la version du dossier, aux preuves du même client et à un identifiant de demande.
- Écriture ciblée sur une nouvelle copie XLSM. Les formules et structures passent par la préparation d’une variante web ; les plans périmés et sources étrangères sont refusés.
- Journal, reprise après redémarrage, détection du rejeu d'une demande et du doublon exact d'une ligne métier.
- Invalidation des résultats enregistrés après une saisie ; recalcul dans une instance Excel dédiée, macros désactivées ; contrôle des entrées après sauvegarde.
- Qualifications sourcées et datées : modules actifs/inactifs, hypothèses et données confirmées ; disponibilité distincte du CA, des coûts, du cash, de la fiscalité et du DCF.
- Résolution locale du WACC, sans macro ni itération circulaire globale, avec contrôle après sauvegarde et réouverture.
- Vérification des trois tables de sensibilité par 24 copies scalaires et 57 comparaisons ; conservation des entrées et preuve spécifique à la version calculée.
- Profil et questionnaire adaptés à l’activité, calendrier janvier–décembre sur 1 à 10 ans et sources distinguant hypothèses, données confirmées et informations manquantes.
- Scénarios nommés, objectifs à un levier et sensibilités à un ou deux axes avec reprise ; tours de financement en numéraire et pool salarié dans une table de capitalisation déterministe.
- Réalisé mensuel importé ou saisi, corrections historisées, budget initial conservé et raccord au futur calculé soumis à qualification. Une donnée absente reste manquante.
- Excel modifiable, PDF, Word et PowerPoint produits depuis un même instantané calculé ; tableaux et graphiques PowerPoint éditables. Réimport limité aux entrées reconnues, avec aperçu des différences.
- Aide locale de correspondance PCG issue des documents fournis et auditée ; les comptes historiques et inconnus restent signalés avant confirmation.
- Rapport Markdown historique présentant les données, sources, qualifications, questions et historique.
- Atelier React/TypeScript et FastAPI, CLI JSON et serveur MCP stdio. L’ancienne interface Tkinter reste disponible pour compatibilité.
- Maintenance de formules existantes sur une version expérimentale, avec analyse d'impact et tests natifs avant publication explicite ; les dossiers en cours conservent leur version.

Le chat web appelle réellement le coordinateur et les spécialistes utiles via l’API configurée. Le routage déterministe de l’ancienne interface reste disponible. Le serveur MCP partage le service de brouillons, d’aperçus, d’adoption et de restauration à travers les outils `bp_web_*`.

Les commandes spécialisées et leurs prérequis sont décrits dans les guides [Catalogue sémantique](docs/CATALOGUE_SEMANTIQUE.md), [Qualifications](docs/QUALIFICATIONS.md), [WACC](docs/model_wacc.md), [Sensibilités](docs/model_sensitivity.md) et [Versions](docs/MODELES_ET_VERSIONS.md). Une hypothèse sourcée peut servir à un scénario provisoire ; seul un dossier qualifié permet d'afficher ses résultats comme disponibles.

## Utilisation en ligne de commande

Depuis le répertoire du projet :

```powershell
py -3.14 -m tca_bp doctor
py -3.14 -m tca_bp build
py -3.14 -m tca_bp create --client "Client de démonstration" --name "Prévisionnel"
py -3.14 -m tca_bp list
py -3.14 -m tca_bp agents
```

Utiliser ensuite l'identifiant de dossier retourné :

```powershell
py -3.14 -m tca_bp source DOSSIER --text "Réponse explicite du porteur" --title "Entretien initial"
py -3.14 -m tca_bp ask DOSSIER "Je souhaite ajouter un recrutement"
py -3.14 -m tca_bp fields DOSSIER Effectifs
py -3.14 -m tca_bp inspect DOSSIER Control --cells C10,C59
py -3.14 -m tca_bp prepare DOSSIER lot.json --request-id demande_001
py -3.14 -m tca_bp apply DOSSIER PLAN_RETOURNE
py -3.14 -m tca_bp recalculate DOSSIER
py -3.14 -m tca_bp report DOSSIER
```

Exemple de lot, dont `SOURCE_RETOURNEE` doit être remplacé par une source du dossier :

```json
[
  {
    "sheet": "Stock",
    "cell": "E10",
    "value": 30,
    "reason": "Couverture de stock confirmée lors de l'entretien",
    "evidence": "SOURCE_RETOURNEE",
    "status": "CONFIRME"
  }
]
```

Les remplacements d'une valeur existante ou d'un défaut calculé nécessitent respectivement `replace_existing: true` et `override_default: true`. Ces autorisations sont propres au lot, pas à la feuille entière.

Le statut documentaire `INACTIF` ne peut pas être utilisé pour une écriture : il ne neutralise aucun calcul Excel. Pour désactiver un module, saisir son véritable champ d'activation avec une source et le statut `CONFIRME`. Un zéro explicite se qualifie comme toute valeur renseignée.

`--data-dir CHEMIN`, placé avant la commande, permet d'utiliser un espace de dossiers distinct, notamment pour les tests. Les identifiants, les preuves et le chemin de la dernière copie sont conservés dans l'état ; l'outil ne choisit pas « le fichier le plus récent ».

## Agents et assistants

Les contrats se trouvent sous `agents/` ; les fiches détaillées de modèle sont générées sous `docs/feuilles/`. [Le guide des agents](docs/AGENTS_ET_QUESTIONNAIRES.md) explique les responsabilités et les questionnaires.

La configuration MCP du projet est fournie dans `.vscode/mcp.json`. Elle lance `run_mcp.py` avec le Python de l'environnement local. Pour un autre client MCP, utiliser la même commande Python avec le chemin absolu de `run_mcp.py`.

Le serveur expose les dossiers, sources, fiches, inspections et propositions. Une pièce jointe ne peut jamais modifier ses droits. L'assistant doit lire le dossier, citer les sources, poser les questions manquantes puis préparer un lot concret. Les résultats financiers nécessitent une preuve de recalcul distincte.

Références techniques : [serveurs MCP dans VS Code](https://code.visualstudio.com/docs/agent-customization/mcp-servers), [transport MCP stdio](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports).

## Périmètre du modèle et vérification

La trame conserve les 33 feuilles et l'architecture de calcul existante. Les données du dossier de référence sont retirées ou migrées selon des règles explicites ; les clés et les libellés d'offres sont distingués. Les résultats enregistrés et les caches de graphiques sont invalidés. La capacité technique est de dix ans ; le début et l'horizon actif font partie du contrat de calendrier.

Certaines règles annuelles de fiscalité et conventions de calcul sont héritées du moteur. Leur applicabilité doit être qualifiée pour le dossier concerné. Une hypothèse non renseignée n'est pas une qualification favorable. Une copie vide ne permet pas de revendiquer une valorisation.

Le recalcul courant désactive les macros. La résolution WACC n'est donc pas exécutée par le bouton de recalcul. Les tables natives ont leur propre état. « Recalculé » signifie qu'Excel a terminé le calcul et sauvegardé la copie ; ce statut ne certifie pas les hypothèses économiques ou fiscales.

Le contrôle des doublons métiers détecte un rejeu identique et s'appuie aussi sur les identités des registres. Il ne constitue pas une déduplication sémantique universelle de descriptions différentes d'une même opération.

## Développement et tests

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m tca_bp.gui --smoke
.venv\Scripts\python.exe tools\validate_workflows.py
# Validation sur de nouvelles copies, avec Microsoft Excel :
.venv\Scripts\python.exe tools\validate_workflows.py --native
```

Les tests unitaires et adversariaux portent sur les limites de saisie, l'isolation, le rejeu, la reprise, les sources modifiées et le protocole MCP. La recette utilise trois dossiers fictifs distincts ; ses reçus sont conservés sous `runtime/`, hors de Git. Les attentes financières sont calculées indépendamment des formules pour le périmètre testé.

Le workflow GitHub teste le logiciel sous Windows et Python 3.14 avec ses fixtures fictives, puis exerce la fenêtre cachée. Les tests demandant la trame privée locale sont explicitement ignorés lorsqu'elle est absente ; la CI ne remplace aucune recette Excel et ne reçoit aucun dossier client. Les actions [checkout](https://github.com/actions/checkout) et [setup-python](https://github.com/actions/setup-python) sont liées à des commits précis.

Le dossier `exemple/`, les classeurs, les pièces, les résultats de recette et les espaces clients sont exclus des commits du logiciel. Le générateur et les règles sont versionnés ; les références de dossier doivent rester immuables.
