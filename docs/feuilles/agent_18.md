# Financement E&S

Responsabilité : **Expliquer les agrégats d'apports et leurs décalages.**

Contrat : `AGENT_18`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Faut-il décaler une opération identifiée ou appliquer un scénario aux apports ?

## Règles et contrôles métier

- Vérifier les dates après décalage.
- Une date de consultation ne crée pas d'apport.

## Dépendances

Sources métier du contrat : DATA Financement, Sensi TCA.

Sources directes extraites : Assumptions, DATA Financement, Modèle financier, Sensi TCA.

Feuilles qui consomment directement cette feuille : CALCUL_CIR, Contrôles, DATA Financement, Modèle financier, Valorisation.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Décalage en mois par catégorie

Identifiant : `financement_e_s_j3_j17`. Type : `integer`. Zones : `J3:J17`.

Unité explicite : mois calendaires.

Assiette : Décalage des dates de financement, sans changer le montant acquis.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_e14_e413, active_scenario.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["J3", "J4", "J5", "J6", "J7", "J8", "J9", "J10", "J11", "J12", "J13", "J14", "J15", "J16", "J17"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"whole": true}, "choices": null}`.

Contraintes : `{"whole": true}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `J3` : `'Sensi TCA'!$C$14`
- `J4` : `'Sensi TCA'!$C$14`
- `J5` : `'Sensi TCA'!$C$14`
- `J6` : `'Sensi TCA'!$C$14`
- `J7` : `'Sensi TCA'!$C$14`
- `J8` : `'Sensi TCA'!$C$14`
- `J9` : `'Sensi TCA'!$C$14`
- `J10` : `'Sensi TCA'!$C$14`
- `J11` : `'Sensi TCA'!$C$14`
- `J12` : `'Sensi TCA'!$C$14`
- `J13` : `'Sensi TCA'!$C$14`
- `J14` : `'Sensi TCA'!$C$14`
- `J15` : `'Sensi TCA'!$C$14`
- `J16` : `'Sensi TCA'!$C$14`
- `J17` : `'Sensi TCA'!$C$14`

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Equity — `Financement E&S!M20`

Unité : EUR/an. Ventilation des catégories Equity.

```text
SUMIF($C$3:$C$17,"Equity",M$3:M$17)
```

Sources directes extraites : `'Financement E&S'!$C$3:$C$17`, `'Financement E&S'!M$3:M$17`.

### Comptes courants — `Financement E&S!M21`

Unité : EUR/an. Ventilation des CCA sans les confondre avec capital.

```text
SUMIF($C$3:$C$17,"Compte courant",M$3:M$17)
```

Sources directes extraites : `'Financement E&S'!$C$3:$C$17`, `'Financement E&S'!M$3:M$17`.

### Aides d’exploitation — `Financement E&S!M22`

Unité : EUR/an. Aides datées distinctes des ventes.

```text
SUMIF($C$3:$C$17,"Subvention exploitation",M$3:M$17)
```

Sources directes extraites : `'Financement E&S'!$C$3:$C$17`, `'Financement E&S'!M$3:M$17`.

### Total ventilé — `Financement E&S!M23`

Unité : EUR/an. Rapprochement du total avec le registre et le scénario.

```text
SUM(M20:M22)
```

Sources directes extraites : `'Financement E&S'!M20:M22`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_18 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Equity 50 000, CCA 10 000 et aide d’exploitation 5 000 sur le même exercice.

Attendu : Ventilations 50 000/10 000/5 000, total 65 000 ; un décalage de scénario change les dates, pas le total acquis.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
