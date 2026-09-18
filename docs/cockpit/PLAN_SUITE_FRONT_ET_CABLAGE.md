> Archive documentaire de conception du 15–16 septembre 2026, publiée sans chemins personnels. Les états décrits ci-dessous précèdent l’intégration. Voir [le suivi actuel](../INTEGRATION_COCKPIT.md).

# Plan de reprise : terminer le cockpit, puis le câbler au moteur

Date : 16 septembre 2026. Statut : plan de travail, pas compte rendu d’une réalisation.

Projet : `frontend/src/cockpit` (copie intégrée).

## 1. Comment utiliser les documents

Lire ce plan en premier pour savoir quoi faire ensuite. Lire ensuite [PASSATION_CABLAGE_MOTEUR.md](PASSATION_CABLAGE_MOTEUR.md) pour les comportements actuels, les API existantes et les correspondances métier. [REVUE_UX_UI.md](REVUE_UX_UI.md) indique les contrôles déjà effectués et leurs limites.

Le présent plan complète et actualise l’ordre de travail de la passation : il ajoute la finition fonctionnelle du front qui manque avant le raccord des modules concernés. Il ne remplace ni l’inventaire des API ni les protections du moteur.

| Document | Rôle |
|---|---|
| Ce plan | Ordre de réalisation, écrans manquants, critères de fin, prochain travail concret |
| Passation | Cartographie technique et fonctionnelle, mapping Excel, API, protections, UX/UI |
| Revue UX/UI | Vérifications passées, défauts corrigés et essais restant à mener |

La mission à reprendre en priorité est de compléter le prototype local avec des parcours utilisables. Le câblage réel constitue la phase suivante, module par module. Le travail de rédaction de ce plan ne modifie pas l’application et ne branche pas le moteur.

## 2. Ce que signifie « fonctionnel »

Trois niveaux distincts doivent être annoncés honnêtement :

| Niveau | Ce que le client peut faire | Ce qui permet de le déclarer terminé |
|---|---|---|
| Vue disponible | Ouvrir un écran, comprendre son contenu et son rôle | Accès direct, données présentées, navigation et retour fonctionnels |
| Parcours démo complet | Modifier un brouillon, voir des impacts illustratifs, comparer, conserver et valider dans la démo | Une action produit un état cohérent, persistant et vérifiable de bout en bout |
| Module connecté | Réaliser le même parcours avec le dossier réel et les calculs du moteur | Données qualifiées, transactions serveur, résultats traçables et tests d’intégration réussis |

Un nom de feuille affiché dans une pastille n’est pas une vue disponible. Un clic qui ne produit qu’un message « bientôt disponible » n’est pas un parcours complet. Un prototype cliquable avec des chiffres préparés n’est pas un module connecté.

Il n’est pas nécessaire d’attendre la finition des 33 vues pour commencer un raccord en lecture seule ou connecter le premier module complet. En revanche, on ne doit pas annoncer que « tout le site est fonctionnel » tant que des thèmes se terminent dans une impasse.

## 3. État de départ vérifié

Le code du prototype et les documents ont été consultés pour ce plan. Aucun nouveau test navigateur ni test du moteur n’a été exécuté pour cette rédaction ; les résultats de la passation restent des vérifications du 15 septembre.

| Zone | Ce qui existe | Ce qui reste à faire |
|---|---|---|
| Accueil | Situation fictive, contrat prioritaire, navigation | Faire refléter les autres thèmes et les nouvelles décisions dans l’accueil |
| Parcours | Six thèmes, préférences auto/guidé, phases | Donner un espace utilisable aux cinq thèmes autres que Ventes ; supprimer les faux états « À jour » |
| Installation | Société, logo, palette, objectif, documents factices | Conserver les métadonnées de sources et confirmations ; fiabiliser sauvegarde et sorties |
| Ventes | Contrat Atlas, champs, annulation, impacts et comparaison | Ajouter les informations métier manquantes ; relier contrat, feuilles, grille et sources |
| Expert / Grille | Quatre champs Atlas et quelques résultats fictifs | Remplacer les lignes illustratives par une projection identifiée ; distinguer entrées et résultats |
| Expert / Feuilles | 33 noms dans huit groupes | Rendre chaque feuille accessible et lui donner une présentation adaptée |
| Expert / Liens | Chaîne illustrative Atlas | Rendre les destinations navigables et le contexte cohérent avec la feuille choisie |
| Simulations | Atlas et variantes conservées | Sortir du scénario global unique ; ouvrir un scénario précis et préserver sa provenance |
| Graphiques | Points mensuels interactifs, souris/toucher et sélection active | Préserver ces interactions ; aligner les échelles de comparaison, puis utiliser les séries moteur lors du raccord |
| Décisions | Historique local, application et restauration | Relier chaque décision aux entrées, thèmes, simulation et version concernés |
| Suivi mensuel | Nom du fichier, valeurs et écarts préparés | Parcours période → mapping illustratif → confirmation → écarts → décision contextualisée |
| Livrables | Synthèse web ; boutons qui affichent un message | Aperçu navigable, version choisie et états de génération ; export réel lors du raccord |
| Compagnon | Animation, contexte de page, réponses préparées | Expliquer et préparer les actions de tous les thèmes via les mêmes commandes que les écrans |
| Persistance | Un JSON local centré sur Atlas | Identifiants stables, plusieurs objets métier, migration du stockage sans perte |

Les dix routes actuelles doivent rester accessibles. Le front historique `frontend/` et le moteur `tca_bp/` servent de références de lecture pendant la phase de finition du prototype.

## 4. Résultat attendu pour les feuilles

### 4.1 Parcours de consultation

```text
Parcours → thème → liste ou synthèse métier → fiche d’un élément
                          ↕
Expert → groupe → feuille → vue métier / grille détaillée / dépendances
                          ↓
Modification autorisée → brouillon → impacts → simulation → décision
```

Une même donnée doit rester cohérente lorsqu’on passe de sa fiche métier à la grille. Ces deux présentations utilisent le même brouillon ; elles ne conservent pas deux versions indépendantes de la valeur.

Chaque feuille possède :

- un identifiant stable distinct de son nom Excel ;
- un titre compréhensible et le nom Excel en détail secondaire ;
- une phrase expliquant à quoi elle sert ;
- une présentation adaptée au contenu, avec des données fictives explicitement identifiées en mode démo ;
- une période et un contexte : brouillon, simulation ou version officielle ;
- les sources disponibles et le niveau de confirmation ;
- les entrées autorisées, les résultats protégés et les conséquences des modifications ;
- un retour au groupe/thème et des liens vers les éléments dépendants ;
- une action claire pour demander une explication au compagnon.

Le bouton « Voir la grille détaillée » ouvre les lignes/colonnes utiles, avec les mois lorsque la feuille est périodique. Une légende, une liste de contrats et un bilan ne doivent pas être forcés dans le même tableau mensuel générique.

### 4.2 Couverture des 33 feuilles

Cette liste s’appuie sur [le catalogue des feuilles](../feuilles/README.md). Les accès d’écriture réels seront déterminés champ par champ par le catalogue moteur. « Paramètres » ci-dessous n’autorise jamais l’édition libre des formules ou de toute la feuille.

| Feuille réelle | Présentation web proposée | Interaction attendue |
|---|---|---|
| Légende | Aide de lecture, conventions et unités | Consulter et rejoindre les vues concernées |
| Previsionnel | Présentation du dossier et de son horizon | Consulter le périmètre du modèle |
| Control | Calendrier et configuration du dossier | Paramètres autorisés dans un brouillon |
| Assumptions | Hypothèses générales et catalogue des offres | Modifier une hypothèse en montrant sa portée partagée |
| DATA Contrats | Liste de contrats puis fiche détaillée | Préparer les conditions commerciales et les échéances |
| Contrats | Calendrier de chaque contrat | Consulter les calculs et revenir à la fiche source |
| Revenue | Revenu reconnu, facturé et encaissé par mois | Comparer ces trois flux et ouvrir leur origine |
| DATA COGS | Achats et coûts directs par activité | Préparer quantités, prix et calendrier autorisés |
| COGS | Coûts directs et marge par période | Consulter les résultats et rejoindre les entrées |
| Stock | Niveau de stock et politique de stockage | Modifier les paramètres permis, consulter les effets |
| Charges_Externes | Dépenses récurrentes et ponctuelles | Préparer un poste, son montant et son calendrier |
| Effectifs | Équipe et calendrier des recrutements | Préparer les hypothèses de poste et de coût |
| BFR | Délais clients/fournisseurs, stock et besoin d’exploitation | Consulter les résultats et ouvrir les hypothèses sources |
| DATA CAPEX | Liste et fiche des investissements | Préparer montant, date et caractéristiques autorisées |
| CAPEX | Calendrier d’investissements et amortissements | Consulter les résultats |
| Financement Dette | Emprunts et échéanciers | Préparer les conditions autorisées et comparer l’effet |
| DATA Financement | Opérations de financement | Préparer les entrées du registre |
| Financement E&S | Financement en fonds propres et subventions | Consulter et ouvrir seulement les paramètres autorisés |
| SUBVENTION_INVEST | Subventions d’investissement | Préparer les hypothèses et échéances permises |
| CALCUL_CIR | Hypothèses et synthèse du crédit d’impôt | Entrées autorisées séparées des calculs |
| ATELIER_CIR_IS | Atelier fiscal expliqué | Hypothèses et confirmations avant simulation |
| Modèle financier | Vue consolidée des trajectoires | Lecture seule, liens vers les facteurs explicatifs |
| Compte de Résultat | Tableau annuel/mensuel simplifié | Lecture seule, détail des postes et provenance |
| Bilan | Actif, passif et équilibre | Lecture seule, explications des variations |
| Flux de trésorerie | Encaissements, décaissements et solde | Graphique mensuel, tableau et détail des flux |
| Plan de financement | Besoins, ressources et équilibre | Lecture seule et lien vers les financements |
| KPI Dashboard | Indicateurs et période d’analyse | Résultats protégés ; sélecteurs autorisés seulement |
| Contrôles | Contrôles regroupés par statut | Comprendre un blocage et ouvrir l’entrée à corriger |
| Sensi TCA | Hypothèses d’une analyse de sensibilité | Préparer les variations permises |
| Sensi Analyses | Variables testées et résultats comparés | Paramètres de comparaison autorisés |
| Sensi Graphiques | Visualisations des sensibilités | Consulter et ouvrir le scénario concerné |
| Valorisation | Hypothèses et résultats de valeur | Paramètres autorisés séparés du résultat calculé |
| Comparables | Liste des entreprises/opérations comparables | Préparer les données autorisées, lire la synthèse |

Corriger la correspondance interne de l’alias « Sensi Scénarios » vers la feuille réelle `Sensi TCA`, tout en gardant un titre client neutre comme « Sensibilités » pour préserver la marque blanche. L’étiquette actuelle « Feuille Revenue » sur les quatre entrées Atlas doit devenir un intitulé métier exact : les entrées du contrat appartiennent principalement à `DATA Contrats`, tandis que `Revenue` expose des résultats.

Les trois flux reconnu/facturé/encaissé sont une présentation métier proposée, pas l’affirmation qu’une seule série moteur contient déjà ces trois informations. Qualifier la source de chacun avant leur affichage connecté ; ne pas réétiqueter une série de facturation en revenu reconnu.

Il n’est pas demandé de coder 33 applications séparées : partager des composants pour les listes, fiches, séries, tableaux et dépendances, puis les alimenter avec les définitions propres à chaque feuille.

## 5. Routes et accès à prévoir

Les chemins suivants sont une proposition de mise en œuvre locale. Vérifier les routes existantes avant création et préserver les URLs déjà utilisées.

| Destination | Proposition | Règle |
|---|---|---|
| Catalogue des feuilles | `/expert` | Les huit groupes ouvrent réellement leurs feuilles |
| Feuille identifiée | `/expert/feuilles/[sheetId]` | Liens directs, actualisation et retour navigateur fonctionnels |
| Vue de feuille | `?vue=metier`, `grille` ou `liens` | Conserver la feuille et le contexte lors d’un changement de vue |
| Ventes | `/travail/ventes` | Préserver le parcours Atlas actuel |
| Coûts et marge | `/travail/couts` | Relier achats, charges et stock |
| Équipe | `/travail/equipe` | Relier postes et recrutements |
| Investissements et financement | `/travail/investissements` | Relier investissements, dette et fonds propres |
| Trésorerie et fiscalité | `/travail/tresorerie` | Relier délais, flux et hypothèses fiscales |
| Synthèse et valeur | `/travail/synthese` | Relier états financiers, contrôles et valorisation |
| Simulation identifiée | `/simulations/[scenarioId]` | Préserver `/simulations/atlas` comme entrée compatible |

Le moteur ne doit pas recevoir un nom de feuille ou une adresse de cellule fabriqué depuis le libellé visible. Le catalogue relie identifiant de vue, identifiant moteur, champs permis et dépendances.

Pour cette phase locale, conserver une entreprise fictive active. Prévoir néanmoins les identifiants de dossier dans les interfaces internes ; ne pas construire maintenant une gestion multi-entreprise ou une authentification qui n’ont pas été demandées.

## 6. Ordre de réalisation du front

Toutes les cases ci-dessous sont à faire ou à revérifier. Leur présence dans le plan n’indique pas une fonctionnalité livrée.

### F0. Reprendre l’existant et poser un état partagé évolutif

Objectif : prolonger le prototype sans perdre les préférences et scénarios déjà enregistrés.

- [ ] Lire la passation, puis comparer les fichiers réellement présents ; respecter les changements de l’utilisateur.
- [ ] Vérifier les routes actives, les composants de présentation et les données locales ; noter les écarts depuis l’audit.
- [ ] Définir une petite interface commune de lecture et de commande, compatible avec `CockpitGateway` de la passation.
- [ ] Garder une implémentation démo locale et préparer les types de l’implémentation moteur, sans appels réels à ce stade.
- [ ] Introduire des identifiants de feuille, élément métier, brouillon, scénario, version et source.
- [ ] Versionner le stockage et migrer `cockpit-demo:v1` : société, logo, palette, préférences, Atlas, scénarios et historique doivent être préservés.
- [ ] Permettre l’état modifié/incomplet/à simuler par élément ; une nouvelle saisie invalide les résultats qui en dépendent.
- [ ] Retirer dès ce lot les statuts « À jour » des thèmes sans écran ; afficher honnêtement « À compléter » jusqu’à la livraison de leur parcours.

Critère de fin : le parcours Atlas existant fonctionne encore après migration, les données locales survivent à l’actualisation et les nouvelles vues pourront utiliser le même brouillon.

Références : passation §§11, 12, 15 et 16. Ne pas entreprendre une réécriture générale du provider avant d’avoir un premier usage concret.

### F1. Construire un accès réel aux feuilles

Objectif : depuis « Feuilles », ouvrir chacune des 33 vues et comprendre ce qu’elle représente.

- [ ] Créer le catalogue de vues avec les huit groupes et les 33 correspondances de la section 4.
- [ ] Remplacer les étiquettes de feuille par de vrais liens explicitement identifiables.
- [ ] Construire la route de détail et les modes vue métier/grille/dépendances selon le type de feuille.
- [ ] Donner à chaque vue du contenu représentatif propre à son rôle ; ne pas recopier le contrat Atlas dans toutes les feuilles.
- [ ] Ouvrir une entrée source depuis un résultat protégé et revenir à l’endroit d’origine.
- [ ] Gérer identifiant inconnu, état vide et indisponibilité avec un retour utile.
- [ ] Conserver les périodes et le contexte de consultation dans les liens pertinents.

Critère de fin : 33 destinations distinctes accessibles par clic et URL directe ; aucun faux bouton de feuille ; les vues calculées ne proposent pas une modification directe de leurs résultats.

F1 donne une couverture de consultation. Il ne suffit pas, à lui seul, à déclarer les six thèmes fonctionnels.

### F2. Terminer Ventes et contrats de bout en bout

Objectif : livrer le premier module intégralement testable, qui servira ensuite de premier raccord moteur.

- [ ] Relier liste des contrats, fiche Atlas, `DATA Contrats`, calendrier `Contrats` et résultats `Revenue`.
- [ ] Ajouter les informations absentes qui comptent pour le raccord : offre, quantité/prix ou forfait explicite, dates, reconnaissance, facturation, acompte/solde, statut/probabilité et source.
- [ ] Exposer clairement le caractère partagé du délai de paiement de l’offre ; ne pas présenter ce changement comme limité à Atlas.
- [ ] Utiliser « reconnaissance sur quatre mois » comme paramétrage de contrat homologué ; garder les formules calculées protégées.
- [ ] Rendre auto/guidé utilisables sur le même jeu de champs et les mêmes commandes.
- [ ] Faire fonctionner annulation locale, sauvegarde du brouillon et abandon explicite avec confirmation selon la portée.
- [ ] Relier impacts à l’entrée modifiée, à la source et aux vues qui seront touchées.
- [ ] Comparer référence/scénario/variante, modifier les conditions puis recalculer la démo avant toute validation.
- [ ] Conserver et rouvrir un scénario identifié ; appliquer dans la démo, relire la version créée et restaurer un ancien jalon.

Critère de fin : depuis l’accueil, préparer Atlas, ouvrir ses feuilles, modifier une valeur, comprendre les impacts, simuler, conserver, valider puis retrouver/restaurer la version sans impasse. La référence ne change jamais pendant la préparation.

Les résultats de démonstration restent préparés et identifiés comme tels. Ils ne doivent pas devenir une deuxième implémentation du modèle financier en TypeScript. Une combinaison non couverte par une fixture ne doit pas afficher des chiffres sans lien avec les entrées.

Références : passation §§9.4 à 9.7, 13, 17 et 18.

### F3. Donner un parcours complet aux cinq autres thèmes

Objectif : rendre tous les thèmes utilisables avec une décision représentative, des vues adaptées et le même cycle de brouillon.

| Thème | Essai de démonstration à préparer | Vues principales | Conséquences à expliquer |
|---|---|---|---|
| Coûts et marge | Modifier le coût d’achat d’un composant | DATA COGS, COGS, Stock, Charges_Externes | Marge, achats et besoin de trésorerie |
| Équipe | Décaler un recrutement | Effectifs et charges associées | Coût mensuel, résultat et trésorerie |
| Investissements et financement | Décaler un équipement ou modifier son financement | DATA CAPEX, CAPEX, dette, financements | Décaissement, amortissement et remboursement |
| Trésorerie et fiscalité | Modifier une hypothèse de délai autorisée | Assumptions, BFR, flux, atelier fiscal | Calendrier de trésorerie et postes affectés |
| Synthèse et valeur | Comparer deux scénarios et examiner les hypothèses de valeur | États financiers, KPI, contrôles, valorisation, comparables | Résultats et valeur ; états calculés protégés |

Pour chaque thème :

- [ ] ouvrir la route depuis Parcours, puis atteindre les feuilles associées ;
- [ ] conserver le mode auto/guidé après actualisation ;
- [ ] expliquer les entrées, sources et effets ;
- [ ] préparer un brouillon et proposer la prochaine action ;
- [ ] produire un aperçu de démo cohérent avec le cas représentatif ;
- [ ] conserver/comparer/valider une simulation de ce thème, sans la renommer Atlas ;
- [ ] refléter cette décision dans l’accueil, le journal et la version locale concernée ;
- [ ] garder les validations et limites du catalogue visibles.

Critère de fin : six thèmes ont chacun un parcours testable ; aucun n’est déclaré « À jour » simplement parce qu’il n’a pas encore d’écran.

Références : passation §§19, 20 et 24. Une adaptation non homologuée reste une proposition à examiner ; le compagnon ne fabrique pas une nouvelle formule centrale.

### F4. Terminer les parcours transversaux

#### Installation et sources

- [ ] Enregistrer les métadonnées des exemples de documents et les faits confirmés dans l’état démo.
- [ ] Permettre confirmer, corriger et retirer un fait ; répercuter son état sur le brouillon concerné.
- [ ] Garder l’avertissement « document non analysé dans la démo » et ne lire aucun document financier réel.
- [ ] Corriger `Enregistrer et terminer` pour rejoindre la destination initialement demandée.
- [ ] Protéger les changements lors des sorties, y compris l’historique navigateur, sans empêcher le retour normal entre étapes.
- [ ] Aligner les extensions annoncées sur les capacités propres à chaque import : sources documentaires selon la passation §14.3, réalisé CSV/XLSX/XLSM selon §14.7. Ne pas confondre ces deux sélecteurs ; l’ancien XLS demande une conversion distincte.

Critère de fin : les sources fictives restent retrouvables, les confirmations ont un effet et une sortie ne perd pas silencieusement les modifications.

#### Suivi mensuel

- [ ] Choisir une période et un exemple de réalisé.
- [ ] Afficher des colonnes/lignes d’exemple et permettre leur correspondance avec les postes.
- [ ] Présenter l’aperçu puis demander la confirmation.
- [ ] Distinguer réalisé, budget et projection dans les tableaux et graphiques.
- [ ] Ouvrir le thème réellement concerné depuis un écart ; ne pas renvoyer systématiquement vers Atlas.
- [ ] Préparer une nouvelle décision sans remplacer automatiquement la référence.

Critère de fin : import factice → confirmation → écart expliqué → hypothèse contextualisée → simulation est navigable de bout en bout.

#### Livrables

- [ ] Choisir une version officielle et consulter la synthèse qui lui correspond.
- [ ] Ouvrir des aperçus web des formats prévus avec période, version et statut.
- [ ] Prévoir les états en attente/en cours/prêt/échec dans le service de démo et les composants.
- [ ] Nommer clairement les actions disponibles : un aperçu est un aperçu ; un téléchargement doit fournir réellement un fichier d’exemple explicitement identifié, sinon ne pas annoncer un fichier prêt.
- [ ] Réserver la génération des véritables XLSM/PDF/DOCX/PPTX au moteur existant.

Critère de fin : le client peut examiner le contenu et comprendre la version livrée ; aucun bouton de création ne se limite à une fausse notification de succès.

#### Compagnon, décisions et état commun

- [ ] Donner au compagnon le thème, l’élément, la feuille et le scénario courant.
- [ ] Déclencher les mêmes commandes que les boutons ; rendre les réponses préparées pertinentes pour chaque thème.
- [ ] Montrer « préparation », « proposition » et « validation » comme des étapes distinctes.
- [ ] Relier chaque entrée du journal à son scénario et aux vues des données concernées.
- [ ] Conserver les modifications locales, erreurs et tâches en cours lorsqu’on navigue.

Critère de fin : le compagnon reste unique et contextualisé, aucun résultat n’est déclaré appliqué avant la réussite de la commande démo ou moteur correspondante.

### F5. Revue fonctionnelle et visuelle de la version complète

- [ ] Unifier les titres, noms de feuilles, libellés d’actions et statuts à travers les routes.
- [ ] Conserver le style pastel lumineux, le verre local et le compagnon actuel ; ne pas lancer une nouvelle refonte graphique.
- [ ] Corriger les comparaisons de courbes : mêmes périodes et échelle verticale commune, points mensuels souris/toucher/clavier, distinction réalisé/prévision.
- [ ] Vérifier toutes les destinations, retours, ouvertures de sources et liens de dépendance.
- [ ] Vérifier les états vide, incomplet, modifié, en cours, périmé, échec et résultat disponible avec le service de démo.
- [ ] Vérifier mobile, clavier, zoom 200 %, palettes, mouvement réduit et repli sans transparence sur les nouveaux composants.
- [ ] Relancer les contrôles de code adaptés et les parcours complets affectés ; préserver le stockage de l’utilisateur lors des essais.
- [ ] Mettre à jour la matrice d’avancement de la section 11 et la passation avec ce qui est réellement terminé.

Critère de fin : toutes les vues et tous les thèmes sont utilisables dans le périmètre de démonstration annoncé. Les limitations restantes sont nommées précisément. « Front démo complet » n’est pas synonyme de « application financière connectée ».

## 7. Pont entre finition du front et câblage

Ordre recommandé pour livrer d’abord le visuel complet demandé :

```text
F0 : état et commandes communs
  → F1 : accès aux feuilles
  → F2 : parcours Ventes complet
  → F3 : cinq autres thèmes
  → F4 : sources, suivi, livrables et compagnon
  → F5 : revue de l’ensemble
  → C0 à C5 : raccord réel progressif
```

Si la mission de la conversation suivante inclut déjà le raccord, C0 peut commencer après F0 et C1 après F1 en lecture seule ; le premier essai complet C2 sur Atlas commence après F2. F3/F4 peuvent continuer côté démo. Cette option ne doit pas mélanger des valeurs fictives avec un dossier connecté.

Le choix démo/connecté appartient à la configuration et au service utilisé. Une page connectée incomplète montre un état manquant ou une indisponibilité ; elle ne récupère jamais une valeur Atlas comme secours.

## 8. Lots de câblage après les parcours concernés

| Lot | Travail concret | Dépendance | Critère de fin | Renvoi à la passation |
|---|---|---|---|---|
| C0 : lecture du dossier | Gateway moteur, origine locale, santé, dossier, catalogue, jobs | F0 ; dossier de test distinct | La bonne entreprise et la révision s’affichent, sans fixture | §§14 à 16, lot 0 |
| C1 : feuilles et indicateurs | Vraies données des vues, sources, séries et historique | F1 ; métriques qualifiées | Même valeur/unité/période/révision dans toutes ses représentations | §§9, 13, 20, lot 1 |
| C2 : Ventes complet | Contrat sémantique, brouillon, impacts, simulation isolée, adoption, restauration | F2 ; choix métier Atlas | Parcours réel complet avec version officielle inchangée jusqu’à validation | §§13, 15, 17, 18 ; lots 3 à 5 |
| C3 : cinq autres thèmes | Brancher les mêmes commandes sur les registres et paramètres autorisés | F3 ; C2 stabilisé | Chaque thème a un cas réel vérifié et des résultats liés au bon calcul | §§19, 20, 25 |
| C4 : sources, mensuel, livrables | Upload/extraction, mapping, réalisé, prévision actualisée, rapports | F4 ; flux officiels fiables | Pièces sourcées, aperçu confirmé, vrais fichiers liés à une version | §14 ; lots 2, 6 et 7 |
| C5 : compagnon et recette | Conversation réelle, propositions, grille sécurisée, reprise et non-régression | F4/F5 ; commandes précédentes | Boutons et compagnon utilisent la même chaîne contrôlée | §§21 à 24, 27 ; lot 8 |

Réutiliser les API existantes avant d’ajouter des routes. Les adaptateurs Contrat, Impacts, Simulation et Journal ne doivent contenir que les correspondances et l’orchestration absentes ; le calcul reste dans le moteur.

Pour C2, utiliser des sources de test déjà confirmées dans le moteur, ou raccorder le minimum de gestion des sources nécessaire avant la première écriture. Le lot C4 complète l’import/extraction et les autres parcours ; il ne justifie jamais une écriture Atlas sans provenance. Les simulations réelles exigent également un modèle de test et le service de recalcul disponibles.

La création d’une copie de scénario existe déjà ; elle ne simule pas automatiquement le brouillon. Capturer exactement la révision, les opérations, les sources et les empreintes, préparer/appliquer dans la copie isolée puis la recalculer. La référence parent reste inchangée pendant cette simulation, conformément à la passation §17.

Une proposition d’adoption de scénario crée ou remet en cohérence le brouillon parent, puis repasse par aperçu et jeton valide. Si le brouillon d’origine et la référence sont strictement identiques à ceux de la simulation, réutiliser ce chemin contrôlé. Si les empreintes diffèrent, obtenir un nouvel aperçu ; ne jamais recopier les KPI ou écraser la référence avec le fichier du scénario.

Les commandes longues doivent afficher une attente, supporter la navigation, retrouver leur résultat et éviter les doubles écritures. Si l’application a créé une version mais que le recalcul a échoué, cette situation doit apparaître comme telle avec une reprise possible.

## 9. Choix déjà retenus et décisions encore nécessaires

### Déjà retenu pour la prochaine réalisation du front

- Prototype local, interface française et marque blanche personnalisable.
- Aucune publication externe ni authentification à ajouter à cette phase.
- Style iOS pastel et lumineux, effets de verre locaux, absence de grosse barre inférieure.
- Un seul compagnon animé ; modes auto/guidé par thème.
- Le dirigeant valide lui-même l’adoption d’une simulation et peut restaurer un jalon.
- Les résultats/formules centrales restent protégés ; les paramètres autorisés peuvent être préparés dans un brouillon.
- Feuilles présentées en vues métier et grille détaillée facultative.
- Données fictives du prototype ; aucun vrai document financier à analyser dans cette phase.
- Préserver les sources du front historique et le moteur pendant la finition front.

Ne pas redemander ces décisions simplement parce qu’elles figuraient comme questions dans une ancienne version de la passation.

### Choix à régler avant les écritures réelles concernées

| Question | Pourquoi elle compte | Travail possible en attendant |
|---|---|---|
| Délai partagé par offre ou propre au contrat ? | Le moteur actuel porte le délai dans l’offre | Présenter clairement le délai partagé existant ; ne pas inventer de migration |
| Offre Atlas, forfait ou quantité × prix, TVA ? | Le montant seul ne suffit pas pour créer une ligne réelle | Utiliser une offre fictive explicitement décrite en démo |
| Dates exactes et reconnaissance/facturation ? | Détermine les périodes et encaissements | Préparer les champs ; garder la convention de démo explicite |
| Probabilité d’un contrat probable ? | Ne peut pas être confondue avec signé/réalisé | Montrer le champ et l’état à confirmer |
| Définition du revenu, de la marge et de la visibilité ? | Certaines métriques actuelles sont ambiguës ou de mauvaise unité pour la carte | C0, catalogue et lecture des valeurs déjà qualifiées |
| Local à long terme ou futur produit hébergé ? | Affecte stockage, identité et exploitation | Livrer le prototype et le premier raccord local dans le périmètre établi |

Ces décisions ne bloquent pas la finition visuelle et fonctionnelle de la démo. Ne pas arrêter tout le projet pour une question qui ne concerne qu’un futur champ connecté.

## 10. Corrections de documentation à ne pas propager dans le code

- Le composant partagé s’appelle `Surface`, pas `SpatialSurface`.
- Les états actuels de `CompanionBadge` sont `calm`, `awake`, `engaged`.
- L’utilisateur a demandé le caractère simple `-` devant les nombres négatifs. La passation avait inversé ce choix en imposant `−` : conserver la préférence utilisateur et centraliser le formatage. Éviter `—` dans les textes, comme demandé, en utilisant `:` ou des parenthèses.
- Les feuilles calculées et les saisies autorisées doivent être distinguées au niveau des champs. Le catalogue réel peut permettre un sélecteur dans une feuille de synthèse sans autoriser l’écriture de ses résultats.
- « Les 33 feuilles sont listées » décrit l’existant ; cela ne signifie pas qu’elles s’ouvrent ou que leurs parcours sont terminés.
- Les rapports de tests anciens ne prouvent pas les nouvelles routes ni le raccord réel. Consigner les vérifications de chaque lot terminé.

## 11. Matrice d’avancement à tenir pendant la suite

Statuts autorisés : `À faire`, `En cours`, `À vérifier`, `Terminé`. Une preuve de parcours ou de test doit accompagner `Terminé`. Au 16 septembre, les nouveaux lots de ce plan ne sont pas exécutés.

| Lot | Statut initial | Preuve à joindre |
|---|---|---|
| F0 : état partagé et migration | À faire | Reprise d’une session existante et parcours Atlas préservé |
| F1 : 33 feuilles accessibles | À faire | Liste des 33 destinations, accès direct et retour |
| F2 : Ventes complet | À faire | Parcours guidé/auto, grille, impacts, simulation, décision, restauration |
| F3 : cinq autres thèmes | À faire | Un parcours représentatif complet par thème |
| F4 : parcours transversaux | À faire | Sources, suivi mensuel, livrables et compagnon contextualisé |
| F5 : recette front | À faire | Liens, états, responsive, accessibilité et contrôles de code |
| C0 : dossier réel | À faire | Dossier de test lu sans mélange de fixtures |
| C1 : lectures moteur | À faire | Concordance des valeurs entre moteur et vues |
| C2 : Ventes connecté | À faire | Simulation isolée puis nouvelle version avec reçu |
| C3 : autres thèmes connectés | À faire | Un cas réel contrôlé par thème |
| C4 : imports et rapports | À faire | Sources et réalisé confirmés, téléchargements réels |
| C5 : recette complète | À faire | Reprises, conflits, permissions et non-régression UX/UI |

Ne pas mettre tous les lots à `Terminé` à la suite d’un build réussi. La compilation prouve que le code peut être construit ; les essais de parcours prouvent ce que le client peut faire.

## 12. Critères de livraison

### Front prêt pour le raccord du premier module

- [ ] Accès au thème Ventes, à ses fiches et à ses feuilles identifiées.
- [ ] Même donnée dans la fiche et la grille, avec source, unité, période et statut.
- [ ] Brouillon distinct de la référence, annulation et abandon compréhensibles.
- [ ] Impacts et simulation liés aux entrées exactes ; résultat invalidé dès qu’elles changent.
- [ ] Conservation, adoption et restauration traçables dans la démo.
- [ ] Une interface de service remplaçable par l’API sans refaire les écrans.
- [ ] Tous les états d’attente/erreur utiles au module sont présentables.

### Front de démonstration complet

- [ ] Les 33 feuilles s’ouvrent sous une forme adaptée.
- [ ] Les six thèmes disposent d’un parcours représentatif complet.
- [ ] Sources, suivi mensuel, livrables et compagnon sont intégrés au parcours.
- [ ] Les liens directs, retours, actualisations et préférences fonctionnent.
- [ ] Les limitations de démo sont exactes et ne masquent pas des boutons inertes.
- [ ] L’interface reste lisible et utilisable sur ordinateur et téléphone.

### Application réellement câblée

Appliquer les critères de la passation §30 : données réelles identifiées, écritures contrôlées, séries moteur, imports et exports effectifs, compagnon sur les mêmes commandes et aucune fixture sur le chemin connecté.

## 13. Consigne prête à transmettre à l’autre conversation

> Reprends le cockpit dans `frontend/src/cockpit` (copie intégrée). Lis d’abord `PLAN_SUITE_FRONT_ET_CABLAGE.md`, puis `PASSATION_CABLAGE_MOTEUR.md` et `REVUE_UX_UI.md`. La priorité est de terminer les fonctionnalités du front local décrites dans les lots F0 à F5 : accès réel aux 33 feuilles sous des vues métier et des grilles adaptées, parcours Ventes complet, cinq autres thèmes, sources fictives confirmables, suivi mensuel, aperçus des livrables et compagnon contextualisé. Commence par F0, F1 et F2, vérifie ce premier module puis poursuis F3 à F5. Conserve le style iOS pastel premium et les comportements déjà validés. Préserve les données locales existantes et limite les modifications au prototype. Utilise des données de démonstration explicites, sans lire de vrai document financier ni fabriquer un moteur financier dans React. Pour ce premier travail, prépare les interfaces de raccord mais garde le moteur en lecture documentaire ; les lots C0 à C5 constituent la suite du plan. Ne considère pas une feuille listée, une pastille ou un message « bientôt disponible » comme une fonction terminée. Mets à jour la matrice d’avancement avec les preuves de parcours, les points restants et l’adresse locale de prévisualisation.

Si la nouvelle mission demande expressément le raccord en plus du front, appliquer la progression de la section 7 et les lots C0 à C5 sur un dossier moteur de test distinct. Les décisions bloquantes doivent être résolues avant leurs écritures concernées, sans interrompre les travaux indépendants.
