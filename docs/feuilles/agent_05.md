# DATA Contrats

Responsabilité : **Préparer les contrats identifiés et leurs conditions commerciales.**

Contrat : `AGENT_05`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Objectif commercial, affaire probable ou contrat signé ?
- Quelle offre, quel client, quelle quantité et quel prix unitaire HT ?
- Quelles dates de prestation, de facturation et quelles conditions de paiement ?
- Quel régime TVA est confirmé par la pièce ?

## Règles et contrôles métier

- Ne pas enregistrer deux fois la même affaire.
- Distinguer prix unitaire, total, HT et TTC.
- Chaque tranche positive possède une date.

## Dépendances

Sources métier du contrat : Assumptions, Control.

Sources directes extraites : Assumptions, Control, Sensi TCA.

Feuilles qui consomment directement cette feuille : ATELIER_CIR_IS, Contrats, Contrôles, Revenue.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Client / affaire

Identifiant : `contract_client`. Type : `text`. Zones : `B14:B413`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité de la contrepartie ou de l’affaire ; distingue les lignes du registre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32", "B33", "B34", "B35", "B36", "B37", "B38", "B39", "B40", "B41", "B42", "B43", "B44", "B45", "B46", "B47", "B48", "B49", "B50", "B51", "B52", "B53", "B54", "B55", "B56", "B57", "B58", "B59", "B60", "B61", "B62", "B63", "B64", "B65", "B66", "B67", "B68", "B69", "B70", "B71", "B72", "B73", "B74", "B75", "B76", "B77", "B78", "B79", "B80", "B81", "B82", "B83", "B84", "B85", "B86", "B87", "B88", "B89", "B90", "B91", "B92", "B93", "B94", "B95", "B96", "B97", "B98", "B99", "B100", "B101", "B102", "B103", "B104", "B105", "B106", "B107", "B108", "B109", "B110", "B111", "B112", "B113", "B114", "B115", "B116", "B117", "B118", "B119", "B120", "B121", "B122", "B123", "B124", "B125", "B126", "B127", "B128", "B129", "B130", "B131", "B132", "B133", "B134", "B135", "B136", "B137", "B138", "B139", "B140", "B141", "B142", "B143", "B144", "B145", "B146", "B147", "B148", "B149", "B150", "B151", "B152", "B153", "B154", "B155", "B156", "B157", "B158", "B159", "B160", "B161", "B162", "B163", "B164", "B165", "B166", "B167", "B168", "B169", "B170", "B171", "B172", "B173", "B174", "B175", "B176", "B177", "B178", "B179", "B180", "B181", "B182", "B183", "B184", "B185", "B186", "B187", "B188", "B189", "B190", "B191", "B192", "B193", "B194", "B195", "B196", "B197", "B198", "B199", "B200", "B201", "B202", "B203", "B204", "B205", "B206", "B207", "B208", "B209", "B210", "B211", "B212", "B213", "B214", "B215", "B216", "B217", "B218", "B219", "B220", "B221", "B222", "B223", "B224", "B225", "B226", "B227", "B228", "B229", "B230", "B231", "B232", "B233", "B234", "B235", "B236", "B237", "B238", "B239", "B240", "B241", "B242", "B243", "B244", "B245", "B246", "B247", "B248", "B249", "B250", "B251", "B252", "B253", "B254", "B255", "B256", "B257", "B258", "B259", "B260", "B261", "B262", "B263", "B264", "B265", "B266", "B267", "B268", "B269", "B270", "B271", "B272", "B273", "B274", "B275", "B276", "B277", "B278", "B279", "B280", "B281", "B282", "B283", "B284", "B285", "B286", "B287", "B288", "B289", "B290", "B291", "B292", "B293", "B294", "B295", "B296", "B297", "B298", "B299", "B300", "B301", "B302", "B303", "B304", "B305", "B306", "B307", "B308", "B309", "B310", "B311", "B312", "B313", "B314", "B315", "B316", "B317", "B318", "B319", "B320", "B321", "B322", "B323", "B324", "B325", "B326", "B327", "B328", "B329", "B330", "B331", "B332", "B333", "B334", "B335", "B336", "B337", "B338", "B339", "B340", "B341", "B342", "B343", "B344", "B345", "B346", "B347", "B348", "B349", "B350", "B351", "B352", "B353", "B354", "B355", "B356", "B357", "B358", "B359", "B360", "B361", "B362", "B363", "B364", "B365", "B366", "B367", "B368", "B369", "B370", "B371", "B372", "B373", "B374", "B375", "B376", "B377", "B378", "B379", "B380", "B381", "B382", "B383", "B384", "B385", "B386", "B387", "B388", "B389", "B390", "B391", "B392", "B393", "B394", "B395", "B396", "B397", "B398", "B399", "B400", "B401", "B402", "B403", "B404", "B405", "B406", "B407", "B408", "B409", "B410", "B411", "B412", "B413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Prestation

Identifiant : `contract_offer`. Type : `enum`. Zones : `C14:C413`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Identifiant de l’offre rattachée à la ligne de contrat.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : offer_label, offer_active, offer_unit.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C86", "C87", "C88", "C89", "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97", "C98", "C99", "C100", "C101", "C102", "C103", "C104", "C105", "C106", "C107", "C108", "C109", "C110", "C111", "C112", "C113", "C114", "C115", "C116", "C117", "C118", "C119", "C120", "C121", "C122", "C123", "C124", "C125", "C126", "C127", "C128", "C129", "C130", "C131", "C132", "C133", "C134", "C135", "C136", "C137", "C138", "C139", "C140", "C141", "C142", "C143", "C144", "C145", "C146", "C147", "C148", "C149", "C150", "C151", "C152", "C153", "C154", "C155", "C156", "C157", "C158", "C159", "C160", "C161", "C162", "C163", "C164", "C165", "C166", "C167", "C168", "C169", "C170", "C171", "C172", "C173", "C174", "C175", "C176", "C177", "C178", "C179", "C180", "C181", "C182", "C183", "C184", "C185", "C186", "C187", "C188", "C189", "C190", "C191", "C192", "C193", "C194", "C195", "C196", "C197", "C198", "C199", "C200", "C201", "C202", "C203", "C204", "C205", "C206", "C207", "C208", "C209", "C210", "C211", "C212", "C213", "C214", "C215", "C216", "C217", "C218", "C219", "C220", "C221", "C222", "C223", "C224", "C225", "C226", "C227", "C228", "C229", "C230", "C231", "C232", "C233", "C234", "C235", "C236", "C237", "C238", "C239", "C240", "C241", "C242", "C243", "C244", "C245", "C246", "C247", "C248", "C249", "C250", "C251", "C252", "C253", "C254", "C255", "C256", "C257", "C258", "C259", "C260", "C261", "C262", "C263", "C264", "C265", "C266", "C267", "C268", "C269", "C270", "C271", "C272", "C273", "C274", "C275", "C276", "C277", "C278", "C279", "C280", "C281", "C282", "C283", "C284", "C285", "C286", "C287", "C288", "C289", "C290", "C291", "C292", "C293", "C294", "C295", "C296", "C297", "C298", "C299", "C300", "C301", "C302", "C303", "C304", "C305", "C306", "C307", "C308", "C309", "C310", "C311", "C312", "C313", "C314", "C315", "C316", "C317", "C318", "C319", "C320", "C321", "C322", "C323", "C324", "C325", "C326", "C327", "C328", "C329", "C330", "C331", "C332", "C333", "C334", "C335", "C336", "C337", "C338", "C339", "C340", "C341", "C342", "C343", "C344", "C345", "C346", "C347", "C348", "C349", "C350", "C351", "C352", "C353", "C354", "C355", "C356", "C357", "C358", "C359", "C360", "C361", "C362", "C363", "C364", "C365", "C366", "C367", "C368", "C369", "C370", "C371", "C372", "C373", "C374", "C375", "C376", "C377", "C378", "C379", "C380", "C381", "C382", "C383", "C384", "C385", "C386", "C387", "C388", "C389", "C390", "C391", "C392", "C393", "C394", "C395", "C396", "C397", "C398", "C399", "C400", "C401", "C402", "C403", "C404", "C405", "C406", "C407", "C408", "C409", "C410", "C411", "C412", "C413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Offre 01", "Offre 02", "Offre 03", "Offre 04", "Offre 05", "Offre 06", "Offre 07", "Offre 08", "Offre 09", "Offre 10", "Offre 11", "Offre 12", "Offre 13"]}`.

Choix du catalogue : ["Offre 01", "Offre 02", "Offre 03", "Offre 04", "Offre 05", "Offre 06", "Offre 07", "Offre 08", "Offre 09", "Offre 10", "Offre 11", "Offre 12", "Offre 13"].

Liste dynamique Libelles_Prestations = Assumptions!$B$15:$B$27. Résoudre à nouveau après une modification autorisée du catalogue.

### Quantité

Identifiant : `contract_quantity`. Type : `number`. Zones : `E14:E413`.

Unité explicite : unité de l’offre désignée par offer_unit.

Assiette : Quantité contractuelle totale ; le prix unitaire reste séparé.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_offer, contract_unit_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40", "E41", "E42", "E43", "E44", "E45", "E46", "E47", "E48", "E49", "E50", "E51", "E52", "E53", "E54", "E55", "E56", "E57", "E58", "E59", "E60", "E61", "E62", "E63", "E64", "E65", "E66", "E67", "E68", "E69", "E70", "E71", "E72", "E73", "E74", "E75", "E76", "E77", "E78", "E79", "E80", "E81", "E82", "E83", "E84", "E85", "E86", "E87", "E88", "E89", "E90", "E91", "E92", "E93", "E94", "E95", "E96", "E97", "E98", "E99", "E100", "E101", "E102", "E103", "E104", "E105", "E106", "E107", "E108", "E109", "E110", "E111", "E112", "E113", "E114", "E115", "E116", "E117", "E118", "E119", "E120", "E121", "E122", "E123", "E124", "E125", "E126", "E127", "E128", "E129", "E130", "E131", "E132", "E133", "E134", "E135", "E136", "E137", "E138", "E139", "E140", "E141", "E142", "E143", "E144", "E145", "E146", "E147", "E148", "E149", "E150", "E151", "E152", "E153", "E154", "E155", "E156", "E157", "E158", "E159", "E160", "E161", "E162", "E163", "E164", "E165", "E166", "E167", "E168", "E169", "E170", "E171", "E172", "E173", "E174", "E175", "E176", "E177", "E178", "E179", "E180", "E181", "E182", "E183", "E184", "E185", "E186", "E187", "E188", "E189", "E190", "E191", "E192", "E193", "E194", "E195", "E196", "E197", "E198", "E199", "E200", "E201", "E202", "E203", "E204", "E205", "E206", "E207", "E208", "E209", "E210", "E211", "E212", "E213", "E214", "E215", "E216", "E217", "E218", "E219", "E220", "E221", "E222", "E223", "E224", "E225", "E226", "E227", "E228", "E229", "E230", "E231", "E232", "E233", "E234", "E235", "E236", "E237", "E238", "E239", "E240", "E241", "E242", "E243", "E244", "E245", "E246", "E247", "E248", "E249", "E250", "E251", "E252", "E253", "E254", "E255", "E256", "E257", "E258", "E259", "E260", "E261", "E262", "E263", "E264", "E265", "E266", "E267", "E268", "E269", "E270", "E271", "E272", "E273", "E274", "E275", "E276", "E277", "E278", "E279", "E280", "E281", "E282", "E283", "E284", "E285", "E286", "E287", "E288", "E289", "E290", "E291", "E292", "E293", "E294", "E295", "E296", "E297", "E298", "E299", "E300", "E301", "E302", "E303", "E304", "E305", "E306", "E307", "E308", "E309", "E310", "E311", "E312", "E313", "E314", "E315", "E316", "E317", "E318", "E319", "E320", "E321", "E322", "E323", "E324", "E325", "E326", "E327", "E328", "E329", "E330", "E331", "E332", "E333", "E334", "E335", "E336", "E337", "E338", "E339", "E340", "E341", "E342", "E343", "E344", "E345", "E346", "E347", "E348", "E349", "E350", "E351", "E352", "E353", "E354", "E355", "E356", "E357", "E358", "E359", "E360", "E361", "E362", "E363", "E364", "E365", "E366", "E367", "E368", "E369", "E370", "E371", "E372", "E373", "E374", "E375", "E376", "E377", "E378", "E379", "E380", "E381", "E382", "E383", "E384", "E385", "E386", "E387", "E388", "E389", "E390", "E391", "E392", "E393", "E394", "E395", "E396", "E397", "E398", "E399", "E400", "E401", "E402", "E403", "E404", "E405", "E406", "E407", "E408", "E409", "E410", "E411", "E412", "E413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"exclusive_min": 0}, "choices": null}`.

Contraintes : `{"exclusive_min": 0}`.

### Prix négocié

Identifiant : `contract_unit_price`. Type : `number`. Zones : `F14:F413`.

Unité explicite : EUR HT par unité contractuelle.

Assiette : Prix négocié unitaire du contrat, conservé avec sa cohorte ; montant brut = quantité × prix.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_offer, contract_quantity.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "F25", "F26", "F27", "F28", "F29", "F30", "F31", "F32", "F33", "F34", "F35", "F36", "F37", "F38", "F39", "F40", "F41", "F42", "F43", "F44", "F45", "F46", "F47", "F48", "F49", "F50", "F51", "F52", "F53", "F54", "F55", "F56", "F57", "F58", "F59", "F60", "F61", "F62", "F63", "F64", "F65", "F66", "F67", "F68", "F69", "F70", "F71", "F72", "F73", "F74", "F75", "F76", "F77", "F78", "F79", "F80", "F81", "F82", "F83", "F84", "F85", "F86", "F87", "F88", "F89", "F90", "F91", "F92", "F93", "F94", "F95", "F96", "F97", "F98", "F99", "F100", "F101", "F102", "F103", "F104", "F105", "F106", "F107", "F108", "F109", "F110", "F111", "F112", "F113", "F114", "F115", "F116", "F117", "F118", "F119", "F120", "F121", "F122", "F123", "F124", "F125", "F126", "F127", "F128", "F129", "F130", "F131", "F132", "F133", "F134", "F135", "F136", "F137", "F138", "F139", "F140", "F141", "F142", "F143", "F144", "F145", "F146", "F147", "F148", "F149", "F150", "F151", "F152", "F153", "F154", "F155", "F156", "F157", "F158", "F159", "F160", "F161", "F162", "F163", "F164", "F165", "F166", "F167", "F168", "F169", "F170", "F171", "F172", "F173", "F174", "F175", "F176", "F177", "F178", "F179", "F180", "F181", "F182", "F183", "F184", "F185", "F186", "F187", "F188", "F189", "F190", "F191", "F192", "F193", "F194", "F195", "F196", "F197", "F198", "F199", "F200", "F201", "F202", "F203", "F204", "F205", "F206", "F207", "F208", "F209", "F210", "F211", "F212", "F213", "F214", "F215", "F216", "F217", "F218", "F219", "F220", "F221", "F222", "F223", "F224", "F225", "F226", "F227", "F228", "F229", "F230", "F231", "F232", "F233", "F234", "F235", "F236", "F237", "F238", "F239", "F240", "F241", "F242", "F243", "F244", "F245", "F246", "F247", "F248", "F249", "F250", "F251", "F252", "F253", "F254", "F255", "F256", "F257", "F258", "F259", "F260", "F261", "F262", "F263", "F264", "F265", "F266", "F267", "F268", "F269", "F270", "F271", "F272", "F273", "F274", "F275", "F276", "F277", "F278", "F279", "F280", "F281", "F282", "F283", "F284", "F285", "F286", "F287", "F288", "F289", "F290", "F291", "F292", "F293", "F294", "F295", "F296", "F297", "F298", "F299", "F300", "F301", "F302", "F303", "F304", "F305", "F306", "F307", "F308", "F309", "F310", "F311", "F312", "F313", "F314", "F315", "F316", "F317", "F318", "F319", "F320", "F321", "F322", "F323", "F324", "F325", "F326", "F327", "F328", "F329", "F330", "F331", "F332", "F333", "F334", "F335", "F336", "F337", "F338", "F339", "F340", "F341", "F342", "F343", "F344", "F345", "F346", "F347", "F348", "F349", "F350", "F351", "F352", "F353", "F354", "F355", "F356", "F357", "F358", "F359", "F360", "F361", "F362", "F363", "F364", "F365", "F366", "F367", "F368", "F369", "F370", "F371", "F372", "F373", "F374", "F375", "F376", "F377", "F378", "F379", "F380", "F381", "F382", "F383", "F384", "F385", "F386", "F387", "F388", "F389", "F390", "F391", "F392", "F393", "F394", "F395", "F396", "F397", "F398", "F399", "F400", "F401", "F402", "F403", "F404", "F405", "F406", "F407", "F408", "F409", "F410", "F411", "F412", "F413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"exclusive_min": 0}, "choices": null}`.

Contraintes : `{"exclusive_min": 0}`.

### Début du contrat

Identifiant : `contract_start`. Type : `date`. Zones : `H14:H413`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Début/fin réels de la prestation contractuelle ; fin au moins égale au début.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, active_horizon_years, contract_recognition.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["H14", "H15", "H16", "H17", "H18", "H19", "H20", "H21", "H22", "H23", "H24", "H25", "H26", "H27", "H28", "H29", "H30", "H31", "H32", "H33", "H34", "H35", "H36", "H37", "H38", "H39", "H40", "H41", "H42", "H43", "H44", "H45", "H46", "H47", "H48", "H49", "H50", "H51", "H52", "H53", "H54", "H55", "H56", "H57", "H58", "H59", "H60", "H61", "H62", "H63", "H64", "H65", "H66", "H67", "H68", "H69", "H70", "H71", "H72", "H73", "H74", "H75", "H76", "H77", "H78", "H79", "H80", "H81", "H82", "H83", "H84", "H85", "H86", "H87", "H88", "H89", "H90", "H91", "H92", "H93", "H94", "H95", "H96", "H97", "H98", "H99", "H100", "H101", "H102", "H103", "H104", "H105", "H106", "H107", "H108", "H109", "H110", "H111", "H112", "H113", "H114", "H115", "H116", "H117", "H118", "H119", "H120", "H121", "H122", "H123", "H124", "H125", "H126", "H127", "H128", "H129", "H130", "H131", "H132", "H133", "H134", "H135", "H136", "H137", "H138", "H139", "H140", "H141", "H142", "H143", "H144", "H145", "H146", "H147", "H148", "H149", "H150", "H151", "H152", "H153", "H154", "H155", "H156", "H157", "H158", "H159", "H160", "H161", "H162", "H163", "H164", "H165", "H166", "H167", "H168", "H169", "H170", "H171", "H172", "H173", "H174", "H175", "H176", "H177", "H178", "H179", "H180", "H181", "H182", "H183", "H184", "H185", "H186", "H187", "H188", "H189", "H190", "H191", "H192", "H193", "H194", "H195", "H196", "H197", "H198", "H199", "H200", "H201", "H202", "H203", "H204", "H205", "H206", "H207", "H208", "H209", "H210", "H211", "H212", "H213", "H214", "H215", "H216", "H217", "H218", "H219", "H220", "H221", "H222", "H223", "H224", "H225", "H226", "H227", "H228", "H229", "H230", "H231", "H232", "H233", "H234", "H235", "H236", "H237", "H238", "H239", "H240", "H241", "H242", "H243", "H244", "H245", "H246", "H247", "H248", "H249", "H250", "H251", "H252", "H253", "H254", "H255", "H256", "H257", "H258", "H259", "H260", "H261", "H262", "H263", "H264", "H265", "H266", "H267", "H268", "H269", "H270", "H271", "H272", "H273", "H274", "H275", "H276", "H277", "H278", "H279", "H280", "H281", "H282", "H283", "H284", "H285", "H286", "H287", "H288", "H289", "H290", "H291", "H292", "H293", "H294", "H295", "H296", "H297", "H298", "H299", "H300", "H301", "H302", "H303", "H304", "H305", "H306", "H307", "H308", "H309", "H310", "H311", "H312", "H313", "H314", "H315", "H316", "H317", "H318", "H319", "H320", "H321", "H322", "H323", "H324", "H325", "H326", "H327", "H328", "H329", "H330", "H331", "H332", "H333", "H334", "H335", "H336", "H337", "H338", "H339", "H340", "H341", "H342", "H343", "H344", "H345", "H346", "H347", "H348", "H349", "H350", "H351", "H352", "H353", "H354", "H355", "H356", "H357", "H358", "H359", "H360", "H361", "H362", "H363", "H364", "H365", "H366", "H367", "H368", "H369", "H370", "H371", "H372", "H373", "H374", "H375", "H376", "H377", "H378", "H379", "H380", "H381", "H382", "H383", "H384", "H385", "H386", "H387", "H388", "H389", "H390", "H391", "H392", "H393", "H394", "H395", "H396", "H397", "H398", "H399", "H400", "H401", "H402", "H403", "H404", "H405", "H406", "H407", "H408", "H409", "H410", "H411", "H412", "H413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Date de fin ≥ date de début. Les dates doivent être des dates Excel numériques, pas du texte affichant une date.

### Fin du contrat

Identifiant : `contract_end`. Type : `date`. Zones : `I14:I413`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Début/fin réels de la prestation contractuelle ; fin au moins égale au début.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, active_horizon_years, contract_recognition.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["I14", "I15", "I16", "I17", "I18", "I19", "I20", "I21", "I22", "I23", "I24", "I25", "I26", "I27", "I28", "I29", "I30", "I31", "I32", "I33", "I34", "I35", "I36", "I37", "I38", "I39", "I40", "I41", "I42", "I43", "I44", "I45", "I46", "I47", "I48", "I49", "I50", "I51", "I52", "I53", "I54", "I55", "I56", "I57", "I58", "I59", "I60", "I61", "I62", "I63", "I64", "I65", "I66", "I67", "I68", "I69", "I70", "I71", "I72", "I73", "I74", "I75", "I76", "I77", "I78", "I79", "I80", "I81", "I82", "I83", "I84", "I85", "I86", "I87", "I88", "I89", "I90", "I91", "I92", "I93", "I94", "I95", "I96", "I97", "I98", "I99", "I100", "I101", "I102", "I103", "I104", "I105", "I106", "I107", "I108", "I109", "I110", "I111", "I112", "I113", "I114", "I115", "I116", "I117", "I118", "I119", "I120", "I121", "I122", "I123", "I124", "I125", "I126", "I127", "I128", "I129", "I130", "I131", "I132", "I133", "I134", "I135", "I136", "I137", "I138", "I139", "I140", "I141", "I142", "I143", "I144", "I145", "I146", "I147", "I148", "I149", "I150", "I151", "I152", "I153", "I154", "I155", "I156", "I157", "I158", "I159", "I160", "I161", "I162", "I163", "I164", "I165", "I166", "I167", "I168", "I169", "I170", "I171", "I172", "I173", "I174", "I175", "I176", "I177", "I178", "I179", "I180", "I181", "I182", "I183", "I184", "I185", "I186", "I187", "I188", "I189", "I190", "I191", "I192", "I193", "I194", "I195", "I196", "I197", "I198", "I199", "I200", "I201", "I202", "I203", "I204", "I205", "I206", "I207", "I208", "I209", "I210", "I211", "I212", "I213", "I214", "I215", "I216", "I217", "I218", "I219", "I220", "I221", "I222", "I223", "I224", "I225", "I226", "I227", "I228", "I229", "I230", "I231", "I232", "I233", "I234", "I235", "I236", "I237", "I238", "I239", "I240", "I241", "I242", "I243", "I244", "I245", "I246", "I247", "I248", "I249", "I250", "I251", "I252", "I253", "I254", "I255", "I256", "I257", "I258", "I259", "I260", "I261", "I262", "I263", "I264", "I265", "I266", "I267", "I268", "I269", "I270", "I271", "I272", "I273", "I274", "I275", "I276", "I277", "I278", "I279", "I280", "I281", "I282", "I283", "I284", "I285", "I286", "I287", "I288", "I289", "I290", "I291", "I292", "I293", "I294", "I295", "I296", "I297", "I298", "I299", "I300", "I301", "I302", "I303", "I304", "I305", "I306", "I307", "I308", "I309", "I310", "I311", "I312", "I313", "I314", "I315", "I316", "I317", "I318", "I319", "I320", "I321", "I322", "I323", "I324", "I325", "I326", "I327", "I328", "I329", "I330", "I331", "I332", "I333", "I334", "I335", "I336", "I337", "I338", "I339", "I340", "I341", "I342", "I343", "I344", "I345", "I346", "I347", "I348", "I349", "I350", "I351", "I352", "I353", "I354", "I355", "I356", "I357", "I358", "I359", "I360", "I361", "I362", "I363", "I364", "I365", "I366", "I367", "I368", "I369", "I370", "I371", "I372", "I373", "I374", "I375", "I376", "I377", "I378", "I379", "I380", "I381", "I382", "I383", "I384", "I385", "I386", "I387", "I388", "I389", "I390", "I391", "I392", "I393", "I394", "I395", "I396", "I397", "I398", "I399", "I400", "I401", "I402", "I403", "I404", "I405", "I406", "I407", "I408", "I409", "I410", "I411", "I412", "I413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

Date de fin ≥ date de début. Les dates doivent être des dates Excel numériques, pas du texte affichant une date.

### Mode de reconnaissance

Identifiant : `contract_recognition`. Type : `enum`. Zones : `J14:J413`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Répartition du CA reconnu ; distincte de la facturation et du cash.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_start, contract_end, contract_quantity.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["J14", "J15", "J16", "J17", "J18", "J19", "J20", "J21", "J22", "J23", "J24", "J25", "J26", "J27", "J28", "J29", "J30", "J31", "J32", "J33", "J34", "J35", "J36", "J37", "J38", "J39", "J40", "J41", "J42", "J43", "J44", "J45", "J46", "J47", "J48", "J49", "J50", "J51", "J52", "J53", "J54", "J55", "J56", "J57", "J58", "J59", "J60", "J61", "J62", "J63", "J64", "J65", "J66", "J67", "J68", "J69", "J70", "J71", "J72", "J73", "J74", "J75", "J76", "J77", "J78", "J79", "J80", "J81", "J82", "J83", "J84", "J85", "J86", "J87", "J88", "J89", "J90", "J91", "J92", "J93", "J94", "J95", "J96", "J97", "J98", "J99", "J100", "J101", "J102", "J103", "J104", "J105", "J106", "J107", "J108", "J109", "J110", "J111", "J112", "J113", "J114", "J115", "J116", "J117", "J118", "J119", "J120", "J121", "J122", "J123", "J124", "J125", "J126", "J127", "J128", "J129", "J130", "J131", "J132", "J133", "J134", "J135", "J136", "J137", "J138", "J139", "J140", "J141", "J142", "J143", "J144", "J145", "J146", "J147", "J148", "J149", "J150", "J151", "J152", "J153", "J154", "J155", "J156", "J157", "J158", "J159", "J160", "J161", "J162", "J163", "J164", "J165", "J166", "J167", "J168", "J169", "J170", "J171", "J172", "J173", "J174", "J175", "J176", "J177", "J178", "J179", "J180", "J181", "J182", "J183", "J184", "J185", "J186", "J187", "J188", "J189", "J190", "J191", "J192", "J193", "J194", "J195", "J196", "J197", "J198", "J199", "J200", "J201", "J202", "J203", "J204", "J205", "J206", "J207", "J208", "J209", "J210", "J211", "J212", "J213", "J214", "J215", "J216", "J217", "J218", "J219", "J220", "J221", "J222", "J223", "J224", "J225", "J226", "J227", "J228", "J229", "J230", "J231", "J232", "J233", "J234", "J235", "J236", "J237", "J238", "J239", "J240", "J241", "J242", "J243", "J244", "J245", "J246", "J247", "J248", "J249", "J250", "J251", "J252", "J253", "J254", "J255", "J256", "J257", "J258", "J259", "J260", "J261", "J262", "J263", "J264", "J265", "J266", "J267", "J268", "J269", "J270", "J271", "J272", "J273", "J274", "J275", "J276", "J277", "J278", "J279", "J280", "J281", "J282", "J283", "J284", "J285", "J286", "J287", "J288", "J289", "J290", "J291", "J292", "J293", "J294", "J295", "J296", "J297", "J298", "J299", "J300", "J301", "J302", "J303", "J304", "J305", "J306", "J307", "J308", "J309", "J310", "J311", "J312", "J313", "J314", "J315", "J316", "J317", "J318", "J319", "J320", "J321", "J322", "J323", "J324", "J325", "J326", "J327", "J328", "J329", "J330", "J331", "J332", "J333", "J334", "J335", "J336", "J337", "J338", "J339", "J340", "J341", "J342", "J343", "J344", "J345", "J346", "J347", "J348", "J349", "J350", "J351", "J352", "J353", "J354", "J355", "J356", "J357", "J358", "J359", "J360", "J361", "J362", "J363", "J364", "J365", "J366", "J367", "J368", "J369", "J370", "J371", "J372", "J373", "J374", "J375", "J376", "J377", "J378", "J379", "J380", "J381", "J382", "J383", "J384", "J385", "J386", "J387", "J388", "J389", "J390", "J391", "J392", "J393", "J394", "J395", "J396", "J397", "J398", "J399", "J400", "J401", "J402", "J403", "J404", "J405", "J406", "J407", "J408", "J409", "J410", "J411", "J412", "J413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Etalee sur la duree", "Fin de contrat"]}`.

Choix du catalogue : ["Etalee sur la duree", "Fin de contrat"].

### Mode de facturation

Identifiant : `contract_invoicing`. Type : `enum`. Zones : `K14:K413`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Échéancier de facturation du montant contractuel.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_start, contract_end, contract_deposit_rate, contract_milestone_rate.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["K14", "K15", "K16", "K17", "K18", "K19", "K20", "K21", "K22", "K23", "K24", "K25", "K26", "K27", "K28", "K29", "K30", "K31", "K32", "K33", "K34", "K35", "K36", "K37", "K38", "K39", "K40", "K41", "K42", "K43", "K44", "K45", "K46", "K47", "K48", "K49", "K50", "K51", "K52", "K53", "K54", "K55", "K56", "K57", "K58", "K59", "K60", "K61", "K62", "K63", "K64", "K65", "K66", "K67", "K68", "K69", "K70", "K71", "K72", "K73", "K74", "K75", "K76", "K77", "K78", "K79", "K80", "K81", "K82", "K83", "K84", "K85", "K86", "K87", "K88", "K89", "K90", "K91", "K92", "K93", "K94", "K95", "K96", "K97", "K98", "K99", "K100", "K101", "K102", "K103", "K104", "K105", "K106", "K107", "K108", "K109", "K110", "K111", "K112", "K113", "K114", "K115", "K116", "K117", "K118", "K119", "K120", "K121", "K122", "K123", "K124", "K125", "K126", "K127", "K128", "K129", "K130", "K131", "K132", "K133", "K134", "K135", "K136", "K137", "K138", "K139", "K140", "K141", "K142", "K143", "K144", "K145", "K146", "K147", "K148", "K149", "K150", "K151", "K152", "K153", "K154", "K155", "K156", "K157", "K158", "K159", "K160", "K161", "K162", "K163", "K164", "K165", "K166", "K167", "K168", "K169", "K170", "K171", "K172", "K173", "K174", "K175", "K176", "K177", "K178", "K179", "K180", "K181", "K182", "K183", "K184", "K185", "K186", "K187", "K188", "K189", "K190", "K191", "K192", "K193", "K194", "K195", "K196", "K197", "K198", "K199", "K200", "K201", "K202", "K203", "K204", "K205", "K206", "K207", "K208", "K209", "K210", "K211", "K212", "K213", "K214", "K215", "K216", "K217", "K218", "K219", "K220", "K221", "K222", "K223", "K224", "K225", "K226", "K227", "K228", "K229", "K230", "K231", "K232", "K233", "K234", "K235", "K236", "K237", "K238", "K239", "K240", "K241", "K242", "K243", "K244", "K245", "K246", "K247", "K248", "K249", "K250", "K251", "K252", "K253", "K254", "K255", "K256", "K257", "K258", "K259", "K260", "K261", "K262", "K263", "K264", "K265", "K266", "K267", "K268", "K269", "K270", "K271", "K272", "K273", "K274", "K275", "K276", "K277", "K278", "K279", "K280", "K281", "K282", "K283", "K284", "K285", "K286", "K287", "K288", "K289", "K290", "K291", "K292", "K293", "K294", "K295", "K296", "K297", "K298", "K299", "K300", "K301", "K302", "K303", "K304", "K305", "K306", "K307", "K308", "K309", "K310", "K311", "K312", "K313", "K314", "K315", "K316", "K317", "K318", "K319", "K320", "K321", "K322", "K323", "K324", "K325", "K326", "K327", "K328", "K329", "K330", "K331", "K332", "K333", "K334", "K335", "K336", "K337", "K338", "K339", "K340", "K341", "K342", "K343", "K344", "K345", "K346", "K347", "K348", "K349", "K350", "K351", "K352", "K353", "K354", "K355", "K356", "K357", "K358", "K359", "K360", "K361", "K362", "K363", "K364", "K365", "K366", "K367", "K368", "K369", "K370", "K371", "K372", "K373", "K374", "K375", "K376", "K377", "K378", "K379", "K380", "K381", "K382", "K383", "K384", "K385", "K386", "K387", "K388", "K389", "K390", "K391", "K392", "K393", "K394", "K395", "K396", "K397", "K398", "K399", "K400", "K401", "K402", "K403", "K404", "K405", "K406", "K407", "K408", "K409", "K410", "K411", "K412", "K413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Au fil de l'eau", "Acompte et solde"]}`.

Choix du catalogue : ["Au fil de l'eau", "Acompte et solde"].

### Acompte

Identifiant : `contract_deposit_rate`. Type : `number`. Zones : `L14:L413`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part du montant HT du contrat ; le solde est calculé après acompte et jalon.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_quantity, contract_unit_price, contract_invoicing.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

L + N ≤ 1. Le solde P = MAX(0,1-L-N) est calculé et interdit.

### Date de l’acompte

Identifiant : `contract_deposit_date`. Type : `date`. Zones : `M14:M413`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de facture de la tranche correspondante ; cash après délai applicable.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_invoicing, contract_start, contract_end.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Jalon

Identifiant : `contract_milestone_rate`. Type : `number`. Zones : `N14:N413`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part du montant HT du contrat ; le solde est calculé après acompte et jalon.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_quantity, contract_unit_price, contract_invoicing.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

L + N ≤ 1. Le solde P = MAX(0,1-L-N) est calculé et interdit.

### Date du jalon

Identifiant : `contract_milestone_date`. Type : `date`. Zones : `O14:O413`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de facture de la tranche correspondante ; cash après délai applicable.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_invoicing, contract_start, contract_end.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Date du solde

Identifiant : `contract_balance_date`. Type : `date`. Zones : `Q14:Q413`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date de facture de la tranche correspondante ; cash après délai applicable.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_invoicing, contract_start, contract_end.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Statut

Identifiant : `contract_status`. Type : `enum`. Zones : `R14:R413`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Qualité commerciale du contrat : signed/probable selon les choix exacts ; pilote la pondération.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_weight.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23", "R24", "R25", "R26", "R27", "R28", "R29", "R30", "R31", "R32", "R33", "R34", "R35", "R36", "R37", "R38", "R39", "R40", "R41", "R42", "R43", "R44", "R45", "R46", "R47", "R48", "R49", "R50", "R51", "R52", "R53", "R54", "R55", "R56", "R57", "R58", "R59", "R60", "R61", "R62", "R63", "R64", "R65", "R66", "R67", "R68", "R69", "R70", "R71", "R72", "R73", "R74", "R75", "R76", "R77", "R78", "R79", "R80", "R81", "R82", "R83", "R84", "R85", "R86", "R87", "R88", "R89", "R90", "R91", "R92", "R93", "R94", "R95", "R96", "R97", "R98", "R99", "R100", "R101", "R102", "R103", "R104", "R105", "R106", "R107", "R108", "R109", "R110", "R111", "R112", "R113", "R114", "R115", "R116", "R117", "R118", "R119", "R120", "R121", "R122", "R123", "R124", "R125", "R126", "R127", "R128", "R129", "R130", "R131", "R132", "R133", "R134", "R135", "R136", "R137", "R138", "R139", "R140", "R141", "R142", "R143", "R144", "R145", "R146", "R147", "R148", "R149", "R150", "R151", "R152", "R153", "R154", "R155", "R156", "R157", "R158", "R159", "R160", "R161", "R162", "R163", "R164", "R165", "R166", "R167", "R168", "R169", "R170", "R171", "R172", "R173", "R174", "R175", "R176", "R177", "R178", "R179", "R180", "R181", "R182", "R183", "R184", "R185", "R186", "R187", "R188", "R189", "R190", "R191", "R192", "R193", "R194", "R195", "R196", "R197", "R198", "R199", "R200", "R201", "R202", "R203", "R204", "R205", "R206", "R207", "R208", "R209", "R210", "R211", "R212", "R213", "R214", "R215", "R216", "R217", "R218", "R219", "R220", "R221", "R222", "R223", "R224", "R225", "R226", "R227", "R228", "R229", "R230", "R231", "R232", "R233", "R234", "R235", "R236", "R237", "R238", "R239", "R240", "R241", "R242", "R243", "R244", "R245", "R246", "R247", "R248", "R249", "R250", "R251", "R252", "R253", "R254", "R255", "R256", "R257", "R258", "R259", "R260", "R261", "R262", "R263", "R264", "R265", "R266", "R267", "R268", "R269", "R270", "R271", "R272", "R273", "R274", "R275", "R276", "R277", "R278", "R279", "R280", "R281", "R282", "R283", "R284", "R285", "R286", "R287", "R288", "R289", "R290", "R291", "R292", "R293", "R294", "R295", "R296", "R297", "R298", "R299", "R300", "R301", "R302", "R303", "R304", "R305", "R306", "R307", "R308", "R309", "R310", "R311", "R312", "R313", "R314", "R315", "R316", "R317", "R318", "R319", "R320", "R321", "R322", "R323", "R324", "R325", "R326", "R327", "R328", "R329", "R330", "R331", "R332", "R333", "R334", "R335", "R336", "R337", "R338", "R339", "R340", "R341", "R342", "R343", "R344", "R345", "R346", "R347", "R348", "R349", "R350", "R351", "R352", "R353", "R354", "R355", "R356", "R357", "R358", "R359", "R360", "R361", "R362", "R363", "R364", "R365", "R366", "R367", "R368", "R369", "R370", "R371", "R372", "R373", "R374", "R375", "R376", "R377", "R378", "R379", "R380", "R381", "R382", "R383", "R384", "R385", "R386", "R387", "R388", "R389", "R390", "R391", "R392", "R393", "R394", "R395", "R396", "R397", "R398", "R399", "R400", "R401", "R402", "R403", "R404", "R405", "R406", "R407", "R408", "R409", "R410", "R411", "R412", "R413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Signe", "Probable", "Previsionnel"]}`.

Choix du catalogue : ["Signe", "Probable", "Previsionnel"].

Previsionnel existe dans la validation et les formules, mais le rôle courant du registre est contrats signés/probables. Pour une nouvelle prévision générique, utiliser le plan Assumptions ; n’ajouter Previsionnel ici qu’avec justification explicite du cas. Alias Signé accepté par la formule, émettre Signe pour respecter la validation exacte.

### Pondération

Identifiant : `contract_weight`. Type : `number`. Zones : `S14:S413`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Probabilité appliquée au montant d’un contrat pondéré ; signé conserve sa règle de pondération propre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_status, contract_quantity, contract_unit_price.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

Les contrats signés sont pondérés à 100 % par le moteur, quel que soit S.

### Régime TVA dérogatoire du contrat

Identifiant : `contract_vat_regime`. Type : `enum`. Zones : `AL14:AL413`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Dérogation documentée au régime TVA de l’offre ; vide suit le défaut prévu, pas une exonération.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_offer, atelier_cir_is_d143_d155.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["Biens", "Services encaissements", "Services débits", "Exonéré / hors champ"]}`.

Choix du catalogue : ["Biens", "Services encaissements", "Services débits", "Exonéré / hors champ"].

### Taux TVA dérogatoire du contrat

Identifiant : `contract_vat_rate`. Type : `number`. Zones : `AM14:AM413`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : TVA sur base HT contractuelle, dérogation explicite au taux de l’offre.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : contract_vat_regime, atelier_cir_is_e143_e155.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1}`.

## Registre

Le coordinateur cherche une ligne libre dans le classeur courant, compare les identités déjà présentes et pose les questions manquantes avant de préparer une proposition.

```json
{
  "start_row": 14,
  "end_row": 413,
  "identity_columns": [
    "AL",
    "AM",
    "B",
    "C",
    "E",
    "F",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "Q",
    "R",
    "S"
  ],
  "required": [
    "B",
    "C",
    "E",
    "F",
    "H",
    "I",
    "J",
    "K",
    "R"
  ]
}
```

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Montant brut de la première ligne — `DATA Contrats!G14`

Unité : EUR. Quantité multipliée par prix unitaire, après identification du contrat.

```text
IF($B14="","",N($E14)*N($F14))
```

Sources directes extraites : `'DATA Contrats'!$B14`, `'DATA Contrats'!$E14`, `'DATA Contrats'!$F14`.

### Montant pondéré — `DATA Contrats!X14`

Unité : EUR. Le statut signé conserve 100 % ; le probable utilise sa probabilité documentée.

```text
IF($B14="",0,N($G14)*IF(OR($R14="Signe",$R14="Signé"),1,IF($S14="",1,N($S14))))
```

Sources directes extraites : `'DATA Contrats'!$B14`, `'DATA Contrats'!$G14`, `'DATA Contrats'!$R14`, `'DATA Contrats'!$S14`.

### Total pondéré du registre — `DATA Contrats!F6`

Unité : EUR. Agrège les contrats identifiés ; un objectif commercial n’est pas une preuve de contrat.

```text
SUM($X$14:$X$413)
```

Sources directes extraites : `'DATA Contrats'!$X$14:$X$413`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_05 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Contrat identifié de 3 unités à 2 000 EUR, signé, dates et facturation complètes.

Attendu : G14 et X14 valent 6 000 ; F6 vaut 6 000 si le registre ne contient que ce contrat.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
