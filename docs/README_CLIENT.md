# TCA BP — application client

Application locale Windows pour préparer un business plan dans des copies Excel versionnées, à partir de vos pièces et réponses. Le pack contient sa trame générique et ses manifestes ; aucun document du dossier de référence n'est nécessaire.

## Démarrer

1. Extraire tout le ZIP dans un répertoire local.
2. Installer Python 3.14 avec Tcl/Tk, puis exécuter `Installer_TCA_BP.ps1`. L'installation des dépendances peut nécessiter Internet.
3. Double-cliquer sur `Lancer_TCA_BP.cmd`.
4. Créer un dossier, ajouter vos sources, choisir une feuille et préparer les saisies.
5. Examiner l'aperçu avant d'appliquer le lot. Demander séparément le recalcul avec Microsoft Excel.

Les dossiers sont conservés dans l'espace local de l'utilisateur, distinct de la trame. Le chemin exact figure dans l'application. Les macros restent désactivées lors du recalcul courant. Un calcul terminé ne confirme pas les hypothèses économiques ou fiscales ; les sensibilités et le WACC ont leur propre périmètre de validation.

## Commandes utiles

Depuis le répertoire extrait, après installation :

```powershell
.venv\Scripts\python.exe -m tca_bp doctor
.venv\Scripts\python.exe -m tca_bp gui
.venv\Scripts\python.exe -m tca_bp create --client "Client de démonstration" --name "Prévisionnel"
.venv\Scripts\python.exe -m tca_bp list
.venv\Scripts\python.exe -m tca_bp agents
```

La commande `--help` décrit les opérations. Les commandes `build` et `maintenance-*` sont réservées au dépôt de développement TCA et sont refusées dans ce pack. Si la trame ou ses manifestes manquent, restaurer une archive client complète et vérifiée ; ne pas remplacer des formules dans le dossier courant.

## Sources et assistants

Le dialogue intégré repose sur des contrats et questionnaires. Il ne transforme pas automatiquement une pièce en valeurs validées. Chaque proposition reste liée aux sources, au dossier et à sa révision. Les valeurs absentes et les zéros explicitement confirmés sont distincts.

Un assistant compatible MCP peut utiliser le serveur local `run_mcp.py`, configuré dans `.vscode/mcp.json`. Le logiciel n'envoie lui-même aucune pièce vers un service cloud. Le raisonnement d'un assistant ne tient pas lieu de validation d'une source ou de preuve de calcul.

## Guides

- [Utiliser l'interface](INTERFACE.md)
- [Agents et questionnaires](AGENTS_ET_QUESTIONNAIRES.md)
- [Résoudre le WACC et lire sa preuve](model_wacc.md)
- [Vérifier les tables de sensibilité](model_sensitivity.md)
- [Périmètre et limites de livraison](ETAT_LIVRAISON.md)
- [Installation et distribution](DISTRIBUTION.md)

Le pack exclut le générateur de modèle, la maintenance de formules, les scripts et les tests du dépôt. Il conserve les licences et la provenance des composants nécessaires à la saisie. `PACKAGE_MANIFEST.json` décrit les empreintes des fichiers ; conserver séparément l'empreinte du ZIP communiquée par TCA.
