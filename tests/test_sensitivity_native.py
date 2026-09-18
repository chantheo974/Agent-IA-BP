"""Preuves de protocole et comparateur ; aucune instance Excel dans ces tests."""
import copy
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp import sensitivity_native as native
from tca_bp.storage import digest


def mathematical_campaign():
    specs = native.scenarios()
    base = {'D24': 1000, 'E24': 700, 'F24': 100, 'G24': -200,
            'C39': 1000, 'D39': -200, 'C49': -200}
    tables, observations = {}, []
    for spec in specs:
        spec['sha256'] = spec['id'] + '_fixture_hash'
        volume, aid, index = (spec['drivers'][c] for c in native.DRIVERS)
        vector = {'D24': 1000 + volume*1000-index*10, 'E24': 700+volume*700-index*8,
                  'F24': 100+volume*300-index*7, 'G24': -200+volume*200+aid*500-index*6,
                  'C39': 1000+volume*1000, 'D39': -200+volume*200,
                  'C49': -200+volume*200+aid*500}
        outputs = {ref: vector[ref] for ref in spec['targets'].values()}
        tables.update({target: outputs[ref] for target, ref in spec['targets'].items()})
        observations.append({'id': spec['id'], 'sha256': spec['sha256'], 'drivers': spec['drivers'],
                             'calculation_state': 0, 'calculation_mode': 'AUTO_NO_TABLE',
                             'copy_preserved': True, 'outputs': outputs})
    receipt = {'tables': tables, 'persisted_tables': copy.deepcopy(tables),
               'base_outputs': base, 'persisted_base_outputs': copy.deepcopy(base),
               'scalars': observations, 'macros_enabled': False, 'iteration_enabled': False,
               'source_preserved': True, 'save_reopen_verified': True, 'calculation_state': 0,
               'restoration': 'ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE',
               'scalar_copies_saved': False, 'technical_writes_to_base': []}
    return {'scenarios': specs}, receipt


class SensitivityComparisonTests(unittest.TestCase):
    def test_preparation_consumes_native_deadline_before_any_process_is_started(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with patch.object(native,'available',return_value=True),patch.object(native.time,'monotonic',side_effect=[0,2]),patch.object(native,'prepare_campaign') as prepare,patch.object(native,'_verify_plan') as verify,patch.object(native.subprocess,'Popen') as launch:
                with self.assertRaises(TimeoutError):
                    native.verify_native(None,root/'source.xlsm',root/'output.xlsm',root/'receipt.json',timeout=1)
                prepare.assert_called_once()
                self.assertEqual(prepare.call_args.kwargs['deadline'],1)
                verify.assert_not_called()
                launch.assert_not_called()

    def test_exact_closed_scope_and_axes_orientation(self):
        specs = native.scenarios()
        self.assertEqual(len(specs), 24)
        self.assertEqual(sum(len(s['targets']) for s in specs), 57)
        self.assertEqual(len({a for s in specs for a in s['targets']}), 57)
        selected = next(s for s in specs if s['id'] == 'matrix_F51')
        self.assertEqual(selected['drivers'], {'C8': -.1, 'C14': -1, 'C18': 0})
        self.assertEqual(selected['targets'], {'F51': 'C49'})

    def test_all_57_independent_comparisons_pass(self):
        plan, receipt = mathematical_campaign()
        result = native.compare_results(plan, receipt)
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['comparisons']), 57)
        self.assertTrue(all(result['non_degeneracy'].values()))
        self.assertFalse(result['financial_model_globally_validated'])

    def test_missing_bool_error_nan_and_infinite_cannot_pass(self):
        for bad in (None, True, False, '', '0', '#N/A', math.nan, math.inf):
            for location in ('tables', 'persisted_tables', 'scalar'):
                plan, receipt = mathematical_campaign()
                if location == 'scalar':
                    receipt['scalars'][0]['outputs']['D24'] = bad
                else:
                    receipt[location]['D25'] = bad
                with self.subTest(value=bad, location=location), self.assertRaises(ValueError):
                    native.compare_results(plan, receipt)

    def test_one_wrong_cell_cannot_hide_behind_neutral_points(self):
        plan, receipt = mathematical_campaign()
        receipt['tables']['F51'] += 1
        receipt['persisted_tables']['F51'] += 1
        result = native.compare_results(plan, receipt)
        self.assertFalse(result['passed'])
        self.assertEqual([c['cell'] for c in result['comparisons'] if not c['passed']], ['F51'])

    def test_missing_duplicate_swapped_or_changed_scalar_rejected(self):
        for mutation in ('missing', 'duplicate', 'order', 'hash', 'boolean_driver'):
            plan, receipt = mathematical_campaign()
            if mutation == 'missing': receipt['scalars'].pop()
            if mutation == 'duplicate': receipt['scalars'][-1] = receipt['scalars'][0]
            if mutation == 'order': receipt['scalars'][0:2] = receipt['scalars'][1::-1]
            if mutation == 'hash': receipt['scalars'][0]['sha256'] = 'other'
            if mutation == 'boolean_driver': receipt['scalars'][0]['drivers'] = {'C8': False, 'C14': 0, 'C18': 1}
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                native.compare_results(plan, receipt)

    def test_persistence_and_proof_types_are_strict(self):
        mutations = [('save_reopen_verified', 'true'), ('source_preserved', 1), ('iteration_enabled', 0),
                     ('calculation_state', False), ('scalar_copies_saved', 'false'),
                     ('technical_writes_to_base', ['C8']), ('macros_enabled', True)]
        for key, bad in mutations:
            plan, receipt = mathematical_campaign(); receipt[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError): native.compare_results(plan, receipt)
        plan, receipt = mathematical_campaign(); receipt['persisted_base_outputs']['D24'] += 1
        with self.assertRaises(ValueError): native.compare_results(plan, receipt)

    def test_degenerate_tables_and_each_degenerate_matrix_axis_fail(self):
        for axis in ('both', 'volume', 'aid'):
            plan, receipt = mathematical_campaign()
            for spec, observation in zip(plan['scenarios'], receipt['scalars']):
                if spec['table'] != 'volume_aides': continue
                volume, aid = spec['drivers']['C8'], spec['drivers']['C14']
                value = -200 + (volume*200 if axis == 'aid' else 0) + (aid*500 if axis == 'volume' else 0)
                observation['outputs']['C49'] = value
                for target in spec['targets']:
                    receipt['tables'][target] = receipt['persisted_tables'][target] = value
            with self.subTest(axis=axis): self.assertFalse(native.compare_results(plan, receipt)['passed'])


class InstrumentPatchTests(unittest.TestCase):
    XML = (b'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
           b'<c r="C8" s="605"><v>0</v></c><c r="C14" s="605"><v>0</v></c>'
           b'<c r="C18" s="2481"><v>0</v></c><c r="D8"><f>IF($C$18=1,$F8,0)</f><v>9</v></c>'
           b'</sheetData><sheetProtection sheet="1"/></worksheet>')

    def test_only_the_three_literals_change_and_original_bytes_restore(self):
        values = {'C8': -.1, 'C14': -1, 'C18': 0}
        patched = native._patch_literals(self.XML, values)
        self.assertNotEqual(self.XML, patched)
        self.assertEqual(native._patch_literals(patched, dict.fromkeys(native.DRIVERS, 0)), self.XML)
        self.assertIn(b'<f>IF($C$18=1,$F8,0)</f><v>9</v>', patched)
        self.assertIn(b'<sheetProtection sheet="1"/>', patched)

    def test_free_writes_formulas_and_ambiguous_cells_are_refused(self):
        for values in ({'C8': 1}, {'C8': 0, 'C14': 0, 'C18': False},
                       {'C8': 0, 'C14': 0, 'C18': 0, 'D8': 3}):
            with self.assertRaises(ValueError): native._patch_literals(self.XML, values)
        for xml in (self.XML.replace(b'<v>0</v>', b'<f>1</f><v>0</v>', 1),
                    self.XML.replace(b'<c r="C8"', b'<c r="C9"'),
                    self.XML + b'<c r="C8"><v>0</v></c>'):
            with self.assertRaises(ValueError): native._patch_literals(xml, dict.fromkeys(native.DRIVERS, 0))


class InterruptedProtocolTests(unittest.TestCase):
    def test_preexisting_excel_and_partial_campaign_never_adopt_or_change_source(self):
        for existing in ({71}, set()):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); source = root/'source.xlsm'; source.write_bytes(b'fictional-source')
                prepared = root/'instruments'; prepared.mkdir()
                (prepared/'plan.json').write_text('{}', encoding='utf-8')
                plan = {'source_sha256': digest(source), 'model_id': 'fixture', 'template_sha256': 'fixture',
                        'scenarios': native.scenarios()}
                worker = type('Worker', (), {})()
                worker.stdout = iter(json.dumps(x)+'\n' for x in [
                    {'event': 'owned_process', 'pid': 71},
                    {'event': 'progress', 'stage': 'scalar_complete', 'completed': 2},
                    {'event': 'error', 'error': 'Interruption simulée après deux scénarios'}])
                class CapturedInput(io.StringIO):
                    def close(self):
                        self.saved=self.getvalue()
                        super().close()
                    def getvalue(self):
                        return self.saved if self.closed else super().getvalue()
                worker.stderr = iter(()); worker.stdin = CapturedInput(); worker.returncode = None
                worker.poll = lambda: worker.returncode
                worker.kill = lambda: setattr(worker, 'returncode', 2)
                worker.wait = lambda timeout: 2
                owned = type('Owned', (), {'terminate': lambda self: setattr(self, 'terminated', True),
                                           'close': lambda self: setattr(self, 'closed', True)})()
                with patch.object(native, 'available', return_value=True), \
                     patch.object(native, '_verify_plan', return_value=plan), \
                     patch.object(native, 'existing_excel_pids', return_value=existing), \
                     patch.object(native.subprocess, 'Popen', return_value=worker), \
                     patch.object(native, 'OwnedExcelProcess', return_value=owned) as factory:
                    with self.assertRaises(ValueError):
                        native.verify_native(object(), source, root/'result.xlsm', root/'result.json', prepared=prepared)
                self.assertEqual(source.read_bytes(), b'fictional-source')
                self.assertFalse((root/'result.xlsm').exists())
                failure = json.loads((root/'result.echec.json').read_text(encoding='utf-8'))
                self.assertFalse(failure['adopted']); self.assertTrue(failure['source_preserved'])
                if existing:
                    factory.assert_not_called(); self.assertEqual(worker.stdin.getvalue(), '')
                else:
                    self.assertTrue(owned.terminated); self.assertTrue(owned.closed)
                    self.assertIn('ownership_confirmed', worker.stdin.getvalue())


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.output = self.folder/'base.xlsm'; self.output.write_bytes(b'fictional native base')
        self.plan, self.base = mathematical_campaign()
        self.plan['source_sha256'] = 'source_fixture'
        self.base.update(source_sha256='source_fixture', output_sha256=digest(self.output), version='fixture')
        self.scalars = self.base.pop('scalars')
        self.binding = {'source_sha256': 'source_fixture', 'plan_sha256': 'plan_fixture', 'implementation_sha256': 'code_fixture'}
        self.ledger = {'schema': 'tca-sensitivity-checkpoints/1', 'binding': self.binding, 'records': []}

    def record(self, identifier, data):
        native._record_checkpoint(self.folder, self.ledger, self.binding, self.plan, self.output, identifier, data)

    def load(self, binding=None):
        return native._load_checkpoints(self.folder, binding or self.binding, self.plan, self.output)

    def test_resume_two_completed_scalars_but_never_qualify_partial_campaign(self):
        self.record('base', self.base)
        for observation in self.scalars[:2]: self.record(observation['id'], observation)
        resumed, ledger = self.load()
        self.assertEqual(len(resumed['scalars']), 2)
        self.assertEqual(len(ledger['records']), 3)
        with self.assertRaises(ValueError):
            native.compare_results(self.plan, {**resumed['base'], 'scalars': resumed['scalars']})

    def test_mismatch_in_code_source_or_plan_blocks_resume(self):
        self.record('base', self.base)
        for key in self.binding:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.load({**self.binding, key: 'changed'})

    def test_changed_base_or_checkpoint_blocks_resume(self):
        self.record('base', self.base)
        self.output.write_bytes(b'changed base')
        with self.assertRaises(ValueError): self.load()
        self.output.write_bytes(b'fictional native base')
        (self.folder/'base.json').write_text('{}', encoding='utf-8')
        with self.assertRaises(ValueError): self.load()

    def test_skips_duplicates_and_invalid_values_are_not_checkpointed(self):
        self.record('base', self.base)
        with self.assertRaises(ValueError): self.record(self.scalars[1]['id'], self.scalars[1])
        bad = copy.deepcopy(self.scalars[0]); bad['outputs']['D24'] = math.nan
        with self.assertRaises(ValueError): self.record(bad['id'], bad)
        self.assertEqual(len(self.ledger['records']), 1)
        self.record(self.scalars[0]['id'], self.scalars[0])
        with self.assertRaises(ValueError): self.record(self.scalars[0]['id'], self.scalars[0])

    def test_native_budget_is_bounded_at_one_hour(self):
        self.assertEqual(native.MAX_NATIVE_SECONDS, 3600)
        for bad in (3601, 0, False, math.inf):
            with self.subTest(timeout=bad), self.assertRaises(ValueError):
                native.verify_native(None, 'source', 'output', 'receipt', timeout=bad)


class SensitivityEconomicFixtureTests(unittest.TestCase):
    def test_monthly_ledger_proves_both_matrix_axes_and_non_degenerate_base(self):
        from tools.financial_cases_sensitivity import cash_schedule,cash_minimum,cases
        rows=cash_schedule()
        self.assertEqual(rows[0]['customer_receipts'],0)
        self.assertEqual(rows[0]['purchases_paid'],8000)
        self.assertEqual(rows[0]['inventory'],4000)
        self.assertEqual(cash_minimum(),-48000)
        self.assertEqual(rows[-1]['closing_cash'],305400)
        self.assertEqual(cash_minimum(-.2,0),-46400)
        self.assertEqual(cash_minimum(-.2,-1),-106400)
        for volume in (0,-.1,-.2):
            for aid in (0,-.5,-1):
                self.assertEqual(cash_minimum(volume,aid),-48000-8000*volume+60000*aid)
        self.assertEqual(len(cases()[0]['oracles']),14)


if __name__ == '__main__': unittest.main()
