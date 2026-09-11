# Qualification des données et disponibilité des résultats

Le calcul Excel et la qualification documentaire ont deux états séparés. `outputs_current` indique que les caches proviennent d’un recalcul de la copie reconnue, avec les entrées conservées. `qualified_availability` indique, pour CA, COGS, CASH, FISCALITE et DCF, si les conditions sources prévues sont réunies. Ces conditions ne constituent pas une certification économique ni une revue juridique automatique.

| État constaté | Effet |
|---|---|
| Donnée absente | Information à demander ; aucun zéro implicite |
| Valeur héritée sans état documentaire | Valeur non qualifiée |
| Texte « À confirmer » non vide | Décision manquante, même avec un statut documentaire CONFIRME |
| HYPOTHESE et source intacte | Scénario provisoire ; `scenario_ready` peut être vrai, `available` reste faux |
| CONFIRME, source intacte et valeur concordante | Condition documentaire satisfaite |
| État enregistré différent de la valeur réelle | État périmé ; nouvelle qualification nécessaire |
| INACTIF sur une valeur scalaire | Ne neutralise jamais sa contribution Excel |
| Module INACTIF confirmé et sourcé | Applicable uniquement en l’absence d’activité contradictoire |
| Défaut calculé reconnu | Exception limitée aux défauts explicites de registres/prix ; jamais pour confirmer un paramètre fiscal propriétaire |

Les états d’une cellule proviennent des lots de saisie existants : valeur, statut, justification et identifiant de source. Une source appartient au dossier et son empreinte est vérifiée. Son contenu est lu comme des données ; il ne peut modifier les permissions ou les règles de qualification.

Une déclaration de périmètre s’enregistre avec `Application.declare_qualification(case_id, declaration)`. Le contrat accepte `module`, `state` ACTIF/INACTIF, `status` CONFIRME/HYPOTHESE, `evidence` identifiant de source et `reason`. Modules : CA, COGS, STOCK, CIR, REGLES_FISCALES, BFR_TERMINAL, DATA Contrats, Effectifs, DATA CAPEX, DATA Financement, Financement Dette et SUBVENTION_INVEST. Déclarer un module n’écrit aucune cellule. L’évaluation explicite suivante, `Application.qualifications(case_id)`, détecte notamment les contradictions avec une ligne de registre ou un stock existant.

REGLES_FISCALES requiert aussi `jurisdiction`, `valid_from` et `valid_to` au format ISO. La période doit couvrir tous les exercices actifs. Le service lie cette déclaration à la version exacte du modèle et à sa trame. Elle atteste une revue externe sourcée, sans inventer une loi, un taux ou une éligibilité. Une nouvelle version de modèle ne réutilise pas implicitement cette revue.

Les gardes inspectent les valeurs propriétaires réelles : calendrier Control C10/C59 ; activation, quantités, prix, capacités et paiements des offres ; méthodes COGS ; registres actifs ; charges externes ; ouvertures Control C28:C34 ; fiscalité Assumptions D77:D79 et D83:D88 ; conditions IS et CVAE ATELIER_CIR_IS lignes 66 et 85, loyers/valeur locative CFE lignes 89/91, CA de groupe lignes 110/111 et ouverture C93 ; TVA des offres/contrats et paramètres D160:D166. Le CIR actif requiert les hypothèses Assumptions D68:D76 et les montants/qualifications annuels CALCUL_CIR lignes 18, 19, 41, 42 et 43. Les données et la part R&D des registres déterminent son activité, pas le nom de l’entreprise. Les durées et parts R&D par défaut d’un CAPEX remontent aux cellules du catalogue sélectionné : une formule de recherche reconnue ne qualifie pas une valeur de catalogue absente.

Pour le DCF, le taux normatif provient de Valorisation D9. Un zéro calculé dans D115 ne le remplace pas. Croissance, mode WACC, taux ou paramètres de marché et comparables sont qualifiés selon le mode. Le closing D15 est calculé : les dates propriétaires sont demandées dans DATA Financement, pour la catégorie technique relayée par Assumptions B134. Le mode Itération requiert en plus une preuve de convergence liée à la copie et à la signature des entrées. La déclaration BFR_TERMINAL rend explicite la revue de la normalisation terminale ; après recalcul, le diagnostic réel BFR E49 doit aussi valider cette normalisation. La qualification DCF ne certifie pas les autres hypothèses de la méthode VC.

Le scénario Central et les chocs techniques nuls constituent le point neutre explicite du modèle. Une modification, une valeur absente ou un état documentaire enregistré sur ces commandes est qualifié selon le périmètre affecté. Le scénario Manuel demande les chocs propriétaires. Les résultats des tables de sensibilité attendent leur preuve native spécifique.

Les erreurs natives sont comptées intégralement par périmètre. Les rectangles annuels documentés hors horizon sont exclus des blocages actifs, en conservant leur nombre et les détails bruts. Une adresse dont l’horizon n’est pas reconnu reste active par prudence. Une erreur DCF bloque DCF ; elle ne bloque pas CA. Un ancien reçu tronqué dépourvu d’attribution complète nécessite un nouveau recalcul pour attribuer les erreurs sans supposer leur innocuité.

Les reçus de qualification sont enregistrés dans les rapports privés du dossier. L’historique conserve leur chemin, leur empreinte et l’empreinte de leurs conditions : dossier, client, version exacte, classeur, états, déclarations, sources et reçu du calcul. Une modification de l’une de ces conditions invalide la disponibilité. Les questions sont regroupées par champ métier avec les cellules et les périmètres concernés. Les lectures `get_case` ne relancent pas une analyse Excel complète.

`Application.inspect` conserve les valeurs d’entrée et les formules consultables. Une sortie calculée indisponible est renvoyée avec `current.value=null`, `value_withheld=true` et son périmètre de qualification. Les fichiers Excel de consultation peuvent encore montrer leurs caches : ces gardes d’application ne réécrivent pas rétroactivement les formules. La vérification indépendante des tables natives, de WACC et des oracles financiers reste distincte.

Tests logiciels : `tests/test_qualifications.py` vérifie les règles de statut et de dépendance. `tests/test_qualification_service.py` parcourt saisie sourcée, déclaration, persistance, recalcul **simulé sans Excel**, consultation gardée et invalidation. Les taux de ses fixtures sont des nombres arbitraires destinés au test logiciel, sans valeur fiscale. Un test logiciel positif ne constitue pas une recette native financière.
