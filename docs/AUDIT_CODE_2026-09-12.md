# Audit du code TCA BP — 12 septembre 2026

Audit du dépôt complet : moteur Python 3.14, atelier web FastAPI, interface React/TypeScript, pilotage Excel par PowerShell, serveur MCP, interface Tkinter, outils de construction et de distribution, tests et intégration continue.

Le périmètre couvre le code livré et le code non encore commité (`tca_bp/web_*.py`, `frontend/`, `tests/test_web_*.py`), ainsi que les modifications en cours sur le calcul natif et le service.

## Méthode

Treize puis six lecteurs spécialisés ont parcouru le dépôt par dimension : sécurité du serveur local, concurrence et transactions, cycle de vie des brouillons, transformations structurelles, coordination avec le fournisseur IA, frontend, service applicatif, calcul natif Excel, moteur de modèle, agents et connaissance, tests, empaquetage, hygiène du dépôt et qualité du code. Chaque constat exigeait un scénario d'échec concret appuyé sur le code lu.

Les constats ont ensuite été revérifiés, et plusieurs mesures ont été prises directement sur le poste : durée de hachage des archives de modèle, taille réelle des répertoires de données, analyse syntaxique des scripts PowerShell par l'analyseur Windows, comportement réel du flux d'événements lors d'une déconnexion du navigateur.

Soixante-deux constats sont issus des lecteurs. Sept constats supplémentaires proviennent de vérifications directes, dont le plus grave n'avait été relevé par aucun lecteur.

## État de référence avant modification

| Mesure | Valeur |
|---|---|
| Tests Python | 479 réussis |
| Tests navigateur Playwright | 8 réussis |
| Compilation TypeScript et Vite | réussie |

## Défauts corrigés

### Les deux installateurs Windows ne pouvaient pas s'exécuter

`Installer_TCA_BP.ps1` et `Installer_TCA_BP_Web.ps1` contenaient une apostrophe typographique U+2019 à l'intérieur de chaînes entre apostrophes simples. Windows PowerShell 5.1 traite ce caractère comme un délimiteur de chaîne : l'analyse du script échoue avant toute exécution.

```
throw 'Création de l’environnement Python interrompue.'
       ~~~~~~~~~~~~~
Jeton inattendu « environnement » dans l'expression ou l'instruction.
```

L'installateur du pack client était donc inutilisable en l'état. Les apostrophes typographiques ont été remplacées par la forme échappée officielle de PowerShell. Les six scripts du dépôt s'analysent désormais sans erreur.

Ce défaut n'a été trouvé par aucun lecteur : il est apparu en soumettant réellement les scripts à l'analyseur PowerShell.

### Les scripts PowerShell accentués étaient lus en page de code ANSI

`tca_bp/sensitivity_worker.ps1`, `tca_bp/web_structure_worker.ps1` et `Installer_TCA_BP_Web.ps1` contenaient des messages accentués sans marque d'ordre d'octets UTF-8. Windows PowerShell 5.1 lit alors le fichier en cp1252 et les diagnostics deviennent illisibles. La marque a été ajoutée et les fins de ligne normalisées en CRLF, conformément à `.gitattributes`.

Un test, `tests/test_powershell_scripts.py`, vérifie désormais l'absence de guillemets typographiques, la présence de la marque UTF-8 sur tout script accentué, et soumet chaque script à l'analyseur Windows PowerShell.

### Le serveur d'outils MCP s'arrêtait sur toute erreur inattendue

Un appel d'outil ne rattrapait que `ValueError`, `OSError`, `KeyError` et `TypeError`. Toute autre exception traversait la boucle de lecture et terminait le processus, privant l'assistant de l'ensemble des outils.

Le cas se produisait de façon certaine dans le pack Windows client : celui-ci embarque `mcp_server.py`, qui annonce les six outils `bp_web_*`, mais aucun module `web_*.py`. Le premier appel levait `ModuleNotFoundError` et fermait la session.

Deux corrections : les outils web ne sont plus annoncés quand leurs modules sont absents de l'installation, et un outil défaillant renvoie une erreur sans détail interne au lieu d'interrompre la session. La version annoncée par le serveur suit désormais celle du paquet, au lieu d'un `0.1.0` figé.

### Chaque aperçu laissait une copie complète du classeur sur le disque

Un aperçu crée `transactions/web_preview_<identifiant>/apercu.xlsm`, et une application y ajoute la variante scellée du modèle. Rien n'effaçait ces répertoires : ni l'adoption, ni l'abandon du brouillon, ni le remplacement d'un aperçu par un autre. Le répertoire technique `.web-structure-<identifiant>` du pilote Excel était concerné par le même défaut.

Les copies devenues inutiles sont maintenant retirées à l'adoption, à l'abandon et au remplacement. La version publiée sous `versions/` et son reçu ne sont jamais touchés. Trois tests couvrent ces trois chemins.

### Lecture d'un dossier : 153 ms de hachage inutile à chaque appel

`get_case()` vérifie l'archive du modèle épinglé, ce qui relit et hache tous ses composants. Une archive mesure 247 Mo sur ce poste, dont 184 Mo pour le seul graphe de dépendances. Chaque lecture de dossier coûtait donc environ 153 ms de hachage, et cette lecture intervient à chaque saisie dans la grille, à chaque rafraîchissement et après chaque application.

L'empreinte complète est désormais calculée à la première vérification du processus, puis reprise tant que la taille et l'horodatage de chaque composant sont inchangés. Toute écriture, même de taille identique, modifie l'horodatage et impose une relecture complète.

| Mesure | Avant | Après |
|---|---|---|
| Vérification de l'archive | 158 ms | 5,3 ms |
| Détection d'une archive modifiée | oui | oui, vérifiée par essai |

### Le flux d'événements ne décroissait jamais

La table `web_events` n'était jamais purgée. Elle sert au rattrapage court d'un navigateur, alors que l'historique auditable vit dans `history` et `web_jobs`. Les deux mille derniers événements par dossier sont désormais conservés, et un index couvre la lecture par dossier. Les identifiants restant croissants, un curseur ancien reçoit toujours les événements suivants.

### L'identifiant de demande était régénéré à chaque tentative

Le serveur implémente une véritable clé d'idempotence : une demande déjà connue renvoie le travail existant au lieu d'en créer un second. L'interface tirait pourtant un identifiant neuf à chaque clic. Après une coupure de transport, un second envoi créait donc un deuxième recalcul, ou un deuxième appel facturé au fournisseur IA.

L'identifiant désigne maintenant l'intention et non la tentative. Il est conservé après une coupure de transport et renouvelé seulement après une réponse effectivement reçue du serveur. Les cinq actions concernées sont couvertes : conversation, reprise de tâche, application d'un lot, recalcul et restauration. Un test Playwright vérifie les deux comportements.

### Le flux d'événements n'était jamais reconstruit après une fermeture définitive

Quand le flux répond par une erreur HTTP, le navigateur ferme la connexion et ne retente jamais. L'interface restait indéfiniment sur « Reconnexion… » sans rien retenter, et continuait d'afficher l'ancienne révision, l'ancien brouillon et un bouton d'application armé sur un jeton périmé. Le repli par sondage ne s'active que lorsqu'un travail est en cours, donc à partir de données qui n'étaient plus rafraîchies.

Le flux est désormais reconstruit après une fermeture définitive, et une reconnexion réussie relit le dossier pour rattraper ce qui a été manqué. Le test correspondant échoue si la reconstruction est retirée, vérification faite.

### Une erreur restait affichée après changement de dossier

Le succès d'une action vérifiait que le dossier affiché n'avait pas changé, mais pas l'échec. Une erreur concernant le dossier A pouvait s'afficher au-dessus du dossier B. Le garde est désormais appliqué aux deux chemins.

### Un reçu de construction pouvait attester un modèle incomplet

`model_build` publiait `build_receipt.json` avant de régénérer le graphe de dépendances. Une reconstruction ultérieure s'arrête sur la seule présence de ce reçu : un échec de la dernière étape laissait donc un modèle incomplet considéré comme construit. L'ordre a été inversé.

### Une suppression masquait toutes les pertes de composants

Le contrôle de perte de composants du classeur était entièrement désactivé dès qu'une seule opération `delete_` figurait dans le lot. Une suppression de ligne masquait donc la disparition d'un graphique ou d'un tableau ailleurs dans le classeur. La perte est maintenant toujours signalée, bloquante hors suppression et consignée comme avertissement en présence d'une suppression demandée.

### Corrections mineures

- `zipfile.ZipFile(source)` était passé en valeur par défaut de `dict.get`, donc évalué à chaque construction et jamais fermé. La lecture réutilise le classeur déjà ouvert.
- `recovery_status` construisait deux fois la description complète du dossier.
- Import `sqlite3` inutilisé dans `service.py`.
- La version `0.3.0` était recopiée en dur dans le serveur web, la santé de l'API et le manifeste du pack. Ces trois points suivent maintenant `tca_bp.__version__`.
- Le message « Installer Python 3.14 avant de continuer » était inatteignable quand la commande `py` est absente : PowerShell échouait avant le test du code de retour.
- Le délai du travail d'intégration continue passe de 15 à 40 minutes ; la suite Python dure environ 9 minutes en local et l'exécution distante est plus lente.
- Le reçu de `verify_web_release` énumère désormais ce qu'il ne couvre pas : parcours navigateur, construction du pack, calculs Excel natifs et connexion au fournisseur réel.

## Points appelant votre décision

### Des documents d'un client réel sont indexés pour commit

Neuf fichiers du répertoire `exemple/`, soit environ 23 Mo, sont dans l'index Git et seront inclus au prochain commit : deux classeurs de prévisionnel, deux présentations, deux guides PDF, une archive et une note de livraison, tous nommés d'après un client identifiable.

Le fichier `.gitignore` exclut pourtant `exemple/`, `*.xlsm`, `*.pdf`, `*.pptx` et `*.zip` : ces fichiers ont donc été ajoutés en forçant l'exclusion. Le README énonce par ailleurs que « le dossier `exemple/`, les classeurs, les pièces, les résultats de recette et les espaces clients sont exclus des commits du logiciel ».

Un commit rend ces fichiers difficiles à retirer de l'historique. Je n'ai pas modifié l'index : retirer ces fichiers ou les conserver est votre décision.

```
git restore --staged exemple/
```

### Chaque lot appliqué crée une archive de modèle de 247 Mo

Toute application d'un lot scelle une variante privée du modèle, qui contient une copie du classeur et surtout un graphe de dépendances de 184 Mo et une classification de cellules de 59 Mo, écrits en JSON dense. Le modèle de base pèse déjà 248 Mo.

Cinq lots appliqués représentent donc environ 1,2 Go, en plus des copies de versions. Sur un poste dont le profil est synchronisé, l'effet est notable. Trois pistes, par ordre de risque croissant : compresser les composants JSON de l'archive, ne stocker que la différence par rapport au modèle parent, ou ne conserver le graphe que pour les modèles publiés. Toutes changent le format d'archive et ses vérifications ; c'est une décision de conception.

### Les campagnes de sensibilité conservent vingt-quatre copies du classeur

Chaque vérification des tables laisse un répertoire d'instruments contenant vingt-quatre copies scalaires complètes, jamais supprimé. Ces copies sont peut-être la matière des cinquante-sept comparaisons, donc une preuve à conserver. Si le reçu suffit à établir la preuve, leur suppression après adoption libérerait plusieurs centaines de mégaoctets par campagne.

### Les nombres collés depuis une source anglophone peuvent être mal interprétés

`parseValue` accepte indifféremment le point et la virgule comme séparateur décimal. La valeur `1,500` copiée depuis un site financier anglophone devient 1,5 au lieu de 1500. Rendre la règle stricte évite la confusion, mais change le comportement de saisie pour tous les utilisateurs : à arbitrer.

## Constats signalés, non corrigés

Classés par priorité. Aucun n'a été modifié, soit parce que le risque de régression dépassait le bénéfice sans validation Excel réelle, soit parce qu'il s'agit d'un choix produit.

### Processus Excel

- Si le superviseur abandonne avant d'avoir reçu l'identifiant du processus Excel, il tue PowerShell mais laisse l'instance Excel active. Le motif se répète dans le pilote structurel, le solveur WACC et le recalcul. Tuer les processus apparus entre-temps risquerait de fermer un classeur ouvert par l'utilisateur ; une correction sûre demande que le script lui-même se referme à la fermeture de son entrée standard.
- Une exception dans la fermeture du classeur, à l'intérieur du bloc final du script de sensibilité, saute l'appel à `Quit` et laisse un processus orphelin.
- Le délai de la campagne de sensibilité ne couvre ni la préparation des vingt-quatre copies ni les deux vérifications finales.
- La tolérance absolue de 0,01 appliquée à des montants en euros produit des écarts de jugement sur de grandes valeurs.
- Les évaluations du solveur WACC utilisent `Worksheet.Calculate` en mode manuel, ce qui peut laisser des dépendances inter-feuilles non recalculées.

### Atelier web et interface

- La copie d'une sélection entière lance une requête par bloc de cent lignes sans plafond, alors que le collage et la suppression sont bornés à deux mille cellules.
- L'état « occupé » est un booléen global : une action lente sur un dossier désactive les boutons de tous les autres.
- Chaque action déclenche sept requêtes, dupliquées par l'événement serveur et par le sondage.
- Le cache de cellules de la grille n'est jamais purgé pendant la navigation dans une feuille.
- Le téléchargement du classeur navigue la page entière et perd l'état de l'atelier en cas d'erreur.
- Les formats monétaires et comptables intégrés d'Excel manquent à l'affichage des cellules.
- Un profil complet est reconstruit par opération structurelle, au lieu d'une fois par lot.

### Service et moteur

- Un échec transitoire d'`apply_plan` rend le plan définitivement inapplicable sans issue documentée.
- `_open` laisse le classeur client ouvert, donc verrouillé, pour les exceptions hors du bloc protégé.
- La publication par lien physique échoue sur un système de fichiers qui ne les prend pas en charge.
- Chaque ouverture de classeur analyse intégralement les trente-trois feuilles au moins deux fois ; `ProfileEngine.context` ouvre et analyse le classeur deux fois par appel.
- La réécriture d'une formule ancre d'un groupe partagé peut orpheliner les autres membres du groupe.
- `map_between_profiles` lève une exception au lieu de signaler une feuille disparue.
- Les ancrages natifs du WACC et des sensibilités peuvent devenir tous nuls sans diagnostic bloquant.
- `open_workbook` et `export_report` accumulent des copies complètes du classeur.
- Les identifiants hérités des plages protégées et du partage de fichier ne sont pas retirés à la construction.

### Tests

- Le pilote natif structurel n'a aucun test, contrairement à ses équivalents WACC et sensibilités.
- La construction et la vérification du pack web ne sont pas testées.
- Le téléversement de pièce jointe n'est pas testé.
- Le flux d'événements n'est testé qu'au niveau du magasin, jamais en HTTP.
- La fixture Playwright neutralise le flux d'événements : toute la logique temps réel échappe aux tests navigateur.
- Les garde-fous du middleware ne sont que partiellement couverts : requête trop volumineuse, longueur invalide, en-têtes d'origine.
- Le protecteur DPAPI réellement utilisé en production n'est exercé qu'en dehors de son appelant.
- La reprise d'un travail interrompu n'est pas testée côté serveur HTTP ; elle l'est désormais côté interface.

### Dette

- `invalidate_caches` et `invalidate_chart` existent en double exemplaire.
- La reprise sur points de contrôle des sensibilités est inaccessible depuis le produit.
- Une lecture COM de sept références de base est immédiatement écrasée dans le script de sensibilité.
- Une installation non éditable produit un atelier web sans interface compilée ni modèle.

## Constats examinés puis écartés

Ces points ont été signalés puis réfutés par vérification directe. Ils figurent ici pour éviter qu'ils ne soient relevés à nouveau.

- **Trois dépendances frontend jamais importées.** `lodash`, `marked` et `react-responsive-carousel` ne sont importées nulle part dans `frontend/src`, mais ce sont des dépendances de pair exigées par `@glideapps/glide-data-grid`, et elles sont bien embarquées dans le bundle de production. Les retirer casserait la grille. La grille n'emploie par ailleurs que des cellules de type texte, donc `marked` n'est jamais appliqué à un contenu de cellule : il n'y a pas de voie d'injection de ce côté.
- **Le flux d'événements ne détecterait pas la déconnexion du navigateur sous le middleware.** Vérifié par essai réel avec la version installée de Starlette : à la fermeture du client, la boucle s'arrête et le générateur se termine. Aucune fuite de fil d'exécution.
- **L'import de pièce par MCP lit n'importe quel fichier local.** C'est la fonction attendue d'un serveur local qui importe un document désigné par l'utilisateur, sous son propre compte, avec liste d'extensions et limite de taille. Ce n'est pas une élévation de privilège.
- **Les versions de dépendances paraissaient fantaisistes.** `lodash 4.18.1`, `vite 8.3.0`, `@vitejs/plugin-react 6.1.1` et `glide-data-grid 6.0.3` sont bien installées et verrouillées.
- **Le classeur du dossier est haché à chaque lecture.** Exact, mais mesuré à 5,5 ms pour un classeur de 9,6 Mo. Affaiblir ce contrôle d'intégrité pour ce gain n'est pas justifié.

## Tests après modification

| Mesure | Avant | Après |
|---|---|---|
| Tests Python | 479 réussis | 489 réussis |
| Tests navigateur Playwright | 8 réussis | 10 réussis |
| Compilation TypeScript et Vite | réussie | réussie |
| Analyse des six scripts PowerShell | deux échecs | six réussites |

Aucun échec, aucun test ignoré ajouté. Les douze tests nouveaux couvrent le nettoyage des copies d'aperçu, la purge du flux d'événements, la résistance du serveur d'outils, la conformité des scripts PowerShell, la stabilité de l'identifiant de demande et la reconstruction du flux d'événements.

Deux de ces tests ont été vérifiés par réintroduction du défaut : ils échouent bien quand la correction est retirée.

## Documents de travail

Les soixante-deux constats bruts des lecteurs, avec leur preuve citée et leur correction proposée, sont conservés dans `runtime/audit_findings.json`, hors du dépôt.
