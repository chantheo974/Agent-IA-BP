"""Publication et refus transactionnels sur dossiers fictifs, sans Excel."""
from __future__ import annotations

from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.calculation_operations import _preflight
from tca_bp.service import Application
from tca_bp.storage import atomic_json, canonical, digest
from tests.test_service_adversarial import WitnessEngine


def assessment():
    return {'status': 'EVALUE', 'scopes': {name: {
        'scenario_ready': True, 'qualification_ready': False, 'available': False,
        'blockers': [], 'hypotheses': [{'code': 'HYPOTHESE', 'message': 'Scénario provisoire'}]
    } for name in ('CA', 'COGS', 'FISCALITE', 'CASH', 'DCF')}}


class PreflightTests(unittest.TestCase):
    def test_provisional_sourced_scenario_can_be_calculated(self):
        for operation in ('wacc', 'sensitivity'):
            _preflight(assessment(), operation)

    def test_sensitivity_requires_only_its_four_upstream_scopes(self):
        value = assessment()
        del value['scopes']['DCF']
        _preflight(value, 'sensitivity')
        with self.assertRaises(ValueError):
            _preflight(value, 'wacc')

    def test_wacc_allows_only_missing_wacc_and_dcf_formula_errors(self):
        value = assessment()
        value['scopes']['DCF'].update(scenario_ready=False, blockers=[
            {'code': 'WACC_NON_VERIFIE'}, {'code': 'ERREURS_FORMULES_NON_RESOLUES'}])
        _preflight(value, 'wacc')
        _preflight(value, 'sensitivity')  # aucune table n'utilise la DCF
        for name in ('CA', 'COGS', 'FISCALITE', 'CASH'):
            invalid = deepcopy(value)
            invalid['scopes'][name].update(scenario_ready=False,
                blockers=[{'code': 'ERREURS_FORMULES_NON_RESOLUES'}])
            for operation in ('wacc', 'sensitivity'):
                with self.subTest(name=name, operation=operation), self.assertRaises(ValueError):
                    _preflight(invalid, operation)

    def test_unqualified_market_input_and_terminal_bfr_still_block_wacc(self):
        for code in ('SOURCE_NON_VERIFIEE', 'PANEL_NON_QUALIFIE', 'BFR_TERMINAL_NON_VALIDE',
                     'PERIMETRE_AMONT_NON_QUALIFIE'):
            value = assessment()
            value['scopes']['DCF'].update(scenario_ready=False, blockers=[{'code': code}])
            with self.subTest(code=code), self.assertRaises(ValueError):
                _preflight(value, 'wacc')

    def test_incomplete_or_malformed_assessment_is_refused(self):
        variants = [None, [], {}, {'status': 'EVALUE', 'scopes': {}}, assessment()]
        variants[-1]['scopes']['CA']['scenario_ready'] = False
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValueError):
                _preflight(value, 'wacc')


class CalculationOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.engine = WitnessEngine(self.root)
        self.app = Application(self.root, self.root / 'data', engine=self.engine)
        self.app.create_case('Client fictif', 'Scénario fictif', case_id='fiction')
        self.document = self.root / 'hypothese.txt'
        self.document.write_text('Valeur hypothétique de cinq unités.', encoding='utf-8')
        self.source = self.app.add_source('fiction', path=self.document)
        plan = self.app.prepare_changes('fiction', [{'sheet': 'Entrées', 'cell': 'A1',
            'value': 5, 'reason': 'Hypothèse de travail documentée', 'evidence': self.source['id'],
            'status': 'HYPOTHESE'}])
        self.app.apply_plan('fiction', plan['id'])
        self.evaluation = patch.object(self.app, '_evaluate_qualifications_locked',
                                       side_effect=self.qualified)
        self.evaluation.start()
        self.addCleanup(self.evaluation.stop)
        self.native_calls = 0

    def qualified(self, row=None, *args):
        return {**assessment(), 'basis_sha256': self.app._qualification_basis(row or self.app._row('fiction'))['fingerprint']}

    def native(self, source, output, receipt, *, sensitivity=False, **kwargs):
        self.native_calls += 1
        original = digest(source)
        data = json.loads(source.read_text(encoding='utf-8'))
        data['cache'] = self.native_calls
        output.write_text(canonical(data), encoding='utf-8')
        result = {'status': 'TABLES_VERIFIEES' if sensitivity else 'CONVERGENCE_LOCALE',
            'source_sha256': original, 'output_sha256': digest(output), 'adopted': False,
            'macros_enabled': False, 'iteration_enabled': False, 'source_preserved': True,
            'save_reopen_verified': True, 'calculation_state': 0,
            'global_uniqueness_proven': False, 'financial_model_globally_validated': False}
        if sensitivity:
            signature = self.engine.context(source)['input_signature']
            result.update(passed=True, input_signature_before=signature,
                          input_signature_after=signature, comparisons=[{'passed': True}])
        atomic_json(receipt, result)
        return result

    def invoke(self, operation='wacc', worker=None):
        if operation == 'wacc':
            with patch('tca_bp.wacc_native.solve_native', worker or self.native):
                return self.app.solve_wacc('fiction')
        def tables(engine, *args, **kwargs):
            return self.native(*args, sensitivity=True, **kwargs)
        with patch('tca_bp.sensitivity_native.verify_native', worker or tables):
            return self.app.verify_sensitivity('fiction')

    def events(self, kind):
        with self.app.store.connection() as db:
            return [json.loads(row['details']) for row in db.execute(
                'SELECT details FROM history WHERE case_id=? AND kind=? ORDER BY rowid', ('fiction', kind))]

    def test_success_publishes_exactly_one_version_and_keeps_hypotheses(self):
        before = self.app._row('fiction')
        source_hash = digest(self.app._workbook(before))
        result = self.invoke()
        after = self.app._row('fiction')
        self.assertEqual(after['revision'], before['revision'] + 1)
        self.assertEqual(after['field_states'], before['field_states'])
        self.assertTrue(all(v['status'] == 'HYPOTHESE' for v in json.loads(after['field_states']).values()))
        self.assertEqual(digest(self.app._workbook(before)), source_hash)
        self.assertEqual(after['sha256'], digest(Path(result['workbook_path'])))
        self.assertEqual(len(self.events('WACC_RESOLU')), 1)
        self.assertEqual(len(self.events('RECALCUL_EXCEL')), 1)
        self.assertFalse(result['global_uniqueness_proven'])
        self.assertTrue(all(not v['available'] for v in result['qualified_availability'].values()))
        self.assertIsNotNone(self.app._specific_calculation_proofs(after)['wacc'])

    def test_sql_failure_cannot_leave_an_adopted_external_receipt(self):
        before = self.app._row('fiction')
        history = self.app.store.history
        def writing(db, case_id, kind, details):
            if kind == 'RECALCUL_EXCEL':
                self.assertTrue(details['adopted'])
                path = Path(details['workbook_path']).with_suffix('.verification.json')
                self.assertFalse(json.loads(path.read_text(encoding='utf-8'))['adopted'])
                raise OSError('Échec SQL fictif avant commit')
            history(db, case_id, kind, details)
        with patch.object(self.app.store, 'history', side_effect=writing):
            with self.assertRaisesRegex(OSError, 'Échec SQL'):
                self.invoke()
        self.assertEqual(self.app._row('fiction')['revision'], before['revision'])
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])
        path = next(self.app.store.case_dir('fiction').glob('versions/*.verification.json'))
        self.assertFalse(json.loads(path.read_text(encoding='utf-8'))['adopted'])

    def test_post_commit_verification_mirror_failure_keeps_adopted_result(self):
        def writing(path, value):
            if path.name.endswith('.verification.json') and value.get('adopted') is True:
                raise OSError('Miroir du reçu fictivement indisponible')
            atomic_json(path, value)
        with patch('tca_bp.calculation_operations.atomic_json', side_effect=writing):
            result = self.invoke()
        self.assertTrue(result['adopted'])
        self.assertIn('miroir', result['report_notice'])
        self.assertFalse(json.loads(Path(result['report_path']).read_text(encoding='utf-8'))['adopted'])
        self.assertTrue(self.events('RECALCUL_EXCEL')[0]['adopted'])
        self.assertEqual(len(self.events('RECU_RECALCUL_MIROIR_INCOMPLET')), 1)
        self.assertIsNotNone(self.app._specific_calculation_proofs(self.app._row('fiction'))['wacc'])

    def test_failure_keeps_current_pointer_and_preserves_artifacts(self):
        before = self.app._row('fiction')
        def failed(*args, **kwargs):
            self.native(*args, **kwargs)
            raise ValueError('Non convergence fictive')
        with self.assertRaisesRegex(ValueError, 'Non convergence'):
            self.invoke(worker=failed)
        after = self.app._row('fiction')
        self.assertEqual((after['revision'], after['sha256']), (before['revision'], before['sha256']))
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])
        reports = list(self.app.store.case_dir('fiction').glob('transactions/wacc_*/transaction.json'))
        receipt = json.loads(reports[0].read_text(encoding='utf-8'))
        self.assertEqual(receipt['status'], 'ECHEC_A_INSPECTER')
        self.assertFalse(receipt['adopted'])
        self.assertEqual(len(receipt['created_artifacts']), 2)
        recovery = self.app.recovery_status('fiction')['transactions_to_inspect'][0]
        self.assertEqual(recovery['status'], 'CALCUL_NON_ADOPTE_A_INSPECTER')
        self.assertFalse(recovery['needs_reapply'])

    def test_identical_later_calculation_does_not_mark_failed_attempt_as_committed(self):
        def failed(*args, **kwargs):
            self.native(*args, **kwargs)
            raise ValueError('Échec après sauvegarde fictive')
        with self.assertRaises(ValueError):
            self.invoke(worker=failed)
        self.native_calls = 0  # le second worker produit exactement les mêmes octets
        self.invoke()
        recovery = self.app.recovery_status('fiction')['transactions_to_inspect'][0]
        self.assertEqual(recovery['status'], 'CALCUL_NON_ADOPTE_A_INSPECTER')
        self.assertFalse(recovery['needs_reapply'])

    def test_concurrent_invocation_is_refused_before_second_worker(self):
        def concurrent(*args, **kwargs):
            with self.assertRaisesRegex(ValueError, 'transaction en cours'):
                self.app.solve_wacc('fiction')
            return self.native(*args, **kwargs)
        self.invoke(worker=concurrent)
        self.assertEqual(self.native_calls, 1)
        self.assertEqual(len(self.events('WACC_RESOLU')), 1)

    def test_invalid_timeout_never_evaluates_or_launches_native(self):
        for operation, method, maximum in [('wacc', self.app.solve_wacc, 600),
                                           ('sensitivity', self.app.verify_sensitivity, 3600)]:
            for timeout in (True, 0, -1, maximum + 1, float('inf'), float('nan'), '60'):
                with self.subTest(operation=operation, timeout=timeout), self.assertRaises(ValueError):
                    method('fiction', timeout=timeout)
        self.assertEqual(self.native_calls, 0)
        self.app._evaluate_qualifications_locked.assert_not_called()

    def test_changed_document_blocks_adoption(self):
        before = self.app._row('fiction')
        def changed(*args, **kwargs):
            result = self.native(*args, **kwargs)
            stored = self.app.store.case_dir('fiction') / self.source['path']
            stored.write_text('Valeur remplacée sans preuve', encoding='utf-8')
            return result
        with self.assertRaisesRegex(ValueError, 'sources|qualifications'):
            self.invoke(worker=changed)
        self.assertEqual(self.app._row('fiction')['revision'], before['revision'])

    def test_document_changed_after_qualification_is_refused_before_worker(self):
        def evaluated(row, *args):
            result = self.qualified(row)
            stored = self.app.store.case_dir('fiction') / self.source['path']
            stored.write_text('Document changé après évaluation', encoding='utf-8')
            return result
        self.app._evaluate_qualifications_locked.side_effect = evaluated
        with self.assertRaisesRegex(ValueError, 'depuis leur évaluation'):
            self.invoke()
        self.assertEqual(self.native_calls, 0)

    def test_changed_model_pin_during_native_blocks_adoption(self):
        before = self.app._row('fiction')
        def changed(*args, **kwargs):
            result = self.native(*args, **kwargs)
            with self.app.store.connection() as db:
                db.execute('UPDATE cases SET schema_sha256=? WHERE id=?', ('0' * 64, 'fiction'))
            return result
        with self.assertRaisesRegex(ValueError, 'dossier|modèle'):
            self.invoke(worker=changed)
        self.assertEqual(self.app._row('fiction')['revision'], before['revision'])
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])

    def test_changed_workbook_source_blocks_adoption(self):
        before = self.app._row('fiction')
        def changed(source, *args, **kwargs):
            result = self.native(source, *args, **kwargs)
            source.write_text(source.read_text(encoding='utf-8') + ' ', encoding='utf-8')
            return result
        with self.assertRaises(ValueError):
            self.invoke(worker=changed)
        self.assertEqual(self.app._row('fiction')['revision'], before['revision'])

    def test_changed_inputs_in_output_block_adoption(self):
        def changed(source, output, receipt, **kwargs):
            result = self.native(source, output, receipt, **kwargs)
            data = json.loads(output.read_text(encoding='utf-8'))
            data['input'] = 777
            output.write_text(canonical(data), encoding='utf-8')
            result['output_sha256'] = digest(output)
            atomic_json(receipt, result)
            return result
        with self.assertRaisesRegex(ValueError, 'entrées'):
            self.invoke(worker=changed)
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])

    def test_receipt_file_must_equal_the_native_return_value(self):
        def changed(source, output, receipt, **kwargs):
            result = self.native(source, output, receipt, **kwargs)
            atomic_json(receipt, {**result, 'source_preserved': False})
            return result
        with self.assertRaisesRegex(ValueError, 'diffère'):
            self.invoke(worker=changed)
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])

    def test_late_receipt_change_before_publication_is_refused(self):
        def writing(path, value):
            atomic_json(path, value)
            if path.suffixes[-2:] == ['.verification', '.json']:
                path.with_name(path.name.replace('.verification.json', '.native.json')).write_text('{}', encoding='utf-8')
        with patch('tca_bp.calculation_operations.atomic_json', side_effect=writing):
            with self.assertRaisesRegex(ValueError, 'fichiers du calcul'):
                self.invoke()
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])

    def test_tables_work_without_wacc_and_do_not_invent_its_proof(self):
        result = self.invoke('sensitivity')
        proofs = self.app._specific_calculation_proofs(self.app._row('fiction'))
        self.assertEqual(result['status'], 'TABLES_VERIFIEES')
        self.assertIsNone(proofs['wacc'])
        self.assertIsNotNone(proofs['sensitivity'])

    def test_tables_receipt_with_wrong_input_signature_is_not_published(self):
        def changed(engine, source, output, receipt, **kwargs):
            result = self.native(source, output, receipt, sensitivity=True, **kwargs)
            result['input_signature_before'] = 'autre état'
            atomic_json(receipt, result)
            return result
        with self.assertRaisesRegex(ValueError, 'ne prouve pas'):
            self.invoke('sensitivity', worker=changed)
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])

    def test_wacc_survives_two_tables_receipts_and_restart(self):
        self.invoke()
        original = self.app._specific_calculation_proofs(self.app._row('fiction'))['wacc']
        self.invoke('sensitivity')
        result = self.invoke('sensitivity')
        proof = result['wacc_proof']
        self.assertEqual(proof['inherited_wacc_proof']['inherited_wacc_proof'], original)
        restarted = Application(self.root, self.root / 'data', engine=self.engine)
        state = restarted.get_case('fiction')
        self.assertTrue(state['wacc_verified'])
        self.assertTrue(state['sensitivity_verified'])
        self.assertEqual(len(self.events('RECALCUL_EXCEL')), 3)

    def test_changed_origin_receipt_invalidates_carried_wacc_after_restart(self):
        result = self.invoke()
        origin = Path(result['wacc_proof']['receipt_path'])
        self.invoke('sensitivity')
        before = self.app._qualification_basis(self.app._row('fiction'))['fingerprint']
        origin.write_text('{}', encoding='utf-8')
        restarted = Application(self.root, self.root / 'data', engine=self.engine)
        state = restarted.get_case('fiction')
        self.assertFalse(state['wacc_verified'])
        self.assertTrue(state['sensitivity_verified'])
        self.assertNotEqual(before, restarted._qualification_basis(restarted._row('fiction'))['fingerprint'])

    def test_mcp_read_revalidates_persisted_receipt_without_native_execution(self):
        from tca_bp.mcp_server import serve
        self.invoke()
        receipt = self.invoke('sensitivity')['sensitivity_proof']['receipt_path']
        restarted = Application(self.root, self.root / 'data', engine=self.engine)
        query = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                 'params': {'name': 'bp_get_case', 'arguments': {'case_id': 'fiction'}}}
        def read():
            output = io.StringIO()
            serve(restarted, io.StringIO(json.dumps(query) + '\n'), output)
            result = json.loads(output.getvalue())['result']
            self.assertFalse(result.get('isError', False))
            return json.loads(result['content'][0]['text'])
        with patch('tca_bp.wacc_native.solve_native') as wacc, patch('tca_bp.sensitivity_native.verify_native') as tables:
            self.assertTrue(read()['wacc_verified'])
            Path(receipt).write_text('{}', encoding='utf-8')
            after = read()
            self.assertFalse(after['wacc_verified'])
            self.assertFalse(after['sensitivity_verified'])
            wacc.assert_not_called()
            tables.assert_not_called()

    def test_new_wacc_does_not_reuse_old_tables_proof(self):
        self.invoke('sensitivity')
        self.invoke()
        proofs = self.app._specific_calculation_proofs(self.app._row('fiction'))
        self.assertIsNotNone(proofs['wacc'])
        self.assertIsNone(proofs['sensitivity'])

    def test_unsafe_native_result_is_refused_despite_matching_file(self):
        def unsafe(source, output, receipt, **kwargs):
            result = self.native(source, output, receipt, **kwargs)
            result['iteration_enabled'] = True
            atomic_json(receipt, result)
            return result
        with self.assertRaisesRegex(ValueError, 'contrôles natifs'):
            self.invoke(worker=unsafe)
        self.assertEqual(self.events('RECALCUL_EXCEL'), [])

    def test_post_commit_qualification_failure_keeps_calculation_and_reports_unavailability(self):
        self.app._evaluate_qualifications_locked.side_effect = [self.qualified(), ValueError('Source de qualification indisponible')]
        result = self.invoke()
        self.assertEqual(result['status'], 'CONVERGENCE_LOCALE')
        self.assertEqual(result['qualification_status'], 'A_EVALUER')
        self.assertTrue(all(not item['available'] for item in result['qualified_availability'].values()))
        self.assertEqual(len(self.events('RECALCUL_EXCEL')), 1)
        self.assertEqual(len(self.events('QUALIFICATION_ECHOUEE_APRES_RECALCUL')), 1)

    def test_changed_wacc_receipt_during_tables_blocks_adoption(self):
        original = self.invoke()['wacc_proof']
        before = self.app._row('fiction')
        def changed(engine, *args, **kwargs):
            result = self.native(*args, sensitivity=True, **kwargs)
            Path(original['receipt_path']).write_text('{}', encoding='utf-8')
            return result
        with self.assertRaisesRegex(ValueError, 'sources|qualifications|WACC'):
            self.invoke('sensitivity', worker=changed)
        self.assertEqual(self.app._row('fiction')['revision'], before['revision'])

    def test_state_mirror_failure_after_commit_does_not_roll_back_publication(self):
        before = self.app._row('fiction')
        with patch.object(self.app, '_save_state', side_effect=OSError('Miroir temporairement bloqué')):
            with self.assertRaisesRegex(OSError, 'Miroir'):
                self.invoke()
        self.assertEqual(self.app._row('fiction')['revision'], before['revision'] + 1)
        self.assertEqual(len(self.events('RECALCUL_EXCEL')), 1)
        path = next(self.app.store.case_dir('fiction').glob('transactions/wacc_*/transaction.json'))
        transaction = json.loads(path.read_text(encoding='utf-8'))
        self.assertTrue(transaction['adopted'])
        self.assertEqual(transaction['status'], 'COMMIT_CONFIRME_MIROIR_INCOMPLET')
        recovery = self.app.recovery_status('fiction')['transactions_to_inspect'][0]
        self.assertEqual(recovery['status'], 'COMMIT_CONFIRME_MIROIR_INCOMPLET')
        self.assertFalse(recovery['needs_reapply'])


class QualificationCalculationIntegrationTests(unittest.TestCase):
    """Vrais service et évaluateur ; seul le travailleur Excel est simulé."""
    def setUp(self):
        from tests.test_qualification_service import QualificationEngine
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.engine = QualificationEngine(root)
        self.app = Application(root, root / 'data', engine=self.engine)
        self.app.create_case('Client fictif', 'Qualification et tables', case_id='a')
        self.source = self.app.add_source('a', text='Décisions explicites fictives pour une recette logicielle.')
        updates = [{'sheet': key.rsplit('!', 1)[0], 'cell': key.rsplit('!', 1)[1],
            'value': value['value'], 'status': 'CONFIRME', 'evidence': self.source['id'], 'reason': 'Décision fictive'}
            for key, value in self.engine.states.items()]
        plan = self.app.prepare_changes('a', updates)
        self.app.apply_plan('a', plan['id'])
        for module, declaration in self.engine.declarations.items():
            clean = {key: value for key, value in declaration.items() if key not in ('model_id', 'template_sha256')}
            self.app.declare_qualification('a', {**clean, 'module': module,
                'evidence': self.source['id'], 'reason': 'Déclaration explicite fictive'})

    def tables(self, engine, source, output, receipt, **kwargs):
        data = json.loads(source.read_text(encoding='utf-8'))
        data['cache'] = 120
        output.write_text(canonical(data), encoding='utf-8')
        signature = engine.context(source)['input_signature']
        result = {'status': 'TABLES_VERIFIEES', 'source_sha256': digest(source), 'output_sha256': digest(output),
            'adopted': False, 'macros_enabled': False, 'iteration_enabled': False,
            'source_preserved': True, 'save_reopen_verified': True, 'calculation_state': 0,
            'passed': True, 'input_signature_before': signature, 'input_signature_after': signature}
        atomic_json(receipt, result)
        return result

    def test_real_guards_allow_tables_with_unqualified_dcf_and_inspect_rechecks_receipt(self):
        plan = self.app.prepare_changes('a', [{'sheet': 'Valorisation', 'cell': 'D107',
            'value': None, 'status': 'NON_RENSEIGNE', 'evidence': self.source['id'],
            'reason': 'Le mode de valorisation reste à choisir', 'replace_existing': True}])
        self.app.apply_plan('a', plan['id'])
        with patch('tca_bp.wacc_native.solve_native') as wacc:
            with self.assertRaisesRegex(ValueError, 'Calcul indisponible'):
                self.app.solve_wacc('a')
            wacc.assert_not_called()
        with patch('tca_bp.sensitivity_native.verify_native', self.tables):
            result = self.app.verify_sensitivity('a')
        state = self.app.get_case('a')
        self.assertTrue(state['sensitivity_verified'])
        self.assertFalse(state['wacc_verified'])
        self.assertTrue(state['qualified_availability']['CASH']['available'])
        self.assertFalse(state['qualified_availability']['DCF']['available'])
        self.assertEqual(self.app.inspect('a', 'Sensi Analyses', ['D24'])['cells']['D24']['current']['value'], 120)
        Path(result['sensitivity_proof']['receipt_path']).write_text('{}', encoding='utf-8')
        self.assertIsNone(self.app.inspect('a', 'Sensi Analyses', ['D24'])['cells']['D24']['current']['value'])

    def test_provisional_fiscal_scope_can_calculate_but_is_never_confirmed(self):
        self.app.declare_qualification('a', {'module': 'CIR', 'state': 'INACTIF', 'status': 'HYPOTHESE',
            'evidence': self.source['id'], 'reason': 'Décision fictive encore à confirmer'})
        with patch('tca_bp.sensitivity_native.verify_native', self.tables):
            result = self.app.verify_sensitivity('a')
        self.assertEqual(result['status'], 'TABLES_VERIFIEES')
        state = self.app.get_case('a')
        self.assertTrue(state['sensitivity_verified'])
        self.assertEqual(state['qualification_declarations']['CIR']['status'], 'HYPOTHESE')
        self.assertTrue(state['qualified_availability']['CASH']['scenario_ready'])
        self.assertFalse(state['qualified_availability']['CASH']['available'])
        self.assertIsNone(self.app.inspect('a', 'Sensi Analyses', ['D24'])['cells']['D24']['current']['value'])


if __name__ == '__main__':
    unittest.main()
