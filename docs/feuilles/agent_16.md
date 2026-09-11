# Financement Dette

Responsabilité : **Préparer les dettes, tirages, durées, taux et remboursements.**

Contrat : `AGENT_16`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel nominal, taux annuel, durée et mode de remboursement ?
- Quelle date de tirage et quel différé explicite, éventuellement nul ?

## Règles et contrôles métier

- Différé cohérent avec la durée.
- Rapprocher tirage, capital remboursé et dette finale.

## Dépendances

Sources métier du contrat : Control.

Sources directes extraites : Modèle financier.

Feuilles qui consomment directement cette feuille : CALCUL_CIR, Contrôles, Modèle financier.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Nom du financement

Identifiant : `financement_dette_b3_b42`. Type : `text`. Zones : `B3:B42`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité de l’emprunt.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32", "B33", "B34", "B35", "B36", "B37", "B38", "B39", "B40", "B41", "B42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Nominal euros

Identifiant : `financement_dette_c3_c42`. Type : `number`. Zones : `C3:C42`.

Unité explicite : EUR.

Assiette : Principal tiré ; intérêts distincts du remboursement du capital.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Taux annuel

Identifiant : `financement_dette_d3_d42`. Type : `number`. Zones : `D3:D42`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel contractuel de dette ; zéro doit être explicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : financement_dette_c3_c42.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32", "D33", "D34", "D35", "D36", "D37", "D38", "D39", "D40", "D41", "D42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

### Durée en années

Identifiant : `financement_dette_e3_e42`. Type : `number`. Zones : `E3:E42`.

Unité explicite : années ; conversion en mois selon la règle du modèle.

Assiette : Durée totale ou différé ; différé borné par la durée et conversion en mois.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : financement_dette_i3_i42, financement_dette_f3_f42.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40", "E41", "E42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "whole_months": "value*12 entier"}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "whole_months": "value*12 entier"}`.

### Mode de remboursement

Identifiant : `financement_dette_f3_f42`. Type : `enum`. Zones : `F3:F42`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Calendrier contractuel d’amortissement du principal.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : financement_dette_e3_e42, financement_dette_h3_h42.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "F25", "F26", "F27", "F28", "F29", "F30", "F31", "F32", "F33", "F34", "F35", "F36", "F37", "F38", "F39", "F40", "F41", "F42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Amortissement constant", "Remboursement in fine"]}`.

Choix du catalogue : ["Amortissement constant", "Remboursement in fine"].

### Différé en années

Identifiant : `financement_dette_h3_h42`. Type : `number`. Zones : `H3:H42`.

Unité explicite : années ; conversion en mois selon la règle du modèle.

Assiette : Durée totale ou différé ; différé borné par la durée et conversion en mois.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : financement_dette_i3_i42, financement_dette_f3_f42.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "whole_months": "value*12 entier", "for_constant": "H<E"}, "choices": null}`.

Contraintes : `{"min": 0, "whole_months": "value*12 entier", "for_constant": "H<E"}`.

### Date de souscription / tirage

Identifiant : `financement_dette_i3_i42`. Type : `date`. Zones : `I3:I42`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date réelle de tirage/souscription ; préplan nécessite soldes et échéanciers.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["I3", "I4", "I5", "I6", "I7", "I8", "I9", "I10", "I11", "I12", "I13", "I14", "I15", "I16", "I17", "I18", "I19", "I20", "I21", "I22", "I23", "I24", "I25", "I26", "I27", "I28", "I29", "I30", "I31", "I32", "I33", "I34", "I35", "I36", "I37", "I38", "I39", "I40", "I41", "I42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Nature du financement

Identifiant : `financement_dette_j3_j42`. Type : `enum`. Zones : `J3:J42`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Nature de la ressource ; ne change pas son montant.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["J3", "J4", "J5", "J6", "J7", "J8", "J9", "J10", "J11", "J12", "J13", "J14", "J15", "J16", "J17", "J18", "J19", "J20", "J21", "J22", "J23", "J24", "J25", "J26", "J27", "J28", "J29", "J30", "J31", "J32", "J33", "J34", "J35", "J36", "J37", "J38", "J39", "J40", "J41", "J42"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Pret bancaire", "Avance remboursable"]}`.

Choix du catalogue : ["Pret bancaire", "Avance remboursable"].

## Registre

Le coordinateur cherche une ligne libre dans le classeur courant, compare les identités déjà présentes et pose les questions manquantes avant de préparer une proposition.

```json
{
  "start_row": 3,
  "end_row": 42,
  "identity_columns": [
    "B",
    "C",
    "D",
    "E",
    "F",
    "H",
    "I",
    "J"
  ],
  "required": [
    "B",
    "C",
    "D",
    "E",
    "F",
    "I",
    "J"
  ]
}
```

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Capital remboursé — `Financement Dette!M43`

Unité : EUR/an. Calendrier de tirage, différé et mode d’amortissement.

```text
SUMPRODUCT((YEAR($X$2:$EY$2)=M$2)*$X43:$EY43)
```

Sources directes extraites : `'Financement Dette'!$X$2:$EY$2`, `'Financement Dette'!M$2`, `'Financement Dette'!$X43:$EY43`.

### Intérêts payés — `Financement Dette!M86`

Unité : EUR/an. Taux appliqué à l’assiette de dette de la période, distinct du capital.

```text
SUMPRODUCT((YEAR($X$2:$EY$2)=M$2)*$X86:$EY86)
```

Sources directes extraites : `'Financement Dette'!$X$2:$EY$2`, `'Financement Dette'!M$2`, `'Financement Dette'!$X86:$EY86`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_16 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Prêt 120 000 EUR sur 2 ans, taux confirmé zéro, amortissement constant sans différé.

Attendu : Capital 60 000 par année, intérêts 0 ; la troisième année ne crée plus de remboursement.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
