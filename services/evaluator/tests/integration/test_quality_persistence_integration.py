"""Quality facts and evidence against the stack's PostgreSQL and MinIO services.

The in-memory suites define behavior. These cases prove that the same invariants survive the
actual database constraints, async driver, object-store error protocol and cleanup path used by
the evaluator container. Every row and object carries a unique fixture identity and is removed.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from iacode_contracts.quality import (
    QualityCheck,
    QualityFinding,
    QualityPlan,
    QualityPolicy,
    QualityResult,
    QualityVerdict,
)
from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.evidence import QualityEvidenceStore, SqlEvidenceRepository
from iacode_evaluator.store import SqlQualityStore
from iacode_persistence.engine import create_session_factory
from iacode_persistence.models import (
    Artifact,
    Project,
    Task,
    TaskRun,
)
from iacode_persistence.models import (
    QualityEvidence as QualityEvidenceRow,
)
from iacode_persistence.models import (
    QualityFinding as QualityFindingRow,
)
from iacode_persistence.models import (
    QualityPlan as QualityPlanRow,
)
from iacode_persistence.models import (
    QualityResult as QualityResultRow,
)
from iacode_persistence.models import (
    QualityRun as QualityRunRow,
)
from iacode_persistence.models import (
    QualityVerdict as QualityVerdictRow,
)
from minio import Minio
from minio.error import S3Error
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("IACODE_DATABASE_URL"),
        reason="the stack is not configured for this process",
    ),
]

PREFIX = "iacode-quality-itest"


def run(coroutine):
    return asyncio.run(coroutine)


class Fixture:
    def __init__(self) -> None:
        self.slug = f"{PREFIX}-{uuid.uuid4().hex[:10]}"
        self.engine = create_async_engine(os.environ["IACODE_DATABASE_URL"], poolclass=NullPool)
        self.factory = create_session_factory(self.engine)
        self.store = SqlQualityStore(self.factory)
        self.bucket = os.environ.get("IACODE_MINIO_BUCKET", "iacode-artifacts")
        self.client = Minio(
            os.environ["IACODE_MINIO_ENDPOINT"],
            access_key=os.environ["IACODE_MINIO_ACCESS_KEY"],
            secret_key=os.environ["IACODE_MINIO_SECRET_KEY"],
            secure=os.environ.get("IACODE_MINIO_SECURE", "false").lower() == "true",
        )
        self.objects: set[str] = set()
        self.run_ids: set[uuid.UUID] = set()
        self._plan: QualityPlan | None = None

    async def build(self) -> None:
        snapshot = f"snapshot for {self.slug}\n".encode()
        self.snapshot_digest = hashlib.sha256(snapshot).hexdigest()
        self.snapshot_key = f"quality/integration/snapshots/{self.slug}"
        await asyncio.to_thread(
            self.client.put_object,
            self.bucket,
            self.snapshot_key,
            io.BytesIO(snapshot),
            len(snapshot),
            content_type="application/x-tar",
        )
        self.objects.add(self.snapshot_key)
        async with self.factory() as session, session.begin():
            project = Project(slug=self.slug, name="Quality persistence integration")
            session.add(project)
            await session.flush()
            task = Task(project_id=project.id, title=self.slug, description="integration")
            session.add(task)
            await session.flush()
            owner = TaskRun(task_id=task.id, status="RUNNING", attempt=1)
            session.add(owner)
            await session.flush()
            snapshot_row = Artifact(
                task_run_id=owner.id,
                kind="workspace.snapshot",
                storage_bucket=self.bucket,
                storage_key=self.snapshot_key,
                content_type="application/x-tar",
                size_bytes=len(snapshot),
                checksum_sha256=self.snapshot_digest,
            )
            session.add(snapshot_row)
            await session.flush()
            self.owner_run_id = str(owner.id)
            self.snapshot_id = str(snapshot_row.id)

    def plan(self) -> QualityPlan:
        if self._plan is not None:
            return self._plan
        plan_digest = hashlib.sha256(f"plan:{self.slug}".encode()).hexdigest()
        profile_digest = hashlib.sha256(f"profile:{self.slug}".encode()).hexdigest()
        self._plan = QualityPlan(
            planId=plan_digest,
            snapshotId=self.snapshot_id,
            snapshotDigest=self.snapshot_digest,
            projectProfile="python",
            projectProfileDigest=profile_digest,
            policy=QualityPolicy(
                policyId="default",
                version="1.0.0",
                digest="a" * 64,
                profile="python",
                mandatoryCheckKinds=("unit",),
                maxRunSeconds=3600,
                maxCheckSeconds=600,
                maxOutputBytes=131072,
            ),
            checks=(
                QualityCheck(
                    checkId="q001-unit",
                    kind="unit",
                    runner="python.unit",
                    command=("python", "-m", "pytest"),
                    applicabilityReason="the Python profile requires unit tests",
                    timeoutSeconds=600,
                ),
            ),
            createdAt=datetime.now(UTC),
        )
        return self._plan

    async def quality_run(self, suffix: str = "one") -> tuple[QualityPlan, str]:
        plan = self.plan()
        await self.store.create_plan(plan, owner_run_id=self.owner_run_id)
        quality_run = await self.store.create_run(
            plan_id=plan.planId,
            owner_run_id=self.owner_run_id,
            idempotency_key=f"{self.slug}:{suffix}",
        )
        self.run_ids.add(uuid.UUID(quality_run.run_id))
        return plan, quality_run.run_id

    async def remove(self) -> None:
        async with self.factory() as session, session.begin():
            artifact_ids: set[uuid.UUID] = {uuid.UUID(self.snapshot_id)}
            if self.run_ids:
                evidence_artifacts = (
                    await session.execute(
                        select(QualityEvidenceRow.artifact_id).where(
                            QualityEvidenceRow.quality_run_id.in_(self.run_ids)
                        )
                    )
                ).scalars()
                artifact_ids.update(evidence_artifacts)
                await session.execute(
                    delete(QualityRunRow).where(QualityRunRow.id.in_(self.run_ids))
                )
            await session.execute(
                delete(QualityPlanRow).where(
                    QualityPlanRow.snapshot_artifact_id == uuid.UUID(self.snapshot_id)
                )
            )
            await session.execute(delete(Artifact).where(Artifact.id.in_(artifact_ids)))
            await session.execute(delete(Project).where(Project.slug == self.slug))
        for key in self.objects:
            try:
                await asyncio.to_thread(self.client.remove_object, self.bucket, key)
            except S3Error as error:
                if error.code not in {"NoSuchKey", "NoSuchObject"}:
                    raise
        await self.engine.dispose()


@pytest.fixture
def stack() -> Iterator[Fixture]:
    fixture = Fixture()
    run(fixture.build())
    try:
        yield fixture
    finally:
        run(fixture.remove())


class SqlQualityLifecycleTests:
    def test_plan_run_results_verdict_and_events_round_trip(self, stack: Fixture) -> None:
        plan = stack.plan()
        first_plan = run(stack.store.create_plan(plan, owner_run_id=stack.owner_run_id))
        assert run(stack.store.create_plan(plan, owner_run_id=stack.owner_run_id)) == first_plan
        quality_run = run(
            stack.store.create_run(
                plan_id=plan.planId,
                owner_run_id=stack.owner_run_id,
                idempotency_key=f"{stack.slug}:lifecycle",
            )
        )
        stack.run_ids.add(uuid.UUID(quality_run.run_id))
        retried = run(
            stack.store.create_run(
                plan_id=plan.planId,
                owner_run_id=stack.owner_run_id,
                idempotency_key=f"{stack.slug}:lifecycle",
            )
        )
        assert retried == quality_run

        for state, event_type in (
            ("PLANNED", "PLANNED"),
            ("QUEUED", "QUEUED"),
            ("RUNNING", "STARTED"),
        ):
            current = run(
                stack.store.transition(
                    quality_run.run_id,
                    state=state,
                    event_type=event_type,
                    dedupe_key=f"{stack.slug}:{event_type.lower()}",
                    payload={"state": state},
                )
            )
            assert current.state == state

        result = QualityResult(
            resultId=str(uuid.uuid4()),
            runId=quality_run.run_id,
            checkId="q001-unit",
            status="PASSED",
            exitCode=0,
            durationMs=17,
            summary="unit tests passed",
            findings=(
                QualityFinding(
                    findingId=str(uuid.uuid4()),
                    checkId="q001-unit",
                    severity="INFO",
                    category="unit",
                    fingerprint=hashlib.sha256(f"finding:{stack.slug}".encode()).hexdigest(),
                    message="the integration fixture finding",
                ),
            ),
            finishedAt=datetime.now(UTC),
        )
        assert (
            run(
                stack.store.record_result(
                    result,
                    callback_key=f"{stack.slug}:result",
                    owner_run_id=stack.owner_run_id,
                )
            )
            == result
        )
        assert (
            run(
                stack.store.record_result(
                    result,
                    callback_key=f"{stack.slug}:result",
                    owner_run_id=stack.owner_run_id,
                )
            )
            == result
        )
        verdict_content = {
            "contractVersion": "1.0.0",
            "runId": quality_run.run_id,
            "planId": plan.planId,
            "verdict": "PASS",
            "reasons": ("every applicable mandatory check passed",),
            "resultDigests": ("b" * 64,),
            "evidenceDigests": (),
            "derivedAt": datetime.now(UTC),
        }
        verdict = QualityVerdict(**verdict_content, digest=digest(verdict_content))
        assert run(stack.store.record_verdict(verdict)) == verdict
        completed = run(
            stack.store.transition(
                quality_run.run_id,
                state="SUCCEEDED",
                event_type="COMPLETED",
                dedupe_key=f"{stack.slug}:completed",
                payload={"verdict": "PASS"},
                reason="quality verdict PASS",
            )
        )
        assert completed.state == "SUCCEEDED" and completed.finished_at is not None
        stored_plan = run(stack.store.plan_for_run(quality_run.run_id))
        assert stored_plan is not None and stored_plan.plan == plan
        assert run(stack.store.results_for_run(quality_run.run_id)) == (result,)
        assert run(stack.store.verdict_for_run(quality_run.run_id)) == verdict
        assert [event.sequence for event in run(stack.store.events(quality_run.run_id))] == list(
            range(1, 8)
        )
        reproduction = run(
            stack.store.create_run(
                plan_id=plan.planId,
                owner_run_id=stack.owner_run_id,
                idempotency_key=f"{stack.slug}:reproduction",
                reproduction_of_run_id=quality_run.run_id,
            )
        )
        stack.run_ids.add(uuid.UUID(reproduction.run_id))
        assert reproduction.reproduction_of_run_id == quality_run.run_id
        with pytest.raises(QualityError, match="another quality run"):
            run(
                stack.store.create_run(
                    plan_id=plan.planId,
                    owner_run_id=stack.owner_run_id,
                    idempotency_key=f"{stack.slug}:reproduction",
                )
            )
        with pytest.raises(QualityError, match="late"):
            run(
                stack.store.record_result(
                    result.model_copy(update={"resultId": str(uuid.uuid4())}),
                    callback_key=f"{stack.slug}:late",
                    owner_run_id=stack.owner_run_id,
                )
            )

        async def counts() -> tuple[int, int, int]:
            async with stack.factory() as session:
                results = (
                    await session.execute(
                        select(func.count())
                        .select_from(QualityResultRow)
                        .where(QualityResultRow.quality_run_id == uuid.UUID(quality_run.run_id))
                    )
                ).scalar_one()
                verdicts = (
                    await session.execute(
                        select(func.count())
                        .select_from(QualityVerdictRow)
                        .where(QualityVerdictRow.quality_run_id == uuid.UUID(quality_run.run_id))
                    )
                ).scalar_one()
                findings = (
                    await session.execute(
                        select(func.count())
                        .select_from(QualityFindingRow)
                        .where(QualityFindingRow.quality_run_id == uuid.UUID(quality_run.run_id))
                    )
                ).scalar_one()
                return results, verdicts, findings

        assert run(counts()) == (1, 1, 1)


class SqlQualityEvidenceTests:
    def test_evidence_is_rehashed_and_one_artifact_can_support_reproduction(self, stack) -> None:
        _, first_run_id = run(stack.quality_run("evidence-original"))
        _, reproduced_run_id = run(stack.quality_run("evidence-reproduction"))
        repository = SqlEvidenceRepository(stack.factory)
        evidence_store = QualityEvidenceStore(
            client=stack.client,
            bucket=stack.bucket,
            repository=repository,
        )
        content = b"47 passed\n"
        first = run(
            evidence_store.put(
                run_id=first_run_id,
                result_id=None,
                kind="report",
                content=content,
                media_type="text/plain",
                producer="pytest",
                source_digests=(stack.snapshot_digest,),
            )
        )
        key = f"quality/evidence/{first.digest}"
        stack.objects.add(key)
        assert run(evidence_store.resolve(first))
        assert (
            run(
                evidence_store.put(
                    run_id=first_run_id,
                    result_id=None,
                    kind="report",
                    content=content,
                    media_type="text/plain",
                    producer="pytest",
                    source_digests=(stack.snapshot_digest,),
                )
            )
            == first
        )
        reproduced = run(
            evidence_store.put(
                run_id=reproduced_run_id,
                result_id=None,
                kind="report",
                content=content,
                media_type="text/plain",
                producer="pytest",
                source_digests=(stack.snapshot_digest,),
            )
        )
        assert reproduced.evidenceId != first.evidenceId
        assert reproduced.artifactId == first.artifactId
        assert reproduced.digest == first.digest
        assert reproduced.trainingAllowed is False
        assert run(evidence_store.resolve(reproduced))

        stack.client.put_object(
            stack.bucket,
            key,
            io.BytesIO(b"tampered"),
            len(b"tampered"),
            content_type="text/plain",
        )
        assert not run(evidence_store.resolve(first))
        stack.client.remove_object(stack.bucket, key)
        stack.objects.remove(key)
        assert not run(evidence_store.resolve(first))


class IntegrationResidueTests:
    def test_nothing_this_suite_writes_is_left_behind(self) -> None:
        engine = create_async_engine(os.environ["IACODE_DATABASE_URL"], poolclass=NullPool)
        factory = create_session_factory(engine)

        async def residue() -> int:
            async with factory() as session:
                count = (
                    await session.execute(
                        select(func.count())
                        .select_from(Project)
                        .where(Project.slug.like(f"{PREFIX}-%"))
                    )
                ).scalar_one()
            await engine.dispose()
            return count

        assert run(residue()) == 0
