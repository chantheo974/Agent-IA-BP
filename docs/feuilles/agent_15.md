# CAPEX

Responsabilité : **Expliquer décaissements, amortissements, VNC et loyers.**

Contrat : `AGENT_15`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel actif et quelle période faut-il rapprocher ?

## Règles et contrôles métier

- Distinguer fin du bail et fin d'utilisation.
- Éviter les doubles comptes cash, intérêts et amortissements.

## Dépendances

Sources métier du contrat : DATA CAPEX.

Sources directes extraites : Control, DATA CAPEX, Sensi TCA.

Feuilles qui consomment directement cette feuille : Bilan, CALCUL_CIR, Charges_Externes, Compte de Résultat, Contrôles, DATA CAPEX, Modèle financier, Valorisation.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

Aucun champ de saisie dans le catalogue de cette version. L'agent explique les sorties et remonte aux feuilles sources.

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Dotation annuelle — `CAPEX!P75`

Unité : EUR/an. Amortissement de l’actif et date d’exploitation.

```text
SUM(P13:P72)
```

Sources directes extraites : `'CAPEX'!P13:P72`.

### Décaissement Cash — `CAPEX!P77`

Unité : EUR/an. Seuls actifs Cash produisent le décaissement d’achat.

```text
SUMPRODUCT(($F$13:$F$72>=(P$12-YEAR(Control!$C$10))*12+1)*($F$13:$F$72<=(P$12-YEAR(Control!$C$10))*12+12)*$D$13:$D$72*$I$13:$I$72)
```

Sources directes extraites : `'CAPEX'!$F$13:$F$72`, `'CAPEX'!P$12`, `'Control'!$C$10`, `'CAPEX'!$D$13:$D$72`, `'CAPEX'!$I$13:$I$72`.

### Loyers de crédit-bail — `CAPEX!P81`

Unité : EUR/an. Bail selon durée et taux, séparé des actifs Cash.

```text
SUMPRODUCT((INT($AB$85:$FC$85/100)=P$12)*$AB$88:$FC$88)
```

Sources directes extraites : `'CAPEX'!$AB$85:$FC$85`, `'CAPEX'!P$12`, `'CAPEX'!$AB$88:$FC$88`.

### Rapprochement VNC — `CAPEX!P221`

Unité : EUR. VNC mensuelle de décembre rapprochée de la synthèse.

```text
SUMPRODUCT(($AB$85:$FC$85=P$12*100+12)*$AB$217:$FC$217)-P80
```

Sources directes extraites : `'CAPEX'!$AB$85:$FC$85`, `'CAPEX'!P$12`, `'CAPEX'!$AB$217:$FC$217`, `'CAPEX'!P80`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_15 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Actif Cash 12 000 EUR au 1er janvier, durée 3 ans, aucun autre actif.

Attendu : P77 vaut 12 000, P75 vaut 4 000 et P81 vaut 0. Le bail nécessite un cas distinct avec fin des loyers.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
