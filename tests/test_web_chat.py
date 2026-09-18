"""Real orchestration protocol against a fake HTTP provider; no Excel writes."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import threading
import unittest

import httpx

from tca_bp.web_chat import ChatCoordinator, ChatError, validate_operations
from tca_bp.web_settings import WebSettings
from tests.test_web_settings import TestProtector


def result(message="Proposition prête à examiner.", operations=None, questions=None):
    return {"message": message, "operations": operations or [], "questions": questions or []}


def reply(value, *, reasoning="private opaque provider context", tools=None):
    return {"role": "assistant", "content": json.dumps(value, ensure_ascii=False) if value else None,
            "reasoning_content": reasoning, **({"tool_calls": tools} if tools else {})}


def tool(name, args, identifier="call_01"):
    return {"id": identifier, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


def as_sse(answer, *, complete=True):
    parts = []
    for key in ("reasoning_content", "content"):
        text = answer.get(key) or ""
        for start in range(0, len(text), 11):
            parts.append({"choices": [{"index": 0, "delta": {key: text[start:start + 11]}, "finish_reason": None}]})
    for index, call in enumerate(answer.get("tool_calls", [])):
        parts.append({"choices": [{"index": 0, "delta": {"tool_calls": [{"index": index, "id": call["id"], "type": "function", "function": {"name": call["function"]["name"], "arguments": ""}}]}, "finish_reason": None}]})
        arguments = call["function"]["arguments"]
        for start in range(0, len(arguments), 9):
            parts.append({"choices": [{"index": 0, "delta": {"tool_calls": [{"index": index, "function": {"arguments": arguments[start:start + 9]}}]}, "finish_reason": None}]})
    if complete:
        parts.append({"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls" if answer.get("tool_calls") else "stop"}]})
    content = ": provider keepalive\n\n" + "".join("data: " + json.dumps(part) + "\n\n" for part in parts)
    if complete:
        content += "data: [DONE]\n\n"
    return httpx.Response(200, headers={"content-type": "text/event-stream"}, text=content)


class ChatFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.settings = WebSettings(Path(self.temp.name) / "settings.json", protector=TestProtector())
        self.settings.update(api_key="dummy-key-for-protocol-tests")
        self.selection = {"sheet": "Effectifs", "range": "B10:D20", "allow_structure": True}
        self.context = {"case_id": "case_a", "revision": 4, "user_source_id": "src_request",
                        "sources": [{"id": "src_request", "case_id": "case_a", "title": "Demande utilisateur", "text": "Augmente les salaires de 5 %."}],
                        "cells": {"Effectifs": {"C12": {"value": 2000, "formula": None}}},
                        "dependencies": {"Effectifs": ["Control"], "Compte de Résultat": ["Effectifs"]},
                        "agents": [{"id": "AGENT_12", "sheet": "Effectifs", "role": "Préparer les recrutements et salaires.", "checks": ["Salaire brut documenté."]},
                                   {"id": "AGENT_27", "sheet": "Compte de Résultat", "role": "Expliquer les conséquences sur le résultat."}]}
        self.operation = {"type": "set_value", "sheet": "Effectifs", "cell": "C12", "value": 2100, "evidence_id": "src_request"}

    def coordinator(self, answers):
        self.requests = []
        iterator = iter(answers)
        def handler(request):
            self.assertEqual(request.url.path, "/chat/completions")
            self.assertEqual(request.headers["authorization"], "Bearer dummy-key-for-protocol-tests")
            self.requests.append(json.loads(request.content))
            answer = next(iterator)
            return answer if isinstance(answer, httpx.Response) else as_sse(answer)
        return ChatCoordinator(self.settings, transport=httpx.MockTransport(handler))


class ChatTests(ChatFixture, unittest.TestCase):
    def test_provider_reads_draft_without_local_receipts_or_approval_token(self):
        self.context['draft'] = {'id': 'draft_a', 'status': 'READY', 'operations': [self.operation],
            'approval_token': 'private-preview-approval',
            'validation': {'output_path': 'C:/private-profile/native-output.xlsm'}}
        coordinator = self.coordinator([reply(result('Le brouillon propose 2100.'))])
        coordinator.run('Explique le brouillon.', self.selection, self.context)
        sent = json.dumps(self.requests)
        self.assertIn('2100', sent)
        self.assertNotIn('private-preview-approval', sent)
        self.assertNotIn('private-profile', sent)

    def test_real_specialist_dispatch_preserves_private_reasoning(self):
        first = reply(None, tools=[tool("consult_agent", {"agent_id": "AGENT_12", "task": "Calculer le salaire après augmentation."})])
        specialist = reply(result(operations=[self.operation]), reasoning="specialist private reasoning")
        final = reply(result(operations=[self.operation]), reasoning="coordinator private reasoning")
        coordinator = self.coordinator([first, specialist, final])
        events, checkpoints = [], []
        output = coordinator.run("Augmente de 5 %.", self.selection, self.context, emit=events.append, checkpoint=checkpoints.append)
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(output["operations"], [self.operation])
        self.assertEqual(output["agents"][0]["id"], "AGENT_12")
        self.assertNotIn("tools", self.requests[1])
        self.assertEqual(self.requests[2]["messages"][2]["reasoning_content"], "private opaque provider context")
        self.assertEqual(output["provider_messages"][-1]["reasoning_content"], "coordinator private reasoning")
        self.assertIn("specialist private reasoning", json.dumps(output["tool_runs"]))
        self.assertNotIn("private", json.dumps(events))
        self.assertNotIn("dummy-key", json.dumps(checkpoints))
        self.assertEqual(events[-1], {"type": "message", "delta": "Proposition prête à examiner."})

    def test_plain_question_does_not_call_every_agent(self):
        coordinator = self.coordinator([reply(result("Le salaire sélectionné est de 2 000 euros avant modification."))])
        output = coordinator.run("Quel salaire est sélectionné ?", self.selection, self.context)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(output["agents"], [])
        self.assertIn("2000", self.requests[0]["messages"][0]["content"])

    def test_provider_without_tool_use_still_gets_actual_specialist_review(self):
        answers = [reply(result(operations=[self.operation])) for _ in range(3)]
        coordinator = self.coordinator(answers)
        output = coordinator.run("Augmente de 5 %", self.selection, self.context)
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(len(output["agents"]), 1)

    def test_read_dependency_is_case_bound_and_does_not_extend_write_scope(self):
        coordinator = self.coordinator([
            reply(None, tools=[tool("read_cells", {"sheet": "Compte de Résultat", "range": "D10:D12"})]),
            reply(result("Le résultat courant dépend des salaires; un recalcul sera requis après application.")),
        ])
        reads = []
        def reader(sheet, area):
            reads.append((sheet, area))
            return {"revision": 4, "cells": [{"cell": "D10", "value": 100, "calculation_status": "CALCULATED"}]}
        coordinator.run("Explique les effets.", self.selection, self.context, context_reader=reader)
        self.assertEqual(reads, [("Compte de Résultat", "D10:D12")])
        bad = {**self.operation, "sheet": "Compte de Résultat"}
        with self.assertRaisesRegex(ValueError, "feuille sélectionnée"):
            validate_operations([bad], self.selection, self.context)

    def test_unknown_execution_tool_is_never_executed(self):
        coordinator = self.coordinator([
            reply(None, tools=[tool("run_powershell", {"code": "Set-Content stolen.txt secret"})]),
            reply(result("Cette opération ne fait pas partie des outils autorisés.")),
        ])
        output = coordinator.run("Explique cette cellule", self.selection, self.context)
        self.assertEqual(output["operations"], [])
        self.assertIn("non autorisés", self.requests[1]["messages"][-1]["content"])
        self.assertFalse((Path(self.temp.name) / "stolen.txt").exists())

    def test_incomplete_stream_never_emits_partial_json_or_operations(self):
        coordinator = self.coordinator([as_sse(reply(result(operations=[self.operation])), complete=False)])
        events = []
        with self.assertRaises(ChatError) as caught:
            coordinator.run("Augmente", self.selection, self.context, emit=events.append)
        self.assertEqual(caught.exception.code, "PROVIDER_INCOMPLETE")
        self.assertTrue(caught.exception.retryable)
        self.assertFalse(any(event["type"] == "message" for event in events))
        self.assertNotIn("reasoning", json.dumps(events))

    def test_cancel_before_request(self):
        cancel = threading.Event()
        cancel.set()
        coordinator = self.coordinator([])
        with self.assertRaises(ChatError) as caught:
            coordinator.run("Bonjour", self.selection, self.context, cancel=cancel)
        self.assertEqual(caught.exception.code, "CHAT_CANCELLED")
        self.assertEqual(self.requests, [])

    def test_provider_error_checkpoint_has_no_key(self):
        coordinator = self.coordinator([httpx.Response(503, text="secret dummy-key-for-protocol-tests")])
        with self.assertRaises(ChatError) as caught:
            coordinator.run("Bonjour", self.selection, self.context)
        self.assertTrue(caught.exception.retryable)
        self.assertNotIn("secret", str(caught.exception))
        self.assertNotIn("dummy-key", json.dumps(caught.exception.provider_messages))

    def test_reasoning_without_tools_is_retained_across_turns(self):
        history = [{"role": "user", "content": "Précédente question"}, reply(result("Ancienne réponse"), reasoning="required opaque prior context")]
        coordinator = self.coordinator([reply(result("Nouvelle réponse"))])
        coordinator.run("Continue", self.selection, self.context, history=history)
        assistant = next(item for item in self.requests[0]["messages"] if item["role"] == "assistant")
        self.assertEqual(assistant["reasoning_content"], "required opaque prior context")

    def test_incomplete_tool_history_is_resumable_without_dangling_tool(self):
        history = [{"role": "user", "content": "Ancienne question"}, reply(None, tools=[tool("consult_agent", {"agent_id": "AGENT_12", "task": "Relire"})])]
        coordinator = self.coordinator([reply(result("Reprise sans changement."))])
        coordinator.run("Reprends", self.selection, self.context, history=history)
        self.assertFalse(any(item.get("tool_calls") for item in self.requests[0]["messages"]))

    def test_differing_specialist_proposals_require_clarification(self):
        calls = [tool("consult_agent", {"agent_id": "AGENT_12", "task": "Salaire"}, "call_1"),
                 tool("consult_agent", {"agent_id": "AGENT_27", "task": "Effet salaire"}, "call_2")]
        coordinator = self.coordinator([reply(None, tools=calls), reply(result(operations=[self.operation])),
                                        reply(result(operations=[{**self.operation, "value": 2200}])), reply(result(operations=[self.operation]))])
        with self.assertRaisesRegex(ChatError, "contradictoires"):
            coordinator.run("Augmente les salaires", self.selection, self.context)

    def test_invalid_model_proposal_is_not_partially_accepted(self):
        coordinator = self.coordinator([reply(result(operations=[self.operation, {**self.operation, "cell": "A999"}]))])
        with self.assertRaises(ChatError) as caught:
            coordinator.run("Augmente", self.selection, self.context)
        self.assertEqual(caught.exception.code, "PROPOSAL_INVALID")

    def test_current_context_omits_filesystem_paths_and_secrets(self):
        self.context["api_key"] = "should-not-send"
        self.context["sources"][0]["path"] = "C:/Users/private/client.pdf"
        coordinator = self.coordinator([reply(result("Lecture effectuée"))])
        coordinator.run("Explique", self.selection, self.context)
        sent = json.dumps(self.requests[0])
        self.assertNotIn("should-not-send", sent)
        self.assertNotIn("C:/Users", sent)


class OperationValidationTests(ChatFixture, unittest.TestCase):
    def test_source_from_another_case_rejected_even_without_edit(self):
        self.context["sources"][0]["case_id"] = "case_other"
        with self.assertRaisesRegex(ValueError, "autre dossier"):
            validate_operations([], self.selection, self.context)

    def test_missing_source_falls_back_to_current_user_message(self):
        operation = {k: v for k, v in self.operation.items() if k != "evidence_id"}
        self.assertEqual(validate_operations([operation], self.selection, self.context)[0]["evidence_id"], "src_request")
        self.context.pop("user_source_id")
        with self.assertRaisesRegex(ValueError, "source"):
            validate_operations([operation], self.selection, self.context)

    def test_unknown_or_cross_case_source(self):
        with self.assertRaisesRegex(ValueError, "source absente"):
            validate_operations([{**self.operation, "evidence_id": "foreign-source"}], self.selection, self.context)

    def test_same_cell_conflict_and_identical_deduplication(self):
        self.assertEqual(len(validate_operations([self.operation, self.operation], self.selection, self.context)), 1)
        with self.assertRaisesRegex(ValueError, "incompatibles"):
            validate_operations([self.operation, {**self.operation, "value": 2300}], self.selection, self.context)

    def test_structure_requires_explicit_scope_and_role_for_new_sheet(self):
        operation = {"type": "insert_rows", "sheet": "Effectifs", "index": 12, "count": 2}
        self.assertEqual(validate_operations([operation], self.selection, self.context)[0]["index"], 12)
        with self.assertRaises(ValueError):
            validate_operations([operation], {**self.selection, "allow_structure": False}, self.context)
        with self.assertRaisesRegex(ValueError, "sélectionnées"):
            validate_operations([{**operation, "index": 21}], self.selection, self.context)
        new_sheet = {"type": "add_sheet", "name": "Scénario", "role": "Comparer les hypothèses et résultats des variantes."}
        self.assertEqual(validate_operations([new_sheet], self.selection, self.context)[0]["role"], new_sheet["role"])
        with self.assertRaises(ValueError):
            validate_operations([{**new_sheet, "role": ""}], self.selection, self.context)

    def test_formulas_are_explicit_and_no_external_execution(self):
        operation = {"type": "set_formula", "sheet": "Effectifs", "cell": "C12", "formula": "=SUM(C10:C11)*1.05"}
        self.assertEqual(validate_operations([operation], self.selection, self.context)[0]["formula"], operation["formula"])
        for formula in ("=WEBSERVICE(\"https://example.com\")", "=cmd|'calc'!A0", "='[foreign.xlsx]Sheet'!A1", "=RTD(\"server\",\"\",\"x\")"):
            with self.subTest(formula=formula), self.assertRaises(ValueError):
                validate_operations([{**operation, "formula": formula}], self.selection, self.context)
        with self.assertRaises(ValueError):
            validate_operations([{**self.operation, "value": "=SUM(C1:C2)"}], self.selection, self.context)

    def test_reject_unknown_keys_malformed_types_and_nonfinite_values(self):
        bad = [{**self.operation, "python": "print('bad')"}, {**self.operation, "value": float("nan")},
               {**self.operation, "value": {}}, {**self.operation, "type": []},
               {**self.operation, "evidence_id": []}, {**self.operation, "cell": "XFE12"}]
        for operation in bad:
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                validate_operations([operation], self.selection, self.context)


if __name__ == "__main__":
    unittest.main()
