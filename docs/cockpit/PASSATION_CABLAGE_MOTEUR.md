> Archive documentaire de conception du 15–16 septembre 2026, publiée sans chemins personnels. Les états décrits ci-dessous précèdent l’intégration. Voir [le suivi actuel](../INTEGRATION_COCKPIT.md).

# Passation exhaustive : câbler le cockpit web au moteur financier

Date de l’audit : 15 septembre 2026  
Prototype concerné : `visuel web test`  
Moteur existant concerné : projet Python `tca_bp` à la racine du dépôt  
Statut de ce document : constat de l’existant, contrat de raccord recommandé et liste des décisions encore à prendre.

Mise à jour documentaire du 16 septembre 2026 : lire d’abord [PLAN_SUITE_FRONT_ET_CABLAGE.md](PLAN_SUITE_FRONT_ET_CABLAGE.md). Ce nouveau plan détaille les fonctions front encore manquantes et actualise l’ordre de reprise : accès aux feuilles, parcours métier complet, puis raccord progressif des modules. Les lots moteur ci-dessous restent utiles, mais ne doivent plus repousser l’explorateur de feuilles à la fin. Aucun code applicatif n’a été modifié par cette mise à jour.

## 1. But de ce document

Ce document doit permettre à une nouvelle conversation de reprendre le projet sans redécouvrir le fonctionnement de l’interface ni réinventer le moteur.

Il répond à cinq questions :

1. Quels écrans, boutons, états et passages existent dans le nouveau cockpit ?
2. Quelles données sont encore fictives ou uniquement conservées dans le navigateur ?
3. Quelles fonctions existent déjà dans le moteur Python et son API locale ?
4. Comment relier les deux sans perdre les garde-fous métier, l’historique, les sources ni la simplicité de l’interface ?
5. Quels principes UX/UI, composants, microcopies et comportements premium doivent rester inchangés pendant ce raccord ?

Le travail de ce tour est documentaire uniquement. Aucun composant du nouveau cockpit, aucun fichier du front historique et aucun fichier du moteur n’a été modifié pour produire cette passation.

## 2. Résumé exécutable en une page

Le nouveau cockpit est une interface React/TypeScript autonome, visuellement aboutie, mais sa logique financière est encore une démonstration entièrement locale. Il ne contient aucun appel HTTP, ne lit aucun classeur et ne génère aucun livrable réel.

Le dépôt possède déjà, séparément, un moteur opérationnel beaucoup plus riche :

- API FastAPI locale ;
- dossiers et sources ;
- extraction documentaire et OCR local ;
- catalogue de champs et registres métier ;
- brouillon partagé ;
- aperçu contrôlé ;
- application dans une nouvelle copie du XLSM ;
- recalcul Excel séparé ;
- scénarios copiés depuis une révision ;
- versions restaurables ;
- import du réalisé ;
- livrables Excel, PDF, Word et PowerPoint ;
- chat et agents ;
- tâches asynchrones, reprise, idempotence et flux SSE.

La bonne stratégie n’est donc pas de créer un second moteur dans le nouveau front. Il faut :

1. conserver la couche visuelle et les parcours du cockpit ;
2. remplacer progressivement `DemoProvider` par une façade d’application connectée ;
3. réutiliser les API existantes ;
4. ajouter seulement un petit adaptateur « cockpit » pour agréger les réponses et orchestrer la simulation d’un brouillon ;
5. laisser toutes les validations, écritures Excel, versions et décisions officielles au moteur.

Le point métier le plus important découvert pendant l’audit est celui-ci : la démonstration présente « reconnaître la vente sur quatre mois » comme une adaptation de formule. Dans le modèle réel, ce cas doit d’abord être traité par les champs autorisés du registre `DATA Contrats`, notamment `contract_recognition = "Etalee sur la duree"`, avec dates de début et de fin. Il ne faut pas modifier une formule centrale pour obtenir ce comportement.

Deuxième point important : le « délai de paiement » actuel du moteur est porté par l’offre (`offer_payment_days`) et peut donc affecter plusieurs contrats liés à la même offre. L’interface Atlas le présente aujourd’hui comme une condition propre au contrat. Ce choix doit être tranché avant le raccord : soit l’interface avertit que l’hypothèse est partagée, soit le modèle est étendu avec un vrai délai propre au contrat.

Le style visuel n’est pas une couche jetable : la section 24 fixe le contrat UX/UI complet (verre local, pastels, superpositions, navigation, compagnon, graphiques, états asynchrones, microcopies, mobile et accessibilité). Le premier câblage doit changer la provenance des données sans aplatir ni redessiner l’interface.

## 3. Légende utilisée dans la suite

Chaque proposition est qualifiée avec l’un des statuts suivants :

- **EXISTANT COCKPIT** : comportement réellement présent dans `visuel web test`.
- **EXISTANT MOTEUR** : service ou protection réellement présent dans `tca_bp`.
- **ADAPTATEUR À CRÉER** : petite couche nécessaire entre les deux, sans dupliquer les calculs.
- **DÉCISION À PRENDRE** : arbitrage métier ou technique qui ne doit pas être inventé pendant le développement.
- **DÉMO UNIQUEMENT** : valeur ou comportement à ne jamais présenter comme un résultat financier réel.

## 4. Vocabulaire à figer avant tout raccord

Ces objets ne sont pas interchangeables :

| Terme | Définition à conserver |
|---|---|
| Référence officielle | Version actuellement adoptée du dossier financier. Elle est immuable ; une adoption ou une restauration crée une nouvelle version. |
| Brouillon | Lot d’entrées ou d’opérations préparées, encore non appliqué à la référence. |
| Aperçu | Comparaison contrôlée avant/après du brouillon, liée à une révision et à un jeton d’approbation. |
| Simulation | Calcul effectué sur une copie isolée à partir d’une référence et d’un brouillon précis. |
| Scénario conservé | Simulation ou copie nommée gardée pour comparaison future. Ce n’est pas une décision officielle. |
| Décision | Validation humaine traçable qui conduit éventuellement à une nouvelle référence. |
| Source | Pièce ou réponse enregistrée dans le dossier, avec identifiant et empreinte. |
| Réalisé | Données comptables validées pour une période passée. |
| Prévision actualisée | Réalisé pour le passé + hypothèses courantes pour le futur, après raccord et recalcul. |
| Signé | Engagement commercial certain, qui peut ne pas être livré, facturé ou encaissé. |
| Probable | Opportunité ou contrat pondéré ; même à 100 %, elle ne devient pas automatiquement du réalisé. |
| Revenu reconnu | Activité reconnue selon la prestation/livraison. |
| Facturé | Créance émise selon un échéancier de facturation. |
| Encaissé | Mouvement de trésorerie réellement reçu. |

Invariant de langage : signé, probable, livré, revenu reconnu, facturé, encaissé et réalisé doivent rester sept notions distinctes dans les données, les API et l’interface.

## 5. Topologie actuelle du dépôt

### 5.1 Nouveau cockpit

Répertoire : `visuel web test`.

- `app/` : dix routes du cockpit.
- `components/cockpit/` : shell, compagnon, volet d’impacts, provider et composants de présentation.
- `lib/demo.ts` : données, types, contrôles, impacts et calcul fictifs.
- `tests/demo-state.test.mjs` : tests des transitions locales.
- `REVUE_UX_UI.md` : revue visuelle et de parcours déjà réalisée.

Technologies actuelles : React 19, TypeScript, Vinext/Vite, Base UI, composants shadcn et Tailwind.

Prévisualisation locale habituelle : `http://localhost:3000/`. Depuis `visuel web test`, utiliser `OUVRIR-LE-PROTOTYPE.cmd` ou `pnpm dev`. Le prototype n’est pas publié et ne doit pas dépendre d’un hébergement externe.

### 5.2 Front historique

Répertoire : `frontend`.

Il contient déjà un client de l’API moteur, un atelier tableur et des écrans fonctionnels. Il reste une source de vérité utile pour les contrats HTTP et les protections, mais ses composants visuels ne doivent pas être importés dans le nouveau cockpit.

Fichiers particulièrement utiles :

- `frontend/src/api.ts` : erreurs, appels `/api`, identifiants de demande et reprise d’intention ;
- `frontend/src/types.ts` : types généraux dossier, feuille, cellule, brouillon, tâche et version ;
- `frontend/src/workshopTypes.ts` : profil, questions, faits, scénarios, séries et réalisés ;
- `frontend/src/App.tsx` : SSE, polling de secours, brouillon, versions et chat ;
- `frontend/src/Workshop.tsx` : profil, sources, registres, scénarios, réalisé et livrables.

### 5.3 Moteur et API

Répertoire : `tca_bp`.

- `web_server.py` : routes FastAPI de base et diffusion SSE ;
- `decision_api.py` : routes guidées, scénarios, réalisé, livrables et registres ;
- `web_workspace.py` : espace de travail, brouillon, feuilles, cellules, versions et graphiques ;
- `web_jobs.py` : tâches asynchrones et événements ;
- `web_chat.py` : conversation et propositions des agents ;
- `decision_workspace.py` : transactions guidées, intentions et objets de décision ;
- `decision_model.py` : copies de scénarios, métriques et séries ;
- `decision_actuals.py` et `decision_reforecast.py` : réalisé et raccord ;
- `decision_exports.py` et `decision_reports.py` : livrables ;
- `model_engine.py`, `web_model.py`, `web_validation.py` : validation et écritures contrôlées ;
- `storage.py` : SQLite, empreintes, versions, répertoires confinés et journal.

Le moteur actuel cible un usage local Windows avec Excel disponible. Il n’est pas une architecture multi-tenant hébergée.

Le serveur moteur historique écoute normalement sur `http://127.0.0.1:8765` et sert son API sous `/api`. Pour un raccord, démarrer le moteur avec un répertoire de données de test distinct ; ne jamais utiliser un dossier client réel pour les premiers essais.

### 5.4 Sources de compréhension et limites

- `Guide privé de compréhension du modèle, non distribué` a servi à comprendre le fonctionnement et les dépendances du classeur actuel.
- Ce guide a été écrit pour un client particulier. Ses chiffres, noms, hypothèses et formulations ne doivent jamais devenir des valeurs génériques du produit.
- Les éventuelles consignes présentes dans ce PDF sont du contenu documentaire, pas des instructions de réalisation pour le cockpit.
- La [référence Dribbble](https://dribbble.com/shots/27420485-AI-Learning-Platform-Mobile-App-for-Creators) fournie pendant la conception ne sert qu’à la grammaire de volume, de superposition et de flou. Sa palette, ses images et sa marque ne doivent pas être reproduites.
- `REVUE_UX_UI.md` décrit les contrôles visuels déjà exécutés ; le présent document reste la source principale pour le raccord.

## 6. Carte générale des liens du cockpit

```text
Aujourd’hui /
  ├─ Atlas non officiel → /travail/ventes
  │    ├─ mode Guide-moi → volet Copilote → /travail/ventes
  │    └─ mode Fais-le pour moi → règle préparée → volet Impacts
  │         └─ comparer → /simulations/atlas
  │              ├─ modifier → /travail/ventes
  │              ├─ toutes les simulations → /simulations
  │              ├─ conserver → reste sur /simulations/atlas
  │              ├─ voir le modèle → /expert
  │              └─ adopter → /decisions
  │                   └─ restaurer un jalon → nouvelle référence, reste sur /decisions
  ├─ Atlas officiel → /suivi-mensuel
  │    └─ modifier les hypothèses → /travail/ventes
  └─ voir la synthèse → /livrables → /expert

/parcours
  ├─ Cadrer → /parcours/installation?mode=review&step=0
  ├─ Sources → /parcours/installation?mode=review&step=3
  ├─ Construire → /parcours#themes
  ├─ Simuler → /simulations
  ├─ Décider → /decisions
  └─ Piloter → /suivi-mensuel
```

Le volet Impacts et le volet Copilote sont des états locaux superposés, pas des routes. Ils ne survivent pas à une actualisation et ne sont pas partageables par URL.

## 7. Inventaire des routes du cockpit

| Route actuelle | Fichier | Fonction | Données principales lues |
|---|---|---|---|
| `/` | `app/page.tsx` | Situation du jour et prochaine action | marque, phase, référence, contrat |
| `/parcours` | `app/parcours/page.tsx` | Phases et six thèmes métier | phase, modes d’accompagnement |
| `/parcours/installation?mode=review&step=0..4` | `app/parcours/installation/page.tsx` | Profil, marque, objectif, sources et confirmation | marque, objectif |
| `/travail/ventes` | `app/travail/ventes/page.tsx` | Brouillon du contrat Atlas | contrat, undo, règle, mode ventes |
| `/simulations` | `app/simulations/page.tsx` | Scénario actif et variantes conservées | brouillon, résultat, variantes, référence |
| `/simulations/atlas` | `app/simulations/atlas/page.tsx` | Comparaison référence/scénario/recommandation | résultat, référence, règle, contrat |
| `/decisions` | `app/decisions/page.tsx` | Référence active, journal et restaurations | versions et décisions |
| `/suivi-mensuel` | `app/suivi-mensuel/page.tsx` | Import fictif et écarts mensuels | état mensuel |
| `/livrables` | `app/livrables/page.tsx` | Synthèse web et faux boutons d’export | référence officielle |
| `/expert` | `app/expert/page.tsx` | Grille métier, groupes de feuilles et dépendances | brouillon, règle, référence |

Limite actuelle : aucune route ne contient de `caseId`, `contractId`, `scenarioId`, `referenceId` ou `periodId`. Atlas et Luméo sont codés en dur.

**DÉCISION À PRENDRE** :

- installation strictement mono-entreprise : conserver les URLs lisibles et mettre le `caseId` actif dans le contexte connecté ;
- plusieurs dossiers ou liens partageables : préférer `/dossiers/{caseId}/...`, puis `/travail/contrats/{recordId}` et `/simulations/{scenarioId}`.

Ne pas cacher un choix multi-dossier dans un simple `localStorage` si des liens profonds doivent être fiables.

## 8. Navigation globale et composants transversaux

Source : `components/cockpit/app-shell.tsx`.

| Élément | Lien ou effet actuel | Effet moteur futur |
|---|---|---|
| Logo/nom | `/` | aucun ; marque alimentée depuis le profil |
| Aujourd’hui | `/` | charger la synthèse de la référence active |
| Parcours | `/parcours` | charger progression et disponibilités |
| Simulations | `/simulations` | charger scénarios et simulation courante |
| Décisions | `/decisions` | charger versions et journal |
| Suivi mensuel | `/suivi-mensuel` | charger le dernier arrêté |
| Livrables | `/livrables` | charger rapports de la révision active |
| Mode expert | `/expert` | charger catalogue et projection protégée |
| Personnaliser | `/parcours/installation?mode=review` | charger profil et préférences |
| Carte Version officielle | `/decisions` | afficher révision et version actives |
| Compagnon flottant | ouvre le Copilote, sauf sur `/` | ouvrir la conversation dans le contexte courant |
| Notification | se ferme localement | aucune écriture métier |
| Réinitialiser la démo | remplace le JSON local | à supprimer du produit ou garder sous un drapeau de démo |

À chaque changement de route, le shell :

- remet le défilement en haut ;
- déplace le focus vers le contenu principal ;
- adapte le titre du document ;
- joue une transition visuelle, sauf si les animations sont réduites.

Ces comportements doivent rester purement front.

## 9. Contrat détaillé de chaque écran

### 9.1 Aujourd’hui `/`

**EXISTANT COCKPIT**

- Affiche la phase, la référence officielle, le point bas, la visibilité, une alerte et le contrat prioritaire.
- `Préparer le contrat Atlas` va vers `/travail/ventes` si Atlas n’est pas officiel.
- `Préparer le suivi mensuel` va vers `/suivi-mensuel` si Atlas est officiel.
- La bulle compagnon ouvre le Copilote.
- `Voir la synthèse` va vers `/livrables`.
- La courbe est consultable à la souris, au doigt et au clavier.

**RACCORDEMENT**

L’écran doit recevoir un modèle de lecture agrégé comprenant : dossier actif, référence active, fraîcheur du calcul, indicateurs qualifiés, séries de trésorerie, alertes, sujets prioritaires et prochaine action. La phase et la disponibilité des actions doivent être calculées à partir du workflow serveur, pas seulement d’un texte local.

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}` ;
- `GET /api/cases/{case_id}/workshop` ;
- `GET /api/cases/{case_id}/scenarios/compare` pour métriques et séries ;
- `GET /api/cases/{case_id}/jobs` pour l’activité en cours.

**ADAPTATEUR À CRÉER**

Un `GET /api/cases/{case_id}/cockpit` peut agréger ces informations et produire les alertes/priorités sans faire porter cette composition à chaque page.

### 9.2 Parcours `/parcours`

**EXISTANT COCKPIT**

- `Modifier mes informations` ouvre l’installation en révision.
- Les phases antérieures et la phase courante sont cliquables ; les suivantes ne le sont pas.
- Chaque thème mémorise `Guide-moi` ou `Fais-le pour moi`.
- `Continuer sur ce thème` existe seulement pour Ventes et contrats.
- Les cinq autres thèmes sont encore des cartes sans espace de travail.
- La légende des six états de contrôle est statique.

**RACCORDEMENT**

- Profil et questionnaire peuvent déterminer Cadrer/Sources/Construire.
- Brouillon et contrôles peuvent déterminer Simuler.
- Simulation fraîche et valide peut déterminer Décider.
- Réalisé validé peut déterminer Piloter.
- Les préférences d’accompagnement sont des préférences d’utilisateur, pas des données financières.

**DÉCISION À PRENDRE**

Définir une règle de progression exacte. Une phase ne doit pas devenir « terminée » uniquement parce que l’utilisateur a visité une page.

### 9.3 Installation `/parcours/installation`

**EXISTANT COCKPIT**

- Étape 0 Entreprise : nom de société et prénom.
- Étape 1 Identité : logo local, redimensionnement, trois palettes et retrait.
- Étape 2 Objectif : trésorerie, croissance ou financeurs.
- Étape 3 Sources : exemples fictifs ou sélection de fichiers ; seuls les noms existent dans un `useState` de la page. Ils ne rejoignent ni `DemoState` ni `localStorage` et disparaissent à la sortie ou à l’actualisation.
- Étape 4 Confirmation : faits entièrement codés en dur.
- Le numéro d’étape est dans l’URL ; précédent/suivant du navigateur fonctionne.
- Un clic sur un lien interne avec changements ouvre `Rester ici`, `Quitter sans garder` ou `Enregistrer et terminer`. La fermeture/actualisation utilise `beforeunload`, mais le bouton Précédent/Suivant du navigateur n’est pas intercepté par cette modale : c’est un écart à corriger.
- `Enregistrer et terminer` appelle actuellement `finish()` et renvoie toujours vers `/parcours` en révision ou `/` en première installation ; il n’honore pas la destination initialement cliquée.
- En mode révision, la phase financière est conservée.

**EXISTANT MOTEUR RÉUTILISABLE**

- `POST /api/cases` pour créer le dossier ;
- `GET|PUT /api/cases/{case_id}/profile` ;
- `POST /api/cases/{case_id}/profile/propose` pour proposer le calendrier au brouillon ;
- `GET /api/cases/{case_id}/questionnaire` ;
- `POST /api/cases/{case_id}/sources` pour une réponse ;
- `POST /api/cases/{case_id}/sources/upload` pour une pièce ;
- `POST /api/cases/{case_id}/extractions` puis lecture de l’extraction ;
- `POST /api/cases/{case_id}/extractions/{id}/propose` pour envoyer des faits contrôlés au brouillon.

**ADAPTATEUR À CRÉER**

- Persistance du logo, de la palette, du prénom et des modes d’accompagnement, qui ne font pas encore partie du profil moteur.
- Une vue simplifiée des faits extraits avec leurs sources, localisation, confiance et état de confirmation.
- Un état d’onboarding serveur si le produit doit reprendre sur un autre appareil.

Le logo ne doit pas être stocké dans l’état financier. En local, il peut rester un asset du profil ; en mode hébergé, il doit devenir un objet identifié plutôt qu’une longue data URL.

### 9.4 Ventes et contrats `/travail/ventes`

**EXISTANT COCKPIT**

- `Voir le parcours` revient vers `/parcours`.
- `Annuler mon dernier changement` restaure un instantané local et invalide le résultat simulé.
- Le mode guidé ouvre le compagnon ; le mode automatique prépare la règle puis ouvre Impacts.
- Sur grand écran, le client, le montant, le mois de départ, la durée, l’acompte et le délai sont modifiables.
- Sur téléphone, les valeurs complexes sont en lecture seule.
- Toute modification remet le scénario en brouillon et efface le résultat précédent.
- Le statut probable/signé est affiché mais pas modifiable.
- `discardDraft()` existe dans le provider, mais aucun bouton visible ne l’appelle.

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}/registers` ;
- `POST /api/cases/{case_id}/registers/{sheet}/records` ;
- `POST /api/cases/{case_id}/draft/operations` ;
- `GET /api/cases/{case_id}/draft` ;
- `DELETE /api/cases/{case_id}/draft` ;
- sources obligatoires et validation par le catalogue du modèle.

**RACCORDEMENT**

La carte Atlas doit devenir une vue métier d’un enregistrement du registre `DATA Contrats`. Elle ne doit jamais écrire directement une adresse Excel choisie par le front. Le front envoie des identifiants de champs ; le moteur choisit et contrôle la ligne.

L’annulation locale peut rester disponible avant envoi. Après envoi au brouillon partagé, un vrai undo exige soit un historique d’opérations serveur, soit le retrait/recréation explicite du lot. Ne pas faire croire qu’une référence officielle a été annulée quand seul le brouillon a changé.

### 9.5 Simulations `/simulations`

**EXISTANT COCKPIT**

L’action principale dépend de l’état :

- `applied` : tester d’autres conditions dans `/travail/ventes` ;
- `draft` + règle prête : ouvrir Impacts ;
- `draft` non préparé : aller vers `/travail/ventes` ;
- `simulated` ou `saved` : ouvrir `/simulations/atlas`.

Cliquer une variante conservée recopie aujourd’hui ses entrées et métriques dans l’état global puis ouvre la comparaison.

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}/scenarios` ;
- `POST /api/cases/{case_id}/scenarios` crée une copie nommée depuis une révision ;
- `GET /api/cases/{case_id}/scenarios/compare` renvoie référence et scénarios avec métriques et séries.

**RACCORDEMENT**

Une carte conservée doit référencer son `scenario.id` et son `scenario.case_id`. Elle ne doit pas copier une ancienne métrique dans un état global sans vérifier la fraîcheur de la copie et son statut de recalcul.

### 9.6 Comparaison Atlas `/simulations/atlas`

**EXISTANT COCKPIT**

- Sans simulation fraîche : `Reprendre mon brouillon`.
- `Toutes les simulations` revient à `/simulations`.
- `Retour au brouillon` revient à `/travail/ventes`.
- Trois colonnes : référence, scénario courant, piste 40 % / 30 jours / 4 mois.
- `Utiliser ces conditions` remplace le brouillon par cette piste et relance le faux calcul.
- `Garder une copie pour plus tard` crée une variante locale sans toucher la référence.
- `Voir dans le modèle` ouvre `/expert`.
- `Choisir comme version officielle` ouvre une confirmation.
- La confirmation crée aujourd’hui une référence locale puis navigue immédiatement vers `/decisions`.
- Une fois appliqué, `Voir le journal des décisions` ouvre également `/decisions`.

**EXISTANT MOTEUR RÉUTILISABLE**

- copies de scénarios ;
- brouillon, aperçu, application, recalcul ;
- métriques `revenue`, `gross_margin`, `cash_min`, `cash_break_date`, `financing_need` ;
- séries mensuelles `cash`, `revenue`, `receipts`, `payments` ;
- tâches et événements.

**ADAPTATEUR À CRÉER : ORCHESTRATION DE SIMULATION**

L’API actuelle sait créer une copie de scénario, mais elle ne possède pas un appel unique « simuler ce brouillon de la référence sans l’appliquer ». Le flux recommandé est détaillé à la section 17.

Après raccord, ne naviguer vers `/decisions` qu’après une réponse serveur confirmant la nouvelle révision. En cas de conflit, de résultat périmé ou d’échec Excel, rester sur la comparaison et expliquer l’étape à reprendre.

### 9.7 Décisions `/decisions`

**EXISTANT COCKPIT**

- `Tester une décision` ouvre `/simulations`.
- La première version du tableau local est considérée comme la référence active.
- Le journal est en lecture seule.
- Chaque ancienne version peut être restaurée après confirmation.
- Restaurer crée une nouvelle référence et conserve tout l’historique.

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}/versions` ;
- `POST /api/cases/{case_id}/versions/{version_id}/restore` ;
- historique du stockage et reçus de travail.

**ADAPTATEUR À CRÉER**

Une vue de journal métier doit relier version, auteur, motif, scénario, impacts acceptés, sources et résultat du recalcul. Les événements techniques seuls ne suffisent pas à raconter la décision au dirigeant.

Une restauration moteur est une tâche asynchrone. L’interface doit afficher l’état, attendre le succès, recharger la référence et seulement ensuite annoncer que la restauration est terminée.

### 9.8 Suivi mensuel `/suivi-mensuel`

**EXISTANT COCKPIT**

- Avant import : sélecteur Excel/CSV ou exemple fictif.
- Le vrai fichier n’est pas lu ; seul son nom est mémorisé.
- Après import : écarts et courbe sont statiques.
- `Remplacer le fichier` ouvre le sélecteur.
- `Modifier les hypothèses` renvoie vers `/travail/ventes`.

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}/actuals` ;
- `POST /api/cases/{case_id}/actuals/import` ;
- mapping de colonnes, de postes, de locale numérique et d’encodage ;
- `POST /api/cases/{case_id}/actuals` pour une saisie manuelle ;
- `POST /api/cases/{case_id}/actuals/apply` avec jeton d’approbation ;
- `GET /api/cases/{case_id}/actuals/bridge/questions` ;
- `POST /api/cases/{case_id}/actuals/reforecast` ;
- séries de prévision actualisée et comparaisons.

**RACCORDEMENT**

Le bel écran actuel peut rester simple, mais le flux réel doit comporter au moins : arrêté, lecture, mapping, aperçu, confirmation, écarts, raccord, recalcul et nouvelle décision éventuelle. Le contenu d’un fichier ne doit jamais être adopté au premier clic.

### 9.9 Livrables `/livrables`

**EXISTANT COCKPIT**

- Synthèse web à partir de la fausse référence.
- `Ouvrir le détail expert` va vers `/expert`.
- Boutons Excel, PDF et Présentation : simple notification « non connecté ».

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}/reports` ;
- `POST /api/cases/{case_id}/reports` ;
- `GET /api/cases/{case_id}/reports/{report_id}/{format}` ;
- formats déjà prévus : XLSM, PDF, DOCX, PPTX et snapshot JSON ;
- `GET /api/cases/{case_id}/download` pour le classeur courant ;
- `POST /api/cases/{case_id}/roundtrip` pour reprendre les modifications autorisées d’un export.

**RACCORDEMENT**

Un bouton doit créer un job, afficher sa progression, signaler les diagnostics et ne proposer le téléchargement qu’après succès. Chaque jeu de livrables doit rester lié à une révision et au même instantané de chiffres.

### 9.10 Mode expert `/expert`

**EXISTANT COCKPIT**

- Onglets locaux Grille, Feuilles et Liens.
- Montant, durée, acompte et délai modifiables sur grand écran.
- Les résultats sont ceux de la référence et restent en lecture seule.
- `Adapter avec le copilote` ouvre le compagnon.
- La formule affichée est schématique ; aucune formule Excel réelle n’est lue.
- Sur mobile, la grille est en lecture seule.

**EXISTANT MOTEUR RÉUTILISABLE**

- `GET /api/cases/{case_id}/sheets` ;
- `GET /api/cases/{case_id}/cells` ;
- `GET /api/cases/{case_id}/agents` ;
- `POST /api/cases/{case_id}/draft/operations` ;
- catalogue sémantique des champs, permissions et politiques d’écriture ;
- formules et cellules centrales protégées par le moteur.

**RACCORDEMENT**

La grille expert doit consommer une projection filtrée. Une cellule centrale ne doit pas seulement être désactivée dans l’interface : aucune commande publique ne doit permettre de l’écrire. Les entrées autorisées doivent être identifiées par le catalogue, jamais par une liste d’adresses copiée dans React.

## 10. Volets et modales transversaux

### 10.1 Volet Impacts

Source : `components/cockpit/impact-sheet.tsx`.

Actuellement, il affiche quatre impacts générés localement, les contrôles, la règle française, une formule schématique et les feuilles touchées.

- Si tous les contrôles passent : `Comparer à la version officielle` appelle le faux calcul puis ouvre `/simulations/atlas`.
- Sinon : retour vers `/travail/ventes` pour préparer ou corriger.

Le futur volet doit être lié à un triplet immuable :

```text
case_id + base_revision + draft_fingerprint
```

La simulation doit recevoir exactement le même triplet. Si le brouillon change après lecture des impacts, le volet et la simulation deviennent périmés.

Le contrat d’affichage utile à conserver comprend :

- ce qui change ;
- effet direct ;
- effets en chaîne ;
- éléments inchangés ;
- horizon et périodes ;
- valeur avant/après et unité ;
- source et niveau de confirmation ;
- feuilles, champs ou entités touchés ;
- contrôles et fraîcheur ;
- lien vers la preuve ou l’entrée, si autorisé.

### 10.2 Volet Copilote

Source : `components/cockpit/copilot-sheet.tsx`.

Actuellement, le compagnon répond par quelques mots-clés et peut :

- passer Ventes en mode guidé ;
- passer Ventes en mode automatique ;
- préparer localement la règle ;
- ouvrir Impacts.

Le moteur possède déjà :

- `GET /api/cases/{case_id}/chat` ;
- `POST /api/cases/{case_id}/chat` ;
- sélection de feuille/plage/multi-feuilles ;
- agents de feuille ;
- propositions qui rejoignent le brouillon ;
- job asynchrone et événements `chat`.

Le compagnon du cockpit doit utiliser les mêmes commandes que les boutons. Il ne doit jamais disposer d’un chemin d’écriture parallèle. Une réponse doit distinguer : texte, explication, proposition, aperçu, demande de confirmation, exécution, résultat et erreur.

### 10.3 Confirmations

Quatre confirmations existent :

1. réinitialisation de la démo ;
2. sortie de l’installation avec changements ;
3. adoption d’un scénario ;
4. restauration d’une version.

Après raccord, une modale n’est pas une transaction. Le clic de confirmation déclenche la commande ; l’interface reste en attente jusqu’au reçu serveur.

## 11. État local actuel

Source : `lib/demo.ts` et `components/cockpit/demo-provider.tsx`.

Le JSON complet est enregistré dans `window.localStorage` sous la clé `cockpit-demo:v1` après hydratation.

| Champ de `DemoState` | Usage actuel | Destination réelle |
|---|---|---|
| `schemaVersion` | migration du JSON local | version des contrats d’API/cache |
| `brand` | société, prénom, logo, palette | profil société/utilisateur |
| `objective` | objectif d’installation | mandat ou profil |
| `phase` | phase globale | workflow dérivé côté serveur |
| `themeModes` | auto/guidé par thème | préférence utilisateur |
| `contract` | unique brouillon Atlas | registre métier + brouillon |
| `contractUndo` | 12 instantanés locaux | historique de saisie locale ou révisions de brouillon |
| `scenarioStatus` | état global Atlas | état par simulation/scénario |
| `simulatedMetrics` | résultat fictif courant | résultat versionné d’un run |
| `savedVariants` | copies locales | scénarios serveur |
| `rule` | unique règle locale | champs/règles homologués du modèle |
| `referenceMetrics` | faux résultats officiels | métriques de la révision active |
| `referenceIncludesAtlas` | booléen manuel | à supprimer, dériver du registre de la version |
| `referenceVersions` | historique local | versions moteur |
| `decisions` | journal local | journal métier/audit |
| `chatMessages` | 24 messages max | conversation serveur |
| `monthly` | booléen + nom de fichier | import, actuals et reforecast |
| `onboardingCompleted` | indicateur non lu par les pages | workflow/profil |

### 11.1 Correspondance des actions du provider

| Action actuelle | Effet dans la démonstration | Remplacement connecté |
|---|---|---|
| `setThemeMode` | mémorise automatique/guidé et ajoute un message | préférence utilisateur, sans écriture financière |
| `updateContract` | crée un undo, modifie Atlas, invalide résultat et statut | saisie locale puis commande contrat avec révision attendue |
| `undoContract` | restaure le dernier instantané local | undo local avant envoi ou nouvelle révision explicite du brouillon serveur |
| `discardDraft` | recopie le contrat de la référence active | `DELETE /draft` puis relecture de la référence ; confirmation visible |
| `stageRevenueRule` | force durée 4 mois et reconnaissance étalée | recette homologuée produisant des champs `contract_*`, pas une formule front |
| `simulate` | valide puis appelle `calculateScenario()` | job `scenarios/from-draft`, résultat lié au fingerprint |
| `saveScenario` | copie entrées et métriques dans `savedVariants` | conserver/nommer le scénario moteur déjà recalculé |
| `loadSavedVariant` | recopie entrées et anciennes métriques sans contrôle de fraîcheur | créer un nouveau brouillon depuis les entrées du scénario, puis recalcul obligatoire si base différente |
| `applyScenario` | copie les KPI simulés dans la référence locale | adoption vers brouillon parent, aperçu, jeton, application, version et recalcul |
| `restoreVersion` | copie un ancien instantané et crée une nouvelle référence locale | job `/versions/{version_id}/restore`, puis relecture du reçu et du calcul |
| `setBrand` | fusionne société, prénom, logo et palette | profil visuel utilisateur/entreprise séparé de la finance |
| `addChat` | conserve au plus 24 messages locaux | thread serveur, job conversation et événements `chat` |
| `importMonthly` | conserve seulement le nom du fichier | upload, mapping, aperçu, validation, actuals et reforecast |
| `completeOnboarding` | pose un booléen actuellement non consommé | état de workflow reprenable ou progression dérivée |
| `resetDemo` | remplace toutes les fixtures | disponible uniquement lorsque `DemoCockpitGateway` est actif |

Dans l’état actuel, `updateContract()` groupe les changements du même champ sur une courte fenêtre pour n’en faire qu’une annulation et conserve douze instantanés maximum. `saveScenario()` déduplique par sérialisation JSON et `applyScenario()` compare également des objets sérialisés. Ces comparaisons doivent devenir des identifiants, révisions et empreintes canoniques côté moteur.

Doivent rester locaux : ouverture des volets, notification, focus, saisie non validée, index de carrousel et mois survolé dans un graphique.

Ne doivent plus rester la source de vérité locale : brouillon partagé, résultats, scénarios, versions, décisions, sources, réalisé et livrables.

## 12. Ce qui est fictif et doit disparaître du chemin de production

### 12.1 Calcul

`calculateScenario()` dans `lib/demo.ts` utilise des coefficients arbitraires. Il ne réalise ni comptabilité, ni BFR, ni calendrier, ni TVA, ni coût direct réel. `customer`, `startMonth` et `commercialStatus` n’influencent même pas le résultat.

Cette fonction doit être remplacée, pas perfectionnée.

Fixtures initiales à reconnaître pour éviter de les prendre pour une réponse moteur : référence à 2,4 M€ de chiffre d’affaires, 46 % de marge, point bas 118 k€ et visibilité 11 mois ; contrat Atlas Mobility de 480 k€, 4 mois, 20 % d’acompte, 60 jours, octobre 2026, probable et revenu initialement reconnu en une fois.

Le faux calcul utilise un facteur de revenu de 79 % si étalé sinon 72 %, un gain d’acompte de `max(0, acompte − 20) × 3 800`, une pénalité de délai de `max(0, délai − 30) × 2 050`, un gain de durée de `max(0, 4 − mois) × 8 000`, puis borne arbitrairement le point bas à 18 k€. Ces nombres restent uniquement des fixtures de démonstration et ne doivent être ni déplacés vers l’API ni utilisés comme tests de vérité financière.

### 12.2 Courbes

Les courbes utilisent plusieurs séries codées en dur :

- `DEFAULT_CASH_CURVE_POINTS` et `IMPROVED_CASH_CURVE_POINTS` dans `components/cockpit/page-elements.tsx` ;
- `cashEvolution` construit depuis dix offsets fixes dans `app/simulations/page.tsx` ;
- `monthlyCashPoints` dans `app/suivi-mensuel/page.tsx` ;
- les colonnes de comparaison Atlas réemploient les templates de `CashCurve` en les décalant.

Quand un point bas est fourni au template, la forme est simplement déplacée verticalement. Le composant interactif peut être conservé ; toutes ses séries et tous ses points doivent venir du moteur en mode connecté.

### 12.3 Impacts et contrôles

Les quatre impacts sont statiques. Le contrôle « moteur central inchangé » vaut toujours vrai. Le contrôle d’un contrat signé à 480 k€ est spécifique à Atlas.

### 12.4 Import et livrables

Les fichiers d’installation et mensuels ne sont pas lus. Les livrables ne sont pas générés. Les dates `Aujourd’hui` et `À l’instant`, les identifiants `Date.now()` et les comparaisons par `JSON.stringify` ne sont pas des mécanismes métier acceptables.

Le suivi mensuel fictif montre notamment juillet 2026 à 200 k€, août à 55 k€, septembre projeté à 100 k€, octobre projeté à 172 k€, puis des écarts « encaissements −45 k€ », « achats +18 k€ » et « trésorerie −63 k€ ». Ces valeurs servent seulement à reconnaître les fixtures dans le code et doivent disparaître entièrement du mode connecté.

L’installation propose deux noms factices, `Contrat Atlas (exemple fictif)` et `Situation de départ (exemple fictif)`, puis affirme sans extraction réelle : activité d’équipements d’inspection industrielle/maintenance B2B, trésorerie disponible de 320 k€ et contrat Atlas probable à 480 k€. Le mode connecté doit remplacer toute la carte de confirmation par les faits réellement extraits ou saisis, chacun avec source et état de confirmation.

### 12.5 Outils de contexte de modèle

Le provider enregistre actuellement :

- `read_cockpit_status` ;
- `stage_atlas_contract_simulation`.

Le second annonce `status: staged` après un simple `updateContract`, ce qui peut être incohérent avec l’état de la règle. Lors du raccord, ces outils doivent devenir des adaptateurs aux mêmes services sécurisés que l’interface ou être retirés.

## 13. Modèle de domaine à conserver ou enrichir

### 13.1 Métriques et séries

Le moteur retourne déjà des objets portant identifiant, libellé, valeur, unité, statut, qualification, feuille et cellule. Il faut conserver cette richesse jusque dans le view-model, même si l’écran n’en montre qu’une partie.

Séries moteur existantes :

- `cash` : trésorerie mensuelle ;
- `revenue` : chiffre d’affaires mensuel ;
- `receipts` : encaissements ;
- `payments` : décaissements.

Métriques moteur existantes :

- `revenue` ;
- `gross_margin` ;
- `ebitda` ;
- `net_income` ;
- `valuation` ;
- `valuation_vc` ;
- `cash_min` ;
- `cash_break_date` ;
- `financing_need`.

**BLOCAGE DE SÉMANTIQUE À LEVER AVANT D’ALIMENTER L’UI**

L’audit de `decision_model.py` et du guide du classeur fait apparaître trois noms qu’il ne faut pas brancher tels quels sans test sur un classeur de référence :

1. `gross_margin` pointe vers `Compte de Résultat!D25` et représente un montant en EUR, alors que le cockpit affiche actuellement un pourcentage. L’API cible doit distinguer `gross_margin_amount` et `gross_margin_rate`.
2. La série appelée `revenue` lit actuellement la ligne 88 de `Modèle financier`. D’après le guide, cette ligne correspondrait au facturé et non au revenu reconnu. Il faut vérifier cette sémantique sur le classeur, puis renommer la série ou la relier au bon total.
3. La ligne 301 de `Modèle financier` représente les encaissements totaux. Elle ne doit pas être libellée « règlements clients » si elle inclut d’autres flux.

Tant que ces trois points ne sont pas qualifiés, l’interface doit afficher un état « À vérifier » plutôt qu’un chiffre au libellé potentiellement faux.

Écarts avec les cartes actuelles :

| Carte du cockpit | Source moteur | Attention |
|---|---|---|
| Chiffre d’affaires sur l’horizon | série `revenue` sommée sur l’horizon choisi, ou métriques annuelles | le `revenue` simple est annuel, pas automatiquement « horizon » |
| Marge brute en % | `gross_margin / revenue` | le moteur expose une marge en EUR ; le taux doit être calculé avec statut et période identiques |
| Point bas | `cash_min` | correspondance directe si la série est complète et fraîche |
| Visibilité en mois | série `cash` + `cash_break_date` | le moteur ne renvoie pas le `runway` actuel ; définir précisément la convention |
| Tension de cash | différence des `cash_min` scénario/référence | valeur comparative, pas une métrique isolée du classeur |

Ne jamais afficher une ancienne valeur en cache comme résultat courant. Si la qualification ou la fraîcheur ne permet pas l’usage, afficher « À compléter ou recalculer ».

### 13.2 Contrat Atlas vers le modèle réel

Le registre réel est `DATA Contrats`. Les identifiants pertinents sont :

| Champ du cockpit | Champ(s) réel(s) | Conversion/contrainte |
|---|---|---|
| Client | `contract_client` | texte ; source requise |
| Montant 480 k€ | `contract_quantity` × `contract_unit_price` | aucun champ « montant total » directement saisissable ; ne pas supposer quantité = 1 sans accord métier |
| Offre | `contract_offer` | obligatoire pour relier prix, unité et paramètres d’offre ; absent du prototype |
| Début | `contract_start` | vraie date ISO, pas le texte « Octobre 2026 » |
| Durée 4 mois | `contract_end` dérivé du début et de la convention de fin | décider dates inclusives/exclusives ; moteur exige fin ≥ début |
| Revenu progressif | `contract_recognition = "Etalee sur la duree"` | choix exact du catalogue ; formule centrale inchangée |
| Revenu à la fin | `contract_recognition = "Fin de contrat"` | choix exact du catalogue |
| Facturation acompte/solde | `contract_invoicing = "Acompte et solde"` | distinct de la reconnaissance du revenu |
| Acompte 20 % ou 40 % | `contract_deposit_rate = 0.20` ou `0.40` | le moteur attend une fraction entre 0 et 1 |
| Date de l’acompte | `contract_deposit_date` | vraie date de facture |
| Date du solde | `contract_balance_date` | date de facture du solde, pas date d’encaissement |
| Statut probable | `contract_status = "Probable"` | pondération séparée |
| Statut signé | `contract_status = "Signe"` | valeur exacte du catalogue, même si l’UI affiche « Signé » |
| Probabilité | `contract_weight` | fraction ; absente du prototype ; signé est pondéré à 100 % par le moteur |
| TVA | `contract_vat_regime`, `contract_vat_rate` | absents du prototype ; vide suit le défaut de l’offre |
| Délai client 30/60 jours | `offer_payment_days` | porté par l’offre, pas par la ligne contrat dans le modèle actuel |

Repères physiques confirmés dans le classeur pour l’adaptateur serveur, à ne jamais recopier dans les composants React :

| Donnée | Zone de `DATA Contrats` |
|---|---|
| Client | colonne B |
| Offre/prestation | colonne C |
| Quantité | colonne E |
| Prix unitaire négocié | colonne F |
| Début / fin | colonnes H / I |
| Reconnaissance | colonne J |
| Facturation | colonne K |
| Acompte | colonnes L / M |
| Jalon | colonnes N / O |
| Solde | colonnes P / Q |
| Signé ou probable | colonne R |
| Pondération | colonne S |
| Exceptions TVA | colonnes AL / AM |

Les lignes métier disponibles vont actuellement de 14 à 413. Ces coordonnées sont un détail d’implémentation du modèle versionné : le cockpit doit continuer à parler avec les identifiants sémantiques `contract_*`.

Chaîne de dépendances à expliquer au dirigeant avec des noms simples, tout en la conservant techniquement côté moteur :

```text
Assumptions + DATA Contrats
  → Contrats
  → Revenue
  → COGS / Stock / ATELIER_CIR_IS / BFR
  → Modèle financier
  → Compte de Résultat / Bilan / Flux
  → KPI Dashboard / Contrôles
```

Totaux utiles de `Revenue` à qualifier dans l’adaptateur : ligne 282 revenu reconnu, 283 facturé, 284 encaissé, 285 créances, 286 avances/PCA et 287 FAE.

Les feuilles calculées `Contrats`, `Revenue`, `COGS`, `CAPEX`, `Modèle financier`, `Compte de Résultat`, `Bilan`, `Flux de trésorerie`, `Plan de financement`, `KPI Dashboard` et `Contrôles` restent verrouillées. Les saisies passent par les registres `DATA *` ou les plages explicitement autorisées du catalogue.

### 13.3 Blocage métier : délai propre au contrat ou partagé par l’offre

**DÉCISION À PRENDRE AVANT LE PREMIER CÂBLAGE D’ÉCRITURE**

Option A, sans changer le modèle : le cockpit indique clairement « délai d’encaissement de l’offre » et avertit de tous les contrats affectés avant modification.

Option B, cohérente avec le texte actuel : étendre le modèle et son catalogue avec un délai propre à la ligne contrat, puis faire valider ses formules, dépendances, migrations et tests.

Il est interdit de présenter une modification globale d’offre comme un changement limité à Atlas.

### 13.4 La règle « quatre mois » n’est pas une formule à réécrire

Pour le cas homologué montré dans la démo, l’action du compagnon doit préparer des valeurs autorisées : dates, `contract_recognition`, mode de facturation et acompte. La formule schématique peut rester une explication pédagogique, mais le moteur doit continuer à protéger les formules centrales.

Une véritable adaptation de formule ne doit apparaître que pour un cas non couvert par le catalogue et suivre un processus de maintenance/homologation distinct du parcours client ordinaire.

## 14. API moteur existante : inventaire

Préfixe : `/api`.

### 14.1 Système et dossiers

| Méthode | Route | Usage |
|---|---|---|
| GET | `/health` | état et version du serveur |
| GET | `/settings` | configuration publique du fournisseur de chat |
| PUT | `/settings` | enregistrer base URL, modèle et secret côté poste |
| POST | `/settings/test` | tester la configuration |
| GET | `/cases` | lister les dossiers |
| POST | `/cases` | créer un dossier |
| GET | `/cases/{case_id}` | lire le dossier actif et sa révision |

### 14.2 Classeur et espace de travail

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/workshop` | vue globale guidée |
| GET | `/cases/{case_id}/sheets` | feuilles disponibles |
| GET | `/cases/{case_id}/cells` | fenêtre de cellules d’une feuille |
| GET | `/cases/{case_id}/agents` | agents et rôles par feuille |
| GET | `/cases/{case_id}/charts` | graphiques présents dans le classeur |
| GET | `/cases/{case_id}/registers` | registres métier et champs autorisés |
| POST | `/cases/{case_id}/registers/{sheet}/records` | préparer une ligne métier au brouillon |
| POST | `/cases/{case_id}/registers/{sheet}/extend` | préparer une extension autorisée |
| POST | `/cases/{case_id}/offers` | préparer une offre supplémentaire |

### 14.3 Sources et extraction

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/sources` | lister les sources |
| GET | `/cases/{case_id}/sources/{source_id}` | lire le texte d’une source |
| GET | `/cases/{case_id}/sources/{source_id}/file` | ouvrir la pièce enregistrée |
| POST | `/cases/{case_id}/sources` | ajouter une réponse textuelle |
| POST | `/cases/{case_id}/sources/upload` | téléverser une pièce, 50 Mio maximum (`50 × 1024 × 1024` octets) |
| GET | `/cases/{case_id}/extractions` | lister les extractions |
| POST | `/cases/{case_id}/extractions` | lancer une extraction |
| GET | `/cases/{case_id}/extractions/{id}` | lire faits, pages et diagnostics |
| POST | `/cases/{case_id}/extractions/{id}/propose` | proposer les faits sélectionnés au brouillon |

**DÉCISION DE FORMATS À ALIGNER AVANT CÂBLAGE**

| Format | Installation actuelle | Extraction moteur | Suivi actuel | Import réalisé moteur |
|---|---:|---:|---:|---:|
| PDF | oui | oui | non | non |
| DOCX | oui | oui | non | non |
| PPTX | non | oui | non | non |
| XLSX | oui | oui | oui | oui |
| XLSM | non | oui | non | oui |
| XLS ancien | oui | non | oui | non |
| CSV | oui | oui | oui | oui |
| TXT | non | oui | non | non |
| PNG/JPEG/TIFF/BMP/WebP | non | oui par OCR si disponible | non | non |

Le navigateur ne doit donc pas continuer à annoncer `.xls` comme pris en charge tant qu’un convertisseur contrôlé n’existe pas. À l’inverse, décider explicitement si `.xlsm`, PPTX, texte et images doivent apparaître dans le sélecteur. Le serveur reste l’autorité et refuse tout format non autorisé, indépendamment de l’attribut HTML `accept`.

### 14.4 Profil, questionnaire et qualifications

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/profile` | profil entreprise |
| PUT | `/cases/{case_id}/profile` | enregistrer le profil |
| POST | `/cases/{case_id}/profile/propose` | préparer calendrier/horizon au brouillon |
| GET | `/cases/{case_id}/questionnaire` | questions et champs attendus |
| POST | `/cases/{case_id}/answers` | proposer des réponses guidées |
| GET | `/cases/{case_id}/qualifications` | modules, règles et questions |
| POST | `/cases/{case_id}/qualifications/preview` | examiner une qualification |
| POST | `/cases/{case_id}/qualifications/apply` | adopter la qualification avec jeton |

### 14.5 Brouillon, aperçu et version officielle

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/draft` | lire le brouillon partagé |
| POST | `/cases/{case_id}/draft/operations` | ajouter des opérations contrôlées |
| POST | `/cases/{case_id}/draft/resolve` | arbitrer un conflit |
| DELETE | `/cases/{case_id}/draft` | abandonner le brouillon |
| POST | `/cases/{case_id}/draft/preview` | lancer l’aperçu |
| GET | `/cases/{case_id}/draft/preview-details` | télécharger le manifeste détaillé si présent |
| POST | `/cases/{case_id}/draft/apply` | appliquer le brouillon approuvé dans une nouvelle copie |
| POST | `/cases/{case_id}/recalculate` | recalculer la version courante avec Excel |
| GET | `/cases/{case_id}/versions` | lister les versions |
| POST | `/cases/{case_id}/versions/{version_id}/restore` | restaurer en créant une nouvelle version |
| GET | `/cases/{case_id}/download` | télécharger le XLSM courant |

### 14.6 Scénarios et analyses

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/scenarios` | scénarios liés à la référence |
| POST | `/cases/{case_id}/scenarios` | créer une copie nommée de la révision courante |
| GET | `/cases/{case_id}/scenarios/compare` | métriques, métriques annuelles et séries |
| GET | `/cases/{case_id}/capitalization` | simulation de capitalisation |
| POST | `/cases/{case_id}/capitalization` | préparer un aperçu de dilution |
| POST | `/cases/{case_id}/capitalization/apply` | adopter cette simulation spécifique |
| GET | `/cases/{case_id}/goals` | résultats de recherche d’objectif |
| POST | `/cases/{case_id}/goals` | lancer une recherche d’objectif |
| GET | `/cases/{case_id}/sensitivities` | campagnes de sensibilité |
| POST | `/cases/{case_id}/sensitivities` | lancer une campagne |

### 14.7 Réalisé

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/actuals` | données validées, écarts, historique et forecast |
| POST | `/cases/{case_id}/actuals` | aperçu d’une saisie manuelle |
| POST | `/cases/{case_id}/actuals/import` | lire/mapper un fichier et produire un aperçu |
| POST | `/cases/{case_id}/actuals/apply` | adopter l’aperçu du réalisé |
| GET | `/cases/{case_id}/actuals/bridge/questions` | questions du raccord |
| POST | `/cases/{case_id}/actuals/reforecast` | préparer le raccord au brouillon |
| GET | `/cases/{case_id}/accounting/catalog` | catalogue comptable |
| GET | `/cases/{case_id}/accounting/mapping` | aide indicative de correspondance |

### 14.8 Livrables et aller-retour Excel

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/reports` | lister les jeux de livrables |
| POST | `/cases/{case_id}/reports` | générer un jeu depuis une révision |
| GET | `/cases/{case_id}/reports/{report_id}/{format}` | télécharger un format |
| POST | `/cases/{case_id}/roundtrip` | comparer un Excel exporté puis modifié |

### 14.9 Chat, tâches, événements et reprise

| Méthode | Route | Usage |
|---|---|---|
| GET | `/cases/{case_id}/chat` | historique de conversation |
| POST | `/cases/{case_id}/chat` | envoyer une demande contextualisée |
| GET | `/cases/{case_id}/jobs` | tâches et états |
| POST | `/cases/{case_id}/jobs/{job_id}/retry` | reprendre un échec/interruption |
| POST | `/cases/{case_id}/jobs/{job_id}/cancel` | interruption contrôlée de sensibilité |
| GET | `/cases/{case_id}/events?after={cursor}` | flux SSE `refresh`, `resync`, `job`, `chat` avec reprise |
| GET | `/cases/{case_id}/intents/{request_id}` | retrouver le résultat d’une intention |
| GET | `/cases/{case_id}/intents/{request_id}/review` | examiner une intention ambiguë |
| POST | `/cases/{case_id}/intents/{request_id}/review` | clôturer après examen sans rejouer |

### 14.10 Maintenance de modèle

Ces routes ne doivent pas apparaître comme des actions ordinaires d’un dirigeant :

- `POST /cases/{case_id}/model/wacc-fingerprint` ;
- `POST /cases/{case_id}/model/dcf-calendar` ;
- `POST /cases/{case_id}/model/fiscal-calendar`.

Elles préparent des migrations contrôlées au brouillon et relèvent d’un parcours expert/maintenance.

## 15. Protections moteur à réutiliser telles quelles

### 15.1 Révision attendue

Toute écriture importante doit porter `expected_revision`. Si la référence a changé depuis l’écran, le serveur refuse le lot. Le front recharge et propose à l’utilisateur de réexaminer les différences.

### 15.2 Identifiant d’intention

Le front historique crée un `request_id` stable à partir de l’intention, le garde en local pendant une coupure et interroge `/intents/{request_id}` avant de rejouer. Un même identifiant avec un contenu différent est refusé.

Cette logique doit être adaptée dans le nouveau client API. Ne jamais régénérer un identifiant à chaque retry réseau d’une commande financière.

### 15.3 Brouillon, aperçu et jeton

Le flux d’écriture officiel est :

```text
opérations → brouillon → aperçu → jeton d’approbation → application → nouvelle version → recalcul
```

L’application vérifie que le `draft_id`, le statut `READY` et `approval_token` correspondent toujours. Si l’aperçu a changé, il faut le relire.

### 15.4 Empreinte et source

Les sources, le classeur, le modèle et les opérations portent des empreintes. Une source altérée ou un modèle incompatible bloque l’écriture. Les chemins sont confinés au dossier.

### 15.5 Formules protégées

Le catalogue autorise des valeurs littérales uniquement dans les zones reconnues. Une entrée vide ne devient pas zéro. Les formules centrales, valeurs calculées et structures non autorisées restent refusées par le moteur.

## 16. Architecture de raccord recommandée

### 16.1 Principe

```text
Pages du cockpit
      ↓
CockpitProvider + hooks de lecture/commande
      ↓
CockpitGateway (types stables orientés dirigeant)
      ↓
Client HTTP commun : révision, request_id, erreurs, jobs, SSE
      ↓
API FastAPI existante
      ↓
Services tca_bp et adaptateur cockpit très fin
      ↓
SQLite + copies XLSM + recalcul Excel
```

`CockpitGateway` ne calcule pas la finance. Il :

- normalise les réponses ;
- agrège les vues ;
- transforme un pourcentage UI en fraction moteur ;
- traduit les choix du catalogue en libellés humains ;
- suit les jobs ;
- détecte une réponse périmée ;
- présente les erreurs.

### 16.2 Même origine

Le front historique appelle des URLs relatives `/api`. Il faut conserver ce principe.

Pour le développement, le serveur du cockpit peut proxyfier `/api` vers `http://127.0.0.1:8765`. Pour la livraison, deux options restent à valider :

1. produire un build statique servi par FastAPI ;
2. lancer le serveur du cockpit et le moteur derrière un lanceur/proxy local commun.

Éviter de disperser une URL absolue du moteur dans les composants et éviter une configuration CORS large.

### 16.3 Façade de front

Une interface transitoire peut reprendre les verbes actuels, mais avec des promesses et des identifiants :

```ts
interface CockpitGateway {
  getCockpit(caseId: string): Promise<CockpitSummary>;
  getJourney(caseId: string): Promise<JourneyView>;
  getContractDraft(caseId: string, recordId: string): Promise<ContractDraftView>;
  patchContractDraft(command: ContractDraftCommand): Promise<DraftView>;
  previewImpacts(caseId: string, draftId: string): Promise<ImpactPreview>;
  runSimulation(command: SimulationCommand): Promise<JobReceipt>;
  getSimulation(caseId: string, simulationId: string): Promise<SimulationView>;
  saveScenario(command: SaveScenarioCommand): Promise<ScenarioView>;
  applyCandidate(command: ApplyCandidateCommand): Promise<JobReceipt>;
  listVersions(caseId: string): Promise<ReferenceView[]>;
  restoreVersion(command: RestoreCommand): Promise<JobReceipt>;
  importActuals(command: ActualsImportCommand): Promise<ActualsPreview>;
  generateReport(command: ReportCommand): Promise<JobReceipt>;
  sendCompanionMessage(command: CompanionCommand): Promise<JobReceipt>;
}
```

Les noms sont indicatifs. La logique existante du moteur reste la source de vérité.

Prévoir deux implémentations derrière cette même interface : `DemoCockpitGateway`, qui conserve les fixtures actuelles pour la démonstration, et `EngineCockpitGateway`, qui parle à l’API réelle. Le choix doit venir d’une configuration explicite au démarrage. Il est interdit de compléter silencieusement une réponse moteur incomplète avec une valeur de démonstration.

### 16.4 View-model minimal

```ts
type QualifiedValue = {
  value: number | string | null;
  unit: string;
  status: string;
  period?: string;
  sourceIds?: string[];
  calculationRevision?: number;
  fresh: boolean;
};

type CashSeries = {
  id: 'cash';
  categories: string[]; // YYYY-MM
  values: Array<number | null>;
  unit: 'EUR';
  status: string;
};

type ImpactPreview = {
  caseId: string;
  baseRevision: number;
  draftId: string;
  draftFingerprint: string;
  controls: ControlView[];
  impacts: ImpactView[];
  approvalState: 'incomplete' | 'reviewable' | 'stale';
};
```

Tous les montants transportés par l’API doivent rester numériques avec unité/devise séparée. Le format français appartient à l’affichage.

### 16.5 Façades métier recommandées

Les routes existantes suffisent pour commencer en lecture seule. Pour éviter que les pages connaissent les feuilles, les coordonnées et l’orchestration Excel, les façades suivantes sont recommandées :

| Méthode et route indicative | Rôle | Règle de sécurité |
|---|---|---|
| `GET /api/cases/{case_id}/cockpit` | agréger référence, phase, alertes, brouillon et jobs | lecture seule, révision et fraîcheur visibles |
| `POST /api/cases/{case_id}/contracts/draft` | traduire un contrat métier vers `DATA Contrats` | source, `request_id` et `expected_revision` obligatoires |
| `GET /api/cases/{case_id}/draft/impacts` | exposer changements, chaîne, invariants et contrôles | réponse liée au fingerprint du brouillon |
| `POST /api/cases/{case_id}/scenarios/from-draft` | simuler le brouillon dans une copie enfant | aucune mutation de la référence |
| `POST /api/cases/{case_id}/scenarios/{scenario_id}/adopt` | recréer les entrées reconnues dans un brouillon parent | ne contourne jamais aperçu et jeton d’approbation |
| `GET /api/cases/{case_id}/decisions` | agréger le journal métier | relie auteur, raison, sources et versions |
| `GET /api/cases/{case_id}/rules/catalog` | lister les recettes homologuées | aucune formule fabriquée par le navigateur |
| `POST /api/cases/{case_id}/rules/{rule_id}/propose` | proposer une recette au brouillon | migration inconnue réservée au mainteneur du modèle |

Exemple de commande Contrat, volontairement dépourvue de coordonnées Excel :

```json
{
  "request_id": "uuid-stable",
  "expected_revision": 12,
  "evidence_id": "source-id",
  "contract": {
    "record_id": null,
    "client": "Atlas Mobility",
    "offer_id": "offre-id",
    "quantity": 1,
    "unit_price": 480000,
    "start_date": "2026-10-01",
    "end_date": "2027-01-31",
    "recognition": "SPREAD_OVER_PERIOD",
    "invoicing": {
      "mode": "DEPOSIT_AND_BALANCE",
      "deposit_rate": 0.4,
      "deposit_date": "2026-10-01",
      "balance_date": "2027-01-31"
    },
    "commercial": {
      "status": "PROBABLE",
      "weight": 1
    }
  }
}
```

L’adaptateur résout l’offre, convertit les enums UX vers les libellés du catalogue, calcule les dates selon une convention explicitée, ajoute les preuves et refuse un contrat incomplet. L’exemple `quantity = 1` n’est valable que si Atlas est confirmé comme une prestation au forfait.

L’adoption d’un scénario ne doit pas copier son fichier sur la référence. Elle compare ses entrées reconnues, crée un brouillon dans le dossier parent, conserve la filiation, puis repasse par aperçu et application. Le nom exact des routes reste modifiable avant implémentation ; leur séparation d’autorité, elle, est obligatoire.

## 17. Orchestration correcte d’une simulation

L’API actuelle offre les briques mais pas l’orchestration complète. La proposition suivante minimise les nouveaux développements.

### 17.1 Préparer le candidat sur la référence

1. Lire la référence et sa `revision`.
2. Ajouter ou modifier les valeurs autorisées au brouillon de la référence.
3. Conserver `draft_id`, empreinte des opérations, sources et `expected_revision`.
4. Lancer l’aperçu et lire les contrôles/impacts.

Aucune version officielle n’est modifiée.

### 17.2 Simuler dans une copie isolée

Créer un endpoint d’orchestration, par exemple :

```text
POST /api/cases/{case_id}/scenarios/from-draft
```

Entrée : `draft_id`, `draft_fingerprint`, `expected_revision`, nom et `request_id`.

Traitement serveur :

1. vérifier que le brouillon et la référence correspondent toujours ;
2. créer une copie de scénario à partir de la révision ;
3. recopier exactement les opérations et leurs sources dans la copie ;
4. préparer/appliquer l’aperçu uniquement dans la copie ;
5. recalculer la copie avec Excel ;
6. lire les métriques et séries ;
7. enregistrer un `simulation_id` avec les empreintes de départ ;
8. publier les événements du job.

La référence de base reste inchangée.

### 17.3 Conserver

Un scénario temporaire peut être marqué comme conservé et nommé. S’il est déjà une copie moteur, ne pas dupliquer une nouvelle fois le XLSM sans raison.

### 17.4 Appliquer officiellement

Au clic final :

1. vérifier que `simulation_id`, brouillon, révision de base et empreinte sont toujours identiques ;
2. appliquer le brouillon déjà approuvé sur la référence avec son jeton ;
3. créer la nouvelle version ;
4. recalculer ;
5. enregistrer la décision et le lien vers la simulation ;
6. renvoyer la nouvelle révision ;
7. seulement alors, naviguer vers Décisions.

Si l’application réussit mais le recalcul échoue, la nouvelle version existe avec un statut « À recalculer/Échec ». Ne pas annoncer de métriques officielles fraîches. Proposer la reprise de la tâche.

### 17.5 Pourquoi ne pas « copier le résultat du scénario »

Un résultat agrégé n’est pas une source suffisante pour publier une référence. La référence doit être reproductible depuis les opérations, les sources, le modèle et le calcul. Copier cinq KPI depuis le navigateur détruirait cette traçabilité.

## 18. Impacts : ce qui existe et ce qu’il manque

Le moteur dispose déjà du graphe de dépendances, du catalogue des champs, du brouillon, des diagnostics et de l’aperçu avant/après. Il manque une vue métier compacte correspondant au volet du cockpit.

**ADAPTATEUR À CRÉER** : transformer le différentiel de l’aperçu en :

- entrées directement modifiées ;
- calculs dépendants ;
- sorties touchées ;
- invariants vérifiés ;
- thèmes concernés ;
- périodes ;
- valeurs avant/après ;
- sources ;
- qualifications ;
- statut de fraîcheur.

Cette vue peut être produite par un nouveau service de lecture. Elle ne doit pas reprogrammer les formules ou prédire le résultat sans calcul.

## 19. Modes d’accompagnement et thèmes

Les six thèmes actuels sont utiles comme couche de compréhension :

| Thème | Feuilles actuelles associées |
|---|---|
| Ventes et contrats | DATA Contrats, Contrats, Revenue |
| Coûts et marge | DATA COGS, COGS, Stock, Charges_Externes |
| Équipe | Effectifs, CALCUL_CIR |
| Investissements et financement | DATA CAPEX, CAPEX, Financement Dette, DATA Financement, Financement E&S, SUBVENTION_INVEST |
| Trésorerie et fiscalité | BFR, ATELIER_CIR_IS, Flux de trésorerie |
| Synthèse et valeur | KPI Dashboard, Contrôles, Valorisation, Sensi Analyses |

Les associations doivent être lues depuis le profil/catalogue versionné du modèle à terme. Un renommage de feuille ne doit pas casser un thème métier.

`Guide-moi` et `Fais-le pour moi` changent le niveau d’explication, pas les règles d’autorisation :

- guidé : questions une par une, mais mêmes contrôles ;
- automatique : le compagnon prépare plus de champs au brouillon, mais n’applique jamais la référence.

## 20. Huit groupes du mode expert

Le prototype masque les 33 feuilles sous huit groupes :

1. Cadre du projet : Légende, Control, Assumptions, Previsionnel.
2. Ventes et contrats : DATA Contrats, Contrats, Revenue.
3. Coûts, exploitation et équipe : DATA COGS, COGS, Stock, Charges_Externes, Effectifs.
4. Investissements et financements : DATA CAPEX, CAPEX, Financement Dette, DATA Financement, Financement E&S, SUBVENTION_INVEST.
5. Fiscalité et besoin d’exploitation : CALCUL_CIR, ATELIER_CIR_IS, BFR.
6. Résultats et trésorerie : Modèle financier, Compte de Résultat, Bilan, Flux de trésorerie, Plan de financement.
7. Scénarios et valeur : Sensi Scénarios, Sensi Analyses, Sensi Graphiques, Valorisation, Comparables.
8. Tableau de bord et validations : KPI Dashboard, Contrôles.

Ces groupes sont une navigation, pas une politique de sécurité. Les droits d’écriture viennent du catalogue du moteur.

Écart de libellé à normaliser : le prototype nomme une feuille `Sensi Scénarios`, alors que le modèle documenté expose `Sensi TCA`. La future navigation doit utiliser un identifiant stable du catalogue et afficher le libellé réellement renvoyé, pas déduire une feuille depuis ce texte de démonstration.

## 21. Tâches asynchrones et mises à jour en temps réel

Les statuts existants incluent notamment `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED` et `INTERRUPTED`.

Le front historique utilise :

- `EventSource` sur `/events` ;
- événements `refresh`, `resync`, `job` et `chat` ;
- reconnexion automatique ;
- relecture complète après reconnexion ;
- polling `/jobs` toutes les deux secondes tant qu’un job tourne.

Le nouveau cockpit doit reprendre ce comportement derrière un hook commun. Aucune page ne doit créer son propre mécanisme de polling.

Les événements métier futurs peuvent voyager dans le flux existant sans nouveau bus : `DraftChanged`, `PreviewQueued`, `PreviewReady`, `PreviewBlocked`, `SimulationQueued`, `SimulationReady`, `SimulationFailed`, `ReferenceAdopted`, `VersionRestored`, `ActualsImported`, `ActualsApplied`, `ReportReady` et `IntentReviewRequired`.

Le client doit considérer la livraison comme « au moins une fois » : dédupliquer les événements par identifiant, ne jamais déclencher une seconde écriture depuis leur réception et refaire une lecture autoritative complète après `resync`.

États UX minimaux pour chaque commande longue :

- prêt ;
- en attente ;
- en cours avec étape lisible ;
- terminé ;
- échec récupérable ;
- échec exigeant une revue ;
- résultat périmé ;
- connexion perdue, tâche peut-être toujours en cours ;
- reprise réussie.

La fermeture du navigateur n’arrête pas une tâche déjà reçue par le moteur.

## 22. Erreurs, conflits et messages

Comportements actuels de l’API :

- `400` : en-tête `Content-Length` invalide ;
- `403` : hôte, origine ou requête cross-site refusée par la protection locale ;
- `409` : conflit métier, révision, brouillon ou intention à examiner ;
- `413` : requête HTTP supérieure à 52 Mio refusée par le middleware ;
- `422` : paramètres invalides, sans réexposer un secret ;
- `502` : fournisseur externe indisponible, avec caractère retentable ;
- erreur réseau : serveur local injoignable ou réponse interrompue.

Nuance d’upload actuelle : la pièce elle-même est limitée à 50 Mio. Entre cette limite fichier et la limite HTTP de 52 Mio, le dépassement lève aujourd’hui un `ValueError` traduit en `409`; au-delà de 52 Mio, le middleware répond `413`. Le futur adaptateur peut uniformiser le code métier en `UPLOAD_TOO_LARGE`, mais doit conserver les deux protections serveur.

Règles d’interface :

- ne pas perdre les valeurs saisies sur une erreur ;
- ne pas naviguer après une mutation échouée ;
- ne pas afficher un toast de succès avant le reçu ;
- sur `409`, recharger la révision et expliquer ce qui a changé ;
- sur état incertain, consulter l’intention avant toute nouvelle écriture ;
- afficher l’identifiant du dossier, la révision et le job dans le détail technique ;
- présenter au dirigeant une formulation simple et une action précise.

### 22.1 Enveloppe d’erreur commune recommandée

```json
{
  "code": "STALE_REVISION",
  "message": "Une version plus récente existe.",
  "request_id": "uuid",
  "correlation_id": "trace-id",
  "retryable": false,
  "current_revision": 13,
  "field_errors": []
}
```

Codes que le gateway doit savoir traduire en états UX : `STALE_REVISION`, `IDEMPOTENCY_MISMATCH`, `DRAFT_CONFLICT`, `PREVIEW_BLOCKED`, `APPROVAL_TOKEN_EXPIRED`, `SOURCE_REQUIRED`, `MISSING_ASSUMPTION`, `CALCULATION_OUTDATED`, `FORMULA_CHANGE_FORBIDDEN`, `MODEL_MIGRATION_REQUIRED`, `INTENT_REVIEW_REQUIRED`, `UPLOAD_TOO_LARGE`, `UNSUPPORTED_FILE` et `WORKER_INTERRUPTED`.

Le `correlation_id` doit suivre la chaîne complète : clic, commande HTTP, intention, job, événement, puis version, scénario ou rapport. Le message dirigé vers le client reste simple ; le code et l’identifiant servent au diagnostic.

### 22.2 Observabilité sans fuite de données

Mesures minimales : longueur des files, attente et exécution, durée Excel, blocages d’aperçu, conflits de révision, intentions à revoir, échecs de recalcul et âge du dernier calcul valide.

Ne jamais journaliser les valeurs financières détaillées, le contenu intégral d’un document, le classeur, un secret fournisseur ou des données personnelles inutiles.

## 23. Sécurité, confidentialité et déploiement

### 23.1 Situation actuelle

Le moteur est local, avec SQLite, dossiers confinés, secrets protégés sur le compte Windows et Excel local. Il n’existe pas d’authentification multi-utilisateur ni d’isolation multi-tenant hébergée. Le serveur actuel mise également sur la même origine, une politique CSP et l’absence de cache pour les réponses sensibles ; ces protections sont utiles mais ne remplacent pas une authentification si le produit sort de la machine.

### 23.2 Si le produit reste local

- utiliser `127.0.0.1` ;
- même origine entre front et API ;
- jeton de session local ou protection contre les requêtes d’une autre origine ;
- vérification stricte des uploads ;
- un seul service propriétaire du stockage ;
- sauvegarde et restauration du dossier de données.

### 23.3 Si le produit devient hébergé

Il faudra une architecture distincte : authentification, organisations, rôles, stockage objet, chiffrement, audit, quotas et workers Windows/Excel isolés. Le verrou local et SQLite ne suffisent pas à une collaboration distante.

**DÉCISION À PRENDRE** : livraison desktop locale pour les 90 jours, hébergement, ou hybride. Ne pas commencer le câblage en supposant implicitement le cloud.

### 23.4 Permissions métier

Rôles minimaux à prévoir, même en local si plusieurs personnes utilisent le dossier :

- lecteur ;
- contributeur de brouillon ;
- dirigeant pouvant adopter une référence ;
- assistant/conseil ;
- mainteneur de modèle.

Le client peut modifier les entrées métier. Le compagnon ou l’assistant peut préparer des adaptations. Les formules centrales et les migrations de modèle restent réservées au processus de maintenance.

## 24. Contrat UX/UI premium à préserver pendant le câblage

Le raccord au moteur ne doit pas transformer le cockpit en écran technique. L’UX/UI fait partie du contrat fonctionnel : le dirigeant doit toujours savoir où il est, ce qui est encore un essai, ce qui changera et quelle action rend une décision officielle.

### 24.1 Direction visuelle et primitives

La direction actuelle est une interprétation professionnelle, lumineuse et pastel de la profondeur iOS, pas une copie d’Apple :

- fond très clair avec halos lilas, ciel, menthe et pêche ;
- marque blanche pilotée par `--brand`, `--brand-deep`, `--brand-soft` et `--brand-accent` ;
- aucune marque TCA visible dans le produit client ; le nom, le logo et la palette de l’entreprise restent prioritaires ;
- textes financiers foncés et surfaces critiques suffisamment opaques ;
- verre local : le contenu qui passe derrière doit être perceptible puis flouté, sans voile opaque couvrant toute la page ;
- trois niveaux de profondeur maximum et trois cartes interactives maximum dans une pile ;
- une carte active au premier plan, couches secondaires qui dépassent sans cacher chiffre ou action, bulles contextuelles aux angles ;
- pas de grosse barre de navigation en bas ; îlot latéral flottant sur ordinateur, capsule supérieure et tiroir sur téléphone ;
- pas d’image externe nécessaire pour les halos et décors.

Primitives à conserver et à réutiliser plutôt que recréer page par page :

| Primitive | Source | Usage |
|---|---|---|
| `Surface` | `components/cockpit/page-elements.tsx` | variantes `solid`, `glass`, `tinted`, `floating` |
| `SpatialCluster` | même fichier | composition spatiale et isolation des couches |
| `CardStack` | même fichier | pile limitée et ordre visuel maîtrisé |
| `FloatingBubble` | même fichier | information courte, jamais un faux bouton |
| `StateBadge` et `Delta` | même fichier | états et écarts strictement non cliquables |
| `CashCurve` | même fichier | courbe mensuelle interactive et accessible |
| `NumberField` | `components/cockpit/number-field.tsx` | saisie intermédiaire sûre avant validation du brouillon |
| `liquid-control` | `app/globals.css` | contrôles vitrés tactiles |
| `top-glass-control` | `app/globals.css` | marque et commandes flottantes supérieures |
| `nav-island` | `app/globals.css` | navigation détachée, sans panneau blanc massif |
| `CompanionBadge` | `components/cockpit/companion-mark.tsx` | compagnon vivant, non technique |

Repères actuels centralisés dans `app/globals.css` : fond `#f4f7fb`, surfaces solides autour de 96,5 % de blanc, verre générique autour de 58 %, ombres `--shadow-near`, `--shadow-mid`, `--shadow-far`, flou de 26 px pour les capsules hautes, 36 px pour les bulles, 42 px pour l’îlot de navigation et environ 44 px pour les grandes plaques ; rayons courants de 30 à 38 px pour les cartes et de 18 à 24 px pour les contrôles ; courbe d’animation `cubic-bezier(0.16, 1, 0.3, 1)`. Ces valeurs peuvent être affinées, mais ne doivent pas être remplacées par des cartes opaques et des ombres grises génériques lors du raccord.

Les pictogrammes applicatifs sont servis localement depuis `public/icone/iconoir-sprite.svg`, par `components/ui/site-icon.tsx`. La source Iconoir, sa révision et sa licence MIT sont documentées dans `public/icone/SOURCE.md` et `LICENSE-ICONOIR.txt`. Le compagnon est un SVG original séparé de cette banque. Ne pas réintroduire un casque d’assistance, l’icône étincelle de GPT ou des pictogrammes provenant de CDN.

### 24.2 Affordance : ce qui ressemble à un bouton doit agir

Règles impératives :

1. Un contrôle du cockpit navigue dès le premier clic ou toucher. L’utilisateur ne doit jamais devoir cliquer le fond flou pour fermer le menu puis recliquer la destination.
2. Le tiroir mobile se ferme automatiquement après sélection ; le fond flou sert seulement à annuler/fermer.
3. Toute capsule avec contour, survol, ombre de contrôle ou curseur de main est un vrai lien ou bouton avec focus clavier.
4. Une information non interactive, comme le thème « Ventes et contrats » ou le nom « Contrat Atlas Mobility », utilise une typographie de métadonnée, sans style de bouton.
5. Une zone entière peut être cliquable, mais elle ne doit pas contenir plusieurs actions concurrentes invisibles.
6. Les cartes arrière décoratives sont sans événements et retirées de l’ordre clavier.
7. Une action désactivée explique la condition manquante dans le voisinage immédiat ; la couleur seule ne suffit pas.

Les choix `Guide-moi` et `Fais-le pour moi` forment un contrôle segmenté unique : même famille de couleur et même poids visuel, état sélectionné net par fond/contour/`aria-pressed`, aucun pictogramme ambigu d’ampoule ou d’assistance pour différencier artificiellement les deux.

Le bandeau d’accueil « Décision à préparer / Ventes et contrats » doit donc être soit une phrase de contexte non cliquable, soit un seul lien clairement libellé « Ouvrir Ventes et contrats ». Deux pastilles de même apparence dont une seule agit sont interdites.

### 24.3 Hiérarchie et vocabulaire des actions

Une seule action principale fortement colorée par contexte. Les actions de navigation, de brouillon, de simulation et de référence ne doivent jamais être regroupées comme si elles avaient le même effet.

| Libellé recommandé | Effet exact | Niveau |
|---|---|---|
| `Voir le parcours` | naviguer sans modifier les données | navigation secondaire |
| `Annuler mon dernier changement` | restaurer la dernière saisie du brouillon | action locale réversible |
| `Abandonner ce brouillon` | supprimer toutes les modifications non officielles | destructive, confirmation |
| `Revenir aux valeurs officielles` | recharger la référence dans un nouveau brouillon ou quitter la comparaison | destructive pour le brouillon, jamais pour l’historique |
| `Voir les impacts` | lancer/lire l’aperçu du brouillon | étape de contrôle |
| `Comparer avec la version officielle` | créer ou ouvrir une simulation isolée | étape de simulation |
| `Garder cette simulation` | conserver le scénario sans modifier la référence | secondaire sûre |
| `Préparer comme future version officielle` | adopter les entrées du scénario dans le brouillon parent | étape avant validation |
| `Valider la nouvelle version officielle` | appliquer l’aperçu approuvé et créer une version | action finale, confirmation et reçu |
| `Restaurer cette version` | créer une nouvelle version depuis un jalon | action finale, confirmation et reçu |

Éviter le libellé ambigu `Retour au parcours` à proximité de `Annuler` et `Revenir à la référence` sans explication. Ne pas écrire `Choisir comme version officielle` si une seconde phase de contrôle est encore nécessaire : le verbe visible doit correspondre à l’effet réel du clic.

### 24.4 Installation et navigation séquentielle

- Les cinq étapes restent adressables par `?step=0..4`; précédent/suivant du navigateur et liens d’étape restent fonctionnels.
- `Précédent` et `Continuer` sont placés de part et d’autre de la largeur disponible, dans la même famille pastel et avec un contraste lisible. Aucun grand ovale ne les enferme ensemble.
- Chaque cible mesure au moins 44 × 44 px et dispose d’un focus visible.
- Sur petit écran, employer les libellés courts sur toute la largeur mobile ; ne pas attendre 320 px pour traiter un débordement.
- Le compagnon et les commandes d’étape ne peuvent pas occuper le même angle.
- En mode révision, `Enregistrer et terminer` existe à chaque étape.
- Cible de raccord : si l’utilisateur avait cliqué un autre lien, l’interface mémorise cette destination. Après `Enregistrer et terminer`, elle termine réellement la sortie demandée. Écart actuel : `finish()` ignore encore `exitTo` et revient systématiquement vers `/parcours` ou `/`.
- Le changement d’étape et le bouton Précédent/Suivant du navigateur doivent passer par la même protection de saisie ; l’interception actuelle couvre les liens internes et `beforeunload`, pas `popstate`.
- Une actualisation/fermeture avec changements non enregistrés conserve l’avertissement natif prévu.

### 24.5 Compagnon

Le compagnon doit évoquer un partenaire calme, curieux et vivant, pas un service d’assistance technique :

- forme organique colorée, petit visage discret, animation de respiration, flux et clignement ;
- trois états visuels sobres : `calm`, `awake`, `engaged` ;
- accélération légère lorsque le volet est ouvert ou qu’une proposition est prête ;
- aucun clignotement rapide, aucune animation indispensable à la compréhension ;
- aucune pastille rouge d’urgence pour une simple disponibilité ;
- animation entièrement coupée avec `prefers-reduced-motion` ;
- palette dérivée de la marque, mais contraste du visage stable ;
- un seul compagnon sur tout le site, dont la compétence et le texte changent avec la page.

Le volet doit toujours annoncer son contexte : dossier, thème, brouillon ou simulation et référence de départ. Une réponse distingue visuellement explication, proposition, contrôles, confirmation, tâche en cours, résultat et erreur. Le compagnon emploie exactement les mêmes commandes que les boutons de la page.

L’historique de conversation se comporte comme un journal accessible (`role="log"` ou sémantique équivalente) avec annonces polies des nouvelles réponses. Pendant un job, employer une formulation simple comme « Je prépare la simulation », montrer l’étape en cours puis le reçu ; ne jamais dire « appliqué » avant le succès serveur.

### 24.6 Graphiques et chiffres

Les courbes actuelles sont belles mais fictives. Lors du raccord :

- transmettre les vrais points mensuels du moteur, sans lisser ni déplacer artificiellement la série ;
- garder le dégradé de ligne multicolore piloté par la hauteur/zone de risque, avec sens financier documenté ;
- afficher un point interactif au survol, au toucher et au focus clavier pour chaque mois ;
- info-bulle : mois, valeur exacte, unité, nature `réalisé`, `prévision`, `scénario` ou `référence`, et fraîcheur si nécessaire ;
- conserver l’info-bulle dans la carte à 320 px et au zoom 200 % ;
- annoncer le point bas sur la même ligne que le titre si l’espace le permet, en texte simple `Point bas : 42 k€` ;
- ne pas ajouter une étiquette jaune volumineuse ou une pastille ronde `40 %` qui évoque une remise commerciale ;
- distinguer réalisé et prévision par libellé et motif/forme en plus de la couleur ;
- fournir un résumé textuel accessible et une liste/table compacte des valeurs si le graphique est essentiel à la décision ;
- comparer uniquement des calendriers alignés et signaler explicitement les mois absents ;
- pour plusieurs scénarios, imposer le même domaine temporel, la même échelle verticale et la même ligne zéro. Le composant actuel auto-ajuste chaque courbe séparément : cette propriété est acceptable pour une carte isolée, mais visuellement trompeuse dans une comparaison et doit être corrigée au raccord.

### 24.7 Typographie, nombres et microcopie française

- Taille de texte normale : 16 px minimum dans les zones de lecture et de saisie ; les métadonnées peuvent descendre à 13 px si leur contraste reste suffisant.
- Pour une valeur négative, conserver le caractère simple `-`, conformément à la demande explicite de l’utilisateur ; ne pas le remplacer par `−` ou par un tiret cadratin.
- Éviter le tiret cadratin `—` dans les textes ; préférer `:`, une phrase séparée ou des parenthèses.
- Format français : virgule décimale, espaces insécables, `138 k€`, `2,78 M€`, pourcentage séparé par une espace.
- Ne pas fusionner les mots `probable`, `signé`, `reconnu`, `facturé`, `encaissé` et `réalisé`.
- Ne jamais appeler un montant de marge un taux de marge.
- Dans le parcours dirigeant, parler d’abord en langage métier. Le nom de feuille et la formule ne sont visibles qu’en détail expert facultatif.
- Les textes longs et noms de contrats doivent revenir à la ligne ; jamais déborder d’une carte ou être tronqués sans accès au contenu complet.

Correction documentaire du 16 septembre : la première rédaction inversait la préférence utilisateur. Le `-` déjà utilisé dans les pages Simulations et dans `formatEuro()` est le choix à conserver. Centraliser ce formatage côté interface ; le moteur doit transmettre une valeur numérique, jamais une chaîne déjà préfixée.

### 24.8 États de chargement, fraîcheur et erreurs

Chaque donnée ou commande raccordée doit avoir un état visuel explicite :

```text
chargement → prêt → modifié localement → brouillon envoyé → aperçu en cours
→ impacts à relire → simulation en cours → résultat frais
→ adoption en cours → version créée ou erreur/revue nécessaire
```

- Les squelettes gardent la géométrie des cartes pour éviter un saut de mise en page.
- Aucun chiffre fictif ou ancien ne clignote avant l’hydratation ou pendant un chargement moteur.
- Une tâche longue garde la page utilisable, montre une formulation métier de l’étape et peut être retrouvée après navigation.
- Aucun succès optimiste pour une écriture financière. Le bouton montre l’attente et le succès suit le reçu serveur.
- Une simulation périmée reste identifiable mais ne peut pas être adoptée.
- Les erreurs conservent les saisies et proposent une action précise : réessayer, recharger, revoir ou contacter le mainteneur.
- Les détails techniques `case_id`, révision, job et corrélation restent repliés, copiables et accessibles à l’assistant.

Matrice minimale des états connectés :

| État | Présentation et action attendues |
|---|---|
| Hydratation initiale | squelette stable, aucun chiffre de fixture |
| Aucun dossier | invitation claire à commencer l’installation |
| Lecture fraîche | valeurs, période, unité et révision cohérentes |
| Saisie locale non envoyée | indicateur discret « Modifications non enregistrées », sortie protégée |
| Brouillon serveur modifié | état « Brouillon », aperçu disponible, référence inchangée |
| File d’attente | action verrouillée contre le double clic, possibilité de quitter la page |
| Calcul en cours | étape lisible, `aria-busy`, progression ou activité annoncée |
| Succès | reçu serveur, nouvelle révision ou identifiant de résultat visible |
| Résultat périmé | chiffres conservés comme historique, action officielle désactivée, nouveau calcul proposé |
| Validation de champ | erreur au voisinage du champ, focus possible, autres saisies conservées |
| Conflit `409` | expliquer qu’une version plus récente existe, proposer de recharger et comparer |
| Hors ligne ou réponse incertaine | ne pas rejouer ; retrouver l’intention, afficher que la tâche peut continuer |
| Échec récupérable | garder le contexte et proposer une reprise avec le même `request_id` |
| Revue nécessaire | expliquer ce qui doit être vérifié ; aucun retry automatique |
| Permission refusée | expliquer le rôle requis sans masquer l’objet consultable |
| Interrompu/annulé | état final explicite ; distinguer annulation du job et abandon du brouillon |
| Version créée, recalcul échoué | référence créée mais chiffres marqués « À recalculer », reprise proposée |

Les erreurs critiques restent dans la carte concernée. Un toast sert aux confirmations secondaires, jamais comme unique trace d’un blocage financier.

### 24.9 Transitions, volets et focus

- Une navigation joue un fondu et une translation courte, environ 180 à 380 ms avec `--ease-ios`, sans écran blanc intermédiaire.
- L’élément choisi peut s’élever de quelques pixels ; pas de zoom spectaculaire sur les chiffres.
- Un volet arrive comme une plaque de verre détachée. Le fond est assombri/flouté localement et devient inerte au clavier.
- À l’ouverture, le focus va au titre ou au premier contrôle utile ; à la fermeture, il revient au déclencheur.
- `Échap` ferme un volet non bloquant. Une tâche déjà reçue par le moteur continue et reste retrouvable.
- Les titres de page, le focus principal et le retour en haut gérés par `AppShell` sont conservés.
- Avec `prefers-reduced-motion`, transitions et compagnon deviennent instantanés.
- Avec `prefers-reduced-transparency` ou sans `backdrop-filter`, les surfaces deviennent opaques avec un contraste équivalent, sans perdre de bord ni de hiérarchie.
- L’animation d’arrivée actuelle `.route-stage` dure 460 ms. Elle peut être conservée si elle reste fluide ; les micro-interactions de contrôles restent plus courtes, généralement entre 180 et 380 ms.

### 24.10 Responsive et accessibilité

Vérifier systématiquement 1440, 1024, 768, 390 et 320 px, puis zoom navigateur 200 % :

- aucune superposition ne masque contenu, focus ou bouton ;
- les superpositions fortes sont réservées aux grands écrans, actuellement le plus souvent à partir de 1280 px ; entre 768 et 1279 px, les compositions restent principalement linéaires ; sous 768 px, utiliser des cartes linéaires ou un carrousel `scroll-snap` avec aperçu de la carte suivante ;
- la grille expert reste soit lisible avec défilement annoncé, soit en lecture seule sur téléphone ;
- aucun défilement horizontal de page n’est admis ; seule la grille experte peut défiler dans un conteneur explicitement annoncé ;
- le menu, le compagnon, les toasts, les pieds de volet et les commandes d’installation ne se chevauchent pas ;
- les espacements bas tiennent compte de `env(safe-area-inset-bottom)` sur mobile ;
- zones tactiles de 44 px minimum ; focus visible de 3 px ; ordre DOM logique ;
- état actif annoncé autrement que par la couleur ;
- icônes décoratives masquées aux lecteurs d’écran, boutons icône nommés ;
- info-bulles et alertes accessibles au clavier ;
- contrastes vérifiés pour chacune des trois palettes et pour chaque état ;
- cartes arrière masquées retirées de l’ordre de tabulation.
- sous 360 px, les sélecteurs et groupes de métriques repassent en une colonne ; le zoom 200 % doit déclencher le même type de repli ;
- la zone principale conserve un lien d’évitement et expose l’état courant avec `aria-current`, `aria-pressed`, `aria-busy` ou `aria-live` selon le composant ;
- les contrastes visent au minimum 4,5:1 pour le texte courant et 3:1 pour contrôles, états graphiques et focus.

### 24.11 Matrice de non-régression UX/UI

| Zone | Ce qui doit rester vrai après raccord |
|---|---|
| Accueil | une situation, une alerte compréhensible, une prochaine action directe |
| Parcours | chaque phase cliquable quand disponible ; thèmes non disponibles clairement annoncés |
| Installation | retour, continuation, sauvegarde et sortie sans perte clairement distincts |
| Ventes | on sait que l’on modifie un brouillon et non la référence |
| Impacts | chaque conséquence porte origine, horizon, niveau de confirmation et état |
| Simulations | scénario sélectionné au premier plan ; vrais points mensuels interactifs |
| Décisions | version officielle, scénario conservé et ancienne version ne se ressemblent pas |
| Suivi mensuel | réalisé et prévision visibles comme deux natures distinctes |
| Livrables | génération, progression, disponibilité et révision du document visibles |
| Expert | entrées modifiables et résultats protégés immédiatement reconnaissables |
| Compagnon | personnage cohérent, contexte courant explicite, aucune écriture parallèle |

Le fichier `REVUE_UX_UI.md` garde la trace des vérifications déjà réalisées. La présente section est le contrat de non-régression pour le futur raccord moteur.

## 25. Plan de transformation des fichiers du cockpit

Cette section ne demande pas de modifier les fichiers maintenant. Elle indique où intervenir lors de la prochaine conversation.

### 25.1 Nouveaux fichiers recommandés

```text
lib/api/client.ts             appels, erreurs, request_id, uploads
lib/api/types.ts              contrats bruts du moteur
lib/api/cockpit-gateway.ts    adaptation vers les vues du cockpit
lib/api/jobs.ts               SSE, polling et attente d’un reçu
lib/view-models/              normalisation des métriques, séries et statuts
components/cockpit/cockpit-provider.tsx
app/loading.tsx               squelette global sans chiffres fictifs
app/error.tsx                 erreur récupérable et identifiant de corrélation
app/not-found.tsx             retour sûr vers le dossier actif
```

### 25.2 Fichiers à faire évoluer

- `app/layout.tsx` : remplacer progressivement `DemoProvider` par `CockpitProvider`.
- `components/cockpit/demo-provider.tsx` : conserver temporairement comme implémentation de démonstration derrière la même interface, puis le retirer du chemin réel.
- `lib/demo.ts` : déplacer les fixtures dans un fichier explicitement démo ; supprimer calculs et impacts fictifs du mode connecté.
- chaque route : remplacer les lectures de `state` par des view-models, sans changer l’UI lors du premier raccord.
- `CashCurve` : recevoir uniquement des points moteur ou une fixture explicitement marquée.
- `ImpactSheet` : charger un aperçu lié au brouillon.
- `CopilotSheet` : brancher chat, jobs et propositions.

### 25.3 Fichiers moteur probablement à ajouter ou compléter

- `tca_bp/cockpit_api.py` : vues agrégées et orchestration, installée depuis `web_server.py` ;
- `tca_bp/contracts_api.py` : façade sémantique pour les contrats et traduction vers les registres ;
- `tca_bp/simulation_service.py` : copie, application isolée, recalcul et résultat de scénario depuis brouillon ;
- `tca_bp/rules_api.py` : catalogue versionné de recettes homologuées et propositions contrôlées ;
- tests de cette façade dans `tests/test_cockpit_api.py` ;
- éventuellement un stockage léger des préférences visuelles, séparé de la finance.

Le nouvel adaptateur doit appeler les services existants. Il ne doit pas éditer le XLSM directement.

## 26. Ordre d’implémentation recommandé

Cette section décrit les lots de raccord moteur de l’audit initial. L’ordre global de reprise est maintenant défini par les lots F0 à F5 puis C0 à C5 du [plan de suite](PLAN_SUITE_FRONT_ET_CABLAGE.md). Pour une mission front uniquement, terminer les parcours avec des données fictives sans connecter le moteur. Si la mission inclut expressément le raccord, la lecture seule peut commencer après le socle commun et le premier module Ventes peut être connecté une fois son parcours complet, sans attendre 33 vues métier sur mesure.

L’explorateur de feuilles et les droits de grille sont préparés dès F1, puis raccordés avec les modules concernés. Seuls l’approfondissement de la grille et le compagnon réel restent dans le lot 8 ci-dessous.

### Lot 0 : connexion sans mutation

- lancer le moteur sur un stockage de test ;
- ajouter le proxy `/api` ;
- lire `/health`, `/cases` et un dossier ;
- afficher hors ligne/reconnexion ;
- garder le mode démo séparé par configuration explicite.

Critère : aucune donnée fictive ne se mélange aux données moteur.

### Lot 1 : cockpit en lecture seule

- référence active ;
- métriques qualifiées ;
- vraie série `cash` ;
- versions ;
- statut de calcul ;
- livrables existants.

Critère : Accueil, Décisions et Livrables lisent une même révision.

### Lot 2 : installation et sources

- création du dossier ;
- profil ;
- upload ;
- extraction ;
- faits à confirmer ;
- proposition au brouillon.

Critère : aucune extraction n’est automatiquement considérée comme confirmée.

### Lot 3 : contrat Atlas en brouillon

- charger le registre `DATA Contrats` ;
- résoudre le mapping Atlas ;
- exiger une source ;
- préparer le record ;
- lire les questions et conflits ;
- abandonner le brouillon.

Critère : aucune adresse Excel n’est codée dans la page et aucune formule n’est modifiée.

### Lot 4 : impacts, aperçu et simulation

- aperçu réel ;
- vue d’impacts ;
- orchestration de copie ;
- recalcul ;
- comparaison avec vraies séries.

Critère : modifier le brouillon rend immédiatement l’ancienne simulation périmée.

### Lot 5 : conserver, adopter et restaurer

- scénarios nommés ;
- adoption sûre ;
- journal ;
- versions ;
- restauration asynchrone.

Critère : aucune action ne supprime une version ; un double clic ne double pas une application.

### Lot 6 : réalisé mensuel

- fichier, mapping, aperçu, adoption ;
- écarts ;
- reforecast ;
- nouvelle décision.

Critère : budget, réalisé et prévision actualisée restent trois objets séparés.

### Lot 7 : livrables

- génération ;
- suivi de job ;
- téléchargement ;
- aller-retour Excel contrôlé.

### Lot 8 : compagnon et approfondissement expert

- chat réel ;
- contexte de page ;
- propositions vers le même brouillon ;
- grille sécurisée ;
- outils de contexte de modèle réécrits.

## 27. Tests de raccord indispensables

### 27.1 Contrats et calcul

- 20 % UI devient bien 0,20 moteur.
- Montant, quantité et prix ne sont jamais confondus.
- Quatre mois produit des dates valides et la bonne convention de fin.
- `Etalee sur la duree` change la reconnaissance, pas la facturation.
- Acompte + jalon ne dépasse pas 100 %.
- Statut probable et pondération restent distincts.
- Changer `offer_payment_days` annonce les autres contrats touchés.

### 27.2 Brouillon et référence

- modifier ne touche jamais la référence ;
- aperçu lié à la bonne révision ;
- résultat périmé après modification ;
- double envoi idempotent ;
- conflit de révision visible ;
- application seulement avec jeton valide ;
- restauration crée une nouvelle version.

### 27.3 Scénarios

- la copie a la même empreinte de départ ;
- les opérations simulées sont exactement celles du candidat ;
- la référence ne change pas pendant le recalcul de la copie ;
- scénario échoué ne montre pas de métriques anciennes ;
- comparaison aligne les périodes et signale hors période/manquant.

### 27.4 Sources et réalisé

- source obligatoire pour une entrée métier ;
- fichier altéré refusé ;
- import > 50 Mio refusé ;
- mapping ambigu demandé ;
- encodage CSV explicite ;
- réalisé absent n’est pas zéro ;
- reforecast ne remplace pas la référence silencieusement.

### 27.5 UX et accessibilité

- clavier, focus et historique navigateur conservés ;
- pas de navigation avant succès ;
- erreurs lisibles et saisies conservées ;
- progression de job annoncée ;
- mobile en lecture seule pour la grille complexe ;
- courbes avec valeur mensuelle accessible ;
- réduction des animations ;
- zoom 200 % ;
- aucun contenu moteur masqué sous une carte superposée.

Recette visuelle minimale : les dix routes à 1440, 1024, 768, 390 et 320 px, avec les trois palettes, flou présent puis indisponible, réduction des animations, réduction de transparence et zoom 200 %. Sur les routes raccordées, rejouer au moins les états vide, chargement, calcul en cours, résultat frais, résultat périmé, erreur, conflit et hors ligne. Conserver des captures de référence pour détecter les régressions de profondeur, de contraste, de débordement et de chevauchement.

Pour les interactions : parcours intégral au clavier, survol et focus des graphiques, glisser/toucher sur mobile, lecteur d’écran NVDA ou VoiceOver, ordre du focus dans les volets, fermeture par `Échap` et restitution du focus au déclencheur. Les essais iPhone/Safari réel et lecteur d’écran vocal restent à faire même si les contrôles navigateur sont passants.

### 27.6 Non-régression

- tests moteur existants ;
- tests API existants ;
- tests d’état du prototype en mode démo ;
- nouveaux tests d’intégration du gateway ;
- parcours navigateur avec stockage moteur de test séparé ;
- vérification qu’aucun fichier du front historique n’est modifié par erreur.

## 28. Décisions ouvertes à prendre explicitement

La première rédaction réunissait décisions acquises et questions futures. Le [plan de suite, section 9](PLAN_SUITE_FRONT_ET_CABLAGE.md#9-choix-déjà-retenus-et-décisions-encore-nécessaires), les sépare pour éviter un questionnaire bloquant inutile.

Déjà retenu : prototype et premier raccord locaux, dirigeant autonome pour adopter/restaurer, compagnon qui prépare et simule sans adoption silencieuse, vues métier avec détail expert facultatif, persistance locale de l’identité et des préférences. Les cinq thèmes manquants doivent avoir un espace utilisable. Les choix de cloud, de multi-entreprise et de stockage distant ne bloquent pas cette phase.

À résoudre avant les écritures ou affichages réels concernés :

1. Le délai reste-t-il partagé par offre, en montrant les contrats affectés, ou une extension distincte du modèle est-elle demandée ? Ne pas supposer une condition propre à Atlas.
2. Quelle offre, unité, quantité, prix et TVA correspondent au contrat ? Ne pas convertir silencieusement le montant global.
3. Quelles dates exactes, règle de reconnaissance, modalités de facturation, probabilité et sources confirmées doivent être utilisées ?
4. Quel sens et quelle unité portent revenu, marge et visibilité de trésorerie ? Une métrique non qualifiée ne doit pas être présentée comme fiable.
5. Le dossier moteur de test et le recalcul Excel sont-ils disponibles pour vérifier les simulations réelles ?

Les formats d’import doivent suivre les API existantes, avec conversion des anciens `.xls` seulement si elle est demandée. Les détails des autres thèmes sont précisés avant leur propre raccord. Une question locale à un champ ne bloque ni la consultation des feuilles ni les autres travaux indépendants.

## 29. Invariants non négociables

1. Le navigateur n’est jamais la source de vérité financière.
2. Brouillon, simulation, scénario conservé et référence sont des objets distincts.
3. Une modification invalide tout calcul construit sur l’ancienne empreinte.
4. Une simulation référence exactement modèle, révision, opérations et sources.
5. Conserver un scénario ne modifie pas la référence.
6. Adopter et restaurer créent toujours une nouvelle version.
7. Aucune ancienne version n’est écrasée.
8. Les notifications de succès suivent le reçu moteur.
9. Le compagnon propose ; le dirigeant confirme la référence.
10. Les formules centrales n’ont aucun chemin d’écriture ordinaire.
11. Les valeurs absentes ne deviennent jamais zéro.
12. Une valeur calculée en cache n’est pas un résultat frais.
13. Chaque résultat porte période, unité, statut et révision.
14. Chaque écriture est sourcée, révisée, idempotente et auditée.
15. Signé, probable, reconnu, facturé, encaissé et réalisé ne sont jamais fusionnés.

## 30. Critères de fin du raccord

Le cockpit sera réellement câblé lorsque :

- toutes les valeurs financières visibles proviennent d’un dossier et d’une révision identifiés ;
- aucune fixture ne peut apparaître en mode connecté ;
- le contrat est préparé via le registre et le catalogue ;
- Impacts et Simulation portent la même empreinte ;
- les vraies séries mensuelles alimentent les courbes ;
- conserver, adopter et restaurer utilisent les transactions moteur ;
- le réalisé suit lecture, mapping, aperçu et confirmation ;
- les livrables sont réellement générés et liés à la référence ;
- le compagnon passe par le brouillon partagé ;
- toutes les erreurs et reprises sont compréhensibles ;
- les tests de concurrence, idempotence, versions et protections passent ;
- l’interface conserve son niveau UX/UI premium sans cacher la traçabilité.

## 31. Consigne de reprise pour la prochaine conversation

Commencer par [PLAN_SUITE_FRONT_ET_CABLAGE.md](PLAN_SUITE_FRONT_ET_CABLAGE.md), puis lire cette passation. La consigne prête à transmettre figure à la section 13 du plan. Ensuite :

1. vérifier l’état réel de `visuel web test`, `frontend/src/api.ts`, `tca_bp/web_server.py`, `tca_bp/decision_api.py` et `tca_bp/decision_model.py` ;
2. ne modifier aucun calcul financier dans React ;
3. ne réécrire aucun service moteur déjà existant ;
4. commencer par les lots front F0, F1 et F2 ; ne lancer les lots moteur que si la nouvelle mission inclut expressément le raccord ;
5. garder le mode démonstration explicitement séparé ;
6. résoudre uniquement les décisions encore ouvertes qui conditionnent les écritures concernées, sans redemander les choix déjà retenus ;
7. vérifier chaque lot avec un stockage de test séparé ;
8. ne toucher au front historique que si la mission le demande explicitement.

Documents complémentaires à consulter :

- `REVUE_UX_UI.md` dans ce dossier ;
- `../docs/ATELIER_WEB.md` ;
- `../docs/ARCHITECTURE.md` ;
- `../docs/INTERFACE.md` ;
- `../feuilles/agent_05.md` pour `DATA Contrats` ;
- `../feuilles/agent_04.md` pour les offres ;
- `../docs/RECETTE_WEB.md` ;
- `../docs/QUALIFICATIONS.md`.

## 32. Vérification ayant servi à cette passation

L’audit a lu les dix routes, les composants transversaux, le provider, les types, les tests du prototype, le client API historique, les routes FastAPI et les documents métier du moteur.

Les contrôles ont été relancés après rédaction de cette passation :

- `node --test tests/demo-state.test.mjs` : 10 réussis, 0 échec ;
- `pnpm exec tsc --noEmit` : réussi ;
- `pnpm exec oxlint app components/cockpit lib tests/demo-state.test.mjs` : réussi ;
- `pnpm run build` : réussi, avec les dix routes inventoriées dans ce document.

Les dix tests d’état couvrent notamment : règle idempotente, simulation fraîche obligatoire, application unique, quatre variantes conservées, restauration, undo, valeurs invalides, recommandation atomique et import mensuel isolé.

Limite de ces tests : ils ne démarrent pas le moteur, Excel, les appels réseau, la concurrence ni les permissions. Ils valident le comportement de démonstration, pas encore le raccord.
