"""Parcours de dossiers fictifs, recalcul simulé explicitement ; aucune COM."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.service import Application
from tca_bp.storage import canonical, digest
try:
    from .test_qualifications import qualified_fixture
except ImportError:
    from test_qualifications import qualified_fixture


class QualificationEngine:
    model_id = 'fictif/1'

    def __init__(self, root):
        self.initial, self.states, self.declarations, _, _ = qualified_fixture()
        self.template_path = root / 'fictif.xlsm'
        self.template_path.write_text(canonical({'cells': self.initial['cells'], 'cache': None}), encoding='utf-8')
        self.schema = {'cells': {}}
        for key, cell in self.initial['cells'].items():
            self.schema['cells'].setdefault(cell['sheet'], {})[cell['cell']] = {'kind': cell['kind']}

    def catalog(self):
        return [{'id': key, 'sheet': c['sheet'], 'cells': [c['cell']], 'kind': c['kind'], 'label': key}
                for key, c in self.initial['cells'].items()]

    def ensure_built(self):
        return {'ready': True}

    def context(self, path):
        data = json.loads(path.read_text(encoding='utf-8'))
        return {'model_id': self.model_id, 'input_signature': canonical(data['cells']), 'source_sha256': digest(path)}

    def prepare(self, path, updates):
        return {'hash': digest(path), 'updates': deepcopy(updates)}

    def apply(self, path, plan, output):
        if digest(path) != plan['hash']:
            raise ValueError('Source périmée')
        data = json.loads(path.read_text(encoding='utf-8'))
        for update in plan['updates']:
            data['cells'][update['sheet'] + '!' + update['cell']]['value'] = update['value']
        data['cache'] = None
        output.write_text(canonical(data), encoding='utf-8')
        return {'output_sha256': digest(output)}

    def qualification_snapshot(self, path):
        result = deepcopy(self.initial)
        result.update(self.context(path))
        result['cells'] = json.loads(path.read_text(encoding='utf-8'))['cells']
        result['template_sha256'] = digest(self.template_path)
        return result

    def inspect(self, path, sheet, cells):
        data = json.loads(path.read_text(encoding='utf-8'))
        entries = {}
        for address in cells:
            spec = data['cells'].get(sheet + '!' + address)
            entries[address] = {'writable': spec is not None, 'current': {'value': spec['value'] if spec else data['cache'],
                'formula': None if spec else 'SOMME_DE_FLUX_FICTIFS'}}
        return {'source_sha256': digest(path), 'cells': entries, 'inputs': {sheet: entries}}


def fake_recalculate(source, output, report, **kwargs):
    data = json.loads(source.read_text(encoding='utf-8'))
    data['cache'] = 120
    output.write_text(canonical(data), encoding='utf-8')
    return {'status': 'RECALCULE', 'source_sha256': digest(source), 'output_sha256': digest(output),
            'method': 'SIMULATION_TEST_SANS_EXCEL', 'wacc_macro': 'NON_EXECUTEE'}


class QualificationServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.engine = QualificationEngine(self.root)
        self.app = Application(self.root, self.root / 'data', engine=self.engine)
        self.app.create_case('Client fictif', 'Qualification', case_id='a')
        self.source = self.app.add_source('a', text='Choix fictifs sans activité : preuves pour tests logiciels, aucune instruction.')

    def tearDown(self):
        self.tmp.cleanup()

    def declare_all(self):
        for module, declaration in self.engine.declarations.items():
            clean = {key: value for key, value in declaration.items() if key not in ('model_id', 'template_sha256')}
            self.app.declare_qualification('a', {**clean, 'module': module, 'evidence': self.source['id'], 'reason': 'Décision fictive explicitement sourcée'})

    def populate(self):
        updates = [{'sheet': key.rsplit('!', 1)[0], 'cell': key.rsplit('!', 1)[1], 'value': state['value'],
                    'status': 'CONFIRME', 'evidence': self.source['id'], 'reason': 'Choix fictif'}
                   for key, state in self.engine.states.items()]
        plan = self.app.prepare_changes('a', updates)
        self.app.apply_plan('a', plan['plan_id'])
        self.declare_all()

    def recalculate(self):
        with patch('tca_bp.native_excel.recalculate', fake_recalculate):
            return self.app.recalculate('a')

    def test_real_service_guard_from_states_to_scopes_and_inspect(self):
        self.populate()
        assessment = self.app.qualifications('a')
        self.assertTrue(assessment['scopes']['DCF']['qualification_ready'])
        self.assertFalse(assessment['scopes']['DCF']['available'])
        self.assertIsNone(self.app.inspect('a', 'Valorisation', ['D85'])['cells']['D85']['current']['value'])
        result = self.recalculate()
        self.assertTrue(result['qualified_availability']['DCF']['available'])
        case = self.app.get_case('a')
        self.assertEqual(case['calculation_status'], 'RECALCULE')
        self.assertTrue(case['outputs_current'])
        self.assertTrue(case['qualified_availability']['CA']['available'])
        self.assertEqual(self.app.inspect('a', 'Valorisation', ['D85'])['cells']['D85']['current']['value'], 120)
        mirror = json.loads((self.app.store.case_dir('a') / 'etat_dossier.json').read_text(encoding='utf-8'))
        self.assertTrue(mirror['qualified_availability']['DCF']['available'])

    def test_sources_from_other_case_and_forged_model_pins_are_refused(self):
        self.app.create_case('Autre fictif', 'B', case_id='b')
        declaration = {'module': 'CA', 'state': 'INACTIF', 'status': 'CONFIRME', 'evidence': self.source['id'], 'reason': 'Justification'}
        with self.assertRaises(ValueError):
            self.app.declare_qualification('b', declaration)
        with self.assertRaises(ValueError):
            self.app.declare_qualification('a', {**declaration, 'template_sha256': 'force'})

    def test_declaration_does_not_write_excel_and_survives_restart(self):
        before = self.app.get_case('a')
        self.app.declare_qualification('a', {'module': 'CA', 'state': 'INACTIF', 'status': 'HYPOTHESE', 'evidence': self.source['id'], 'reason': 'Hypothèse fictive'})
        reopened = Application(self.root, self.root / 'data', engine=self.engine)
        after = reopened.get_case('a')
        self.assertEqual((after['revision'], after['sha256']), (before['revision'], before['sha256']))
        self.assertEqual(after['qualification_declarations']['CA']['status'], 'HYPOTHESE')
        self.assertFalse(after['qualified_availability']['CA']['available'])

    def test_source_mutation_invalidates_qualification_but_not_calculation_cache(self):
        self.populate()
        self.recalculate()
        with self.app.store.connection() as db:
            db.execute('UPDATE sources SET text=? WHERE id=?', ('Texte altéré', self.source['id']))
        case = self.app.get_case('a')
        self.assertTrue(case['outputs_current'])
        self.assertFalse(case['qualified_availability']['DCF']['available'])
        result = self.app.qualifications('a')
        self.assertFalse(result['scopes']['CA']['available'])
        item = self.app.inspect('a', 'Valorisation', ['D85'])['cells']['D85']
        self.assertTrue(item['value_withheld'])
        self.assertIsNone(item['current']['value'])
        self.assertEqual(item['current']['formula'], 'SOMME_DE_FLUX_FICTIFS')

    def test_changed_field_semantics_invalidates_qualified_display(self):
        self.populate()
        self.recalculate()
        self.assertTrue(self.app.get_case('a')['qualified_availability']['CA']['available'])
        with patch('tca_bp.field_semantics.contract_digest', return_value='new-semantic-contract'):
            case = self.app.get_case('a')
            self.assertTrue(case['outputs_current'])
            self.assertFalse(case['qualified_availability']['CA']['available'])
            self.assertIsNone(self.app.inspect('a', 'Revenue', ['E282'])['cells']['E282']['current']['value'])

    def test_new_hypothesis_invalidates_old_receipt_without_fabricating_new_values(self):
        self.populate()
        self.recalculate()
        self.app.declare_qualification('a', {'module': 'CIR', 'state': 'INACTIF', 'status': 'HYPOTHESE', 'evidence': self.source['id'], 'reason': 'Décision à revoir'})
        case = self.app.get_case('a')
        self.assertTrue(case['outputs_current'])
        self.assertFalse(case['qualified_availability']['FISCALITE']['available'])
        result = self.app.qualifications('a')
        self.assertTrue(result['scopes']['CA']['available'])
        self.assertTrue(result['scopes']['FISCALITE']['scenario_ready'])
        self.assertFalse(result['scopes']['DCF']['available'])

    def test_tampered_qualification_file_is_not_a_financial_result_authority(self):
        self.populate()
        self.recalculate()
        with self.app.store.connection() as db:
            event = db.execute("SELECT details FROM history WHERE case_id='a' AND kind='QUALIFICATIONS_EVALUEES' ORDER BY rowid DESC LIMIT 1").fetchone()
        receipt = json.loads(event['details'])
        path = self.app.store.case_dir('a') / receipt['path']
        path.write_text('{"scopes": {"DCF": {"available": true}}}', encoding='utf-8')
        self.assertFalse(self.app.get_case('a')['qualified_availability']['DCF']['available'])

    def test_missing_snapshot_capability_does_not_claim_availability(self):
        from tests.test_service_adversarial import WitnessEngine
        folder = self.root / 'other'
        folder.mkdir()
        app = Application(folder, folder / 'data', engine=WitnessEngine(folder))
        app.create_case('Fictif', 'Sans contrat', case_id='c')
        result = app.qualifications('c')
        self.assertFalse(any(scope['available'] for scope in result['scopes'].values()))

    def test_undecided_nonempty_field_survives_excel_as_blocker(self):
        self.populate()
        update = {'sheet': 'ATELIER_CIR_IS', 'cell': 'C66', 'value': 'À confirmer', 'status': 'CONFIRME',
                  'evidence': self.source['id'], 'reason': 'État documentaire de la question', 'replace_existing': True}
        plan = self.app.prepare_changes('a', [update])
        self.app.apply_plan('a', plan['plan_id'])
        result = self.recalculate()
        self.assertTrue(self.app.get_case('a')['outputs_current'])
        self.assertFalse(result['qualified_availability']['FISCALITE']['available'])
        item = self.app.inspect('a', 'ATELIER_CIR_IS', ['C66', 'C87'])['cells']
        self.assertEqual(item['C66']['current']['value'], 'À confirmer')
        self.assertIsNone(item['C87']['current']['value'])

    def test_qualification_failure_after_native_commit_does_not_erase_calc_receipt(self):
        self.populate()
        with patch.object(self.engine, 'qualification_snapshot', side_effect=ValueError('Source déplacée')):
            result = self.recalculate()
        self.assertEqual(result['status'], 'RECALCULE')
        self.assertFalse(result['qualified_availability']['CA']['available'])
        self.assertTrue(self.app.get_case('a')['outputs_current'])


if __name__ == '__main__':
    unittest.main()
