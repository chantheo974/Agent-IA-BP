# Modification versionnée du modèle

Le parcours de maintenance crée une **version distincte du modèle**, avec ses propres empreintes, carte et tests. Il ne remplace pas la trame courante et ne modifie aucun dossier existant. Il est séparé de la saisie métier.

Le périmètre implémenté est la modification de **formules ordinaires existantes**, y compris une cellule appartenant à un groupe de formules partagées. Ajouter une feuille ou colonne, modifier une macro, modifier une formule matricielle ou la définition d'une table native exige un développement distinct. La saisie courante ne peut pas ouvrir ces droits.

## 1. Préparer une proposition contrôlable

```python
from tca_bp.maintenance import Maintenance

maintenance = Maintenance(engine)
proposal = maintenance.propose(
    changes=[{
        "sheet": "FEUILLE_EXISTANTE",
        "cell": "ADRESSE_FORMULE_EXISTANTE",
        "formula": "NOUVELLE_FORMULE_EXCEL",
        "reason": "Règle économique attendue et différence avant/après."
    }],
    version_id="tca-bp-template/2",
    reason="Description de l'évolution demandée et de son périmètre."
)
```

La proposition contient l'ancienne formule effective lue dans le modèle, la nouvelle formule, le modèle et le SHA de départ, le périmètre métier affecté et sa base documentaire. Son empreinte permet de détecter une modification entre préparation et construction.

Les références externes et fonctions appelant un service ou du code externe sont exclues de ce parcours. Les fonctions Excel de calcul restent soumises aux vérifications et essais natifs ; une formule acceptée comme texte n'est pas une preuve de validité économique.

Le graphe extrait de la version sert à propager l'impact par feuille. S'il est absent, les contrats métier fournissent une estimation conservatrice, identifiée comme telle. Les références dynamiques et la macro WACC nécessitent toujours une qualification propre.

`component_impact` complète ce périmètre : consommateurs directs, références nouvelles, noms définis, tables natives, sorties WACC, clés de catalogue, constantes protégées référencées, validations et objets. Il distingue les références réellement localisées de la propagation conservatrice par feuille. Les constantes sont désignées par adresse, sans recopier leur contenu dans le rapport. L'empreinte du graphe est liée à la proposition et revérifiée avant construction.

Le rapport porte aussi `model_ref`, `source_template_sha256` et `source_schema_sha256`, relus par le registre des modèles, avec `graph_sha256`. Ces éléments identifient les composants examinés ensemble, y compris lorsque deux variantes conservent le même identifiant de modèle. Ils sont revérifiés après analyse puis lors de la construction de la proposition figée. Une nouvelle empreinte de schéma ou de graphe exige une nouvelle proposition. Aucun archivage ni changement du modèle ne découle de cette lecture.

Les appels `INDIRECT` et `OFFSET` sont repérés dans les formules courantes **et dans les nouvelles formules proposées**. Le rapport distingue les nouveaux appels dans `proposed_dynamic_references_to_review` ; les chaînes de texte et noms de feuilles cités ne sont pas assimilés à des fonctions. Leur présence impose une revue de leurs destinations et des essais ; cette détection ne résout pas leur cible. Le champ `graph_derivation_verified` reste `false` : les empreintes assurent la traçabilité des composants, pas une preuve de dérivation ou d'exhaustivité du graphe.

La couverture statique reste explicitement incomplète : les objets et références dynamiques appellent une revue et une recette native. Par exemple, la modification du dernier exercice `Control!C60` touche 31 feuilles dans la trame 1.1.2 ; le rapport identifie 49 092 consommateurs directs, les trois tables et la chaîne WACC. Il ne transforme pas ces dépendances en autorisations d'écriture.

## 2. Construire une version expérimentale

```python
version = maintenance.build(proposal)
```

La construction vérifie à nouveau le modèle de départ, les anciennes formules et la proposition. Elle prépare un paquet XLSM dans un espace temporaire, modifie les formules prévues et supprime les caches de calcul. Si une ancre de formule partagée change, les autres membres sont matérialisés en formules ordinaires équivalentes.

Le moteur effectue ensuite le contrôle de scellement : les différences de formules doivent correspondre aux modifications prévues. Les entrées, constantes et composants hors impact doivent rester conformes. La nouvelle carte est liée au nouveau modèle. La source est contrôlée inchangée avant publication du répertoire.

Le résultat est placé dans un sous-dossier dédié de `models/versions/`. Le statut est `EXPERIMENTALE`. `maintenance.json` documente la proposition et les empreintes. La présence d'une version expérimentale ne l'active pas pour les utilisateurs.

## 3. Vérifier avec des attentes indépendantes et Excel

```python
validation = maintenance.validate(version["model_dir"], [
    {
        "name": "Nom du cas fictif",
        "fictional": True,
        "updates": [
            {
                "sheet": "FEUILLE_ENTREE",
                "cell": "ADRESSE_ENTREE",
                "value": 2,
                "reason": "Entrée fictive documentée pour le cas de test.",
                "evidence": "TEST_FICTIF_001"
            }
        ],
        "outputs": [
            {
                "sheet": "FEUILLE_MODIFIEE",
                "cell": "ADRESSE_FORMULE_MODIFIEE",
                "expected": 6,
                "tolerance": 0.000001
            }
        ],
        "include_tables": False
    }
])
```

Ces valeurs illustrent seulement le format. L'attendu doit se déduire de la règle métier indépendamment de la formule codée. **Chaque formule modifiée doit apparaître dans au moins une attente native.** Ajouter également des contrôles de ses consommateurs et des cas limites pertinents.

Pour chaque scénario, le moteur prépare les entrées fictives dans une copie. Excel recalcule une autre copie avec macros désactivées. Le protocole vérifie :

- fin du calcul natif et concordance des empreintes source/sortie ;
- signature des entrées inchangée pendant le recalcul ;
- compatibilité de la copie avec la nouvelle version ;
- valeur de chaque sortie comparée à l'attendu, selon la tolérance indiquée.

Les scénarios, fichiers produits, preuves Excel et résultats détaillés sont conservés dans `validation/run_.../`. Une erreur de calcul, une incompatibilité ou un attendu non satisfait produit `FAIL`. L'absence d'Excel produit également un échec de validation ; aucun calcul Python n'est présenté comme Excel.

Ce parcours n'exécute pas le bouton WACC. Une modification affectant le WACC ou la définition des tables ne peut pas être qualifiée seulement par ce jeu d'oracles ordinaires.

## Commandes utilisables depuis le terminal

Les fichiers JSON sont lus en UTF-8. `changements.json` contient la liste `changes` de la première étape ; `scenarios.json` contient la liste des scénarios de la troisième étape. Les chemins ci-dessous sont des exemples à remplacer par les fichiers réellement préparés.

```powershell
py -3.14 -m tca_bp maintenance-propose changements.json --version "tca-bp-template/2" --reason "Règle et périmètre de l'évolution demandée." --out proposition.json
py -3.14 -m tca_bp maintenance-build proposition.json
py -3.14 -m tca_bp maintenance-validate "models/versions/version_RETOURNEE" scenarios.json
```

`maintenance-propose` n'écrit aucune formule et refuse d'écraser `--out`. Sans `--out`, la proposition complète est rendue en JSON sur la sortie standard. `maintenance-build` renvoie le chemin réel `model_dir` de la nouvelle version. `maintenance-validate` rend `PASS` ou `FAIL`, conserve ses preuves et renvoie un code de sortie 1 si un oracle échoue. Une demande refusée renvoie le code 2.

Pour partir d'une variante existante, passer explicitement `--model-dir CHEMIN` à `maintenance-propose` puis à `maintenance-build`. Les deux étapes vérifient l'identifiant et les empreintes du même modèle de départ. Ces commandes ne créent aucun dossier client.

## 4. Valider la publication

```python
publication = maintenance.approve(
    version["model_dir"],
    validation["report_path"],
    approved_by="Responsable ayant explicitement validé cette version"
)
```

L'opération exige un rapport natif `PASS` correspondant exactement à la proposition, au modèle et aux empreintes du classeur et du manifeste. Elle revérifie les fichiers de preuve, le fichier original des scénarios et chaque valeur attendue en relisant le classeur recalculé. Modifier un indicateur `PASS` dans le rapport ne remplace donc pas l'oracle. Elle refuse une publication déjà existante.

`publication.json` identifie le responsable, la preuve et la version publiée. **Publier ce descripteur ne remplace pas le modèle par défaut et ne migre aucun dossier existant.** Pour utiliser la version, instancier explicitement `ModelEngine(project_root, model_dir=...)` ; les dossiers doivent rester liés à leur version d'origine tant qu'une migration distincte n'est pas autorisée et vérifiée.

L'approbation nominative est une trace locale de la décision du responsable, pas un mécanisme d'authentification ou de signature électronique.

Après la décision explicite du responsable, la commande équivalente est :

```powershell
py -3.14 -m tca_bp maintenance-approve "models/versions/version_RETOURNEE" "CHEMIN_DU_RAPPORT_VALIDATION.json" --approved-by "Nom du responsable"
```

Cette commande n'est pas exposée comme une approbation automatique au serveur MCP. Une recette technique exécutée par un assistant s'arrête avant cette décision.

## Tests du protocole

```text
py -3.14 -m unittest tests.test_maintenance tests.test_maintenance_impact -v
```

Les tests unitaires utilisent un **paquet OOXML fictif** et un témoin de recalcul simulé. Ils démontrent la modification XML, la conservation d'une formule partagée hors impact, les refus, la liaison des preuves et le processus de publication. Ils ne constituent ni un calcul Excel réel ni une certification de toutes les formules du business plan.

## Exemple de recette native limitée

Les fichiers [maintenance-calendrier-changements.json](exemples/maintenance-calendrier-changements.json) et [maintenance-calendrier-scenarios.json](exemples/maintenance-calendrier-scenarios.json) préparent une réécriture équivalente de `Control!C60`, dernière année du plan. L'ancien calcul `YEAR($C$10)+$C$59-1` devient `YEAR($C$10)+SUM($C$59,-1)`.

L'oracle se déduit directement de la liste des trois exercices fictifs **2030, 2031, 2032**. Le scénario saisit le 1er janvier 2030 et un horizon de trois ans, puis attend exactement 2032. Cette recette exerce la proposition, le scellement et un calcul réel d'une formule. Elle ne qualifie pas les résultats financiers, la fiscalité, les tables de sensibilité ou le WACC. Son exécution technique ne vaut pas approbation du responsable.

Ces deux fichiers décrivent une recette ; seuls les rapports d'exécution conservés dans la version testée attestent de son résultat sur un poste donné.

La [recette exécutée le 11 septembre 2026](RECETTE_MAINTENANCE.md) documente le résultat natif, les empreintes et les limites observées. Elle s'est arrêtée avant toute approbation de publication.
