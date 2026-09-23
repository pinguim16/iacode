#!/usr/bin/env python3
"""The coding rehearsal: a coding team changes a synthetic repository inside a real sandbox.

`docs/GATE-3-CHECKLIST.md` section 24. The scenarios on the host drive it one subcommand at a time:

    python /app/rehearsal/coding.py worker     run the harness worker
    python /app/rehearsal/coding.py poller     ask Temporal whether a queue has a poller
    python /app/rehearsal/coding.py create     create a coding run over a snapshot, and start it
    python /app/rehearsal/coding.py state      print the run's state as one JSON line
    python /app/rehearsal/coding.py cancel     cancel the run, as the API does
    python /app/rehearsal/coding.py held       whether the scripted model is holding a turn
    python /app/rehearsal/coding.py go         release the turn it is holding
    python /app/rehearsal/coding.py report     what the run recorded, as one JSON document

Everything is real except the model. The run is created by the real
:class:`~iacode_agent_runtime.service.AgentRuntimeService` — the same plan resolution, snapshot
validation and persistence the API uses — and executed by the real
:class:`~iacode_orchestrator.workflows.agent_run.AgentRunWorkflow` with the real persistence
activities, on the stack's Temporal server. Every tool request of a sandboxed stage is dispatched to
the stack's own sandbox service on its own queue, which executes it in a container on the real
engine. The one substitution is the model: it answers from a script, so the sequence of tools is
known and the scenario can assert what each one produced.

The script is not blind. The developer patches only after the tests it ran came back red, and the
reviewer approves only if the commit it inspects carries the fix; otherwise the agent says so and
the scenario fails on what the run recorded.

**Nothing here executes a tool.** This process asks for tools; the sandbox executes them.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import shlex
import sys
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, "/app/src")

from iacode_agent_runtime.contracts import ModelCallOutcome
from iacode_agent_runtime.persistence import SqlAgentRunStore
from iacode_agent_runtime.protocol import ENVELOPE_VERSION
from iacode_agent_runtime.registry import AgentRegistry
from iacode_agent_runtime.service import AgentRuntimeService
from iacode_contracts.agent_runtime import AGENT_RUN_WORKFLOW, CANCEL_SIGNAL, CreateAgentRunRequest
from iacode_contracts.sandbox import SANDBOX_TASK_QUEUE
from iacode_persistence.engine import create_engine, create_session_factory
from iacode_persistence.models import (
    AgentRun,
    RunEvent,
    SandboxSession,
    TaskRun,
    ToolCall,
    ToolRequest,
    ToolResult,
)
from sqlalchemy import select
from temporalio import activity
from temporalio.client import Client
from temporalio.worker import Worker

from iacode_orchestrator.agent_runtime import runtime_context
from iacode_orchestrator.agent_runtime.activities import (
    attach_model_call,
    cancel_pending_tool_requests,
    create_tool_request,
    finish_stage,
    read_tool_result,
    record_event,
    resolve_tool_request,
    set_run_state,
    start_stage,
)
from iacode_orchestrator.config import get_worker_settings
from iacode_orchestrator.workflows.agent_run import AgentRunWorkflow

#: A queue of its own, so the rehearsal never takes a task from the worker that serves real runs.
TASK_QUEUE = "iacode-agent-runtime-coding-rehearsal"

#: The scenarios the script knows, named in the task so the answer is a function of the run.
SCENARIOS = ("coding", "timeout", "cancel", "recovery")

#: Where a held turn waits, inside this container. The scenario releases it with ``go``.
HOLD_DIRECTORY = Path("/tmp")

#: How long a held turn waits for ``go`` before it gives up and says so.
HOLD_SECONDS = 300

TEST_COMMAND = "python3 -m unittest -v test_calc"

FIX = """--- a/calc.py
+++ b/calc.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
"""

COMMIT_MESSAGE = "fix(calc): add returns the sum"


def envelope(kind: str, **fields: Any) -> str:
    return json.dumps({"version": ENVELOPE_VERSION, "kind": kind, **fields})


def tool(name: str, **arguments: Any) -> str:
    return envelope("TOOL_REQUEST", tool={"name": name, "arguments": arguments})


def final(content: str, summary: str) -> str:
    return envelope("FINAL", content=content, summary=summary)


def marker(data: str, name: str) -> str:
    found = re.search(rf"{name}=(\S+)", data)
    return found.group(1) if found else ""


def host_spellings(sentinel: str) -> list[str]:
    """Every way a command might try to name the host file: raw, and as the host's drive.

    Inside a sandbox none of them is the host's file. The raw spelling is a relative name there, so
    writing it lands in the sandbox's own temporary directory; the drive spellings name mount
    points the sandbox does not have.
    """
    posix = sentinel.replace(chr(92), "/")
    drive, separator, rest = posix.partition(":")
    spellings = [sentinel]
    if separator and len(drive) == 1:
        letter = drive.lower()
        spellings += [f"/mnt/{letter}{rest}", f"/{letter}{rest}",
                      f"/run/desktop/mnt/host/{letter}{rest}"]
    return spellings


def probe_command(sentinel: str) -> str:
    """Report where the command runs, and try to reach the host's sentinel from there."""
    lines = [
        "echo UID=$(id -u)",
        "echo PID1=$(tr '\\000' ' ' < /proc/1/cmdline)",
        "if [ -e /var/run/docker.sock ]; then echo SOCKET=PRESENT; else echo SOCKET=ABSENT; fi",
        "cd /tmp",
    ]
    for index, target in enumerate(host_spellings(sentinel)):
        lines.append(f"if echo TAMPERED > {shlex.quote(target)} 2>/dev/null; "
                     f"then echo WRITE-{index}=SANDBOX-ONLY; else echo WRITE-{index}=REFUSED; fi")
    return "; ".join(lines)


async def hold(run_id: str) -> bool:
    """Hold this turn until the scenario says ``go``; ``False`` when it never does."""
    (HOLD_DIRECTORY / f"iacode-coding-held-{run_id}").write_text("held", encoding="utf-8")
    release = HOLD_DIRECTORY / f"iacode-coding-go-{run_id}"
    for _ in range(HOLD_SECONDS * 2):
        if release.exists():
            return True
        activity.heartbeat()
        await asyncio.sleep(0.5)
    return False


async def answer(payload: dict[str, Any]) -> str:
    """The scripted agent: what to say at this stage and turn of this run's scenario."""
    data = str(payload.get("data") or "")
    stage = int(payload.get("stageIndex") or 0)
    turn = int(payload.get("turn") or 1)
    scenario = marker(data, "IACODE_SCENARIO") or "coding"
    run_id = str(payload.get("runId") or "")

    if stage == 0:
        return final("Read calc.py, run the tests, fix what they show, run them again, show the "
                     "diff and commit it.", "a plan for the change")

    if stage == 2:
        if turn == 1:
            return tool("git.show", revision="HEAD")
        approved = "+    return a + b" in data and COMMIT_MESSAGE in data
        verdict = "APPROVED" if approved else "CHANGES-REQUESTED"
        return final(verdict, f"review: {verdict}")

    if scenario == "timeout":
        if turn == 1:
            return tool("shell.exec", command="sleep 60", timeoutSeconds=3)
        seen = '"timedOut": true' in data
        return final("TIMEOUT-SEEN" if seen else "TIMEOUT-NOT-SEEN",
                     "the command was stopped at its timeout")

    if scenario == "cancel":
        if turn == 1:
            return tool("shell.exec", command="sleep 600", timeoutSeconds=280)
        return final("NOT-CANCELLED", "the run was expected to be cancelled before this turn")

    if scenario == "recovery":
        if turn == 1:
            return tool("filesystem.write", path="kept.txt", content="kept across a restart")
        if turn == 2:
            if not await hold(run_id):
                return final("NEVER-RELEASED", "the scenario never released the held turn")
            return tool("filesystem.read", path="kept.txt")
        kept = "kept across a restart" in data
        return final("WORKSPACE-KEPT" if kept else "WORKSPACE-LOST",
                     "read back what was written before the restart")

    steps = {
        1: lambda: tool("filesystem.read", path="calc.py"),
        2: lambda: tool("shell.exec", command=TEST_COMMAND),
        3: lambda: (tool("filesystem.apply_patch", patch=FIX)
                    if "FAILED (failures=1)" in data
                    else final("TESTS-NOT-RED", "the tests did not fail, so nothing was fixed")),
        4: lambda: tool("shell.exec", command=TEST_COMMAND),
        5: lambda: tool("shell.exec", command=probe_command(marker(data, "IACODE_SENTINEL"))),
        6: lambda: tool("git.diff"),
        7: lambda: tool("git.add", paths=["calc.py"]),
        8: lambda: tool("git.commit", message=COMMIT_MESSAGE),
    }
    if turn in steps:
        return steps[turn]()
    return final("FIXED", "the change is committed in the run's workspace")


@activity.defn(name="iacode_agent_runtime_call_model")
async def scripted_call_model(payload: dict) -> dict:
    """The one substitution: the model answers from the script above."""
    text = await answer(payload)
    outcome = ModelCallOutcome(
        text=text,
        model_call_id=None,
        gateway_request_id=f"rehearsal-{uuid.uuid4().hex[:12]}",
        provider="rehearsal",
        model="scripted",
        endpoint="rehearsal",
        route_reason="EXPLICIT_MODEL",
        finish_reason="STOP",
        latency_ms=1.0,
        total_tokens=None,
    )
    return {"text": outcome.text, **outcome.to_dict()}


def settings():
    return get_worker_settings()


def sessions():
    configuration = settings()
    engine = create_engine(
        configuration.database_url,
        pool_size=configuration.database_pool_size,
        max_overflow=configuration.database_max_overflow,
        connect_timeout_seconds=configuration.database_connect_timeout_seconds,
    )
    return engine, create_session_factory(engine)


async def client() -> Client:
    configuration = settings()
    return await Client.connect(configuration.temporal_target, namespace=configuration.namespace)


async def run_worker() -> int:
    configuration = settings()
    runtime_context.set_context(runtime_context.build_context(configuration))
    worker = Worker(
        await client(),
        task_queue=TASK_QUEUE,
        workflows=[AgentRunWorkflow],
        activities=[
            record_event, set_run_state, start_stage, finish_stage, attach_model_call,
            create_tool_request, read_tool_result, cancel_pending_tool_requests,
            resolve_tool_request, scripted_call_model,
        ],
        identity="iacode-coding-rehearsal",
    )
    print(json.dumps({"event": "worker-started", "taskQueue": TASK_QUEUE}), flush=True)
    async with worker:
        await asyncio.Event().wait()
    return 0


async def poller(queue: str) -> int:
    """Ask Temporal whether a queue has a poller, rather than reading a log line (`LSN-0043`)."""
    from temporalio.api.enums.v1 import TaskQueueType
    from temporalio.api.taskqueue.v1 import TaskQueue
    from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

    connected = await client()
    kind = (TaskQueueType.TASK_QUEUE_TYPE_ACTIVITY if queue == SANDBOX_TASK_QUEUE
            else TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW)
    response = await connected.workflow_service.describe_task_queue(
        DescribeTaskQueueRequest(namespace=settings().namespace,
                                 task_queue=TaskQueue(name=queue), task_queue_type=kind))
    print(json.dumps({"taskQueue": queue, "pollers": len(list(response.pollers))}), flush=True)
    return 0


async def create(snapshot: str, scenario: str, sentinel: str) -> int:
    """Create the run through the real service, then start the real workflow on this queue."""
    engine, factory = sessions()
    try:
        service = AgentRuntimeService(session_factory=factory,
                                      registry=AgentRegistry(Path(settings().repository_root)),
                                      store=SqlAgentRunStore(factory))
        task = (f"Make the synthetic repository's tests pass.\n"
                f"IACODE_SCENARIO={scenario}\nIACODE_SENTINEL={sentinel or '-'}\n")
        plan, created = await service.create_run(CreateAgentRunRequest(
            task=task, title=f"sandbox {scenario} rehearsal", team="coding",
            workspaceSnapshot=snapshot, maxTurns=30, maxModelCalls=40,
            maxDurationSeconds=900, toolWaitTimeoutSeconds=600))
        workflow_id = f"iacode-agent-run-{created.runId}"
        connected = await client()
        await connected.start_workflow(AGENT_RUN_WORKFLOW, plan.to_dict(), id=workflow_id,
                                       task_queue=TASK_QUEUE)
        await service.store.set_run_state(created.runId, "QUEUED", workflow_id=workflow_id)
        print(json.dumps({"runId": created.runId, "workflowId": workflow_id,
                          "workspace": plan.workspace,
                          "policies": [stage.sandbox_policy for stage in plan.stages]}),
              flush=True)
        return 0
    finally:
        await engine.dispose()


async def state(run_id: str) -> int:
    engine, factory = sessions()
    try:
        record = await SqlAgentRunStore(factory).load_run(run_id)
        async with factory() as session:
            sandboxes = (await session.execute(
                select(SandboxSession).where(SandboxSession.task_run_id == uuid.UUID(run_id))
            )).scalars().all()
        print(json.dumps({
            "runId": run_id,
            "state": record.state if record else None,
            "sandboxStates": sorted(item.state for item in sandboxes),
        }), flush=True)
        return 0
    finally:
        await engine.dispose()


async def cancel(run_id: str) -> int:
    """Request cancellation exactly as the API does: record it, then tell the workflow."""
    engine, factory = sessions()
    try:
        await SqlAgentRunStore(factory).request_cancellation(run_id)
        handle = (await client()).get_workflow_handle(f"iacode-agent-run-{run_id}")
        await handle.signal(CANCEL_SIGNAL, "rehearsal")
        print(json.dumps({"cancelled": run_id}), flush=True)
        return 0
    finally:
        await engine.dispose()


def held(run_id: str) -> int:
    print(json.dumps({"held": (HOLD_DIRECTORY / f"iacode-coding-held-{run_id}").exists()}),
          flush=True)
    return 0


def go(run_id: str) -> int:
    (HOLD_DIRECTORY / f"iacode-coding-go-{run_id}").write_text("go", encoding="utf-8")
    print(json.dumps({"released": run_id}), flush=True)
    return 0


def _clip(value: Any, limit: int = 4000) -> Any:
    """A report is evidence, not a dump: every text in it is bounded."""
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + "...[clipped]"
    if isinstance(value, dict):
        return {key: _clip(item, limit) for key, item in value.items()}
    if isinstance(value, list):
        return [_clip(item, limit) for item in value[:50]]
    return value


async def report(run_id: str) -> int:
    """What the run recorded, read from the database rather than from anything this process sent."""
    engine, factory = sessions()
    identifier = uuid.UUID(run_id)
    try:
        async with factory() as session:
            run = await session.get(TaskRun, identifier)
            stages = (await session.execute(
                select(AgentRun).where(AgentRun.task_run_id == identifier)
                .order_by(AgentRun.stage_index))).scalars().all()
            requests = (await session.execute(
                select(ToolRequest).where(ToolRequest.task_run_id == identifier)
                .order_by(ToolRequest.created_at))).scalars().all()
            results = {row.tool_request_id: row for row in (await session.execute(
                select(ToolResult).where(ToolResult.tool_request_id.in_(
                    [item.id for item in requests])))).scalars().all()} if requests else {}
            calls = {row.tool_request_id: row for row in (await session.execute(
                select(ToolCall).where(ToolCall.tool_request_id.in_(
                    [item.id for item in requests])))).scalars().all()} if requests else {}
            sandboxes = (await session.execute(
                select(SandboxSession).where(SandboxSession.task_run_id == identifier)
                .order_by(SandboxSession.created_at))).scalars().all()
            events = (await session.execute(
                select(RunEvent).where(RunEvent.task_run_id == identifier)
                .order_by(RunEvent.sequence))).scalars().all()
        stage_of = {item.id: item.stage_name for item in stages}
        executions = []
        for item in requests:
            result, call = results.get(item.id), calls.get(item.id)
            executions.append({
                "toolRequestId": str(item.id),
                "stage": stage_of.get(item.agent_run_id),
                "tool": item.tool_name,
                "requestStatus": item.status,
                "resultStatus": result.status if result else None,
                "resultOutput": _clip(result.output) if result else None,
                "resultError": _clip(result.error) if result else None,
                "executionStatus": call.status if call else None,
                "exitCode": call.exit_code if call else None,
                "timedOut": call.timed_out if call else None,
                "durationMs": call.latency_ms if call else None,
                "sandboxSession": str(call.sandbox_session_id) if call and
                call.sandbox_session_id else None,
            })
        print(json.dumps({
            "runId": run_id,
            "state": run.status if run else None,
            "result": _clip(run.result) if run else None,
            "errorType": run.error_type if run else None,
            "errorSummary": run.error_summary if run else None,
            "stages": [{"name": item.stage_name, "agent": item.agent_slug,
                        "status": item.status, "output": _clip(item.output, 400)}
                       for item in stages],
            "executions": executions,
            "sandboxes": [{"sessionId": str(item.id), "state": item.state,
                           "policy": item.policy, "containerName": item.container_name,
                           "networkProfile": item.network_profile,
                           "imageFingerprint": item.image_fingerprint}
                          for item in sandboxes],
            "events": [item.event_type for item in events],
        }), flush=True)
        return 0
    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("worker", "poller", "create", "state", "cancel",
                                            "held", "go", "report"))
    parser.add_argument("--run", default=None)
    parser.add_argument("--queue", default=TASK_QUEUE)
    parser.add_argument("--snapshot", default=None)
    parser.add_argument("--scenario", choices=SCENARIOS, default="coding")
    parser.add_argument("--sentinel", default="")
    arguments = parser.parse_args()

    if arguments.command == "worker":
        return asyncio.run(run_worker())
    if arguments.command == "poller":
        return asyncio.run(poller(arguments.queue))
    if arguments.command == "create":
        if not arguments.snapshot:
            parser.error("--snapshot is required to create a coding run")
        return asyncio.run(create(arguments.snapshot, arguments.scenario, arguments.sentinel))
    if not arguments.run:
        parser.error("--run is required for this command")
    if arguments.command == "state":
        return asyncio.run(state(arguments.run))
    if arguments.command == "cancel":
        return asyncio.run(cancel(arguments.run))
    if arguments.command == "held":
        return held(arguments.run)
    if arguments.command == "go":
        return go(arguments.run)
    return asyncio.run(report(arguments.run))


if __name__ == "__main__":
    sys.exit(main())
