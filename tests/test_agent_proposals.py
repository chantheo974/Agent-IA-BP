"""Réconciliation multiagents : conflits locaux, identité et transaction unique."""
from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.agents import Coordinator, PROPOSAL_CONTEXT_KEYS
from tca_bp.knowledge import contracts
from tca_bp.mcp_server import dispatch
from tca_bp.model_registry import model_pin
from tca_bp.service import Application
try:
    from .test_agents import FakeEngine
    from .test_qualification_service import QualificationEngine
except ImportError:
    from test_agents import FakeEngine
    from test_qualification_service import QualificationEngine


AUTHORS = [agent['id'] for agent in contracts()]


def context_of(case):
    return {'case_id': case['id'], 'client_id': case['client_id'], **model_pin(case),
            'revision': case['revision'], 'source_sha256': case['sha256']}


class MergeProposalTests(unittest.TestCase):
    def setUp(self):
        self.engine = FakeEngine()
        self.coordinator = Coordinator(self.engine)
        self.context = {key: 'test' for key in PROPOSAL_CONTEXT_KEYS}
        self.context.update(model_id=self.engine.model_id, revision=0)

    def proposal(self, value=2, author=0, **change):
        return {'agent_id': AUTHORS[author], 'context': deepcopy(self.context), 'updates': [{
            'sheet': 'DATA Contrats', 'cell': 'E3', 'value': value, 'status': 'CONFIRME',
            'evidence': 'source_a', 'reason': 'Quantité documentée', **change}], 'questions': []}

    def test_equal_values_merge_all_evidence_and_reasons_without_writing(self):
        result = self.coordinator.merge_proposals([self.proposal(), self.proposal(2.0, 1, evidence='source_b', reason='Contrat concordant')])
        self.assertEqual(result['status'], 'READY_FOR_PREPARATION')
        self.assertEqual(len(result['updates']), 1)
        self.assertIn('source_b', result['updates'][0]['reason'])
        self.assertEqual(len(result['contributions'][0]['proposals']), 2)
        self.assertEqual(self.engine.prepares, [])

    def test_incompatible_values_suspend_whole_batch_and_keep_exact_alternatives(self):
        extra = self.proposal('Client fictif', cell='B3')
        result = self.coordinator.merge_proposals([self.proposal(), self.proposal(3, 1), extra])
        self.assertEqual(result['status'], 'NEEDS_REVIEW')
        self.assertEqual(result['updates'], [])
        self.assertEqual({v['update']['value'] for v in result['conflicts'][0]['proposals']}, {2, 3})
        self.assertTrue(result['questions'])

    def test_status_and_permission_differences_are_conflicts_not_promotions(self):
        for change in ({'status': 'HYPOTHESE'}, {'replace_existing': True}, {'override_default': True}):
            with self.subTest(change=change):
                result = self.coordinator.merge_proposals([self.proposal(), self.proposal(author=1, **change)])
                self.assertEqual(result['status'], 'NEEDS_REVIEW')

    def test_boolean_is_not_merged_with_number(self):
        result = self.coordinator.merge_proposals([self.proposal(1), self.proposal(True, 1)])
        self.assertTrue(result['conflicts'])

    def test_questions_suspend_batch_without_changing_engine(self):
        proposal = self.proposal()
        proposal['questions'] = ['Le contrat est-il signé ou seulement probable ?']
        result = self.coordinator.merge_proposals([proposal])
        self.assertEqual(result['status'], 'NEEDS_INPUT')
        self.assertFalse(result['updates'])
        self.assertFalse(self.engine.prepares)

    def test_document_has_no_authority_and_protected_output_is_refused(self):
        document = {**self.proposal(), 'origin': 'document'}
        result = self.coordinator.merge_proposals([document])
        self.assertEqual(result['status'], 'REFUSED')
        self.assertFalse(result['updates'])
        result = self.coordinator.merge_proposals([self.proposal(cell='X99')])
        self.assertEqual(result['refusals'][0]['code'], 'HORS_CATALOGUE')

    def test_cross_case_or_model_or_revision_is_refused(self):
        for key, value in [('case_id', 'other'), ('model_ref', 'other'), ('revision', 1), ('source_sha256', 'other')]:
            proposal = self.proposal()
            proposal['context'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.coordinator.merge_proposals([proposal], expected_context=self.context)

    def test_reordering_proposals_keeps_exact_digest_and_merged_changes(self):
        a, b = self.proposal(), self.proposal(author=1, evidence='source_b')
        left = self.coordinator.merge_proposals([a, b])
        right = self.coordinator.merge_proposals([b, a])
        self.assertEqual(left['proposal_sha256'], right['proposal_sha256'])
        self.assertEqual(left['updates'], right['updates'])

    def test_formula_instruction_and_unknown_privilege_flag_are_rejected(self):
        for proposal in (self.proposal('=DELETE()'), self.proposal(force=True), self.proposal(status='INACTIF')):
            with self.assertRaises(ValueError):
                self.coordinator.merge_proposals([proposal])


class AgentProposalServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.engine = QualificationEngine(self.root)
        self.app = Application(self.root, self.root / 'data', engine=self.engine)
        self.case = self.app.create_case('Fictif A', 'Propositions', case_id='a')
        self.source = self.app.add_source('a', text='Réponse fictive : une année de prévision.')

    def tearDown(self):
        self.tmp.cleanup()

    def proposal(self, value=1, author=0, evidence=None):
        return {'agent_id': AUTHORS[author], 'context': context_of(self.case), 'updates': [{
            'sheet': 'Control', 'cell': 'C59', 'value': value, 'status': 'CONFIRME',
            'evidence': evidence or self.source['id'], 'reason': 'Horizon documenté'}]}

    def test_conflict_suspends_only_batch_and_an_independent_plan_can_be_prepared(self):
        before = self.app.get_case('a')
        result = self.app.prepare_agent_proposals('a', [self.proposal(), self.proposal(2, 1)], 'conflict')
        self.assertEqual(result['status'], 'NEEDS_REVIEW')
        after = self.app.get_case('a')
        self.assertEqual((after['revision'], after['sha256']), (before['revision'], before['sha256']))
        self.assertEqual(after['plans'], [])
        self.assertTrue(after['questions'])
        good = self.app.prepare_agent_proposals('a', [self.proposal()], 'independent')
        self.assertEqual(good['status'], 'PRET_A_APPLIQUER')

    def test_all_concordant_sources_must_belong_to_case(self):
        self.app.create_case('Fictif B', 'Autre', case_id='b')
        other = self.app.add_source('b', text='Source extérieure au dossier A')
        with self.assertRaises(ValueError):
            self.app.prepare_agent_proposals('a', [self.proposal(), self.proposal(author=1, evidence=other['id'])], 'foreign')
        self.assertFalse(self.app.get_case('a')['plans'])

    def test_prepare_and_applied_replay_preserve_request_identity(self):
        proposals = [self.proposal(), self.proposal(author=1)]
        plan = self.app.prepare_agent_proposals('a', proposals, 'same')
        self.assertEqual(plan['request_id'], 'same')
        replay = self.app.prepare_agent_proposals('a', proposals, 'same')
        self.assertEqual(replay['id'], plan['id'])
        self.app.apply_plan('a', plan['id'])
        replay = self.app.prepare_agent_proposals('a', proposals, 'same')
        self.assertEqual(replay['status'], 'DEJA_APPLIQUE')
        self.assertEqual(self.app.get_case('a')['revision'], 1)
        with self.assertRaises(ValueError):
            self.app.prepare_agent_proposals('a', [self.proposal(author=2)], 'same')

    def test_revision_change_between_merge_and_prepare_is_detected_under_lock(self):
        real = self.app.prepare_changes
        def changed(*args, **kwargs):
            with self.app.store.connection() as db:
                db.execute("UPDATE cases SET revision=revision+1 WHERE id='a'")
            return real(*args, **kwargs)
        with patch.object(self.app, 'prepare_changes', changed), self.assertRaises(ValueError):
            self.app.prepare_agent_proposals('a', [self.proposal()], 'race')
        self.assertFalse(self.app.get_case('a')['plans'])

    def test_registered_provenance_survives_prepare_failure(self):
        with patch.object(self.app, 'prepare_changes', side_effect=ValueError('Échec simulé')), self.assertRaises(ValueError):
            self.app.prepare_agent_proposals('a', [self.proposal()], 'recover')
        with self.assertRaises(ValueError):
            self.app.prepare_agent_proposals('a', [self.proposal(author=1)], 'recover')
        plan = self.app.prepare_agent_proposals('a', [self.proposal()], 'recover')
        self.assertEqual(plan['status'], 'PRET_A_APPLIQUER')

    def test_mcp_calls_same_guarded_pipeline(self):
        result = dispatch(self.app, 'bp_prepare_agent_proposals', {'case_id': 'a', 'proposals': [self.proposal()], 'request_id': 'mcp'})
        self.assertEqual(result['status'], 'PRET_A_APPLIQUER')
        self.assertEqual(self.app.get_case('a')['revision'], 0)

    def test_cli_reads_structured_list_and_does_not_apply(self):
        from tca_bp.__main__ import main
        path = self.root / 'proposals.json'
        path.write_text(json.dumps([self.proposal()]), encoding='utf-8')
        output = io.StringIO()
        with patch('tca_bp.service.Application', return_value=self.app), contextlib.redirect_stdout(output):
            status = main(['prepare-agent-proposals', 'a', str(path), '--request-id', 'cli'])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'PRET_A_APPLIQUER')
        self.assertEqual(self.app.get_case('a')['revision'], 0)


if __name__ == '__main__':
    unittest.main()
