"""Real PostgreSQL, source files and authenticated HTTP in exclusively owned test databases.

Synthetic curated grants authorize only these isolated validation inputs. These are not provider
or user rights, and inserted task facts are not substituted for the separate live workflow proof.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from iacode_api.experience.runtime import build_experience_runtime
from iacode_api.knowledge.runtime import build_knowledge_runtime
from iacode_api.main import create_app
from iacode_common.desktop_auth import signed_headers
from iacode_contracts.desktop import PROTOCOL
from iacode_contracts.experience import CaptureExperience
from iacode_contracts.knowledge import IngestKnowledge
from iacode_evaluator.store import SqlQualityStore
from iacode_knowledge.domain import KnowledgeError, canonical, parse_search
from iacode_persistence.engine import create_engine, create_session_factory
from iacode_persistence.models import Experience, Project, Task, TaskRun
from iacode_persistence.models import KnowledgeDocument as Document
from iacode_persistence.models import KnowledgeEvent as Event
from iacode_persistence.models import KnowledgeIndexEntry as Index
from minio import Minio
from sqlalchemy import create_engine as sync_engine
from sqlalchemy import delete, event, func, select, text
from sqlalchemy.exc import DBAPIError

from tests.conftest import stack_is_configured, stack_settings
from tests.integration.test_migrations import _alembic, _DisposableDatabase, _sync_url
from tests.knowledge_fixture import deploy_source, mutate_grant

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(), reason="real Foundation services not configured"),
]


@pytest.fixture
def database():
    with _DisposableDatabase() as owned:
        result = _alembic(owned.url, "upgrade", "head")
        assert result.returncode == 0, result.stdout[-2000:]
        yield owned


@pytest.fixture
async def rig(database, tmp_path):
    settings = stack_settings().model_copy(
        update={
            "database_url": database.url,
            "knowledge_source_root": str(tmp_path),
        }
    )
    engine = create_engine(database.url, pool_size=8, max_overflow=8)
    sessions = create_session_factory(engine)
    minio = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key.get_secret_value(),
        secret_key=settings.minio_secret_key.get_secret_value(),
        secure=settings.minio_secure,
    )
    experience = build_experience_runtime(settings, sessions, minio, SqlQualityStore(sessions))
    runtime = build_knowledge_runtime(settings, sessions, experience)
    project = str(uuid.uuid4())
    now = datetime.now(UTC)
    async with sessions() as session, session.begin():
        session.add(Project(id=uuid.UUID(project), slug="knowledge-" + project, name="Owned test"))
    fixture = deploy_source(tmp_path, project, now)
    try:
        yield SimpleNamespace(
            runtime=runtime,
            experience=experience,
            sessions=sessions,
            project=project,
            now=now,
            root=tmp_path,
            fixture=fixture,
            database=database,
            settings=settings,
        )
    finally:
        await runtime.close()
        await experience.close()
        await engine.dispose()


async def ingest(rig, fixture=None, now=None, **updates):
    fixture = fixture or rig.fixture
    request = IngestKnowledge.model_validate_json(canonical({**fixture["request"], **updates}))
    return await rig.runtime.service.ingest(rig.project, request, now or rig.now)


async def search(rig, query, *, now=None, limit=10):
    request, tokens = parse_search(
        canonical({"query": query, "limit": limit}), rig.runtime.service.policy
    )
    return await rig.runtime.service.search(rig.project, request, tokens, now or rig.now)


async def refused(operation, code):
    with pytest.raises(KnowledgeError) as caught:
        await operation
    assert caught.value.code == code


async def counts(rig):
    async with rig.sessions() as session:
        return tuple(
            [
                await session.scalar(select(func.count()).select_from(model))
                for model in (Document, Index, Event)
            ]
        )


def policy(rig, **updates):
    previous = rig.runtime.service.policy
    value = type(previous).model_validate_json(
        canonical(
            {
                **previous.model_dump(mode="json"),
                **updates,
            }
        )
    )
    rig.runtime.service.policy = rig.runtime.store.policy = rig.runtime.sources.policy = value
    return previous


async def test_real_publication_restart_exact_spans_and_minimal_audit(rig):
    fixture = deploy_source(
        rig.root, rig.project, rig.now, text="API café\r\nPostgreSQL 🚀 indexes."
    )
    row = await ingest(rig, fixture)
    assert row.state == "ACTIVE" and not row.replay
    document = await rig.runtime.service.deliver(row, rig.now)
    assert "".join(chunk.text for chunk in document.chunks) == fixture["artifact"]["text"]
    restarted = build_knowledge_runtime(rig.settings, rig.sessions, rig.experience)
    loaded = await restarted.store.get(rig.project, row.document_id)
    assert await restarted.service.deliver(loaded, rig.now) == document
    assert await counts(rig) == (1, len(document.chunks), 1)
    for chunk in document.chunks:
        assert fixture["artifact"]["text"][chunk.start : chunk.end] == chunk.text
        assert hashlib.sha256(chunk.text.encode("utf-8")).hexdigest() == chunk.digest
    async with rig.sessions() as session:
        audit = (await session.scalars(select(Event))).one()
        assert set(audit.__table__.columns.keys()) == {"id", "created_at", "document_id", "kind"}
        assert audit.kind == "INDEXED"


async def test_varied_corpus_measures_actual_inverted_matching_rank_and_exact_citations(rig):
    corpus = {
        "full": "PostgreSQL migration rollback.",
        "long": "PostgreSQL migration rollback preserves durable records and audit history.",
        "partial": "PostgreSQL indexes accelerate lookups.",
        "unrelated": "Ocean tides follow the moon.",
        "unicode": "CAFÉ API Unicode \ufb01le \uff21\uff30\uff29.",
    }
    rows = {}
    for name, content in corpus.items():
        fixture = deploy_source(rig.root, rig.project, rig.now, name=name, text=content)
        rows[name] = await ingest(rig, fixture)
    observations = []
    engine = rig.sessions.kw["bind"].sync_engine

    def observe(_connection, _cursor, statement, parameters, _context, _many):
        if "?|" in statement:
            observations.append((statement, parameters))

    event.listen(engine, "before_cursor_execute", observe)
    try:
        hits = await search(rig, "PostgreSQL migration rollback")
    finally:
        event.remove(engine, "before_cursor_execute", observe)
    assert [hit.citation.documentId for hit in hits] == [
        rows[name].document_id for name in ("full", "long", "partial")
    ]
    assert [hit.score for hit in hits] == [3, 3, 1]
    assert observations and all("rollback" not in sql for sql, _ in observations)
    assert all(parameters for _, parameters in observations)
    unicode_hits = await search(rig, "café api file")
    assert len(unicode_hits) == 1 and unicode_hits[0].score == 3
    assert unicode_hits[0].citation.documentId == rows["unicode"].document_id
    assert await search(rig, "volcano absent") == []
    assert await search(rig, "x' OR 1=1 --") == []
    for hit in hits + unicode_hits:
        name = next(
            name for name, row in rows.items() if row.document_id == hit.citation.documentId
        )
        citation = hit.citation
        assert corpus[name][citation.start : citation.end] == hit.excerpt
        assert hashlib.sha256(hit.excerpt.encode()).hexdigest() == citation.chunkDigest
        loaded = await rig.runtime.store.get(rig.project, citation.documentId)
        doc = await rig.runtime.service.deliver(loaded, rig.now)
        assert citation == rig.runtime.service.citation(loaded, doc, doc.chunks[0])
    async with rig.sessions() as session:
        definition = await session.scalar(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE indexname='ix_knowledge_index_entries_tokens'"
            )
        )
        assert "USING gin (tokens)" in definition


async def test_concurrent_stable_retry_and_accepted_response_loss_keep_one_fact(rig):
    rows = await asyncio.gather(*(ingest(rig) for _ in range(4)))
    assert len({row.document_id for row in rows}) == 1
    assert len({row.content_digest for row in rows}) == 1
    # Discard the first response and retry the same request through a reconstructed real runtime.
    rig.runtime = build_knowledge_runtime(rig.settings, rig.sessions, rig.experience)
    replay = await ingest(rig, now=rig.now + timedelta(seconds=1))
    assert replay.replay and replay.document_id == rows[0].document_id
    assert replay.expires_at == rows[0].expires_at
    assert await counts(rig) == (1, 1, 1)


async def test_conflicting_key_and_new_key_cannot_renew_same_material(rig):
    row = await ingest(rig)
    await refused(ingest(rig, retentionSeconds=601), "REQUEST_CONFLICT")
    await refused(ingest(rig, idempotencyKey=str(uuid.uuid4())), "SOURCE_REVISION_CONFLICT")
    assert (await rig.runtime.store.get(rig.project, row.document_id)).expires_at == row.expires_at
    assert await counts(rig) == (1, 1, 1)


async def test_withdrawal_purges_actual_body_index_and_never_resurrects(rig):
    row = await ingest(rig)
    first = await rig.runtime.store.withdraw(rig.project, row.document_id, rig.now)
    second = await rig.runtime.store.withdraw(rig.project, row.document_id, rig.now)
    assert first == second and first.state == "DELETED" and first.body == {}
    await refused(rig.runtime.service.deliver(first, rig.now), "KNOWLEDGE_UNAVAILABLE")
    await refused(ingest(rig), "KNOWLEDGE_UNAVAILABLE")
    await refused(ingest(rig, idempotencyKey=str(uuid.uuid4())), "KNOWLEDGE_UNAVAILABLE")
    assert await search(rig, "PostgreSQL") == []
    assert await counts(rig) == (1, 0, 2)
    async with rig.sessions() as session:
        stored = await session.get(Document, uuid.UUID(row.document_id))
        assert stored.body == {} and stored.purged_at == rig.now and stored.metadata_ == {}
        assert stored.version == 2 and stored.updated_at == rig.now


async def test_actual_retention_check_tracks_lifecycle_version_without_payload_rewrite(rig):
    row = await ingest(rig)
    checked = rig.now + timedelta(seconds=1)
    result = await rig.runtime.store.sweep(rig.runtime.sources, checked)
    assert result == {"checked": 1, "purged": 0, "tombstonesRemoved": 0}
    async with rig.sessions() as session:
        stored = await session.get(Document, uuid.UUID(row.document_id))
        assert stored.version == 2 and stored.updated_at == checked and stored.checked_at == checked
        assert stored.content_digest == row.content_digest and stored.body == row.body
    await rig.runtime.store.withdraw(rig.project, row.document_id, checked)
    async with rig.sessions() as session:
        stored = await session.get(Document, uuid.UUID(row.document_id))
        assert stored.version == 3 and stored.body == {}


async def test_expiry_denies_before_sweep_and_bounded_purge_then_finite_gc(rig):
    policy(rig, batchSize=1, sourceCaptureMaxAgeSeconds=2, tombstoneRetentionSeconds=2)
    row = await ingest(rig, retentionSeconds=1)
    other = deploy_source(rig.root, rig.project, rig.now, name="second")
    await ingest(rig, other, retentionSeconds=1)
    boundary = rig.now + timedelta(seconds=1)
    await refused(rig.runtime.service.deliver(row, boundary), "KNOWLEDGE_UNAVAILABLE")
    assert await rig.runtime.store.page(rig.project, None, 25, boundary) == []
    assert await search(rig, "PostgreSQL", now=boundary) == []
    assert (await rig.runtime.store.sweep(rig.runtime.sources, boundary))["purged"] == 1
    assert await counts(rig) == (2, 1, 3)
    assert (await rig.runtime.store.sweep(rig.runtime.sources, boundary))["purged"] == 1
    assert await counts(rig) == (2, 0, 4)
    later = boundary + timedelta(seconds=3)
    assert (await rig.runtime.store.sweep(rig.runtime.sources, later))["tombstonesRemoved"] == 1
    assert (await rig.runtime.store.sweep(rig.runtime.sources, later))["tombstonesRemoved"] == 1
    assert await counts(rig) == (0, 0, 0)
    await refused(ingest(rig, now=later, idempotencyKey=str(uuid.uuid4())), "SOURCE_TOO_OLD")


async def test_revocation_current_source_change_and_missing_object_never_disclose(rig):
    row = await ingest(rig)
    mutate_grant(rig.root, rig.fixture["entry"], {"status": "REVOKED"})
    await refused(rig.runtime.service.deliver(row, rig.now), "SOURCE_REVOKED")
    assert await search(rig, "PostgreSQL") == []
    assert (await rig.runtime.store.sweep(rig.runtime.sources, rig.now))["purged"] == 1
    assert await counts(rig) == (1, 0, 2)
    changed = deploy_source(rig.root, rig.project, rig.now, name="changed")
    changed_row = await ingest(rig, changed)
    path = rig.root / changed["entry"]["artifactPath"]
    path.write_bytes(path.read_bytes() + b" ")
    await refused(rig.runtime.service.deliver(changed_row, rig.now), "SOURCE_CHANGED")
    assert await search(rig, "PostgreSQL") == []
    path.unlink()
    await refused(rig.runtime.service.deliver(changed_row, rig.now), "SOURCE_OBJECT_UNAVAILABLE")
    await refused(search(rig, "PostgreSQL"), "SOURCE_OBJECT_UNAVAILABLE")


async def test_revision_change_invalidates_old_and_actual_rebuild_publishes_new_citations(rig):
    before = await ingest(rig)
    fixture = deploy_source(
        rig.root,
        rig.project,
        rig.now,
        revision="fixture-v2",
        text="Replacement migration rollback chapter.",
    )
    await refused(rig.runtime.service.deliver(before, rig.now), "SOURCE_CHANGED")
    assert await search(rig, "PostgreSQL") == []
    after = await ingest(rig, fixture)
    assert after.document_id != before.document_id and after.revision == "fixture-v2"
    assert (await rig.runtime.store.get(rig.project, before.document_id)).state == "INVALIDATED"
    hits = await search(rig, "Replacement rollback")
    assert len(hits) == 1 and hits[0].citation.documentId == after.document_id
    assert hits[0].citation.revision == "fixture-v2"
    assert await counts(rig) == (2, 1, 3)


async def test_policy_drift_requires_real_reindex_and_cannot_extend_original_ceiling(rig):
    before = await ingest(rig, retentionSeconds=60)
    policy(rig, maxQueryChars=511)
    await refused(rig.runtime.service.deliver(before, rig.now), "INDEX_STALE")
    await refused(search(rig, "PostgreSQL"), "INDEX_STALE")
    after = await ingest(
        rig,
        now=rig.now + timedelta(seconds=1),
        idempotencyKey=str(uuid.uuid4()),
        retentionSeconds=600,
    )
    assert after.policy_digest != before.policy_digest
    assert after.expires_at == before.expires_at == after.retention_ceiling
    assert after.content_digest != before.content_digest
    assert (await rig.runtime.store.get(rig.project, before.document_id)).body == {}
    assert len(await search(rig, "PostgreSQL", now=rig.now + timedelta(seconds=1))) == 1


async def test_grant_reindex_cannot_reset_original_retention_or_accept_changed_same_revision(rig):
    before = await ingest(rig, retentionSeconds=30)
    mutate_grant(rig.root, rig.fixture["entry"], {"grantId": str(uuid.uuid4())})
    await refused(rig.runtime.service.deliver(before, rig.now), "SOURCE_CHANGED")
    after = await ingest(
        rig,
        now=rig.now + timedelta(seconds=1),
        idempotencyKey=str(uuid.uuid4()),
        retentionSeconds=600,
    )
    assert after.grant_digest != before.grant_digest
    assert after.expires_at == before.expires_at
    changed = deploy_source(rig.root, rig.project, rig.now, text="Changed bytes same revision.")
    await refused(ingest(rig, changed), "SOURCE_REVISION_CONFLICT")


async def test_missing_index_or_audit_is_corruption_not_successful_empty_search(rig):
    row = await ingest(rig)
    async with rig.sessions() as session, session.begin():
        await session.execute(delete(Index).where(Index.document_id == uuid.UUID(row.document_id)))
    await refused(search(rig, "PostgreSQL"), "INDEX_CORRUPT")
    await refused(search(rig, "absent"), "INDEX_CORRUPT")
    await refused(rig.runtime.service.deliver(row, rig.now), "INDEX_CORRUPT")


async def test_missing_indexed_audit_fails_even_with_valid_index_and_digest(rig):
    row = await ingest(rig)
    async with rig.sessions() as session, session.begin():
        await session.execute(delete(Event).where(Event.document_id == uuid.UUID(row.document_id)))
    await refused(search(rig, "PostgreSQL"), "INDEX_CORRUPT")


async def test_capacity_is_explicit_failure_not_silently_truncated_success(rig):
    policy(rig, maxCandidates=1)
    await ingest(rig)
    fixture = deploy_source(rig.root, rig.project, rig.now, name="another")
    await ingest(rig, fixture)
    await refused(search(rig, "PostgreSQL"), "INDEX_CAPACITY_EXCEEDED")
    assert await search(rig, "absent") == []


async def test_audit_failure_rolls_back_document_and_all_index_rows(rig):
    engine = sync_engine(_sync_url(rig.database.url))
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE FUNCTION refuse_owned_knowledge_audit() RETURNS trigger "
                    "LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION "
                    "'owned audit failure'; END $$"
                )
            )
            connection.execute(
                text(
                    "CREATE TRIGGER refuse_owned_knowledge_audit BEFORE INSERT "
                    "ON knowledge_events FOR EACH ROW "
                    "EXECUTE FUNCTION refuse_owned_knowledge_audit()"
                )
            )
        with pytest.raises(DBAPIError):
            await ingest(rig)
        assert await counts(rig) == (0, 0, 0)
    finally:
        engine.dispose()


async def test_real_immutable_guards_and_admin_corruption_are_refused(rig):
    row = await ingest(rig)
    for sql, extra in (
        ("UPDATE knowledge_documents SET content_digest=repeat('a',64) WHERE id=:id", {}),
        (
            "UPDATE knowledge_documents SET body=body || CAST(:body AS JSONB) WHERE id=:id",
            {"body": json.dumps({"forged": True})},
        ),
        ("UPDATE knowledge_index_entries SET tokens='[]'::jsonb WHERE document_id=:id", {}),
        ("UPDATE knowledge_events SET kind='DELETED' WHERE document_id=:id", {}),
    ):
        with pytest.raises(DBAPIError):
            async with rig.sessions() as session, session.begin():
                await session.execute(text(sql), {"id": uuid.UUID(row.document_id), **extra})
    engine = sync_engine(_sync_url(rig.database.url))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE knowledge_documents DISABLE TRIGGER knowledge_document_immutable")
            )
            connection.execute(
                text(
                    "UPDATE knowledge_documents SET body=body || CAST(:body AS JSONB) WHERE id=:id"
                ),
                {"body": json.dumps({"title": "forged"}), "id": row.document_id},
            )
            connection.execute(
                text("ALTER TABLE knowledge_documents ENABLE TRIGGER knowledge_document_immutable")
            )
    finally:
        engine.dispose()
    corrupted = await rig.runtime.store.get(rig.project, row.document_id)
    await refused(rig.runtime.service.deliver(corrupted, rig.now), "STORED_DIGEST_INVALID")
    await refused(search(rig, "absent"), "STORED_DIGEST_INVALID")


async def test_real_source_permission_denial_and_cross_project_have_zero_sql_effects(rig):
    mutate_grant(rig.root, rig.fixture["entry"], {"ragAllowed": False})
    await refused(ingest(rig), "REUSE_PERMISSION_DENIED")
    assert await counts(rig) == (0, 0, 0)
    mutate_grant(rig.root, rig.fixture["entry"], {"ragAllowed": True, "license": "unknown"})
    await refused(ingest(rig), "RIGHTS_EVIDENCE_UNVERIFIED")
    assert await counts(rig) == (0, 0, 0)
    request = IngestKnowledge.model_validate_json(canonical(rig.fixture["request"]))
    await refused(
        rig.runtime.service.ingest(str(uuid.uuid4()), request, rig.now), "SOURCE_NOT_FOUND"
    )
    assert await counts(rig) == (0, 0, 0)


async def test_actual_storage_only_experience_is_validated_then_denied_without_rights_promotion(
    rig,
):
    task, run = uuid.uuid4(), uuid.uuid4()
    async with rig.sessions() as session, session.begin():
        session.add(
            Task(id=task, project_id=uuid.UUID(rig.project), title="Private task not copied")
        )
        await session.flush()
        session.add(
            TaskRun(
                id=run,
                task_id=task,
                status="SUCCEEDED",
                attempt=1,
                started_at=rig.now - timedelta(seconds=2),
                finished_at=rig.now - timedelta(seconds=1),
                result="Private answer",
            )
        )
    request = CaptureExperience(
        taskRunId=str(run),
        storageConsent=True,
        idempotencyKey=str(uuid.uuid4()),
        retentionSeconds=600,
    )
    experience = await rig.experience.service.capture(rig.project, request, rig.now)
    before = canonical(
        (await rig.experience.service.deliver(experience, rig.now)).model_dump(mode="json")
    )
    request = IngestKnowledge(
        sourceKind="experience",
        sourceId=experience.experience_id,
        revision=experience.content_digest,
        storageConsent=True,
        idempotencyKey=str(uuid.uuid4()),
        retentionSeconds=600,
    )
    await refused(
        rig.runtime.service.ingest(rig.project, request, rig.now), "REUSE_PERMISSION_DENIED"
    )
    assert await counts(rig) == (0, 0, 0)
    assert (
        canonical(
            (await rig.experience.service.deliver(experience, rig.now)).model_dump(mode="json")
        )
        == before
    )
    async with rig.sessions() as session:
        assert await session.get(Experience, uuid.UUID(experience.experience_id)) is not None
        assert await session.get(TaskRun, run) is not None


async def test_actual_query_projection_excludes_open_metadata_and_private_runtime_columns(rig):
    row = await ingest(rig)
    statements = []
    engine = rig.sessions.kw["bind"].sync_engine

    def observe(_connection, _cursor, statement, _parameters, _context, _many):
        if statement.startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", observe)
    try:
        assert len(await search(rig, "PostgreSQL")) == 1
        await rig.runtime.store.withdraw(rig.project, row.document_id, rig.now)
    finally:
        event.remove(engine, "before_cursor_execute", observe)
    assert statements
    for statement in statements:
        projection = statement.partition("FROM")[0]
        assert "knowledge_documents.metadata" not in projection
        assert "task_runs." not in projection and "agent_runs." not in projection


def seed_project(database):
    project = str(uuid.uuid4())
    engine = sync_engine(_sync_url(database.url))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO projects(id,slug,name) VALUES(:p,:s,'Owned')"),
                {"p": project, "s": "knowledge-http-" + project},
            )
    finally:
        engine.dispose()
    return project


def test_real_http_authentication_citations_export_page_scope_and_withdrawal(database, tmp_path):
    project = seed_project(database)
    key = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    settings = stack_settings().model_copy(
        update={
            "database_url": database.url,
            "knowledge_source_root": str(tmp_path),
            "desktop_token": type(stack_settings().desktop_token)(key),
            "desktop_token_expires_at": datetime.now(UTC) + timedelta(hours=1),
        }
    )
    fixture = deploy_source(tmp_path, project, datetime.now(UTC))
    root = f"/api/v1/knowledge/projects/{project}"

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

    with TestClient(create_app(settings)) as client:
        for method, suffix in (
            ("POST", "/ingestions"),
            ("POST", "/search"),
            ("GET", "/documents"),
            ("DELETE", "/documents/invalid"),
        ):
            assert send(client, method, root + suffix, authenticated=False).status_code == 401
        response = send(client, "POST", root + "/ingestions", fixture["request"])
        assert response.status_code == 201, response.text
        created = response.json()
        assert send(client, "POST", root + "/ingestions", fixture["request"]).json()[
            "idempotentReplay"
        ]
        target = root + "/documents/" + created["documentId"]
        inspected = send(client, "GET", target)
        exported = send(client, "GET", target + "/export")
        assert inspected.status_code == exported.status_code == 200
        assert (
            inspected.json() == exported.json() and exported.headers["cache-control"] == "no-store"
        )
        hit = send(client, "POST", root + "/search", {"query": "PostgreSQL"}).json()["results"][0]
        citation = send(client, "GET", target + "/chunks/" + hit["citation"]["chunkId"])
        assert citation.status_code == 200 and citation.json()["citation"] == hit["citation"]
        assert citation.json()["excerpt"] == hit["excerpt"]
        page = send(client, "GET", root + "/documents?limit=1").json()
        assert (
            len(page["documents"]) == 1
            and page["documents"][0]["documentId"] == created["documentId"]
        )
        assert (
            send(client, "GET", root + "/documents?cursor=" + page["nextCursor"]).json()[
                "documents"
            ]
            == []
        )
        wrong = f"/api/v1/knowledge/projects/{uuid.uuid4()}"
        assert send(client, "GET", wrong + "/documents/" + created["documentId"]).status_code == 404
        assert (
            send(client, "DELETE", wrong + "/documents/" + created["documentId"]).status_code == 404
        )
        assert (
            send(client, "GET", wrong + "/documents?cursor=" + page["nextCursor"]).status_code
            == 400
        )
        assert (
            send(client, "POST", root + "/search", {"query": "absent"}).json()["outcome"]
            == "NO_PERMITTED_MATCH"
        )
        assert send(client, "GET", target + "?use=training").status_code == 400
        assert send(client, "DELETE", target).json()["state"] == "DELETED"
        assert send(client, "DELETE", target).json()["state"] == "DELETED"
        assert send(client, "GET", target).status_code == 410
        assert send(client, "POST", root + "/ingestions", fixture["request"]).status_code == 410


def test_migration_zero_parity_reversible_preserves_existing_experience_identity():
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "0007_experience_store").returncode == 0
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
                original = connection.execute(
                    text(
                        "SELECT body,rag_allowed,training_allowed,distillation_allowed,"
                        "schema_version,"
                        "state FROM experiences WHERE id=:id"
                    ),
                    {"id": identity},
                ).one()
            result = _alembic(database.url, "upgrade", "head")
            assert result.returncode == 0, result.stdout
            result = _alembic(database.url, "check")
            assert result.returncode == 0, result.stdout
            with engine.connect() as connection:
                assert (
                    str(
                        connection.scalar(
                            text("SELECT id FROM experiences WHERE id=:id"), {"id": identity}
                        )
                    )
                    == identity
                )
                assert (
                    connection.execute(
                        text(
                            "SELECT body,rag_allowed,training_allowed,distillation_allowed,"
                            "schema_version,"
                            "state FROM experiences WHERE id=:id"
                        ),
                        {"id": identity},
                    ).one()
                    == original
                )
            result = _alembic(database.url, "downgrade", "0007_experience_store")
            assert result.returncode == 0, result.stdout
            assert not (
                {"knowledge_documents", "knowledge_index_entries", "knowledge_events"}
                & database.tables()
            )
            with engine.connect() as connection:
                assert (
                    str(
                        connection.scalar(
                            text("SELECT id FROM experiences WHERE id=:id"), {"id": identity}
                        )
                    )
                    == identity
                )
            assert _alembic(database.url, "upgrade", "head").returncode == 0
        finally:
            engine.dispose()
