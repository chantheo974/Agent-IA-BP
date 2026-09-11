# DATA CAPEX

Responsabilité : **Préparer les investissements et qualifier achat, bail, nature et R&D.**

Contrat : `AGENT_14`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel actif, quel montant HT, quelle typologie et quelle date d'acquisition ?
- Achat décaissé ou crédit-bail confirmé ?
- Quelle nature et quelle affectation R&D sont documentées ?
- Pour un bail : durée, taux, entretien, assurance et fin d'exploitation ?

## Règles et contrôles métier

- Remplacer un défaut calculé seulement avec justification.
- Ne pas créer deux actifs pour une même dépense.

## Dépendances

Sources métier du contrat : Control, Assumptions.

Sources directes extraites : Assumptions, CAPEX.

Feuilles qui consomment directement cette feuille : Bilan, CAPEX, Charges_Externes, Contrôles.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Intitulé investissement

Identifiant : `data_capex_b13_b72`. Type : `text`. Zones : `B13:B72`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité de l’investissement ; une dépense réelle ne doit pas être dupliquée.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32", "B33", "B34", "B35", "B36", "B37", "B38", "B39", "B40", "B41", "B42", "B43", "B44", "B45", "B46", "B47", "B48", "B49", "B50", "B51", "B52", "B53", "B54", "B55", "B56", "B57", "B58", "B59", "B60", "B61", "B62", "B63", "B64", "B65", "B66", "B67", "B68", "B69", "B70", "B71", "B72"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Typologie catalogue

Identifiant : `data_capex_c13_c72`. Type : `enum`. Zones : `C13:C72`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Typologie stable du catalogue CAPEX ; source des défauts de durée et quote-part.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : capex_catalog_years, capex_catalog_rd_share.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Banc d'essais technique", "Banc / moyens de qualification", "Moyens d'essais environnementaux", "Moyens d'essais mixtes recherche / production", "Instrumentation et mesure", "Équipement de laboratoire", "Prototypes et démonstrateurs immobilisés", "Véhicules / moyens d'essais", "Outillage d'intégration / présérie", "Outillage de production série", "Ligne d'intégration / production", "Machines-outils et équipements d'atelier", "Équipements de manutention et logistique", "Équipements de sécurité et contrôle d'accès", "Logiciels de conception et simulation", "Logiciels de gestion (PLM, MES, ERP)", "Informatique et infrastructure", "Serveurs et calcul haute performance", "Aménagements et installations techniques", "Mobilier et agencement"]}`.

Choix du catalogue : ["Banc d'essais technique", "Banc / moyens de qualification", "Moyens d'essais environnementaux", "Moyens d'essais mixtes recherche / production", "Instrumentation et mesure", "Équipement de laboratoire", "Prototypes et démonstrateurs immobilisés", "Véhicules / moyens d'essais", "Outillage d'intégration / présérie", "Outillage de production série", "Ligne d'intégration / production", "Machines-outils et équipements d'atelier", "Équipements de manutention et logistique", "Équipements de sécurité et contrôle d'accès", "Logiciels de conception et simulation", "Logiciels de gestion (PLM, MES, ERP)", "Informatique et infrastructure", "Serveurs et calcul haute performance", "Aménagements et installations techniques", "Mobilier et agencement"].

### Montant HT euros

Identifiant : `data_capex_d13_d72`. Type : `number`. Zones : `D13:D72`.

Unité explicite : EUR HT.

Assiette : Prix de l’actif ou montant support du bail ; ne pas doubler le cash du loyer.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_i13_i72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32", "D33", "D34", "D35", "D36", "D37", "D38", "D39", "D40", "D41", "D42", "D43", "D44", "D45", "D46", "D47", "D48", "D49", "D50", "D51", "D52", "D53", "D54", "D55", "D56", "D57", "D58", "D59", "D60", "D61", "D62", "D63", "D64", "D65", "D66", "D67", "D68", "D69", "D70", "D71", "D72"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Date acquisition / début du bail

Identifiant : `data_capex_e13_e72`. Type : `date`. Zones : `E13:E72`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Acquisition/début de bail ou dernière date d’exploitation ; bornes d’amortissement et services.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40", "E41", "E42", "E43", "E44", "E45", "E46", "E47", "E48", "E49", "E50", "E51", "E52", "E53", "E54", "E55", "E56", "E57", "E58", "E59", "E60", "E61", "E62", "E63", "E64", "E65", "E66", "E67", "E68", "E69", "E70", "E71", "E72"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Affectation R&D

Identifiant : `data_capex_g13_g72`. Type : `enum`. Zones : `G13:G72`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Affectation R&D de l’actif ; qualification fiscale distincte.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_h13_h72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["G13", "G14", "G15", "G16", "G17", "G18", "G19", "G20", "G21", "G22", "G23", "G24", "G25", "G26", "G27", "G28", "G29", "G30", "G31", "G32", "G33", "G34", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42", "G43", "G44", "G45", "G46", "G47", "G48", "G49", "G50", "G51", "G52", "G53", "G54", "G55", "G56", "G57", "G58", "G59", "G60", "G61", "G62", "G63", "G64", "G65", "G66", "G67", "G68", "G69", "G70", "G71", "G72"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non"]}`.

Choix du catalogue : ["Oui", "Non"].

### Mode de financement

Identifiant : `data_capex_i13_i72`. Type : `enum`. Zones : `I13:I72`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Cash ou crédit-bail : pilotes de décaissement et charge distincts.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["I13", "I14", "I15", "I16", "I17", "I18", "I19", "I20", "I21", "I22", "I23", "I24", "I25", "I26", "I27", "I28", "I29", "I30", "I31", "I32", "I33", "I34", "I35", "I36", "I37", "I38", "I39", "I40", "I41", "I42", "I43", "I44", "I45", "I46", "I47", "I48", "I49", "I50", "I51", "I52", "I53", "I54", "I55", "I56", "I57", "I58", "I59", "I60", "I61", "I62", "I63", "I64", "I65", "I66", "I67", "I68", "I69", "I70", "I71", "I72"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Cash", "Crédit-bail"]}`.

Choix du catalogue : ["Cash", "Crédit-bail"].

### Durée amortissement en années

Identifiant : `data_capex_f13_f72`. Type : `number`. Zones : `F13:F72`.

Unité explicite : années ; conversion en mois selon la règle du modèle.

Assiette : Durée d’amortissement ; un défaut de typologie doit rester explicite et remplaçable seulement sur justification.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_c13_c72, data_capex_e13_e72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "F25", "F26", "F27", "F28", "F29", "F30", "F31", "F32", "F33", "F34", "F35", "F36", "F37", "F38", "F39", "F40", "F41", "F42", "F43", "F44", "F45", "F46", "F47", "F48", "F49", "F50", "F51", "F52", "F53", "F54", "F55", "F56", "F57", "F58", "F59", "F60", "F61", "F62", "F63", "F64", "F65", "F66", "F67", "F68", "F69", "F70", "F71", "F72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `F13` : `IF($C13="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C13,Assumptions!$B$98:$B$121,0)),""))`
  Sources extraites : 'DATA CAPEX'!$C13, 'Assumptions'!$C$98:$C$121, 'Assumptions'!$B$98:$B$121.
- `F14` : `IF($C14="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C14,Assumptions!$B$98:$B$121,0)),""))`
- `F15` : `IF($C15="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C15,Assumptions!$B$98:$B$121,0)),""))`
- `F16` : `IF($C16="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C16,Assumptions!$B$98:$B$121,0)),""))`
- `F17` : `IF($C17="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C17,Assumptions!$B$98:$B$121,0)),""))`
- `F18` : `IF($C18="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C18,Assumptions!$B$98:$B$121,0)),""))`
- `F19` : `IF($C19="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C19,Assumptions!$B$98:$B$121,0)),""))`
- `F20` : `IF($C20="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C20,Assumptions!$B$98:$B$121,0)),""))`
- `F21` : `IF($C21="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C21,Assumptions!$B$98:$B$121,0)),""))`
- `F22` : `IF($C22="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C22,Assumptions!$B$98:$B$121,0)),""))`
- `F23` : `IF($C23="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C23,Assumptions!$B$98:$B$121,0)),""))`
- `F24` : `IF($C24="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C24,Assumptions!$B$98:$B$121,0)),""))`
- `F25` : `IF($C25="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C25,Assumptions!$B$98:$B$121,0)),""))`
- `F26` : `IF($C26="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C26,Assumptions!$B$98:$B$121,0)),""))`
- `F27` : `IF($C27="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C27,Assumptions!$B$98:$B$121,0)),""))`
- `F28` : `IF($C28="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C28,Assumptions!$B$98:$B$121,0)),""))`
- `F29` : `IF($C29="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C29,Assumptions!$B$98:$B$121,0)),""))`
- `F30` : `IF($C30="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C30,Assumptions!$B$98:$B$121,0)),""))`
- `F31` : `IF($C31="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C31,Assumptions!$B$98:$B$121,0)),""))`
- `F32` : `IF($C32="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C32,Assumptions!$B$98:$B$121,0)),""))`
- `F33` : `IF($C33="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C33,Assumptions!$B$98:$B$121,0)),""))`
- `F34` : `IF($C34="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C34,Assumptions!$B$98:$B$121,0)),""))`
- `F35` : `IF($C35="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C35,Assumptions!$B$98:$B$121,0)),""))`
- `F36` : `IF($C36="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C36,Assumptions!$B$98:$B$121,0)),""))`
- `F37` : `IF($C37="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C37,Assumptions!$B$98:$B$121,0)),""))`
- `F38` : `IF($C38="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C38,Assumptions!$B$98:$B$121,0)),""))`
- `F39` : `IF($C39="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C39,Assumptions!$B$98:$B$121,0)),""))`
- `F40` : `IF($C40="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C40,Assumptions!$B$98:$B$121,0)),""))`
- `F41` : `IF($C41="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C41,Assumptions!$B$98:$B$121,0)),""))`
- `F42` : `IF($C42="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C42,Assumptions!$B$98:$B$121,0)),""))`
- `F43` : `IF($C43="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C43,Assumptions!$B$98:$B$121,0)),""))`
- `F44` : `IF($C44="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C44,Assumptions!$B$98:$B$121,0)),""))`
- `F45` : `IF($C45="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C45,Assumptions!$B$98:$B$121,0)),""))`
- `F46` : `IF($C46="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C46,Assumptions!$B$98:$B$121,0)),""))`
- `F47` : `IF($C47="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C47,Assumptions!$B$98:$B$121,0)),""))`
- `F48` : `IF($C48="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C48,Assumptions!$B$98:$B$121,0)),""))`
- `F49` : `IF($C49="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C49,Assumptions!$B$98:$B$121,0)),""))`
- `F50` : `IF($C50="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C50,Assumptions!$B$98:$B$121,0)),""))`
- `F51` : `IF($C51="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C51,Assumptions!$B$98:$B$121,0)),""))`
- `F52` : `IF($C52="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C52,Assumptions!$B$98:$B$121,0)),""))`
- `F53` : `IF($C53="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C53,Assumptions!$B$98:$B$121,0)),""))`
- `F54` : `IF($C54="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C54,Assumptions!$B$98:$B$121,0)),""))`
- `F55` : `IF($C55="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C55,Assumptions!$B$98:$B$121,0)),""))`
- `F56` : `IF($C56="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C56,Assumptions!$B$98:$B$121,0)),""))`
- `F57` : `IF($C57="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C57,Assumptions!$B$98:$B$121,0)),""))`
- `F58` : `IF($C58="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C58,Assumptions!$B$98:$B$121,0)),""))`
- `F59` : `IF($C59="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C59,Assumptions!$B$98:$B$121,0)),""))`
- `F60` : `IF($C60="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C60,Assumptions!$B$98:$B$121,0)),""))`
- `F61` : `IF($C61="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C61,Assumptions!$B$98:$B$121,0)),""))`
- `F62` : `IF($C62="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C62,Assumptions!$B$98:$B$121,0)),""))`
- `F63` : `IF($C63="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C63,Assumptions!$B$98:$B$121,0)),""))`
- `F64` : `IF($C64="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C64,Assumptions!$B$98:$B$121,0)),""))`
- `F65` : `IF($C65="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C65,Assumptions!$B$98:$B$121,0)),""))`
- `F66` : `IF($C66="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C66,Assumptions!$B$98:$B$121,0)),""))`
- `F67` : `IF($C67="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C67,Assumptions!$B$98:$B$121,0)),""))`
- `F68` : `IF($C68="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C68,Assumptions!$B$98:$B$121,0)),""))`
- `F69` : `IF($C69="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C69,Assumptions!$B$98:$B$121,0)),""))`
- `F70` : `IF($C70="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C70,Assumptions!$B$98:$B$121,0)),""))`
- `F71` : `IF($C71="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C71,Assumptions!$B$98:$B$121,0)),""))`
- `F72` : `IF($C72="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C72,Assumptions!$B$98:$B$121,0)),""))`

### Part affectée R&D

Identifiant : `data_capex_h13_h72`. Type : `number`. Zones : `H13:H72`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Quote-part de l’actif affectée à R&D ; aucune éligibilité fiscale automatique.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_g13_g72, data_capex_c13_c72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["H13", "H14", "H15", "H16", "H17", "H18", "H19", "H20", "H21", "H22", "H23", "H24", "H25", "H26", "H27", "H28", "H29", "H30", "H31", "H32", "H33", "H34", "H35", "H36", "H37", "H38", "H39", "H40", "H41", "H42", "H43", "H44", "H45", "H46", "H47", "H48", "H49", "H50", "H51", "H52", "H53", "H54", "H55", "H56", "H57", "H58", "H59", "H60", "H61", "H62", "H63", "H64", "H65", "H66", "H67", "H68", "H69", "H70", "H71", "H72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `H13` : `IF($C13="","",IF($G13="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C13,Assumptions!$B$98:$B$121,0)),0)))`
- `H14` : `IF($C14="","",IF($G14="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C14,Assumptions!$B$98:$B$121,0)),0)))`
- `H15` : `IF($C15="","",IF($G15="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C15,Assumptions!$B$98:$B$121,0)),0)))`
- `H16` : `IF($C16="","",IF($G16="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C16,Assumptions!$B$98:$B$121,0)),0)))`
- `H17` : `IF($C17="","",IF($G17="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C17,Assumptions!$B$98:$B$121,0)),0)))`
- `H18` : `IF($C18="","",IF($G18="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C18,Assumptions!$B$98:$B$121,0)),0)))`
- `H19` : `IF($C19="","",IF($G19="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C19,Assumptions!$B$98:$B$121,0)),0)))`
- `H20` : `IF($C20="","",IF($G20="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C20,Assumptions!$B$98:$B$121,0)),0)))`
- `H21` : `IF($C21="","",IF($G21="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C21,Assumptions!$B$98:$B$121,0)),0)))`
- `H22` : `IF($C22="","",IF($G22="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C22,Assumptions!$B$98:$B$121,0)),0)))`
- `H23` : `IF($C23="","",IF($G23="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C23,Assumptions!$B$98:$B$121,0)),0)))`
- `H24` : `IF($C24="","",IF($G24="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C24,Assumptions!$B$98:$B$121,0)),0)))`
- `H25` : `IF($C25="","",IF($G25="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C25,Assumptions!$B$98:$B$121,0)),0)))`
- `H26` : `IF($C26="","",IF($G26="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C26,Assumptions!$B$98:$B$121,0)),0)))`
- `H27` : `IF($C27="","",IF($G27="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C27,Assumptions!$B$98:$B$121,0)),0)))`
- `H28` : `IF($C28="","",IF($G28="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C28,Assumptions!$B$98:$B$121,0)),0)))`
- `H29` : `IF($C29="","",IF($G29="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C29,Assumptions!$B$98:$B$121,0)),0)))`
- `H30` : `IF($C30="","",IF($G30="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C30,Assumptions!$B$98:$B$121,0)),0)))`
- `H31` : `IF($C31="","",IF($G31="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C31,Assumptions!$B$98:$B$121,0)),0)))`
- `H32` : `IF($C32="","",IF($G32="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C32,Assumptions!$B$98:$B$121,0)),0)))`
- `H33` : `IF($C33="","",IF($G33="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C33,Assumptions!$B$98:$B$121,0)),0)))`
- `H34` : `IF($C34="","",IF($G34="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C34,Assumptions!$B$98:$B$121,0)),0)))`
- `H35` : `IF($C35="","",IF($G35="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C35,Assumptions!$B$98:$B$121,0)),0)))`
- `H36` : `IF($C36="","",IF($G36="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C36,Assumptions!$B$98:$B$121,0)),0)))`
- `H37` : `IF($C37="","",IF($G37="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C37,Assumptions!$B$98:$B$121,0)),0)))`
- `H38` : `IF($C38="","",IF($G38="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C38,Assumptions!$B$98:$B$121,0)),0)))`
- `H39` : `IF($C39="","",IF($G39="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C39,Assumptions!$B$98:$B$121,0)),0)))`
- `H40` : `IF($C40="","",IF($G40="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C40,Assumptions!$B$98:$B$121,0)),0)))`
- `H41` : `IF($C41="","",IF($G41="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C41,Assumptions!$B$98:$B$121,0)),0)))`
- `H42` : `IF($C42="","",IF($G42="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C42,Assumptions!$B$98:$B$121,0)),0)))`
- `H43` : `IF($C43="","",IF($G43="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C43,Assumptions!$B$98:$B$121,0)),0)))`
- `H44` : `IF($C44="","",IF($G44="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C44,Assumptions!$B$98:$B$121,0)),0)))`
- `H45` : `IF($C45="","",IF($G45="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C45,Assumptions!$B$98:$B$121,0)),0)))`
- `H46` : `IF($C46="","",IF($G46="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C46,Assumptions!$B$98:$B$121,0)),0)))`
- `H47` : `IF($C47="","",IF($G47="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C47,Assumptions!$B$98:$B$121,0)),0)))`
- `H48` : `IF($C48="","",IF($G48="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C48,Assumptions!$B$98:$B$121,0)),0)))`
- `H49` : `IF($C49="","",IF($G49="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C49,Assumptions!$B$98:$B$121,0)),0)))`
- `H50` : `IF($C50="","",IF($G50="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C50,Assumptions!$B$98:$B$121,0)),0)))`
- `H51` : `IF($C51="","",IF($G51="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C51,Assumptions!$B$98:$B$121,0)),0)))`
- `H52` : `IF($C52="","",IF($G52="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C52,Assumptions!$B$98:$B$121,0)),0)))`
- `H53` : `IF($C53="","",IF($G53="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C53,Assumptions!$B$98:$B$121,0)),0)))`
- `H54` : `IF($C54="","",IF($G54="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C54,Assumptions!$B$98:$B$121,0)),0)))`
- `H55` : `IF($C55="","",IF($G55="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C55,Assumptions!$B$98:$B$121,0)),0)))`
- `H56` : `IF($C56="","",IF($G56="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C56,Assumptions!$B$98:$B$121,0)),0)))`
- `H57` : `IF($C57="","",IF($G57="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C57,Assumptions!$B$98:$B$121,0)),0)))`
- `H58` : `IF($C58="","",IF($G58="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C58,Assumptions!$B$98:$B$121,0)),0)))`
- `H59` : `IF($C59="","",IF($G59="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C59,Assumptions!$B$98:$B$121,0)),0)))`
- `H60` : `IF($C60="","",IF($G60="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C60,Assumptions!$B$98:$B$121,0)),0)))`
- `H61` : `IF($C61="","",IF($G61="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C61,Assumptions!$B$98:$B$121,0)),0)))`
- `H62` : `IF($C62="","",IF($G62="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C62,Assumptions!$B$98:$B$121,0)),0)))`
- `H63` : `IF($C63="","",IF($G63="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C63,Assumptions!$B$98:$B$121,0)),0)))`
- `H64` : `IF($C64="","",IF($G64="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C64,Assumptions!$B$98:$B$121,0)),0)))`
- `H65` : `IF($C65="","",IF($G65="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C65,Assumptions!$B$98:$B$121,0)),0)))`
- `H66` : `IF($C66="","",IF($G66="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C66,Assumptions!$B$98:$B$121,0)),0)))`
- `H67` : `IF($C67="","",IF($G67="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C67,Assumptions!$B$98:$B$121,0)),0)))`
- `H68` : `IF($C68="","",IF($G68="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C68,Assumptions!$B$98:$B$121,0)),0)))`
- `H69` : `IF($C69="","",IF($G69="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C69,Assumptions!$B$98:$B$121,0)),0)))`
- `H70` : `IF($C70="","",IF($G70="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C70,Assumptions!$B$98:$B$121,0)),0)))`
- `H71` : `IF($C71="","",IF($G71="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C71,Assumptions!$B$98:$B$121,0)),0)))`
- `H72` : `IF($C72="","",IF($G72="Non",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C72,Assumptions!$B$98:$B$121,0)),0)))`

### Durée crédit-bail en années

Identifiant : `data_capex_j13_j72`. Type : `number`. Zones : `J13:J72`.

Unité explicite : années ; conversion en mois selon la règle du modèle.

Assiette : Durée du crédit-bail ; nombre entier de mois requis par la carte.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_i13_i72, data_capex_e13_e72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["J13", "J14", "J15", "J16", "J17", "J18", "J19", "J20", "J21", "J22", "J23", "J24", "J25", "J26", "J27", "J28", "J29", "J30", "J31", "J32", "J33", "J34", "J35", "J36", "J37", "J38", "J39", "J40", "J41", "J42", "J43", "J44", "J45", "J46", "J47", "J48", "J49", "J50", "J51", "J52", "J53", "J54", "J55", "J56", "J57", "J58", "J59", "J60", "J61", "J62", "J63", "J64", "J65", "J66", "J67", "J68", "J69", "J70", "J71", "J72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "whole_months": "value * 12 entier à 1e-8 près"}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "whole_months": "value * 12 entier à 1e-8 près"}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `J13` : `IF($I13<>"Crédit-bail","",IF(N($F13)=0,"",N($F13)))`
- `J14` : `IF($I14<>"Crédit-bail","",IF(N($F14)=0,"",N($F14)))`
- `J15` : `IF($I15<>"Crédit-bail","",IF(N($F15)=0,"",N($F15)))`
- `J16` : `IF($I16<>"Crédit-bail","",IF(N($F16)=0,"",N($F16)))`
- `J17` : `IF($I17<>"Crédit-bail","",IF(N($F17)=0,"",N($F17)))`
- `J18` : `IF($I18<>"Crédit-bail","",IF(N($F18)=0,"",N($F18)))`
- `J19` : `IF($I19<>"Crédit-bail","",IF(N($F19)=0,"",N($F19)))`
- `J20` : `IF($I20<>"Crédit-bail","",IF(N($F20)=0,"",N($F20)))`
- `J21` : `IF($I21<>"Crédit-bail","",IF(N($F21)=0,"",N($F21)))`
- `J22` : `IF($I22<>"Crédit-bail","",IF(N($F22)=0,"",N($F22)))`
- `J23` : `IF($I23<>"Crédit-bail","",IF(N($F23)=0,"",N($F23)))`
- `J24` : `IF($I24<>"Crédit-bail","",IF(N($F24)=0,"",N($F24)))`
- `J25` : `IF($I25<>"Crédit-bail","",IF(N($F25)=0,"",N($F25)))`
- `J26` : `IF($I26<>"Crédit-bail","",IF(N($F26)=0,"",N($F26)))`
- `J27` : `IF($I27<>"Crédit-bail","",IF(N($F27)=0,"",N($F27)))`
- `J28` : `IF($I28<>"Crédit-bail","",IF(N($F28)=0,"",N($F28)))`
- `J29` : `IF($I29<>"Crédit-bail","",IF(N($F29)=0,"",N($F29)))`
- `J30` : `IF($I30<>"Crédit-bail","",IF(N($F30)=0,"",N($F30)))`
- `J31` : `IF($I31<>"Crédit-bail","",IF(N($F31)=0,"",N($F31)))`
- `J32` : `IF($I32<>"Crédit-bail","",IF(N($F32)=0,"",N($F32)))`
- `J33` : `IF($I33<>"Crédit-bail","",IF(N($F33)=0,"",N($F33)))`
- `J34` : `IF($I34<>"Crédit-bail","",IF(N($F34)=0,"",N($F34)))`
- `J35` : `IF($I35<>"Crédit-bail","",IF(N($F35)=0,"",N($F35)))`
- `J36` : `IF($I36<>"Crédit-bail","",IF(N($F36)=0,"",N($F36)))`
- `J37` : `IF($I37<>"Crédit-bail","",IF(N($F37)=0,"",N($F37)))`
- `J38` : `IF($I38<>"Crédit-bail","",IF(N($F38)=0,"",N($F38)))`
- `J39` : `IF($I39<>"Crédit-bail","",IF(N($F39)=0,"",N($F39)))`
- `J40` : `IF($I40<>"Crédit-bail","",IF(N($F40)=0,"",N($F40)))`
- `J41` : `IF($I41<>"Crédit-bail","",IF(N($F41)=0,"",N($F41)))`
- `J42` : `IF($I42<>"Crédit-bail","",IF(N($F42)=0,"",N($F42)))`
- `J43` : `IF($I43<>"Crédit-bail","",IF(N($F43)=0,"",N($F43)))`
- `J44` : `IF($I44<>"Crédit-bail","",IF(N($F44)=0,"",N($F44)))`
- `J45` : `IF($I45<>"Crédit-bail","",IF(N($F45)=0,"",N($F45)))`
- `J46` : `IF($I46<>"Crédit-bail","",IF(N($F46)=0,"",N($F46)))`
- `J47` : `IF($I47<>"Crédit-bail","",IF(N($F47)=0,"",N($F47)))`
- `J48` : `IF($I48<>"Crédit-bail","",IF(N($F48)=0,"",N($F48)))`
- `J49` : `IF($I49<>"Crédit-bail","",IF(N($F49)=0,"",N($F49)))`
- `J50` : `IF($I50<>"Crédit-bail","",IF(N($F50)=0,"",N($F50)))`
- `J51` : `IF($I51<>"Crédit-bail","",IF(N($F51)=0,"",N($F51)))`
- `J52` : `IF($I52<>"Crédit-bail","",IF(N($F52)=0,"",N($F52)))`
- `J53` : `IF($I53<>"Crédit-bail","",IF(N($F53)=0,"",N($F53)))`
- `J54` : `IF($I54<>"Crédit-bail","",IF(N($F54)=0,"",N($F54)))`
- `J55` : `IF($I55<>"Crédit-bail","",IF(N($F55)=0,"",N($F55)))`
- `J56` : `IF($I56<>"Crédit-bail","",IF(N($F56)=0,"",N($F56)))`
- `J57` : `IF($I57<>"Crédit-bail","",IF(N($F57)=0,"",N($F57)))`
- `J58` : `IF($I58<>"Crédit-bail","",IF(N($F58)=0,"",N($F58)))`
- `J59` : `IF($I59<>"Crédit-bail","",IF(N($F59)=0,"",N($F59)))`
- `J60` : `IF($I60<>"Crédit-bail","",IF(N($F60)=0,"",N($F60)))`
- `J61` : `IF($I61<>"Crédit-bail","",IF(N($F61)=0,"",N($F61)))`
- `J62` : `IF($I62<>"Crédit-bail","",IF(N($F62)=0,"",N($F62)))`
- `J63` : `IF($I63<>"Crédit-bail","",IF(N($F63)=0,"",N($F63)))`
- `J64` : `IF($I64<>"Crédit-bail","",IF(N($F64)=0,"",N($F64)))`
- `J65` : `IF($I65<>"Crédit-bail","",IF(N($F65)=0,"",N($F65)))`
- `J66` : `IF($I66<>"Crédit-bail","",IF(N($F66)=0,"",N($F66)))`
- `J67` : `IF($I67<>"Crédit-bail","",IF(N($F67)=0,"",N($F67)))`
- `J68` : `IF($I68<>"Crédit-bail","",IF(N($F68)=0,"",N($F68)))`
- `J69` : `IF($I69<>"Crédit-bail","",IF(N($F69)=0,"",N($F69)))`
- `J70` : `IF($I70<>"Crédit-bail","",IF(N($F70)=0,"",N($F70)))`
- `J71` : `IF($I71<>"Crédit-bail","",IF(N($F71)=0,"",N($F71)))`
- `J72` : `IF($I72<>"Crédit-bail","",IF(N($F72)=0,"",N($F72)))`

### Taux annuel crédit-bail

Identifiant : `data_capex_k13_k72`. Type : `number`. Zones : `K13:K72`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Taux annuel du crédit-bail, avant conversion au taux mensuel du moteur.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_i13_i72, data_capex_j13_j72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["K13", "K14", "K15", "K16", "K17", "K18", "K19", "K20", "K21", "K22", "K23", "K24", "K25", "K26", "K27", "K28", "K29", "K30", "K31", "K32", "K33", "K34", "K35", "K36", "K37", "K38", "K39", "K40", "K41", "K42", "K43", "K44", "K45", "K46", "K47", "K48", "K49", "K50", "K51", "K52", "K53", "K54", "K55", "K56", "K57", "K58", "K59", "K60", "K61", "K62", "K63", "K64", "K65", "K66", "K67", "K68", "K69", "K70", "K71", "K72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0}, "choices": null}`.

Contraintes : `{"min": 0}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `K13` : `IF($I13<>"Crédit-bail","",Assumptions!$D$91)`
- `K14` : `IF($I14<>"Crédit-bail","",Assumptions!$D$91)`
- `K15` : `IF($I15<>"Crédit-bail","",Assumptions!$D$91)`
- `K16` : `IF($I16<>"Crédit-bail","",Assumptions!$D$91)`
- `K17` : `IF($I17<>"Crédit-bail","",Assumptions!$D$91)`
- `K18` : `IF($I18<>"Crédit-bail","",Assumptions!$D$91)`
- `K19` : `IF($I19<>"Crédit-bail","",Assumptions!$D$91)`
- `K20` : `IF($I20<>"Crédit-bail","",Assumptions!$D$91)`
- `K21` : `IF($I21<>"Crédit-bail","",Assumptions!$D$91)`
- `K22` : `IF($I22<>"Crédit-bail","",Assumptions!$D$91)`
- `K23` : `IF($I23<>"Crédit-bail","",Assumptions!$D$91)`
- `K24` : `IF($I24<>"Crédit-bail","",Assumptions!$D$91)`
- `K25` : `IF($I25<>"Crédit-bail","",Assumptions!$D$91)`
- `K26` : `IF($I26<>"Crédit-bail","",Assumptions!$D$91)`
- `K27` : `IF($I27<>"Crédit-bail","",Assumptions!$D$91)`
- `K28` : `IF($I28<>"Crédit-bail","",Assumptions!$D$91)`
- `K29` : `IF($I29<>"Crédit-bail","",Assumptions!$D$91)`
- `K30` : `IF($I30<>"Crédit-bail","",Assumptions!$D$91)`
- `K31` : `IF($I31<>"Crédit-bail","",Assumptions!$D$91)`
- `K32` : `IF($I32<>"Crédit-bail","",Assumptions!$D$91)`
- `K33` : `IF($I33<>"Crédit-bail","",Assumptions!$D$91)`
- `K34` : `IF($I34<>"Crédit-bail","",Assumptions!$D$91)`
- `K35` : `IF($I35<>"Crédit-bail","",Assumptions!$D$91)`
- `K36` : `IF($I36<>"Crédit-bail","",Assumptions!$D$91)`
- `K37` : `IF($I37<>"Crédit-bail","",Assumptions!$D$91)`
- `K38` : `IF($I38<>"Crédit-bail","",Assumptions!$D$91)`
- `K39` : `IF($I39<>"Crédit-bail","",Assumptions!$D$91)`
- `K40` : `IF($I40<>"Crédit-bail","",Assumptions!$D$91)`
- `K41` : `IF($I41<>"Crédit-bail","",Assumptions!$D$91)`
- `K42` : `IF($I42<>"Crédit-bail","",Assumptions!$D$91)`
- `K43` : `IF($I43<>"Crédit-bail","",Assumptions!$D$91)`
- `K44` : `IF($I44<>"Crédit-bail","",Assumptions!$D$91)`
- `K45` : `IF($I45<>"Crédit-bail","",Assumptions!$D$91)`
- `K46` : `IF($I46<>"Crédit-bail","",Assumptions!$D$91)`
- `K47` : `IF($I47<>"Crédit-bail","",Assumptions!$D$91)`
- `K48` : `IF($I48<>"Crédit-bail","",Assumptions!$D$91)`
- `K49` : `IF($I49<>"Crédit-bail","",Assumptions!$D$91)`
- `K50` : `IF($I50<>"Crédit-bail","",Assumptions!$D$91)`
- `K51` : `IF($I51<>"Crédit-bail","",Assumptions!$D$91)`
- `K52` : `IF($I52<>"Crédit-bail","",Assumptions!$D$91)`
- `K53` : `IF($I53<>"Crédit-bail","",Assumptions!$D$91)`
- `K54` : `IF($I54<>"Crédit-bail","",Assumptions!$D$91)`
- `K55` : `IF($I55<>"Crédit-bail","",Assumptions!$D$91)`
- `K56` : `IF($I56<>"Crédit-bail","",Assumptions!$D$91)`
- `K57` : `IF($I57<>"Crédit-bail","",Assumptions!$D$91)`
- `K58` : `IF($I58<>"Crédit-bail","",Assumptions!$D$91)`
- `K59` : `IF($I59<>"Crédit-bail","",Assumptions!$D$91)`
- `K60` : `IF($I60<>"Crédit-bail","",Assumptions!$D$91)`
- `K61` : `IF($I61<>"Crédit-bail","",Assumptions!$D$91)`
- `K62` : `IF($I62<>"Crédit-bail","",Assumptions!$D$91)`
- `K63` : `IF($I63<>"Crédit-bail","",Assumptions!$D$91)`
- `K64` : `IF($I64<>"Crédit-bail","",Assumptions!$D$91)`
- `K65` : `IF($I65<>"Crédit-bail","",Assumptions!$D$91)`
- `K66` : `IF($I66<>"Crédit-bail","",Assumptions!$D$91)`
- `K67` : `IF($I67<>"Crédit-bail","",Assumptions!$D$91)`
- `K68` : `IF($I68<>"Crédit-bail","",Assumptions!$D$91)`
- `K69` : `IF($I69<>"Crédit-bail","",Assumptions!$D$91)`
- `K70` : `IF($I70<>"Crédit-bail","",Assumptions!$D$91)`
- `K71` : `IF($I71<>"Crédit-bail","",Assumptions!$D$91)`
- `K72` : `IF($I72<>"Crédit-bail","",Assumptions!$D$91)`

### Nature de l’immobilisation

Identifiant : `data_capex_m13_m72`. Type : `enum`. Zones : `M13:M72`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Nature corporelle/incorporelle de l’immobilisation selon typologie ; défaut propriétaire explicite.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_c13_c72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["M13", "M14", "M15", "M16", "M17", "M18", "M19", "M20", "M21", "M22", "M23", "M24", "M25", "M26", "M27", "M28", "M29", "M30", "M31", "M32", "M33", "M34", "M35", "M36", "M37", "M38", "M39", "M40", "M41", "M42", "M43", "M44", "M45", "M46", "M47", "M48", "M49", "M50", "M51", "M52", "M53", "M54", "M55", "M56", "M57", "M58", "M59", "M60", "M61", "M62", "M63", "M64", "M65", "M66", "M67", "M68", "M69", "M70", "M71", "M72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Corporelle", "Incorporelle"]}`.

Choix du catalogue : ["Corporelle", "Incorporelle"].

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `M13` : `IF($B13="","",IF(OR($C13="Logiciels de conception et simulation",$C13="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M14` : `IF($B14="","",IF(OR($C14="Logiciels de conception et simulation",$C14="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M15` : `IF($B15="","",IF(OR($C15="Logiciels de conception et simulation",$C15="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M16` : `IF($B16="","",IF(OR($C16="Logiciels de conception et simulation",$C16="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M17` : `IF($B17="","",IF(OR($C17="Logiciels de conception et simulation",$C17="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M18` : `IF($B18="","",IF(OR($C18="Logiciels de conception et simulation",$C18="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M19` : `IF($B19="","",IF(OR($C19="Logiciels de conception et simulation",$C19="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M20` : `IF($B20="","",IF(OR($C20="Logiciels de conception et simulation",$C20="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M21` : `IF($B21="","",IF(OR($C21="Logiciels de conception et simulation",$C21="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M22` : `IF($B22="","",IF(OR($C22="Logiciels de conception et simulation",$C22="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M23` : `IF($B23="","",IF(OR($C23="Logiciels de conception et simulation",$C23="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M24` : `IF($B24="","",IF(OR($C24="Logiciels de conception et simulation",$C24="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M25` : `IF($B25="","",IF(OR($C25="Logiciels de conception et simulation",$C25="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M26` : `IF($B26="","",IF(OR($C26="Logiciels de conception et simulation",$C26="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M27` : `IF($B27="","",IF(OR($C27="Logiciels de conception et simulation",$C27="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M28` : `IF($B28="","",IF(OR($C28="Logiciels de conception et simulation",$C28="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M29` : `IF($B29="","",IF(OR($C29="Logiciels de conception et simulation",$C29="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M30` : `IF($B30="","",IF(OR($C30="Logiciels de conception et simulation",$C30="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M31` : `IF($B31="","",IF(OR($C31="Logiciels de conception et simulation",$C31="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M32` : `IF($B32="","",IF(OR($C32="Logiciels de conception et simulation",$C32="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M33` : `IF($B33="","",IF(OR($C33="Logiciels de conception et simulation",$C33="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M34` : `IF($B34="","",IF(OR($C34="Logiciels de conception et simulation",$C34="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M35` : `IF($B35="","",IF(OR($C35="Logiciels de conception et simulation",$C35="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M36` : `IF($B36="","",IF(OR($C36="Logiciels de conception et simulation",$C36="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M37` : `IF($B37="","",IF(OR($C37="Logiciels de conception et simulation",$C37="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M38` : `IF($B38="","",IF(OR($C38="Logiciels de conception et simulation",$C38="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M39` : `IF($B39="","",IF(OR($C39="Logiciels de conception et simulation",$C39="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M40` : `IF($B40="","",IF(OR($C40="Logiciels de conception et simulation",$C40="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M41` : `IF($B41="","",IF(OR($C41="Logiciels de conception et simulation",$C41="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M42` : `IF($B42="","",IF(OR($C42="Logiciels de conception et simulation",$C42="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M43` : `IF($B43="","",IF(OR($C43="Logiciels de conception et simulation",$C43="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M44` : `IF($B44="","",IF(OR($C44="Logiciels de conception et simulation",$C44="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M45` : `IF($B45="","",IF(OR($C45="Logiciels de conception et simulation",$C45="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M46` : `IF($B46="","",IF(OR($C46="Logiciels de conception et simulation",$C46="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M47` : `IF($B47="","",IF(OR($C47="Logiciels de conception et simulation",$C47="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M48` : `IF($B48="","",IF(OR($C48="Logiciels de conception et simulation",$C48="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M49` : `IF($B49="","",IF(OR($C49="Logiciels de conception et simulation",$C49="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M50` : `IF($B50="","",IF(OR($C50="Logiciels de conception et simulation",$C50="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M51` : `IF($B51="","",IF(OR($C51="Logiciels de conception et simulation",$C51="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M52` : `IF($B52="","",IF(OR($C52="Logiciels de conception et simulation",$C52="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M53` : `IF($B53="","",IF(OR($C53="Logiciels de conception et simulation",$C53="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M54` : `IF($B54="","",IF(OR($C54="Logiciels de conception et simulation",$C54="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M55` : `IF($B55="","",IF(OR($C55="Logiciels de conception et simulation",$C55="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M56` : `IF($B56="","",IF(OR($C56="Logiciels de conception et simulation",$C56="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M57` : `IF($B57="","",IF(OR($C57="Logiciels de conception et simulation",$C57="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M58` : `IF($B58="","",IF(OR($C58="Logiciels de conception et simulation",$C58="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M59` : `IF($B59="","",IF(OR($C59="Logiciels de conception et simulation",$C59="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M60` : `IF($B60="","",IF(OR($C60="Logiciels de conception et simulation",$C60="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M61` : `IF($B61="","",IF(OR($C61="Logiciels de conception et simulation",$C61="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M62` : `IF($B62="","",IF(OR($C62="Logiciels de conception et simulation",$C62="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M63` : `IF($B63="","",IF(OR($C63="Logiciels de conception et simulation",$C63="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M64` : `IF($B64="","",IF(OR($C64="Logiciels de conception et simulation",$C64="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M65` : `IF($B65="","",IF(OR($C65="Logiciels de conception et simulation",$C65="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M66` : `IF($B66="","",IF(OR($C66="Logiciels de conception et simulation",$C66="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M67` : `IF($B67="","",IF(OR($C67="Logiciels de conception et simulation",$C67="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M68` : `IF($B68="","",IF(OR($C68="Logiciels de conception et simulation",$C68="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M69` : `IF($B69="","",IF(OR($C69="Logiciels de conception et simulation",$C69="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M70` : `IF($B70="","",IF(OR($C70="Logiciels de conception et simulation",$C70="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M71` : `IF($B71="","",IF(OR($C71="Logiciels de conception et simulation",$C71="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`
- `M72` : `IF($B72="","",IF(OR($C72="Logiciels de conception et simulation",$C72="Logiciels de gestion (PLM, MES, ERP)"),"Incorporelle","Corporelle"))`

### Entretien inclus dans le loyer

Identifiant : `data_capex_n13_n72`. Type : `enum`. Zones : `N13:N72`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Inclusion contractuelle d’entretien/assurance dans les loyers ; éviter un double coût.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_i13_i72, data_capex_j13_j72, data_capex_p13_p72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22", "N23", "N24", "N25", "N26", "N27", "N28", "N29", "N30", "N31", "N32", "N33", "N34", "N35", "N36", "N37", "N38", "N39", "N40", "N41", "N42", "N43", "N44", "N45", "N46", "N47", "N48", "N49", "N50", "N51", "N52", "N53", "N54", "N55", "N56", "N57", "N58", "N59", "N60", "N61", "N62", "N63", "N64", "N65", "N66", "N67", "N68", "N69", "N70", "N71", "N72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non"]}`.

Choix du catalogue : ["Oui", "Non"].

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `N13` : `IF(OR($B13="",$I13<>"Crédit-bail"),"","Non")`
- `N14` : `IF(OR($B14="",$I14<>"Crédit-bail"),"","Non")`
- `N15` : `IF(OR($B15="",$I15<>"Crédit-bail"),"","Non")`
- `N16` : `IF(OR($B16="",$I16<>"Crédit-bail"),"","Non")`
- `N17` : `IF(OR($B17="",$I17<>"Crédit-bail"),"","Non")`
- `N18` : `IF(OR($B18="",$I18<>"Crédit-bail"),"","Non")`
- `N19` : `IF(OR($B19="",$I19<>"Crédit-bail"),"","Non")`
- `N20` : `IF(OR($B20="",$I20<>"Crédit-bail"),"","Non")`
- `N21` : `IF(OR($B21="",$I21<>"Crédit-bail"),"","Non")`
- `N22` : `IF(OR($B22="",$I22<>"Crédit-bail"),"","Non")`
- `N23` : `IF(OR($B23="",$I23<>"Crédit-bail"),"","Non")`
- `N24` : `IF(OR($B24="",$I24<>"Crédit-bail"),"","Non")`
- `N25` : `IF(OR($B25="",$I25<>"Crédit-bail"),"","Non")`
- `N26` : `IF(OR($B26="",$I26<>"Crédit-bail"),"","Non")`
- `N27` : `IF(OR($B27="",$I27<>"Crédit-bail"),"","Non")`
- `N28` : `IF(OR($B28="",$I28<>"Crédit-bail"),"","Non")`
- `N29` : `IF(OR($B29="",$I29<>"Crédit-bail"),"","Non")`
- `N30` : `IF(OR($B30="",$I30<>"Crédit-bail"),"","Non")`
- `N31` : `IF(OR($B31="",$I31<>"Crédit-bail"),"","Non")`
- `N32` : `IF(OR($B32="",$I32<>"Crédit-bail"),"","Non")`
- `N33` : `IF(OR($B33="",$I33<>"Crédit-bail"),"","Non")`
- `N34` : `IF(OR($B34="",$I34<>"Crédit-bail"),"","Non")`
- `N35` : `IF(OR($B35="",$I35<>"Crédit-bail"),"","Non")`
- `N36` : `IF(OR($B36="",$I36<>"Crédit-bail"),"","Non")`
- `N37` : `IF(OR($B37="",$I37<>"Crédit-bail"),"","Non")`
- `N38` : `IF(OR($B38="",$I38<>"Crédit-bail"),"","Non")`
- `N39` : `IF(OR($B39="",$I39<>"Crédit-bail"),"","Non")`
- `N40` : `IF(OR($B40="",$I40<>"Crédit-bail"),"","Non")`
- `N41` : `IF(OR($B41="",$I41<>"Crédit-bail"),"","Non")`
- `N42` : `IF(OR($B42="",$I42<>"Crédit-bail"),"","Non")`
- `N43` : `IF(OR($B43="",$I43<>"Crédit-bail"),"","Non")`
- `N44` : `IF(OR($B44="",$I44<>"Crédit-bail"),"","Non")`
- `N45` : `IF(OR($B45="",$I45<>"Crédit-bail"),"","Non")`
- `N46` : `IF(OR($B46="",$I46<>"Crédit-bail"),"","Non")`
- `N47` : `IF(OR($B47="",$I47<>"Crédit-bail"),"","Non")`
- `N48` : `IF(OR($B48="",$I48<>"Crédit-bail"),"","Non")`
- `N49` : `IF(OR($B49="",$I49<>"Crédit-bail"),"","Non")`
- `N50` : `IF(OR($B50="",$I50<>"Crédit-bail"),"","Non")`
- `N51` : `IF(OR($B51="",$I51<>"Crédit-bail"),"","Non")`
- `N52` : `IF(OR($B52="",$I52<>"Crédit-bail"),"","Non")`
- `N53` : `IF(OR($B53="",$I53<>"Crédit-bail"),"","Non")`
- `N54` : `IF(OR($B54="",$I54<>"Crédit-bail"),"","Non")`
- `N55` : `IF(OR($B55="",$I55<>"Crédit-bail"),"","Non")`
- `N56` : `IF(OR($B56="",$I56<>"Crédit-bail"),"","Non")`
- `N57` : `IF(OR($B57="",$I57<>"Crédit-bail"),"","Non")`
- `N58` : `IF(OR($B58="",$I58<>"Crédit-bail"),"","Non")`
- `N59` : `IF(OR($B59="",$I59<>"Crédit-bail"),"","Non")`
- `N60` : `IF(OR($B60="",$I60<>"Crédit-bail"),"","Non")`
- `N61` : `IF(OR($B61="",$I61<>"Crédit-bail"),"","Non")`
- `N62` : `IF(OR($B62="",$I62<>"Crédit-bail"),"","Non")`
- `N63` : `IF(OR($B63="",$I63<>"Crédit-bail"),"","Non")`
- `N64` : `IF(OR($B64="",$I64<>"Crédit-bail"),"","Non")`
- `N65` : `IF(OR($B65="",$I65<>"Crédit-bail"),"","Non")`
- `N66` : `IF(OR($B66="",$I66<>"Crédit-bail"),"","Non")`
- `N67` : `IF(OR($B67="",$I67<>"Crédit-bail"),"","Non")`
- `N68` : `IF(OR($B68="",$I68<>"Crédit-bail"),"","Non")`
- `N69` : `IF(OR($B69="",$I69<>"Crédit-bail"),"","Non")`
- `N70` : `IF(OR($B70="",$I70<>"Crédit-bail"),"","Non")`
- `N71` : `IF(OR($B71="",$I71<>"Crédit-bail"),"","Non")`
- `N72` : `IF(OR($B72="",$I72<>"Crédit-bail"),"","Non")`

### Assurance incluse dans le loyer

Identifiant : `data_capex_o13_o72`. Type : `enum`. Zones : `O13:O72`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Inclusion contractuelle d’entretien/assurance dans les loyers ; éviter un double coût.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_capex_i13_i72, data_capex_j13_j72, data_capex_p13_p72.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["O13", "O14", "O15", "O16", "O17", "O18", "O19", "O20", "O21", "O22", "O23", "O24", "O25", "O26", "O27", "O28", "O29", "O30", "O31", "O32", "O33", "O34", "O35", "O36", "O37", "O38", "O39", "O40", "O41", "O42", "O43", "O44", "O45", "O46", "O47", "O48", "O49", "O50", "O51", "O52", "O53", "O54", "O55", "O56", "O57", "O58", "O59", "O60", "O61", "O62", "O63", "O64", "O65", "O66", "O67", "O68", "O69", "O70", "O71", "O72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Oui", "Non"]}`.

Choix du catalogue : ["Oui", "Non"].

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `O13` : `IF(OR($B13="",$I13<>"Crédit-bail"),"","Non")`
- `O14` : `IF(OR($B14="",$I14<>"Crédit-bail"),"","Non")`
- `O15` : `IF(OR($B15="",$I15<>"Crédit-bail"),"","Non")`
- `O16` : `IF(OR($B16="",$I16<>"Crédit-bail"),"","Non")`
- `O17` : `IF(OR($B17="",$I17<>"Crédit-bail"),"","Non")`
- `O18` : `IF(OR($B18="",$I18<>"Crédit-bail"),"","Non")`
- `O19` : `IF(OR($B19="",$I19<>"Crédit-bail"),"","Non")`
- `O20` : `IF(OR($B20="",$I20<>"Crédit-bail"),"","Non")`
- `O21` : `IF(OR($B21="",$I21<>"Crédit-bail"),"","Non")`
- `O22` : `IF(OR($B22="",$I22<>"Crédit-bail"),"","Non")`
- `O23` : `IF(OR($B23="",$I23<>"Crédit-bail"),"","Non")`
- `O24` : `IF(OR($B24="",$I24<>"Crédit-bail"),"","Non")`
- `O25` : `IF(OR($B25="",$I25<>"Crédit-bail"),"","Non")`
- `O26` : `IF(OR($B26="",$I26<>"Crédit-bail"),"","Non")`
- `O27` : `IF(OR($B27="",$I27<>"Crédit-bail"),"","Non")`
- `O28` : `IF(OR($B28="",$I28<>"Crédit-bail"),"","Non")`
- `O29` : `IF(OR($B29="",$I29<>"Crédit-bail"),"","Non")`
- `O30` : `IF(OR($B30="",$I30<>"Crédit-bail"),"","Non")`
- `O31` : `IF(OR($B31="",$I31<>"Crédit-bail"),"","Non")`
- `O32` : `IF(OR($B32="",$I32<>"Crédit-bail"),"","Non")`
- `O33` : `IF(OR($B33="",$I33<>"Crédit-bail"),"","Non")`
- `O34` : `IF(OR($B34="",$I34<>"Crédit-bail"),"","Non")`
- `O35` : `IF(OR($B35="",$I35<>"Crédit-bail"),"","Non")`
- `O36` : `IF(OR($B36="",$I36<>"Crédit-bail"),"","Non")`
- `O37` : `IF(OR($B37="",$I37<>"Crédit-bail"),"","Non")`
- `O38` : `IF(OR($B38="",$I38<>"Crédit-bail"),"","Non")`
- `O39` : `IF(OR($B39="",$I39<>"Crédit-bail"),"","Non")`
- `O40` : `IF(OR($B40="",$I40<>"Crédit-bail"),"","Non")`
- `O41` : `IF(OR($B41="",$I41<>"Crédit-bail"),"","Non")`
- `O42` : `IF(OR($B42="",$I42<>"Crédit-bail"),"","Non")`
- `O43` : `IF(OR($B43="",$I43<>"Crédit-bail"),"","Non")`
- `O44` : `IF(OR($B44="",$I44<>"Crédit-bail"),"","Non")`
- `O45` : `IF(OR($B45="",$I45<>"Crédit-bail"),"","Non")`
- `O46` : `IF(OR($B46="",$I46<>"Crédit-bail"),"","Non")`
- `O47` : `IF(OR($B47="",$I47<>"Crédit-bail"),"","Non")`
- `O48` : `IF(OR($B48="",$I48<>"Crédit-bail"),"","Non")`
- `O49` : `IF(OR($B49="",$I49<>"Crédit-bail"),"","Non")`
- `O50` : `IF(OR($B50="",$I50<>"Crédit-bail"),"","Non")`
- `O51` : `IF(OR($B51="",$I51<>"Crédit-bail"),"","Non")`
- `O52` : `IF(OR($B52="",$I52<>"Crédit-bail"),"","Non")`
- `O53` : `IF(OR($B53="",$I53<>"Crédit-bail"),"","Non")`
- `O54` : `IF(OR($B54="",$I54<>"Crédit-bail"),"","Non")`
- `O55` : `IF(OR($B55="",$I55<>"Crédit-bail"),"","Non")`
- `O56` : `IF(OR($B56="",$I56<>"Crédit-bail"),"","Non")`
- `O57` : `IF(OR($B57="",$I57<>"Crédit-bail"),"","Non")`
- `O58` : `IF(OR($B58="",$I58<>"Crédit-bail"),"","Non")`
- `O59` : `IF(OR($B59="",$I59<>"Crédit-bail"),"","Non")`
- `O60` : `IF(OR($B60="",$I60<>"Crédit-bail"),"","Non")`
- `O61` : `IF(OR($B61="",$I61<>"Crédit-bail"),"","Non")`
- `O62` : `IF(OR($B62="",$I62<>"Crédit-bail"),"","Non")`
- `O63` : `IF(OR($B63="",$I63<>"Crédit-bail"),"","Non")`
- `O64` : `IF(OR($B64="",$I64<>"Crédit-bail"),"","Non")`
- `O65` : `IF(OR($B65="",$I65<>"Crédit-bail"),"","Non")`
- `O66` : `IF(OR($B66="",$I66<>"Crédit-bail"),"","Non")`
- `O67` : `IF(OR($B67="",$I67<>"Crédit-bail"),"","Non")`
- `O68` : `IF(OR($B68="",$I68<>"Crédit-bail"),"","Non")`
- `O69` : `IF(OR($B69="",$I69<>"Crédit-bail"),"","Non")`
- `O70` : `IF(OR($B70="",$I70<>"Crédit-bail"),"","Non")`
- `O71` : `IF(OR($B71="",$I71<>"Crédit-bail"),"","Non")`
- `O72` : `IF(OR($B72="",$I72<>"Crédit-bail"),"","Non")`

### Dernière date d’exploitation du bien loué

Identifiant : `data_capex_p13_p72`. Type : `date`. Zones : `P13:P72`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Acquisition/début de bail ou dernière date d’exploitation ; bornes d’amortissement et services.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS", "default_cells": ["P13", "P14", "P15", "P16", "P17", "P18", "P19", "P20", "P21", "P22", "P23", "P24", "P25", "P26", "P27", "P28", "P29", "P30", "P31", "P32", "P33", "P34", "P35", "P36", "P37", "P38", "P39", "P40", "P41", "P42", "P43", "P44", "P45", "P46", "P47", "P48", "P49", "P50", "P51", "P52", "P53", "P54", "P55", "P56", "P57", "P58", "P59", "P60", "P61", "P62", "P63", "P64", "P65", "P66", "P67", "P68", "P69", "P70", "P71", "P72"], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_cell_same_row": "E", "max_date": "9999-12-31"}, "choices": null}`.

Contraintes : `{"min_cell_same_row": "E", "max_date": "9999-12-31"}`.

Défauts calculés, remplaçables seulement sur source et accord explicites :

- `P13` : `IF(OR($B13="",$I13<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E13),N($E13)>0,ISNUMBER($J13),N($J13)>0,ABS(N($J13)*12-ROUND(N($J13)*12,0))<0.00000001),EDATE(DATE(YEAR($E13),MONTH($E13),1),ROUND(N($J13)*12,0))-1,""),""))`
- `P14` : `IF(OR($B14="",$I14<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E14),N($E14)>0,ISNUMBER($J14),N($J14)>0,ABS(N($J14)*12-ROUND(N($J14)*12,0))<0.00000001),EDATE(DATE(YEAR($E14),MONTH($E14),1),ROUND(N($J14)*12,0))-1,""),""))`
- `P15` : `IF(OR($B15="",$I15<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E15),N($E15)>0,ISNUMBER($J15),N($J15)>0,ABS(N($J15)*12-ROUND(N($J15)*12,0))<0.00000001),EDATE(DATE(YEAR($E15),MONTH($E15),1),ROUND(N($J15)*12,0))-1,""),""))`
- `P16` : `IF(OR($B16="",$I16<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E16),N($E16)>0,ISNUMBER($J16),N($J16)>0,ABS(N($J16)*12-ROUND(N($J16)*12,0))<0.00000001),EDATE(DATE(YEAR($E16),MONTH($E16),1),ROUND(N($J16)*12,0))-1,""),""))`
- `P17` : `IF(OR($B17="",$I17<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E17),N($E17)>0,ISNUMBER($J17),N($J17)>0,ABS(N($J17)*12-ROUND(N($J17)*12,0))<0.00000001),EDATE(DATE(YEAR($E17),MONTH($E17),1),ROUND(N($J17)*12,0))-1,""),""))`
- `P18` : `IF(OR($B18="",$I18<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E18),N($E18)>0,ISNUMBER($J18),N($J18)>0,ABS(N($J18)*12-ROUND(N($J18)*12,0))<0.00000001),EDATE(DATE(YEAR($E18),MONTH($E18),1),ROUND(N($J18)*12,0))-1,""),""))`
- `P19` : `IF(OR($B19="",$I19<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E19),N($E19)>0,ISNUMBER($J19),N($J19)>0,ABS(N($J19)*12-ROUND(N($J19)*12,0))<0.00000001),EDATE(DATE(YEAR($E19),MONTH($E19),1),ROUND(N($J19)*12,0))-1,""),""))`
- `P20` : `IF(OR($B20="",$I20<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E20),N($E20)>0,ISNUMBER($J20),N($J20)>0,ABS(N($J20)*12-ROUND(N($J20)*12,0))<0.00000001),EDATE(DATE(YEAR($E20),MONTH($E20),1),ROUND(N($J20)*12,0))-1,""),""))`
- `P21` : `IF(OR($B21="",$I21<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E21),N($E21)>0,ISNUMBER($J21),N($J21)>0,ABS(N($J21)*12-ROUND(N($J21)*12,0))<0.00000001),EDATE(DATE(YEAR($E21),MONTH($E21),1),ROUND(N($J21)*12,0))-1,""),""))`
- `P22` : `IF(OR($B22="",$I22<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E22),N($E22)>0,ISNUMBER($J22),N($J22)>0,ABS(N($J22)*12-ROUND(N($J22)*12,0))<0.00000001),EDATE(DATE(YEAR($E22),MONTH($E22),1),ROUND(N($J22)*12,0))-1,""),""))`
- `P23` : `IF(OR($B23="",$I23<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E23),N($E23)>0,ISNUMBER($J23),N($J23)>0,ABS(N($J23)*12-ROUND(N($J23)*12,0))<0.00000001),EDATE(DATE(YEAR($E23),MONTH($E23),1),ROUND(N($J23)*12,0))-1,""),""))`
- `P24` : `IF(OR($B24="",$I24<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E24),N($E24)>0,ISNUMBER($J24),N($J24)>0,ABS(N($J24)*12-ROUND(N($J24)*12,0))<0.00000001),EDATE(DATE(YEAR($E24),MONTH($E24),1),ROUND(N($J24)*12,0))-1,""),""))`
- `P25` : `IF(OR($B25="",$I25<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E25),N($E25)>0,ISNUMBER($J25),N($J25)>0,ABS(N($J25)*12-ROUND(N($J25)*12,0))<0.00000001),EDATE(DATE(YEAR($E25),MONTH($E25),1),ROUND(N($J25)*12,0))-1,""),""))`
- `P26` : `IF(OR($B26="",$I26<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E26),N($E26)>0,ISNUMBER($J26),N($J26)>0,ABS(N($J26)*12-ROUND(N($J26)*12,0))<0.00000001),EDATE(DATE(YEAR($E26),MONTH($E26),1),ROUND(N($J26)*12,0))-1,""),""))`
- `P27` : `IF(OR($B27="",$I27<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E27),N($E27)>0,ISNUMBER($J27),N($J27)>0,ABS(N($J27)*12-ROUND(N($J27)*12,0))<0.00000001),EDATE(DATE(YEAR($E27),MONTH($E27),1),ROUND(N($J27)*12,0))-1,""),""))`
- `P28` : `IF(OR($B28="",$I28<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E28),N($E28)>0,ISNUMBER($J28),N($J28)>0,ABS(N($J28)*12-ROUND(N($J28)*12,0))<0.00000001),EDATE(DATE(YEAR($E28),MONTH($E28),1),ROUND(N($J28)*12,0))-1,""),""))`
- `P29` : `IF(OR($B29="",$I29<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E29),N($E29)>0,ISNUMBER($J29),N($J29)>0,ABS(N($J29)*12-ROUND(N($J29)*12,0))<0.00000001),EDATE(DATE(YEAR($E29),MONTH($E29),1),ROUND(N($J29)*12,0))-1,""),""))`
- `P30` : `IF(OR($B30="",$I30<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E30),N($E30)>0,ISNUMBER($J30),N($J30)>0,ABS(N($J30)*12-ROUND(N($J30)*12,0))<0.00000001),EDATE(DATE(YEAR($E30),MONTH($E30),1),ROUND(N($J30)*12,0))-1,""),""))`
- `P31` : `IF(OR($B31="",$I31<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E31),N($E31)>0,ISNUMBER($J31),N($J31)>0,ABS(N($J31)*12-ROUND(N($J31)*12,0))<0.00000001),EDATE(DATE(YEAR($E31),MONTH($E31),1),ROUND(N($J31)*12,0))-1,""),""))`
- `P32` : `IF(OR($B32="",$I32<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E32),N($E32)>0,ISNUMBER($J32),N($J32)>0,ABS(N($J32)*12-ROUND(N($J32)*12,0))<0.00000001),EDATE(DATE(YEAR($E32),MONTH($E32),1),ROUND(N($J32)*12,0))-1,""),""))`
- `P33` : `IF(OR($B33="",$I33<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E33),N($E33)>0,ISNUMBER($J33),N($J33)>0,ABS(N($J33)*12-ROUND(N($J33)*12,0))<0.00000001),EDATE(DATE(YEAR($E33),MONTH($E33),1),ROUND(N($J33)*12,0))-1,""),""))`
- `P34` : `IF(OR($B34="",$I34<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E34),N($E34)>0,ISNUMBER($J34),N($J34)>0,ABS(N($J34)*12-ROUND(N($J34)*12,0))<0.00000001),EDATE(DATE(YEAR($E34),MONTH($E34),1),ROUND(N($J34)*12,0))-1,""),""))`
- `P35` : `IF(OR($B35="",$I35<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E35),N($E35)>0,ISNUMBER($J35),N($J35)>0,ABS(N($J35)*12-ROUND(N($J35)*12,0))<0.00000001),EDATE(DATE(YEAR($E35),MONTH($E35),1),ROUND(N($J35)*12,0))-1,""),""))`
- `P36` : `IF(OR($B36="",$I36<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E36),N($E36)>0,ISNUMBER($J36),N($J36)>0,ABS(N($J36)*12-ROUND(N($J36)*12,0))<0.00000001),EDATE(DATE(YEAR($E36),MONTH($E36),1),ROUND(N($J36)*12,0))-1,""),""))`
- `P37` : `IF(OR($B37="",$I37<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E37),N($E37)>0,ISNUMBER($J37),N($J37)>0,ABS(N($J37)*12-ROUND(N($J37)*12,0))<0.00000001),EDATE(DATE(YEAR($E37),MONTH($E37),1),ROUND(N($J37)*12,0))-1,""),""))`
- `P38` : `IF(OR($B38="",$I38<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E38),N($E38)>0,ISNUMBER($J38),N($J38)>0,ABS(N($J38)*12-ROUND(N($J38)*12,0))<0.00000001),EDATE(DATE(YEAR($E38),MONTH($E38),1),ROUND(N($J38)*12,0))-1,""),""))`
- `P39` : `IF(OR($B39="",$I39<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E39),N($E39)>0,ISNUMBER($J39),N($J39)>0,ABS(N($J39)*12-ROUND(N($J39)*12,0))<0.00000001),EDATE(DATE(YEAR($E39),MONTH($E39),1),ROUND(N($J39)*12,0))-1,""),""))`
- `P40` : `IF(OR($B40="",$I40<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E40),N($E40)>0,ISNUMBER($J40),N($J40)>0,ABS(N($J40)*12-ROUND(N($J40)*12,0))<0.00000001),EDATE(DATE(YEAR($E40),MONTH($E40),1),ROUND(N($J40)*12,0))-1,""),""))`
- `P41` : `IF(OR($B41="",$I41<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E41),N($E41)>0,ISNUMBER($J41),N($J41)>0,ABS(N($J41)*12-ROUND(N($J41)*12,0))<0.00000001),EDATE(DATE(YEAR($E41),MONTH($E41),1),ROUND(N($J41)*12,0))-1,""),""))`
- `P42` : `IF(OR($B42="",$I42<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E42),N($E42)>0,ISNUMBER($J42),N($J42)>0,ABS(N($J42)*12-ROUND(N($J42)*12,0))<0.00000001),EDATE(DATE(YEAR($E42),MONTH($E42),1),ROUND(N($J42)*12,0))-1,""),""))`
- `P43` : `IF(OR($B43="",$I43<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E43),N($E43)>0,ISNUMBER($J43),N($J43)>0,ABS(N($J43)*12-ROUND(N($J43)*12,0))<0.00000001),EDATE(DATE(YEAR($E43),MONTH($E43),1),ROUND(N($J43)*12,0))-1,""),""))`
- `P44` : `IF(OR($B44="",$I44<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E44),N($E44)>0,ISNUMBER($J44),N($J44)>0,ABS(N($J44)*12-ROUND(N($J44)*12,0))<0.00000001),EDATE(DATE(YEAR($E44),MONTH($E44),1),ROUND(N($J44)*12,0))-1,""),""))`
- `P45` : `IF(OR($B45="",$I45<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E45),N($E45)>0,ISNUMBER($J45),N($J45)>0,ABS(N($J45)*12-ROUND(N($J45)*12,0))<0.00000001),EDATE(DATE(YEAR($E45),MONTH($E45),1),ROUND(N($J45)*12,0))-1,""),""))`
- `P46` : `IF(OR($B46="",$I46<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E46),N($E46)>0,ISNUMBER($J46),N($J46)>0,ABS(N($J46)*12-ROUND(N($J46)*12,0))<0.00000001),EDATE(DATE(YEAR($E46),MONTH($E46),1),ROUND(N($J46)*12,0))-1,""),""))`
- `P47` : `IF(OR($B47="",$I47<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E47),N($E47)>0,ISNUMBER($J47),N($J47)>0,ABS(N($J47)*12-ROUND(N($J47)*12,0))<0.00000001),EDATE(DATE(YEAR($E47),MONTH($E47),1),ROUND(N($J47)*12,0))-1,""),""))`
- `P48` : `IF(OR($B48="",$I48<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E48),N($E48)>0,ISNUMBER($J48),N($J48)>0,ABS(N($J48)*12-ROUND(N($J48)*12,0))<0.00000001),EDATE(DATE(YEAR($E48),MONTH($E48),1),ROUND(N($J48)*12,0))-1,""),""))`
- `P49` : `IF(OR($B49="",$I49<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E49),N($E49)>0,ISNUMBER($J49),N($J49)>0,ABS(N($J49)*12-ROUND(N($J49)*12,0))<0.00000001),EDATE(DATE(YEAR($E49),MONTH($E49),1),ROUND(N($J49)*12,0))-1,""),""))`
- `P50` : `IF(OR($B50="",$I50<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E50),N($E50)>0,ISNUMBER($J50),N($J50)>0,ABS(N($J50)*12-ROUND(N($J50)*12,0))<0.00000001),EDATE(DATE(YEAR($E50),MONTH($E50),1),ROUND(N($J50)*12,0))-1,""),""))`
- `P51` : `IF(OR($B51="",$I51<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E51),N($E51)>0,ISNUMBER($J51),N($J51)>0,ABS(N($J51)*12-ROUND(N($J51)*12,0))<0.00000001),EDATE(DATE(YEAR($E51),MONTH($E51),1),ROUND(N($J51)*12,0))-1,""),""))`
- `P52` : `IF(OR($B52="",$I52<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E52),N($E52)>0,ISNUMBER($J52),N($J52)>0,ABS(N($J52)*12-ROUND(N($J52)*12,0))<0.00000001),EDATE(DATE(YEAR($E52),MONTH($E52),1),ROUND(N($J52)*12,0))-1,""),""))`
- `P53` : `IF(OR($B53="",$I53<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E53),N($E53)>0,ISNUMBER($J53),N($J53)>0,ABS(N($J53)*12-ROUND(N($J53)*12,0))<0.00000001),EDATE(DATE(YEAR($E53),MONTH($E53),1),ROUND(N($J53)*12,0))-1,""),""))`
- `P54` : `IF(OR($B54="",$I54<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E54),N($E54)>0,ISNUMBER($J54),N($J54)>0,ABS(N($J54)*12-ROUND(N($J54)*12,0))<0.00000001),EDATE(DATE(YEAR($E54),MONTH($E54),1),ROUND(N($J54)*12,0))-1,""),""))`
- `P55` : `IF(OR($B55="",$I55<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E55),N($E55)>0,ISNUMBER($J55),N($J55)>0,ABS(N($J55)*12-ROUND(N($J55)*12,0))<0.00000001),EDATE(DATE(YEAR($E55),MONTH($E55),1),ROUND(N($J55)*12,0))-1,""),""))`
- `P56` : `IF(OR($B56="",$I56<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E56),N($E56)>0,ISNUMBER($J56),N($J56)>0,ABS(N($J56)*12-ROUND(N($J56)*12,0))<0.00000001),EDATE(DATE(YEAR($E56),MONTH($E56),1),ROUND(N($J56)*12,0))-1,""),""))`
- `P57` : `IF(OR($B57="",$I57<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E57),N($E57)>0,ISNUMBER($J57),N($J57)>0,ABS(N($J57)*12-ROUND(N($J57)*12,0))<0.00000001),EDATE(DATE(YEAR($E57),MONTH($E57),1),ROUND(N($J57)*12,0))-1,""),""))`
- `P58` : `IF(OR($B58="",$I58<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E58),N($E58)>0,ISNUMBER($J58),N($J58)>0,ABS(N($J58)*12-ROUND(N($J58)*12,0))<0.00000001),EDATE(DATE(YEAR($E58),MONTH($E58),1),ROUND(N($J58)*12,0))-1,""),""))`
- `P59` : `IF(OR($B59="",$I59<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E59),N($E59)>0,ISNUMBER($J59),N($J59)>0,ABS(N($J59)*12-ROUND(N($J59)*12,0))<0.00000001),EDATE(DATE(YEAR($E59),MONTH($E59),1),ROUND(N($J59)*12,0))-1,""),""))`
- `P60` : `IF(OR($B60="",$I60<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E60),N($E60)>0,ISNUMBER($J60),N($J60)>0,ABS(N($J60)*12-ROUND(N($J60)*12,0))<0.00000001),EDATE(DATE(YEAR($E60),MONTH($E60),1),ROUND(N($J60)*12,0))-1,""),""))`
- `P61` : `IF(OR($B61="",$I61<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E61),N($E61)>0,ISNUMBER($J61),N($J61)>0,ABS(N($J61)*12-ROUND(N($J61)*12,0))<0.00000001),EDATE(DATE(YEAR($E61),MONTH($E61),1),ROUND(N($J61)*12,0))-1,""),""))`
- `P62` : `IF(OR($B62="",$I62<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E62),N($E62)>0,ISNUMBER($J62),N($J62)>0,ABS(N($J62)*12-ROUND(N($J62)*12,0))<0.00000001),EDATE(DATE(YEAR($E62),MONTH($E62),1),ROUND(N($J62)*12,0))-1,""),""))`
- `P63` : `IF(OR($B63="",$I63<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E63),N($E63)>0,ISNUMBER($J63),N($J63)>0,ABS(N($J63)*12-ROUND(N($J63)*12,0))<0.00000001),EDATE(DATE(YEAR($E63),MONTH($E63),1),ROUND(N($J63)*12,0))-1,""),""))`
- `P64` : `IF(OR($B64="",$I64<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E64),N($E64)>0,ISNUMBER($J64),N($J64)>0,ABS(N($J64)*12-ROUND(N($J64)*12,0))<0.00000001),EDATE(DATE(YEAR($E64),MONTH($E64),1),ROUND(N($J64)*12,0))-1,""),""))`
- `P65` : `IF(OR($B65="",$I65<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E65),N($E65)>0,ISNUMBER($J65),N($J65)>0,ABS(N($J65)*12-ROUND(N($J65)*12,0))<0.00000001),EDATE(DATE(YEAR($E65),MONTH($E65),1),ROUND(N($J65)*12,0))-1,""),""))`
- `P66` : `IF(OR($B66="",$I66<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E66),N($E66)>0,ISNUMBER($J66),N($J66)>0,ABS(N($J66)*12-ROUND(N($J66)*12,0))<0.00000001),EDATE(DATE(YEAR($E66),MONTH($E66),1),ROUND(N($J66)*12,0))-1,""),""))`
- `P67` : `IF(OR($B67="",$I67<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E67),N($E67)>0,ISNUMBER($J67),N($J67)>0,ABS(N($J67)*12-ROUND(N($J67)*12,0))<0.00000001),EDATE(DATE(YEAR($E67),MONTH($E67),1),ROUND(N($J67)*12,0))-1,""),""))`
- `P68` : `IF(OR($B68="",$I68<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E68),N($E68)>0,ISNUMBER($J68),N($J68)>0,ABS(N($J68)*12-ROUND(N($J68)*12,0))<0.00000001),EDATE(DATE(YEAR($E68),MONTH($E68),1),ROUND(N($J68)*12,0))-1,""),""))`
- `P69` : `IF(OR($B69="",$I69<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E69),N($E69)>0,ISNUMBER($J69),N($J69)>0,ABS(N($J69)*12-ROUND(N($J69)*12,0))<0.00000001),EDATE(DATE(YEAR($E69),MONTH($E69),1),ROUND(N($J69)*12,0))-1,""),""))`
- `P70` : `IF(OR($B70="",$I70<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E70),N($E70)>0,ISNUMBER($J70),N($J70)>0,ABS(N($J70)*12-ROUND(N($J70)*12,0))<0.00000001),EDATE(DATE(YEAR($E70),MONTH($E70),1),ROUND(N($J70)*12,0))-1,""),""))`
- `P71` : `IF(OR($B71="",$I71<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E71),N($E71)>0,ISNUMBER($J71),N($J71)>0,ABS(N($J71)*12-ROUND(N($J71)*12,0))<0.00000001),EDATE(DATE(YEAR($E71),MONTH($E71),1),ROUND(N($J71)*12,0))-1,""),""))`
- `P72` : `IF(OR($B72="",$I72<>"Crédit-bail"),"",IFERROR(IF(AND(ISNUMBER($E72),N($E72)>0,ISNUMBER($J72),N($J72)>0,ABS(N($J72)*12-ROUND(N($J72)*12,0))<0.00000001),EDATE(DATE(YEAR($E72),MONTH($E72),1),ROUND(N($J72)*12,0))-1,""),""))`

## Registre

Le coordinateur cherche une ligne libre dans le classeur courant, compare les identités déjà présentes et pose les questions manquantes avant de préparer une proposition.

```json
{
  "start_row": 13,
  "end_row": 72,
  "identity_columns": [
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "M",
    "N",
    "O",
    "P"
  ],
  "required": [
    "B",
    "C",
    "D",
    "E",
    "G",
    "I"
  ]
}
```

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Durée proposée — `DATA CAPEX!F13`

Unité : années. Défaut lu dans le catalogue de typologie ; absence ne vaut pas durée zéro.

```text
IF($C13="","",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C13,Assumptions!$B$98:$B$121,0)),""))
```

Sources directes extraites : `'DATA CAPEX'!$C13`, `'Assumptions'!$C$98:$C$121`, `'Assumptions'!$B$98:$B$121`.

### Complétude de l’actif — `DATA CAPEX!L13`

Unité : diagnostic. Nature, date, montant, affectation R&D et paramètres du bail doivent être compatibles.

```text
IF(IF(AND($B13<>"",NOT(OR($M13="Corporelle",$M13="Incorporelle"))),"⚠ nature d'immobilisation vide ou invalide",IF($B13="","",IF(IFERROR(MATCH($C13,Assumptions!$B$98:$B$121,0),0)=0,"⚠ typologie hors catalogue",IF(OR(N($D13)=0,$E13="",N($F13)=0),"⚠ incomplet",IF(AND($G13="Non",N($H13)>0),"⚠ R&D Non avec % > 0",IF(AND($G13="Oui",N($H13)=0),"⚠ R&D Oui avec % = 0",IF($I13="Crédit-bail",IF(NOT(AND(ISNUMBER($J13),N($J13)>0,ABS(N($J13)*12-ROUND(N($J13)*12,0))<0.00000001)),"⚠ bail incomplet ou invalide : durée positive en mois entiers",IF(NOT(AND(ISNUMBER($K13),N($K13)>=0)),"⚠ bail incomplet ou invalide : taux numérique positif ou nul","OK")),"OK")))))))<>"OK",IF(AND($B13<>"",NOT(OR($M13="Corporelle",$M13="Incorporelle"))),"⚠ nature d'immobilisation vide ou invalide",IF($B13="","",IF(IFERROR(MATCH($C13,Assumptions!$B$98:$B$121,0),0)=0,"⚠ typologie hors catalogue",IF(OR(N($D13)=0,$E13="",N($F13)=0),"⚠ incomplet",IF(AND($G13="Non",N($H13)>0),"⚠ R&D Non avec % > 0",IF(AND($G13="Oui",N($H13)=0),"⚠ R&D Oui avec % = 0",IF($I13="Crédit-bail",IF(NOT(AND(ISNUMBER($J13),N($J13)>0,ABS(N($J13)*12-ROUND(N($J13)*12,0))<0.00000001)),"⚠ bail incomplet ou invalide : durée positive en mois entiers",IF(NOT(AND(ISNUMBER($K13),N($K13)>=0)),"⚠ bail incomplet ou invalide : taux numérique positif ou nul","OK")),"OK"))))))),IF($I13<>"Crédit-bail","OK",IF(NOT(OR($N13="Oui",$N13="Non")),"⚠ entretien : choisir Oui ou Non",IF(NOT(OR($O13="Oui",$O13="Non")),"⚠ assurance : choisir Oui ou Non",IF(NOT(IFERROR(AND(ISNUMBER($P13),$P13>=$E13,$P13<DATE(9999,12,31)+1),FALSE)),"⚠ fin d’exploitation CB vide ou invalide","OK")))))
```

Sources directes extraites : `'DATA CAPEX'!$B13`, `'DATA CAPEX'!$M13`, `'DATA CAPEX'!$C13`, `'Assumptions'!$B$98:$B$121`, `'DATA CAPEX'!$D13`, `'DATA CAPEX'!$E13`, `'DATA CAPEX'!$F13`, `'DATA CAPEX'!$G13`, `'DATA CAPEX'!$H13`, `'DATA CAPEX'!$I13`, `'DATA CAPEX'!$J13`, `'DATA CAPEX'!$K13`, `'DATA CAPEX'!$N13`, `'DATA CAPEX'!$O13`, `'DATA CAPEX'!$P13`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_14 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Actif identifié 12 000 EUR, acquis début année, Cash, durée explicitement 3 ans ; puis supprimer sa date.

Attendu : Le premier lot peut être proposé avec source ; le second doit demander la date, sans créer un investissement au mois zéro.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
