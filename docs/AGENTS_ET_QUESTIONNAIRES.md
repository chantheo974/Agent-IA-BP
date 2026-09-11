# Agents et questionnaires métier

Le coordinateur fournit **33 contrats de responsabilité**, un par feuille du modèle. Il fonctionne en Python 3.14 avec la bibliothèque standard, sans abonnement API ni appel à un modèle distant. Les contrats JSON sont dans `agents/agent_01.json` à `agents/agent_33.json`.

Il sait orienter une demande en français, poser les questions correspondant aux champs du catalogue, préparer une ligne de registre à partir de réponses structurées, rechercher un doublon probable et soumettre la proposition au moteur. Il ne remplace pas une lecture économique ni une revue de pièce par une extraction automatique de chiffres.

## Répartition des responsabilités

1. Le **service de dossier** conserve client, dossier, sources, historique, états, identité de demande et transactions.
2. Le **coordinateur** choisit les responsables métier et construit une proposition cohérente. Il ne modifie aucun classeur.
3. Le **moteur central** fournit le catalogue, reconnaît le modèle, vérifie les valeurs et états attendus, puis applique une transaction autorisée sur une nouvelle copie.
4. Le **calcul natif Excel** actualise les formules. Les tables de sensibilité et la résolution WACC disposent de preuves distinctes.

Le routage lit `graphe_dependances.json` de la version du moteur et inverse ses liens source/consommateur pour suivre les conséquences en aval. Il traverse les cycles une seule fois et ne rajoute aucune dépendance issue des seuls contrats métier. `business_dependencies` conserve ces indications de rôle séparément. La fermeture par feuille reste conservatrice : elle ne signifie pas que toutes les cellules de chaque feuille changent. Les références dynamiques, noms et macros gardent les limites déclarées du graphe.

Si le graphe est absent, le coordinateur retourne `NEEDS_REVIEW`, avec un impact aval non déterminé. Un graphe d'une autre version ou référençant une feuille inconnue est refusé. Son empreinte est renvoyée avec les résultats ; une nouvelle version du fichier invalide l'index en mémoire.

## API utilisable depuis Codex ou la CLI du projet

```python
from tca_bp.agents import Coordinator

# engine est le ModelEngine de la version reconnue.
coordinator = Coordinator(engine)
coordinator.agents()  # 33 responsables, rôles, dépendances, contrôles, questions
coordinator.route("Ajouter un recrutement à 0,8 ETP")
coordinator.questions("Effectifs")
coordinator.explain("BFR", "E46", workbook="dossiers/mon_dossier/copie.xlsm")
```

`route()` renvoie `intent`, `sheets`, `affected_sheets`, `dependency_basis`, `graph_sha256`, les limites d'extraction, au maximum quatre premières questions, un message et `can_write=False`. Les intentions sont `input_update`, `explain`, `diagnostic` et `model_change`. Une demande de changement de formule ou structure part vers le développement versionné. Aucun mot trouvé dans une demande ne constitue une permission d'écrire une feuille entière.

`questions()` dérive les champs, choix et contraintes du catalogue du moteur. Une unité explicite du catalogue est prioritaire ; à défaut, le libellé et le type fournissent une indication à confirmer, particulièrement HT/TTC et prix unitaire/total. Les colonnes requises des registres sont prioritaires. Un champ confirmé avec la valeur **0** n'est pas redemandé simplement parce qu'il est nul. Une hypothèse reste identifiable. Le contexte facultatif peut contenir :

```json
{
  "answers": {
    "employee_fte": {"value": 0.8, "status": "CONFIRME"},
    "employee_salary": {"value": null, "status": "NON_RENSEIGNE"}
  }
}
```

Les identifiants montrés sont des identifiants de champs ; leur disponibilité exacte relève du catalogue de la version du modèle.

## Préparer un registre

Le parcours s'applique aux contrats, effectifs, investissements, financements, dettes et subventions d'investissement.

```python
result = coordinator.plan_record(
    workbook="dossiers/mon_dossier/copie.xlsm",
    sheet="DATA Contrats",
    values={
        "contract_client": {"value": "Client fictif A", "status": "CONFIRME"},
        "contract_offer": {"value": "Offre 01", "status": "CONFIRME"},
        "contract_quantity": {"value": 2, "status": "CONFIRME"},
        "contract_unit_price": {"value": 1200, "status": "HYPOTHESE"}
    },
    evidence_id="SOURCE_DU_DOSSIER"
)
```

Cet exemple volontairement incomplet **ne crée aucun contrat** : les dates, modes et autres champs requis ressortent dans `questions`. Les exemples fictifs n'alimentent pas la trame distribuée.

Le coordinateur :

- relit les places disponibles dans le classeur courant ; une ligne partielle n'est pas présumée libre ;
- mappe chaque `field_id` vers l'adresse de la ligne choisie ; un champ inconnu ou appartenant à un autre registre est refusé ;
- lit les états actuels, maintient les inconnues et préserve les défauts calculés non explicitement remplacés ;
- demande les champs requis manquants avant de valider ;
- recherche une opération existante partageant les éléments d'identité disponibles ;
- appelle `engine.prepare()` ; une règle métier refusée reste un refus ;
- retourne une proposition, jamais un classeur modifié.

| Statut | Sens | Action suivante |
|---|---|---|
| `NEEDS_INPUT` | Ligne incomplète ou remplacement de défaut non justifié | Répondre aux questions du résultat |
| `NEEDS_REVIEW` | Doublon métier probable | Examiner les lignes existantes et identifier la bonne opération |
| `REFUSED` | Registre plein, inspection incomplète ou règle moteur refusée | Résoudre la cause ; aucun contournement automatique |
| `READY` | Proposition complète validée sur le fichier lu | La présenter via le service de dossier pour validation et application |

`result["updates"]` suit le format public du service : `sheet`, `cell`, `value`, `reason`, `evidence` (identifiant de source), `status`, et éventuellement `replace_existing` / `override_default`. Les états lus sont conservés séparément dans `expected_states`. Le service reconstruit sa proposition liée à la version actuelle du dossier avant d'écrire.

Les valeurs simples, sans enveloppe explicite, portent le statut `HYPOTHESE`. Ajouter une source ne transforme pas automatiquement son contenu en donnée confirmée.

Le contrôle de doublon du coordinateur est un rapprochement conservateur, pas une identité universelle d'opération. Le service doit également gérer l'identifiant de demande et le rejeu. Deux opérations légitimement semblables doivent être distinguées avec des preuves métier, jamais en désactivant le contrôle.

## États et défauts

| État | Interprétation |
|---|---|
| `NON_RENSEIGNE` | Information absente ; aucune valeur inventée |
| `HYPOTHESE` | Valeur de travail explicite, encore à confirmer |
| `CONFIRME` | Valeur explicitement confirmée avec sa source |
| `INACTIF` | État d'un module ; refusé comme simple statut d'une valeur à écrire |
| `A_RECALCULER` | État d'un calcul après modification d'entrée |
| `VERIFIE_SUR_PERIMETRE` | Vérification d'un calcul sur une version et un périmètre précis |

Les deux derniers états qualifient un calcul, pas la certitude d'une nouvelle donnée d'entrée. Ils ne sont pas utilisés pour remplir une ligne de registre. La saisie d'un montant nul reste une vraie valeur ; `null` reste une absence. Le parcours de création d'une ligne ne réalise pas un effacement demandé ailleurs.

`INACTIF` ne neutralise pas une valeur dans Excel. Toute nouvelle saisie portant ce seul statut est refusée, même pour zéro. Pour désactiver un module, renseigner son véritable champ d'activation dans le catalogue, selon les choix du moteur, et qualifier cette décision `CONFIRME`. Un zéro explicite peut être `CONFIRME` ou `HYPOTHESE`.

Pour remplacer un défaut calculé, fournir une valeur, `override_default: true` et une raison métier spécifique. Le moteur vérifie ensuite que la formule existante est exactement l'un des défauts autorisés. Une formule de calcul ne devient pas modifiable parce que son explication est comprise.

## Pièces jointes et propositions JSON

```python
source = coordinator.intake_source("SOURCE_1", texte_document, title="Devis reçu")
```

Cette méthode renvoie des extraits numérotés à qualifier, sans changement de cellule. Les lignes ressemblant à des instructions sont signalées comme contenu documentaire. Même si aucune ligne suspecte n'est reconnue, **aucun contenu documentaire n'est exécuté**. Le détecteur n'est pas une preuve qu'une pièce est sûre.

`route(texte_document, source_type="document")` retourne `source_review`, sans feuille ni action de saisie. Le routage d'une opération exige une demande utilisateur distincte.

Une proposition de registre peut être enregistrée en JSON et réimportée :

```json
{
  "schema": "tca-bp-record-proposal/1",
  "model_id": "IDENTIFIANT_RETOURNE_PAR_LE_MOTEUR",
  "intent": "input_update",
  "sheet": "DATA Contrats",
  "values": {
    "contract_client": {"value": "Client fictif A", "status": "CONFIRME"}
  },
  "evidence_id": "SOURCE_DU_DOSSIER"
}
```

`import_record_proposal(workbook, proposal)` refuse les clés inconnues, un autre modèle et les intentions de modification structurelle. Ce format transporte les réponses métier. L'identité client, le dossier, l'autorisation, la validité de la source et la clé de rejeu restent vérifiés par le service du dossier.

## Explications et fraîcheur des résultats

`explain()` expose les dépendances entrantes et sortantes extraites, le rôle et les **calculs clés effectivement lus** dans le classeur demandé. Par exemple, le compte de résultat sélectionne D7 (CA), D69 (EBE), D72 (résultat d'exploitation) et D85 (résultat net). Chaque ancre comprend son unité, sa règle métier, la formule lue et les références du graphe uniquement si l'empreinte de cette formule concorde. Une formule remplacée ou non inspectée ne conserve pas des dépendances prétendument vérifiées. Une valeur en cache reste non certifiée.

Les 33 [fiches de feuille](feuilles/README.md) reprennent ces sélections, les défauts autorisés et les séries XML des graphiques effectivement attachés. Leurs `test_cases` spécifient des données fictives et des attentes indépendantes propres à la feuille, avec le statut `SPECIFICATION_NON_EXECUTEE`. Les cas ne sont ni exécutés ni considérés comme des reçus natifs par la génération des fiches. Une modification de modèle exige de régénérer les fiches contre la nouvelle empreinte et de rejouer les scénarios concernés.

Une preuve complète passée au coordinateur doit contenir `verified=True`, `completed=True`, `inputs_match=True`, `evidence_id`, `sheets` et `workbook_sha256`. L'empreinte doit correspondre au fichier actuellement lu, et la feuille doit appartenir au périmètre vérifié. Sinon `result_claims_allowed` reste `False`.

Un simple retour Excel `RECALCULE` ne suffit pas à confirmer les hypothèses économiques ou toutes les sorties. Le service conserve séparément les statuts des sensibilités et de la macro WACC. Aucun taux ou résultat financier n'est inventé par le coordinateur.

## Propositions concordantes et conflits

Le [parcours de réconciliation](PROPOSITIONS_ET_CONFLITS.md) expose `merge_proposals`, la préparation centrale d’un lot multiagents, les contrôles de version sous verrou et les questions d’arbitrage. Une contradiction suspend le lot concerné ; aucune partie du lot n’est écrite automatiquement. CLI : `prepare-agent-proposals`. MCP : `bp_prepare_agent_proposals`.

## Validation des agents

Exécuter les tests ciblés sans Excel ni données client :

```text
py -3.14 -m unittest tests.test_agents tests.test_agent_graph_knowledge tests.test_agent_proposals -v
```

Ils vérifient notamment : les 33 contrats et leurs spécifications, le sens des dépendances extraites, les cycles, l'absence de graphe, la mauvaise version, l'actualisation de l'index et les empreintes des formules métier. Les ancrages et les quatre graphiques sont contrôlés statiquement sur la trame locale lorsqu'elle est présente. Ils couvrent aussi le routage français, les pièces traitées comme données, le zéro confirmé, les inconnues, la ligne libre, le défaut justifié, les doublons, les refus et la fraîcheur. Ces tests logiciels n'exécutent pas les 33 scénarios financiers dans Excel.
