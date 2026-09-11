"""Impact d'une règle : propagation, noms, tables, objets et zones protégées."""
from copy import deepcopy
import json
import shutil
import tempfile
from pathlib import Path
import unittest
import zipfile

from tca_bp.maintenance import Maintenance
from tca_bp.maintenance_impact import impact_report
from tca_bp.model_engine import ModelEngine
from tca_bp.model_registry import ModelRegistry
from tca_bp.storage import canonical, digest
from tests.test_maintenance import FixtureEngine, make_fixture
from tests.test_model_versions import fixture as sealed_fixture


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_fixture(self.root / 'base')
        self.engine = FixtureEngine(self.root)
        self.engine.schema = {'cells': {'Inputs': {'A1': {}}}, 'fields': [
            {'id': 'offer_code', 'sheet': 'Inputs', 'ranges': ['A1']}]}
        self.graph = {'model_id': 'fixture/1', 'sheets': {'Inputs': []},
            'cells': [{'sheet': 'Inputs', 'cell': 'B2', 'references': ["'Inputs'!B1"], 'defined_names': []}],
            'defined_names': [{'name': 'Result', 'text': 'Inputs!$B$1'}],
            'native_tables': [{'id': 'example', 'sheet': 'Inputs', 'range': 'C3:D5', 'inputs': ['A1']}],
            'macro': {'outputs': {'Inputs': ['D10']}}}
        self.save_graph()
        self.change = {'sheet': 'Inputs', 'cell': 'B1', 'old_formula': 'A1*2', 'new_formula': 'A1+A2'}

    def tearDown(self):
        self.temp.cleanup()

    def save_graph(self):
        (self.engine.model_dir / 'graphe_dependances.json').write_text(json.dumps(self.graph), encoding='utf8')

    def test_reports_direct_chain_names_native_and_constant_without_values(self):
        report = impact_report(self.engine, [self.change])
        self.assertEqual(report['direct_formula_dependants'], [{'sheet': 'Inputs', 'cell': 'B2', 'depends_on': ['Inputs!B1']}])
        self.assertEqual(report['defined_names'][0]['direct_targets'], ['Inputs!B1'])
        self.assertEqual(report['protected_constants_referenced'], [
            {'reference': "'Inputs'!A2", 'protected_constant_count': 1, 'sample_cells': ['A2'], 'sample_truncated': False}])
        self.assertEqual(report['native_tables'][0]['id'], 'example')
        self.assertTrue(report['wacc']['native_validation_required'])
        self.assertFalse(report['coverage_complete'])

    def test_detects_dynamic_formula_validation_and_drawing(self):
        path = self.engine.template_path
        with zipfile.ZipFile(path) as archive:
            parts = [(deepcopy(i), archive.read(i.filename)) for i in archive.infolist()]
        with zipfile.ZipFile(path, 'w') as archive:
            for info, data in parts:
                if info.filename == 'xl/worksheets/sheet1.xml':
                    data = data.replace(b'A1*2', b'INDIRECT("A1")*2').replace(
                        b'</worksheet>', b'<dataValidations><dataValidation type="list" sqref="A1"><formula1>Choices</formula1></dataValidation></dataValidations><drawing/></worksheet>')
                archive.writestr(info, data)
        report = impact_report(self.engine, [self.change])
        self.assertIn({'sheet': 'Inputs', 'cell': 'B1'}, report['dynamic_references_to_review'])
        self.assertEqual(report['validations_to_review'][0]['range'], 'A1')
        self.assertEqual(report['objects_to_review'][0]['type'], 'drawing')

    def test_new_dynamic_functions_are_reported_before_the_workbook_changes(self):
        before = digest(self.engine.template_path)
        for formula, functions in [
                ('INDIRECT("A2")*2', ['INDIRECT']),
                ('offset(A1,1,0)*2', ['OFFSET']),
                ('IF(A1,INDIRECT("A2"),_xlfn.OFFSET(A1,1,0))', ['INDIRECT', 'OFFSET'])]:
            with self.subTest(formula=formula):
                report = impact_report(self.engine, [{**self.change, 'new_formula': formula}])
                self.assertIn({'sheet': 'Inputs', 'cell': 'B1'}, report['dynamic_references_to_review'])
                self.assertEqual(report['proposed_dynamic_references_to_review'], [
                    {'sheet': 'Inputs', 'cell': 'B1', 'functions': functions}])
                self.assertFalse(report['coverage_complete'])
        self.assertEqual(digest(self.engine.template_path), before)

    def test_dynamic_text_and_quoted_sheet_names_are_not_function_calls(self):
        for formula in ('"INDIRECT("&"OFFSET("', '"INDIRECT(""A2"")"', "'OFFSET('!A1+1"):
            with self.subTest(formula=formula):
                report = impact_report(self.engine, [{**self.change, 'new_formula': formula}])
                self.assertEqual(report['dynamic_references_to_review'], [])
                self.assertEqual(report['proposed_dynamic_references_to_review'], [])

    def real_engine(self):
        engine = sealed_fixture(self.root / 'sealed')
        graph = {**self.graph, 'model_id': engine.model_id,
                 'sheets': {'Inputs': [], 'Control': [], 'Assumptions': []},
                 'cells': [{'sheet': 'Inputs', 'cell': 'B1', 'references': ["'Inputs'!A1"]}]}
        (engine.model_dir / 'graphe_dependances.json').write_text(canonical(graph), encoding='utf8')
        return engine

    def test_real_model_binding_identifies_exact_components_without_creating_an_archive(self):
        engine = self.real_engine()
        before = {p.name: digest(p) for p in engine.model_dir.iterdir()}
        report = impact_report(engine, [self.change])
        seal = ModelRegistry(engine.model_dir, engine.project_root).describe(engine)
        self.assertEqual(report['model_ref'], seal['model_ref'])
        self.assertEqual(report['source_template_sha256'], seal['template_sha256'])
        self.assertEqual(report['source_schema_sha256'], seal['schema_sha256'])
        self.assertEqual(report['graph_sha256'], seal['files']['graphe_dependances.json'])
        self.assertEqual(report['source_kind'], 'MODELE')
        self.assertFalse(report['graph_derivation_verified'])
        self.assertEqual({p.name: digest(p) for p in engine.model_dir.iterdir()}, before)

    def test_same_id_and_template_with_another_schema_rejects_old_proposal(self):
        engine = self.real_engine()
        proposal = Maintenance(engine).propose([self.change], 'fixture/next', 'Règle fictive à contrôler indépendamment.')
        variant = self.root / 'schema_variant'
        shutil.copytree(engine.model_dir, variant)
        schema = json.loads((variant / 'modele.json').read_text(encoding='utf8'))
        schema['fields'][0]['label'] = 'Montant fictif revu'
        (variant / 'modele.json').write_text(canonical(schema), encoding='utf8')
        receipt = json.loads((variant / 'build_receipt.json').read_text(encoding='utf8'))
        receipt['schema_sha256'] = digest(variant / 'modele.json')
        (variant / 'build_receipt.json').write_text(canonical(receipt), encoding='utf8')
        revised = ModelEngine(self.root, variant)
        fresh = impact_report(revised, [self.change])
        prior = proposal['component_impact']
        self.assertEqual(fresh['model_id'], prior['model_id'])
        self.assertEqual(fresh['source_template_sha256'], prior['source_template_sha256'])
        self.assertNotEqual(fresh['source_schema_sha256'], prior['source_schema_sha256'])
        self.assertNotEqual(fresh['model_ref'], prior['model_ref'])
        with self.assertRaisesRegex(ValueError, 'composants ou le graphe ont changé'):
            Maintenance(revised).build(proposal)
        self.assertFalse((self.root / 'models' / 'versions').exists())

    def test_graph_change_alters_binding_without_changing_template_or_schema(self):
        engine = self.real_engine()
        before = impact_report(engine, [self.change])
        path = engine.model_dir / 'graphe_dependances.json'
        graph = json.loads(path.read_text(encoding='utf8'))
        graph['defined_names'].append({'name': 'NewReference', 'text': 'Inputs!$A$1'})
        path.write_text(canonical(graph), encoding='utf8')
        after = impact_report(engine, [self.change])
        for key in ('model_id', 'source_template_sha256', 'source_schema_sha256'):
            self.assertEqual(before[key], after[key])
        self.assertNotEqual(before['graph_sha256'], after['graph_sha256'])
        self.assertNotEqual(before['model_ref'], after['model_ref'])
        self.assertFalse(after['graph_derivation_verified'])

    def test_missing_or_wrong_graph_is_never_presented_as_complete(self):
        self.graph['model_id'] = 'other/1'
        self.save_graph()
        with self.assertRaisesRegex(ValueError, 'autre version'):
            impact_report(self.engine, [self.change])
        (self.engine.model_dir / 'graphe_dependances.json').unlink()
        self.assertEqual(impact_report(self.engine, [self.change])['status'], 'GRAPHE_ABSENT')

    def test_changed_graph_blocks_an_existing_proposal(self):
        maintenance = Maintenance(self.engine)
        proposal = maintenance.propose([self.change], 'fixture/2', 'Changer la règle selon la recette indépendante.')
        self.graph['defined_names'].append({'name': 'Other', 'text': 'Inputs!$A$2'})
        self.save_graph()
        with self.assertRaisesRegex(ValueError, 'graphe ont changé'):
            maintenance.build(proposal)


if __name__ == '__main__':
    unittest.main()
