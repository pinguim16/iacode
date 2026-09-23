"""The durable agent run.

This is the workflow that makes a run survive things. It holds no business logic: it builds the
engine's :class:`~iacode_agent_runtime.engine.Effects` out of activities and lets the engine decide
what happens next. Everything in this module is either an activity invocation, a signal handler, a
query or arithmetic over the frozen plan — which is exactly the set of things that replay
deterministically.

Three mechanisms are worth stating plainly.

**The pause is a condition, not a poll.** ``WAITING_FOR_TOOL`` is
:func:`temporalio.workflow.wait_condition` over a signal, with the run's own tool-wait timeout. A
worker that dies while a run is waiting loses nothing: the condition is part of the workflow's
state, Temporal rebuilds it from history, and the run resumes when the result arrives. That is the
whole durability claim of this Gate, and the restart scenario exercises it against a real container
restart.

**A lost signal is survivable.** The API writes the tool result to the database *and* signals the
workflow. If the signal is lost — a worker restarting at exactly the wrong moment — the workflow
reads the stored row when the condition times out and resumes anyway. A design that trusted the
signal alone would be a design whose durability depended on delivery luck.

**Cancellation is a signal, not a Temporal cancel.** A hard cancellation would abort the very
activities that record the cancellation, so the run would stop without the history saying it
stopped. The signal sets a flag the engine reads between steps; the run then ends through the same
path as any other terminal outcome, with its state, its event and its pending tool requests all
recorded.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError
from temporalio.workflow import ActivityCancellationType

with workflow.unsafe.imports_passed_through():
    from iacode_agent_runtime.budgets import BudgetLedger
    from iacode_agent_runtime.contracts import (
        ModelCallOutcome,
        RunPlan,
        StagePlan,
        ToolResult,
        TurnRequest,
    )
    from iacode_agent_runtime.engine import AgentRunEngine, RunOutcome
    from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
    from iacode_agent_runtime.events import RunEvent
    from iacode_agent_runtime.ports import StageCompletion
    from iacode_agent_runtime.states import RunState
    from iacode_contracts.agent_runtime import (
        AGENT_RUN_WORKFLOW,
        CANCEL_SIGNAL,
        TOOL_RESULT_SIGNAL,
    )
    from iacode_contracts.sandbox import (
        SANDBOX_AGENT_RESULT_KEY,
        SANDBOX_CONTRACT_VERSION,
        SANDBOX_EXECUTE_ACTIVITY,
        SANDBOX_RELEASE_ACTIVITY,
        SANDBOX_TASK_QUEUE,
    )

__all__ = ["AGENT_RUN_WORKFLOW_NAME", "CANCEL_SIGNAL", "TOOL_RESULT_SIGNAL", "AgentRunWorkflow"]

#: The names are the shared contract's. The API starts and signals this workflow, so a second
#: spelling here would be a signal that silently goes nowhere.
AGENT_RUN_WORKFLOW_NAME = AGENT_RUN_WORKFLOW

#: Store activities are small writes against a local database. Ten seconds is generous; anything
#: longer is a database problem Temporal should retry rather than a slow query to wait out.
STORE_TIMEOUT = timedelta(seconds=30)

#: The longest one model call may take. Above the gateway's own read timeout, so the gateway's
#: classified timeout arrives as a decision rather than as an activity that vanished.
MODEL_CALL_CEILING_SECONDS = 900

#: How long a sandbox execution may go without reporting that it is alive. The sandbox heartbeats
#: every few seconds while a tool runs, so this detects a sandbox service that died mid-execution
#: rather than bounding how long a tool may take - the policy's own timeout does that.
SANDBOX_HEARTBEAT_TIMEOUT = timedelta(seconds=120)


def _activity_error(error: BaseException) -> AgentRuntimeError | None:
    """The classified runtime failure inside an activity error, if that is what it is."""
    cause = error
    while cause is not None:
        if isinstance(cause, ApplicationError):
            details: dict[str, Any] = {}
            if cause.details and isinstance(cause.details[0], dict):
                details = cause.details[0]
            try:
                error_type = AgentRuntimeErrorType(str(cause.type))
            except ValueError:
                return None
            return AgentRuntimeError(
                error_type,
                str(details.get("message") or cause.message),
                stage=details.get("stage"),
                details=dict(details.get("details") or {}),
                upstream_type=details.get("upstreamType"),
            )
        cause = cause.__cause__ if cause.__cause__ is not cause else None
    return None


@dataclass
class _WorkflowEffects:
    """The engine's effects, implemented as activity invocations.

    Two small maps make the Gate 3 dispatch possible without widening the engine's protocol: which
    stage an agent run belongs to (from ``start_stage``) and what each tool request asked for (from
    ``create_tool_request``). Both are filled from activity results and arguments, so a replay
    rebuilds them identically.
    """

    plan: RunPlan
    workflow_ref: AgentRunWorkflow
    model_timeout: timedelta
    stages_by_agent_run: dict[str, StagePlan] = field(default_factory=dict)
    requests: dict[str, dict[str, Any]] = field(default_factory=dict)

    async def new_id(self) -> str:
        # Deterministic by construction: the SDK seeds this from the workflow's own identity, so a
        # replay produces the same identifier and a retried step addresses the same tool request.
        return str(workflow.uuid4())

    async def record_event(self, event: RunEvent) -> None:
        await self._call("iacode_agent_runtime_record_event", {
            "runId": event.run_id,
            "type": event.type,
            "dedupeKey": event.dedupe_key,
            "stage": event.stage,
            "agentRunId": event.agent_run_id,
            "payload": dict(event.payload),
            "team": self.plan.team,
        })

    async def set_state(self, state: str, **fields: Any) -> None:
        payload = {"runId": self.plan.run_id, "state": state}
        mapping = {
            "current_stage": "currentStage", "budget_used": "budgetUsed", "result": "result",
            "result_summary": "resultSummary", "error_type": "errorType",
            "error_summary": "errorSummary", "failed_stage": "failedStage",
            "workflow_id": "workflowId", "started": "started", "finished": "finished",
        }
        for key, value in fields.items():
            if value is not None and key in mapping:
                payload[mapping[key]] = value
        await self._call("iacode_agent_runtime_set_state", payload)

    async def start_stage(self, stage: StagePlan) -> str:
        agent_run_id = await self._call("iacode_agent_runtime_start_stage", {
            "runId": self.plan.run_id,
            "stageIndex": stage.index,
            "stageName": stage.name,
            "agent": stage.agent,
            "profileVersion": stage.profile_version,
            "promptTemplateVersion": stage.prompt_template_version,
            "promptTemplateHash": stage.prompt_template_hash,
            "outputName": stage.output_name,
        })
        self.stages_by_agent_run[str(agent_run_id)] = stage
        return agent_run_id

    async def finish_stage(self, agent_run_id: str, completion: StageCompletion) -> None:
        await self._call("iacode_agent_runtime_finish_stage", {
            "agentRunId": agent_run_id,
            "state": completion.state,
            "output": completion.output,
            "outputSummary": completion.output_summary,
            "turns": completion.turns,
            "modelCalls": completion.model_calls,
            "errorType": completion.error_type,
            "errorSummary": completion.error_summary,
        })

    async def call_model(self, request: TurnRequest) -> ModelCallOutcome:
        body = await self._call("iacode_agent_runtime_call_model", {
            "runId": request.run_id,
            "stageIndex": request.stage_index,
            "turn": request.turn,
            "instructions": request.instructions,
            "data": request.data,
            "route": request.route,
            "model": request.model,
            "allowedActions": list(request.allowed_actions),
            "structuredOutput": request.structured_output,
            "repairOf": request.repair_of,
        }, start_to_close=self.model_timeout)
        return ModelCallOutcome(
            text=str(body.get("text") or ""),
            model_call_id=body.get("modelCallId"),
            gateway_request_id=str(body.get("gatewayRequestId") or ""),
            provider=str(body.get("provider") or ""),
            model=str(body.get("model") or ""),
            endpoint=str(body.get("endpoint") or ""),
            route_reason=str(body.get("routeReason") or ""),
            finish_reason=str(body.get("finishReason") or ""),
            latency_ms=float(body.get("latencyMs") or 0.0),
            total_tokens=body.get("totalTokens"),
            input_tokens=body.get("inputTokens"),
            output_tokens=body.get("outputTokens"),
            cost=body.get("cost"),
            cost_known=bool(body.get("costKnown")),
            repair_attempt=bool(body.get("repairAttempt")),
        )

    async def attach_model_call(self, agent_run_id: str,
                                gateway_request_id: str) -> str | None:
        if not gateway_request_id:
            return None
        return await self._call("iacode_agent_runtime_attach_model_call", {
            "agentRunId": agent_run_id, "gatewayRequestId": gateway_request_id})

    async def create_tool_request(self, tool_request_id: str, agent_run_id: str, name: str,
                                  arguments: dict[str, Any]) -> None:
        await self._call("iacode_agent_runtime_create_tool_request", {
            "runId": self.plan.run_id,
            "agentRunId": agent_run_id,
            "toolRequestId": tool_request_id,
            "name": name,
            "arguments": arguments,
        })
        self.requests[tool_request_id] = {"agentRunId": agent_run_id, "name": name,
                                          "arguments": dict(arguments)}

    async def wait_for_tool(self, tool_request_id: str,
                            timeout_seconds: int) -> ToolResult | None:
        request = self.requests.get(tool_request_id)
        stage = (self.stages_by_agent_run.get(str(request["agentRunId"]))
                 if request else None)
        if request is not None and stage is not None and stage.sandbox_policy:
            return await self._execute_in_sandbox(tool_request_id, request, stage,
                                                  timeout_seconds)
        # Gate 2's path, unchanged: a stage with no sandbox policy has its tools answered from
        # outside, through the API's tool-result endpoint and this workflow's signal.
        reference = self.workflow_ref
        reference.awaiting = tool_request_id
        try:
            await workflow.wait_condition(
                lambda: tool_request_id in reference.results or reference.cancel_requested,
                timeout=timedelta(seconds=timeout_seconds))
        except TimeoutError:
            # The signal may simply have been lost. The stored row is authoritative, so the wait
            # ends by asking the database rather than by assuming the worst.
            stored = await self._call("iacode_agent_runtime_read_tool_result",
                                      {"toolRequestId": tool_request_id})
            return ToolResult.from_dict(stored) if stored else None
        finally:
            reference.awaiting = None
        if reference.cancel_requested and tool_request_id not in reference.results:
            return None
        return ToolResult.from_dict(reference.results[tool_request_id])

    async def _execute_in_sandbox(self, tool_request_id: str, request: dict[str, Any],
                                  stage: StagePlan, timeout_seconds: int) -> ToolResult | None:
        """Dispatch a tool request to the sandbox, persist its result, and resume.

        The sandbox's answer is an activity result: Temporal delivers it durably, so there is no
        signal to lose. It is recorded through the same store validation the API's tool-result
        endpoint uses, and the stored result is what resumes the engine. A cancellation cancels the
        activity, which stops every process the tool started before the run records that it was
        cancelled.
        """
        reference = self.workflow_ref
        payload = {
            "contractVersion": SANDBOX_CONTRACT_VERSION,
            "toolRequestId": tool_request_id,
            "runId": self.plan.run_id,
            "agentRunId": request["agentRunId"],
            "agent": stage.agent,
            "tool": request["name"],
            "arguments": request["arguments"],
            "policy": stage.sandbox_policy,
            "workspace": dict(self.plan.workspace) or {"kind": "empty"},
        }
        handle = workflow.start_activity(
            SANDBOX_EXECUTE_ACTIVITY, payload, task_queue=SANDBOX_TASK_QUEUE,
            schedule_to_close_timeout=timedelta(seconds=timeout_seconds),
            heartbeat_timeout=SANDBOX_HEARTBEAT_TIMEOUT,
            cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2),
                                     maximum_interval=timedelta(seconds=30),
                                     maximum_attempts=3))
        reference.awaiting = tool_request_id
        try:
            await workflow.wait_condition(lambda: handle.done() or reference.cancel_requested)
            if not handle.done():
                handle.cancel()
                with contextlib.suppress(ActivityError, asyncio.CancelledError):
                    await handle
                return None
            try:
                body = await handle
                result = dict(body[SANDBOX_AGENT_RESULT_KEY])
            except ActivityError as error:
                # The sandbox could not answer at all - its service down past the retries, or the
                # schedule exhausted. The agent receives that as a failed tool, rather than the run
                # waiting for a result that will never come.
                result = {"toolRequestId": tool_request_id, "status": "FAILED", "output": {},
                          "error": f"the sandbox did not answer: {type(error.cause).__name__}",
                          "metadata": {"executor": "sandbox",
                                       "errorCode": "SANDBOX_UNAVAILABLE"}}
        except asyncio.CancelledError:
            handle.cancel()
            raise
        finally:
            reference.awaiting = None
        stored = await self._call("iacode_agent_runtime_resolve_tool_request",
                                  {"runId": self.plan.run_id, "result": result})
        return ToolResult.from_dict(stored)

    async def release_sandboxes(self) -> None:
        """End the run's sandbox sessions. A failure is logged; the sweeper is the backstop."""
        if not any(stage.sandbox_policy for stage in self.plan.stages):
            return
        try:
            await workflow.execute_activity(
                SANDBOX_RELEASE_ACTIVITY, {"runId": self.plan.run_id},
                task_queue=SANDBOX_TASK_QUEUE,
                schedule_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2),
                                         maximum_interval=timedelta(seconds=30),
                                         maximum_attempts=5))
        except ActivityError as error:
            workflow.logger.warning(
                "the run's sandbox sessions were not released; the sweeper will expire them: %s",
                type(error.cause).__name__)

    def cancelled(self) -> bool:
        return self.workflow_ref.cancel_requested

    async def cancel_pending_tools(self) -> int:
        """Close every request nobody will answer, so a finished run leaves nothing pending."""
        return await self._call("iacode_agent_runtime_cancel_pending_tool_requests",
                                {"runId": self.plan.run_id})

    async def _call(self, name: str, payload: dict[str, Any],
                    start_to_close: timedelta = STORE_TIMEOUT) -> Any:
        # Named `start_to_close` rather than `timeout`: it is Temporal's activity timeout, not a
        # timeout on this coroutine, and a parameter called `timeout` on an async function reads
        # as the latter to every reader and to the linter alike.
        try:
            return await workflow.execute_activity(
                name, payload,
                start_to_close_timeout=start_to_close,
                retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1),
                                         maximum_interval=timedelta(seconds=30),
                                         maximum_attempts=5),
            )
        except ActivityError as error:
            classified = _activity_error(error)
            if classified is not None:
                raise classified from None
            raise


@workflow.defn(name=AGENT_RUN_WORKFLOW_NAME)
class AgentRunWorkflow:
    """One durable agent run."""

    def __init__(self) -> None:
        self.results: dict[str, dict[str, Any]] = {}
        self.cancel_requested = False
        self.awaiting: str | None = None
        self.state: str = str(RunState.QUEUED)
        self.summary: dict[str, Any] = {}

    # -- signals and queries ---------------------------------------------------------------------

    @workflow.signal(name=TOOL_RESULT_SIGNAL)
    def deliver_tool_result(self, payload: dict[str, Any]) -> None:
        """Accept a tool result. Validation happened in the API, against the database."""
        identifier = str(payload.get("toolRequestId") or "")
        if identifier:
            self.results[identifier] = dict(payload)

    @workflow.signal(name=CANCEL_SIGNAL)
    def request_cancellation(self, reason: str = "") -> None:
        self.cancel_requested = True

    @workflow.query(name="state")
    def current_state(self) -> str:
        return self.state

    @workflow.query(name="awaiting_tool")
    def awaiting_tool(self) -> str | None:
        return self.awaiting

    @workflow.query(name="summary")
    def current_summary(self) -> dict[str, Any]:
        return dict(self.summary)

    # -- the run ----------------------------------------------------------------------------------

    @workflow.run
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = RunPlan.from_dict(payload)
        effects = _WorkflowEffects(
            plan=plan,
            workflow_ref=self,
            model_timeout=timedelta(seconds=min(MODEL_CALL_CEILING_SECONDS,
                                                plan.budget.max_duration_seconds)),
        )
        engine = AgentRunEngine(
            plan=plan,
            effects=effects,
            ledger=BudgetLedger(budget=plan.budget),
        )
        self.state = str(RunState.RUNNING)
        try:
            outcome = await self._run_within_deadline(plan, effects, engine)
        except AgentRuntimeError as error:
            # The engine handles every failure it can classify. Anything arriving here failed while
            # the engine was recording a failure, which is worth ending explicitly rather than
            # leaving the run RUNNING for ever.
            outcome = await self._unrecoverable(plan, effects, error)

        # The run is over, whatever the outcome: its sandbox goes with it.
        await effects.release_sandboxes()
        if outcome.state != str(RunState.SUCCEEDED):
            await effects.cancel_pending_tools()
        self.state = outcome.state
        self.summary = outcome.to_dict()
        return self.summary

    async def _run_within_deadline(self, plan: RunPlan, effects: _WorkflowEffects,
                                   engine: AgentRunEngine) -> RunOutcome:
        """The engine, raced against its own wall-clock deadline.

        Deliberately *not* ``asyncio.wait_for``. From Python 3.11 that helper implements its
        timeout by cancelling **the task that awaits it** — here, the workflow's own main task —
        and converting the cancellation into ``TimeoutError``. The conversion works, but the
        workflow task is left in a cancelling state, so the very next activity it schedules is
        cancelled before it starts. The effect is a run that ends at its deadline and never records
        that it did: the workflow fails with ``Activity cancelled`` while the row stays ``RUNNING``
        for ever. `LSN-0046`.

        Racing an explicit child task against a timer keeps the cancellation where it belongs. The
        child is cancelled, its in-flight activity goes with it, and the main task — never
        cancelled — is still able to write the failure down.
        """
        work = asyncio.ensure_future(engine.execute())
        timer = asyncio.ensure_future(asyncio.sleep(plan.budget.max_duration_seconds))
        try:
            await asyncio.wait({work, timer}, return_when=asyncio.FIRST_COMPLETED)
        except BaseException:
            work.cancel()
            timer.cancel()
            raise

        if work.done():
            timer.cancel()
            return work.result()

        work.cancel()
        try:
            await work
        except asyncio.CancelledError:
            pass
        except Exception as error:
            # Everything the cancelled work can raise on its way out, and it is not one thing.
            # Cancelling a task that awaits an activity does not surface as ``CancelledError``:
            # Temporal raises ``ActivityError`` whose cause is a cancellation, and the engine may
            # classify an ``AgentRuntimeError`` of its own first. None of them is the reason the
            # run ended — the deadline is — so the deadline is what gets recorded. `LSN-0046`.
            workflow.logger.info(
                "the engine stopped with %s while the deadline was being applied",
                type(error).__name__)
        return await self._deadline_exceeded(plan, effects, engine)

    async def _deadline_exceeded(self, plan: RunPlan, effects: _WorkflowEffects,
                                 engine: AgentRunEngine) -> RunOutcome:
        error = AgentRuntimeError(
            AgentRuntimeErrorType.RUN_DEADLINE_EXCEEDED,
            f"the run exceeded its deadline of {plan.budget.max_duration_seconds}s",
            details={"limit": "maxDurationSeconds",
                     "value": plan.budget.max_duration_seconds})
        # The terminal event before the terminal state, as the engine does. G2-F-010.
        await effects.record_event(RunEvent(
            run_id=plan.run_id, type="RUN_FAILED", dedupe_key="run-deadline",
            payload={"errorType": str(error.error_type), "message": error.message}))
        await effects.set_state(
            str(RunState.FAILED), error_type=str(error.error_type),
            error_summary=error.message, budget_used=engine.ledger.to_dict(), finished=True)
        return RunOutcome(state=str(RunState.FAILED), error_type=str(error.error_type),
                          error_summary=error.message,
                          turns=engine.ledger.turns_used,
                          model_calls=engine.ledger.model_calls_used)

    async def _unrecoverable(self, plan: RunPlan, effects: _WorkflowEffects,
                             error: AgentRuntimeError) -> RunOutcome:
        await effects.record_event(RunEvent(
            run_id=plan.run_id, type="RUN_FAILED", dedupe_key="run-unrecoverable",
            payload={"errorType": str(error.error_type), "message": error.message}))
        await effects.set_state(
            str(RunState.FAILED), error_type=str(error.error_type),
            error_summary=error.message, finished=True)
        return RunOutcome(state=str(RunState.FAILED), error_type=str(error.error_type),
                          error_summary=error.message)
