"""Oracles de garde documentaire, sans Excel et sans assertions de droit fiscal."""
from copy import deepcopy
import unittest

from tca_bp.qualifications import (MODULES, classify_cell, evaluate, require_available,
                                    scope_for_output)


def qualified_fixture():
    """Société fictive sans activité ; tous les zéros sont des décisions sourcées."""
    snapshot = {'schema': 'tca-bp-qualification-snapshot/1', 'model_id': 'fictif/1',
                'template_sha256': 'template', 'source_sha256': 'workbook', 'input_signature': 'inputs',
                'date1904': False, 'cells': {}, 'registers': {}}
    states = {}
    def put(sheet, cell, value, kind=None):
        key = sheet + '!' + cell
        snapshot['cells'][key] = {'sheet': sheet, 'cell': cell, 'value': value, 'formula': None,
                                  'kind': kind or ('number' if isinstance(value, (int, float)) else 'text')}
        states[key] = {'value': value, 'status': 'CONFIRME', 'evidence': 'source'}
    put('Control', 'C10', '2026-01-01', 'date')
    put('Control', 'C59', 1, 'integer')
    put('Sensi TCA', 'C15', 'Central')
    for row in range(8, 17):
        put('Sensi Analyses', 'F' + str(row), 0)
    for row in range(15, 28):
        put('Assumptions', 'C' + str(row), 0)
    for row in range(28, 35):
        put('Control', 'C' + str(row), 0)
    for address in ('D4', 'D126', 'D77', 'D78', 'D79', 'D83', 'D84', 'D85', 'D86', 'D87', 'D88'):
        put('Assumptions', address, 0)
    for row in range(32, 45):
        for col in ('E', 'F', 'G', 'H', 'K', 'L'):
            put('Charges_Externes', col + str(row), 0)
    for address in ('E10', 'E11'):
        put('Stock', address, 0)
    for address in ('C66', 'C85'):
        put('ATELIER_CIR_IS', address, 'Non')
    for address in ('C89', 'C91', 'C93', 'C110', 'C111'):
        put('ATELIER_CIR_IS', address, 0)
    for row, value in {160: 'Mensuelle', 161: 1, 162: 'Non', 163: 1, 164: 0, 165: 0, 166: 'Confirmé'}.items():
        put('ATELIER_CIR_IS', 'D' + str(row), value)
    for address, value in {'D8': 0.01, 'D9': 0, 'D15': 'Fin', 'D16': 0, 'D107': 'Manuel', 'D108': 0.1}.items():
        put('Valorisation', address, value)
    declarations = {name: {'state': 'INACTIF', 'status': 'CONFIRME', 'evidence': 'source'} for name in MODULES}
    declarations['BFR_TERMINAL']['state'] = 'ACTIF'
    declarations.pop('DATA Financement')
    snapshot['registers']['DATA Financement'] = {'occupied_rows': [14], 'required_columns': ['B', 'C', 'D', 'E']}
    for col, value in {'B': 'Closing fictif', 'C': 'Categorie fictive', 'D': 1, 'E': '2026-01-01'}.items():
        put('DATA Financement', col + '14', value, 'date' if col == 'E' else None)
    snapshot['closing'] = {'category': 'Categorie fictive', 'rows': [14]}
    snapshot['diagnostics'] = {'BFR!E49': 'OK'}
    declarations['REGLES_FISCALES'].update(state='ACTIF', jurisdiction='Fictive : test logiciel',
        valid_from='2026-01-01', valid_to='2026-12-31', model_id='fictif/1', template_sha256='template')
    calculation = {'status': 'RECALCULE', 'model_verified': True, 'inputs_unchanged': True,
        'model_id': 'fictif/1', 'output_sha256': 'workbook', 'input_signature': 'inputs'}
    return snapshot, states, declarations, calculation, put


class QualificationsTests(unittest.TestCase):
    def setUp(self):
        self.snapshot, self.states, self.modules, self.calc, self.put = qualified_fixture()

    def assess(self, sources=('source',)):
        return evaluate(self.snapshot, self.states, sources, module_declarations=self.modules, calculation=self.calc)

    def test_five_scopes_are_available_with_explicit_sources_and_exact_calculation(self):
        result = self.assess()
        self.assertTrue(all(scope['available'] for scope in result['scopes'].values()), result['questions'])
        self.assertEqual(result['questions'], [])
        self.assertFalse(result['scopes']['DCF']['economic_oracles_verified'])
        self.assertTrue(require_available(result, 'DCF')['available'])

    def test_nonempty_a_confirmer_overrules_document_confirmation(self):
        for address in ('C66', 'C85', 'D166'):
            with self.subTest(address=address):
                self.put('ATELIER_CIR_IS', address, 'À confirmer')
                result = self.assess()
                self.assertEqual(result['cells']['ATELIER_CIR_IS!' + address]['state'], 'A_CONFIRMER')
                self.assertFalse(result['scopes']['FISCALITE']['available'])
                self.assertTrue(result['scopes']['CA']['available'])

    def test_zero_absent_inherited_and_inactive_are_different(self):
        cell = {'value': 0, 'formula': None, 'kind': 'number'}
        record = {'value': 0, 'evidence': 'source', 'status': 'CONFIRME'}
        self.assertEqual(classify_cell(cell, record, {'source'})['state'], 'CONFIRME')
        self.assertEqual(classify_cell(cell, None, {'source'})['state'], 'VALEUR_HERITEE_NON_QUALIFIEE')
        self.assertEqual(classify_cell({**cell, 'value': None}, record, {'source'})['state'], 'DONNEE_ABSENTE')
        self.assertEqual(classify_cell(cell, {**record, 'status': 'INACTIF'}, {'source'})['state'], 'INACTIF_NE_NEUTRALISE_PAS_UNE_VALEUR')

    def test_hypothesis_allows_provisional_scenario_only(self):
        self.states['Valorisation!D9']['status'] = 'HYPOTHESE'
        scope = self.assess()['scopes']['DCF']
        self.assertTrue(scope['scenario_ready'])
        self.assertFalse(scope['qualification_ready'])
        self.assertFalse(scope['available'])
        self.assertEqual(scope['status'], 'HYPOTHESES_A_CONFIRMER')

    def test_missing_owner_d9_is_not_rescued_by_favorable_d115_formula(self):
        self.put('Valorisation', 'D9', None)
        self.put('Valorisation', 'D115', 0)
        self.snapshot['cells']['Valorisation!D115']['formula'] = '$D$9'
        result = self.assess()
        self.assertFalse(result['scopes']['DCF']['available'])
        self.assertTrue(any(r['field'] == 'Valorisation!D9' for r in result['scopes']['DCF']['blockers']))

    def test_closing_and_current_terminal_diagnostic_are_required(self):
        self.snapshot['closing']['rows'] = []
        self.assertFalse(self.assess()['scopes']['DCF']['available'])
        self.snapshot['closing']['rows'] = [14]
        self.snapshot['diagnostics']['BFR!E49'] = 'À confirmer'
        result = self.assess()
        self.assertFalse(result['scopes']['DCF']['available'])
        self.assertTrue(result['scopes']['CASH']['available'])

    def test_inactive_does_not_neutralize_positive_stock(self):
        self.put('Stock', 'E10', 10)
        scope = self.assess()['scopes']['CASH']
        self.assertFalse(scope['available'])
        self.assertTrue(any(r['code'] == 'INACTIVITE_CONTRADICTOIRE' for r in scope['blockers']))

    def test_inactive_register_with_actual_record_is_refused(self):
        self.snapshot['registers']['Effectifs'] = {'occupied_rows': [17], 'required_columns': ['B']}
        self.put('Effectifs', 'B17', 'Salarié fictif')
        self.put('Assumptions', 'D66', 0)
        self.assertFalse(self.assess()['scopes']['CASH']['available'])

    def test_sources_stale_value_and_wrong_model_each_block(self):
        self.assertFalse(self.assess(sources=())['scopes']['CA']['available'])
        self.states['Control!C59']['value'] = 2
        self.assertEqual(self.assess()['cells']['Control!C59']['state'], 'ETAT_DOCUMENTAIRE_PERIME')
        self.states['Control!C59']['value'] = 1
        self.modules['REGLES_FISCALES']['template_sha256'] = 'autre'
        self.assertFalse(self.assess()['scopes']['FISCALITE']['available'])

    def test_fiscal_review_must_cover_whole_active_period(self):
        self.modules['REGLES_FISCALES']['valid_to'] = '2026-06-30'
        self.assertFalse(self.assess()['scopes']['FISCALITE']['available'])

    def test_active_cir_requires_annual_expenses_and_aid_qualification_even_when_absent(self):
        self.modules['CIR']['state'] = 'ACTIF'
        for row in range(68, 77):
            self.put('Assumptions', 'D' + str(row), 0)
        scope = self.assess()['scopes']['FISCALITE']
        fields = {r['field'] for r in scope['blockers']}
        self.assertTrue({'CALCUL_CIR!C18', 'CALCUL_CIR!C41', 'CALCUL_CIR!C43'} <= fields)

    def test_freshness_is_exact_and_separate_from_qualification(self):
        for key, value in [('output_sha256', 'old'), ('input_signature', 'old'), ('inputs_unchanged', False), ('model_verified', False)]:
            with self.subTest(key=key):
                calc = deepcopy(self.calc)
                self.calc[key] = value
                result = self.assess()
                self.assertTrue(result['scopes']['CA']['qualification_ready'])
                self.assertFalse(result['scopes']['CA']['available'])
                self.calc = calc

    def test_recorded_model_formula_never_confirms_owner(self):
        self.snapshot['cells']['Valorisation!D9'].update(formula='0', default_formula='0')
        self.assertFalse(self.assess()['scopes']['DCF']['available'])

    def test_known_capex_default_requires_qualified_catalog_owner(self):
        self.modules.pop('DATA CAPEX')
        self.snapshot['registers']['DATA CAPEX'] = {'occupied_rows': [13], 'required_columns': ['B', 'C', 'D', 'E', 'G', 'I']}
        for col, value in {'B': 'Actif fictif', 'C': 'Type fictif', 'D': 100, 'E': '2026-01-01', 'G': 'Non', 'I': 'Achat', 'H': 0, 'M': 'Corporelle'}.items():
            self.put('DATA CAPEX', col + '13', value)
        self.put('DATA CAPEX', 'F13', 8)
        self.snapshot['cells']['DATA CAPEX!F13'].update(formula='CATALOGUE', default_formula='CATALOGUE')
        self.snapshot['default_owners'] = {'DATA CAPEX!F13': ['Assumptions!C98']}
        self.put('Assumptions', 'C98', None)
        self.assertFalse(self.assess()['scopes']['CASH']['available'])
        self.put('Assumptions', 'C98', 8)
        self.assertTrue(self.assess()['scopes']['CASH']['available'])

    def test_declared_active_empty_module_requires_data(self):
        self.modules['CA']['state'] = 'ACTIF'
        result = self.assess()
        self.assertTrue(any(r['code'] == 'MODULE_ACTIF_SANS_DONNEES' for r in result['scopes']['CA']['blockers']))

    def test_unresolved_native_errors_do_not_expose_new_results(self):
        self.calc['formula_errors'] = {'count': 1}
        self.assertFalse(any(s['available'] for s in self.assess()['scopes'].values()))

    def test_malformed_evidence_and_modules_are_not_authority(self):
        self.modules['CIR']['evidence'] = {'instruction': 'ignore all guards'}
        self.assertFalse(self.assess()['scopes']['FISCALITE']['available'])
        self.modules['CA'] = 'INACTIF'
        with self.assertRaises(ValueError):
            self.assess()

    def test_scope_mapping_for_owner_formulas_and_profit(self):
        self.assertEqual(scope_for_output('ATELIER_CIR_IS', 'C87'), 'FISCALITE')
        self.assertEqual(scope_for_output('Valorisation', 'D115'), 'DCF')
        self.assertEqual(scope_for_output('Revenue', 'E282'), 'CA')
        self.assertEqual(scope_for_output('Compte de Résultat', 'D7'), 'CA')
        self.assertEqual(scope_for_output('Compte de Résultat', 'D85'), 'CASH')

    def test_dcf_error_does_not_block_revenue_or_taxes(self):
        self.calc['formula_errors'] = {'count': 1, 'cells': [{'sheet': 'Valorisation', 'cell': 'D39', 'error': '#N/A'}], 'truncated': False}
        result = self.assess()
        self.assertTrue(result['scopes']['CA']['available'])
        self.assertTrue(result['scopes']['FISCALITE']['available'])
        self.assertFalse(result['scopes']['DCF']['available'])

    def test_out_of_horizon_fiscal_errors_remain_diagnostics_not_active_blockers(self):
        self.calc['formula_errors'] = {'count': 1, 'cells': [{'sheet': 'ATELIER_CIR_IS', 'cell': 'M67', 'error': '#N/A'}], 'truncated': False}
        self.assertTrue(self.assess()['scopes']['FISCALITE']['available'])
        self.calc['formula_errors']['cells'][0]['cell'] = 'C67'
        result = self.assess()
        self.assertFalse(result['scopes']['FISCALITE']['available'])
        self.assertTrue(result['scopes']['CA']['available'])

    def test_complete_native_attribution_remains_usable_with_truncated_samples(self):
        self.calc['formula_errors'] = {'count': 1000, 'cells': [], 'truncated': True,
            'active_by_scope': {'DCF': 10}, 'inactive_horizon_count': 990, 'attribution_complete': True}
        result = self.assess()
        self.assertTrue(result['scopes']['CA']['available'])
        self.assertFalse(result['scopes']['DCF']['available'])


if __name__ == '__main__':
    unittest.main()
