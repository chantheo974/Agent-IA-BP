# TCA BP Web 0.5.0 — guide de prise en main

L’atelier ouvre votre dossier TCA dans le navigateur, sur votre poste Windows. Le tableur, le chat, les documents et les versions travaillent sur le même dossier. Les modifications financières passent par un brouillon, un aperçu puis votre validation.

## Démarrer

1. Extraire le pack dans un dossier local, puis exécuter `Installer_TCA_BP_Web.ps1`. Python 3.14 et Microsoft Excel doivent être installés. Internet sert à installer les dépendances et l’OCR ; vos documents ne sont pas envoyés pendant cette installation.
2. Ouvrir `Lancer_TCA_BP_Web.cmd`. Le navigateur utilise normalement `http://127.0.0.1:8765`. Garder le serveur local ouvert pendant le travail.
3. Choisir un dossier existant à gauche ou **Nouveau dossier** pour partir de la trame TCA.

Le pack contient l’interface compilée : Node n’est pas nécessaire pour l’utiliser. Un seul serveur doit utiliser un stockage donné. Depuis le dépôt, construire l’interface avec `npm ci` puis `npm run build` dans `frontend`, et lancer à la racine `.venv\Scripts\python.exe -m tca_bp.web_server`. L’option `--data-dir "chemin"` permet un stockage de test distinct.

Les nouveaux dossiers de ce pack partent de la trame corrigée et épinglée dans `models/initial-web.json`. Les 71 corrections de calendrier et de contrôles sont déjà intégrées ; les trois migrations techniques décrites plus bas concernent les anciens modèles. Les hypothèses propres à votre entreprise et les qualifications restent à renseigner. Un ancien dossier conserve son modèle et ses sources lorsqu’il est rouvert.

Les données résident par défaut dans `%LOCALAPPDATA%\TCA_BP\<identifiant de l’installation>`, séparément du ZIP. Installer le logiciel ailleurs ouvre donc un autre stockage. Pour reprendre le précédent, fermer son ancien serveur puis exécuter `Lancer_TCA_BP_Web.cmd --data-dir "chemin du stockage existant"`. Choisir le répertoire qui contient `tca_bp.sqlite3` et `dossiers`, en conservant également ses archives `modeles` ; ne sélectionner ni un seul classeur ni seulement le sous-dossier d’une entreprise.

## Construire le premier prévisionnel

Le nouvel accueil est le cockpit connecté à vos dossiers locaux. **Parcours** ouvre six thèmes : ventes, coûts, équipe, investissements, trésorerie et synthèse. **Personnaliser** donne accès au profil de l’entreprise, au prénom, au logo et aux trois palettes. **Mode expert** ouvre le catalogue des feuilles, leur fiche métier, leur grille et leurs dépendances. **Documents**, **Simulations**, **Décisions**, **Suivi mensuel** et **Livrables** réutilisent les services du dossier.

Pour tester une modification, choisir une source, préparer les entrées métier et examiner **le brouillon**. Dans **Simulations**, nommer l’essai puis lancer son calcul. La copie reçoit les hypothèses et les sources ; la référence reste intacte. **Conserver le scénario** garde cet essai pour le rouvrir et le comparer. **Préparer l’adoption** reprend ses changements au brouillon de la référence : vérifier l’aperçu, approuver, appliquer puis recalculer. Un dossier ou brouillon modifié entre-temps exige un nouvel examen.

Les grilles du cockpit protègent les formules, résultats et cellules hors du catalogue de saisie. Pour une modification du modèle (formule, ligne, colonne ou feuille), ouvrir `/atelier`, l’espace de maintenance conservé. Les étapes détaillées ci-dessous décrivent aussi ses intitulés historiques. Ne pas mélanger un lot de maintenance avec un lot métier en cours.

La démonstration `/demo` utilise exclusivement des données fictives locales au navigateur. Sa bannière la distingue des dossiers réels. Elle propose des cas préparés ; une combinaison non couverte ne produit pas de nouveaux résultats financiers. Ses aperçus documentaires sont des vues web ; les vrais fichiers se génèrent dans **Livrables** du cockpit connecté.

1. **Entreprise** : décrire l’activité, les revenus, les objectifs et les modules. Choisir la première année, un horizon de 1 à 10 ans et le démarrage d’activité. Enregistrer le profil, puis **Proposer ce calendrier au classeur**. Les exercices suivent janvier–décembre ; renseigner aussi les dates propres aux ventes, contrats et recrutements.
2. **Documents** : importer une pièce ou une réponse écrite, puis **Extraire les informations**. **Examiner les preuves** permet de lire le texte et sa localisation, d’ouvrir le fichier source lorsqu’une pièce est jointe, de corriger une valeur retenue et de choisir son champ destinataire. Sélectionner les faits utiles avant de les proposer au brouillon. Une extraction incertaine reste à vérifier ; les limites OCR et les valeurs issues de caches de formules sont signalées avant confirmation.
3. **Prévisionnel** : utiliser le tableur ou **Hypothèses guidées**. Cliquer sur la référence d’un champ ouvre sa cellule. Préciser si une réponse est une hypothèse ou une information confirmée, et choisir sa source.
4. Pour un contrat, recrutement, investissement ou financement, utiliser **Ajouter une opération métier**. Choisir le registre et sa source, puis compléter les questions de l’agent. Les valeurs calculées restent conservées. Une ligne libre insérée dans la grille ne devient pas automatiquement une ligne métier qualifiée.
5. Ouvrir **Voir le lot**, puis **Vérifier l’aperçu**. Examiner anciennes et nouvelles valeurs, formules, changements de structure et contrôles. Les grands lots sont présentés par pages, avec accès direct à la dernière page. Si une extension de structure affiche un échantillon, son nombre total est annoncé : utiliser **Télécharger tous les changements de structure** pour examiner le détail complet avant application. Résoudre les conflits avant **Appliquer en nouvelle version**.
6. **Recalculer**, puis examiner les résultats et graphiques avec leur statut. La grille ne recalcule pas les formules : cette étape utilise Excel sur une copie du dossier.

Dans **Confirmer les modules et les règles du dossier**, choisir le module, son application active ou inactive, sa qualification et sa source, puis justifier la déclaration. Les règles fiscales demandent aussi juridiction et dates de validité. **Examiner cette qualification** affiche ces éléments avant adoption. Les questions restantes guident les compléments nécessaires ; des chiffres remplis ne qualifient pas automatiquement une activité ou une règle.

Le catalogue peut être étendu par **Préparer une offre supplémentaire** dans Scénarios ; cette version ajoute une offre de produit libre selon la recette du modèle. L’extension qualifiée du registre Effectifs apparaît dans son formulaire, de 1 à 50 lignes entières par lot. Les autres registres utilisent leurs emplacements disponibles. Les menus de feuille proposent aussi valeurs, formules, lignes, colonnes et feuilles, sous réserve des contrôles du modèle.

**Convention des effectifs : le mois de sortie est exclu du calcul.** Une entrée au 1er janvier et une sortie au 31 décembre comptent 11 mois dans la trame conservée. Avec 60 000 € de salaire annuel et 40 % de charges, le coût est donc 77 000 €. Vérifier cette convention lors de la saisie ; la date de sortie n’est pas inclusive.

## Utiliser le chat et le tableur ensemble

Dans les réglages, enregistrer adresse API, modèle et clé, puis **Tester la configuration enregistrée**. `deepseek-v4-pro` est la valeur initiale ; les suggestions de modèles sont actualisées depuis le fournisseur sans remplacer silencieusement votre choix. La clé est protégée pour le compte Windows courant et n’est pas renvoyée au navigateur après enregistrement.

L’essai réel du chat avec la clé et le fournisseur configurés reste à réaliser pour cette livraison. Les tests avec un fournisseur simulé et le contrôle de configuration ne remplacent pas cet essai.

Sélectionner une plage, puis **Discuter de cette sélection**. Le chat consulte les dépendances utiles. Pour préparer des changements sur plusieurs feuilles, cocher explicitement ces feuilles dans son périmètre. La plage sélectionnée reste la limite de la feuille principale ; les feuilles supplémentaires sont désignées en entier. Les propositions rejoignent le brouillon de la grille ; elles ne sont pas appliquées directement. Le fournisseur reçoit la demande et les extraits nécessaires du dossier courant. En l’absence de clé opérationnelle, formulaires et tableur restent utilisables.

Un collage demande de choisir le format numérique français ou anglais et d’examiner les conversions. Collage et effacement sont limités à 2 000 cellules par lot dans la grille ; la copie est limitée à 20 000 cellules. Les identifiants commençant par zéro restent conservés.

## Comparer les décisions

**Scénarios** crée des copies nommées avec leur révision de départ. Ouvrir une copie, modifier ses hypothèses, appliquer et recalculer ; la référence reste conservée. Les indicateurs non calculés sont signalés plutôt que remplacés par un ancien résultat en cache. Dans **Comparaison mensuelle des scénarios**, choisir trésorerie, chiffre d’affaires, encaissements ou décaissements : les colonnes sont alignées par mois. **À compléter** distingue une donnée absente de **Hors période**, qui indique un mois extérieur au calendrier du scénario.

Les scénarios, recherches d’objectif et analyses de sensibilité utilisent le prévisionnel. La prévision actualisée avec les données réelles reste une vue séparée dans **Réalisé** ; ses corrections ne sont pas intégrées automatiquement à ces simulations.

- **Capital et dilution** : renseigner les associés et leurs titres, puis les tours successifs en numéraire. Le pool salarié est exprimé en pourcentage pleinement dilué, constitué avant le tour par défaut. Calculer l’aperçu, vérifier la répartition par tour puis adopter explicitement la simulation. Si le pool existant dépasse une nouvelle cible plus basse, il reste conservé : l’aperçu le signale et affiche le pourcentage obtenu.

Dans cette simulation, chaque tour représente un groupe distinct de nouveaux investisseurs. Les titres peuvent être fractionnaires pour montrer la dilution économique. La répartition entre plusieurs investisseurs d’un même tour, la consolidation d’un réinvestissement par un associé existant et les arrondis d’une émission juridique ne sont pas calculés.
- **Recherche d’objectif** : choisir un levier numérique, ses bornes et une cible. Le point bas de trésorerie porte sur le début du prévisionnel jusqu’au mois choisi ; le résultat porte sur l’année contenant ce mois. La valorisation utilise l’horizon et la date de référence du modèle. Le solveur ne change pas le WACC pour atteindre la cible. Le résultat est un scénario à examiner ; une cible peut être impossible ou non calculable.
- **Analyses de sensibilité** : choisir un ou deux axes distincts, de 2 à 20 valeurs par axe séparées par `;`, au format français. L’interface limite une campagne à 25 combinaisons. **Tâches** permet de suivre, interrompre ou reprendre les campagnes ; les points terminés restent consultables.

Pour les horizons courts, **Contrôle de fraîcheur du WACC** permet de **Mettre à jour le contrôle WACC**. Cette migration prépare cinq formules de contrôle au brouillon, sans changer le taux de valorisation. Si elle est déjà effectuée, le brouillon existant reste conservé.

À proximité, **Formules de valorisation et horizon** propose **Adapter la valorisation à l’horizon**. Cette autre migration prépare dix formules DCF qui excluent les années inactives ; les données manquantes des années actives restent à compléter. Terminer ou retirer le brouillon courant, préparer la migration, examiner les anciennes et nouvelles formules, puis appliquer et recalculer. Une migration déjà effectuée conserve le brouillon existant.

**Fiscalité, trésorerie et horizon** propose aussi **Adapter fiscalité et trésorerie à l’horizon**. Cette migration prépare 56 formules : 55 agrégats annuels et l’indicateur de date de rupture de trésorerie `KPI Dashboard!E68`. Dans ce lot, les périodes non sélectionnées sont exclues, mais les erreurs des périodes retenues restent visibles. Elle demande également un brouillon libre, un aperçu et une application explicite ; une migration déjà effectuée conserve le brouillon existant.

Si les trois migrations sont nécessaires, examiner et appliquer d’abord les **cinq contrôles WACC**, puis préparer, examiner et appliquer les **dix formules DCF**, puis les **56 formules de fiscalité et trésorerie**. Conserver trois lots distincts : leurs contrôles de migration sont spécifiques. Confirmer ensuite les qualifications requises pour le nouveau modèle, puis recalculer et résoudre le WACC. Les qualifications liées à l’ancien modèle ne sont pas transférées silencieusement ; préparer ou appliquer ces formules ne suffit donc pas à rendre la valorisation exploitable.

## Importer le réalisé mensuel

Recalculer d’abord le budget de référence et examiner ses contrôles. La première validation du réalisé exige un budget calculé exploitable, conservé séparément.

Dans **Réalisé**, choisir un arrêté au dernier jour du mois et le format des nombres. Importer un CSV ou le premier tableau d’un XLSX/XLSM contenant des valeurs, ou saisir les lignes manuellement. Les périodes utilisent `AAAA-MM`. Associer les colonnes période, poste et valeur, puis les libellés du fichier aux postes métier. Exemple : `CA` vers **Chiffre d’affaires**, `Banque` vers **Trésorerie**. Sans colonne de nature associée, le poste détermine flux, solde ou volume. Les formules importées et les conversions ambiguës produisent un diagnostic.

Pour un CSV, choisir explicitement son encodage : **UTF-8** par défaut, avec ou sans BOM, ou **Windows-1252**. Vérifier les accents des en-têtes après lecture. En cas d’erreur, changer ce choix puis relire le fichier ; l’encodage retenu est conservé dans la trace de l’import.

Vérifier l’aperçu puis adopter les données. Les corrections sont historisées ; les mois absents restent manquants. **Préparer le raccord dans Excel** prépare ensuite le brouillon de raccord : examiner son aperçu, appliquer et recalculer. Budget initial, réalisé et prévision actualisée restent distincts. Une trésorerie ou un bilan non raccordé ne constitue pas une prévision exploitable.

Le formulaire de raccord demande les valeurs du modèle à l’arrêté lorsqu’elles ne sont pas liées automatiquement, leurs sources et le traitement des écarts de trésorerie, créances, stocks, actifs, fournisseurs, dettes, passifs et capitaux propres. Aucune politique n’est choisie par défaut. Les corrections mensuelles comportent des écritures débit/crédit équilibrées, une source et une explication. Elles sont **nettes par rapport au modèle** : ne pas ajouter de nouveau des encaissements ou remboursements déjà prévus. Chaque écriture de trésorerie précise le flux corrigé, encaissements ou décaissements, y compris lorsque sa correction diminue le flux existant. Une correction de résultat net demande un traitement fiscal explicite ; aucun impôt mensuel n’est inventé. Une préparation partielle conserve ses questions et reste à compléter.

**Aide à la correspondance comptable** consulte les fichiers PCG fournis au projet. Les correspondances sont indicatives, datées et à confirmer selon le compte, ses auxiliaires et l’arrêté ; elles n’appliquent aucune écriture. Cette aide ne réalise pas un import automatique de balance ou de grand livre et ne transforme pas un solde en encaissement.

## Produire les livrables et reprendre un dossier

Dans **Livrables**, **Préparer les quatre livrables** crée Excel, PDF, Word et PowerPoint à partir d’un même instantané calculé. Consulter les diagnostics avant téléchargement. Le PowerPoint utilise des tableaux et graphiques éditables ; le classeur reste modifiable. Le lien facultatif **Détail des chiffres (JSON)** donne accès à l’instantané partagé pour examiner ses données précises.

Pour reprendre des corrections externes, choisir l’Excel téléchargé depuis ce jeu de livrables et **Comparer et préparer les corrections**. Seules les entrées reconnues rejoignent le brouillon ; une origine inconnue ou une modification de formule ou de structure produit un diagnostic. Le téléchargement direct du classeur reste disponible, mais utiliser le jeu de livrables pour le réimport contrôlé.

**Historique** conserve les copies précédentes. Restaurer crée une nouvelle révision ; les anciennes preuves restent conservées. L’espace utilisé et disponible est visible dans Livrables.

La fermeture du navigateur n’arrête pas une tâche déjà reçue. Rouvrir l’atelier recharge son état. Après coupure, réessayer la même demande retrouve son identifiant ; une demande ambiguë ouvre **Examiner une demande interrompue**. Lire l’état conservé avant une éventuelle clôture explicite : elle ne relance aucun traitement. Ne préparer une nouvelle demande qu’après vérification du dossier.

## OCR local et limites

L’installateur prépare Tesseract et les modèles français/anglais pour votre compte sous `%LOCALAPPDATA%\TCA_BP\runtimes\tesseract`. Le rendu des PDF et l’OCR sont locaux. Contrôle sans téléchargement : `.venv\Scripts\python.exe tools\install_ocr.py --check`. Une installation Tesseract existante peut aussi être désignée par `TCA_TESSERACT_PATH`, avec les langues `fra` et `eng` opérationnelles. Une indisponibilité de l’OCR ou une page illisible est signalée dans les extractions.

Le prototype concerne la trame TCA et ses variantes contrôlées. Hébergement, comptes clients, abonnements, connexions bancaires/comptables, instruments convertibles, modification du VBA et modèles Excel sans lien avec la trame ne sont pas inclus. Les composants VBA sont préservés ; les traitements habituels s’exécutent sans macros.

Ce guide décrit le fonctionnement ; il ne certifie pas la validité économique des hypothèses ni une recette complète. Les vérifications et leurs limites figurent dans [RECETTE_WEB.md](RECETTE_WEB.md). Pour un retour, noter dossier/révision, action, résultat attendu et résultat obtenu, puis joindre le diagnostic visible sans clé API.
