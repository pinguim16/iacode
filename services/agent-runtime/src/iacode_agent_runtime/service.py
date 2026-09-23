"""Creating a run, reading one, cancelling one, and answering a tool request.

This is the runtime's application service: the operations a caller performs on a run that are not
the run itself. The HTTP layer above it is a translation of arguments and status codes, and the
durable workflow below it is the execution — this module is what both of them talk to.

**A plan is resolved once, at creation.** The team, every profile, every prompt template and its
hash are read here and frozen into a :class:`~iacode_agent_runtime.contracts.RunPlan` that the
workflow carries. An operator who edits a profile changes the next run, not one that is already in
flight, and the run's provenance says exactly which definition produced it. A workflow that re-read
the registry each turn would change behaviour mid-run with nothing in the history to show why.

**Creation is idempotent on a key the caller supplies.** An HTTP client that retries a creation
because it did not see the response must not get a second run. The uniqueness constraint in the
database is the mechanism; this module turns the conflict into the first run's answer.

The service builds the shapes in ``iacode_contracts.agent_runtime`` directly rather than through a
second set of domain objects. Those shapes are in a shared package precisely so more than one
process can speak them, and a second mapping layer would be a second thing to keep in step with the
first for no gain.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from iacode_common.identifiers import uuid7
from iacode_contracts.agent_runtime import (
    AgentProfileSummary,
    AgentRunCreated,
    AgentRunDetail,
    AgentRunStageView,
    AgentRunSummaryView,
    BudgetView,
    CreateAgentRunRequest,
    RunEventPage,
    RunEventPayload,
    TeamProfileSummary,
    TeamStageSummary,
    ToolRequestView,
    ToolResultSubmission,
)
from iacode_contracts.sandbox import ToolExecutionView
from iacode_persistence.models import AgentRun, ModelCall, Project, Task, TaskRun, ToolCall
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from iacode_agent_runtime.budgets import Budget, BudgetLedger
from iacode_agent_runtime.contracts import RunPlan, StagePlan, ToolResult
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.limits import RuntimeLimits, enforce_size
from iacode_agent_runtime.persistence import SqlAgentRunStore, bootstrap_registry
from iacode_agent_runtime.registry import AgentRegistry, BootstrapOutcome
from iacode_agent_runtime.states import RunState

__all__ = ["DEFAULT_PROJECT_SLUG", "AgentRuntimeService"]

#: Where a run with no project of its own is filed. Gate 2 has no project management and inventing
#: one would be a capability with no requirement behind it; a single well-named row is honest about
#: that and gives the foreign key something real to point at.
DEFAULT_PROJECT_SLUG = "iacode-agent-runtime"


@dataclass
class AgentRuntimeService:
    """Operations on runs, over the shared schema and the repository's declared profiles."""

    session_factory: async_sessionmaker[AsyncSession]
    registry: AgentRegistry
    store: SqlAgentRunStore
    default_budget: Budget = field(default_factory=Budget)
    limits: RuntimeLimits = field(default_factory=RuntimeLimits)

    _registered: str | None = None
    _registration_lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    # -- registration ----------------------------------------------------------------------------

    async def ensure_registered(self) -> BootstrapOutcome:
        """Make sure the declared profiles exist as rows, at most once per process.

        Not at start-up: `docs/GATE-0-CHECKLIST.md` row 3.3 keeps the API's start-up free of I/O so
        it can start while PostgreSQL is still initialising and report ``NOT_READY`` rather than
        crash-looping. Not on every request either, because that would be a handful of queries per
        run for an answer that changes only when somebody edits a definition.

        So: the first run of a process registers, and a later edit to a definition re-registers,
        because the fingerprint is the digests of what the registry currently declares. The
        bootstrap itself is idempotent and leaves a customised row alone, so doing it again is
        never destructive.
        """
        fingerprint = "|".join(
            sorted(record.definition_hash for record in self.registry.agent_records())
            + sorted(record.definition_hash for record in self.registry.team_records()))
        if self._registered == fingerprint:
            return BootstrapOutcome()
        async with self._registration_lock:
            if self._registered == fingerprint:
                return BootstrapOutcome()
            outcome = await bootstrap_registry(self.session_factory, self.registry)
            self._registered = fingerprint
            return outcome

    # -- creation --------------------------------------------------------------------------------

    async def create_run(self, request: CreateAgentRunRequest, *,
                         correlation_id: str | None = None) -> tuple[RunPlan, AgentRunCreated]:
        """Resolve the plan, persist the task and the run, and answer immediately."""
        enforce_size(request.task, self.limits.max_task_bytes, what="the task")
        await self.ensure_registered()
        team = self.registry.team(request.team)
        budget = self.default_budget.with_overrides(
            max_turns=request.maxTurns,
            max_model_calls=request.maxModelCalls,
            max_duration_seconds=request.maxDurationSeconds,
            tool_wait_timeout_seconds=request.toolWaitTimeoutSeconds,
            max_total_tokens=request.maxTotalTokens,
        )

        stages: list[StagePlan] = []
        for stage in team.stages:
            profile = self.registry.agent(stage.agent)
            if not profile.enabled:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.PROFILE_NOT_FOUND,
                    f"agent {profile.agent!r} is disabled and cannot run",
                    details={"agent": profile.agent})
            stages.append(StagePlan(
                index=stage.index,
                name=stage.name,
                agent=profile.agent,
                agent_name=profile.name,
                role_instructions=profile.template.render(
                    role=profile.role, description=profile.description),
                inputs=stage.inputs,
                output_name=stage.output_name,
                max_turns=min(profile.max_turns, budget.max_turns),
                allowed_actions=profile.allowed_actions,
                profile_version=profile.version,
                prompt_template=profile.template.path,
                prompt_template_version=profile.template.version,
                prompt_template_hash=profile.template.content_hash,
                default_route=profile.default_route,
                sandbox_policy=profile.sandbox_policy,
            ))
        workspace = await self._workspace_for(request, stages)

        if request.idempotencyKey:
            existing = await self._run_by_idempotency_key(request.idempotencyKey)
            if existing is not None:
                plan = await self._plan_for(existing, stages, budget, correlation_id)
                return plan, AgentRunCreated(
                    runId=str(existing.id), taskId=str(existing.task_id),
                    state=existing.status, team=existing.team_slug or team.team,
                    createdAt=_iso(existing.created_at), idempotentReplay=True)

        project_id = await self._default_project()
        run_id = uuid7()
        task_id = uuid7()
        title = request.title or _title_from(request.task)

        try:
            async with self.session_factory() as session, session.begin():
                session.add(Task(
                    id=task_id, project_id=project_id, title=title,
                    description=request.task, status="PENDING"))
                session.add(TaskRun(
                    id=run_id,
                    task_id=task_id,
                    status=str(RunState.CREATED),
                    attempt=1,
                    team_slug=team.team,
                    team_version=team.version,
                    route=request.route,
                    model_override=request.model,
                    idempotency_key=request.idempotencyKey,
                    budget=budget.to_dict(),
                    budget_used=BudgetLedger(budget=budget).to_dict(),
                    correlation_id=correlation_id,
                    metadata_=dict(request.metadata),
                    workspace=dict(workspace),
                ))
        except IntegrityError:
            # Two concurrent creations shared an idempotency key. The row the first one wrote is
            # the answer to both, which is the whole point of the key.
            existing = await self._run_by_idempotency_key(request.idempotencyKey or "")
            if existing is None:
                raise
            plan = await self._plan_for(existing, stages, budget, correlation_id)
            return plan, AgentRunCreated(
                runId=str(existing.id), taskId=str(existing.task_id), state=existing.status,
                team=existing.team_slug or team.team, createdAt=_iso(existing.created_at),
                idempotentReplay=True)

        plan = RunPlan(
            run_id=str(run_id),
            task_id=str(task_id),
            task=request.task,
            team=team.team,
            team_version=team.version,
            stages=tuple(stages),
            budget=budget,
            route=request.route,
            model=request.model,
            correlation_id=correlation_id,
            title=title,
            metadata=dict(request.metadata),
            workspace=dict(workspace),
        )
        await self.store.append_event(_created_event(plan))
        record = await self.store.load_run(str(run_id))
        return plan, AgentRunCreated(
            runId=str(run_id), taskId=str(task_id), state=str(RunState.CREATED),
            team=team.team,
            createdAt=_iso(record.created_at if record else datetime.now(UTC)))

    async def mark_queued(self, run_id: str, workflow_id: str) -> None:
        """Record that the durable workflow now owns the run."""
        await self.store.set_run_state(run_id, str(RunState.QUEUED), workflow_id=workflow_id)

    # -- reading ---------------------------------------------------------------------------------

    async def detail(self, run_id: str) -> AgentRunDetail:
        async with self.session_factory() as session:
            row = await session.get(TaskRun, _as_uuid(run_id))
            if row is None:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INVALID_REQUEST,
                    f"no run with identifier {run_id}",
                    details={"runId": run_id})
            task = await session.get(Task, row.task_id)
            stage_rows = (await session.execute(
                select(AgentRun).where(AgentRun.task_run_id == row.id)
                .order_by(AgentRun.stage_index))).scalars().all()
            usage = await self._usage_for(session, [stage.id for stage in stage_rows])
            executions = await self._executions_for(session, [stage.id for stage in stage_rows])
        requests = await self.store.list_tool_requests(run_id)
        detail = self._detail(row, task, stage_rows, requests, usage)
        return detail.model_copy(update={"toolExecutions": executions})

    async def list_runs(self, limit: int = 25) -> list[AgentRunDetail]:
        async with self.session_factory() as session:
            rows = (await session.execute(
                select(TaskRun).order_by(TaskRun.created_at.desc()).limit(limit))).scalars().all()
            details = []
            for row in rows:
                task = await session.get(Task, row.task_id)
                stage_rows = (await session.execute(
                    select(AgentRun).where(AgentRun.task_run_id == row.id)
                    .order_by(AgentRun.stage_index))).scalars().all()
                usage = await self._usage_for(session, [stage.id for stage in stage_rows])
                details.append(self._detail(row, task, stage_rows, (), usage))
        return details

    async def events(self, run_id: str, *, after: int = 0, limit: int = 500) -> RunEventPage:
        events = await self.store.read_events(run_id, after=after, limit=limit)
        payloads = [
            RunEventPayload(
                runId=run_id, sequence=int(event.sequence or 0), type=event.type,
                createdAt=_iso(event.created_at), agentRunId=event.agent_run_id,
                stage=event.stage, payload=dict(event.payload))
            for event in events
        ]
        cursor = payloads[-1].sequence if payloads else after
        return RunEventPage(runId=run_id, total=len(payloads), nextCursor=cursor,
                            events=payloads)

    # -- acting ----------------------------------------------------------------------------------

    async def request_cancellation(self, run_id: str) -> AgentRunDetail:
        await self.store.request_cancellation(run_id)
        return await self.detail(run_id)

    async def submit_tool_result(self, run_id: str,
                                 submission: ToolResultSubmission) -> ToolResult:
        enforce_size(submission.output, self.limits.max_tool_result_bytes,
                     what="the tool result output")
        result = ToolResult(
            tool_request_id=submission.toolRequestId,
            status=submission.status,
            output=dict(submission.output),
            error=submission.error,
            metadata=dict(submission.metadata),
        )
        return await self.store.resolve_tool_request(run_id, result)

    # -- registry listings -------------------------------------------------------------------------

    def agent_summaries(self) -> list[AgentProfileSummary]:
        return [
            AgentProfileSummary(**profile.summary())
            for profile in sorted(self.registry.agents().values(), key=lambda item: item.agent)
        ]

    def team_summaries(self) -> list[TeamProfileSummary]:
        summaries = []
        for team in sorted(self.registry.teams().values(), key=lambda item: item.team):
            payload = team.summary()
            summaries.append(TeamProfileSummary(
                team=payload["team"], name=payload["name"], description=payload["description"],
                version=payload["version"], enabled=payload["enabled"],
                stages=[TeamStageSummary(**stage) for stage in payload["stages"]]))
        return summaries

    # -- internals ---------------------------------------------------------------------------------

    async def _workspace_for(self, request: CreateAgentRunRequest,
                             stages: list[StagePlan]) -> dict[str, str]:
        """Where the run's sandbox workspace comes from, checked before the run exists.

        A run whose stages have no sandbox policy has no workspace. A run that names a snapshot must
        name an artifact that is an authorised workspace snapshot; anything else is refused here,
        with the run not created, rather than discovered by the sandbox on the first tool call.
        """
        if not request.workspaceSnapshot:
            return {"kind": "empty"} if any(stage.sandbox_policy for stage in stages) else {}
        from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND
        from iacode_persistence.models import Artifact

        try:
            identifier = uuid.UUID(request.workspaceSnapshot)
        except ValueError:
            identifier = None
        row = None
        if identifier is not None:
            async with self.session_factory() as session:
                row = await session.get(Artifact, identifier)
        if row is None or row.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"{request.workspaceSnapshot!r} is not an authorised workspace snapshot",
                details={"workspaceSnapshot": request.workspaceSnapshot})
        if not any(stage.sandbox_policy for stage in stages):
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"team {request.team!r} executes no tool, so it has no workspace to provision",
                details={"team": request.team})
        return {"kind": "snapshot", "artifactId": str(row.id), "checksum": row.checksum_sha256}

    async def _default_project(self):
        async with self.session_factory() as session, session.begin():
            row = (await session.execute(
                select(Project).where(Project.slug == DEFAULT_PROJECT_SLUG))).scalars().first()
            if row is None:
                row = Project(slug=DEFAULT_PROJECT_SLUG, name="IACode Agent Runtime",
                              description="Runs created through the agent runtime API.")
                session.add(row)
                await session.flush()
            return row.id

    async def _run_by_idempotency_key(self, key: str) -> TaskRun | None:
        if not key:
            return None
        async with self.session_factory() as session:
            return (await session.execute(
                select(TaskRun).where(TaskRun.idempotency_key == key))).scalars().first()

    async def _plan_for(self, row: TaskRun, stages: list[StagePlan], budget: Budget,
                        correlation_id: str | None) -> RunPlan:
        async with self.session_factory() as session:
            task = await session.get(Task, row.task_id)
        return RunPlan(
            run_id=str(row.id), task_id=str(row.task_id),
            task=(task.description or "") if task else "",
            team=row.team_slug or "", team_version=row.team_version or "",
            stages=tuple(stages), budget=Budget.from_dict(row.budget) or budget,
            route=row.route, model=row.model_override,
            correlation_id=row.correlation_id or correlation_id,
            title=(task.title if task else None),
            metadata={str(k): str(v) for k, v in (row.metadata_ or {}).items()},
            workspace={str(k): str(v) for k, v in (row.workspace or {}).items()})

    @staticmethod
    async def _executions_for(session: AsyncSession,
                              agent_run_ids: list[Any]) -> list[ToolExecutionView]:
        """What the sandbox executed for these agent runs, read from ``tool_calls``.

        The runtime executes nothing; it reads the execution record the sandbox wrote, for the
        operational page. The record carries no output, so neither does the view.
        """
        if not agent_run_ids:
            return []
        rows = (await session.execute(
            select(ToolCall).where(ToolCall.agent_run_id.in_(agent_run_ids))
            .order_by(ToolCall.created_at))).scalars().all()
        return [
            ToolExecutionView(
                toolRequestId=str(row.tool_request_id or ""), tool=row.tool_name,
                status=row.status, durationMs=row.latency_ms,
                sandboxSession=(str(row.sandbox_session_id).replace("-", "")[:12]
                                if row.sandbox_session_id else None),
                exitCode=row.exit_code, timedOut=row.timed_out, truncated=row.truncated,
                errorCode=row.error_code, summary=(row.summary or "")[:240],
                createdAt=_iso(row.created_at))
            for row in rows
        ]

    @staticmethod
    async def _usage_for(session: AsyncSession, agent_run_ids: list[Any]) -> dict[str, Any]:
        """Aggregate usage, derived from ``model_calls`` rather than counted a second time."""
        if not agent_run_ids:
            return {"totalTokens": None, "cost": None, "costKnown": False}
        totals = (await session.execute(
            select(
                func.sum(ModelCall.input_tokens + ModelCall.output_tokens),
                func.sum(ModelCall.cost),
                func.count(ModelCall.id),
                func.count(ModelCall.cost),
            ).where(ModelCall.agent_run_id.in_(agent_run_ids)))).one()
        tokens, cost, calls, priced = totals
        return {
            "totalTokens": int(tokens) if tokens is not None else None,
            # A cost is reported only when every recorded call carried one. A partial sum would be
            # a smaller number wearing the name of the total, which is worse than saying UNKNOWN.
            "cost": float(cost) if cost is not None and calls and priced == calls else None,
            "costKnown": bool(calls and priced == calls),
        }

    def _detail(self, row: TaskRun, task: Task | None, stages, requests,
                usage: dict[str, Any]) -> AgentRunDetail:
        budget = Budget.from_dict(row.budget)
        used = dict(row.budget_used or {})
        pending = next((item for item in requests if item.status == "PENDING"), None)
        return AgentRunDetail(
            runId=str(row.id),
            taskId=str(row.task_id),
            title=task.title if task else None,
            task=(task.description or "") if task else "",
            team=row.team_slug or "",
            teamVersion=row.team_version,
            state=row.status,
            route=row.route,
            model=row.model_override,
            currentStage=row.current_stage,
            createdAt=_iso(row.created_at),
            startedAt=_iso(row.started_at) if row.started_at else None,
            finishedAt=_iso(row.finished_at) if row.finished_at else None,
            workflowId=row.workflow_id,
            budget=BudgetView(
                maxTurns=budget.max_turns,
                maxModelCalls=budget.max_model_calls,
                maxDurationSeconds=budget.max_duration_seconds,
                toolWaitTimeoutSeconds=budget.tool_wait_timeout_seconds,
                maxTotalTokens=budget.max_total_tokens,
                turnsUsed=int(used.get("turnsUsed", 0)),
                modelCallsUsed=int(used.get("modelCallsUsed", 0)),
                tokensUsed=used.get("tokensUsed"),
                tokensEnforceable=bool(used.get("tokensEnforceable", True)),
            ),
            stages=[
                AgentRunStageView(
                    index=stage.stage_index,
                    name=stage.stage_name or f"stage-{stage.stage_index}",
                    agent=stage.agent_slug or "",
                    agentRunId=str(stage.id),
                    state=stage.status,
                    profileVersion=stage.profile_version,
                    promptTemplateVersion=stage.prompt_template_version,
                    promptTemplateHash=stage.prompt_template_hash,
                    turns=stage.turns,
                    modelCalls=stage.model_calls,
                    outputName=stage.output_name,
                    outputSummary=stage.output_summary,
                    startedAt=_iso(stage.started_at) if stage.started_at else None,
                    finishedAt=_iso(stage.finished_at) if stage.finished_at else None,
                )
                for stage in stages
            ],
            pendingToolRequest=_tool_view(pending) if pending else None,
            toolRequests=[_tool_view(item) for item in requests],
            result=row.result,
            resultSummary=row.result_summary,
            errorType=row.error_type,
            errorSummary=row.error_summary,
            failedStage=row.failed_stage,
            correlationId=row.correlation_id,
            summary=AgentRunSummaryView(
                agentsExecuted=len([stage for stage in stages
                                    if stage.status in ("SUCCEEDED", "FAILED", "CANCELLED")]),
                turns=int(used.get("turnsUsed", 0)),
                modelCalls=int(used.get("modelCallsUsed", 0)),
                toolsRequested=len(requests),
                toolsResolved=len([item for item in requests if item.status == "RESOLVED"]),
                durationSeconds=_duration(row),
                finalState=row.status,
                totalTokens=usage.get("totalTokens"),
                cost=usage.get("cost"),
                costKnown=bool(usage.get("costKnown")),
            ),
            trainingAllowed=bool(row.training_allowed),
        )


def _tool_view(request) -> ToolRequestView:
    return ToolRequestView(
        toolRequestId=request.tool_request_id,
        agentRunId=request.agent_run_id,
        name=request.name,
        arguments=dict(request.arguments),
        status=request.status,
        createdAt=_iso(request.created_at),
        resolvedAt=_iso(request.resolved_at) if request.resolved_at else None,
    )


def _created_event(plan: RunPlan):
    from iacode_agent_runtime.events import RunEvent, safe_payload

    return RunEvent(
        run_id=plan.run_id,
        type="RUN_CREATED",
        dedupe_key="run-created",
        payload=safe_payload({
            "team": plan.team,
            "teamVersion": plan.team_version,
            "stages": len(plan.stages),
            "route": plan.route,
            "model": plan.model,
            "maxTurns": plan.budget.max_turns,
            "maxModelCalls": plan.budget.max_model_calls,
        }),
    )


def _title_from(task: str, limit: int = 120) -> str:
    first = (task or "").strip().splitlines()
    value = first[0].strip() if first else "agent run"
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _duration(row: TaskRun) -> float | None:
    if row.started_at is None:
        return None
    end = row.finished_at or datetime.now(UTC)
    return round((end - row.started_at).total_seconds(), 3)


def _iso(value: datetime | None) -> str:
    return (value or datetime.now(UTC)).astimezone(UTC).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


def _as_uuid(value: str):
    import uuid as _uuid_module

    try:
        return _uuid_module.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as error:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            "the run identifier is not valid",
            details={"runId": str(value)}) from error


def registry_root(root: Path) -> AgentRegistry:
    """The registry for a repository checkout or an image that carries ``agents/``."""
    return AgentRegistry(root)
