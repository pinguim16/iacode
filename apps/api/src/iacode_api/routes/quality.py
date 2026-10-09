"""Bounded HTTP lifecycle for durable Quality Engine runs."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, FastAPI, Query, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from iacode_contracts.foundation import ErrorResponse
from iacode_contracts.quality import (
    QUALITY_CANCEL_SIGNAL,
    QUALITY_RUN_WORKFLOW,
    QUALITY_TERMINAL_RUN_STATES,
    CreateQualityRunRequest,
    QualityCheckSummary,
    QualityPlan,
    QualityRunCreated,
    QualityRunDetail,
    QualityRunEvent,
    QualityRunEventPage,
    QualityRunList,
    QualityRunSummary,
    ReproduceQualityRunRequest,
)
from iacode_evaluator.errors import QualityError
from iacode_telemetry.context import get_correlation_id
from iacode_telemetry.logging import get_logger

from iacode_api.dependencies import get_resources

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/quality-runs", tags=["quality"])
EVENT_PAGE_SIZE = 200


def workflow_id_for(run_id: str) -> str:
    return f"iacode-quality-run-{run_id}"


def _status(code: str) -> int:
    if code in {"RUN_NOT_FOUND", "PLAN_NOT_FOUND"}:
        return status.HTTP_404_NOT_FOUND
    if code in {"SNAPSHOT_NOT_AUTHORISED"}:
        return status.HTTP_403_FORBIDDEN
    if code.endswith("CONFLICT") or code in {
        "RUN_TRANSITION_INVALID",
        "REPRODUCTION_SOURCE_ACTIVE",
        "LATE_RESULT",
    }:
        return status.HTTP_409_CONFLICT
    if code in {"EVIDENCE_STORE_UNAVAILABLE"}:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_400_BAD_REQUEST


def register_quality_errors(app: FastAPI) -> None:
    @app.exception_handler(QualityError)
    async def _handle(request: Request, error: QualityError) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
        body = ErrorResponse(
            code=error.code,
            message=str(error),
            correlationId=correlation_id,
        )
        response = JSONResponse(
            status_code=_status(error.code), content=body.model_dump(mode="json")
        )
        if correlation_id:
            response.headers[request.app.state.settings.correlation_header] = correlation_id
        return response


def _checks(plan: QualityPlan) -> tuple[QualityCheckSummary, ...]:
    return tuple(
        QualityCheckSummary(
            checkId=check.checkId,
            kind=check.kind,
            mandatory=check.mandatory,
            applicable=check.applicable,
            applicabilityReason=check.applicabilityReason,
        )
        for check in plan.checks
    )


async def _summary(resources: Any, run: Any) -> QualityRunSummary:
    plan = await resources.quality.store.plan_for_run(run.run_id)
    if plan is None:
        raise QualityError("PLAN_NOT_FOUND", "the quality run has no frozen plan")
    verdict = await resources.quality.store.verdict_for_run(run.run_id)
    return QualityRunSummary(
        runId=run.run_id,
        planId=plan.plan.planId,
        state=run.state,
        profile=plan.plan.projectProfile,
        ownerRunId=run.owner_run_id,
        reproductionOfRunId=run.reproduction_of_run_id,
        createdAt=run.created_at,
        finishedAt=run.finished_at,
        verdict=verdict.verdict if verdict else None,
    )


async def _start(resources: Any, run: Any, plan: QualityPlan) -> None:
    workflow_id = workflow_id_for(run.run_id)
    try:
        await resources.temporal.start_quality_run(
            workflow=QUALITY_RUN_WORKFLOW,
            workflow_id=workflow_id,
            payload={"runId": run.run_id},
            task_queue=resources.quality.task_queue,
            execution_timeout_seconds=plan.policy.maxRunSeconds + 300,
        )
        await resources.quality.store.bind_workflow(run.run_id, workflow_id)
    except Exception as error:
        await resources.quality.store.transition(
            run.run_id,
            state="INVALID",
            event_type="INVALIDATED",
            dedupe_key="api:workflow-start-failed",
            payload={"reason": "durable workflow could not be started"},
            reason="durable quality workflow could not be started",
        )
        logger.error("could not start the quality workflow", exc_info=error)
        raise QualityError(
            "QUALITY_WORKFLOW_UNAVAILABLE", "the durable quality workflow could not be started"
        ) from error


@router.post("", response_model=QualityRunCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_quality_run(
    request: Request, payload: CreateQualityRunRequest
) -> QualityRunCreated:
    resources = get_resources(request)
    if payload.policyId != "default":
        raise QualityError("QUALITY_POLICY_UNKNOWN", "only the canonical default policy exists")
    files = await resources.quality.snapshots.read(payload.snapshotId, payload.snapshotDigest)
    planned = await resources.quality.service.create_profile_and_plan(
        snapshot_id=payload.snapshotId,
        snapshot_digest=payload.snapshotDigest,
        project_files=files,
        configuration=payload.configuration,
        owner_run_id=payload.ownerRunId,
    )
    run = await resources.quality.service.start_run(
        plan_id=planned.plan.planId,
        owner_run_id=payload.ownerRunId,
        idempotency_key=payload.idempotencyKey,
    )
    replay = run.workflow_id is not None
    if not replay:
        await _start(resources, run, planned.plan)
        run = await resources.quality.store.run(run.run_id)
    return QualityRunCreated(
        runId=run.run_id,
        planId=planned.plan.planId,
        state=run.state,
        profile=planned.plan.projectProfile,
        checks=_checks(planned.plan),
        idempotentReplay=replay,
    )


@router.get("", response_model=QualityRunList)
async def list_quality_runs(
    request: Request,
    cursor: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
) -> QualityRunList:
    resources = get_resources(request)
    runs = await resources.quality.store.list_runs(after=cursor, limit=limit)
    summaries = tuple([await _summary(resources, run) for run in runs])
    return QualityRunList(
        runs=summaries,
        nextCursor=runs[-1].run_id if len(runs) == limit else None,
    )


@router.get("/{run_id}", response_model=QualityRunDetail)
async def read_quality_run(request: Request, run_id: str) -> QualityRunDetail:
    resources = get_resources(request)
    view = await resources.quality.service.get_run(run_id)
    return QualityRunDetail(
        run=await _summary(resources, view.run),
        checks=_checks(view.plan),
        results=view.results,
        findings=view.findings,
        evidence=view.evidence,
        verdict=view.verdict,
    )


async def _event_page(resources: Any, run_id: str, after: int, limit: int) -> QualityRunEventPage:
    run = await resources.quality.store.run(run_id)
    if run is None:
        raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
    events = await resources.quality.store.events(run_id, after=after, limit=limit)
    cursor = events[-1].sequence if events else after
    return QualityRunEventPage(
        events=tuple(
            QualityRunEvent(
                sequence=event.sequence,
                eventType=event.event_type,
                payload=event.payload,
                createdAt=event.created_at,
            )
            for event in events
        ),
        nextCursor=cursor,
        terminal=run.state in QUALITY_TERMINAL_RUN_STATES,
    )


@router.get("/{run_id}/events", response_model=QualityRunEventPage)
async def read_quality_events(
    request: Request,
    run_id: str,
    after: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> QualityRunEventPage:
    return await _event_page(get_resources(request), run_id, after, limit)


@router.get("/{run_id}/events/stream")
async def stream_quality_events(
    request: Request, run_id: str, after: int = Query(default=0, ge=0)
) -> StreamingResponse:
    resources = get_resources(request)
    if await resources.quality.store.run(run_id) is None:
        raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")

    async def stream() -> AsyncIterator[str]:
        cursor = after
        while True:
            page = await _event_page(resources, run_id, cursor, EVENT_PAGE_SIZE)
            for event in page.events:
                cursor = event.sequence
                yield (
                    "data: "
                    + json.dumps(event.model_dump(mode="json"), separators=(",", ":"))
                    + "\n\n"
                )
            if page.terminal and not page.events:
                return
            if not page.events:
                await asyncio.sleep(resources.settings.quality_event_stream_poll_seconds)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/{run_id}/cancel", response_model=QualityRunSummary)
async def cancel_quality_run(request: Request, run_id: str) -> QualityRunSummary:
    resources = get_resources(request)
    run = await resources.quality.service.request_cancel(
        run_id, request_id=get_correlation_id() or f"api:{run_id}"
    )
    if run.workflow_id and run.state not in QUALITY_TERMINAL_RUN_STATES:
        delivered = await resources.temporal.signal_quality_run(
            workflow_id=run.workflow_id,
            signal=QUALITY_CANCEL_SIGNAL,
            payload="operator request",
        )
        if not delivered:
            raise QualityError(
                "QUALITY_WORKFLOW_UNAVAILABLE", "the quality workflow did not accept cancellation"
            )
    return await _summary(resources, run)


@router.post("/{run_id}/reproductions", response_model=QualityRunCreated, status_code=202)
async def reproduce_quality_run(
    request: Request, run_id: str, payload: ReproduceQualityRunRequest
) -> QualityRunCreated:
    resources = get_resources(request)
    reproduced = await resources.quality.service.request_reproduction(
        run_id, idempotency_key=payload.idempotencyKey
    )
    plan_record = await resources.quality.store.plan_for_run(reproduced.run_id)
    if plan_record is None:
        raise QualityError("PLAN_NOT_FOUND", "the quality run has no frozen plan")
    replay = reproduced.workflow_id is not None
    if not replay:
        await _start(resources, reproduced, plan_record.plan)
        reproduced = await resources.quality.store.run(reproduced.run_id)
    return QualityRunCreated(
        runId=reproduced.run_id,
        planId=plan_record.plan.planId,
        state=reproduced.state,
        profile=plan_record.plan.projectProfile,
        checks=_checks(plan_record.plan),
        idempotentReplay=replay,
    )


__all__ = ["register_quality_errors", "router", "workflow_id_for"]
