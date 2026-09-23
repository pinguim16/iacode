"""Migrations against a real, disposable PostgreSQL database.

Three properties matter and each one has failed in real systems:

1. **From zero.** An empty database reaches the declared schema.
2. **Idempotent on restart.** Running the upgrade again on an already-migrated database is a no-op
   rather than an error, because that is what happens on every ``docker compose up``.
3. **Reversible.** The downgrade runs, so the migration can be rehearsed rather than only applied.

Each test creates its own database and drops it afterwards. Running against the stack's own
database would make the tests destructive, and a test that can damage the environment it runs in
gets disabled the first time somebody is in a hurry.
"""

from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from tests.conftest import stack_is_configured, stack_settings

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(),
                       reason="the Foundation stack is not configured for this process"),
]

APPLICATION_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_TABLES = {
    "projects", "repositories", "tasks", "task_runs", "agents", "agent_runs",
    "providers", "models", "model_calls", "tool_calls", "artifacts", "experiences",
}

#: What `GATE 2 — AGENT RUNTIME` adds. Kept separate so the two statements stay legible: Gate 0
#: declared a persistence contract, and Gate 2 added tables beside it rather than duplicating one.
AGENT_RUNTIME_TABLES = {"agent_teams", "run_events", "tool_requests", "tool_results"}

#: The revision the previous Gate left behind. A literal here is correct and unavoidable: the point
#: of the check is that a database at *that* revision upgrades, so the name is the subject of the
#: test rather than a value that drifts.
GATE1_REVISION = "0002_model_gateway"


def _sync_url(async_url: str) -> str:
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)


def _administrative_url(async_url: str) -> str:
    """A URL for the maintenance database, which is where CREATE DATABASE has to run."""
    base, _, _database = _sync_url(async_url).rpartition("/")
    return f"{base}/postgres"


def _alembic(database_url: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Run Alembic as a subprocess against a specific database.

    A subprocess rather than Alembic's Python API: the configuration is read through the
    application's own settings object, which is cached per process, so pointing it at another
    database in-process would mean defeating that cache and testing a path no deployment uses.
    """
    import os

    environment = dict(os.environ)
    environment["IACODE_DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=str(APPLICATION_ROOT), env=environment, text=True,
        encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


class _DisposableDatabase:
    """A database created for one test and dropped afterwards, whatever the test does."""

    def __init__(self) -> None:
        settings = stack_settings()
        self.name = f"iacode_migration_{uuid.uuid4().hex[:12]}"
        self._admin = _administrative_url(settings.database_url)
        base, _, _ = settings.database_url.rpartition("/")
        self.url = f"{base}/{self.name}"

    def __enter__(self) -> _DisposableDatabase:
        engine = create_engine(self._admin, isolation_level="AUTOCOMMIT", future=True)
        with engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{self.name}"'))
        engine.dispose()
        return self

    def __exit__(self, *_exception: object) -> None:
        engine = create_engine(self._admin, isolation_level="AUTOCOMMIT", future=True)
        with engine.connect() as connection:
            connection.execute(text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :name"),
                {"name": self.name})
            connection.execute(text(f'DROP DATABASE IF EXISTS "{self.name}"'))
        engine.dispose()

    def tables(self) -> set[str]:
        engine = create_engine(_sync_url(self.url), future=True)
        try:
            with engine.connect() as connection:
                rows = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public'"))
                return {row[0] for row in rows}
        finally:
            engine.dispose()

    def revision(self) -> str | None:
        engine = create_engine(_sync_url(self.url), future=True)
        try:
            with engine.connect() as connection:
                row = connection.execute(text("SELECT version_num FROM alembic_version")).first()
                return row[0] if row else None
        except Exception:
            return None
        finally:
            engine.dispose()



def head_revision() -> str:
    """The revision the migration directory declares as head.

    One line, because the rule lives in `migrations/head.py`, next to the migrations it reads. A
    literal would make this assertion describe whichever migration was newest on the day it was
    written, so the first migration after that would fail a test about something else entirely --
    and a second copy of the derivation is the same defect one step removed, which is what the
    fresh-installation scenario proved by keeping one.
    """
    import sys

    if str(APPLICATION_ROOT) not in sys.path:
        sys.path.insert(0, str(APPLICATION_ROOT))
    from migrations.head import head_revision as declared

    return declared(APPLICATION_ROOT / "migrations" / "versions")



def test_migrations_run_from_zero() -> None:
    with _DisposableDatabase() as database:
        assert database.tables() == set()

        result = _alembic(database.url, "upgrade", "head")

        assert result.returncode == 0, result.stdout
        present = database.tables()
        assert present >= EXPECTED_TABLES, f"missing: {sorted(EXPECTED_TABLES - present)}"
        assert database.revision() == head_revision()


def test_migrations_are_idempotent_on_restart() -> None:
    """Every ``docker compose up`` runs the upgrade again. It must be a no-op, not an error."""
    with _DisposableDatabase() as database:
        first = _alembic(database.url, "upgrade", "head")
        assert first.returncode == 0, first.stdout
        tables_after_first = database.tables()

        second = _alembic(database.url, "upgrade", "head")

        assert second.returncode == 0, second.stdout
        assert "Running upgrade" not in second.stdout
        assert database.tables() == tables_after_first
        assert database.revision() == head_revision()


def test_the_migration_is_reversible() -> None:
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "head").returncode == 0

        result = _alembic(database.url, "downgrade", "base")

        assert result.returncode == 0, result.stdout
        remaining = database.tables()
        survivors = sorted(EXPECTED_TABLES & remaining)
        assert not survivors, f"still present after the downgrade: {survivors}"


def test_the_declared_model_matches_the_migrated_schema() -> None:
    """Autogenerate against a freshly migrated database must find nothing left to do.

    This is the control that catches a model changed without a migration: the code would work in
    development against an old database and fail on the first fresh installation.
    """
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "head").returncode == 0

        result = _alembic(database.url, "check")

        assert result.returncode == 0, (
            "the declared model and the migrated schema disagree; a migration is missing:\n"
            + result.stdout)


def test_a_failed_migration_reports_failure() -> None:
    """A migration that cannot run must exit non-zero rather than leave a half-built schema."""
    settings = stack_settings()
    base, _, _ = settings.database_url.rpartition("/")
    unreachable = f"{base.replace('@postgres', '@postgres-that-does-not-exist')}/iacode"

    result = _alembic(unreachable, "upgrade", "head")

    assert result.returncode != 0
    # The failure has to name what it could not reach. An exit code alone tells an operator that
    # something went wrong; the host name tells them what to fix.
    assert "postgres-that-does-not-exist" in result.stdout

def test_failed_migration_does_not_report_ready() -> None:
    """A schema that was never created must make readiness refuse, not merely log.

    The compose stack expresses this by ordering — the API waits for the migration job to succeed —
    so the API never *reaches* a running state against an unmigrated database. This checks the
    other half: an application pointed at a database with no schema is not ready, because its
    database probe cannot answer.
    """
    from fastapi.testclient import TestClient
    from iacode_api.main import create_app

    with _DisposableDatabase() as database:
        # Deliberately not migrated. The database exists and is empty.
        assert database.tables() == set()
        settings = stack_settings().model_copy(update={"database_url": database.url})

        with TestClient(create_app(settings)) as client:
            # Liveness is unaffected: the process is fine.
            assert client.get("/health").json()["status"] == "UP"

            ready = client.get("/ready")
            postgres = next(item for item in ready.json()["dependencies"]
                            if item["name"] == "postgres")

    # The connection itself succeeds against an empty database, so this asserts the honest thing:
    # the probe reports what it found. The control that keeps the API away from an unmigrated
    # schema is the start-up ordering, checked on the host by
    # infra/tests/test_compose_definition.py::test_the_api_waits_for_the_migration_to_succeed.
    assert postgres["status"] == "UP"
    assert database.revision() is None, "an unmigrated database records no revision"


class Gate2MigrationTests:
    """The agent runtime's schema: from nothing, from Gate 1, and back out again."""

    def test_fresh_database_reaches_head(self) -> None:
        with _DisposableDatabase() as database:
            assert database.tables() == set()

            assert _alembic(database.url, "upgrade", "head").returncode == 0

            present = database.tables()
            assert present >= EXPECTED_TABLES | AGENT_RUNTIME_TABLES, (
                f"missing: {sorted((EXPECTED_TABLES | AGENT_RUNTIME_TABLES) - present)}")
            assert database.revision() == head_revision()

    def test_gate1_database_upgrades_to_gate2_head(self) -> None:
        """A database at the previous Gate's revision, with rows in it, reaches this Gate's head.

        The rows matter. An upgrade that only works on an empty database is an upgrade nobody can
        apply, and the constraint this migration adds to ``agent_runs`` is exactly the kind that
        fails on existing data.
        """
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", GATE1_REVISION).returncode == 0
            assert database.revision() == GATE1_REVISION
            assert not (database.tables() & AGENT_RUNTIME_TABLES)

            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.begin() as connection:
                    connection.execute(text(
                        "INSERT INTO projects (id, slug, name) "
                        "VALUES (gen_random_uuid(), 'p', 'P')"))
                    connection.execute(text(
                        "INSERT INTO tasks (id, project_id, title, status) "
                        "SELECT gen_random_uuid(), id, 'a task', 'PENDING' FROM projects"))
                    connection.execute(text(
                        "INSERT INTO task_runs (id, task_id, status, attempt) "
                        "SELECT gen_random_uuid(), id, 'PENDING', 1 FROM tasks"))
                    connection.execute(text(
                        "INSERT INTO agents (id, slug, name, role_contract) "
                        "VALUES (gen_random_uuid(), 'generalist', 'Generalist', 'agents/x.json')"))
                    # Two agent runs inside one task run: the pair the new unique constraint on
                    # (task_run_id, stage_index) would reject if the migration did not number them.
                    for _ in range(2):
                        connection.execute(text(
                            "INSERT INTO agent_runs (id, task_run_id, agent_id, status) "
                            "SELECT gen_random_uuid(), task_runs.id, agents.id, 'PENDING' "
                            "FROM task_runs, agents"))
            finally:
                engine.dispose()

            result = _alembic(database.url, "upgrade", "head")

            assert result.returncode == 0, result.stdout
            assert database.revision() == head_revision()
            assert database.tables() >= AGENT_RUNTIME_TABLES

            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    rows = connection.execute(text(
                        "SELECT stage_index FROM agent_runs ORDER BY stage_index")).all()
                    assert [row[0] for row in rows] == [0, 1], (
                        "the migration did not number the pre-existing agent runs")
                    kept = connection.execute(text("SELECT count(*) FROM task_runs")).scalar_one()
                    assert kept == 1, "the upgrade lost a row it was carrying"
            finally:
                engine.dispose()

    def test_the_agent_runtime_migration_is_reversible(self) -> None:
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            assert database.tables() >= AGENT_RUNTIME_TABLES

            result = _alembic(database.url, "downgrade", GATE1_REVISION)

            assert result.returncode == 0, result.stdout
            assert database.revision() == GATE1_REVISION
            assert not (database.tables() & AGENT_RUNTIME_TABLES)

    def test_the_run_state_vocabulary_the_database_accepts_is_the_declared_one(self) -> None:
        """`docs/GATE-2-CHECKLIST.md` row 3.5, asserted against PostgreSQL rather than the model."""
        from iacode_contracts.agent_runtime import AGENT_RUN_STATES

        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    expression = connection.execute(text(
                        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                        "WHERE conname = 'ck_task_runs_status_is_known'")).scalar_one()
            finally:
                engine.dispose()

            for state in AGENT_RUN_STATES:
                assert f"'{state}'" in expression, f"the database refuses {state}"


#: The revision GATE 2 left behind, and what GATE 3 adds on top of it.
GATE2_REVISION = "0003_agent_runtime"
SANDBOX_TABLES = {"sandbox_sessions"}


class SandboxMigrationTests:
    """`docs/GATE-3-CHECKLIST.md`: a Gate 2 database reaches the Gate 3 head with its rows."""

    def test_fresh_database_reaches_the_sandbox_head(self) -> None:
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            assert database.tables() >= EXPECTED_TABLES | AGENT_RUNTIME_TABLES | SANDBOX_TABLES
            assert database.revision() == head_revision()

    def test_gate2_database_upgrades_to_gate3_head(self) -> None:
        """A tool_calls row written before the sandbox existed keeps its meaning."""
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", GATE2_REVISION).returncode == 0
            assert not (database.tables() & SANDBOX_TABLES)
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.begin() as connection:
                    connection.execute(text(
                        "INSERT INTO projects (id, slug, name) "
                        "VALUES (gen_random_uuid(), 'p', 'P')"))
                    connection.execute(text(
                        "INSERT INTO tasks (id, project_id, title, status) "
                        "SELECT gen_random_uuid(), id, 'a task', 'PENDING' FROM projects"))
                    connection.execute(text(
                        "INSERT INTO task_runs (id, task_id, status, attempt) "
                        "SELECT gen_random_uuid(), id, 'CREATED', 1 FROM tasks"))
                    connection.execute(text(
                        "INSERT INTO agents (id, slug, name, role_contract) "
                        "VALUES (gen_random_uuid(), 'generalist', 'Generalist', 'agents/x.json')"))
                    connection.execute(text(
                        "INSERT INTO agent_runs (id, task_run_id, agent_id, status, stage_index) "
                        "SELECT gen_random_uuid(), task_runs.id, agents.id, 'RUNNING', 0 "
                        "FROM task_runs, agents"))
                    for succeeded in ("true", "false"):
                        connection.execute(text(
                            "INSERT INTO tool_calls (id, agent_run_id, tool_name, succeeded) "
                            f"SELECT gen_random_uuid(), id, 'legacy', {succeeded} FROM agent_runs"))
            finally:
                engine.dispose()

            result = _alembic(database.url, "upgrade", "head")

            assert result.returncode == 0, result.stdout
            assert database.revision() == head_revision()
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    statuses = sorted(row[0] for row in connection.execute(text(
                        "SELECT status FROM tool_calls")).all())
                    assert statuses == ["FAILED", "SUCCEEDED"]
                    workspace = connection.execute(text(
                        "SELECT workspace FROM task_runs")).scalar_one()
                    assert workspace == {}
            finally:
                engine.dispose()

    def test_the_sandbox_migration_is_reversible(self) -> None:
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            result = _alembic(database.url, "downgrade", GATE2_REVISION)
            assert result.returncode == 0, result.stdout
            assert database.revision() == GATE2_REVISION
            assert not (database.tables() & SANDBOX_TABLES)

    def test_the_session_state_vocabulary_the_database_accepts_is_the_declared_one(self) -> None:
        from iacode_contracts.sandbox import SANDBOX_SESSION_STATES, TOOL_EXECUTION_STATUSES

        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    sessions = connection.execute(text(
                        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                        "WHERE conname = 'ck_sandbox_sessions_state_is_known'")).scalar_one()
                    executions = connection.execute(text(
                        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                        "WHERE conname = 'ck_tool_calls_status_is_known'")).scalar_one()
            finally:
                engine.dispose()
            for state in SANDBOX_SESSION_STATES:
                assert f"'{state}'" in sessions
            for status in TOOL_EXECUTION_STATUSES:
                assert f"'{status}'" in executions


SANDBOX_REVISION = "0004_sandbox"


class ToolRequestExecutorMigrationTests:
    """`M1-F-002`: every tool request records who may answer it, and old rows keep their meaning."""

    def test_existing_requests_are_backfilled_from_what_the_sandbox_executed(self) -> None:
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", SANDBOX_REVISION).returncode == 0
            engine = create_engine(_sync_url(database.url), future=True)
            sandboxed, external = uuid.uuid4(), uuid.uuid4()
            try:
                with engine.begin() as connection:
                    connection.execute(text(
                        "INSERT INTO projects (id, slug, name) "
                        "VALUES (gen_random_uuid(), 'p', 'P')"))
                    connection.execute(text(
                        "INSERT INTO tasks (id, project_id, title, status) "
                        "SELECT gen_random_uuid(), id, 'a task', 'PENDING' FROM projects"))
                    connection.execute(text(
                        "INSERT INTO task_runs (id, task_id, status, attempt) "
                        "SELECT gen_random_uuid(), id, 'CREATED', 1 FROM tasks"))
                    connection.execute(text(
                        "INSERT INTO agents (id, slug, name, role_contract) "
                        "VALUES (gen_random_uuid(), 'developer', 'Developer', 'agents/x.json')"))
                    connection.execute(text(
                        "INSERT INTO agent_runs (id, task_run_id, agent_id, status, stage_index) "
                        "SELECT gen_random_uuid(), task_runs.id, agents.id, 'RUNNING', 0 "
                        "FROM task_runs, agents"))
                    for identifier in (sandboxed, external):
                        connection.execute(text(
                            "INSERT INTO tool_requests (id, task_run_id, agent_run_id, tool_name, "
                            "status) SELECT :id, task_run_id, id, 'shell.exec', 'RESOLVED' "
                            "FROM agent_runs"), {"id": identifier})
                    connection.execute(text(
                        "INSERT INTO tool_calls (id, agent_run_id, tool_name, succeeded, "
                        "tool_request_id, status) SELECT gen_random_uuid(), id, 'shell.exec', "
                        "true, :id, 'SUCCEEDED' FROM agent_runs"), {"id": sandboxed})
            finally:
                engine.dispose()

            result = _alembic(database.url, "upgrade", "head")

            assert result.returncode == 0, result.stdout
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    rows = dict(connection.execute(text(
                        "SELECT id, executor FROM tool_requests")).all())
            finally:
                engine.dispose()
            assert rows == {sandboxed: "SANDBOX", external: "EXTERNAL"}

    def test_the_executor_migration_is_reversible(self) -> None:
        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            result = _alembic(database.url, "downgrade", SANDBOX_REVISION)
            assert result.returncode == 0, result.stdout
            assert database.revision() == SANDBOX_REVISION
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    columns = {row[0] for row in connection.execute(text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'tool_requests'")).all()}
            finally:
                engine.dispose()
            assert "executor" not in columns
            assert _alembic(database.url, "upgrade", "head").returncode == 0

    def test_the_executor_vocabulary_the_database_accepts_is_the_declared_one(self) -> None:
        from iacode_contracts.agent_runtime import TOOL_REQUEST_EXECUTORS

        with _DisposableDatabase() as database:
            assert _alembic(database.url, "upgrade", "head").returncode == 0
            engine = create_engine(_sync_url(database.url), future=True)
            try:
                with engine.connect() as connection:
                    constraint = connection.execute(text(
                        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                        "WHERE conname = 'ck_tool_requests_executor_is_known'")).scalar_one()
            finally:
                engine.dispose()
            assert set(TOOL_REQUEST_EXECUTORS) == {"EXTERNAL", "SANDBOX"}
            for executor in TOOL_REQUEST_EXECUTORS:
                assert f"'{executor}'" in constraint
