"""The activities: every effect the agent runtime has on the world.

One activity per method of :class:`~iacode_agent_runtime.engine.Effects`. Each one is small,
because the decision about *which* effect to run next belongs to the engine and the decision about
*when* belongs to Temporal; an activity that contained logic would be logic outside the replayable
history.

**A classified failure is not retried.** An :class:`~iacode_agent_runtime.errors.AgentRuntimeError`
is a decision — a budget was reached, an envelope was invalid, the gateway refused — and repeating
it produces the same decision while spending the same money. It is raised as a non-retryable
``ApplicationError`` carrying its type, and the workflow reconstructs it on the other side. Anything
else — a dropped database connection, a restarted container — is left to Temporal's retry policy,
which is what that policy is for.

**The metrics live here.** Recording them in the activity that appends an event means one place
decides what a run's telemetry says, instead of every call site remembering to increment something.
"""

from __future__ import annotations

from typing import Any

from iacode_agent_runtime.contracts import ToolResult
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.events import RunEvent
from iacode_agent_runtime.ports import StageCompletion
from iacode_agent_runtime.telemetry import runtime_log_fields
from iacode_contracts.agent_runtime import TOOL_EXECUTOR_EXTERNAL, TOOL_EXECUTOR_SANDBOX
from iacode_telemetry.logging import get_logger
from temporalio import activity
from temporalio.exceptions import ApplicationError

from iacode_orchestrator.agent_runtime.runtime_context import get_context

__all__ = [
    "AGENT_RUNTIME_ACTIVITIES",
    "attach_model_call",
    "call_model",
    "cancel_pending_tool_requests",
    "create_tool_request",
    "finish_stage",
    "read_tool_result",
    "record_event",
    "resolve_tool_request",
    "set_run_state",
    "start_stage",
]

logger = get_logger(__name__)


def _refuse(error: AgentRuntimeError) -> ApplicationError:
    """Turn a classified runtime failure into a decision Temporal will not repeat."""
    return ApplicationError(
        error.message,
        error.to_dict(),
        type=str(error.error_type),
        non_retryable=True,
    )


@activity.defn(name="iacode_agent_runtime_record_event")
async def record_event(payload: dict[str, Any]) -> dict[str, Any]:
    context = get_context()
    try:
        event = RunEvent(
            run_id=str(payload["runId"]),
            type=str(payload["type"]),
            dedupe_key=str(payload["dedupeKey"]),
            stage=payload.get("stage"),
            agent_run_id=payload.get("agentRunId"),
            payload=dict(payload.get("payload") or {}),
        )
        stored = await context.store.append_event(event)
    except AgentRuntimeError as error:
        raise _refuse(error) from None
    _record_metrics(context, stored, payload.get("agent"), payload.get("team"))
    logger.info("agent run event", extra=runtime_log_fields(
        run_id=stored.run_id, agent_run_id=stored.agent_run_id, stage=stored.stage,
        event_type=stored.type, status=str(stored.sequence)))
    return {"sequence": stored.sequence, "type": stored.type}


def _record_metrics(context, event: RunEvent, agent: str | None, team: str | None) -> None:
    metrics = context.metrics
    if event.type == "RUN_STARTED":
        metrics.run_started(team or event.payload.get("team") or "unknown")
    elif event.type == "MODEL_CALL_STARTED":
        metrics.turn_executed(agent or event.stage or "unknown")
    elif event.type == "TOOL_REQUESTED":
        metrics.tool_requested(agent or event.stage or "unknown")
        metrics.waiting(1)
    elif event.type == "TOOL_RESULT_RECEIVED":
        metrics.waiting(-1)
    elif event.type == "RUN_CANCELLED":
        metrics.cancelled()
    elif event.type == "RUN_FAILED":
        error_type = str(event.payload.get("errorType") or "UNKNOWN")
        metrics.run_failed(error_type)
        if error_type == str(AgentRuntimeErrorType.BUDGET_EXCEEDED):
            metrics.budget_exhausted(error_type)


@activity.defn(name="iacode_agent_runtime_set_state")
async def set_run_state(payload: dict[str, Any]) -> str:
    context = get_context()
    try:
        return await context.store.set_run_state(
            str(payload["runId"]), str(payload["state"]),
            current_stage=payload.get("currentStage"),
            budget_used=payload.get("budgetUsed"),
            result=payload.get("result"),
            result_summary=payload.get("resultSummary"),
            error_type=payload.get("errorType"),
            error_summary=payload.get("errorSummary"),
            failed_stage=payload.get("failedStage"),
            workflow_id=payload.get("workflowId"),
            started=bool(payload.get("started")),
            finished=bool(payload.get("finished")),
        )
    except AgentRuntimeError as error:
        raise _refuse(error) from None


@activity.defn(name="iacode_agent_runtime_start_stage")
async def start_stage(payload: dict[str, Any]) -> str:
    context = get_context()
    try:
        record = await context.store.start_stage(
            str(payload["runId"]),
            stage_index=int(payload["stageIndex"]),
            stage_name=str(payload["stageName"]),
            agent=str(payload["agent"]),
            profile_version=str(payload["profileVersion"]),
            prompt_template_version=str(payload["promptTemplateVersion"]),
            prompt_template_hash=str(payload["promptTemplateHash"]),
            output_name=str(payload["outputName"]),
        )
    except AgentRuntimeError as error:
        raise _refuse(error) from None
    return record.agent_run_id


@activity.defn(name="iacode_agent_runtime_finish_stage")
async def finish_stage(payload: dict[str, Any]) -> None:
    context = get_context()
    try:
        await context.store.finish_stage(str(payload["agentRunId"]), StageCompletion(
            state=str(payload["state"]),
            output=str(payload.get("output") or ""),
            output_summary=str(payload.get("outputSummary") or ""),
            turns=int(payload.get("turns") or 0),
            model_calls=int(payload.get("modelCalls") or 0),
            error_type=payload.get("errorType"),
            error_summary=payload.get("errorSummary"),
        ))
    except AgentRuntimeError as error:
        raise _refuse(error) from None


@activity.defn(name="iacode_agent_runtime_call_model")
async def call_model(payload: dict[str, Any]) -> dict[str, Any]:
    """One turn, through the Model Gateway and through nothing else."""
    context = get_context()
    from iacode_agent_runtime.contracts import TurnRequest

    request = TurnRequest(
        run_id=str(payload["runId"]),
        stage_index=int(payload["stageIndex"]),
        turn=int(payload["turn"]),
        instructions=str(payload["instructions"]),
        data=str(payload["data"]),
        route=payload.get("route"),
        model=payload.get("model"),
        allowed_actions=tuple(payload.get("allowedActions") or ()),
        structured_output=bool(payload.get("structuredOutput")),
        repair_of=payload.get("repairOf"),
    )
    try:
        outcome = await context.model_client.complete(request)
    except AgentRuntimeError as error:
        raise _refuse(error) from None
    return {"text": outcome.text, **outcome.to_dict()}


@activity.defn(name="iacode_agent_runtime_attach_model_call")
async def attach_model_call(payload: dict[str, Any]) -> str | None:
    context = get_context()
    try:
        return await context.store.attach_model_call(
            str(payload["agentRunId"]), str(payload.get("gatewayRequestId") or ""))
    except AgentRuntimeError as error:
        raise _refuse(error) from None


@activity.defn(name="iacode_agent_runtime_create_tool_request")
async def create_tool_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Persist a tool request. **Nothing here executes it, and nothing resolves its name.**"""
    context = get_context()
    try:
        request = await context.store.create_tool_request(
            str(payload["runId"]),
            agent_run_id=payload.get("agentRunId"),
            name=str(payload["name"]),
            arguments=dict(payload.get("arguments") or {}),
            tool_request_id=str(payload["toolRequestId"]),
            executor=str(payload.get("executor") or TOOL_EXECUTOR_EXTERNAL),
        )
    except AgentRuntimeError as error:
        raise _refuse(error) from None
    return request.to_dict()


@activity.defn(name="iacode_agent_runtime_read_tool_result")
async def read_tool_result(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Read a result the API recorded.

    The signal carries the result too, but a signal can be lost between the API's write and the
    workflow's next step — a worker restarting at exactly the wrong moment. Reading the stored row
    is what makes the resume survive that, and it is why the durability scenario passes.
    """
    context = get_context()
    try:
        result = await context.store.tool_result_for(str(payload["toolRequestId"]))
    except AgentRuntimeError as error:
        raise _refuse(error) from None
    return result.to_dict() if result else None


@activity.defn(name="iacode_agent_runtime_resolve_tool_request")
async def resolve_tool_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Persist the sandbox's result for a tool request, through the store's own validation.

    Gate 3's sandbox answers a request by returning its result to the workflow, and the workflow
    records it here before resuming the engine. This activity is the sandbox's internal path: it
    is registered on the worker and scheduled only by `_execute_in_sandbox`, and no HTTP route
    reaches it, so its origin is ``SANDBOX`` by construction (`M1-F-002`). The store applies the
    same checks the API's endpoint gets — the request exists, belongs to this run, is owned by
    the sandbox, is still pending and the run is not terminal — and a retried delivery of the same
    result resolves the request once.
    """
    context = get_context()
    try:
        stored = await context.store.resolve_tool_request(
            str(payload["runId"]), ToolResult.from_dict(dict(payload["result"])),
            origin=TOOL_EXECUTOR_SANDBOX)
    except AgentRuntimeError as error:
        raise _refuse(error) from None
    return stored.to_dict()


@activity.defn(name="iacode_agent_runtime_cancel_pending_tool_requests")
async def cancel_pending_tool_requests(payload: dict[str, Any]) -> int:
    context = get_context()
    try:
        return await context.store.cancel_pending_tool_requests(str(payload["runId"]))
    except AgentRuntimeError as error:
        raise _refuse(error) from None


def tool_result_from(payload: dict[str, Any]) -> ToolResult:
    """Rebuild a tool result from what crossed the workflow boundary."""
    return ToolResult.from_dict(payload)


#: Everything the worker registers. One list, so a new activity cannot be written and forgotten.
AGENT_RUNTIME_ACTIVITIES = [
    record_event,
    set_run_state,
    start_stage,
    finish_stage,
    call_model,
    attach_model_call,
    create_tool_request,
    read_tool_result,
    resolve_tool_request,
    cancel_pending_tool_requests,
]
