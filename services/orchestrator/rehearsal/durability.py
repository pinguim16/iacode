#!/usr/bin/env python3
"""The durability rehearsal: one run, one tool pause, one real worker restart.

Five subcommands, each doing one thing so the scenario on the host can step through the rehearsal
and restart the worker container in the middle of it.

    python /app/rehearsal/durability.py worker      run the harness worker (this is what restarts)
    python /app/rehearsal/durability.py poller      ask Temporal whether the queue has a poller
    python /app/rehearsal/durability.py create      create the task, the run and the workflow
                                                   (--looping --deadline N for the deadline check)
    python /app/rehearsal/durability.py state       print the run's state as one JSON line
    python /app/rehearsal/durability.py resolve     answer the pending tool request
    python /app/rehearsal/durability.py cancel      cancel the run, as the API does
    python /app/rehearsal/durability.py try-resolve attempt a late answer and report the refusal
    python /app/rehearsal/durability.py events      print the recorded events

The workflow is the real :class:`~iacode_orchestrator.workflows.agent_run.AgentRunWorkflow`, the
persistence activities are the real ones, and Temporal is the stack's own server. Exactly one thing
is scripted: the model. It answers the first turn with a tool request and the second with a final
answer, which is the sequence the restart has to survive.

**Nothing here executes a tool.** The result is supplied by ``resolve``, over the same store the
API writes through, which is what a sandbox will do from Gate 3 onwards.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/app/src")

from iacode_agent_runtime.budgets import Budget
from iacode_agent_runtime.contracts import ModelCallOutcome, RunPlan, StagePlan, ToolResult
from iacode_agent_runtime.persistence import SqlAgentRunStore
from iacode_agent_runtime.protocol import ENVELOPE_VERSION
from iacode_agent_runtime.registry import AgentRegistry
from iacode_agent_runtime.states import RunState
from iacode_common.identifiers import uuid7
from iacode_contracts.agent_runtime import (
    AGENT_RUN_WORKFLOW,
    CANCEL_SIGNAL,
    TOOL_EXECUTOR_EXTERNAL,
    TOOL_RESULT_SIGNAL,
)
from iacode_persistence.engine import create_engine, create_session_factory
from iacode_persistence.models import Agent, Project, Task, TaskRun
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
    set_run_state,
    start_stage,
)
from iacode_orchestrator.config import get_worker_settings
from iacode_orchestrator.workflows.agent_run import AgentRunWorkflow

#: A queue of its own, so the rehearsal never takes a task from the worker that serves real runs.
TASK_QUEUE = "iacode-agent-runtime-rehearsal"

#: The tool the scripted agent asks for. An inert name: it is stored and compared, never resolved.
TOOL_NAME = "rehearsal.read"

#: A task carrying this marker makes the scripted agent answer MESSAGE for ever, which is what the
#: deadline rehearsal needs: a run that is alive and going nowhere.
LOOP_MARKER = "IACODE_LOOP_FOREVER"

PROJECT_SLUG = "iacode-durability-rehearsal"
AGENT_SLUG = "rehearsal-agent"


def envelope(kind: str, **fields) -> str:
    return json.dumps({"version": ENVELOPE_VERSION, "kind": kind, **fields})


@activity.defn(name="iacode_agent_runtime_call_model")
async def scripted_call_model(payload: dict) -> dict:
    """The one substitution. Turn 1 asks for a tool; every later turn finishes.

    The turn number comes from the request the engine built, so the answer is a function of the
    run's own state rather than of anything this process remembers — which is what lets the
    activity survive the restart it is here to demonstrate.
    """
    turn = int(payload.get("turn") or 1)
    if LOOP_MARKER in str(payload.get("data") or ""):
        # A run that never finishes, for the deadline rehearsal. The answer is a function of the
        # task the run carries, so it survives a replay exactly like the branch below.
        text = envelope("MESSAGE", content="still working")
    elif turn == 1:
        text = envelope("TOOL_REQUEST",
                        tool={"name": TOOL_NAME, "arguments": {"path": "README.md"}})
    else:
        text = envelope("FINAL", content="IACODE_DURABILITY_OK",
                        summary="resumed after the restart")
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


def plan_for(run_id: str, task_id: str, task: str, *, deadline_seconds: int = 600,
             max_turns: int = 4) -> RunPlan:
    """A one-stage plan whose agent is permitted exactly the one inert tool name."""
    registry = AgentRegistry(Path(settings().repository_root))
    profile = registry.agent("generalist")
    stage = StagePlan(
        index=0,
        name="answer",
        agent=AGENT_SLUG,
        agent_name="Rehearsal agent",
        role_instructions=profile.template.render(
            role="rehearsal", description="A scripted agent used to rehearse a restart."),
        inputs=("task",),
        output_name="answer",
        max_turns=max_turns,
        allowed_actions=(TOOL_NAME,),
        profile_version="rehearsal",
        prompt_template=profile.template.path,
        prompt_template_version=profile.template.version,
        prompt_template_hash=profile.template.content_hash,
    )
    return RunPlan(
        run_id=run_id,
        task_id=task_id,
        task=task,
        team="durability-rehearsal",
        team_version="1.0.0",
        stages=(stage,),
        budget=Budget(max_turns=max_turns, max_model_calls=max_turns * 2,
                      max_duration_seconds=deadline_seconds,
                      tool_wait_timeout_seconds=deadline_seconds),
    )


async def run_worker() -> int:
    configuration = settings()
    runtime_context.set_context(runtime_context.build_context(configuration))
    client = await Client.connect(configuration.temporal_target,
                                  namespace=configuration.namespace)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AgentRunWorkflow],
        activities=[
            record_event, set_run_state, start_stage, finish_stage, attach_model_call,
            create_tool_request, read_tool_result, cancel_pending_tool_requests,
            scripted_call_model,
        ],
        identity="iacode-durability-rehearsal",
    )
    print(json.dumps({"event": "worker-started", "taskQueue": TASK_QUEUE}), flush=True)
    async with worker:
        await asyncio.Event().wait()
    return 0


async def poller() -> int:
    """Ask Temporal whether this queue has a poller, rather than reading a log line.

    The worker prints that it started *before* it begins polling, so a scenario that waited for
    the log line could start a run against a queue nobody was watching yet. Asking the server is
    the observable fact, and it is the same question the worker's own healthcheck asks.
    """
    from temporalio.api.enums.v1 import TaskQueueType
    from temporalio.api.taskqueue.v1 import TaskQueue
    from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

    configuration = settings()
    client = await Client.connect(configuration.temporal_target,
                                  namespace=configuration.namespace)
    response = await client.workflow_service.describe_task_queue(
        DescribeTaskQueueRequest(
            namespace=configuration.namespace,
            task_queue=TaskQueue(name=TASK_QUEUE),
            task_queue_type=TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW))
    print(json.dumps({"taskQueue": TASK_QUEUE, "pollers": len(list(response.pollers))}),
          flush=True)
    return 0


async def create(*, looping: bool = False, deadline_seconds: int = 600) -> int:
    engine, factory = sessions()
    try:
        run_id, task_id = uuid7(), uuid7()
        async with factory() as session, session.begin():
            project = (await session.execute(
                select(Project).where(Project.slug == PROJECT_SLUG))).scalars().first()
            if project is None:
                project = Project(slug=PROJECT_SLUG, name="Durability rehearsal")
                session.add(project)
                await session.flush()
            agent = (await session.execute(
                select(Agent).where(Agent.slug == AGENT_SLUG))).scalars().first()
            if agent is None:
                session.add(Agent(slug=AGENT_SLUG, name="Rehearsal agent",
                                  role_contract="services/orchestrator/rehearsal/durability.py",
                                  enabled=True, role="rehearsal",
                                  allowed_actions=[TOOL_NAME]))
            instruction = (f"{LOOP_MARKER}: keep going." if looping
                           else "Ask for a tool, then finish.")
            task = Task(id=task_id, project_id=project.id, title="durability rehearsal",
                        description=instruction)
            session.add(task)
            session.add(TaskRun(id=run_id, task_id=task_id, status=str(RunState.CREATED),
                                attempt=1, team_slug="durability-rehearsal",
                                team_version="1.0.0",
                                budget=Budget(max_turns=50 if looping else 4,
                                              max_model_calls=100 if looping else 4,
                                              max_duration_seconds=deadline_seconds,
                                              tool_wait_timeout_seconds=deadline_seconds
                                              ).to_dict()))

        plan = plan_for(str(run_id), str(task_id), instruction,
                        deadline_seconds=deadline_seconds,
                        max_turns=50 if looping else 4)
        store = SqlAgentRunStore(factory)
        configuration = settings()
        client = await Client.connect(configuration.temporal_target,
                                      namespace=configuration.namespace)
        workflow_id = f"iacode-agent-run-{run_id}"
        await client.start_workflow(
            AGENT_RUN_WORKFLOW, plan.to_dict(), id=workflow_id, task_queue=TASK_QUEUE)
        await store.set_run_state(str(run_id), str(RunState.QUEUED), workflow_id=workflow_id)
        print(json.dumps({"runId": str(run_id), "workflowId": workflow_id}), flush=True)
        return 0
    finally:
        await engine.dispose()


async def state(run_id: str) -> int:
    engine, factory = sessions()
    try:
        store = SqlAgentRunStore(factory)
        record = await store.load_run(run_id)
        pending = await store.pending_tool_request(run_id)
        print(json.dumps({
            "runId": run_id,
            "state": record.state if record else None,
            "result": record.result if record else None,
            "errorType": record.error_type if record else None,
            "pendingToolRequest": pending.tool_request_id if pending else None,
            "pendingToolName": pending.name if pending else None,
        }), flush=True)
        return 0
    finally:
        await engine.dispose()


async def resolve(run_id: str) -> int:
    """Answer the pending tool request and tell the workflow, exactly as the API does."""
    engine, factory = sessions()
    try:
        store = SqlAgentRunStore(factory)
        pending = await store.pending_tool_request(run_id)
        if pending is None:
            print(json.dumps({"error": "no pending tool request"}), flush=True)
            return 1
        result = ToolResult(tool_request_id=pending.tool_request_id, status="SUCCEEDED",
                            output={"body": "the rehearsal supplied this"},
                            metadata={"by": "durability-rehearsal"})
        await store.resolve_tool_request(run_id, result, origin=TOOL_EXECUTOR_EXTERNAL)
        configuration = settings()
        client = await Client.connect(configuration.temporal_target,
                                      namespace=configuration.namespace)
        handle = client.get_workflow_handle(f"iacode-agent-run-{run_id}")
        await handle.signal(TOOL_RESULT_SIGNAL, result.to_dict())
        print(json.dumps({"resolved": pending.tool_request_id}), flush=True)
        return 0
    finally:
        await engine.dispose()


async def cancel(run_id: str) -> int:
    """Request cancellation exactly as the API does: record it, then tell the workflow."""
    engine, factory = sessions()
    try:
        store = SqlAgentRunStore(factory)
        await store.request_cancellation(run_id)
        configuration = settings()
        client = await Client.connect(configuration.temporal_target,
                                      namespace=configuration.namespace)
        handle = client.get_workflow_handle(f"iacode-agent-run-{run_id}")
        await handle.signal(CANCEL_SIGNAL, "rehearsal")
        print(json.dumps({"cancelled": run_id}), flush=True)
        return 0
    finally:
        await engine.dispose()


async def try_resolve(run_id: str) -> int:
    """Attempt to answer a tool request and report the refusal, if there is one.

    This is the shape a late or forged result takes: the run is over, and the store is what says
    so. It prints the refusal rather than raising, because the scenario asserts on the refusal.
    """
    engine, factory = sessions()
    try:
        store = SqlAgentRunStore(factory)
        requests = await store.list_tool_requests(run_id)
        if not requests:
            print(json.dumps({"accepted": False, "reason": "no tool request exists"}), flush=True)
            return 0
        result = ToolResult(tool_request_id=requests[-1].tool_request_id, status="SUCCEEDED",
                            output={"body": "too late"})
        try:
            await store.resolve_tool_request(run_id, result, origin=TOOL_EXECUTOR_EXTERNAL)
        except Exception as error:  # noqa: BLE001 - the refusal is the subject of the check
            print(json.dumps({"accepted": False, "reason": str(error),
                              "errorClass": type(error).__name__}), flush=True)
            return 0
        print(json.dumps({"accepted": True}), flush=True)
        return 0
    finally:
        await engine.dispose()


async def events(run_id: str) -> int:
    engine, factory = sessions()
    try:
        store = SqlAgentRunStore(factory)
        recorded = await store.read_events(run_id, limit=500)
        print(json.dumps([
            {"sequence": item.sequence, "type": item.type, "stage": item.stage}
            for item in recorded
        ]), flush=True)
        return 0
    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("worker", "poller", "create", "state", "resolve",
                                            "cancel", "try-resolve", "events"))
    parser.add_argument("--run", default=None)
    parser.add_argument("--looping", action="store_true",
                        help="create a run whose agent never finishes, for the deadline rehearsal")
    parser.add_argument("--deadline", type=int, default=600,
                        help="the run's wall-clock deadline, in seconds")
    arguments = parser.parse_args()

    if arguments.command == "worker":
        return asyncio.run(run_worker())
    if arguments.command == "poller":
        return asyncio.run(poller())
    if arguments.command == "create":
        return asyncio.run(create(looping=arguments.looping,
                                  deadline_seconds=arguments.deadline))
    if not arguments.run:
        parser.error("--run is required for this command")
    if arguments.command == "state":
        return asyncio.run(state(arguments.run))
    if arguments.command == "resolve":
        return asyncio.run(resolve(arguments.run))
    if arguments.command == "cancel":
        return asyncio.run(cancel(arguments.run))
    if arguments.command == "try-resolve":
        return asyncio.run(try_resolve(arguments.run))
    return asyncio.run(events(arguments.run))


if __name__ == "__main__":
    sys.exit(main())
