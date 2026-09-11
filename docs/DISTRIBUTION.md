# Pack local de l'application

`tools/package_app.py`, exécuté depuis le dépôt de développement, crée une archive ZIP **client** contenant l'application et le modèle générique déjà construit. Le destinataire n'a pas besoin des classeurs, présentations, pièces ou archives du dossier de référence. Le modèle présent dans le pack est chargé après vérification de ses empreintes ; aucune reconstruction n'est nécessaire tant qu'il reste intact.

Ce conditionnement n'est pas un exécutable portable : Python 3.14 avec Tcl/Tk reste nécessaire. L'installateur crée l'environnement Python et installe les dépendances, dont `pypdf` ; cette installation peut nécessiter Internet. Microsoft Excel est requis pour le recalcul natif. Le pack n'active pas les macros.

## Créer et vérifier dans le dépôt de développement

Avant une livraison, terminer la vérification native du modèle et examiner l'[état de livraison](ETAT_LIVRAISON.md). Le conditionnement contrôle l'intégrité des fichiers ; il ne remplace pas cette recette. Aucun pack financier certifié n'est déduit d'un simple succès du script.

Depuis le dépôt de développement :

```powershell
.venv\Scripts\python.exe tools\package_app.py --output dist\TCA_BP_local.zip
.venv\Scripts\python.exe tools\package_app.py --verify dist\TCA_BP_local.zip
```

Ces commandes sont réservées au dépôt TCA : `tools/package_app.py` n'est pas livré au client. La destination doit être nouvelle et séparée des sources, modèles, codes et dossiers clients. Le script refuse un fichier existant. Il ne construit pas le modèle, ne lance pas Excel et ne modifie aucun document de référence. Le fichier final n'est publié qu'après vérification du ZIP préparé.

## Contenu

- Modules nécessaires à la saisie, à l'interface, au CLI et au MCP, installateur, lanceur et configuration MCP locale.
- Documentation et 33 contrats d'agents.
- Catalogue sémantique complémentaire, ses définitions et témoins de dimension, avec le [guide de lecture](CATALOGUE_SEMANTIQUE.md).
- Trame `models/generic-v1/TCA_BP_Trame_generique.xlsm`, catalogue, classification, graphe, migrations, manifeste du modèle et reçu de construction.
- Licence et provenance du lecteur OLE ainsi que la provenance du moteur adapté.
- `LIRE_AVANT_UTILISATION.md` et `PACKAGE_MANIFEST.json`, avec taille et SHA256 de chaque fichier du pack.

Le `README.md` du pack provient du [guide client](README_CLIENT.md), avec ses liens adaptés à sa position racine. Le README du dépôt, qui contient les commandes de construction et de recette, n'est pas copié. Les chemins absolus du poste de construction sont remplacés par des chemins relatifs dans le reçu distribué. L'empreinte de la référence est conservée comme provenance, sans le fichier de référence. Les documents de maintenance et les preuves locales sous `runtime/` ou `models/versions/` ne sont pas copiés : leurs liens deviennent des mentions explicites de ressources internes non incluses dans le pack. Les guides du dépôt restent inchangés. Une autre cible documentaire manquante bloque le conditionnement.

L'inclusion repose sur une liste de fichiers autorisés, y compris pour les modules Python. Un nouveau module n'entre pas automatiquement dans le pack. `model_build.py`, `maintenance.py`, `model_maintenance.py`, les autres modules de construction, `tools/`, `tests/`, les exemples de maintenance, `exemple/`, `.git/`, `.venv/`, `runtime/`, les espaces clients et les secrets sont exclus. Les liens de fichiers ou répertoires ne peuvent pas importer des données extérieures.

Le moteur client importe `model_runtime.py` pour invalider les résultats périmés, sans importer le générateur. Le scellement de variantes reste dans `model_maintenance.py`, absent du pack. Les commandes `build` et `maintenance-*` retournent un refus JSON explicite dans le pack client. L'absence de la trame préconstruite demande de restaurer un pack complet ; elle ne déclenche pas une recherche de documents d'origine.

Le manifeste détecte un fichier manquant, altéré, supplémentaire ou un chemin interdit. Le contrôle vérifie aussi les liens documentaires et refuse les chemins personnels détectés dans les documents, manifestes et composants XML du classeur, sans afficher leur contenu. Il ne constitue pas une signature d'auteur : un attaquant capable de remplacer à la fois les fichiers et leur manifeste peut produire d'autres empreintes. Conserver ou transmettre séparément l'empreinte SHA256 du ZIP retournée par le script si une comparaison indépendante est nécessaire.

Après promotion de la trame validée et création du ZIP réel, exécuter de nouveau `--verify` sur le fichier final. Son résultat doit être `VERIFIE`. Comparer `template_sha256` à l'empreinte du modèle réellement promu, puis conserver `package_sha256` avec le reçu de livraison. Cette vérification n'ouvre pas Excel et ne s'appuie pas sur les documents de référence.

```powershell
$packCheck = & '.venv\Scripts\python.exe' 'tools\package_app.py' --verify 'dist\TCA_BP_local.zip' | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $packCheck.status -ne 'VERIFIE') { throw 'Le pack ne passe pas la vérification.' }
$promotedHash = (Get-FileHash -LiteralPath 'models\generic-v1\TCA_BP_Trame_generique.xlsm' -Algorithm SHA256).Hash.ToLowerInvariant()
if ($packCheck.template_sha256 -ne $promotedHash) { throw 'Le pack contient une autre version du modèle.' }
$packCheck
```

## Installer le pack

1. Extraire l'intégralité de l'archive dans un répertoire local.
2. Lire `LIRE_AVANT_UTILISATION.md`, puis exécuter `Installer_TCA_BP.ps1`.
3. Lancer `Lancer_TCA_BP.cmd`. Créer le dossier et ajouter ses propres sources.
4. Demander explicitement le recalcul Excel après les saisies. Les actions WACC et vérification des sensibilités utilisent leurs composants locaux dédiés, également inclus dans le pack, et produisent leurs propres reçus. Le statut des hypothèses reste distinct de ces calculs.

Les dossiers créés sont conservés dans l'espace local de l'utilisateur, hors du répertoire du modèle. La séparation exclut effectivement l'implémentation des opérations de développement ; le code de saisie Python reste lisible. Elle ne remplace pas les contrôles de droits du système Windows et ne chiffre pas les fichiers.

## Tests du conditionnement

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p test_package_app.py -v
```

Les tests utilisent uniquement une fixture fictive et des répertoires temporaires. Ils vérifient l'exclusion des sources et du développement, l'exhaustivité du manifeste, les refus d'écrasement et d'altération, les contrats/licences, les liens de preuves locales et la confidentialité. Un processus Python `-I -S` importe les vrais modules extraits du pack synthétique, initialise le service, expose les 33 agents, crée un dossier fictif et vérifie le refus des opérations de développement. La fixture ne démontre pas les formules financières d'un modèle réel. Aucun pack final ni calcul Excel n'est produit par ces tests.

La sonde d'extraction désactive aussi le chargement du site Python : les hooks d'une installation de développement externe ne peuvent pas retrouver un module absent du ZIP. Elle exerce le cœur autonome avec une source texte ; elle ne teste pas les imports PDF ni l'installation des dépendances. L'installateur du pack crée son propre environnement .venv.
