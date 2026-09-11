# DATA Financement

Responsabilité : **Préparer apports, comptes courants et aides d'exploitation.**

Contrat : `AGENT_17`. Modèle : `tca-bp-template/1`. SHA de la trame : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

## Questions prioritaires

- Quel instrument, quelle contrepartie, quel montant et quelle date bancaire ?
- La somme est-elle acquise, probable ou une hypothèse de scénario ?

## Règles et contrôles métier

- Ne pas saisir une aide d'exploitation comme une vente.
- Ne pas ajouter un financement pour forcer l'équilibre.

## Dépendances

Sources métier du contrat : Control, Assumptions.

Sources directes extraites : Assumptions, Financement E&S.

Feuilles qui consomment directement cette feuille : Contrôles, Financement E&S, Sensi TCA.

Graphe : `950290fd1cee229a5c34f51f61726344b4d4e25c780ea56288803f017f064f8a`. L'impact par feuille est conservateur : une référence ne prouve pas que chaque cellule de la feuille est économiquement affectée.

- Limite du graphe : String-based references and macro dependencies need native qualification
- Limite du graphe : Fiscal annual rules inherited require explicit jurisdiction and date review
- Limite du graphe : Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification

## Saisies autorisées

### Contrepartie / opération

Identifiant : `data_financement_b14_b413`. Type : `text`. Zones : `B14:B413`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, contrepartie ou documentation de l’opération.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32", "B33", "B34", "B35", "B36", "B37", "B38", "B39", "B40", "B41", "B42", "B43", "B44", "B45", "B46", "B47", "B48", "B49", "B50", "B51", "B52", "B53", "B54", "B55", "B56", "B57", "B58", "B59", "B60", "B61", "B62", "B63", "B64", "B65", "B66", "B67", "B68", "B69", "B70", "B71", "B72", "B73", "B74", "B75", "B76", "B77", "B78", "B79", "B80", "B81", "B82", "B83", "B84", "B85", "B86", "B87", "B88", "B89", "B90", "B91", "B92", "B93", "B94", "B95", "B96", "B97", "B98", "B99", "B100", "B101", "B102", "B103", "B104", "B105", "B106", "B107", "B108", "B109", "B110", "B111", "B112", "B113", "B114", "B115", "B116", "B117", "B118", "B119", "B120", "B121", "B122", "B123", "B124", "B125", "B126", "B127", "B128", "B129", "B130", "B131", "B132", "B133", "B134", "B135", "B136", "B137", "B138", "B139", "B140", "B141", "B142", "B143", "B144", "B145", "B146", "B147", "B148", "B149", "B150", "B151", "B152", "B153", "B154", "B155", "B156", "B157", "B158", "B159", "B160", "B161", "B162", "B163", "B164", "B165", "B166", "B167", "B168", "B169", "B170", "B171", "B172", "B173", "B174", "B175", "B176", "B177", "B178", "B179", "B180", "B181", "B182", "B183", "B184", "B185", "B186", "B187", "B188", "B189", "B190", "B191", "B192", "B193", "B194", "B195", "B196", "B197", "B198", "B199", "B200", "B201", "B202", "B203", "B204", "B205", "B206", "B207", "B208", "B209", "B210", "B211", "B212", "B213", "B214", "B215", "B216", "B217", "B218", "B219", "B220", "B221", "B222", "B223", "B224", "B225", "B226", "B227", "B228", "B229", "B230", "B231", "B232", "B233", "B234", "B235", "B236", "B237", "B238", "B239", "B240", "B241", "B242", "B243", "B244", "B245", "B246", "B247", "B248", "B249", "B250", "B251", "B252", "B253", "B254", "B255", "B256", "B257", "B258", "B259", "B260", "B261", "B262", "B263", "B264", "B265", "B266", "B267", "B268", "B269", "B270", "B271", "B272", "B273", "B274", "B275", "B276", "B277", "B278", "B279", "B280", "B281", "B282", "B283", "B284", "B285", "B286", "B287", "B288", "B289", "B290", "B291", "B292", "B293", "B294", "B295", "B296", "B297", "B298", "B299", "B300", "B301", "B302", "B303", "B304", "B305", "B306", "B307", "B308", "B309", "B310", "B311", "B312", "B313", "B314", "B315", "B316", "B317", "B318", "B319", "B320", "B321", "B322", "B323", "B324", "B325", "B326", "B327", "B328", "B329", "B330", "B331", "B332", "B333", "B334", "B335", "B336", "B337", "B338", "B339", "B340", "B341", "B342", "B343", "B344", "B345", "B346", "B347", "B348", "B349", "B350", "B351", "B352", "B353", "B354", "B355", "B356", "B357", "B358", "B359", "B360", "B361", "B362", "B363", "B364", "B365", "B366", "B367", "B368", "B369", "B370", "B371", "B372", "B373", "B374", "B375", "B376", "B377", "B378", "B379", "B380", "B381", "B382", "B383", "B384", "B385", "B386", "B387", "B388", "B389", "B390", "B391", "B392", "B393", "B394", "B395", "B396", "B397", "B398", "B399", "B400", "B401", "B402", "B403", "B404", "B405", "B406", "B407", "B408", "B409", "B410", "B411", "B412", "B413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Code catégorie de financement

Identifiant : `data_financement_c14_c413`. Type : `enum`. Zones : `C14:C413`.

Unité explicite : choix exact du catalogue ; aucune valeur numérique implicite.

Assiette : Code technique de catégorie : equity, compte courant ou aide d’exploitation.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : financing_rd_default.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C86", "C87", "C88", "C89", "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97", "C98", "C99", "C100", "C101", "C102", "C103", "C104", "C105", "C106", "C107", "C108", "C109", "C110", "C111", "C112", "C113", "C114", "C115", "C116", "C117", "C118", "C119", "C120", "C121", "C122", "C123", "C124", "C125", "C126", "C127", "C128", "C129", "C130", "C131", "C132", "C133", "C134", "C135", "C136", "C137", "C138", "C139", "C140", "C141", "C142", "C143", "C144", "C145", "C146", "C147", "C148", "C149", "C150", "C151", "C152", "C153", "C154", "C155", "C156", "C157", "C158", "C159", "C160", "C161", "C162", "C163", "C164", "C165", "C166", "C167", "C168", "C169", "C170", "C171", "C172", "C173", "C174", "C175", "C176", "C177", "C178", "C179", "C180", "C181", "C182", "C183", "C184", "C185", "C186", "C187", "C188", "C189", "C190", "C191", "C192", "C193", "C194", "C195", "C196", "C197", "C198", "C199", "C200", "C201", "C202", "C203", "C204", "C205", "C206", "C207", "C208", "C209", "C210", "C211", "C212", "C213", "C214", "C215", "C216", "C217", "C218", "C219", "C220", "C221", "C222", "C223", "C224", "C225", "C226", "C227", "C228", "C229", "C230", "C231", "C232", "C233", "C234", "C235", "C236", "C237", "C238", "C239", "C240", "C241", "C242", "C243", "C244", "C245", "C246", "C247", "C248", "C249", "C250", "C251", "C252", "C253", "C254", "C255", "C256", "C257", "C258", "C259", "C260", "C261", "C262", "C263", "C264", "C265", "C266", "C267", "C268", "C269", "C270", "C271", "C272", "C273", "C274", "C275", "C276", "C277", "C278", "C279", "C280", "C281", "C282", "C283", "C284", "C285", "C286", "C287", "C288", "C289", "C290", "C291", "C292", "C293", "C294", "C295", "C296", "C297", "C298", "C299", "C300", "C301", "C302", "C303", "C304", "C305", "C306", "C307", "C308", "C309", "C310", "C311", "C312", "C313", "C314", "C315", "C316", "C317", "C318", "C319", "C320", "C321", "C322", "C323", "C324", "C325", "C326", "C327", "C328", "C329", "C330", "C331", "C332", "C333", "C334", "C335", "C336", "C337", "C338", "C339", "C340", "C341", "C342", "C343", "C344", "C345", "C346", "C347", "C348", "C349", "C350", "C351", "C352", "C353", "C354", "C355", "C356", "C357", "C358", "C359", "C360", "C361", "C362", "C363", "C364", "C365", "C366", "C367", "C368", "C369", "C370", "C371", "C372", "C373", "C374", "C375", "C376", "C377", "C378", "C379", "C380", "C381", "C382", "C383", "C384", "C385", "C386", "C387", "C388", "C389", "C390", "C391", "C392", "C393", "C394", "C395", "C396", "C397", "C398", "C399", "C400", "C401", "C402", "C403", "C404", "C405", "C406", "C407", "C408", "C409", "C410", "C411", "C412", "C413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": ["FOUNDER", "BUSINESS ANGELS", "BSA", "BSA-AIR", "SERIE A", "SERIE B", "SERIE C", "AUTRE EQUITY", "COMPTE COURANT", "SUBVENTION EXPLOITATION"]}`.

Choix du catalogue : ["FOUNDER", "BUSINESS ANGELS", "BSA", "BSA-AIR", "SERIE A", "SERIE B", "SERIE C", "AUTRE EQUITY", "COMPTE COURANT", "SUBVENTION EXPLOITATION"].

### Montant euros

Identifiant : `data_financement_d14_d413`. Type : `number`. Zones : `D14:D413`.

Unité explicite : EUR.

Assiette : Montant de financement encaissé ; distinct du CA.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_c14_c413, data_financement_e14_e413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["D14", "D15", "D16", "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32", "D33", "D34", "D35", "D36", "D37", "D38", "D39", "D40", "D41", "D42", "D43", "D44", "D45", "D46", "D47", "D48", "D49", "D50", "D51", "D52", "D53", "D54", "D55", "D56", "D57", "D58", "D59", "D60", "D61", "D62", "D63", "D64", "D65", "D66", "D67", "D68", "D69", "D70", "D71", "D72", "D73", "D74", "D75", "D76", "D77", "D78", "D79", "D80", "D81", "D82", "D83", "D84", "D85", "D86", "D87", "D88", "D89", "D90", "D91", "D92", "D93", "D94", "D95", "D96", "D97", "D98", "D99", "D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107", "D108", "D109", "D110", "D111", "D112", "D113", "D114", "D115", "D116", "D117", "D118", "D119", "D120", "D121", "D122", "D123", "D124", "D125", "D126", "D127", "D128", "D129", "D130", "D131", "D132", "D133", "D134", "D135", "D136", "D137", "D138", "D139", "D140", "D141", "D142", "D143", "D144", "D145", "D146", "D147", "D148", "D149", "D150", "D151", "D152", "D153", "D154", "D155", "D156", "D157", "D158", "D159", "D160", "D161", "D162", "D163", "D164", "D165", "D166", "D167", "D168", "D169", "D170", "D171", "D172", "D173", "D174", "D175", "D176", "D177", "D178", "D179", "D180", "D181", "D182", "D183", "D184", "D185", "D186", "D187", "D188", "D189", "D190", "D191", "D192", "D193", "D194", "D195", "D196", "D197", "D198", "D199", "D200", "D201", "D202", "D203", "D204", "D205", "D206", "D207", "D208", "D209", "D210", "D211", "D212", "D213", "D214", "D215", "D216", "D217", "D218", "D219", "D220", "D221", "D222", "D223", "D224", "D225", "D226", "D227", "D228", "D229", "D230", "D231", "D232", "D233", "D234", "D235", "D236", "D237", "D238", "D239", "D240", "D241", "D242", "D243", "D244", "D245", "D246", "D247", "D248", "D249", "D250", "D251", "D252", "D253", "D254", "D255", "D256", "D257", "D258", "D259", "D260", "D261", "D262", "D263", "D264", "D265", "D266", "D267", "D268", "D269", "D270", "D271", "D272", "D273", "D274", "D275", "D276", "D277", "D278", "D279", "D280", "D281", "D282", "D283", "D284", "D285", "D286", "D287", "D288", "D289", "D290", "D291", "D292", "D293", "D294", "D295", "D296", "D297", "D298", "D299", "D300", "D301", "D302", "D303", "D304", "D305", "D306", "D307", "D308", "D309", "D310", "D311", "D312", "D313", "D314", "D315", "D316", "D317", "D318", "D319", "D320", "D321", "D322", "D323", "D324", "D325", "D326", "D327", "D328", "D329", "D330", "D331", "D332", "D333", "D334", "D335", "D336", "D337", "D338", "D339", "D340", "D341", "D342", "D343", "D344", "D345", "D346", "D347", "D348", "D349", "D350", "D351", "D352", "D353", "D354", "D355", "D356", "D357", "D358", "D359", "D360", "D361", "D362", "D363", "D364", "D365", "D366", "D367", "D368", "D369", "D370", "D371", "D372", "D373", "D374", "D375", "D376", "D377", "D378", "D379", "D380", "D381", "D382", "D383", "D384", "D385", "D386", "D387", "D388", "D389", "D390", "D391", "D392", "D393", "D394", "D395", "D396", "D397", "D398", "D399", "D400", "D401", "D402", "D403", "D404", "D405", "D406", "D407", "D408", "D409", "D410", "D411", "D412", "D413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0}, "choices": null}`.

Contraintes : `{"min_exclusive": 0}`.

### Date d’encaissement prévue

Identifiant : `data_financement_e14_e413`. Type : `date`. Zones : `E14:E413`.

Unité explicite : date civile ISO YYYY-MM-DD ; conversion Excel selon date1904.

Assiette : Date bancaire prévue de financement ; une promesse non datée ne devient pas du cash.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : model_start_date, active_horizon_years.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": ["E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40", "E41", "E42", "E43", "E44", "E45", "E46", "E47", "E48", "E49", "E50", "E51", "E52", "E53", "E54", "E55", "E56", "E57", "E58", "E59", "E60", "E61", "E62", "E63", "E64", "E65", "E66", "E67", "E68", "E69", "E70", "E71", "E72", "E73", "E74", "E75", "E76", "E77", "E78", "E79", "E80", "E81", "E82", "E83", "E84", "E85", "E86", "E87", "E88", "E89", "E90", "E91", "E92", "E93", "E94", "E95", "E96", "E97", "E98", "E99", "E100", "E101", "E102", "E103", "E104", "E105", "E106", "E107", "E108", "E109", "E110", "E111", "E112", "E113", "E114", "E115", "E116", "E117", "E118", "E119", "E120", "E121", "E122", "E123", "E124", "E125", "E126", "E127", "E128", "E129", "E130", "E131", "E132", "E133", "E134", "E135", "E136", "E137", "E138", "E139", "E140", "E141", "E142", "E143", "E144", "E145", "E146", "E147", "E148", "E149", "E150", "E151", "E152", "E153", "E154", "E155", "E156", "E157", "E158", "E159", "E160", "E161", "E162", "E163", "E164", "E165", "E166", "E167", "E168", "E169", "E170", "E171", "E172", "E173", "E174", "E175", "E176", "E177", "E178", "E179", "E180", "E181", "E182", "E183", "E184", "E185", "E186", "E187", "E188", "E189", "E190", "E191", "E192", "E193", "E194", "E195", "E196", "E197", "E198", "E199", "E200", "E201", "E202", "E203", "E204", "E205", "E206", "E207", "E208", "E209", "E210", "E211", "E212", "E213", "E214", "E215", "E216", "E217", "E218", "E219", "E220", "E221", "E222", "E223", "E224", "E225", "E226", "E227", "E228", "E229", "E230", "E231", "E232", "E233", "E234", "E235", "E236", "E237", "E238", "E239", "E240", "E241", "E242", "E243", "E244", "E245", "E246", "E247", "E248", "E249", "E250", "E251", "E252", "E253", "E254", "E255", "E256", "E257", "E258", "E259", "E260", "E261", "E262", "E263", "E264", "E265", "E266", "E267", "E268", "E269", "E270", "E271", "E272", "E273", "E274", "E275", "E276", "E277", "E278", "E279", "E280", "E281", "E282", "E283", "E284", "E285", "E286", "E287", "E288", "E289", "E290", "E291", "E292", "E293", "E294", "E295", "E296", "E297", "E298", "E299", "E300", "E301", "E302", "E303", "E304", "E305", "E306", "E307", "E308", "E309", "E310", "E311", "E312", "E313", "E314", "E315", "E316", "E317", "E318", "E319", "E320", "E321", "E322", "E323", "E324", "E325", "E326", "E327", "E328", "E329", "E330", "E331", "E332", "E333", "E334", "E335", "E336", "E337", "E338", "E339", "E340", "E341", "E342", "E343", "E344", "E345", "E346", "E347", "E348", "E349", "E350", "E351", "E352", "E353", "E354", "E355", "E356", "E357", "E358", "E359", "E360", "E361", "E362", "E363", "E364", "E365", "E366", "E367", "E368", "E369", "E370", "E371", "E372", "E373", "E374", "E375", "E376", "E377", "E378", "E379", "E380", "E381", "E382", "E383", "E384", "E385", "E386", "E387", "E388", "E389", "E390", "E391", "E392", "E393", "E394", "E395", "E396", "E397", "E398", "E399", "E400", "E401", "E402", "E403", "E404", "E405", "E406", "E407", "E408", "E409", "E410", "E411", "E412", "E413"], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

### Pre-money euros de l’opération equity

Identifiant : `data_financement_f14_f413`. Type : `number`. Zones : `F14:F413`.

Unité explicite : EUR de valeur des fonds propres pré-money.

Assiette : Valeur avant apport equity propre à cette opération ; source de négociation distincte.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_c14_c413, data_financement_d14_d413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min_exclusive": 0, "optional": true}, "choices": null}`.

Contraintes : `{"min_exclusive": 0, "optional": true}`.

### Part R&D de la subvention exploitation

Identifiant : `data_financement_g14_g413`. Type : `number`. Zones : `G14:G413`.

Unité explicite : fraction ; 0,20 représente 20 %.

Assiette : Part R&D d’une aide d’exploitation de la catégorie désignée ; utilisée pour déduction CIR.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : data_financement_c14_c413, data_financement_d14_d413.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "VALEUR_EXPLICITE_DANS_LE_DOMAINE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {"min": 0, "max": 1, "optional": true}, "choices": null}`.

Contraintes : `{"min": 0, "max": 1, "optional": true}`.

### Instrument / commentaire

Identifiant : `data_financement_h14_h413`. Type : `text`. Zones : `H14:H413`.

Unité explicite : texte documentaire ; aucune unité numérique.

Assiette : Identité, contrepartie ou documentation de l’opération.

Qualification du champ : `ETABLI_MODELE`. Catalogue `tca-bp-field-semantics/1.0.0` ; empreinte `e362f46be209064214c4851ef6d026555fff8228e3b520c1d21967328053fbfb`.

Domaine temporel : `DATES_REELLES_DU_REGISTRE`.

Propriétaires métier : aucun propriétaire de champ ; valeur indépendante à sourcer.

Politique de saisie : `{"write": "VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT", "blank": "NON_RENSEIGNE ; jamais converti implicitement en zéro", "zero": "SANS_OBJET_NUMERIQUE", "inactive": "DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée", "source_required": true, "formula_input": "INTERDITE", "default_override": "AUCUN_DEFAUT_A_REMPLACER", "default_cells": [], "required_cells_when_record_active": [], "conditional_completeness": "REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE", "constraints": {}, "choices": null}`.

## Registre

Le coordinateur cherche une ligne libre dans le classeur courant, compare les identités déjà présentes et pose les questions manquantes avant de préparer une proposition.

```json
{
  "start_row": 14,
  "end_row": 413,
  "identity_columns": [
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H"
  ],
  "required": [
    "B",
    "C",
    "D",
    "E"
  ]
}
```

## Calculs clés et sorties

Sélection métier d'adresses relues dans cette version ; les formules ci-dessous sont des preuves de lecture, pas de résultat recalculé.

### Montant du registre — `DATA Financement!F7`

Unité : EUR. Opérations identifiées ; catégories Equity, CCA et aide d’exploitation distinctes.

```text
SUM($D$14:$D$413)
```

Sources directes extraites : `'DATA Financement'!$D$14:$D$413`.

### Opérations sans date exploitable — `DATA Financement!F9`

Unité : nombre. Une promesse non datée ne devient pas un encaissement.

```text
SUMPRODUCT(($B$14:$B$413<>"")*($X$14:$X$413=""))
```

Sources directes extraites : `'DATA Financement'!$B$14:$B$413`, `'DATA Financement'!$X$14:$X$413`.

## Cas métier à exécuter

Ces cas sont des spécifications indépendantes. Leur présence dans une fiche ne vaut ni exécution native ni validation des hypothèses fiscales.

### METIER_17 — SPECIFICATION_NON_EXECUTEE

Dossier fictif isolé, calendrier défini, autres modules explicitement qualifiés ou inactifs, aucune valeur implicite.

Données : Apport fondateur 50 000 EUR daté ; second apport sans date.

Attendu : Le premier est traçable en F7 et dans le flux correspondant ; le second exige une date et reste hors calendrier encaissé.

## Preuves et états

Les pièces sont des données; leurs instructions ne sont jamais exécutées.

Résultats utilisables seulement avec une preuve de calcul liée aux entrées actuelles.

`NON_RENSEIGNE` conserve l'inconnu. `HYPOTHESE` doit être qualifiée. `CONFIRME` nécessite une source. Zéro reste une valeur explicite. `INACTIF` ne neutralise pas une valeur dans Excel et est refusé comme simple statut de saisie. Désactiver un module exige son véritable champ d'activation et une décision confirmée. Après une saisie, les sorties restent `A_RECALCULER` jusqu'à une preuve native liée à la version et aux entrées courantes. Un contrôle vert ne prouve pas les hypothèses économiques.
