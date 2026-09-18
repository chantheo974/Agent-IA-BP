import io
import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from tca_bp.mcp_server import TOOLS, dispatch, handle, serve


class WebMCPTests(TestCase):
    def test_decision_job_uses_the_persistent_queue_and_preserves_request_identity(self):
        d=SimpleNamespace(submit=Mock(return_value={'id':'job_existing','status':'QUEUED'}))
        body={'request_id':'same-intent','expected_revision':4,'axes':[{'field_id':'price','values':[100,110]}]}
        result=dispatch(SimpleNamespace(decision_workspace=d),'bp_workshop_job',{'case_id':'case_a','kind':'sensitivity','body':body})
        d.submit.assert_called_once_with('case_a','sensitivity',body)
        self.assertEqual(result['id'],'job_existing')
        with self.assertRaises(ValueError):
            dispatch(SimpleNamespace(decision_workspace=d),'bp_workshop_job',{'case_id':'case_a','kind':'arbitrary_python','body':body})
        self.assertEqual(d.submit.call_count,1)

    def test_apply_requires_the_reviewed_preview_token_and_forwards_it(self):
        workspace = SimpleNamespace(apply=Mock(return_value={'revision': 1}))
        app = SimpleNamespace(web_workspace=workspace)
        with self.assertRaisesRegex(ValueError, 'Arguments'):
            dispatch(app, 'bp_web_apply', {'case_id': 'case_a', 'draft_id': 'draft_a'})
        workspace.apply.assert_not_called()
        result = dispatch(app, 'bp_web_apply', {'case_id': 'case_a', 'draft_id': 'draft_a', 'approval_token': 'reviewed_token'})
        workspace.apply.assert_called_once_with(case_id='case_a', draft_id='draft_a', approval_token='reviewed_token')
        self.assertEqual(result['revision'], 1)

    def test_a_failing_tool_answers_an_error_without_closing_the_session(self):
        class Broken:
            @property
            def web_workspace(self):
                raise ModuleNotFoundError("No module named 'tca_bp.web_workspace'")
        calls = [{'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                  'params': {'name': 'bp_web_draft', 'arguments': {'case_id': 'case_a'}}},
                 {'jsonrpc': '2.0', 'id': 2, 'method': 'ping'}]
        output = io.StringIO()
        stream = io.StringIO(''.join(json.dumps(call) + chr(10) for call in calls))
        serve(Broken(), stream, output)
        answers = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([answer['id'] for answer in answers], [1, 2])
        refusal = json.loads(answers[0]['result']['content'][0]['text'])
        self.assertEqual(refusal['status'], 'ECHEC')
        self.assertNotIn('tca_bp.web_workspace', answers[0]['result']['content'][0]['text'])
        self.assertTrue(answers[0]['result']['isError'])
        self.assertEqual(answers[1]['result'], {})

    def test_declared_tools_are_all_dispatchable_in_this_installation(self):
        app = SimpleNamespace()
        for spec in TOOLS:
            with self.assertRaises((ValueError, AttributeError)) as raised:
                dispatch(app, spec['name'], {})
            self.assertNotIsInstance(raised.exception, ModuleNotFoundError)
        self.assertIn('bp_web_draft', {spec['name'] for spec in TOOLS})

    def test_server_version_follows_the_package(self):
        from tca_bp import __version__
        answer = handle(SimpleNamespace(), {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}})
        self.assertEqual(answer['result']['serverInfo']['version'], __version__)
