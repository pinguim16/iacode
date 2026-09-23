"""The SQL implementation of the runtime's ports.

The runtime declares what it needs — :class:`~iacode_agent_runtime.ports.AgentRunStore` — and this
module is the answer in SQLAlchemy, over the shared schema in ``packages/persistence``. Both the API
process and the Temporal worker use it, which is the whole reason the schema is a shared package
rather than a module inside the web application.

Three things this module is responsible for, and each one is a rule that cannot be left to the
caller.

**The state machine is enforced here.** ``set_run_state`` asks
:func:`~iacode_agent_runtime.states.assert_transition` before it writes, because the caller is
sometimes a retried activity acting on state it read a minute ago. A move to the state the run is
already in is a no-op rather than an error — that is what a retry looks like — and a move out of a
terminal state is refused, which is what a late signal looks like.

**An event is appended once.** The sequence is assigned inside the transaction from the current
maximum, and ``dedupe_key`` is unique per run, so an activity Temporal ran twice produces one event
and the second append returns the first one.

**A tool result resolves a request once.** The uniqueness constraint on ``tool_request_id`` is the
mechanism; this module turns the second delivery into the same answer instead of an error, because
a redelivered signal is normal and a caller should not have to tell the difference.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from iacode_common.identifiers import uuid7
from iacode_contracts.agent_runtime import (
    TOOL_EXECUTOR_EXTERNAL,
    TOOL_REQUEST_EXECUTORS,
)
from iacode_persistence.models import (
    Agent,
    AgentRun,
    AgentTeam,
    ModelCall,
    Task,
    TaskRun,
)
from iacode_persistence.models import (
    RunEvent as RunEventRow,
)
from iacode_persistence.models import (
    ToolRequest as ToolRequestRow,
)
from iacode_persistence.models import (
    ToolResult as ToolResultRow,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from iacode_agent_runtime.contracts import StagePlan, ToolRequest, ToolResult
from iacode_agent_runtime.errors import (
    AgentRuntimeError,
    AgentRuntimeErrorType,
    ToolResultInvalidError,
    ToolResultOriginRefusedError,
)
from iacode_agent_runtime.events import RunEvent
from iacode_agent_runtime.ports import AgentRunRecord, RunRecord, StageCompletion
from iacode_agent_runtime.registry import AgentRegistry, BootstrapOutcome
from iacode_agent_runtime.states import RunState, assert_transition, is_terminal

__all__ = ["SqlAgentRunStore", "bootstrap_registry"]


def _uuid(value: str, *, what: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as error:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{what} is not a valid identifier",
            details={"what": what}) from error


class SqlAgentRunStore:
    """Runs, stages, events and tool interactions, in PostgreSQL.

    Each operation opens a short session of its own rather than borrowing one. An activity outlives
    the HTTP request that started the run, and a store bound to a request's unit of work would be
    writing into a session closed under it — the same reason the gateway's store works this way.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    # -- reading -------------------------------------------------------------------------------

    async def load_run(self, run_id: str) -> RunRecord | None:
        async with self._sessions() as session:
            row = await self._run_row(session, run_id)
            if row is None:
                return None
            task = await session.get(Task, row.task_id)
            return RunRecord(
                run_id=str(row.id),
                task_id=str(row.task_id),
                state=row.status,
                team=row.team_slug or "",
                task=(task.description or "") if task else "",
                workflow_id=row.workflow_id,
                current_stage=row.current_stage,
                cancel_requested=row.cancel_requested,
                budget=dict(row.budget or {}),
                budget_used=dict(row.budget_used or {}),
                result=row.result,
                error_type=row.error_type,
                created_at=row.created_at,
            )

    async def read_events(self, run_id: str, *, after: int = 0,
                          limit: int = 500) -> list[RunEvent]:
        async with self._sessions() as session:
            statement = (
                select(RunEventRow)
                .where(RunEventRow.task_run_id == _uuid(run_id, what="the run identifier"),
                       RunEventRow.sequence > after)
                .order_by(RunEventRow.sequence)
                .limit(limit)
            )
            rows = (await session.execute(statement)).scalars().all()
            return [_event_from_row(row, run_id) for row in rows]

    # -- state ---------------------------------------------------------------------------------

    async def set_run_state(
        self,
        run_id: str,
        state: str,
        *,
        current_stage: str | None = None,
        budget_used: dict[str, Any] | None = None,
        result: str | None = None,
        result_summary: str | None = None,
        error_type: str | None = None,
        error_summary: str | None = None,
        failed_stage: str | None = None,
        workflow_id: str | None = None,
        started: bool = False,
        finished: bool = False,
    ) -> str:
        async with self._sessions() as session, session.begin():
            row = await self._run_row(session, run_id, required=True)
            assert row is not None
            if row.status != state:
                assert_transition(row.status, state)
                row.status = state
            if current_stage is not None:
                row.current_stage = current_stage
            if budget_used is not None:
                row.budget_used = dict(budget_used)
            if result is not None:
                row.result = result
            if result_summary is not None:
                row.result_summary = result_summary
            if error_type is not None:
                row.error_type = error_type
            if error_summary is not None:
                row.error_summary = error_summary
            if failed_stage is not None:
                row.failed_stage = failed_stage
            if workflow_id is not None:
                row.workflow_id = workflow_id
            if started and row.started_at is None:
                row.started_at = datetime.now(UTC)
            if finished:
                row.finished_at = datetime.now(UTC)
                task = await session.get(Task, row.task_id)
                if task is not None:
                    task.status = state if state in ("SUCCEEDED", "FAILED", "CANCELLED") \
                        else task.status
            return row.status

    async def request_cancellation(self, run_id: str) -> RunRecord:
        """Mark a run as cancelled-by-request. The workflow performs the actual stop."""
        async with self._sessions() as session, session.begin():
            row = await self._run_row(session, run_id, required=True)
            assert row is not None
            if is_terminal(row.status):
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INVALID_STATE_TRANSITION,
                    f"run {run_id} is already {row.status} and cannot be cancelled",
                    details={"state": row.status})
            row.cancel_requested = True
        record = await self.load_run(run_id)
        assert record is not None
        return record

    # -- events --------------------------------------------------------------------------------

    async def append_event(self, event: RunEvent) -> RunEvent:
        run_uuid = _uuid(event.run_id, what="the run identifier")
        async with self._sessions() as session:
            existing = (await session.execute(
                select(RunEventRow).where(
                    RunEventRow.task_run_id == run_uuid,
                    RunEventRow.dedupe_key == event.dedupe_key))).scalars().first()
            if existing is not None:
                return _event_from_row(existing, event.run_id)
        try:
            async with self._sessions() as session, session.begin():
                highest = (await session.execute(
                    select(func.coalesce(func.max(RunEventRow.sequence), 0)).where(
                        RunEventRow.task_run_id == run_uuid))).scalar_one()
                row = RunEventRow(
                    task_run_id=run_uuid,
                    agent_run_id=(_uuid(event.agent_run_id, what="the agent run identifier")
                                  if event.agent_run_id else None),
                    sequence=int(highest) + 1,
                    event_type=event.type,
                    stage=event.stage,
                    dedupe_key=event.dedupe_key,
                    payload=dict(event.payload),
                )
                session.add(row)
            async with self._sessions() as session:
                stored = (await session.execute(
                    select(RunEventRow).where(
                        RunEventRow.task_run_id == run_uuid,
                        RunEventRow.dedupe_key == event.dedupe_key))).scalars().one()
                return _event_from_row(stored, event.run_id)
        except IntegrityError:
            # Two writers raced for the same sequence or the same occurrence. Either way the event
            # exists now, and returning it is the idempotent answer.
            async with self._sessions() as session:
                stored = (await session.execute(
                    select(RunEventRow).where(
                        RunEventRow.task_run_id == run_uuid,
                        RunEventRow.dedupe_key == event.dedupe_key))).scalars().first()
            if stored is None:
                raise
            return _event_from_row(stored, event.run_id)

    # -- stages --------------------------------------------------------------------------------

    async def start_stage(self, run_id: str, *, stage_index: int, stage_name: str,
                          agent: str, profile_version: str, prompt_template_version: str,
                          prompt_template_hash: str, output_name: str) -> AgentRunRecord:
        run_uuid = _uuid(run_id, what="the run identifier")
        async with self._sessions() as session, session.begin():
            agent_row = (await session.execute(
                select(Agent).where(Agent.slug == agent))).scalars().first()
            if agent_row is None:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.PROFILE_NOT_FOUND,
                    f"agent {agent!r} is not registered",
                    details={"agent": agent})
            existing = (await session.execute(
                select(AgentRun).where(AgentRun.task_run_id == run_uuid,
                                       AgentRun.stage_index == stage_index))).scalars().first()
            if existing is None:
                existing = AgentRun(
                    task_run_id=run_uuid,
                    agent_id=agent_row.id,
                    stage_index=stage_index,
                )
                session.add(existing)
            existing.status = str(RunState.RUNNING)
            existing.stage_name = stage_name
            existing.agent_slug = agent
            existing.profile_version = profile_version
            existing.prompt_template_version = prompt_template_version
            existing.prompt_template_hash = prompt_template_hash
            existing.output_name = output_name
            if existing.started_at is None:
                existing.started_at = datetime.now(UTC)
            await session.flush()
            return AgentRunRecord(
                agent_run_id=str(existing.id),
                run_id=run_id,
                stage_index=stage_index,
                stage_name=stage_name,
                agent=agent,
                state=existing.status,
            )

    async def finish_stage(self, agent_run_id: str, completion: StageCompletion) -> None:
        async with self._sessions() as session, session.begin():
            row = await session.get(AgentRun, _uuid(agent_run_id,
                                                    what="the agent run identifier"))
            if row is None:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                    "the agent run this stage claims to be does not exist",
                    details={"agentRunId": agent_run_id})
            if row.status != completion.state:
                assert_transition(row.status, completion.state)
                row.status = completion.state
            row.output = completion.output or row.output
            row.output_summary = completion.output_summary or row.output_summary
            row.turns = completion.turns
            row.model_calls = completion.model_calls
            row.error_type = completion.error_type
            row.error_summary = completion.error_summary
            row.finished_at = datetime.now(UTC)

    async def attach_model_call(self, agent_run_id: str,
                                gateway_request_id: str) -> str | None:
        """Link the gateway's record of a call to the agent run that caused it.

        The gateway owns the row: it recorded what the call cost, how long it took and which model
        served it. The runtime adds the attribution and nothing else, so aggregate usage stays
        derivable from one authoritative source instead of counted twice.
        """
        if not gateway_request_id:
            return None
        async with self._sessions() as session, session.begin():
            row = (await session.execute(
                select(ModelCall).where(
                    ModelCall.request_id == gateway_request_id))).scalars().first()
            if row is None:
                return None
            row.agent_run_id = _uuid(agent_run_id, what="the agent run identifier")
            return str(row.id)

    # -- tools ---------------------------------------------------------------------------------

    async def create_tool_request(self, run_id: str, *, agent_run_id: str | None, name: str,
                                  arguments: dict[str, Any], tool_request_id: str,
                                  executor: str = TOOL_EXECUTOR_EXTERNAL) -> ToolRequest:
        if executor not in TOOL_REQUEST_EXECUTORS:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                f"{executor!r} is not a tool request executor",
                details={"executor": executor})
        request_uuid = _uuid(tool_request_id, what="the tool request identifier")
        async with self._sessions() as session, session.begin():
            existing = await session.get(ToolRequestRow, request_uuid)
            if existing is None:
                existing = ToolRequestRow(
                    id=request_uuid,
                    task_run_id=_uuid(run_id, what="the run identifier"),
                    agent_run_id=(_uuid(agent_run_id, what="the agent run identifier")
                                  if agent_run_id else None),
                    tool_name=name,
                    arguments=dict(arguments),
                    status="PENDING",
                    executor=executor,
                )
                session.add(existing)
                await session.flush()
            return _tool_request_from_row(existing, run_id)

    async def pending_tool_request(self, run_id: str) -> ToolRequest | None:
        async with self._sessions() as session:
            row = (await session.execute(
                select(ToolRequestRow)
                .where(ToolRequestRow.task_run_id == _uuid(run_id, what="the run identifier"),
                       ToolRequestRow.status == "PENDING")
                .order_by(ToolRequestRow.created_at.desc()))).scalars().first()
            return _tool_request_from_row(row, run_id) if row else None

    async def list_tool_requests(self, run_id: str) -> list[ToolRequest]:
        async with self._sessions() as session:
            rows = (await session.execute(
                select(ToolRequestRow)
                .where(ToolRequestRow.task_run_id == _uuid(run_id, what="the run identifier"))
                .order_by(ToolRequestRow.created_at))).scalars().all()
            return [_tool_request_from_row(row, run_id) for row in rows]

    async def resolve_tool_request(self, run_id: str, result: ToolResult, *,
                                   origin: str) -> ToolResult:
        """Record the answer to a tool request, refusing every shape that is not this run's.

        The five refusals are deliberate and each has a test: a request that does not exist, a
        request belonging to another run, a result from something other than the executor that
        owns the request, a request that is no longer pending, and a run that has already
        finished. The same result delivered twice by the owning executor is not a refusal, it is
        the idempotent answer.

        The ownership check comes before the idempotent answer and before the terminal check
        (`M1-F-002`). The first version stored whatever result arrived first for any pending
        request and answered every later delivery with it, so a result posted to the API while
        the sandbox ran became what the agent received, and the sandbox's own was discarded. A
        result from the wrong origin is now refused whenever it arrives, and it never learns what
        the stored result says.
        """
        if origin not in TOOL_REQUEST_EXECUTORS:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                f"{origin!r} is not a tool result origin", details={"executor": origin})
        request_uuid = _uuid(result.tool_request_id, what="the tool request identifier")
        run_uuid = _uuid(run_id, what="the run identifier")
        async with self._sessions() as session, session.begin():
            run = await self._run_row(session, run_id, required=True)
            assert run is not None
            row = await session.get(ToolRequestRow, request_uuid)
            if row is None:
                raise ToolResultInvalidError(
                    "no tool request with that identifier exists",
                    details={"toolRequestId": result.tool_request_id})
            if row.task_run_id != run_uuid:
                raise ToolResultInvalidError(
                    "that tool request belongs to a different run",
                    details={"toolRequestId": result.tool_request_id, "runId": run_id})
            if row.executor != origin:
                raise ToolResultOriginRefusedError(
                    f"tool request {result.tool_request_id} is answered by its {row.executor} "
                    f"executor; a result from {origin} is not accepted for it",
                    details={"toolRequestId": result.tool_request_id,
                             "executor": row.executor})
            if is_terminal(run.status):
                raise ToolResultInvalidError(
                    f"run {run_id} is already {run.status}; a tool result cannot be accepted",
                    details={"state": run.status})

            stored = (await session.execute(
                select(ToolResultRow).where(
                    ToolResultRow.tool_request_id == request_uuid))).scalars().first()
            if stored is not None:
                return ToolResult(
                    tool_request_id=result.tool_request_id,
                    status=stored.status,
                    output=dict(stored.output or {}),
                    error=stored.error,
                    metadata={str(k): str(v) for k, v in (stored.result_metadata or {}).items()},
                )
            if row.status != "PENDING":
                raise ToolResultInvalidError(
                    f"tool request {result.tool_request_id} is {row.status}, not PENDING",
                    details={"status": row.status})

            session.add(ToolResultRow(
                tool_request_id=request_uuid,
                status=result.status,
                output=dict(result.output),
                error=result.error,
                result_metadata=dict(result.metadata),
            ))
            row.status = "RESOLVED"
            row.resolved_at = datetime.now(UTC)
            return result

    async def cancel_pending_tool_requests(self, run_id: str) -> int:
        async with self._sessions() as session, session.begin():
            rows = (await session.execute(
                select(ToolRequestRow).where(
                    ToolRequestRow.task_run_id == _uuid(run_id, what="the run identifier"),
                    ToolRequestRow.status == "PENDING"))).scalars().all()
            for row in rows:
                row.status = "CANCELLED"
                row.resolved_at = datetime.now(UTC)
            return len(rows)

    async def tool_result_for(self, tool_request_id: str) -> ToolResult | None:
        async with self._sessions() as session:
            row = (await session.execute(
                select(ToolResultRow).where(
                    ToolResultRow.tool_request_id == _uuid(
                        tool_request_id, what="the tool request identifier")))).scalars().first()
            if row is None:
                return None
            return ToolResult(
                tool_request_id=tool_request_id,
                status=row.status,
                output=dict(row.output or {}),
                error=row.error,
                metadata={str(k): str(v) for k, v in (row.result_metadata or {}).items()},
            )

    # -- internals ------------------------------------------------------------------------------

    @staticmethod
    async def _run_row(session: AsyncSession, run_id: str,
                       *, required: bool = False) -> TaskRun | None:
        row = await session.get(TaskRun, _uuid(run_id, what="the run identifier"))
        if row is None and required:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"no run with identifier {run_id}",
                details={"runId": run_id})
        return row


def _event_from_row(row: RunEventRow, run_id: str) -> RunEvent:
    return RunEvent(
        run_id=run_id,
        type=row.event_type,
        dedupe_key=row.dedupe_key,
        stage=row.stage,
        agent_run_id=str(row.agent_run_id) if row.agent_run_id else None,
        payload=dict(row.payload or {}),
        sequence=row.sequence,
        created_at=row.created_at,
    )


def _tool_request_from_row(row: ToolRequestRow, run_id: str) -> ToolRequest:
    return ToolRequest(
        tool_request_id=str(row.id),
        run_id=run_id,
        agent_run_id=str(row.agent_run_id) if row.agent_run_id else None,
        name=row.tool_name,
        arguments=dict(row.arguments or {}),
        status=row.status,
        executor=row.executor,
        created_at=row.created_at,
        resolved_at=row.resolved_at,
    )


async def bootstrap_registry(session_factory: async_sessionmaker[AsyncSession],
                             registry: AgentRegistry) -> BootstrapOutcome:
    """Write the declared profiles and teams into the database, idempotently.

    A row whose ``definition_hash`` already matches is left untouched, and a row an operator marked
    as customised is left untouched whatever its hash, so a start-up cannot quietly revert somebody
    else's deliberate edit. The counts are returned so a caller can assert that a second run
    changed nothing — which is what "idempotent" means and what a log line would only claim.
    """
    created = updated = unchanged = customised = 0
    teams_created = teams_updated = teams_unchanged = teams_customised = 0

    async with session_factory() as session, session.begin():
        for record in registry.agent_records():
            row = (await session.execute(
                select(Agent).where(Agent.slug == record.agent))).scalars().first()
            if row is None:
                row = Agent(slug=record.agent, name=record.name,
                            role_contract=record.role_contract)
                session.add(row)
                created += 1
            elif row.customised:
                customised += 1
                continue
            elif row.definition_hash == record.definition_hash:
                unchanged += 1
                continue
            else:
                updated += 1
            row.name = record.name
            row.role_contract = record.role_contract
            row.role = record.role
            row.description = record.description
            row.profile_version = record.version
            row.default_route = record.default_route
            row.max_turns = record.max_turns
            row.allowed_actions = list(record.allowed_actions)
            row.prompt_template = record.prompt_template
            row.prompt_template_version = record.prompt_template_version
            row.prompt_template_hash = record.prompt_template_hash
            row.definition_hash = record.definition_hash
            row.enabled = record.enabled

        for team in registry.team_records():
            row = (await session.execute(
                select(AgentTeam).where(AgentTeam.slug == team.team))).scalars().first()
            if row is None:
                row = AgentTeam(slug=team.team, name=team.name)
                session.add(row)
                teams_created += 1
            elif row.customised:
                teams_customised += 1
                continue
            elif row.definition_hash == team.definition_hash:
                teams_unchanged += 1
                continue
            else:
                teams_updated += 1
            row.name = team.name
            row.description = team.description
            row.profile_version = team.version
            row.stages = [dict(stage) for stage in team.stages]
            row.definition_hash = team.definition_hash
            row.enabled = team.enabled

    return BootstrapOutcome(
        agents_created=created, agents_updated=updated, agents_unchanged=unchanged,
        agents_customised=customised, teams_created=teams_created, teams_updated=teams_updated,
        teams_unchanged=teams_unchanged, teams_customised=teams_customised)


def new_identifier() -> str:
    """A fresh identifier, using the strategy the repository already defines."""
    return str(uuid7())


def stage_plan_fields(stage: StagePlan) -> dict[str, Any]:
    """What ``start_stage`` needs from a stage plan, in one place."""
    return {
        "stage_index": stage.index,
        "stage_name": stage.name,
        "agent": stage.agent,
        "profile_version": stage.profile_version,
        "prompt_template_version": stage.prompt_template_version,
        "prompt_template_hash": stage.prompt_template_hash,
        "output_name": stage.output_name,
    }
