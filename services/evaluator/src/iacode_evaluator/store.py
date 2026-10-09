"""Durable quality facts with idempotency and event-before-state transitions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any, Protocol

from iacode_common.identifiers import uuid7
from iacode_contracts.quality import (
    QUALITY_RESULT_ORIGIN,
    QUALITY_RUN_EVENT_TYPES,
    QUALITY_RUN_STATES,
    QUALITY_TERMINAL_RUN_STATES,
    QualityPlan,
    QualityResult,
    QualityVerdict,
)

from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.verdict import verdict_digest

TRANSITIONS: dict[str, frozenset[str]] = {
    "CREATED": frozenset({"PLANNED", "CANCELLED", "INVALID"}),
    "PLANNED": frozenset({"QUEUED", "CANCELLED", "INVALID"}),
    "QUEUED": frozenset({"RUNNING", "CANCELLING", "FAILED", "TIMED_OUT", "INVALID"}),
    "RUNNING": frozenset({"CANCELLING", "SUCCEEDED", "FAILED", "TIMED_OUT", "INVALID"}),
    "CANCELLING": frozenset({"CANCELLED", "FAILED", "TIMED_OUT", "INVALID"}),
}


def _result_state_error(state: str) -> QualityError:
    if state == "CANCELLING" or state in QUALITY_TERMINAL_RUN_STATES:
        return QualityError("LATE_RESULT", "a late result callback is refused after execution")
    return QualityError("EARLY_RESULT", "a non-running quality run refuses results")


@dataclass(frozen=True)
class PlanRecord:
    storage_id: str
    plan: QualityPlan
    owner_run_id: str | None


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    plan_id: str
    owner_run_id: str | None
    state: str
    idempotency_key: str
    workflow_id: str | None = None
    reproduction_of_run_id: str | None = None
    terminal_reason: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancel_requested: bool = False
    created_at: datetime | None = None


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    run_id: str
    sequence: int
    event_type: str
    dedupe_key: str
    payload: dict[str, Any]
    created_at: datetime


class QualityStore(Protocol):
    async def create_plan(
        self, plan: QualityPlan, *, owner_run_id: str | None = None
    ) -> PlanRecord: ...

    async def create_run(
        self,
        *,
        plan_id: str,
        owner_run_id: str | None,
        idempotency_key: str,
        reproduction_of_run_id: str | None = None,
    ) -> RunRecord: ...

    async def run(self, run_id: str) -> RunRecord | None: ...

    async def plan_for_run(self, run_id: str) -> PlanRecord | None: ...

    async def results_for_run(self, run_id: str) -> tuple[QualityResult, ...]: ...

    async def verdict_for_run(self, run_id: str) -> QualityVerdict | None: ...

    async def events(
        self, run_id: str, *, after: int = 0, limit: int = 100
    ) -> list[EventRecord]: ...


def _now() -> datetime:
    return datetime.now(UTC)


class MemoryQualityStore:
    """Behavioral store double enforcing the same immutable/idempotent rules as SQL."""

    def __init__(self, now: Any = None) -> None:
        self.now = now or _now
        self.plans: dict[str, PlanRecord] = {}
        self.runs: dict[str, RunRecord] = {}
        self.idempotency: dict[str, str] = {}
        self._events: dict[str, list[EventRecord]] = {}
        self._event_dedupe: dict[tuple[str, str], EventRecord] = {}
        self.results: dict[tuple[str, str], QualityResult] = {}
        self.callbacks: dict[str, QualityResult] = {}
        self.verdicts: dict[str, QualityVerdict] = {}

    async def create_plan(
        self, plan: QualityPlan, *, owner_run_id: str | None = None
    ) -> PlanRecord:
        existing = self.plans.get(plan.planId)
        candidate = PlanRecord(str(uuid7()), plan, owner_run_id)
        if existing is not None:
            if existing.plan != plan or existing.owner_run_id != owner_run_id:
                raise QualityError("PLAN_ID_CONFLICT", "the plan digest names different content")
            return existing
        self.plans[plan.planId] = candidate
        return candidate

    async def create_run(
        self,
        *,
        plan_id: str,
        owner_run_id: str | None,
        idempotency_key: str,
        reproduction_of_run_id: str | None = None,
    ) -> RunRecord:
        plan_record = self.plans.get(plan_id)
        if plan_record is None:
            raise QualityError("PLAN_NOT_FOUND", "the quality plan does not exist")
        existing_id = self.idempotency.get(idempotency_key)
        if existing_id:
            existing = self.runs[existing_id]
            if (
                existing.plan_id != plan_record.storage_id
                or existing.owner_run_id != owner_run_id
                or existing.reproduction_of_run_id != reproduction_of_run_id
            ):
                raise QualityError(
                    "IDEMPOTENCY_CONFLICT", "the key is already bound to another quality run"
                )
            return existing
        run_id = str(uuid7())
        run = RunRecord(
            run_id=run_id,
            plan_id=plan_record.storage_id,
            owner_run_id=owner_run_id,
            state="CREATED",
            idempotency_key=idempotency_key,
            reproduction_of_run_id=reproduction_of_run_id,
            created_at=self.now(),
        )
        self.runs[run_id] = run
        self.idempotency[idempotency_key] = run_id
        await self.append_event(
            run_id,
            event_type="CREATED",
            dedupe_key=f"run-created:{idempotency_key}",
            payload={"planId": plan_id},
        )
        return run

    async def run(self, run_id: str) -> RunRecord | None:
        return self.runs.get(run_id)

    async def plan_for_run(self, run_id: str) -> PlanRecord | None:
        run = self.runs.get(run_id)
        if run is None:
            return None
        return next((item for item in self.plans.values() if item.storage_id == run.plan_id), None)

    async def results_for_run(self, run_id: str) -> tuple[QualityResult, ...]:
        return tuple(
            result for (stored_run_id, _), result in self.results.items() if stored_run_id == run_id
        )

    async def verdict_for_run(self, run_id: str) -> QualityVerdict | None:
        return self.verdicts.get(run_id)

    async def append_event(
        self,
        run_id: str,
        *,
        event_type: str,
        dedupe_key: str,
        payload: dict[str, Any],
    ) -> EventRecord:
        if event_type not in QUALITY_RUN_EVENT_TYPES:
            raise QualityError("EVENT_TYPE_UNKNOWN", f"unknown quality event: {event_type}")
        key = (run_id, dedupe_key)
        existing = self._event_dedupe.get(key)
        if existing is not None:
            if existing.event_type != event_type or existing.payload != payload:
                raise QualityError(
                    "EVENT_DEDUPE_CONFLICT", "the dedupe key names a different event"
                )
            return existing
        if run_id not in self.runs:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        sequence = len(self._events.setdefault(run_id, [])) + 1
        event = EventRecord(
            event_id=str(uuid7()),
            run_id=run_id,
            sequence=sequence,
            event_type=event_type,
            dedupe_key=dedupe_key,
            payload=dict(payload),
            created_at=self.now(),
        )
        self._events[run_id].append(event)
        self._event_dedupe[key] = event
        return event

    async def transition(
        self,
        run_id: str,
        *,
        state: str,
        event_type: str,
        dedupe_key: str,
        payload: dict[str, Any],
        reason: str | None = None,
    ) -> RunRecord:
        run = self.runs.get(run_id)
        if run is None:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        if state == run.state:
            await self.append_event(
                run_id,
                event_type=event_type,
                dedupe_key=dedupe_key,
                payload=payload,
            )
            return run
        if state not in TRANSITIONS.get(run.state, frozenset()):
            raise QualityError(
                "RUN_TRANSITION_INVALID", f"quality run cannot transition {run.state} -> {state}"
            )
        if state in QUALITY_TERMINAL_RUN_STATES and not reason:
            raise QualityError("TERMINAL_REASON_REQUIRED", "a terminal state requires its reason")
        await self.append_event(
            run_id, event_type=event_type, dedupe_key=dedupe_key, payload=payload
        )
        instant = self.now()
        updated = replace(
            run,
            state=state,
            terminal_reason=reason if state in QUALITY_TERMINAL_RUN_STATES else run.terminal_reason,
            started_at=instant if state == "RUNNING" and run.started_at is None else run.started_at,
            finished_at=instant if state in QUALITY_TERMINAL_RUN_STATES else None,
            cancel_requested=state == "CANCELLING" or run.cancel_requested,
        )
        self.runs[run_id] = updated
        return updated

    async def record_result(
        self,
        result: QualityResult,
        *,
        callback_key: str,
        owner_run_id: str | None,
    ) -> QualityResult:
        callback = self.callbacks.get(callback_key)
        if callback is not None:
            if callback != result:
                raise QualityError(
                    "CALLBACK_IDEMPOTENCY_CONFLICT", "the callback key names a different result"
                )
            return callback
        run = self.runs.get(result.runId)
        if run is None:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        if run.owner_run_id != owner_run_id:
            raise QualityError("RUN_OWNER_MISMATCH", "the result owner does not own the run")
        if result.origin != QUALITY_RESULT_ORIGIN:
            raise QualityError("RESULT_ORIGIN_MISMATCH", "only the evaluator may record a result")
        if run.state != "RUNNING":
            raise _result_state_error(run.state)
        key = (result.runId, result.checkId)
        existing = self.results.get(key)
        if existing is not None and existing != result:
            raise QualityError("RESULT_ALREADY_RECORDED", "the check already has a result")
        self.results[key] = result
        self.callbacks[callback_key] = result
        await self.append_event(
            result.runId,
            event_type="CHECK_RECORDED",
            dedupe_key=f"result:{callback_key}",
            payload={
                "checkId": result.checkId,
                "resultDigest": digest(result.model_dump(mode="json")),
            },
        )
        return result

    async def record_verdict(self, verdict: QualityVerdict) -> QualityVerdict:
        existing = self.verdicts.get(verdict.runId)
        if existing is not None:
            if existing != verdict:
                raise QualityError(
                    "VERDICT_REDERIVATION_MISMATCH",
                    "the re-derived verdict differs from the immutable verdict",
                )
            return existing
        run = self.runs.get(verdict.runId)
        if run is None:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        if run.state != "RUNNING":
            raise QualityError(
                "VERDICT_RUN_NOT_ACTIVE", "a verdict can be recorded only for a running run"
            )
        plan = next((item for item in self.plans.values() if item.storage_id == run.plan_id), None)
        if plan is None or plan.plan.planId != verdict.planId:
            raise QualityError(
                "VERDICT_PLAN_MISMATCH", "the verdict does not belong to the run plan"
            )
        if verdict_digest(verdict) != verdict.digest:
            raise QualityError("VERDICT_DIGEST_MISMATCH", "the verdict digest is not canonical")
        self.verdicts[verdict.runId] = verdict
        await self.append_event(
            verdict.runId,
            event_type="VERDICT_DERIVED",
            dedupe_key=f"verdict:{verdict.digest}",
            payload={"verdict": verdict.verdict, "digest": verdict.digest},
        )
        return verdict

    async def events(self, run_id: str, *, after: int = 0, limit: int = 100) -> list[EventRecord]:
        if limit < 1 or limit > 500:
            raise QualityError("PAGE_LIMIT_INVALID", "event limit must be between 1 and 500")
        return [item for item in self._events.get(run_id, []) if item.sequence > after][:limit]


class SqlQualityStore:
    """PostgreSQL implementation; immutable rows are inserted, never updated."""

    def __init__(self, session_factory: Any, now: Any = None) -> None:
        self.session_factory = session_factory
        self.now = now or _now

    async def create_plan(
        self, plan: QualityPlan, *, owner_run_id: str | None = None
    ) -> PlanRecord:
        from iacode_persistence.models import QualityCheck as CheckRow
        from iacode_persistence.models import QualityPlan as PlanRow
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError

        row_id = uuid7()
        body = plan.model_dump(mode="json")
        row = PlanRow(
            id=row_id,
            owner_task_run_id=uuid.UUID(owner_run_id) if owner_run_id else None,
            snapshot_artifact_id=uuid.UUID(plan.snapshotId),
            plan_digest=plan.planId,
            snapshot_digest=plan.snapshotDigest,
            project_profile=plan.projectProfile,
            project_profile_digest=plan.projectProfileDigest,
            policy_id=plan.policy.policyId,
            policy_version=plan.policy.version,
            policy_digest=plan.policy.digest,
            content=body,
        )
        checks = [
            CheckRow(
                quality_plan_id=row_id,
                check_id=check.checkId,
                ordinal=ordinal,
                kind=check.kind,
                runner=check.runner,
                content=check.model_dump(mode="json"),
            )
            for ordinal, check in enumerate(plan.checks, start=1)
        ]
        try:
            async with self.session_factory() as session, session.begin():
                session.add(row)
                await session.flush()
                session.add_all(checks)
        except IntegrityError as error:
            async with self.session_factory() as session:
                existing = (
                    (
                        await session.execute(
                            select(PlanRow).where(PlanRow.plan_digest == plan.planId)
                        )
                    )
                    .scalars()
                    .first()
                )
            if existing is None:
                constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
                raise QualityError(
                    "PLAN_PERSISTENCE_REJECTED",
                    "the database rejected the quality plan"
                    + (f" at {constraint}" if constraint else ""),
                ) from error
            actual_owner = str(existing.owner_task_run_id) if existing.owner_task_run_id else None
            if existing.content != body or actual_owner != owner_run_id:
                raise QualityError(
                    "PLAN_ID_CONFLICT", "the plan digest names different content"
                ) from None
            return PlanRecord(str(existing.id), plan, actual_owner)
        return PlanRecord(str(row_id), plan, owner_run_id)

    @staticmethod
    def _run_record(row: Any) -> RunRecord:
        return RunRecord(
            run_id=str(row.id),
            plan_id=str(row.quality_plan_id),
            owner_run_id=str(row.owner_task_run_id) if row.owner_task_run_id else None,
            state=row.state,
            idempotency_key=row.idempotency_key,
            workflow_id=row.workflow_id,
            reproduction_of_run_id=(
                str(row.reproduction_of_run_id) if row.reproduction_of_run_id else None
            ),
            terminal_reason=row.terminal_reason,
            started_at=row.started_at,
            finished_at=row.finished_at,
            cancel_requested=row.cancel_requested,
            created_at=row.created_at,
        )

    async def create_run(
        self,
        *,
        plan_id: str,
        owner_run_id: str | None,
        idempotency_key: str,
        reproduction_of_run_id: str | None = None,
    ) -> RunRecord:
        from iacode_persistence.models import QualityPlan as PlanRow
        from iacode_persistence.models import QualityRun as RunRow
        from iacode_persistence.models import QualityRunEvent
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError

        identifier = uuid7()
        async with self.session_factory() as session:
            plan_row = (
                (await session.execute(select(PlanRow).where(PlanRow.plan_digest == plan_id)))
                .scalars()
                .first()
            )
        if plan_row is None:
            raise QualityError("PLAN_NOT_FOUND", "the quality plan does not exist")
        row = RunRow(
            id=identifier,
            quality_plan_id=plan_row.id,
            owner_task_run_id=uuid.UUID(owner_run_id) if owner_run_id else None,
            reproduction_of_run_id=(
                uuid.UUID(reproduction_of_run_id) if reproduction_of_run_id else None
            ),
            state="CREATED",
            idempotency_key=idempotency_key,
        )
        event = QualityRunEvent(
            quality_run_id=identifier,
            sequence=1,
            event_type="CREATED",
            dedupe_key=f"run-created:{idempotency_key}",
            payload={"planId": plan_id},
        )
        try:
            async with self.session_factory() as session, session.begin():
                session.add(row)
                await session.flush()
                session.add(event)
        except IntegrityError:
            async with self.session_factory() as session:
                existing = (
                    (
                        await session.execute(
                            select(RunRow).where(RunRow.idempotency_key == idempotency_key)
                        )
                    )
                    .scalars()
                    .first()
                )
            if existing is None:
                raise
            record = self._run_record(existing)
            if (
                record.plan_id != str(plan_row.id)
                or record.owner_run_id != owner_run_id
                or record.reproduction_of_run_id != reproduction_of_run_id
            ):
                raise QualityError(
                    "IDEMPOTENCY_CONFLICT", "the key is already bound to another quality run"
                ) from None
            return record
        return self._run_record(row)

    async def append_event(
        self,
        run_id: str,
        *,
        event_type: str,
        dedupe_key: str,
        payload: dict[str, Any],
    ) -> EventRecord:
        from iacode_persistence.models import QualityRun as RunRow
        from iacode_persistence.models import QualityRunEvent
        from sqlalchemy import func, select
        from sqlalchemy.exc import IntegrityError

        if event_type not in QUALITY_RUN_EVENT_TYPES:
            raise QualityError("EVENT_TYPE_UNKNOWN", f"unknown quality event: {event_type}")
        event_id = uuid7()
        try:
            async with self.session_factory() as session, session.begin():
                run = await session.get(RunRow, uuid.UUID(run_id), with_for_update=True)
                if run is None:
                    raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
                existing = (
                    (
                        await session.execute(
                            select(QualityRunEvent).where(
                                QualityRunEvent.quality_run_id == run.id,
                                QualityRunEvent.dedupe_key == dedupe_key,
                            )
                        )
                    )
                    .scalars()
                    .first()
                )
                if existing is not None:
                    if existing.event_type != event_type or existing.payload != payload:
                        raise QualityError(
                            "EVENT_DEDUPE_CONFLICT", "the dedupe key names a different event"
                        )
                    return EventRecord(
                        event_id=str(existing.id),
                        run_id=run_id,
                        sequence=existing.sequence,
                        event_type=existing.event_type,
                        dedupe_key=existing.dedupe_key,
                        payload=dict(existing.payload),
                        created_at=existing.created_at,
                    )
                sequence = (
                    int(
                        (
                            await session.execute(
                                select(func.coalesce(func.max(QualityRunEvent.sequence), 0)).where(
                                    QualityRunEvent.quality_run_id == run.id
                                )
                            )
                        ).scalar_one()
                    )
                    + 1
                )
                row = QualityRunEvent(
                    id=event_id,
                    quality_run_id=run.id,
                    sequence=sequence,
                    event_type=event_type,
                    dedupe_key=dedupe_key,
                    payload=dict(payload),
                )
                session.add(row)
        except IntegrityError:
            raise QualityError(
                "EVENT_WRITE_CONFLICT", "the quality event could not be appended uniquely"
            ) from None
        return EventRecord(
            event_id, run_id, sequence, event_type, dedupe_key, dict(payload), self.now()
        )

    async def transition(
        self,
        run_id: str,
        *,
        state: str,
        event_type: str,
        dedupe_key: str,
        payload: dict[str, Any],
        reason: str | None = None,
    ) -> RunRecord:
        from iacode_persistence.models import QualityRun as RunRow
        from iacode_persistence.models import QualityRunEvent
        from sqlalchemy import func, select

        if state not in QUALITY_RUN_STATES or event_type not in QUALITY_RUN_EVENT_TYPES:
            raise QualityError("RUN_TRANSITION_INVALID", "the target state or event is unknown")
        async with self.session_factory() as session, session.begin():
            row = await session.get(RunRow, uuid.UUID(run_id), with_for_update=True)
            if row is None:
                raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
            if state != row.state and state not in TRANSITIONS.get(row.state, frozenset()):
                raise QualityError(
                    "RUN_TRANSITION_INVALID",
                    f"quality run cannot transition {row.state} -> {state}",
                )
            if state in QUALITY_TERMINAL_RUN_STATES and not reason:
                raise QualityError(
                    "TERMINAL_REASON_REQUIRED", "a terminal state requires its reason"
                )
            existing = (
                (
                    await session.execute(
                        select(QualityRunEvent).where(
                            QualityRunEvent.quality_run_id == row.id,
                            QualityRunEvent.dedupe_key == dedupe_key,
                        )
                    )
                )
                .scalars()
                .first()
            )
            if existing is None:
                sequence = (
                    int(
                        (
                            await session.execute(
                                select(func.coalesce(func.max(QualityRunEvent.sequence), 0)).where(
                                    QualityRunEvent.quality_run_id == row.id
                                )
                            )
                        ).scalar_one()
                    )
                    + 1
                )
                session.add(
                    QualityRunEvent(
                        quality_run_id=row.id,
                        sequence=sequence,
                        event_type=event_type,
                        dedupe_key=dedupe_key,
                        payload=dict(payload),
                    )
                )
                await session.flush()
            elif existing.event_type != event_type or existing.payload != payload:
                raise QualityError(
                    "EVENT_DEDUPE_CONFLICT", "the dedupe key names a different event"
                )
            if state != row.state:
                instant = self.now()
                row.state = state
                row.version = (row.version or 1) + 1
                if state == "RUNNING" and row.started_at is None:
                    row.started_at = instant
                if state == "CANCELLING":
                    row.cancel_requested = True
                if state in QUALITY_TERMINAL_RUN_STATES:
                    row.terminal_reason = reason
                    row.finished_at = instant
        return await self.run(run_id)  # type: ignore[return-value]

    async def record_result(
        self,
        result: QualityResult,
        *,
        callback_key: str,
        owner_run_id: str | None,
    ) -> QualityResult:
        from iacode_persistence.models import QualityCheck as CheckRow
        from iacode_persistence.models import QualityFinding as FindingRow
        from iacode_persistence.models import QualityResult as ResultRow
        from iacode_persistence.models import QualityRun as RunRow
        from iacode_persistence.models import QualityRunEvent
        from sqlalchemy import func, select
        from sqlalchemy.exc import IntegrityError

        body = result.model_dump(mode="json")
        result_digest = digest(body)
        try:
            async with self.session_factory() as session, session.begin():
                run = await session.get(RunRow, uuid.UUID(result.runId), with_for_update=True)
                if run is None:
                    raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
                actual_owner = str(run.owner_task_run_id) if run.owner_task_run_id else None
                if actual_owner != owner_run_id:
                    raise QualityError(
                        "RUN_OWNER_MISMATCH", "the result owner does not own the run"
                    )
                if result.origin != QUALITY_RESULT_ORIGIN:
                    raise QualityError(
                        "RESULT_ORIGIN_MISMATCH", "only the evaluator may record a result"
                    )
                if run.state != "RUNNING":
                    raise _result_state_error(run.state)
                callback = (
                    (
                        await session.execute(
                            select(ResultRow).where(ResultRow.callback_key == callback_key)
                        )
                    )
                    .scalars()
                    .first()
                )
                if callback is not None:
                    if callback.result_digest != result_digest:
                        raise QualityError(
                            "CALLBACK_IDEMPOTENCY_CONFLICT",
                            "the callback key names a different result",
                        )
                    return result
                check = (
                    (
                        await session.execute(
                            select(CheckRow).where(
                                CheckRow.quality_plan_id == run.quality_plan_id,
                                CheckRow.check_id == result.checkId,
                            )
                        )
                    )
                    .scalars()
                    .first()
                )
                if check is None:
                    raise QualityError(
                        "CHECK_NOT_PLANNED", "the result check is not in the frozen plan"
                    )
                row = ResultRow(
                    quality_run_id=run.id,
                    quality_check_id=check.id,
                    result_id=result.resultId,
                    result_digest=result_digest,
                    callback_key=callback_key,
                    origin=result.origin,
                    status=result.status,
                    sandbox_session_id=uuid.UUID(result.sandboxId) if result.sandboxId else None,
                    exit_code=result.exitCode,
                    duration_ms=result.durationMs,
                    timed_out=result.timedOut,
                    truncated=result.truncated,
                    summary=result.summary,
                    content=body,
                )
                session.add(row)
                await session.flush()
                session.add_all(
                    [
                        FindingRow(
                            quality_run_id=run.id,
                            quality_result_id=row.id,
                            finding_id=finding.findingId,
                            check_id=finding.checkId,
                            severity=finding.severity,
                            category=finding.category,
                            fingerprint=finding.fingerprint,
                            message=finding.message,
                            location=finding.location,
                            recurrence_count=finding.recurrenceCount,
                            evidence_ids=list(finding.evidenceIds),
                        )
                        for finding in result.findings
                    ]
                )
                sequence = (
                    int(
                        (
                            await session.execute(
                                select(func.coalesce(func.max(QualityRunEvent.sequence), 0)).where(
                                    QualityRunEvent.quality_run_id == run.id
                                )
                            )
                        ).scalar_one()
                    )
                    + 1
                )
                session.add(
                    QualityRunEvent(
                        quality_run_id=run.id,
                        sequence=sequence,
                        event_type="CHECK_RECORDED",
                        dedupe_key=f"result:{callback_key}",
                        payload={"checkId": result.checkId, "resultDigest": result_digest},
                    )
                )
        except IntegrityError:
            raise QualityError(
                "RESULT_ALREADY_RECORDED", "the check already has a result"
            ) from None
        return result

    async def record_verdict(self, verdict: QualityVerdict) -> QualityVerdict:
        from iacode_persistence.models import QualityPlan as PlanRow
        from iacode_persistence.models import QualityRun as RunRow
        from iacode_persistence.models import QualityRunEvent
        from iacode_persistence.models import QualityVerdict as VerdictRow
        from sqlalchemy import func, select
        from sqlalchemy.exc import IntegrityError

        body = verdict.model_dump(mode="json")
        try:
            async with self.session_factory() as session, session.begin():
                run = await session.get(RunRow, uuid.UUID(verdict.runId), with_for_update=True)
                if run is None:
                    raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
                existing = (
                    (
                        await session.execute(
                            select(VerdictRow).where(VerdictRow.quality_run_id == run.id)
                        )
                    )
                    .scalars()
                    .first()
                )
                if existing is not None:
                    if existing.digest != verdict.digest or existing.content != body:
                        raise QualityError(
                            "VERDICT_REDERIVATION_MISMATCH",
                            "the re-derived verdict differs from the immutable verdict",
                        )
                    return verdict
                if run.state != "RUNNING":
                    raise QualityError(
                        "VERDICT_RUN_NOT_ACTIVE",
                        "a verdict can be recorded only for a running run",
                    )
                plan = await session.get(PlanRow, run.quality_plan_id)
                if plan is None or plan.plan_digest != verdict.planId:
                    raise QualityError(
                        "VERDICT_PLAN_MISMATCH", "the verdict does not belong to the run plan"
                    )
                if verdict_digest(verdict) != verdict.digest:
                    raise QualityError(
                        "VERDICT_DIGEST_MISMATCH", "the verdict digest is not canonical"
                    )
                session.add(
                    VerdictRow(
                        quality_run_id=run.id,
                        verdict=verdict.verdict,
                        digest=verdict.digest,
                        content=body,
                    )
                )
                await session.flush()
                sequence = (
                    int(
                        (
                            await session.execute(
                                select(func.coalesce(func.max(QualityRunEvent.sequence), 0)).where(
                                    QualityRunEvent.quality_run_id == run.id
                                )
                            )
                        ).scalar_one()
                    )
                    + 1
                )
                session.add(
                    QualityRunEvent(
                        quality_run_id=run.id,
                        sequence=sequence,
                        event_type="VERDICT_DERIVED",
                        dedupe_key=f"verdict:{verdict.digest}",
                        payload={"verdict": verdict.verdict, "digest": verdict.digest},
                    )
                )
        except IntegrityError:
            raise QualityError(
                "VERDICT_WRITE_CONFLICT", "the quality verdict already exists"
            ) from None
        return verdict

    async def run(self, run_id: str) -> RunRecord | None:
        from iacode_persistence.models import QualityRun as RunRow

        async with self.session_factory() as session:
            row = await session.get(RunRow, uuid.UUID(run_id))
        return self._run_record(row) if row else None

    async def plan_for_run(self, run_id: str) -> PlanRecord | None:
        from iacode_persistence.models import QualityPlan as PlanRow
        from iacode_persistence.models import QualityRun as RunRow
        from sqlalchemy import select

        statement = (
            select(PlanRow)
            .join(RunRow, RunRow.quality_plan_id == PlanRow.id)
            .where(RunRow.id == uuid.UUID(run_id))
        )
        async with self.session_factory() as session:
            row = (await session.execute(statement)).scalars().first()
        if row is None:
            return None
        return PlanRecord(
            storage_id=str(row.id),
            plan=QualityPlan.model_validate(row.content),
            owner_run_id=str(row.owner_task_run_id) if row.owner_task_run_id else None,
        )

    async def results_for_run(self, run_id: str) -> tuple[QualityResult, ...]:
        from iacode_persistence.models import QualityResult as ResultRow
        from sqlalchemy import select

        statement = (
            select(ResultRow)
            .where(ResultRow.quality_run_id == uuid.UUID(run_id))
            .order_by(ResultRow.created_at, ResultRow.id)
        )
        async with self.session_factory() as session:
            rows = (await session.execute(statement)).scalars().all()
        return tuple(QualityResult.model_validate(row.content) for row in rows)

    async def verdict_for_run(self, run_id: str) -> QualityVerdict | None:
        from iacode_persistence.models import QualityVerdict as VerdictRow
        from sqlalchemy import select

        statement = select(VerdictRow).where(VerdictRow.quality_run_id == uuid.UUID(run_id))
        async with self.session_factory() as session:
            row = (await session.execute(statement)).scalars().first()
        return QualityVerdict.model_validate(row.content) if row else None

    async def events(self, run_id: str, *, after: int = 0, limit: int = 100) -> list[EventRecord]:
        from iacode_persistence.models import QualityRunEvent
        from sqlalchemy import select

        if limit < 1 or limit > 500:
            raise QualityError("PAGE_LIMIT_INVALID", "event limit must be between 1 and 500")
        statement = (
            select(QualityRunEvent)
            .where(
                QualityRunEvent.quality_run_id == uuid.UUID(run_id),
                QualityRunEvent.sequence > after,
            )
            .order_by(QualityRunEvent.sequence)
            .limit(limit)
        )
        async with self.session_factory() as session:
            rows = (await session.execute(statement)).scalars().all()
        return [
            EventRecord(
                event_id=str(row.id),
                run_id=str(row.quality_run_id),
                sequence=row.sequence,
                event_type=row.event_type,
                dedupe_key=row.dedupe_key,
                payload=dict(row.payload),
                created_at=row.created_at,
            )
            for row in rows
        ]
