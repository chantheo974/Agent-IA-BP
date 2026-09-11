# Atelier business plan TCA Conseil

L'atelier est une application Windows locale en français. Son interface native Tkinter est fournie avec Python 3.14 ; aucun serveur web n'est nécessaire. L'installation du projet ajoute notamment le lecteur PDF `pypdf`. Le service du projet conserve les dossiers, les sources et les versions Excel.

Après l'installation décrite dans le [guide de démarrage](../README.md), double-cliquer sur **Lancer_TCA_BP.cmd**. Depuis le répertoire du projet, la commande équivalente utilise l'environnement installé :

```powershell
.venv\Scripts\python.exe -m tca_bp gui
```

## Premier dossier

1. Cliquer sur **Nouveau dossier**, puis renseigner le client et le nom du dossier.
2. Dans **Documents et preuves**, importer les pièces disponibles ou enregistrer une réponse écrite avec son contexte. L'enregistrement d'une pièce ne confirme pas ses hypothèses.
3. Dans **Conversation**, décrire le besoin. Le coordinateur indique les feuilles concernées et pose les questions utiles. Une conversation ne modifie pas directement le classeur.
4. Dans **Saisie guidée**, choisir un agent de feuille. Les 33 fiches expliquent les rôles, dépendances, informations requises et contrôles. Le calendrier et l'horizon se règlent parmi les champs autorisés de **Control**.

Le dialogue de l'atelier est guidé par des règles et des questionnaires. Il ne transforme pas automatiquement une pièce en valeurs validées. Un assistant externe compatible peut utiliser les mêmes outils par MCP ; son raisonnement reste soumis aux preuves et à la validation des propositions. Les possibilités livrées et leurs limites sont recensées dans l'[état de livraison](ETAT_LIVRAISON.md).

## Préparer et appliquer des valeurs

La liste des champs vient du catalogue du modèle. Son filtre permet de retrouver une entrée par son nom. Choisir un champ affiche ses emplacements, la valeur actuelle et son état documentaire. Lorsqu'un champ possède plusieurs emplacements, la liste permet de choisir celui à modifier ; aucune adresse n'est à taper.

Les nombres acceptent la notation française, par exemple `125 000`, `1 250,50` ou `4 %`. Un pourcentage suivi de `%` est converti en taux : `4 %` donne `0,04`. Sans `%`, `4` reste `4`. Les dates acceptent `JJ/MM/AAAA` ou `AAAA-MM-JJ`. Zéro doit être renseigné explicitement. Une entrée vide n'est jamais convertie en zéro.

Associer chaque saisie à une **source**, choisir son **état** et préciser une justification. **Hypothèse** et **Confirmé** expriment le statut documentaire. Pour désactiver un module, renseigner son véritable champ d'activation : une étiquette documentaire ne neutralise pas ses calculs. Pour effacer une entrée autorisée, cocher **Effacer l'entrée** : la proposition porte alors l'état **Non renseigné**. Le moteur reste responsable de toutes les contraintes et des refus.

Les options de remplacement permettent de préciser l'intention de remplacer une valeur déjà renseignée ou un défaut calculé lorsque le modèle l'autorise. Cliquer sur **Ajouter à la proposition**, puis répéter l'opération pour les autres champs du lot.

**Vérifier et prévisualiser** prépare la proposition. Le tableau avant/après utilise l'instantané contrôlé par le moteur. Si des informations manquent, les questions sont affichées et l'application reste indisponible. Cliquer sur **Appliquer dans une nouvelle copie** est l'action qui produit la nouvelle version ; les versions antérieures restent conservées. L'état des calculs doit ensuite être consulté.

## Ajouter une ligne à un registre

Choisir **Ajouter une ligne au registre**, sélectionner les champs de la ligne et leurs valeurs. Toutes les informations d'une ligne utilisent une même source. Le moteur choisit une ligne disponible et demande les éléments manquants avant application. Il n'est pas nécessaire de mémoriser les adresses Excel. Les lignes complètes sont proposées par les registres pris en charge ; le moteur refuse un ajout sur une feuille qui n'est pas un registre.

Une proposition ne mélange pas ajout de ligne et modification de champs. La vider ou l'appliquer avant de changer de mode. Changer de feuille conserve les champs déjà proposés ; une ligne nouvelle porte toujours sur un seul registre.

## Suivre le dossier

- **Vue d'ensemble** : version du classeur, référence exacte du modèle, disponibilité de son archive, état des calculs, sources et questions ouvertes. Les fiches et les champs utilisent la version du dossier sélectionné. Pour un ancien dossier non épinglé, **Rattacher l'ancien modèle** vérifie la copie initiale et la version choisie ; ce parcours ne migre aucun dossier. Voir [Versions de modèle](MODELES_ET_VERSIONS.md).
- **Qualifications** : déclarer les modules actifs ou inactifs avec une source, une justification et un statut explicite ; puis examiner les prérequis de CA, coûts, trésorerie, fiscalité et DCF. Les règles fiscales exigent une juridiction et une période d'application. Voir [Qualifications et disponibilité](QUALIFICATIONS.md).
- **Recalculer dans Excel** : lance explicitement le recalcul natif. L'option des tables de sensibilité ajoute leur traitement au périmètre. Excel doit être disponible et les conditions du service respectées. Les macros restent désactivées : ce bouton ne lance pas la résolution WACC. Le résultat indique le périmètre exécuté ; un recalcul ne valide pas les hypothèses économiques.
- **Résoudre le WACC** : demande une résolution locale sur la version enregistrée, puis l'enregistrement d'une nouvelle version si les contrôles du service passent. Le reçu précise le taux, le résidu et les limites de convergence. Le délai maximal de l'interface est de dix minutes ; aucune macro n'est exécutée.
- **Vérifier les sensibilités** : demande la confrontation des tables natives aux scénarios scalaires isolés. Le reçu présente les concordances et la conservation de la base. Le délai maximal de l'interface est d'une heure. Ce contrôle distinct ne vaut pas validation économique globale.
- **Ouvrir le classeur** et **Afficher les fichiers** : ouvrent la version courante ou le répertoire du dossier.
- **Rapport du dossier** : génère le rapport puis l'ouvre dans l'application Windows associée.
- **Historique** : affiche les opérations et versions. Un double clic présente leur détail.

Les opérations lentes passent dans un fil de travail. La fenêtre reste disponible pour la lecture, les actions concurrentes sont désactivées et la fermeture attend l'opération en cours. Les erreurs du service sont présentées sans interrompre l'atelier.

Les deux actions de vérification ne se déclenchent ni à l'ouverture ni à l'actualisation du dossier. Une proposition de saisie en cours doit être appliquée ou vidée avant de les lancer. Le statut, la nouvelle révision et le chemin du reçu sont présentés après l'action ; la présence d'un bouton ne constitue pas une preuve de calcul exécuté.

Les commandes équivalentes sont `python -m tca_bp solve-wacc identifiant_du_dossier --timeout 600` et `python -m tca_bp verify-sensitivity identifiant_du_dossier --timeout 3600`. Les outils MCP `bp_solve_wacc` et `bp_verify_sensitivity` prennent `case_id` et un délai facultatif `timeout` en secondes, dans les mêmes bornes. Les sources, le modèle exact et les prérequis restent contrôlés par le service commun.

## Vérification de l'interface

Les tests unitaires ci-dessous sont disponibles dans le dépôt de développement. Le pack client ne contient pas le dossier `tests`.

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p test_gui.py -v
```

Le parcours fictif caché est également disponible dans le pack client :

```powershell
.venv\Scripts\python.exe -m tca_bp.gui --smoke
```

Le mode `--smoke` instancie Tk dans une fenêtre cachée avec un service fictif. Il exerce la création d'un dossier, l'ajout d'une preuve, la saisie typée, l'aperçu, l'application d'une version et la conversation. Il ferme ensuite la fenêtre et publie un résultat JSON. Il ne lit ni ne modifie de données client et ne lance pas Excel. Ce test de parcours complète les tests du moteur et du service ; il ne remplace pas une recette de recalcul natif.
