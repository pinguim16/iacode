"""Quality workflow activities: all I/O and non-deterministic derivation lives here."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from iacode_common.redaction import redact_mapping, redact_text
from iacode_contracts.quality import QualityFinding, QualityResult
from iacode_telemetry.logging import get_logger
from temporalio import activity

from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.evidence import inline_summary
from iacode_evaluator.runtime import EvaluatorRuntime
from iacode_evaluator.telemetry import quality_log_fields
from iacode_evaluator.verdict import derive_verdict

logger = get_logger(__name__)

TRANSITION_ACTIVITY = "iacode_quality_transition"
READ_RUN_ACTIVITY = "iacode_quality_read_run"
READ_PLAN_ACTIVITY = "iacode_quality_read_plan"
RECORD_EXECUTION_ACTIVITY = "iacode_quality_record_execution"
DERIVE_VERDICT_ACTIVITY = "iacode_quality_derive_verdict"

_RUNTIME: EvaluatorRuntime | None = None


def set_runtime(runtime: EvaluatorRuntime | None) -> None:
    global _RUNTIME
    _RUNTIME = runtime


def _runtime() -> EvaluatorRuntime:
    if _RUNTIME is None:
        raise RuntimeError("the evaluator runtime has not been installed")
    return _RUNTIME


def _run_view(record: Any) -> dict[str, Any]:
    return {
        "runId": record.run_id,
        "planId": record.plan_id,
        "ownerRunId": record.owner_run_id,
        "state": record.state,
        "workflowId": record.workflow_id,
        "reproductionOfRunId": record.reproduction_of_run_id,
        "terminalReason": record.terminal_reason,
        "cancelRequested": record.cancel_requested,
    }


@activity.defn(name=TRANSITION_ACTIVITY)
async def transition_run(payload: dict[str, Any]) -> dict[str, Any]:
    runtime = _runtime()
    before = await runtime.store.run(str(payload["runId"]))
    if before is not None and before.finished_at is not None:
        return _run_view(before)
    record = await runtime.store.transition(
        str(payload["runId"]),
        state=str(payload["state"]),
        event_type=str(payload["eventType"]),
        dedupe_key=str(payload["dedupeKey"]),
        payload=dict(payload.get("payload") or {}),
        reason=payload.get("reason"),
    )
    if before is not None and before.state != record.state:
        if record.state == "RUNNING":
            runtime.metrics.started()
        elif record.finished_at is not None:
            runtime.metrics.completed(record.state)
    logger.info(
        "quality run transitioned",
        extra=quality_log_fields(
            correlation_id=payload.get("correlationId"),
            run_id=record.run_id,
            status=record.state,
            reason=record.terminal_reason,
        ),
    )
    return _run_view(record)


@activity.defn(name=READ_RUN_ACTIVITY)
async def read_run(payload: dict[str, Any]) -> dict[str, Any]:
    record = await _runtime().store.run(str(payload["runId"]))
    if record is None:
        raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
    return _run_view(record)


@activity.defn(name=READ_PLAN_ACTIVITY)
async def read_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan = await _runtime().store.plan_for_run(str(payload["runId"]))
    if plan is None:
        raise QualityError("PLAN_NOT_FOUND", "the quality run has no frozen plan")
    return plan.plan.model_dump(mode="json")


def _quality_status(execution: dict[str, Any]) -> str:
    return {
        "SUCCEEDED": "PASSED",
        "FAILED": "FAILED",
        "DENIED": "DENIED",
        "TIMED_OUT": "TIMED_OUT",
        "CANCELLED": "CANCELLED",
        "INTERRUPTED": "ERROR",
        "ERROR": "ERROR",
    }.get(str(execution.get("status") or ""), "ERROR")


def _result_id(run_id: str, check_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"iacode-quality-result:{run_id}:{check_id}"))


@activity.defn(name=RECORD_EXECUTION_ACTIVITY)
async def record_execution(payload: dict[str, Any]) -> dict[str, Any]:
    runtime = _runtime()
    run_id = str(payload["runId"])
    check_id = str(payload["checkId"])
    plan_record = await runtime.store.plan_for_run(run_id)
    run_record = await runtime.store.run(run_id)
    if plan_record is None or run_record is None:
        raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
    check = next((item for item in plan_record.plan.checks if item.checkId == check_id), None)
    if check is None:
        raise QualityError("CHECK_NOT_PLANNED", "the result check is not in the frozen plan")

    execution = dict(payload.get("execution") or {})
    redacted = redact_mapping(execution)
    report = json.dumps(
        {"checkId": check_id, "execution": redacted},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    result_id = _result_id(run_id, check_id)
    evidence = await runtime.evidence.put(
        run_id=run_id,
        result_id=None,
        kind=check.requiredEvidenceKinds[0],
        content=report,
        media_type="application/json",
        producer="iacode-evaluator",
        source_digests=tuple(
            dict.fromkeys((plan_record.plan.snapshotDigest, plan_record.plan.policy.digest))
        ),
    )
    status = _quality_status(execution)
    output = dict(execution.get("output") or {})
    raw_summary = str(
        execution.get("error")
        or output.get("stderr")
        or output.get("stdout")
        or f"{check.kind} check ended {status}"
    )
    summary = inline_summary(redact_text(raw_summary))[:2048]
    findings: tuple[QualityFinding, ...] = ()
    if status != "PASSED":
        finding_content = {
            "checkId": check_id,
            "status": status,
            "reason": str(execution.get("errorCode") or status),
        }
        findings = (
            QualityFinding(
                findingId=str(uuid.uuid5(uuid.NAMESPACE_URL, f"finding:{run_id}:{check_id}")),
                checkId=check_id,
                severity="HIGH" if status in {"FAILED", "ERROR", "TIMED_OUT"} else "MEDIUM",
                category=check.kind,
                fingerprint=digest(finding_content),
                message=summary or f"{check.kind} check ended {status}",
                evidenceIds=(evidence.evidenceId,),
            ),
        )
    result = QualityResult(
        resultId=result_id,
        runId=run_id,
        checkId=check_id,
        status=status,
        exitCode=execution.get("exitCode")
        if status not in {"DENIED", "CANCELLED", "ERROR"}
        else None,
        durationMs=max(0, int(execution.get("durationMs") or 0)),
        timedOut=status == "TIMED_OUT",
        truncated=bool(execution.get("truncated")),
        summary=summary,
        coveragePercent=output.get("coveragePercent"),
        sandboxId=execution.get("sessionId"),
        evidence=(evidence,),
        findings=findings,
        finishedAt=datetime.fromisoformat(str(payload["finishedAt"]).replace("Z", "+00:00")),
    )
    existing = await runtime.store.results_for_run(run_id)
    first_delivery = all(item.checkId != check_id for item in existing)
    recorded = await runtime.store.record_result(
        result,
        callback_key=f"quality:{run_id}:{check_id}",
        owner_run_id=run_record.owner_run_id,
    )
    if first_delivery:
        runtime.metrics.evidence()
        runtime.metrics.check(check.kind, recorded.status, recorded.durationMs)
        for finding in recorded.findings:
            runtime.metrics.finding(finding.severity, finding.category)
    logger.info(
        "quality check recorded",
        extra=quality_log_fields(
            correlation_id=payload.get("correlationId"),
            run_id=run_id,
            plan_id=plan_record.plan.planId,
            check_id=check_id,
            sandbox_id=recorded.sandboxId,
            status=recorded.status,
            duration_ms=recorded.durationMs,
            reason=execution.get("errorCode"),
        ),
    )
    return recorded.model_dump(mode="json")


@activity.defn(name=DERIVE_VERDICT_ACTIVITY)
async def derive_run_verdict(payload: dict[str, Any]) -> dict[str, Any]:
    runtime = _runtime()
    run_id = str(payload["runId"])
    plan_record = await runtime.store.plan_for_run(run_id)
    if plan_record is None:
        raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
    results = await runtime.store.results_for_run(run_id)
    resolved: set[str] = set()
    for result in results:
        for evidence in result.evidence:
            if await runtime.evidence.resolve(evidence):
                resolved.add(evidence.digest)
    verdict = derive_verdict(
        run_id=run_id,
        plan=plan_record.plan,
        results=results,
        resolved_evidence_digests=resolved,
        derived_at=datetime.fromisoformat(str(payload["derivedAt"]).replace("Z", "+00:00")),
    )
    existing = await runtime.store.verdict_for_run(run_id)
    recorded = await runtime.store.record_verdict(verdict)
    if existing is None:
        runtime.metrics.verdict(recorded.verdict)
    return recorded.model_dump(mode="json")


ACTIVITIES = [read_run, read_plan, transition_run, record_execution, derive_run_verdict]

__all__ = [
    "ACTIVITIES",
    "DERIVE_VERDICT_ACTIVITY",
    "READ_PLAN_ACTIVITY",
    "READ_RUN_ACTIVITY",
    "RECORD_EXECUTION_ACTIVITY",
    "TRANSITION_ACTIVITY",
    "derive_run_verdict",
    "read_plan",
    "read_run",
    "record_execution",
    "set_runtime",
    "transition_run",
]
