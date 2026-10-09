"""Immutable evidence and quality lifecycle persistence behavior."""

from __future__ import annotations

from datetime import UTC, datetime

import iacode_persistence.models  # noqa: F401
import pytest
from iacode_contracts.quality import (
    QualityCheck,
    QualityEvidence,
    QualityFinding,
    QualityPlan,
    QualityPolicy,
    QualityResult,
    QualityVerdict,
)
from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.evidence import (
    MemoryEvidenceRepository,
    MemoryObjectStore,
    QualityEvidenceStore,
    inline_summary,
)
from iacode_evaluator.store import MemoryQualityStore
from iacode_persistence.base import Base

SHA = "a" * 64
OTHER_SHA = "b" * 64
NOW = datetime(2026, 10, 9, 12, tzinfo=UTC)


def quality_plan(snapshot_id: str = "snapshot-1") -> QualityPlan:
    policy = QualityPolicy(
        policyId="default",
        version="1.0.0",
        digest=OTHER_SHA,
        profile="python",
        mandatoryCheckKinds=("unit",),
        maxRunSeconds=3600,
        maxCheckSeconds=600,
        maxOutputBytes=131072,
    )
    check = QualityCheck(
        checkId="q001-unit",
        kind="unit",
        runner="python.unit",
        command=("python", "-m", "unittest", "discover"),
        applicabilityReason="the Python profile requires unit tests",
        timeoutSeconds=600,
    )
    return QualityPlan(
        planId=SHA,
        snapshotId=snapshot_id,
        snapshotDigest=OTHER_SHA,
        projectProfile="python",
        projectProfileDigest=SHA,
        policy=policy,
        checks=(check,),
        createdAt=NOW,
    )


def result(run_id: str, *, summary: str = "unit tests passed") -> QualityResult:
    return QualityResult(
        resultId="result-1",
        runId=run_id,
        checkId="q001-unit",
        status="PASSED",
        exitCode=0,
        durationMs=10,
        summary=summary,
        finishedAt=NOW,
    )


class QualityEvidenceTests:
    @pytest.mark.asyncio
    async def test_evidence_is_content_addressed_idempotent_and_resolved(self) -> None:
        objects = MemoryObjectStore()
        repository = MemoryEvidenceRepository()
        store = QualityEvidenceStore(
            client=objects, bucket="iacode-artifacts", repository=repository, now=lambda: NOW
        )
        first = await store.put(
            run_id="run-1",
            result_id="result-1",
            kind="report",
            content=b"35 passed\n",
            media_type="text/plain",
            producer="pytest",
            source_digests=(SHA,),
        )
        second = await store.put(
            run_id="run-1",
            result_id="result-1",
            kind="report",
            content=b"35 passed\n",
            media_type="text/plain",
            producer="pytest",
            source_digests=(SHA,),
        )
        assert first == second
        assert len(repository.records) == 1 and len(objects.objects) == 1
        assert first.trainingAllowed is False
        assert await store.resolve(first)

    @pytest.mark.asyncio
    async def test_evidence_tampering_missing_bytes_and_metadata_conflicts_fail(self) -> None:
        objects = MemoryObjectStore()
        repository = MemoryEvidenceRepository()
        store = QualityEvidenceStore(
            client=objects, bucket="iacode-artifacts", repository=repository, now=lambda: NOW
        )
        evidence = await store.put(
            run_id="run-1",
            result_id=None,
            kind="report",
            content=b"complete",
            media_type="text/plain",
            producer="runner",
        )
        key = next(iter(objects.objects))
        objects.objects[key] = b"mutated"
        assert not await store.resolve(evidence)
        with pytest.raises(QualityError, match="differ"):
            await store.put(
                run_id="run-1",
                result_id=None,
                kind="report",
                content=b"complete",
                media_type="text/plain",
                producer="runner",
            )
        del objects.objects[key]
        assert not await store.resolve(evidence)

    @pytest.mark.asyncio
    async def test_same_bytes_cannot_be_relabelled_as_different_evidence(self) -> None:
        objects = MemoryObjectStore()
        repository = MemoryEvidenceRepository()
        store = QualityEvidenceStore(
            client=objects, bucket="iacode-artifacts", repository=repository, now=lambda: NOW
        )
        await store.put(
            run_id="run-1",
            result_id=None,
            kind="report",
            content=b"same",
            media_type="text/plain",
            producer="runner-a",
        )
        with pytest.raises(QualityError, match="metadata"):
            await store.put(
                run_id="run-1",
                result_id=None,
                kind="report",
                content=b"same",
                media_type="text/plain",
                producer="runner-b",
            )

    @pytest.mark.asyncio
    async def test_reproduction_reuses_bytes_but_gets_its_own_evidence_reference(self) -> None:
        objects = MemoryObjectStore()
        repository = MemoryEvidenceRepository()
        store = QualityEvidenceStore(
            client=objects, bucket="iacode-artifacts", repository=repository, now=lambda: NOW
        )
        original = await store.put(
            run_id="run-1",
            result_id=None,
            kind="report",
            content=b"same output",
            media_type="text/plain",
            producer="runner",
        )
        reproduced = await store.put(
            run_id="run-2",
            result_id=None,
            kind="report",
            content=b"same output",
            media_type="text/plain",
            producer="runner",
        )
        assert original.digest == reproduced.digest
        assert original.evidenceId != reproduced.evidenceId
        assert len(objects.objects) == 1
        assert len(repository.records) == 2

    def test_inline_summaries_are_redacted_and_byte_bounded(self) -> None:
        sensitive_line = "to" + "ken=super-sensitive-value\n"
        summary = inline_summary(sensitive_line + "á" * 5000)
        assert "super-sensitive-value" not in summary
        assert "[REDACTED]" in summary
        assert len(summary.encode("utf-8")) <= 4096
        assert "full output stored as quality evidence" in summary


class QualityStoreTests:
    @pytest.mark.asyncio
    async def test_create_and_event_operations_are_idempotent(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        plan = await store.create_plan(quality_plan())
        assert await store.create_plan(quality_plan()) == plan
        first = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="create-1")
        second = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="create-1")
        assert first == second
        events = await store.events(first.run_id)
        assert [(item.sequence, item.event_type) for item in events] == [(1, "CREATED")]

    @pytest.mark.asyncio
    async def test_event_is_visible_before_the_transitioned_state(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(quality_plan())
        run = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="create-1")
        planned = await store.transition(
            run.run_id,
            state="PLANNED",
            event_type="PLANNED",
            dedupe_key="planned-1",
            payload={"planId": SHA},
        )
        assert planned.state == "PLANNED"
        assert (await store.events(run.run_id))[-1].event_type == "PLANNED"
        with pytest.raises(QualityError, match="reason"):
            await store.transition(
                run.run_id,
                state="CANCELLED",
                event_type="COMPLETED",
                dedupe_key="done-1",
                payload={},
            )

    @pytest.mark.asyncio
    async def test_results_enforce_owner_idempotency_and_late_refusal(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(quality_plan(), owner_run_id="owner-1")
        run = await store.create_run(
            plan_id=SHA, owner_run_id="owner-1", idempotency_key="create-1"
        )
        with pytest.raises(QualityError, match="non-running"):
            await store.record_result(
                result(run.run_id), callback_key="too-early", owner_run_id="owner-1"
            )
        for state, event_type in (
            ("PLANNED", "PLANNED"),
            ("QUEUED", "QUEUED"),
            ("RUNNING", "STARTED"),
        ):
            run = await store.transition(
                run.run_id,
                state=state,
                event_type=event_type,
                dedupe_key=f"state:{state}",
                payload={"state": state},
            )
        recorded = await store.record_result(
            result(run.run_id), callback_key="callback-1", owner_run_id="owner-1"
        )
        assert (
            await store.record_result(
                result(run.run_id), callback_key="callback-1", owner_run_id="owner-1"
            )
            == recorded
        )
        with pytest.raises(QualityError, match="owner"):
            await store.record_result(
                result(run.run_id), callback_key="callback-2", owner_run_id="owner-2"
            )
        await store.transition(
            run.run_id,
            state="CANCELLING",
            event_type="CANCELLATION_REQUESTED",
            dedupe_key="cancel-1",
            payload={"reason": "cancelled"},
            reason="cancelled",
        )
        await store.transition(
            run.run_id,
            state="CANCELLED",
            event_type="COMPLETED",
            dedupe_key="done-1",
            payload={"reason": "cancelled"},
            reason="cancelled",
        )
        with pytest.raises(QualityError, match="late"):
            await store.record_result(
                result(run.run_id), callback_key="callback-3", owner_run_id="owner-1"
            )

    @pytest.mark.asyncio
    async def test_a_stored_verdict_is_rederived_not_overwritten(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(quality_plan())
        run = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="create-1")
        for state, event_type in (
            ("PLANNED", "PLANNED"),
            ("QUEUED", "QUEUED"),
            ("RUNNING", "STARTED"),
        ):
            run = await store.transition(
                run.run_id,
                state=state,
                event_type=event_type,
                dedupe_key=f"state:{state}",
                payload={"state": state},
            )
        verdict_content = {
            "contractVersion": "1.0.0",
            "runId": run.run_id,
            "planId": SHA,
            "verdict": "PASS",
            "reasons": ("all mandatory checks passed",),
            "resultDigests": (SHA,),
            "evidenceDigests": (OTHER_SHA,),
            "derivedAt": NOW,
        }
        verdict = QualityVerdict(**verdict_content, digest=digest(verdict_content))
        assert await store.record_verdict(verdict) == verdict
        changed = verdict.model_copy(update={"verdict": "FAIL", "digest": OTHER_SHA})
        with pytest.raises(QualityError, match="differs"):
            await store.record_verdict(changed)

    @pytest.mark.asyncio
    async def test_event_pages_are_bounded_and_cursor_ordered(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(quality_plan())
        run = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="create-1")
        await store.transition(
            run.run_id,
            state="PLANNED",
            event_type="PLANNED",
            dedupe_key="planned-1",
            payload={},
        )
        assert [item.sequence for item in await store.events(run.run_id, after=1, limit=1)] == [2]
        with pytest.raises(QualityError, match="limit"):
            await store.events(run.run_id, limit=501)

    def test_a_finding_can_reference_only_evidence_of_its_own_result(self) -> None:
        evidence = QualityEvidence(
            evidenceId="evidence-1",
            kind="report",
            artifactId="artifact-1",
            digest=SHA,
            sizeBytes=1,
            mediaType="text/plain",
            producer="pytest",
            createdAt=NOW,
        )
        finding = QualityFinding(
            findingId="finding-1",
            checkId="q001-unit",
            severity="HIGH",
            category="unit",
            fingerprint=OTHER_SHA,
            message="failure",
            evidenceIds=("missing-evidence",),
        )
        with pytest.raises(ValueError, match="outside its result"):
            QualityResult(
                resultId="result-1",
                runId="run-1",
                checkId="q001-unit",
                status="FAILED",
                exitCode=1,
                durationMs=10,
                summary="failed",
                evidence=(evidence,),
                findings=(finding,),
                finishedAt=NOW,
            )


class QualityPersistenceShapeTests:
    def test_all_quality_tables_and_closed_constraints_are_declared(self) -> None:
        tables = Base.metadata.tables
        expected = {
            "quality_plans",
            "quality_checks",
            "quality_runs",
            "quality_results",
            "quality_evidence",
            "quality_findings",
            "quality_verdicts",
            "quality_run_events",
        }
        assert expected <= set(tables)
        assert "training_allowed" in tables["quality_runs"].c
        assert tables["quality_runs"].c.training_allowed.server_default.arg == "false"
        assert tables["quality_evidence"].c.training_allowed.server_default.arg == "false"

    def test_immutable_fact_tables_have_no_update_or_version_columns(self) -> None:
        for name in (
            "quality_plans",
            "quality_checks",
            "quality_results",
            "quality_evidence",
            "quality_findings",
            "quality_verdicts",
            "quality_run_events",
        ):
            assert "updated_at" not in Base.metadata.tables[name].c, name
            assert "version" not in Base.metadata.tables[name].c, name

    def test_database_shapes_cannot_store_full_output_credentials_or_environment(self) -> None:
        forbidden = {"stdout", "stderr", "output", "environment", "credential", "secret"}
        for name in ("quality_results", "quality_evidence", "quality_findings"):
            assert forbidden.isdisjoint(Base.metadata.tables[name].c.keys())
