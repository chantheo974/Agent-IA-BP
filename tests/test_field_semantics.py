"""Sémantique explicite des champs, refus ciblés et vrais lots OOXML sans COM."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tca_bp.agents import _unit, Coordinator
from tca_bp.field_semantics import enrich_catalog, summary, validate_updates
from tca_bp.field_semantics_data import DEFINITIONS
from tca_bp._field_semantics_basis import BASIS
from tca_bp.model_engine import ModelEngine
from tca_bp.qualifications import evaluate
from tca_bp.storage import digest
from tca_bp.vendor.input_engine import Workbook
from tests.test_qualifications import qualified_fixture

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'models/generic-v1-release-1.1.2'
EXPECTED = 'e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12'


class AlteredReader:
    def __init__(self, workbook, formulas=None):
        self.workbook, self.formulas = workbook, formulas or {}

    def formula(self,sheet,cell):
        return self.formulas.get((sheet,cell), self.workbook.formula(sheet,cell))

    def value(self,sheet,cell):
        return self.workbook.value(sheet,cell)


class SemanticDefinitionsWithoutModelTests(unittest.TestCase):
    def test_all_definitions_and_owner_ids_are_explicit_even_without_model(self):
        self.assertEqual(len(DEFINITIONS),297)
        self.assertEqual(set(DEFINITIONS),set(BASIS['fields']))
        for spec in DEFINITIONS.values():
            self.assertTrue(spec['unit'] and spec['basis'] and spec['calendar'])
            self.assertTrue(set(spec['dependencies']) <= set(DEFINITIONS))
            self.assertTrue(set(spec['anchors']) <= set(BASIS['witnesses']))

    def test_missing_semantics_is_never_inferred_from_a_financial_label(self):
        self.assertIn('NON_ETABLIE',_unit({'label':'Taux % en euros annuel','kind':'number'}))

    def test_financial_scope_guard_is_not_global(self):
        snapshot,states,modules,calc,_ = qualified_fixture()
        snapshot['cells']['Valorisation!D9']['semantic_status']='REEXAMEN_REQUIS'
        result=evaluate(snapshot,states,{'source'},module_declarations=modules,calculation=calc)
        self.assertFalse(result['scopes']['DCF']['available'])
        self.assertTrue(result['scopes']['CA']['available'])


class FieldSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not MODEL.is_dir():
            raise unittest.SkipTest('Référence explicite 1.1.2 absente ; aucun choix automatique de version.')
        cls.engine = ModelEngine(ROOT,MODEL)
        cls.raw = deepcopy(cls.engine.schema)
        cls.workbook = Workbook(cls.engine.template_path)
        if cls.workbook.hash != EXPECTED:
            raise AssertionError('Cette recette exige le sceau exact 1.1.2.')
        cls.catalog = enrich_catalog(cls.raw,workbook=cls.workbook)
        cls.by_id = {f['id']:f for f in cls.catalog}

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'workbook'):
            cls.workbook.close()

    def test_exact_297_definitions_no_schema_mutation_or_heuristic(self):
        self.assertEqual(len(self.catalog),297)
        self.assertEqual(set(DEFINITIONS),set(self.by_id))
        self.assertEqual(self.engine.schema,self.raw)
        self.assertTrue(summary(self.catalog)['all_established'])
        for field in self.catalog:
            semantic = field['semantics']
            self.assertTrue(field['unit'] and field['basis'])
            self.assertTrue(semantic['evidence']['field_contract_matches'])
            self.assertTrue(semantic['policy']['source_required'])
            self.assertIsNotNone(semantic['dependencies'])
        self.assertIn('NON_ETABLIE',_unit({'kind':'number','label':'Prix euros % année'}))

    def test_financial_unit_distinctions_from_independent_model_reading(self):
        # Ces attentes distinguent les assiettes, pas uniquement une copie du texte de la fonction.
        self.assertIn('fraction',self.by_id['cogs_logistics']['unit'])
        self.assertIn('fraction',self.by_id['manual_shock_client_delay']['unit'])
        self.assertIn('mois',self.by_id['analysis_financing_delay']['unit'])
        self.assertIn('millions',self.by_id['comparables_e47_e61']['unit'])
        self.assertIn('même unité monétaire',self.by_id['comparables_e117_e136']['unit'])
        self.assertIn('30',self.by_id['stock_coverage']['basis'])
        self.assertNotIn('conventional_month_days',[x['field_id'] for x in self.by_id['stock_coverage']['semantics']['dependencies']['business_owners']])
        self.assertIn('AUCUNE_CONTRAINTE',self.by_id['offer_capacity_2026']['semantics']['policy']['zero'])
        self.assertIn('année civile',self.by_id['valorisation_d16']['unit'])

    def test_all_809_defaults_have_exact_formula_and_sources(self):
        defaults = [x for f in self.catalog for x in f['semantics']['dependencies']['calculated_defaults'].values()]
        self.assertEqual(len(defaults),809)
        self.assertTrue(all(isinstance(x['references'],list) and x['formula'] for x in defaults))
        price = self.by_id['offer_price_2027_2030']['semantics']['dependencies']['calculated_defaults']['G15']
        self.assertEqual(price['formula'],'F15*(1+$D$5)')
        self.assertEqual(set(price['references']),{"'Assumptions'!F15","'Assumptions'!$D$5"})

    def test_unknown_field_is_visible_and_blocks_only_its_proposal(self):
        schema = deepcopy(self.raw)
        schema['fields'].append({'id':'new_unreviewed','sheet':'Control','kind':'number','cells':['Z99'],'label':'Nouveau montant'})
        schema['cells']['Control']['Z99'] = {'kind':'number'}
        catalog = enrich_catalog(schema,workbook=self.workbook)
        self.assertEqual(catalog[-1]['semantics']['status'],'REEXAMEN_REQUIS')
        with self.assertRaisesRegex(ValueError,'new_unreviewed'):
            validate_updates(catalog,[{'sheet':'Control','cell':'Z99','value':3}])
        validate_updates(catalog,[{'sheet':'Control','cell':'C10','value':'2027-01-01'}])

    def test_changed_owner_formula_invalidates_relevant_dimension_only(self):
        catalog = enrich_catalog(self.raw,workbook=AlteredReader(self.workbook,{('Stock','Q15'):'Q14*$E$10/365'}))
        by_id = {f['id']:f for f in catalog}
        self.assertEqual(by_id['stock_coverage']['semantics']['status'],'REEXAMEN_REQUIS')
        self.assertEqual(by_id['offer_price_2026']['semantics']['status'],'ETABLI_MODELE')
        with self.assertRaisesRegex(ValueError,'stock_coverage'):
            validate_updates(catalog,[{'sheet':'Stock','cell':'E10','value':30}])

    def test_equivalent_calendar_rewrite_outside_dimension_witnesses_is_compatible(self):
        altered = AlteredReader(self.workbook,{('Control','C60'):'SUM(YEAR(C10),C59,-1)'})
        self.assertTrue(summary(enrich_catalog(self.raw,workbook=altered))['all_established'])

    def test_changed_field_range_or_default_requires_explicit_review(self):
        schema = deepcopy(self.raw)
        schema['cells']['Assumptions']['G15']['default_formula'] = 'F15*(1+$D$5)*1000'
        catalog = enrich_catalog(schema,workbook=self.workbook)
        field = next(f for f in catalog if f['id']=='offer_price_2027_2030')
        self.assertIn('CONTRAT_CHAMP_MODIFIE',field['semantics']['blocking_reasons'])

    def test_no_workbook_cannot_approve_formula_witnesses(self):
        field = next(f for f in enrich_catalog(self.raw) if f['id']=='stock_coverage')
        self.assertFalse(field['semantics']['can_propose'])

    def test_mutated_returned_catalogue_never_changes_sealed_schema(self):
        fields = self.engine.catalog()
        fields[0]['semantics']['policy']['formula_input'] = 'ALLOWED'
        fields[0]['constraints']['min'] = -1000
        self.assertEqual(self.engine.schema,self.raw)
        self.assertEqual(self.engine.catalog()[0]['semantics']['policy']['formula_input'],'INTERDITE')

    def test_unknown_semantic_owner_blocks_only_required_financial_scopes(self):
        snapshot,states,modules,calc,_ = qualified_fixture()
        snapshot['cells']['Valorisation!D9']['semantic_status'] = 'REEXAMEN_REQUIS'
        snapshot['cells']['Valorisation!D9']['semantic_issues'] = ['PREUVE_ASSIETTE_MODIFIEE_OU_ABSENTE']
        result = evaluate(snapshot,states,{'source'},module_declarations=modules,calculation=calc)
        self.assertTrue(all(result['scopes'][scope]['available'] for scope in ('CA','COGS','CASH','FISCALITE')))
        self.assertFalse(result['scopes']['DCF']['available'])
        self.assertIn('SEMANTIQUE_NON_ETABLIE',[b['code'] for b in result['scopes']['DCF']['blockers']])

    def test_modified_formula_witness_propagates_through_real_snapshot_hook(self):
        changed = enrich_catalog(self.raw,workbook=AlteredReader(self.workbook,{('Stock','Q15'):'Q14*$E$10/365'}))
        snapshot,states,modules,calc,_ = qualified_fixture()
        modules['STOCK']['state']='ACTIF'
        with patch('tca_bp.qualifications.collect_snapshot',return_value=deepcopy(snapshot)), patch.object(self.engine,'catalog',return_value=changed):
            attached = self.engine.qualification_snapshot(self.engine.template_path)
        self.assertEqual(attached['cells']['Stock!E10']['semantic_status'],'REEXAMEN_REQUIS')
        result=evaluate(attached,states,{'source'},module_declarations=modules,calculation=calc)
        self.assertFalse(result['scopes']['CASH']['available'])
        self.assertTrue(result['scopes']['CA']['available'])
        self.assertIn('SEMANTIQUE_NON_ETABLIE',[b['code'] for b in result['scopes']['CASH']['blockers']])

    def test_plan_with_old_semantic_digest_is_refused_before_any_output(self):
        import tempfile
        updates=[{'sheet':'Control','cell':'C10','value':'2026-01-01','reason':'Date fictive documentée','evidence':'fictif','replace_existing':True}]
        plan=self.engine.prepare(self.engine.template_path,updates)
        self.assertIn('semantics_sha256',plan)
        plan['semantics_sha256']='0'*64
        with tempfile.TemporaryDirectory(prefix='tca-semantic-plan-') as tmp:
            output=Path(tmp)/'refused.xlsm'
            with self.assertRaisesRegex(ValueError,'sémantique a changé'):
                self.engine.apply(self.engine.template_path,plan,output)
            self.assertFalse(output.exists())

    def test_unused_semantic_unknown_is_not_a_global_financial_block(self):
        snapshot,states,modules,calc,_ = qualified_fixture()
        snapshot['cells']['Unknown!Z9'] = {'semantic_status':'REEXAMEN_REQUIS'}
        result = evaluate(snapshot,states,{'source'},module_declarations=modules,calculation=calc)
        self.assertTrue(all(scope['available'] for scope in result['scopes'].values()))

    def test_questions_expose_unit_basis_policy_and_sources(self):
        question = next(q for q in Coordinator(self.engine).questions('DATA COGS') if q['field_id']=='cogs_logistics')
        self.assertIn('fraction',question['unit'])
        self.assertIn('CA',question['basis'])
        self.assertEqual(question['semantics']['status'],'ETABLI_MODELE')

    def test_confirmed_answer_does_not_hide_changed_semantic_definition(self):
        changed=deepcopy(self.catalog)
        field=next(f for f in changed if f['id']=='stock_coverage')
        field['semantics']['status']='REEXAMEN_REQUIS'
        with patch.object(self.engine,'catalog',return_value=changed):
            questions=Coordinator(self.engine).questions('Stock',{'answers':{'stock_coverage':{'status':'CONFIRME','value':30}}})
        question=next(q for q in questions if q['field_id']=='stock_coverage')
        self.assertEqual(question['status'],'SEMANTIQUE_A_REEXAMINER')
        self.assertEqual(question['priority'],0)

    def test_fixture_229_remains_preparable_on_exact_e4_without_touching_sources(self):
        folder = ROOT/'runtime/recette_qualifications_service_20260911_215456_eec175'
        if not (folder/'fixture_updates.json').is_file():
            self.skipTest('Reçu privé de la fixture229 absent.')
        files = [folder/'fixture_updates.json',folder/'preparation.json',folder/'qualification_avant_natif.json']
        before = {p:digest(p) for p in files}
        raw = json.loads(files[0].read_text(encoding='utf-8'))
        updates = [{k:v for k,v in u.items() if k!='status'} for u in raw['updates']]
        plan = self.engine.prepare(self.engine.template_path,updates)
        self.assertEqual(len(plan['changes']),229)
        self.assertTrue(plan['valid'])
        self.assertEqual(before,{p:digest(p) for p in files})
        self.assertEqual(digest(self.engine.template_path),EXPECTED)

    def test_three_operations_fixture_batches_remain_preparable(self):
        from tools.financial_cases_common import common_updates,merge_updates
        from tools.financial_cases_operations import cases
        counts=[]
        for case in cases():
            updates = merge_updates(common_updates(3,'2026-01-01'),case['updates'])
            prepared = [dict(u,reason='Événement de recette fictive relu',evidence='fictitious_source',override_default=True,replace_existing=True) for u in updates]
            plan = self.engine.prepare(self.engine.template_path,prepared)
            self.assertTrue(plan['valid'])
            counts.append(len(plan['changes']))
        self.assertEqual(len(counts),3)
        self.assertTrue(all(n>100 for n in counts))


if __name__ == '__main__':
    unittest.main()
