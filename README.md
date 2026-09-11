# TCA BP

Application locale Windows en Python 3.14 pour préparer des business plans à partir de pièces et de réponses métier. Les données sont écrites dans des **copies versionnées d'un modèle Excel**, avec sources, qualifications et journal. Microsoft Excel est nécessaire pour les calculs natifs.

## Démarrer

1. Installer Python 3.14 avec Tcl/Tk. Sur le poste de développement, Python 3.14.3 et Excel sont disponibles.
2. Exécuter `Installer_TCA_BP.ps1`, ou `py -3.14 -m venv .venv` puis `.venv\Scripts\python.exe -m pip install -e .`.
3. Le pack local distribué inclut la trame générique sous `models/generic-v1/` et s'utilise sans dossier d'exemple. Pour construire la trame depuis le seul dépôt de code, placer l'unique archive de référence autorisée sous `exemple/03_Agent_de_saisie/` et son classeur `*Pilotage_protege.xlsm` sous `exemple/01_Previsionnels/`. Le générateur vérifie leurs empreintes et leur correspondance. Le dépôt ne distribue pas ce dossier de référence.
4. Double-cliquer sur **Lancer_TCA_BP.cmd**.
5. Créer un dossier, ajouter une pièce ou une réponse, sélectionner une feuille puis préparer les saisies. L'aperçu du lot précède le bouton d'application. Le recalcul Excel est une action séparée.

Les pièces et les dossiers sont conservés par défaut sous `%LOCALAPPDATA%/TCA_BP/<identifiant du projet>/`. Le chemin exact figure dans l'application et dans `etat_dossier.json`. Aucune clé API n'est nécessaire à la saisie guidée.

## Fonctions disponibles

Les résultats des essais sont consignés dans la [recette de livraison](docs/RECETTE_VALIDATION.md). Le [périmètre livré](docs/ETAT_LIVRAISON.md) distingue les fonctions utilisables des validations financières restant à compléter. Pour transférer l'application avec sa trame, suivre le [guide du pack local](docs/DISTRIBUTION.md).

- Dossiers clients séparés, versions immuables, empreintes et état persistant SQLite.
- Version exacte du modèle archivée avec chaque dossier ; rattachement d'un ancien dossier sur preuve, sans migration automatique.
- Import de réponses, textes, PDF, Word et PowerPoint ; conservation locale des autres pièces prises en charge. Aucun OCR n'est effectué sur les documents scannés.
- 33 contrats d'agents : rôle de chaque feuille, dépendances, questions, sources et limites. Le coordinateur local route une demande française vers les modules concernés.
- Catalogue de 297 champs définis explicitement : unités, base de calcul, calendrier et propriétaires métier ; formulaires de registres, questions de complétude et distinction entre valeur manquante et zéro explicite.
- Propositions liées à la version du dossier, aux preuves du même client et à un identifiant de demande.
- Écriture ciblée sur une nouvelle copie XLSM. Refus des formules libres en saisie, des cellules protégées, des plans périmés et des sources étrangères au dossier.
- Journal, reprise après redémarrage, détection du rejeu d'une demande et du doublon exact d'une ligne métier.
- Invalidation des résultats enregistrés après une saisie ; recalcul dans une instance Excel dédiée, macros désactivées ; contrôle des entrées après sauvegarde.
- Qualifications sourcées et datées : modules actifs/inactifs, hypothèses et données confirmées ; disponibilité distincte du CA, des coûts, du cash, de la fiscalité et du DCF.
- Résolution locale du WACC, sans macro ni itération circulaire globale, avec contrôle après sauvegarde et réouverture.
- Vérification des trois tables de sensibilité par 24 copies scalaires et 57 comparaisons ; conservation des entrées et preuve spécifique à la version calculée.
- Rapport Markdown présentant les données, sources, qualifications, questions et historique.
- Interface Tkinter, CLI JSON et serveur MCP stdio pour utiliser les outils depuis un assistant compatible.
- Maintenance de formules existantes sur une version expérimentale, avec analyse d'impact et tests natifs avant publication explicite ; les dossiers en cours conservent leur version.

Le dialogue local est **guidé par les contrats et les règles métier**. Il ne remplace pas un modèle de langage généraliste. Le serveur MCP permet à un assistant externe de raisonner sur les sources et de proposer des saisies tout en utilisant le même moteur contrôlé. Le logiciel n'envoie lui-même aucune pièce à un service cloud.

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
