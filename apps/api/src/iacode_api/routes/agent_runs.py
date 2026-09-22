"""The Agent Runtime HTTP API.

Eight endpoints under ``/api/v1``. They are a thin translation: the wire shapes in
``iacode_contracts.agent_runtime`` in, the runtime's service out, and back. Every decision that
matters — the plan, the budgets, the state machine, the tool lifecycle — happens in the runtime, so
the HTTP layer and the durable workflow cannot disagree about any of it.

Four properties this module is responsible for.

**Creation answers immediately.** A run can take minutes. The endpoint persists the run, starts the
durable workflow and returns the identifier and the state; it never holds the request open until
the run finishes, because a request that waits for a model is a request that times out.

**A failure tells a caller what it needs and nothing more.** A classified runtime error becomes the
Foundation's error contract with a stable code, a safe message, the stage that failed and the
correlation identifier. The traceback stays in the log, exactly as Gate 0 established.

**A tool result is validated against the database before it reaches the workflow.** Whether the
request exists, whether it belongs to this run, whether it is still pending and whether the run is
still alive are all answered by the store, in one transaction. Only then is the workflow signalled.
A design that signalled first and validated later would let a forged result wake a run.

**Nothing here executes a tool.** The endpoint that accepts a result is an inbox. There is no
endpoint that runs one, and the page offers no button that would.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, FastAPI, Header, Query, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.states import RunState, is_terminal
from iacode_contracts.agent_runtime import (
    AGENT_RUN_WORKFLOW,
    CANCEL_SIGNAL,
    TOOL_RESULT_SIGNAL,
    AgentProfileSummary,
    AgentRunCreated,
    AgentRunDetail,
    AgentRunListResponse,
    CreateAgentRunRequest,
    RunEventPage,
    TeamProfileSummary,
    ToolResultSubmission,
)
from iacode_contracts.foundation import ErrorResponse
from iacode_telemetry.context import get_correlation_id
from iacode_telemetry.logging import get_logger

from iacode_api.dependencies import get_resources

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["agent-runtime"])

#: How a classified runtime failure becomes an HTTP status. Written once, here, so two endpoints
#: cannot answer differently for the same failure.
HTTP_STATUS: dict[AgentRuntimeErrorType, int] = {
    AgentRuntimeErrorType.INVALID_REQUEST: status.HTTP_400_BAD_REQUEST,
    AgentRuntimeErrorType.PROFILE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    AgentRuntimeErrorType.TEAM_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    AgentRuntimeErrorType.PAYLOAD_TOO_LARGE: 413,
    AgentRuntimeErrorType.TOOL_RESULT_INVALID: status.HTTP_409_CONFLICT,
    AgentRuntimeErrorType.TOOL_NOT_PERMITTED: status.HTTP_403_FORBIDDEN,
    AgentRuntimeErrorType.INVALID_STATE_TRANSITION: status.HTTP_409_CONFLICT,
    AgentRuntimeErrorType.BUDGET_EXCEEDED: status.HTTP_409_CONFLICT,
    AgentRuntimeErrorType.CONTEXT_OVERFLOW: 413,
    AgentRuntimeErrorType.GATEWAY_ERROR: status.HTTP_502_BAD_GATEWAY,
    AgentRuntimeErrorType.TOOL_WAIT_TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
    AgentRuntimeErrorType.RUN_DEADLINE_EXCEEDED: status.HTTP_504_GATEWAY_TIMEOUT,
    AgentRuntimeErrorType.RUN_CANCELLED: status.HTTP_409_CONFLICT,
    AgentRuntimeErrorType.INVALID_AGENT_OUTPUT: status.HTTP_502_BAD_GATEWAY,
    AgentRuntimeErrorType.WORKFLOW_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
    AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

#: Detail keys safe to return. An allow-list rather than a deny-list: a key added to a failure
#: somewhere in the runtime must be considered before it reaches a response.
PUBLIC_DETAIL_KEYS = frozenset({
    "limit", "value", "maximum", "setting", "state", "stage", "team", "agent", "available",
    "requested", "permitted", "toolRequestId", "tool", "status", "what", "size", "runId",
})

#: How long an idle event stream waits before sending a keep-alive comment. A proxy that sees no
#: bytes for a minute closes the connection, and a run thinking for two minutes is normal.
KEEPALIVE_SECONDS = 15.0


def workflow_id_for(run_id: str) -> str:
    """The durable workflow's identifier, derived from the run's.

    Derived rather than stored: it means a run can always be addressed without a second lookup, and
    starting the same run twice is refused by Temporal itself.
    """
    return f"iacode-agent-run-{run_id}"


def register_agent_runtime_errors(app: FastAPI) -> None:
    """Install the handler that turns a classified runtime failure into the error contract."""

    @app.exception_handler(AgentRuntimeError)
    async def _handle(request: Request, error: AgentRuntimeError) -> JSONResponse:
        http_status = HTTP_STATUS.get(error.error_type,
                                      status.HTTP_500_INTERNAL_SERVER_ERROR)
        correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
        logger.warning("agent runtime failure", extra={
            "errorType": str(error.error_type), "stage": error.stage, "status": http_status})
        details = {key: value for key, value in error.details.items()
                   if key in PUBLIC_DETAIL_KEYS}
        if error.stage:
            details["stage"] = error.stage
        if error.upstream_type:
            details["upstreamType"] = error.upstream_type
        body = ErrorResponse(
            code=str(error.error_type),
            message=error.message,
            correlationId=correlation_id,
            details=details or None,
        )
        response = JSONResponse(status_code=http_status, content=body.model_dump(mode="json"))
        if correlation_id:
            header = getattr(getattr(request.app.state, "settings", None), "correlation_header",
                             "X-Correlation-ID")
            response.headers[header] = correlation_id
        return response


# ---------------------------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------------------------


@router.post("/agent-runs", response_model=AgentRunCreated,
             status_code=status.HTTP_202_ACCEPTED,
             summary="Create a run and start its durable workflow")
async def create_agent_run(request: Request, payload: CreateAgentRunRequest) -> AgentRunCreated:
    """Persist the run, freeze the plan and hand it to Temporal.

    ``202`` rather than ``201``: the run exists, and it has been accepted for execution that has not
    happened yet. A ``201`` would suggest the thing the caller asked for is ready.
    """
    resources = get_resources(request)
    runtime = resources.agent_runtime
    plan, created = await runtime.service.create_run(
        payload, correlation_id=get_correlation_id())
    if created.idempotentReplay:
        return created

    workflow_id = workflow_id_for(created.runId)
    try:
        await resources.temporal.start_agent_run(
            workflow=AGENT_RUN_WORKFLOW,
            workflow_id=workflow_id,
            payload=plan.to_dict(),
            task_queue=runtime.task_queue,
            execution_timeout_seconds=runtime.execution_timeout_seconds,
        )
    except AgentRuntimeError:
        raise
    except Exception as error:
        # The run row exists and the workflow does not. Recording the failure on the run is what
        # keeps the two consistent: a run stuck at CREATED with no explanation is worse than a run
        # that failed and says why.
        await runtime.store.set_run_state(
            created.runId, str(RunState.FAILED),
            error_type=str(AgentRuntimeErrorType.WORKFLOW_ERROR),
            error_summary="the durable workflow could not be started", finished=True)
        logger.error("could not start the agent run workflow", exc_info=error)
        raise AgentRuntimeError(
            AgentRuntimeErrorType.WORKFLOW_ERROR,
            "the durable workflow could not be started",
            details={"runId": created.runId}) from error

    await runtime.service.mark_queued(created.runId, workflow_id)
    return AgentRunCreated(
        runId=created.runId, taskId=created.taskId, state=str(RunState.QUEUED),
        team=created.team, createdAt=created.createdAt)


@router.get("/agent-runs", response_model=AgentRunListResponse,
            summary="The most recent runs")
async def list_agent_runs(
    request: Request,
    limit: int = Query(default=25, ge=1, le=100),
) -> AgentRunListResponse:
    runs = await get_resources(request).agent_runtime.service.list_runs(limit)
    return AgentRunListResponse(total=len(runs), runs=runs)


@router.get("/agent-runs/{run_id}", response_model=AgentRunDetail,
            summary="One run: its state, its stages, its budget and its result")
async def read_agent_run(request: Request, run_id: str) -> AgentRunDetail:
    return await get_resources(request).agent_runtime.service.detail(run_id)


@router.get("/agent-runs/{run_id}/events", response_model=RunEventPage,
            summary="A page of a run's events, from a cursor")
async def read_agent_run_events(
    request: Request,
    run_id: str,
    after: int = Query(default=0, ge=0, description="Return events after this sequence."),
    limit: int = Query(default=200, ge=1, le=1000),
) -> RunEventPage:
    return await get_resources(request).agent_runtime.service.events(
        run_id, after=after, limit=limit)


@router.get("/agent-runs/{run_id}/events/stream",
            summary="A run's events as they happen, over Server-Sent Events")
async def stream_agent_run_events(
    request: Request,
    run_id: str,
    after: int = Query(default=0, ge=0),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
) -> StreamingResponse:
    """Stream the events that follow a cursor.

    The cursor is the sequence number the store assigned, carried either as ``after`` or as the
    standard ``Last-Event-ID`` header that a browser's ``EventSource`` re-sends automatically. A
    reconnecting consumer therefore receives exactly what it has not seen — and the reconnection
    creates no event, because reading is a read.
    """
    resources = get_resources(request)
    runtime = resources.agent_runtime
    # The run is read once here so a stream for a run that does not exist fails with a status code
    # rather than with an empty stream that looks like a run doing nothing.
    detail = await runtime.service.detail(run_id)
    cursor = _cursor(after, last_event_id)

    async def events() -> AsyncIterator[str]:
        nonlocal cursor
        idle = 0.0
        finished = is_terminal(detail.state)
        while True:
            if await request.is_disconnected():
                return
            page = await runtime.service.events(run_id, after=cursor, limit=200)
            for event in page.events:
                cursor = event.sequence
                idle = 0.0
                body = json.dumps(event.model_dump(mode="json"), ensure_ascii=False)
                yield f"id: {event.sequence}\nevent: {event.type}\ndata: {body}\n\n"
                if event.type in ("RUN_COMPLETED", "RUN_FAILED", "RUN_CANCELLED"):
                    finished = True
            if finished:
                return
            await asyncio.sleep(runtime.event_poll_seconds)
            idle += runtime.event_poll_seconds
            if idle >= KEEPALIVE_SECONDS:
                idle = 0.0
                # A comment frame. It keeps a proxy from closing an idle connection and carries no
                # event, so a consumer's cursor does not move.
                yield ": keep-alive\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-store",
            # Without this an nginx or a proxy in front of the API buffers the whole response and
            # the stream arrives as one block, which looks exactly like streaming being broken.
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/agent-runs/{run_id}/cancel", response_model=AgentRunDetail,
             summary="Cancel a run")
async def cancel_agent_run(request: Request, run_id: str) -> AgentRunDetail:
    """Record the request, then tell the workflow.

    The order matters. The flag is what the engine reads between steps, so a run whose signal is
    lost still stops at its next checkpoint; signalling first and recording second would leave a
    window in which the run is cancelled and nothing says so.
    """
    resources = get_resources(request)
    runtime = resources.agent_runtime
    detail = await runtime.service.request_cancellation(run_id)
    delivered = await resources.temporal.signal_agent_run(
        workflow_id=workflow_id_for(run_id), signal=CANCEL_SIGNAL, payload="operator request")
    logger.info("agent run cancellation requested", extra={
        "runId": run_id, "signalDelivered": delivered})
    return detail


@router.post("/agent-runs/{run_id}/tool-results", response_model=AgentRunDetail,
             summary="Answer a tool request and resume the run")
async def submit_tool_result(request: Request, run_id: str,
                             payload: ToolResultSubmission) -> AgentRunDetail:
    """Accept a result from whatever is authorised to execute. **This endpoint executes nothing.**

    Gate 2 has no executor, so the authorised producer is a test fixture or the development
    simulator. From Gate 3 it is the sandbox. Either way the validation is the same and it happens
    here, against the database, before the workflow is told anything.
    """
    resources = get_resources(request)
    runtime = resources.agent_runtime
    await runtime.service.submit_tool_result(run_id, payload)
    delivered = await resources.temporal.signal_agent_run(
        workflow_id=workflow_id_for(run_id),
        signal=TOOL_RESULT_SIGNAL,
        payload=payload.model_dump(mode="json"),
    )
    logger.info("tool result accepted", extra={
        "runId": run_id, "toolRequestId": payload.toolRequestId, "signalDelivered": delivered})
    return await runtime.service.detail(run_id)


# ---------------------------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------------------------


@router.get("/agents", response_model=list[AgentProfileSummary],
            summary="The declared agent profiles")
async def list_agents(request: Request) -> list[AgentProfileSummary]:
    return get_resources(request).agent_runtime.service.agent_summaries()


@router.get("/agent-teams", response_model=list[TeamProfileSummary],
            summary="The declared teams")
async def list_agent_teams(request: Request) -> list[TeamProfileSummary]:
    return get_resources(request).agent_runtime.service.team_summaries()


def _cursor(after: int, last_event_id: str | None) -> int:
    """The larger of the two cursors a consumer may present.

    ``Last-Event-ID`` is what a browser re-sends by itself; ``after`` is what a script passes.
    Taking the larger means a consumer that supplies both cannot accidentally rewind, and a
    malformed header is ignored rather than fatal.
    """
    value = after
    if last_event_id:
        with contextlib.suppress(ValueError):
            value = max(value, int(last_event_id))
    return max(value, 0)
