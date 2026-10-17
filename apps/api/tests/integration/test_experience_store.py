"""Actual PostgreSQL/migrations and authenticated HTTP, using exclusively owned databases.

These fixtures insert observable source facts, not a production fake. The separate live scenario
must additionally obtain them through a real provider/sandbox/quality workflow.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from iacode_api.experience.runtime import build_experience_runtime
from iacode_api.main import create_app
from iacode_common.desktop_auth import signed_headers
from iacode_contracts.desktop import PROTOCOL
from iacode_contracts.experience import CaptureExperience
from iacode_evaluator.store import SqlQualityStore
from iacode_experience.domain import ExperienceError, canonical
from iacode_persistence.engine import create_engine, create_session_factory
from iacode_persistence.models import Experience, ExperienceEvent, Project, Task, TaskRun
from minio import Minio
from sqlalchemy import create_engine as sync_engine
from sqlalchemy import event, func, select, text
from sqlalchemy.exc import DBAPIError

from tests.conftest import stack_is_configured, stack_settings
from tests.integration.test_migrations import _alembic, _DisposableDatabase, _sync_url

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not stack_is_configured(), reason="the real Foundation stack is not configured"
    ),
]


@pytest.fixture
def database():
    with _DisposableDatabase() as owned:
        migrated = _alembic(owned.url, "upgrade", "head")
        assert migrated.returncode == 0, migrated.stdout[-2000:]
        yield owned


@pytest.fixture
async def rig(database):
    settings = stack_settings().model_copy(update={"database_url": database.url})
    engine = create_engine(database.url, pool_size=8, max_overflow=8)
    sessions = create_session_factory(engine)
    minio = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key.get_secret_value(),
        secret_key=settings.minio_secret_key.get_secret_value(),
        secure=settings.minio_secure,
    )
    runtime = build_experience_runtime(settings, sessions, minio, SqlQualityStore(sessions))
    now = datetime.now(UTC)
    project_id, task_id, run_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    async with sessions() as session, session.begin():
        session.add(
            Project(id=project_id, slug="experience-test-" + project_id.hex, name="Owned test")
        )
        await session.flush()
        session.add(
            Task(
                id=task_id,
                project_id=project_id,
                title="Do not copy this title",
                description="Private goal text is not experience content",
            )
        )
        await session.flush()
        session.add(
            TaskRun(
                id=run_id,
                task_id=task_id,
                status="SUCCEEDED",
                attempt=1,
                started_at=now - timedelta(seconds=2),
                finished_at=now - timedelta(seconds=1),
                result="Raw answer is not copied",
                workspace={},
            )
        )
    request = CaptureExperience(
        taskRunId=str(run_id),
        storageConsent=True,
        idempotencyKey=str(uuid.uuid4()),
        retentionSeconds=60,
    )
    try:
        yield runtime, sessions, str(project_id), request, now, database
    finally:
        await runtime.close()
        await engine.dispose()


async def test_real_capture_restart_read_and_source_projection(rig):
    runtime, sessions, project, request, now, _ = rig
    row = await runtime.service.capture(project, request, now)
    assert row.state == "ACTIVE" and row.body["quality"] is None
    assert row.body["provider"] == row.body["model"] == []
    assert row.body["effort"] is row.body["repository"] is row.body["baseCommit"] is None
    assert not any(word in json.dumps(row.body) for word in ("Private goal", "Raw answer", "title"))
    retrieved = await runtime.store.get(project, row.experience_id)
    assert (await runtime.service.deliver(retrieved, now)).model_dump(mode="json") == row.body
    replay = await runtime.service.capture(project, request, now + timedelta(seconds=1))
    assert replay.replay and replay.experience_id == row.experience_id
    assert replay.expires_at == row.expires_at
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Experience)) == 1
        assert await session.scalar(select(func.count()).select_from(ExperienceEvent)) == 1


async def test_actual_sql_projection_does_not_fetch_unneeded_private_source_columns(rig):
    runtime, sessions, project, request, now, _ = rig
    statements = []

    def observed(_connection, _cursor, statement, _parameters, _context, _many):
        if statement.startswith("SELECT"):
            statements.append(statement)

    engine = sessions.kw["bind"].sync_engine
    event.listen(engine, "before_cursor_execute", observed)
    try:
        row = await runtime.service.capture(project, request, now)
        assert row.state == "ACTIVE"
    finally:
        event.remove(engine, "before_cursor_execute", observed)
    assert statements
    forbidden = {
        "task_runs": ("result", "result_summary", "error_summary", "budget", "budget_used"),
        "agent_runs": ("output", "output_summary", "error_summary"),
        "run_events": ("payload",),
        "tool_calls": ("summary", "artifact_ids"),
    }
    for statement in statements:
        projection = statement.partition("FROM")[0]
        for table, columns in forbidden.items():
            for column in columns:
                # The trailing boundary prevents result/result_summary substring ambiguity.
                assert not re.search(rf"\b{table}\.{column}\b", projection), (
                    f"Unneeded private source column selected: {table}.{column}"
                )


async def test_oversized_required_source_json_is_refused_before_materialization_and_writes(rig):
    runtime, sessions, project, request, now, _ = rig
    async with sessions() as session, session.begin():
        source = await session.get(TaskRun, uuid.UUID(request.taskRunId))
        source.workspace = {"unneededPrivateField": "x" * (runtime.service.policy.maxBodyBytes + 1)}
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.capture(project, request, now)
    assert caught.value.code == "SOURCE_FACT_LIMIT_EXCEEDED"
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Experience)) == 0
        assert await session.scalar(select(func.count()).select_from(ExperienceEvent)) == 0


async def test_real_concurrent_retry_commits_exactly_one_fact_and_audit(rig):
    runtime, sessions, project, request, now, _ = rig
    results = await asyncio.gather(
        *(runtime.service.capture(project, request, now) for _ in range(4))
    )
    assert len({row.experience_id for row in results}) == 1
    assert len({row.content_digest for row in results}) == 1
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Experience)) == 1
        assert await session.scalar(select(func.count()).select_from(ExperienceEvent)) == 1


async def test_conflicting_retry_and_new_key_cannot_renew_or_resurrect(rig):
    runtime, _, project, request, now, _ = rig
    row = await runtime.service.capture(project, request, now)
    changed = request.model_copy(update={"retentionSeconds": 61})
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.capture(project, changed, now)
    assert caught.value.code == "REQUEST_CONFLICT"
    await runtime.store.withdraw(project, row.experience_id, now)
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.capture(project, request, now)
    assert caught.value.code == "EXPERIENCE_UNAVAILABLE"
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.capture(
            project, request.model_copy(update={"idempotencyKey": str(uuid.uuid4())}), now
        )
    assert caught.value.code == "SOURCE_CONFLICT"


async def test_real_expiry_physical_purge_idempotent_withdrawal_and_source_preservation(rig):
    runtime, sessions, project, request, now, _ = rig
    row = await runtime.service.capture(
        project, request.model_copy(update={"retentionSeconds": 1}), now
    )
    boundary = now + timedelta(seconds=1)
    with pytest.raises(ExperienceError):
        await runtime.service.deliver(row, boundary)
    assert await runtime.store.page(project, None, 25, boundary) == []
    assert (await runtime.store.sweep(boundary))["purged"] == 1
    first = await runtime.store.withdraw(project, row.experience_id, boundary)
    second = await runtime.store.withdraw(
        project, row.experience_id, boundary + timedelta(seconds=2)
    )
    assert first == second and first.state == "EXPIRED" and first.body == {}
    async with sessions() as session:
        stored = await session.get(Experience, uuid.UUID(row.experience_id))
        assert stored.summary == "" and stored.body == {} and not stored.storage_allowed
        assert await session.get(TaskRun, uuid.UUID(request.taskRunId)) is not None
        assert await session.scalar(select(func.count()).select_from(ExperienceEvent)) == 2


async def test_bounded_purge_and_finite_gc_never_reset_the_source_capture_window(rig):
    runtime, sessions, project, request, now, _ = rig
    policy = type(runtime.service.policy).model_validate_json(
        canonical(
            {
                **runtime.service.policy.model_dump(mode="json"),
                "batchSize": 2,
                "defaultRetentionSeconds": 30,
                "maxRetentionSeconds": 90,
                "captureMaxAgeSeconds": 90,
                "tombstoneRetentionSeconds": 90,
            }
        )
    )
    runtime.service = replace(runtime.service, policy=policy)
    runtime.store.policy = runtime.sources.policy = policy
    async with sessions() as session, session.begin():
        original = await session.get(TaskRun, uuid.UUID(request.taskRunId))
        task_id = original.task_id
        source_ids = [request.taskRunId, str(uuid.uuid4()), str(uuid.uuid4())]
        for identifier in source_ids[1:]:
            session.add(
                TaskRun(
                    id=uuid.UUID(identifier),
                    task_id=task_id,
                    status="SUCCEEDED",
                    finished_at=now - timedelta(seconds=1),
                    workspace={},
                )
            )
    for identifier in source_ids:
        await runtime.service.capture(
            project,
            CaptureExperience(
                taskRunId=identifier,
                idempotencyKey=str(uuid.uuid4()),
                storageConsent=True,
                retentionSeconds=1,
            ),
            now,
        )
    boundary = now + timedelta(seconds=1)
    assert (await runtime.store.sweep(boundary))["purged"] == 2
    assert (await runtime.store.sweep(boundary))["purged"] == 1
    future = boundary + timedelta(seconds=90)
    assert (await runtime.store.sweep(future))["tombstonesCollected"] == 2
    assert (await runtime.store.sweep(future))["tombstonesCollected"] == 1
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.capture(project, request, future)
    assert caught.value.code == "SOURCE_AGE_REFUSED"
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Experience)) == 0
        assert await session.scalar(select(func.count()).select_from(ExperienceEvent)) == 0
        assert await session.scalar(select(func.count()).select_from(TaskRun)) == 3


async def test_failed_source_capture_preserves_failure_and_unknown_quality(rig):
    runtime, sessions, project, request, now, _ = rig
    async with sessions() as session, session.begin():
        source = await session.get(TaskRun, uuid.UUID(request.taskRunId))
        source.status = "FAILED"
        source.error_summary = "Private source error detail is not copied"
    row = await runtime.service.capture(project, request, now)
    assert row.body["task"]["status"] == row.body["finalResult"]["taskStatus"] == "FAILED"
    assert row.body["failures"][0]["outcome"] == "FAILED"
    assert row.body["finalResult"]["qualityVerdict"] is None
    assert "Private source error" not in json.dumps(row.body)


async def test_future_and_too_old_sources_are_refused_before_capture(rig):
    runtime, sessions, project, request, now, _ = rig
    for finished in (
        now + timedelta(seconds=1),
        now - timedelta(seconds=runtime.service.policy.captureMaxAgeSeconds),
    ):
        async with sessions() as session, session.begin():
            source = await session.get(TaskRun, uuid.UUID(request.taskRunId))
            source.started_at = None
            source.finished_at = finished
        with pytest.raises(ExperienceError) as caught:
            await runtime.service.capture(project, request, now)
        assert caught.value.code == "SOURCE_AGE_REFUSED"
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Experience)) == 0


async def test_real_project_scope_and_missing_active_quality_sources_leave_zero_effects(rig):
    runtime, sessions, project, request, now, _ = rig
    for target, payload, code in (
        (str(uuid.uuid4()), request, "SOURCE_NOT_FOUND"),
        (
            project,
            request.model_copy(update={"qualityRunId": str(uuid.uuid4())}),
            "QUALITY_SOURCE_NOT_TERMINAL",
        ),
    ):
        with pytest.raises(ExperienceError) as caught:
            await runtime.service.capture(target, payload, now)
        assert caught.value.code == code
    async with sessions() as session, session.begin():
        source = await session.get(TaskRun, uuid.UUID(request.taskRunId))
        source.status, source.finished_at = "RUNNING", None
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.capture(project, request, now)
    assert caught.value.code == "SOURCE_NOT_TERMINAL"
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Experience)) == 0


async def test_database_immutability_and_direct_corruption_fail_closed(rig):
    runtime, sessions, project, request, now, database = rig
    row = await runtime.service.capture(project, request, now)
    with pytest.raises(DBAPIError):
        async with sessions() as session, session.begin():
            await session.execute(
                text("UPDATE experiences SET summary='forged' WHERE id=:id"),
                {"id": uuid.UUID(row.experience_id)},
            )
    # The adversary here is explicitly the owner of an isolated disposable database, not a
    # runtime capability. Corrupt bytes below normal guards to exercise recovery validation.
    engine = sync_engine(_sync_url(database.url))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE experiences DISABLE TRIGGER experience_fact_immutable")
            )
            connection.execute(
                text("UPDATE experiences SET body=body || CAST(:body AS JSONB) WHERE id=:id"),
                {"id": row.experience_id, "body": json.dumps({"privateTranscript": True})},
            )
            connection.execute(
                text("ALTER TABLE experiences ENABLE TRIGGER experience_fact_immutable")
            )
    finally:
        engine.dispose()
    corrupted = await runtime.store.get(project, row.experience_id)
    with pytest.raises(ExperienceError) as caught:
        await runtime.service.deliver(corrupted, now)
    assert caught.value.code == "STORED_INTEGRITY_INVALID"


async def test_audit_insert_failure_rolls_back_experience_atomically(rig):
    runtime, sessions, project, request, now, database = rig
    engine = sync_engine(_sync_url(database.url))
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE FUNCTION refuse_owned_audit() RETURNS trigger LANGUAGE plpgsql "
                    "AS $$ BEGIN RAISE EXCEPTION 'owned audit failure'; END $$"
                )
            )
            connection.execute(
                text(
                    "CREATE TRIGGER refuse_owned_audit BEFORE INSERT ON experience_events "
                    "FOR EACH ROW EXECUTE FUNCTION refuse_owned_audit()"
                )
            )
        with pytest.raises(ExperienceError):
            await runtime.service.capture(project, request, now)
        async with sessions() as session:
            assert await session.scalar(select(func.count()).select_from(Experience)) == 0
            assert await session.scalar(select(func.count()).select_from(ExperienceEvent)) == 0
    finally:
        engine.dispose()


def _seed_http(database):
    project, task, run = (str(uuid.uuid4()) for _ in range(3))
    engine = sync_engine(_sync_url(database.url))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO projects(id,slug,name) VALUES(:p,:s,'owned')"),
                {"p": project, "s": "experience-http-" + project},
            )
            connection.execute(
                text("INSERT INTO tasks(id,project_id,title) VALUES(:t,:p,'not copied')"),
                {"t": task, "p": project},
            )
            connection.execute(
                text(
                    "INSERT INTO task_runs(id,task_id,status,finished_at) "
                    "VALUES(:r,:t,'SUCCEEDED',now()-interval '1 second')"
                ),
                {"r": run, "t": task},
            )
    finally:
        engine.dispose()
    return project, run


def test_real_authenticated_http_roundtrip_pagination_scope_reuse_and_withdrawal(database):
    project, run = _seed_http(database)
    key = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    settings = stack_settings().model_copy(
        update={
            "database_url": database.url,
            "desktop_token": type(stack_settings().desktop_token)(key),
            "desktop_token_expires_at": datetime.now(UTC) + timedelta(hours=1),
        }
    )

    def send(client, method, target, value=None, *, authenticated=True):
        raw = b"" if value is None else canonical(value)
        headers = {"Content-Type": "application/json"}
        if authenticated:
            headers.update(
                signed_headers(
                    key, method, target, raw, names=PROTOCOL["headers"], version=PROTOCOL["version"]
                )
            )
        return client.request(method, target, content=raw, headers=headers)

    root = f"/api/v1/experiences/projects/{project}"
    value = {"taskRunId": run, "storageConsent": True, "idempotencyKey": str(uuid.uuid4())}
    with TestClient(create_app(settings)) as client:
        assert send(client, "POST", root, value, authenticated=False).status_code == 401
        created = send(client, "POST", root, value)
        assert created.status_code == 201, created.text
        body = created.json()
        assert send(client, "POST", root, value).json()["idempotentReplay"] is True
        target = root + "/" + body["experienceId"]
        inspected = send(client, "GET", target)
        exported = send(client, "GET", target + "/export")
        assert inspected.status_code == exported.status_code == 200
        assert inspected.json() == exported.json()
        page = send(client, "GET", root + "?limit=1").json()
        assert page["experiences"][0]["contentDigest"] == body["contentDigest"]
        assert (
            send(client, "GET", root + "?cursor=" + page["nextCursor"]).json()["experiences"] == []
        )
        wrong = f"/api/v1/experiences/projects/{uuid.uuid4()}"
        assert send(client, "GET", wrong + "/" + body["experienceId"]).status_code == 404
        assert send(client, "DELETE", wrong + "/" + body["experienceId"]).status_code == 404
        assert send(client, "GET", wrong + "?cursor=" + page["nextCursor"]).status_code == 400
        for use in ("rag", "training", "distillation", "unknown"):
            assert send(client, "GET", target + "?use=" + use).status_code == 403
        assert send(client, "DELETE", target).json()["state"] == "DELETED"
        assert send(client, "DELETE", target).json()["state"] == "DELETED"
        assert send(client, "GET", target).status_code == 410
        assert send(client, "POST", root, value).status_code == 410


def test_legacy_migration_preserves_identity_body_and_rights_without_promotion():
    with _DisposableDatabase() as database:
        before = _alembic(database.url, "upgrade", "0006_quality_engine")
        assert before.returncode == 0, before.stdout
        identity = str(uuid.uuid4())
        engine = sync_engine(_sync_url(database.url))
        try:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO experiences(id,kind,summary,body,source_type,"
                        "ownership,license,"
                        "storage_allowed,rag_allowed,training_allowed,distillation_allowed) "
                        "VALUES(:id,'legacy','preserve',CAST(:body AS JSONB),'external',"
                        "'unknown','unknown',true,true,true,true)"
                    ),
                    {"id": identity, "body": json.dumps({"historical": True})},
                )
            upgraded = _alembic(database.url, "upgrade", "head")
            assert upgraded.returncode == 0, upgraded.stdout
            with engine.connect() as connection:
                legacy = connection.execute(
                    text(
                        "SELECT id,body,storage_allowed,rag_allowed,training_allowed,"
                        "distillation_allowed,schema_version,state FROM experiences "
                        "WHERE id=:id"
                    ),
                    {"id": identity},
                ).one()
            assert str(legacy[0]) == identity and legacy[1] == {"historical": True}
            assert tuple(legacy[2:]) == (True, True, True, True, 0, "LEGACY")
            with pytest.raises(DBAPIError), engine.begin() as connection:
                connection.execute(
                    text("UPDATE experiences SET schema_version=1 WHERE id=:id"), {"id": identity}
                )
            downgraded = _alembic(database.url, "downgrade", "0006_quality_engine")
            assert downgraded.returncode == 0, downgraded.stdout
            with engine.connect() as connection:
                assert connection.execute(
                    text("SELECT body,rag_allowed,training_allowed FROM experiences WHERE id=:id"),
                    {"id": identity},
                ).one() == ({"historical": True}, True, True)
        finally:
            engine.dispose()


def test_raw_authenticated_json_refusals_leave_zero_durable_effects_then_clean_capture(database):
    project, run = _seed_http(database)
    key = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    settings = stack_settings().model_copy(
        update={
            "database_url": database.url,
            "desktop_token": type(stack_settings().desktop_token)(key),
            "desktop_token_expires_at": datetime.now(UTC) + timedelta(hours=1),
        }
    )
    root = f"/api/v1/experiences/projects/{project}"
    value = {"taskRunId": run, "storageConsent": True, "idempotencyKey": str(uuid.uuid4())}
    clean = canonical(value)
    marker = b"rejected-input-must-not-be-echoed"
    cases = (
        (b'{"storageConsent":true,"storageConsent":false}', 400),
        (b'{"storageConsent":NaN}', 400),
        (b'{"storageConsent":Infinity}', 400),
        (b'{"storageConsent":true,"unknown":"\xff"}', 400),
        (b'{"storageConsent":true,"unknown":"\\ud800"}', 400),
        (b"[" * 14 + b"0" + b"]" * 14, 400),
        (canonical({**value, "storageConsent": 1}), 400),
        (canonical({**value, "storageConsent": "true"}), 400),
        (canonical({**value, "privateTranscript": marker.decode()}), 400),
        (b" " * 4097, 413),
    )
    engine = sync_engine(_sync_url(database.url))
    try:
        with TestClient(create_app(settings)) as client:
            for raw, status in cases:
                headers = signed_headers(
                    key, "POST", root, raw, names=PROTOCOL["headers"], version=PROTOCOL["version"]
                )
                response = client.post(root, content=raw, headers=headers)
                assert response.status_code == status, response.text
                assert set(response.json()) == {"code", "message", "correlationId"}
                assert marker.decode() not in response.text and key not in response.text
                with engine.connect() as connection:
                    assert connection.scalar(text("SELECT count(*) FROM experiences")) == 0
                    assert connection.scalar(text("SELECT count(*) FROM experience_events")) == 0
            headers = signed_headers(
                key, "POST", root, clean, names=PROTOCOL["headers"], version=PROTOCOL["version"]
            )
            response = client.post(root, content=clean, headers=headers)
            assert response.status_code == 201, response.text
            with engine.connect() as connection:
                assert connection.scalar(text("SELECT count(*) FROM experiences")) == 1
                assert connection.scalar(text("SELECT count(*) FROM experience_events")) == 1
    finally:
        engine.dispose()
