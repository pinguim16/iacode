"""The activity the workflow dispatches to: what it answers, and under which names.

The workflow and the sandbox run in two processes and meet only on a Temporal queue. The first
version of this activity answered with the execution record alone while the workflow read the tool
result under a key the answer did not have; every suite that drove either side against a double
passed, and the first real run failed its workflow task. The activity is exercised here as Temporal
runs it, and the names it answers with are the shared contract's.
"""

from __future__ import annotations

import asyncio

from iacode_contracts.sandbox import SANDBOX_AGENT_RESULT_KEY, SANDBOX_EXECUTION_KEY
from iacode_sandbox import worker
from sandbox_fixtures import FakeBackend, fake_service, request
from temporalio.testing import ActivityEnvironment

#: What the agent runtime's tool result is made of; the workflow parses exactly these.
TOOL_RESULT_FIELDS = {"toolRequestId", "status", "output", "error", "metadata"}


def execute(payload: dict, backend: FakeBackend) -> dict:
    service, _store = fake_service(backend)
    worker.set_service(service)
    try:
        return asyncio.run(ActivityEnvironment().run(worker.execute_tool, payload))
    finally:
        worker.set_service(None)


class SandboxActivityTests:
    def test_the_activity_answers_the_agent_result_and_the_execution(self) -> None:
        backend = FakeBackend(responses=[{"ok": True, "result": {
            "content": "print('ok')\n", "path": "a.py", "size": 12}}])
        payload = request("filesystem.read", {"path": "a.py"}, run_id="r-1")

        body = execute(payload, backend)

        assert set(body) == {SANDBOX_AGENT_RESULT_KEY, SANDBOX_EXECUTION_KEY}
        agent = body[SANDBOX_AGENT_RESULT_KEY]
        assert set(agent) == TOOL_RESULT_FIELDS
        assert (agent["toolRequestId"], agent["status"]) == (payload["toolRequestId"],
                                                             "SUCCEEDED")
        assert agent["output"]["content"] == "print('ok')\n"
        assert body[SANDBOX_EXECUTION_KEY]["tool"] == "filesystem.read"

    def test_a_refusal_reaches_the_agent_as_a_tool_result_too(self) -> None:
        payload = request("shell", {"command": "id"}, run_id="r-1")

        body = execute(payload, FakeBackend())

        agent = body[SANDBOX_AGENT_RESULT_KEY]
        assert set(agent) == TOOL_RESULT_FIELDS
        assert agent["status"] == "DENIED"
        assert agent["metadata"]["errorCode"] == "UNKNOWN_TOOL"
