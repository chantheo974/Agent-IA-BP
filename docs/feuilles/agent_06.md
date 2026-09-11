# Contrats

Responsabilité : **Expliquer demande, capacité et reports de commandes par cohorte.**

Contrat : `AGENT_06`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel retard, quelle capacité ou quelle cohorte faut-il expliquer ?

## Règles et contrôles métier

- Demande = activité retenue + report selon les règles du modèle.
- Conserver le prix de la cohorte.

## Dépendances

Sources métier du contrat : DATA Contrats, Assumptions.

Sources directes extraites : Assumptions, Control, DATA Contrats, Revenue, Sensi TCA.

Feuilles qui consomment directement cette feuille : ATELIER_CIR_IS, COGS, Contrôles, KPI Dashboard, Revenue.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Demande retenue BP — `Contrats!E92`

Unité : EUR/an. Consolide la demande retenue dans le calendrier annuel.

```text
SUMPRODUCT(($P$5:$EE$5=E$5)*$P92:$EE92)
```

Sources directes extraites : `'Contrats'!$P$5:$EE$5`, `'Contrats'!E$5`, `'Contrats'!$P92:$EE92`.

### Carnet non livré — `Contrats!E313`

Unité : EUR fin année. Conserver la valeur d’origine des cohortes reportées.

```text
SUMIFS($P313:$EE313,$P$3:$EE$3,E$5*100+12)
```

Sources directes extraites : `'Contrats'!$P313:$EE313`, `'Contrats'!$P$3:$EE$3`, `'Contrats'!E$5`.

### Écart reconnu contre demandé — `Contrats!E64`

Unité : EUR/an. Un décalage de livraison peut créer un écart annuel sans perte de commande.

```text
Revenue!E282-E92
```

Sources directes extraites : `'Revenue'!E282`, `'Contrats'!E92`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_06 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Deux cohortes de 2 unités à 100 puis 150 EUR ; capacité de 1 unité par mois, FIFO.

Attendu : Ordre de livraison 100, 100, 150, 150 EUR ; après deux livraisons le carnet vaut 300 EUR. Vérifier aussi les quantités par mois.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
