"""Graphe directionnel et ancrages métier ; aucune exécution financière native."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tca_bp.agents import Coordinator
from tca_bp.knowledge import contracts, graph_dependencies, load_model_graph, sheet_reasoning, chart_sources
from tca_bp.vendor.input_engine import Workbook
try:
    from .test_agents import FakeEngine
except ImportError:
    from test_agents import FakeEngine


class GraphCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.engine = FakeEngine()
        # Un graphe volontairement différent des contrats métier statiques.
        self.engine.dependency_graph['sheets'] = {
            'Revenue': ['DATA Contrats'], 'Bilan': ['Revenue'],
            'Comparables': ['Bilan'], 'COGS': ['DATA COGS'],
        }
        self.coordinator = Coordinator(self.engine)

    def test_downstream_direction_uses_extracted_graph_not_business_contracts(self):
        self.assertEqual(set(self.coordinator._impacted(['Revenue'])), {'Revenue', 'Bilan', 'Comparables'})
        self.assertNotIn('DATA Contrats', self.coordinator._impacted(['Revenue']))
        self.assertNotIn('Modèle financier', self.coordinator._impacted(['Revenue']))
        self.assertNotIn('COGS', self.coordinator._impacted(['Revenue']))

    def test_cycle_and_multiple_sources_terminate_without_duplicates(self):
        self.engine.dependency_graph['sheets']['DATA Contrats'] = ['Comparables']
        result = self.coordinator._impacted(['Revenue', 'DATA COGS'])
        self.assertEqual(len(result), len(set(result)))
        self.assertEqual(set(result), {'Revenue', 'Bilan', 'Comparables', 'DATA Contrats', 'DATA COGS', 'COGS'})

    def test_agents_expose_actual_incoming_outgoing_and_keep_business_role(self):
        spec = next(a for a in self.coordinator.agents() if a['sheet'] == 'Revenue')
        self.assertEqual(spec['dependencies'], ['DATA Contrats'])
        self.assertEqual(spec['dependents'], ['Bilan'])
        self.assertEqual(spec['dependency_basis'], 'GRAPHE_EXTRAIT_MODELE')
        self.assertTrue(spec['graph_sha256'])
        self.assertIn('business_dependencies', spec)

    def test_absent_graph_does_not_invent_downstream_or_claim_full_routing(self):
        del self.engine.dependency_graph
        result = self.coordinator.route('Ajouter un recrutement avec salaire')
        self.assertEqual(result['status'], 'NEEDS_REVIEW')
        self.assertEqual(result['affected_sheets'], result['sheets'])
        self.assertEqual(result['dependency_basis'], 'GRAPHE_INDISPONIBLE')

    def test_wrong_model_and_unknown_dependency_are_refused(self):
        self.engine.dependency_graph['model_id'] = 'other-model'
        with self.assertRaisesRegex(ValueError, 'version'):
            self.coordinator._impacted(['Revenue'])
        self.engine.dependency_graph['model_id'] = self.engine.model_id
        self.engine.dependency_graph['sheets']['Revenue'] = ['Private other workbook']
        with self.assertRaisesRegex(ValueError, 'hors modèle'):
            self.coordinator._impacted(['Revenue'])

    def test_changed_graph_file_refreshes_cached_edges(self):
        with tempfile.TemporaryDirectory() as directory:
            self.engine.model_dir = Path(directory)
            path = self.engine.model_dir / 'graphe_dependances.json'
            path.write_text(json.dumps(self.engine.dependency_graph), encoding='utf-8')
            del self.engine.dependency_graph
            self.assertIn('Comparables', self.coordinator._impacted(['Revenue']))
            path.write_text(json.dumps({'model_id': self.engine.model_id, 'sheets': {'COGS': ['Revenue']}, 'cells': []}), encoding='utf-8')
            self.assertEqual(set(self.coordinator._impacted(['Revenue'])), {'Revenue', 'COGS'})

    def test_explanation_reads_financial_anchors_and_checks_graph_formula_identity(self):
        formula = 'SUM(A1:A3)'
        self.engine.data['D7'] = {'value': 999, 'formula': formula}
        self.engine.dependency_graph['cells'] = [{'sheet': 'Compte de Résultat', 'cell': 'D7',
            'formula_sha256': hashlib.sha256(formula.encode()).hexdigest(), 'references': ['A1:A3'], 'defined_names': []}]
        result = self.coordinator.explain('Compte de Résultat')
        self.assertEqual([p['cell'] for p in result['key_calculations']], ['D7', 'D69', 'D72', 'D85'])
        point = result['key_calculations'][0]
        self.assertEqual(point['formula'], formula)
        self.assertEqual(point['references'], ['A1:A3'])
        self.assertEqual(point['dependency_status'], 'FORMULE_CONFORME_AU_GRAPHE')
        self.assertFalse(result['result_claims_allowed'])
        self.assertEqual(result['test_cases'][0]['status'], 'SPECIFICATION_NON_EXECUTEE')
        self.engine.data['D7']['formula'] = 'A9'
        point = self.coordinator.explain('Compte de Résultat')['key_calculations'][0]
        self.assertEqual(point['references'], [])
        self.assertEqual(point['dependency_status'], 'DEPENDANCES_NON_VERIFIEES')

    def test_every_responsibility_has_specific_reasoning_and_unexecuted_oracle(self):
        specs = contracts()
        self.assertEqual(len(specs), 33)
        self.assertEqual(len({s['test_cases'][0]['id'] for s in specs}), 33)
        for spec in specs:
            with self.subTest(sheet=spec['sheet']):
                self.assertTrue(spec['key_calculations'])
                self.assertTrue(all(p['unit'] and p['reasoning'] for p in spec['key_calculations']))
                self.assertEqual(spec['test_cases'][0]['status'], 'SPECIFICATION_NON_EXECUTEE')
                self.assertTrue(spec['test_cases'][0]['given'])
                self.assertTrue(spec['test_cases'][0]['expected'])


class ModelKnowledgeAnchorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.path = cls.root / 'models/generic-v1/TCA_BP_Trame_generique.xlsm'
        if not cls.path.is_file():
            raise unittest.SkipTest('Trame locale absente ; aucun ancrage natif prétendu vérifié.')
        cls.wb = Workbook(cls.path)
        cls.graph = json.loads((cls.path.parent / 'graphe_dependances.json').read_text(encoding='utf-8'))
        wanted = {(s['sheet'], p['cell']) for s in contracts() for p in s['key_calculations']}
        cls.nodes = {(n['sheet'], n['cell']): n for n in cls.graph.pop('cells') if (n['sheet'], n['cell']) in wanted}

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wb'):
            cls.wb.close()

    def test_all_business_anchors_exist_and_formulas_match_current_graph(self):
        for spec in contracts():
            sheet = spec['sheet']
            cells = self.wb.sheet(sheet)[1]
            for point in spec['key_calculations']:
                address = point['cell']
                with self.subTest(sheet=sheet, cell=address):
                    self.assertIn(address, cells)
                    formula = self.wb.formula(sheet, address)
                    if formula is not None:
                        self.assertIn((sheet, address), self.nodes)
                        self.assertEqual(self.nodes[(sheet, address)]['formula_sha256'], hashlib.sha256(formula.encode('utf-8')).hexdigest())
            self.wb._sheet_cache.pop(sheet, None)

    def test_graphics_are_read_from_attached_xml_series_not_guessed(self):
        charts = chart_sources(self.wb, 'Sensi Graphiques')
        self.assertEqual(len(charts), 4)
        sources = {ref for chart in charts for ref in chart['references']}
        self.assertIn("'Sensi Analyses'!$C$40:$C$45", sources)
        self.assertIn("'Sensi Analyses'!$K$25:$K$33", sources)
        self.assertEqual(chart_sources(self.wb, 'Previsionnel'), [])


if __name__ == '__main__':
    unittest.main()
