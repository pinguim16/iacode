"""The agent runtime's persistence, against the real PostgreSQL from the Compose stack.

What no unit test can prove: that the store enforces the state machine against a real row, that the
event sequence is assigned by the database and is unique per run, that a duplicated append and a
duplicated tool result are both idempotent because a constraint says so, and that a run's aggregate
usage is derived from ``model_calls`` rather than counted a second time.

Every test works inside its own project, task and run, and removes what it created. The catalog and
the run tables are operator-visible, and `.iacode/memory/lessons.jsonl` records a Gate where test
fixtures accumulated in them.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from iacode_agent_runtime.contracts import ToolResult
from iacode_agent_runtime.errors import AgentRuntimeError, ToolResultInvalidError
from iacode_agent_runtime.events import RunEvent
from iacode_agent_runtime.persistence import SqlAgentRunStore, bootstrap_registry
from iacode_agent_runtime.ports import StageCompletion
from iacode_agent_runtime.registry import AgentRegistry
from iacode_agent_runtime.states import RunState
from iacode_api.db import engine as db_engine
from iacode_persistence.models import (
    Agent,
    AgentRun,
    AgentTeam,
    ModelCall,
    Project,
    Task,
    TaskRun,
)
from sqlalchemy import delete, select

from tests.conftest import stack_is_configured, stack_settings

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(),
                       reason="the Foundation stack is not configured for this process"),
]

REPOSITORY_ROOT = Path("/app")


@pytest.fixture
async def session_factory() -> AsyncIterator:
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    try:
        yield db_engine.create_session_factory(engine)
    finally:
        await engine.dispose()


@pytest.fixture
async def run(session_factory) -> AsyncIterator[dict]:
    """A project, a task, a run and an agent, removed again whatever the test does."""
    slug = f"itest-{uuid.uuid4().hex[:10]}"
    async with session_factory() as session, session.begin():
        project = Project(slug=slug, name=slug)
        session.add(project)
        await session.flush()
        task = Task(project_id=project.id, title="integration task",
                    description="Say IACODE_AGENT_OK.")
        session.add(task)
        await session.flush()
        task_run = TaskRun(task_id=task.id, status=str(RunState.CREATED), attempt=1,
                           team_slug="single-agent", team_version="1.0.0",
                           budget={"maxTurns": 4})
        session.add(task_run)
        agent = Agent(slug=slug, name=slug, role_contract=f"agents/profiles/{slug}.json",
                      enabled=True)
        session.add(agent)
        await session.flush()
        context = {"project_id": project.id, "task_id": task.id,
                   "run_id": str(task_run.id), "agent": slug}
    try:
        yield context
    finally:
        async with session_factory() as session, session.begin():
            await session.execute(delete(Project).where(Project.id == context["project_id"]))
            await session.execute(delete(Agent).where(Agent.slug == slug))


@pytest.fixture
def store(session_factory) -> SqlAgentRunStore:
    return SqlAgentRunStore(session_factory)


# ---------------------------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------------------------


async def test_the_store_enforces_the_state_machine(store, run) -> None:
    run_id = run["run_id"]
    assert await store.set_run_state(run_id, str(RunState.QUEUED)) == "QUEUED"
    assert await store.set_run_state(run_id, str(RunState.RUNNING), started=True) == "RUNNING"

    with pytest.raises(AgentRuntimeError):
        await store.set_run_state(run_id, str(RunState.CREATED))


async def test_a_repeated_transition_is_a_no_op_rather_than_an_error(store, run) -> None:
    """A retried activity applies the state it already applied. That is not a failure."""
    run_id = run["run_id"]
    await store.set_run_state(run_id, str(RunState.QUEUED))
    await store.set_run_state(run_id, str(RunState.RUNNING))
    assert await store.set_run_state(run_id, str(RunState.RUNNING)) == "RUNNING"


async def test_a_terminal_run_is_never_resumed(store, run) -> None:
    run_id = run["run_id"]
    await store.set_run_state(run_id, str(RunState.QUEUED))
    await store.set_run_state(run_id, str(RunState.RUNNING))
    await store.set_run_state(run_id, str(RunState.SUCCEEDED), result="done", finished=True)

    with pytest.raises(AgentRuntimeError):
        await store.set_run_state(run_id, str(RunState.RUNNING))

    record = await store.load_run(run_id)
    assert record is not None and record.state == "SUCCEEDED"


async def test_run_state_is_not_held_in_process_memory(store, session_factory, run) -> None:
    """A second store object — a restarted API — reads the same run from the same row."""
    run_id = run["run_id"]
    await store.set_run_state(run_id, str(RunState.QUEUED))

    elsewhere = SqlAgentRunStore(session_factory)
    record = await elsewhere.load_run(run_id)

    assert record is not None
    assert record.state == "QUEUED"
    assert record.task == "Say IACODE_AGENT_OK."


# ---------------------------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------------------------


def event(run_id: str, key: str, event_type: str = "RUN_NOTE", **payload) -> RunEvent:
    return RunEvent(run_id=run_id, type=event_type, dedupe_key=key,
                    payload=payload or {"note": key})


async def test_event_sequence_is_monotonic_per_run(store, run) -> None:
    run_id = run["run_id"]
    sequences = [
        (await store.append_event(event(run_id, f"key-{index}"))).sequence
        for index in range(5)
    ]
    assert sequences == [1, 2, 3, 4, 5]

    read = await store.read_events(run_id)
    assert [item.sequence for item in read] == [1, 2, 3, 4, 5]


async def test_duplicate_append_does_not_duplicate_the_event(store, run) -> None:
    run_id = run["run_id"]
    first = await store.append_event(event(run_id, "run-started", "RUN_STARTED"))
    second = await store.append_event(event(run_id, "run-started", "RUN_STARTED"))

    assert first.sequence == second.sequence
    assert len(await store.read_events(run_id)) == 1


async def test_event_correction_is_a_new_event(store, run) -> None:
    """A stored event is never rewritten. A correction is a later event."""
    run_id = run["run_id"]
    await store.append_event(event(run_id, "note-1", note="first reading"))
    await store.append_event(event(run_id, "note-2", note="corrected reading"))

    events = await store.read_events(run_id)
    assert [item.payload["note"] for item in events] == ["first reading", "corrected reading"]
    assert events[0].sequence < events[1].sequence


async def test_reading_events_after_a_cursor_returns_only_what_follows(store, run) -> None:
    run_id = run["run_id"]
    for index in range(4):
        await store.append_event(event(run_id, f"key-{index}"))

    assert [item.sequence for item in await store.read_events(run_id, after=2)] == [3, 4]
    assert await store.read_events(run_id, after=4) == []


async def test_two_runs_keep_their_own_sequences(store, session_factory, run) -> None:
    """Sequence is per run. Two runs at once must not interleave one counter."""
    async with session_factory() as session, session.begin():
        second = TaskRun(task_id=run["task_id"], status=str(RunState.CREATED), attempt=2)
        session.add(second)
        await session.flush()
        second_id = str(second.id)

    await store.append_event(event(run["run_id"], "a"))
    await store.append_event(event(second_id, "a"))
    await store.append_event(event(second_id, "b"))

    assert [item.sequence for item in await store.read_events(run["run_id"])] == [1]
    assert [item.sequence for item in await store.read_events(second_id)] == [1, 2]


# ---------------------------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------------------------


async def start_stage(store, run) -> str:
    record = await store.start_stage(
        run["run_id"], stage_index=0, stage_name="answer", agent=run["agent"],
        profile_version="1.0.0", prompt_template_version="v1",
        prompt_template_hash="0" * 64, output_name="answer")
    return record.agent_run_id


async def test_a_tool_request_is_persisted_and_found_as_pending(store, run) -> None:
    agent_run_id = await start_stage(store, run)
    identifier = str(uuid.uuid4())

    request = await store.create_tool_request(
        run["run_id"], agent_run_id=agent_run_id, name="repo.read",
        arguments={"path": "README.md"}, tool_request_id=identifier)

    assert request.status == "PENDING"
    pending = await store.pending_tool_request(run["run_id"])
    assert pending is not None and pending.tool_request_id == identifier
    assert pending.arguments == {"path": "README.md"}


async def test_creating_the_same_tool_request_twice_creates_one(store, run) -> None:
    agent_run_id = await start_stage(store, run)
    identifier = str(uuid.uuid4())
    for _ in range(2):
        await store.create_tool_request(
            run["run_id"], agent_run_id=agent_run_id, name="repo.read",
            arguments={}, tool_request_id=identifier)

    assert len(await store.list_tool_requests(run["run_id"])) == 1


async def test_duplicate_tool_result_is_idempotent(store, run) -> None:
    agent_run_id = await start_stage(store, run)
    identifier = str(uuid.uuid4())
    await store.create_tool_request(run["run_id"], agent_run_id=agent_run_id,
                                    name="repo.read", arguments={},
                                    tool_request_id=identifier)
    result = ToolResult(tool_request_id=identifier, status="SUCCEEDED", output={"body": "hello"})

    first = await store.resolve_tool_request(run["run_id"], result)
    second = await store.resolve_tool_request(run["run_id"], result)

    assert first.output == second.output == {"body": "hello"}
    requests = await store.list_tool_requests(run["run_id"])
    assert len(requests) == 1 and requests[0].status == "RESOLVED"


async def test_tool_result_for_another_run_is_refused(store, session_factory, run) -> None:
    agent_run_id = await start_stage(store, run)
    identifier = str(uuid.uuid4())
    await store.create_tool_request(run["run_id"], agent_run_id=agent_run_id,
                                    name="repo.read", arguments={},
                                    tool_request_id=identifier)
    async with session_factory() as session, session.begin():
        other = TaskRun(task_id=run["task_id"], status=str(RunState.RUNNING), attempt=3)
        session.add(other)
        await session.flush()
        other_id = str(other.id)

    with pytest.raises(ToolResultInvalidError):
        await store.resolve_tool_request(
            other_id, ToolResult(tool_request_id=identifier, status="SUCCEEDED"))


async def test_a_tool_result_for_an_unknown_request_is_refused(store, run) -> None:
    with pytest.raises(ToolResultInvalidError):
        await store.resolve_tool_request(
            run["run_id"],
            ToolResult(tool_request_id=str(uuid.uuid4()), status="SUCCEEDED"))


async def test_tool_result_after_a_terminal_state_is_refused(store, run) -> None:
    agent_run_id = await start_stage(store, run)
    identifier = str(uuid.uuid4())
    await store.create_tool_request(run["run_id"], agent_run_id=agent_run_id,
                                    name="repo.read", arguments={},
                                    tool_request_id=identifier)
    await store.set_run_state(run["run_id"], str(RunState.QUEUED))
    await store.set_run_state(run["run_id"], str(RunState.RUNNING))
    await store.set_run_state(run["run_id"], str(RunState.CANCELLED), finished=True)

    with pytest.raises(ToolResultInvalidError):
        await store.resolve_tool_request(
            run["run_id"], ToolResult(tool_request_id=identifier, status="SUCCEEDED"))


async def test_cancelling_a_run_closes_the_requests_nobody_will_answer(store, run) -> None:
    agent_run_id = await start_stage(store, run)
    await store.create_tool_request(run["run_id"], agent_run_id=agent_run_id,
                                    name="repo.read", arguments={},
                                    tool_request_id=str(uuid.uuid4()))

    assert await store.cancel_pending_tool_requests(run["run_id"]) == 1
    assert await store.pending_tool_request(run["run_id"]) is None


async def test_a_tool_request_carries_at_most_one_result(store, session_factory, run) -> None:
    """The constraint is the mechanism, so a second writer cannot make it two."""
    from iacode_persistence.models import ToolResult as ToolResultRow
    from sqlalchemy.exc import IntegrityError

    agent_run_id = await start_stage(store, run)
    identifier = str(uuid.uuid4())
    await store.create_tool_request(run["run_id"], agent_run_id=agent_run_id,
                                    name="repo.read", arguments={},
                                    tool_request_id=identifier)
    await store.resolve_tool_request(
        run["run_id"], ToolResult(tool_request_id=identifier, status="SUCCEEDED"))

    with pytest.raises(IntegrityError):
        async with session_factory() as session, session.begin():
            session.add(ToolResultRow(tool_request_id=uuid.UUID(identifier), status="FAILED"))


# ---------------------------------------------------------------------------------------------
# Stages, model calls and rights
# ---------------------------------------------------------------------------------------------


async def test_starting_the_same_stage_twice_reopens_one_agent_run(store, run) -> None:
    first = await start_stage(store, run)
    second = await start_stage(store, run)
    assert first == second


async def test_a_stage_records_what_produced_it(store, session_factory, run) -> None:
    agent_run_id = await start_stage(store, run)
    await store.finish_stage(agent_run_id, StageCompletion(
        state=str(RunState.SUCCEEDED), output="the answer", output_summary="answered",
        turns=2, model_calls=3))

    async with session_factory() as session:
        row = await session.get(AgentRun, uuid.UUID(agent_run_id))
        assert row is not None
        assert row.status == "SUCCEEDED"
        assert row.profile_version == "1.0.0"
        assert row.prompt_template_version == "v1"
        assert len(row.prompt_template_hash) == 64
        assert row.turns == 2 and row.model_calls == 3
        assert row.output_summary == "answered"


async def test_agent_run_records_profile_and_template_version(store, session_factory,
                                                              run) -> None:
    agent_run_id = await start_stage(store, run)
    async with session_factory() as session:
        row = await session.get(AgentRun, uuid.UUID(agent_run_id))
    assert row is not None
    assert (row.profile_version, row.prompt_template_version) == ("1.0.0", "v1")


async def test_model_call_is_attributed_to_its_agent_run(store, session_factory, run) -> None:
    agent_run_id = await start_stage(store, run)
    request_id = f"gwr-{uuid.uuid4().hex[:12]}"
    async with session_factory() as session, session.begin():
        session.add(ModelCall(request_id=request_id, purpose="agent-turn", status="SUCCEEDED",
                              succeeded=True, input_tokens=10, output_tokens=4))

    model_call_id = await store.attach_model_call(agent_run_id, request_id)

    assert model_call_id is not None
    async with session_factory() as session:
        row = (await session.execute(
            select(ModelCall).where(ModelCall.request_id == request_id))).scalars().one()
        assert str(row.agent_run_id) == agent_run_id
        await session.execute(delete(ModelCall).where(ModelCall.request_id == request_id))
        await session.commit()


async def test_attaching_a_call_the_gateway_never_recorded_is_not_an_error(store, run) -> None:
    agent_run_id = await start_stage(store, run)
    assert await store.attach_model_call(agent_run_id, "gwr-nothing-here") is None


async def test_agent_run_usage_is_derived_from_model_calls(session_factory, store, run) -> None:
    """There is no aggregate usage column: a second count would eventually disagree."""
    columns = set(AgentRun.__table__.columns.keys())
    for forbidden in ("input_tokens", "output_tokens", "total_tokens", "cost"):
        assert forbidden not in columns, f"agent_runs keeps its own {forbidden}"
    assert "agent_run_id" in ModelCall.__table__.columns


async def test_no_raw_provider_prompt_is_persisted(session_factory) -> None:
    """``model_calls`` has nowhere to put one, and the run keeps the task rather than a prompt."""
    call_columns = set(ModelCall.__table__.columns.keys())
    for forbidden in ("prompt", "messages", "completion", "content", "response", "raw_request"):
        assert forbidden not in call_columns

    run_columns = set(TaskRun.__table__.columns.keys())
    for forbidden in ("prompt", "messages", "completion", "raw_request", "system_prompt"):
        assert forbidden not in run_columns
    # What the run does keep is its own instruction and its own answer, which is what lets the
    # workflow resume and the page render after a restart.
    assert "result" in run_columns
    assert "description" in set(Task.__table__.columns.keys())


async def test_nothing_this_gate_persists_is_training_eligible(session_factory, run) -> None:
    async with session_factory() as session:
        row = await session.get(TaskRun, uuid.UUID(run["run_id"]))
    assert row is not None
    assert row.training_allowed is False
    assert TaskRun.__table__.columns["training_allowed"].server_default.arg == "false"


# ---------------------------------------------------------------------------------------------
# The registry bootstrap
# ---------------------------------------------------------------------------------------------


@pytest.fixture
async def clean_registry(session_factory) -> AsyncIterator[AgentRegistry]:
    registry = AgentRegistry(REPOSITORY_ROOT)
    declared = [record.agent for record in registry.agent_records()]
    teams = [record.team for record in registry.team_records()]

    async def remove() -> None:
        async with session_factory() as session, session.begin():
            await session.execute(delete(AgentRun).where(
                AgentRun.agent_id.in_(select(Agent.id).where(Agent.slug.in_(declared)))))
            await session.execute(delete(Agent).where(Agent.slug.in_(declared)))
            await session.execute(delete(AgentTeam).where(AgentTeam.slug.in_(teams)))

    await remove()
    try:
        yield registry
    finally:
        await remove()


async def test_profile_bootstrap_is_idempotent(session_factory, clean_registry) -> None:
    first = await bootstrap_registry(session_factory, clean_registry)
    second = await bootstrap_registry(session_factory, clean_registry)

    # Counted from the registry rather than written down: GATE 3 declares two more roles and one
    # more team, and a literal would have failed it for adding them (`LSN-0037`).
    agents, teams = len(clean_registry.agents()), len(clean_registry.teams())
    assert agents >= 4 and teams >= 2
    assert first.agents_created == agents
    assert first.teams_created == teams
    assert second.changed is False
    assert second.agents_unchanged == agents
    assert second.teams_unchanged == teams


async def test_bootstrap_does_not_overwrite_a_customised_profile(session_factory,
                                                                 clean_registry) -> None:
    """An operator who edited a row did so on purpose. A start-up does not revert it."""
    await bootstrap_registry(session_factory, clean_registry)

    async with session_factory() as session, session.begin():
        row = (await session.execute(
            select(Agent).where(Agent.slug == "planner"))).scalars().one()
        row.customised = True
        row.max_turns = 99
        row.definition_hash = "deliberately-different"

    outcome = await bootstrap_registry(session_factory, clean_registry)

    assert outcome.agents_customised == 1
    assert outcome.agents_updated == 0
    async with session_factory() as session:
        row = (await session.execute(
            select(Agent).where(Agent.slug == "planner"))).scalars().one()
        assert row.max_turns == 99, "the bootstrap reverted an operator's edit"


async def test_the_bootstrap_records_the_declared_configuration(session_factory,
                                                                clean_registry) -> None:
    await bootstrap_registry(session_factory, clean_registry)

    async with session_factory() as session:
        row = (await session.execute(
            select(Agent).where(Agent.slug == "generalist"))).scalars().one()
        team = (await session.execute(
            select(AgentTeam).where(AgentTeam.slug == "planner-reviewer"))).scalars().one()

    assert row.role == "generalist"
    assert row.profile_version == "1.0.0"
    assert row.prompt_template == "agents/prompts/generalist.v1.md"
    assert len(row.prompt_template_hash) == 64
    assert row.allowed_actions == [], "no builtin profile is given a tool in this Gate"
    assert [stage["agent"] for stage in team.stages] == ["planner", "reviewer"]


# ---------------------------------------------------------------------------------------------
# Creating runs: idempotency, isolation and the frozen plan
# ---------------------------------------------------------------------------------------------


@pytest.fixture
async def service(session_factory):
    """The real service, over the real database and the declared profiles."""
    from iacode_agent_runtime.budgets import Budget
    from iacode_agent_runtime.limits import RuntimeLimits
    from iacode_agent_runtime.service import AgentRuntimeService

    created: list[str] = []
    instance = AgentRuntimeService(
        session_factory=session_factory,
        registry=AgentRegistry(REPOSITORY_ROOT),
        store=SqlAgentRunStore(session_factory),
        default_budget=Budget(max_turns=2, max_model_calls=2, max_duration_seconds=60,
                              tool_wait_timeout_seconds=30),
        limits=RuntimeLimits(max_task_bytes=2048),
    )
    instance.created_run_ids = created  # type: ignore[attr-defined]
    try:
        yield instance
    finally:
        # The runs a test created are removed: `task_runs` is operator-visible, and
        # `.iacode/memory/lessons.jsonl` records a Gate where fixtures accumulated in a table an
        # operator reads.
        async with session_factory() as session, session.begin():
            for run_id in created:
                row = await session.get(TaskRun, uuid.UUID(run_id))
                if row is not None:
                    await session.execute(delete(Task).where(Task.id == row.task_id))


def creation(**overrides):
    from iacode_contracts.agent_runtime import CreateAgentRunRequest

    values = {"task": "Reply with exactly: IACODE_AGENT_OK", "team": "single-agent"}
    values.update(overrides)
    return CreateAgentRunRequest(**values)


async def test_same_idempotency_key_returns_the_same_run(service) -> None:
    key = f"itest-{uuid.uuid4().hex[:12]}"

    _plan, first = await service.create_run(creation(idempotencyKey=key))
    service.created_run_ids.append(first.runId)
    _plan, second = await service.create_run(creation(idempotencyKey=key))

    assert second.runId == first.runId
    assert second.idempotentReplay is True
    assert first.idempotentReplay is False


async def test_a_different_key_creates_a_new_run(service) -> None:
    first_key = f"itest-{uuid.uuid4().hex[:12]}"
    second_key = f"itest-{uuid.uuid4().hex[:12]}"

    _plan, first = await service.create_run(creation(idempotencyKey=first_key))
    _plan, second = await service.create_run(creation(idempotencyKey=second_key))
    service.created_run_ids += [first.runId, second.runId]

    assert first.runId != second.runId
    assert second.idempotentReplay is False


async def test_a_creation_without_a_key_always_creates_a_run(service) -> None:
    _plan, first = await service.create_run(creation())
    _plan, second = await service.create_run(creation())
    service.created_run_ids += [first.runId, second.runId]

    assert first.runId != second.runId


async def test_one_task_can_have_two_independent_runs(service, session_factory) -> None:
    """Two runs of the same instruction keep their own state, events and results."""
    _plan, first = await service.create_run(creation(task="the same instruction"))
    _plan, second = await service.create_run(creation(task="the same instruction"))
    service.created_run_ids += [first.runId, second.runId]

    await service.store.set_run_state(first.runId, "QUEUED")
    await service.store.set_run_state(first.runId, "RUNNING")
    await service.store.set_run_state(first.runId, "SUCCEEDED", result="the first answer",
                                      finished=True)
    await service.store.append_event(event(second.runId, "only-the-second"))

    first_detail = await service.detail(first.runId)
    second_detail = await service.detail(second.runId)

    assert first_detail.state == "SUCCEEDED"
    assert second_detail.state == "CREATED"
    assert first_detail.result == "the first answer"
    assert second_detail.result is None
    assert (await service.events(first.runId)).total == 1, "only its own RUN_CREATED"
    assert [item.type for item in (await service.events(second.runId)).events] == [
        "RUN_CREATED", "RUN_NOTE"]


async def test_the_plan_is_frozen_at_creation(service) -> None:
    """Every profile version and prompt hash is resolved once, into the plan the workflow gets."""
    plan, created = await service.create_run(creation(team="planner-reviewer"))
    service.created_run_ids.append(created.runId)

    assert [stage.agent for stage in plan.stages] == ["planner", "reviewer"]
    for stage in plan.stages:
        assert stage.profile_version
        assert len(stage.prompt_template_hash) == 64
        assert stage.role_instructions.strip()
        assert stage.allowed_actions == (), "a shipped profile is given no tool in this Gate"
    assert plan.task == "Reply with exactly: IACODE_AGENT_OK"


async def test_an_unknown_team_is_refused_before_a_run_exists(service, session_factory) -> None:
    from iacode_agent_runtime.errors import AgentRuntimeErrorType

    before = await service.list_runs(limit=100)
    with pytest.raises(AgentRuntimeError) as raised:
        await service.create_run(creation(team="nobody"))

    assert raised.value.error_type is AgentRuntimeErrorType.TEAM_NOT_FOUND
    assert len(await service.list_runs(limit=100)) == len(before)


async def test_an_oversized_task_is_refused_before_a_run_exists(service) -> None:
    from iacode_agent_runtime.errors import AgentRuntimeErrorType

    before = await service.list_runs(limit=100)
    with pytest.raises(AgentRuntimeError) as raised:
        await service.create_run(creation(task="x" * 5000))

    assert raised.value.error_type is AgentRuntimeErrorType.PAYLOAD_TOO_LARGE
    assert len(await service.list_runs(limit=100)) == len(before)


async def test_a_run_reports_its_budget_and_an_unknown_cost(service) -> None:
    _plan, created = await service.create_run(creation())
    service.created_run_ids.append(created.runId)

    detail = await service.detail(created.runId)

    assert detail.budget.maxTurns == 2
    assert detail.budget.maxModelCalls == 2
    assert detail.summary.costKnown is False
    assert detail.summary.cost is None, "an unknown cost is unknown, never zero"
    assert detail.trainingAllowed is False
