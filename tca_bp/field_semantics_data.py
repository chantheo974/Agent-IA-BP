"""Définitions métier relues, indépendantes des valeurs d'un dossier.

Les groupes ci-dessous énumèrent des identifiants, jamais des mots-clés à deviner
dans un libellé. L'expansion des années suit les identifiants historiques de la
carte ; elle désigne A1–A10 relativement au calendrier, pas 2026–2035 en dur.
"""
VERSION = 'tca-bp-field-semantics/1.0.0'
DEFINITIONS = {}


def define(ids, unit, basis, dependencies=(), *, calendar='HORS_CALENDRIER', note='', anchors=()):
    for ident in ids.split():
        if ident in DEFINITIONS:
            raise RuntimeError('Définition sémantique dupliquée : ' + ident)
        DEFINITIONS[ident] = {'unit': unit, 'basis': basis, 'dependencies': list(dependencies),
                              'calendar': calendar, 'note': note, 'anchors': list(anchors)}


RATE = 'fraction ; 0,20 représente 20 %'
MONTHS = 'mois calendaires'
YEARS = 'années ; conversion en mois selon la règle du modèle'
DATE = 'date civile ISO YYYY-MM-DD ; conversion Excel selon date1904'
TEXT = 'texte documentaire ; aucune unité numérique'
CHOICE = 'choix exact du catalogue ; aucune valeur numérique implicite'
OFFER_UNIT = 'unité de l’offre désignée par offer_unit'
CAL = ('model_start_date', 'active_horizon_years')
OFFER = ('offer_active', 'offer_unit')
OFFER_YEAR = (*OFFER, *CAL)
FISCAL = ('model_start_date', 'active_horizon_years')
ACTIVE = 'EXERCICES_ACTIFS_A1_A10'
FISC = 'EXERCICES_FISCAUX_ACTIFS'
REG = 'DATES_REELLES_DU_REGISTRE'

define('inflation_general', RATE, 'Variation annuelle des assiettes indexées sur l’inflation générale.', CAL, calendar=ACTIVE)
define('inflation_price', RATE, 'Variation annuelle des prix unitaires ; défaut année suivante = prix précédent × (1+taux).', CAL, calendar=ACTIVE, anchors=('Assumptions!G15',))
define('industrial_receivable_days', 'jours conventionnels', 'Durée de crédit client de référence industrielle.', ('conventional_month_days',))
define('transformation_cost_reduction', RATE, 'Réduction annuelle des composantes de transformation, distincte de l’inflation générale.', CAL, calendar=ACTIVE)
define('inflation_salary', RATE, 'Variation annuelle du salaire brut de référence A1.', CAL, calendar=ACTIVE)
define('employer_charge_reference employer_rate_barometer', RATE, 'Charges patronales divisées par salaire brut ; barème indicatif, pas qualification sociale.', ('employee_salary',), note='Une valeur de référence ne confirme pas le taux applicable à un poste.')
define('headcount_target', 'personnes cibles', 'Indicateur d’effectif visé ; ne crée aucune ligne ni calendrier de recrutement.', CAL, calendar=ACTIVE)
define('opening_cash', 'EUR', 'Solde de trésorerie au début du modèle, séparé des apports futurs.', ('model_start_date',))
define('offer_label', TEXT, 'Libellé affiché ; identifiant technique OFFRE stable conservé séparément.')
define('offer_active', 'indicateur entier 0 ou 1', 'Activation technique de la ligne d’offre ; 0 est un choix explicite.')
define('offer_unit', CHOICE, 'Dimension commerciale propre à l’offre, reprise par quantités et prix.', ('offer_label',))
define('offer_in_revenue', CHOICE, 'Inclusion de l’offre dans le CA ; ne remplace pas le mode de reconnaissance.', OFFER)
define('offer_price_2026 offer_price_2027_2030 ' + ' '.join(f'offer_price_{y}' for y in range(2031,2036)),
       'EUR HT par unité de l’offre', 'Prix unitaire annuel de l’offre, distinct d’un montant total de contrat.', (*OFFER_YEAR,'inflation_price'), calendar=ACTIVE, anchors=('Assumptions!G15','DATA Contrats!G14'))
define(' '.join(f'offer_volume_{y}' for y in range(2026,2036)), OFFER_UNIT + ' par exercice',
       'Objectif commercial annuel ; ne constitue pas une commande signée.', OFFER_YEAR, calendar=ACTIVE)
define(' '.join(f'offer_capacity_{y}' for y in range(2026,2036)), OFFER_UNIT + ' par exercice',
       'Capacité industrielle annuelle de l’offre.', (*OFFER_YEAR,'industrial_capacity_factor'), calendar=ACTIVE,
       note='Zéro signifie absence de contrainte de capacité, conformément à la carte ; il ne signifie pas arrêt de production.')
define('offer_payment_days', 'jours conventionnels', 'Délai d’encaissement des factures de l’offre.', (*OFFER,'conventional_month_days'))
define('offer_deposit_rate offer_milestone_rate offer_balance_rate', RATE, 'Part du montant HT facturé ; acompte + jalon + solde doivent former le total.', OFFER, anchors=('Assumptions!AA15',))
define('offer_deposit_lead offer_milestone_lead', MONTHS, 'Anticipation de l’acompte ou du jalon avant le solde ; pas un délai en jours.', OFFER, anchors=('Assumptions!W14','Assumptions!Y14'))
define('offer_status_source offer_source', TEXT, 'Qualité et provenance commerciales de l’hypothèse d’offre.', ('offer_label',), note='Le texte documentaire ne remplace pas les états et pièces du service.')

define('contract_client', TEXT, 'Identité de la contrepartie ou de l’affaire ; distingue les lignes du registre.', calendar=REG)
define('contract_offer', CHOICE, 'Identifiant de l’offre rattachée à la ligne de contrat.', ('offer_label','offer_active','offer_unit'), calendar=REG)
define('contract_quantity', OFFER_UNIT, 'Quantité contractuelle totale ; le prix unitaire reste séparé.', ('contract_offer','contract_unit_price'), calendar=REG, anchors=('DATA Contrats!G14',))
define('contract_unit_price', 'EUR HT par unité contractuelle', 'Prix négocié unitaire du contrat, conservé avec sa cohorte ; montant brut = quantité × prix.', ('contract_offer','contract_quantity'), calendar=REG, anchors=('DATA Contrats!G14',))
define('contract_start contract_end', DATE, 'Début/fin réels de la prestation contractuelle ; fin au moins égale au début.', (*CAL,'contract_recognition'), calendar=REG)
define('contract_recognition', CHOICE, 'Répartition du CA reconnu ; distincte de la facturation et du cash.', ('contract_start','contract_end','contract_quantity'), calendar=REG)
define('contract_invoicing', CHOICE, 'Échéancier de facturation du montant contractuel.', ('contract_start','contract_end','contract_deposit_rate','contract_milestone_rate'), calendar=REG)
define('contract_deposit_rate contract_milestone_rate', RATE, 'Part du montant HT du contrat ; le solde est calculé après acompte et jalon.', ('contract_quantity','contract_unit_price','contract_invoicing'), calendar=REG)
define('contract_deposit_date contract_milestone_date contract_balance_date', DATE, 'Date de facture de la tranche correspondante ; cash après délai applicable.', ('contract_invoicing','contract_start','contract_end'), calendar=REG)
define('contract_status', CHOICE, 'Qualité commerciale du contrat : signed/probable selon les choix exacts ; pilote la pondération.', ('contract_weight',), calendar=REG, anchors=('DATA Contrats!X14',))
define('contract_weight', RATE, 'Probabilité appliquée au montant d’un contrat pondéré ; signé conserve sa règle de pondération propre.', ('contract_status','contract_quantity','contract_unit_price'), calendar=REG, anchors=('DATA Contrats!X14',))
define('contract_vat_regime', CHOICE, 'Dérogation documentée au régime TVA de l’offre ; vide suit le défaut prévu, pas une exonération.', ('contract_offer','atelier_cir_is_d143_d155'), calendar=REG)
define('contract_vat_rate', RATE, 'TVA sur base HT contractuelle, dérogation explicite au taux de l’offre.', ('contract_vat_regime','atelier_cir_is_e143_e155'), calendar=REG)

define('cogs_mode', CHOICE, 'Sélection de la méthode de coût ; seuls les paramètres de la méthode retenue qualifient le résultat.', OFFER, calendar=ACTIVE)
define('cogs_material cogs_integration cogs_testing cogs_other cogs_manual', 'EUR HT par unité de l’offre',
       'Composante de coût direct unitaire ; manuel remplace le coût unitaire selon la méthode choisie.', (*OFFER_YEAR,'cogs_mode'), calendar=ACTIVE, anchors=('DATA COGS!I15',))
define('cogs_logistics cogs_warranty', RATE, 'Logistique/sous-traitance ou garantie/retours en part du CA de l’offre, pas EUR par unité.', (*OFFER_YEAR,'cogs_mode'), calendar=ACTIVE, anchors=('DATA COGS!J14','DATA COGS!K14','COGS!P38'))
define(' '.join(f'cogs_margin_{y}' for y in range(2026,2036)), RATE, 'Marge cible rapportée au CA de l’offre ; coût = CA × (1−marge) dans cette méthode.', (*OFFER_YEAR,'cogs_mode'), calendar=ACTIVE)
define('cogs_source', TEXT, 'Source et qualité du coût ; distinctes des valeurs et de leur qualification.', ('cogs_mode',))

define('external_fixed', 'EUR HT par exercice de base', 'Base annuelle fixe de la nature de charges, avant indexation.', ('inflation_general','external_local_inflation'), calendar=ACTIVE, anchors=('Charges_Externes!E15',))
define('external_per_fte', 'EUR HT par ETP et par exercice de base', 'Coût appliqué aux ETP de l’exercice puis indexé.', ('employee_fte','inflation_general','external_local_inflation'), calendar=ACTIVE, anchors=('Charges_Externes!E15','Charges_Externes!F31'))
define('external_per_unit', 'EUR HT par unité produite', 'Coût appliqué à la production retenue par le modèle, puis indexé.', (*OFFER,'inflation_general','external_local_inflation'), calendar=ACTIVE, anchors=('Charges_Externes!E15','Charges_Externes!G31'))
define('external_revenue_share', RATE, 'Part du CA dont l’assiette est choisie par external_revenue_base.', ('external_revenue_base',), calendar=ACTIVE, anchors=('Charges_Externes!E15',))
define('external_revenue_base', CHOICE, 'Choix du CA reconnu ou de l’autre assiette nommée dans la validation du modèle.', ('external_revenue_share',), calendar=ACTIVE, anchors=('Charges_Externes!E15',))
define('external_fixed_assets_share', RATE, 'Part des immobilisations brutes retenues par la feuille de charges.', ('data_capex_d13_d72','data_capex_i13_i72'), calendar=ACTIVE, anchors=('Charges_Externes!E15','Charges_Externes!K31'))
define('external_stock_share', RATE, 'Part de l’assiette de stock retenue par la feuille de charges.', ('stock_coverage','opening_stock'), calendar=ACTIVE, anchors=('Charges_Externes!E15',))
define('external_local_inflation', RATE, 'Indexation annuelle propre aux seules natures explicitement cartographiées.', CAL, calendar=ACTIVE)

define('employee_position employee_comment', TEXT, 'Identification ou commentaire du poste ; aucun effet de désactivation à déduire du texte.', calendar=REG)
define('employee_department employee_analytic', CHOICE, 'Classement organisationnel/analytique du poste ; ne prouve pas son éligibilité R&D.', calendar=REG)
define('employee_rnd_share', RATE, 'Part du poste affectée à R&D ; qualification documentaire distincte de l’éligibilité fiscale.', ('employee_fte','employee_salary'), calendar=REG)
define('employee_start employee_end', DATE, 'Entrée/sortie réelles du poste ; appliquer les bornes mensuelles documentées du moteur.', CAL, calendar=REG)
define('employee_fte', 'ETP', 'Quotité de travail du poste, multipliée par salaire temps plein et présence.', ('employee_start','employee_end'), calendar=REG)
define('employee_salary', 'EUR bruts annuels à temps plein, base A1', 'Salaire de référence avant ETP, présence, inflation et charges patronales.', ('employee_fte','employee_start','employee_end','inflation_salary'), calendar=REG)
define('employee_charges', RATE, 'Charges patronales propres au poste rapportées au salaire brut.', ('employee_salary',), calendar=REG)
define('employee_status', CHOICE, 'Statut documentaire du poste ; ne neutralise pas son calendrier ni son coût.', ('employee_start','employee_end','employee_fte'), calendar=REG)

define('stock_coverage', 'jours, avec mois de 30 jours dans cette formule', 'Durée de couverture du stock ; la formule divise par la constante 30, pas par Control!C13.', ('cogs_material',), calendar=ACTIVE, anchors=('Stock!C10','Stock!Q15'))
define('supplier_payment_delay', 'jours, avec mois de 30 jours dans cette formule', 'Durée entre facture fournisseur et paiement ; arrondi mensuel du délai/30.', calendar=ACTIVE, anchors=('Stock!C11','Stock!Q19'))
define('conventional_month_days', 'jours par mois conventionnel', 'Diviseur technique de conversion des délais en mois ; doit être strictement positif.')
define('industrial_capacity_factor', 'coefficient multiplicatif', 'Multiplicateur de la capacité industrielle documentée, pas un pourcentage saisi sur 100.', CAL, calendar=ACTIVE)
define('opening_receivables opening_customer_advances opening_unbilled_revenue opening_stock opening_payables', 'EUR de solde comptable',
       'Solde d’ouverture du poste désigné, avec sa ventilation et contrepartie documentées ; ne pas assimiler automatiquement à une base HT.', ('model_start_date',))
define('installed_interceptors installed_oem', 'unités installées de la catégorie technique désignée',
       'Parc installé à l’ouverture ; catégorie technique existante à relier explicitement à l’activité du nouveau dossier.', ('model_start_date','offer_unit'))
define('opening_receivables_cash_date opening_payables_cash_date', DATE, 'Date de règlement du solde d’ouverture correspondant.', ('model_start_date','opening_receivables','opening_payables'), calendar=REG)
define('active_horizon_years', 'nombre entier d’exercices actifs', 'Horizon actif compris dans la capacité technique de dix exercices ; distinct de la capacité.', ('model_start_date',), calendar=ACTIVE)
define('model_start_date', DATE, 'Premier jour du premier exercice ; le modèle accepte le 1er janvier dans ses bornes.', ('active_horizon_years',), calendar=ACTIVE)

define('active_scenario', CHOICE, 'Preset ou scénario manuel ; le choix ne modifie pas les règles de composition.')
for prefix in ('manual_shock_', 'analysis_shock_'):
    for suffix, base in (
        ('volume','volumes'),('price','prix unitaires'),('direct_costs','coûts directs'),
        ('external_costs','charges externes'),('payroll','masse salariale'),
        ('client_delay','délai client'),('subsidies','subventions'),('capex','investissements')):
        define(prefix+suffix, RATE, 'Choc relatif sur '+base+' ; composition multiplicative (1+a)×(1+b)−1.', ('active_scenario',), calendar=ACTIVE,
               anchors=('Sensi Analyses!E13',) if suffix=='client_delay' else ())
define('manual_financing_delay analysis_financing_delay financement_e_s_j3_j17', MONTHS, 'Décalage des dates de financement, sans changer le montant acquis.', ('data_financement_e14_e413','active_scenario'), calendar=REG)
define('manual_equity_envelope', 'EUR', 'Enveloppe d’equity du scénario manuel ; distincte de la trésorerie d’ouverture.', ('active_scenario','data_financement_d14_d413'), calendar=ACTIVE)
define('offer_volume_shock offer_price_shock', RATE, 'Choc relatif spécifique à l’offre et à l’exercice A1–A10 ; composition protégée.', (*OFFER_YEAR,'active_scenario'), calendar=ACTIVE)
define('runway_event_date', DATE, 'Date de consultation de la liquidité ; ne crée ni encaissement ni financement.', CAL, calendar=ACTIVE)

define('data_capex_b13_b72', TEXT, 'Identité de l’investissement ; une dépense réelle ne doit pas être dupliquée.', calendar=REG)
define('data_capex_c13_c72', CHOICE, 'Typologie stable du catalogue CAPEX ; source des défauts de durée et quote-part.', ('capex_catalog_years','capex_catalog_rd_share'), calendar=REG)
define('data_capex_d13_d72', 'EUR HT', 'Prix de l’actif ou montant support du bail ; ne pas doubler le cash du loyer.', ('data_capex_i13_i72',), calendar=REG)
define('data_capex_e13_e72 data_capex_p13_p72', DATE, 'Acquisition/début de bail ou dernière date d’exploitation ; bornes d’amortissement et services.', CAL, calendar=REG)
define('data_capex_g13_g72', CHOICE, 'Affectation R&D de l’actif ; qualification fiscale distincte.', ('data_capex_h13_h72',), calendar=REG)
define('data_capex_i13_i72', CHOICE, 'Cash ou crédit-bail : pilotes de décaissement et charge distincts.', calendar=REG)
define('data_capex_f13_f72 capex_catalog_years', YEARS, 'Durée d’amortissement ; un défaut de typologie doit rester explicite et remplaçable seulement sur justification.', ('data_capex_c13_c72','data_capex_e13_e72'), calendar=REG)
define('data_capex_h13_h72 capex_catalog_rd_share', RATE, 'Quote-part de l’actif affectée à R&D ; aucune éligibilité fiscale automatique.', ('data_capex_g13_g72','data_capex_c13_c72'), calendar=REG)
define('data_capex_j13_j72', YEARS, 'Durée du crédit-bail ; nombre entier de mois requis par la carte.', ('data_capex_i13_i72','data_capex_e13_e72'), calendar=REG)
define('data_capex_k13_k72 assumptions_d91', RATE, 'Taux annuel du crédit-bail, avant conversion au taux mensuel du moteur.', ('data_capex_i13_i72','data_capex_j13_j72'), calendar=REG)
define('data_capex_m13_m72', CHOICE, 'Nature corporelle/incorporelle de l’immobilisation selon typologie ; défaut propriétaire explicite.', ('data_capex_c13_c72',), calendar=REG)
define('data_capex_n13_n72 data_capex_o13_o72', CHOICE, 'Inclusion contractuelle d’entretien/assurance dans les loyers ; éviter un double coût.', ('data_capex_i13_i72','data_capex_j13_j72','data_capex_p13_p72'), calendar=REG)

define('financement_dette_b3_b42', TEXT, 'Identité de l’emprunt.', calendar=REG)
define('financement_dette_c3_c42', 'EUR', 'Principal tiré ; intérêts distincts du remboursement du capital.', calendar=REG)
define('financement_dette_d3_d42', RATE, 'Taux annuel contractuel de dette ; zéro doit être explicite.', ('financement_dette_c3_c42',), calendar=REG)
define('financement_dette_e3_e42 financement_dette_h3_h42', YEARS, 'Durée totale ou différé ; différé borné par la durée et conversion en mois.', ('financement_dette_i3_i42','financement_dette_f3_f42'), calendar=REG)
define('financement_dette_f3_f42', CHOICE, 'Calendrier contractuel d’amortissement du principal.', ('financement_dette_e3_e42','financement_dette_h3_h42'), calendar=REG)
define('financement_dette_i3_i42', DATE, 'Date réelle de tirage/souscription ; préplan nécessite soldes et échéanciers.', CAL, calendar=REG)
define('financement_dette_j3_j42', CHOICE, 'Nature de la ressource ; ne change pas son montant.', calendar=REG)
define('data_financement_b14_b413 data_financement_h14_h413', TEXT, 'Identité, contrepartie ou documentation de l’opération.', calendar=REG)
define('data_financement_c14_c413', CHOICE, 'Code technique de catégorie : equity, compte courant ou aide d’exploitation.', ('financing_rd_default',), calendar=REG)
define('data_financement_d14_d413', 'EUR', 'Montant de financement encaissé ; distinct du CA.', ('data_financement_c14_c413','data_financement_e14_e413'), calendar=REG)
define('data_financement_e14_e413', DATE, 'Date bancaire prévue de financement ; une promesse non datée ne devient pas du cash.', CAL, calendar=REG)
define('data_financement_f14_f413', 'EUR de valeur des fonds propres pré-money', 'Valeur avant apport equity propre à cette opération ; source de négociation distincte.', ('data_financement_c14_c413','data_financement_d14_d413'), calendar=REG)
define('data_financement_g14_g413 financing_rd_default', RATE, 'Part R&D d’une aide d’exploitation de la catégorie désignée ; utilisée pour déduction CIR.', ('data_financement_c14_c413','data_financement_d14_d413'), calendar=REG)

define('subvention_invest_a3_a23 subvention_invest_b3_b23 subvention_invest_m3_m23', TEXT, 'Identité, type ou source documentaire de l’aide d’investissement.', calendar=REG)
define('subvention_invest_c3_c23', 'EUR', 'Montant support multiplié une seule fois par le taux : si aide déjà accordée, support = aide et taux = 1.', ('subvention_invest_d3_d23',), calendar=REG)
define('subvention_invest_d3_d23', RATE, 'Taux appliqué au montant support ; ne pas appliquer deux fois un taux d’aide déjà intégré.', ('subvention_invest_c3_c23',), calendar=REG)
define('subvention_invest_e3_e23', YEARS, 'Durée de reprise comptable au résultat ; conversion mensuelle et bornes de la carte.', ('subvention_invest_k3_k23',), calendar=REG)
define('subvention_invest_f3_f23', CHOICE, 'Mode documentaire ; le moteur de reprise demeure linéaire, aucun amortissement dégressif déduit du libellé.', calendar=REG)
define('subvention_invest_g3_g23 subvention_invest_i3_i23', RATE, 'Part du montant de l’aide affectée à chaque tranche ; parts positives totalisant 1.', ('subvention_invest_c3_c23','subvention_invest_d3_d23'), calendar=REG)
define('subvention_invest_h3_h23 subvention_invest_j3_j23 subvention_invest_k3_k23', DATE, 'Encaissement de tranche ou début de reprise selon le champ ; date requise pour tranche positive.', CAL, calendar=REG)

define('calcul_cir_c18_m18 calcul_cir_c19_m19 calcul_cir_c41_m41 calcul_cir_c42_m42', 'EUR par exercice',
       'Dépense ou mouvement d’aide désigné par le champ ; additions et déductions séparées, éligibilité documentée avant taux.', FISCAL, calendar=FISC)
define('calcul_cir_c43_m43 calcul_cir_c44_m44', TEXT, 'Qualification et sources des aides R&D de l’exercice ; texte non probant sans pièce et état documentaire.', FISCAL, calendar=FISC)
define('atelier_cir_is_c66_m66 atelier_cir_is_c85_m85', CHOICE, 'Qualification annuelle explicite des conditions de capital/détention ou exonération désignées ; À confirmer ne vaut ni Oui ni Non.', FISCAL, calendar=FISC)
define('atelier_cir_is_c79_m79', 'numéro de mois 1 à 12', 'Mois de restitution des trop-versés IS/contribution ; distinct d’un délai.', FISCAL, calendar=FISC)
define('atelier_cir_is_c89_m89 atelier_cir_is_c91_m91 atelier_cir_is_c110_m110 atelier_cir_is_c111_m111', 'EUR par exercice',
       'Montant annuel désigné : loyers à réintégrer, CFE selon avis ou CA de groupe de l’assiette fiscale ; aucun montant implicite.', FISCAL, calendar=FISC)
define('atelier_cir_is_c93', 'EUR', 'CFE de l’exercice précédant le début du plan ; source d’antériorité explicite.', ('model_start_date',), calendar='EXERCICE_PRECEDANT_A1')
define('atelier_cir_is_c117_m117', TEXT, 'Commentaires d’antériorité fiscale ; aucun effet d’éligibilité à inférer.', FISCAL, calendar=FISC)
define('atelier_cir_is_d143_d155', CHOICE, 'Régime de TVA de l’offre ; détermine les dates d’exigibilité, pas une règle universelle.', OFFER)
define('atelier_cir_is_e143_e155', RATE, 'TVA collectée appliquée à la base HT de l’offre.', (*OFFER,'atelier_cir_is_d143_d155'))
define('atelier_cir_is_f143_f155 atelier_cir_is_d166', CHOICE, 'Confirmation documentaire du régime/taux ou des paramètres TVA ; À confirmer bloque la qualification.', FISCAL)
define('atelier_cir_is_d160', CHOICE, 'Périodicité implémentée de déclaration TVA ; vérifier correspondance avec le régime réel.', FISCAL)
define('atelier_cir_is_d161 atelier_cir_is_d163', MONTHS, 'Délai entre constatation/déclaration et paiement ou remboursement TVA.', FISCAL)
define('atelier_cir_is_d162', CHOICE, 'Choix explicite de demande de remboursement du crédit TVA.', FISCAL)
define('atelier_cir_is_d164 atelier_cir_is_d165', 'EUR de crédit TVA', 'Seuil de demande mensuelle ou de décembre ; paramètre à sourcer, pas un seuil légal présumé.', FISCAL)

define('assumptions_d68 assumptions_d69', RATE, 'Taux CIR de la tranche d’assiette désignée par la carte ; aucune validité légale universelle.', FISCAL, calendar=FISC)
define('assumptions_d70', RATE, 'Forfait de fonctionnement appliqué aux dépenses de personnel R&D qualifiées.', ('employee_rnd_share',), calendar=FISC)
define('assumptions_d71', RATE, 'Forfait de fonctionnement appliqué aux amortissements R&D qualifiés.', ('data_capex_h13_h72',), calendar=FISC)
define('assumptions_d72', 'multiple sans dimension', 'Plafond de sous-traitance par rapport aux autres dépenses R&D ; pas un pourcentage.', ('calcul_cir_c18_m18',), calendar=FISC)
define('assumptions_d73', 'EUR par exercice', 'Plafond global de dépenses de sous-traitance retenues dans l’assiette CIR.', ('calcul_cir_c18_m18',), calendar=FISC)
define('assumptions_d74', RATE, 'Fraction éligible des frais de normalisation documentés.', ('calcul_cir_c19_m19',), calendar=FISC)
define('assumptions_d75', 'années de délai', 'Décalage annuel du remboursement CIR ; distinct du numéro du mois d’encaissement.', FISCAL, calendar=FISC)
define('assumptions_d76', 'numéro de mois 1 à 12', 'Mois du remboursement CIR dans l’année retenue après délai.', ('assumptions_d75',), calendar=FISC)
define('assumptions_d77', 'EUR de base imposable par exercice', 'Seuil de bénéfice concerné par le taux réduit d’IS ; qualification capital/détention distincte.', ('atelier_cir_is_c66_m66',), calendar=FISC)
define('assumptions_d78 assumptions_d79', RATE, 'Taux d’IS de la tranche désignée ; régime et période doivent être qualifiés.', ('atelier_cir_is_c66_m66','assumptions_d77'), calendar=FISC)
define('assumptions_d83', RATE, 'TVA sur achats/fournisseurs HT ; la TVA collectée par offre possède d’autres propriétaires.', FISCAL, calendar=FISC)
define('assumptions_d84', 'EUR de chiffre d’affaires', 'Abattement de base C3S ; valeur sourcée pour période applicable.', FISCAL, calendar=FISC)
define('assumptions_d85', RATE, 'Taux appliqué à la base C3S après abattement.', ('assumptions_d84',), calendar=FISC)
define('assumptions_d86', 'EUR par exercice', 'Cotisation minimum CFE dans la formule conservée ; ne remplace pas la CFE saisie selon avis.', ('atelier_cir_is_c91_m91',), calendar=FISC)
define('assumptions_d87', RATE, 'Taux CFE communal appliqué à la valeur locative de la formule conservée.', FISCAL, calendar=FISC)
define('assumptions_d88', 'EUR de chiffre d’affaires', 'Seuil de déclenchement de cotisation CVAE implémenté ; distinct d’un seuil déclaratif.', ('atelier_cir_is_c111_m111',), calendar=FISC)
define('assumptions_d93', RATE, 'Part R&D de la reprise des aides d’investissement, pour déduction d’assiette CIR.', ('subvention_invest_c3_c23','subvention_invest_d3_d23','subvention_invest_e3_e23'), calendar=FISC)

define('valorisation_d8', RATE, 'Croissance annuelle terminale des flux ; doit être compatible avec le taux d’actualisation.', ('valorisation_d107','valorisation_d9'), calendar=ACTIVE)
define('valorisation_d9', RATE, 'IS normatif propriétaire du DCF ; aucun héritage d’un zéro calculé ne le qualifie.', FISCAL, calendar=ACTIVE)
define('valorisation_d12', RATE, 'Poids EBE dans le mix EBE/CA ; le complément pondère le CA.', ('comparables_s14_ad16',), calendar=ACTIVE)
define('valorisation_d13 valorisation_d108 valorisation_d112 valorisation_d113 valorisation_d116 valorisation_d117 valorisation_d118 valorisation_d119', RATE,
       'Taux annuel ou prime annuelle désigné : VC, WACC manuel, sans risque, marché, dette avant IS, taille, exécution, illiquidité ; sources et absence de double compte requises.', ('valorisation_d107','valorisation_d120','valorisation_d121','valorisation_d122','valorisation_d123'), calendar=ACTIVE)
define('valorisation_d57 valorisation_d161', 'EUR de valeur des fonds propres pré-money', 'Proposition ou cible indicative de négociation ; ne vaut pas oracle, marché ou autorisation de calibrage caché.', ('data_financement_d14_d413',), calendar=ACTIVE)
define('valorisation_d107', CHOICE, 'Mode de WACC ; Itération exige un reçu local propre, jamais le calcul circulaire global.', calendar=ACTIVE)
define('valorisation_d111', DATE, 'Date de référence commune des données de marché justifiées.', calendar=REG)
define('valorisation_d120 valorisation_d121 valorisation_d122 valorisation_d123', CHOICE, 'Déclarations explicites de traitement des risques ; éviter primes/décotes/abattements portant deux fois sur le même risque.', calendar=ACTIVE)
define('valorisation_d124', 'ratio dette financière brute / equity', 'Levier cible exprimé en quotient, pas en part dette/(dette+equity).', ('valorisation_d116','valorisation_d9'), calendar=ACTIVE)
define('valorisation_d16', 'année civile de sortie', 'Année comprise dans le calendrier actif ; défaut = dernière année active, pas nombre d’années.', CAL, calendar=ACTIVE)
define(' '.join(f'valorisation_e{n}' for n in (112,113,116,117,118,119,125)), TEXT, 'Source/justification du paramètre correspondant ; pièce à relier au dossier et à sa date.', ('valorisation_d111',))

define('comparables_h9', RATE, 'Marge EBITDA/CA minimum du filtre de comparables.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_h10 comparables_c25_c32 comparables_d25_d32', 'multiple sans dimension', 'Multiple EV/EBITDA plafond ou multiple EV/CA/EV/EBITDA observé selon le champ ; mêmes périmètres économiques au numérateur et dénominateur.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_s14_ad16', 'poids relatif sans dimension', 'Poids des statistiques CA/EBITDA par source ; normalisation par les sommes de poids du modèle.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_e25_e32 comparables_f25_f32 comparables_j47_j61 comparables_k47_k61 comparables_j76_j103 comparables_k76_k103',
       'score de pertinence sans dimension', 'Score servant de poids relatif à la sélection ; échelle et critères doivent être explicités dans les sources, sans inventer une probabilité.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_b25_b32 comparables_i25_i32 comparables_j25_j32 comparables_b47_b61 comparables_c47_c61 comparables_d47_d61 comparables_n47_n61 comparables_b76_b103 comparables_c76_c103 comparables_d76_d103 comparables_n76_n103',
       TEXT, 'Identité, périmètre, source ou hypothèses de l’observation comparable désignée.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_e47_e61 comparables_f47_f61 comparables_g47_g61 comparables_e76_e103 comparables_f76_f103 comparables_g76_g103',
       'millions d’EUR (M EUR)', 'CA, EBITDA ou valeur d’entreprise de la société/transaction ; convertir les données source à la même échelle et au périmètre indiqué.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_b117_b136 comparables_k117_k136', TEXT, 'Identifiant et preuve de l’observation de bêta, périmètre de dette et unité monétaire commune.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_c117_c136', CHOICE, 'Inclusion explicite dans la médiane bêta ; données complètes requises.', ('comparables_d117_d136','comparables_e117_e136','comparables_f117_f136','comparables_g117_g136'), calendar='DATE_DES_OBSERVATIONS')
define('comparables_d117_d136', 'coefficient bêta sans dimension', 'Bêta endetté observé selon fréquence/fenêtre et source.', ('comparables_l117_l136','comparables_m117_m136','comparables_j117_j136'), calendar='DATE_DES_OBSERVATIONS')
define('comparables_e117_e136 comparables_f117_f136', 'même unité monétaire documentée pour equity et dette',
       'Montants utilisés uniquement ensemble en ratio dette/equity ; monnaie et facteur d’échelle identiques exigés, aucune conversion implicite.', ('comparables_e117_e136','comparables_f117_f136','comparables_k117_k136'), calendar='DATE_DES_OBSERVATIONS', anchors=('Comparables!I117',))
define('comparables_g117_g136', RATE, 'Taux marginal d’IS utilisé pour désendetter le bêta de la société ; pas le taux normatif du nouveau client.', ('comparables_d117_d136','comparables_e117_e136','comparables_f117_f136'), calendar='DATE_DES_OBSERVATIONS', anchors=('Comparables!I117',))
define('comparables_j117_j136', DATE, 'Date des données de l’observation bêta.', calendar='DATE_DES_OBSERVATIONS')
define('comparables_l117_l136', CHOICE, 'Fréquence d’observation des rendements utilisés pour le bêta.', ('comparables_m117_m136',), calendar='DATE_DES_OBSERVATIONS')
define('comparables_m117_m136', 'années de fenêtre historique', 'Longueur de la fenêtre d’estimation du bêta ; distincte du calendrier du BP.', ('comparables_l117_l136',), calendar='DATE_DES_OBSERVATIONS')
