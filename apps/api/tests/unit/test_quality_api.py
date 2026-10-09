"""Quality HTTP surface: bounded inputs, safe outputs, pagination, and workflow ownership."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from iacode_api.config import settings_for_tests
from iacode_api.main import create_app
from iacode_contracts.quality import QualityCheck, QualityPlan, QualityPolicy
from iacode_evaluator.errors import QualityError
from iacode_evaluator.service import PlannedProfile
from iacode_evaluator.store import EventRecord, PlanRecord, RunRecord

RUN_ID = "0199c000-0000-7000-8000-000000000001"
SNAPSHOT_ID = "0199c000-0000-7000-8000-000000000002"
SHA = "a" * 64
OTHER_SHA = "b" * 64
NOW = datetime(2026, 10, 9, 18, tzinfo=UTC)
RUNS = "/api/v1/quality-runs"


def _plan() -> QualityPlan:
    return QualityPlan(
        planId=SHA,
        snapshotId=SNAPSHOT_ID,
        snapshotDigest=OTHER_SHA,
        projectProfile="python",
        projectProfileDigest=SHA,
        policy=QualityPolicy(
            policyId="default",
            version="1.0.0",
            digest=OTHER_SHA,
            profile="python",
            mandatoryCheckKinds=("unit",),
            maxRunSeconds=60,
            maxCheckSeconds=30,
            maxOutputBytes=4096,
        ),
        checks=(
            QualityCheck(
                checkId="q001-unit",
                kind="unit",
                runner="python.unit",
                command=("python", "-m", "unittest"),
                applicabilityReason="required by the Python profile",
                timeoutSeconds=30,
            ),
        ),
        createdAt=NOW,
    )


class _Store:
    def __init__(self) -> None:
        self.plan = _plan()
        self.record = RunRecord(
            run_id=RUN_ID,
            plan_id="plan-row",
            owner_run_id=None,
            state="CREATED",
            idempotency_key="key-1",
            created_at=NOW,
        )

    async def bind_workflow(self, run_id: str, workflow_id: str) -> RunRecord:
        self.record = RunRecord(**{**self.record.__dict__, "workflow_id": workflow_id})
        return self.record

    async def run(self, run_id: str) -> RunRecord | None:
        return self.record if run_id == RUN_ID else None

    async def plan_for_run(self, run_id: str) -> PlanRecord | None:
        return PlanRecord("plan-row", self.plan, None) if run_id == RUN_ID else None

    async def verdict_for_run(self, _run_id: str):
        return None

    async def list_runs(self, *, after=None, limit=25):
        return (self.record,) if after is None and limit else ()

    async def events(self, run_id: str, *, after=0, limit=100):
        if run_id != RUN_ID:
            return []
        event = EventRecord("event-1", RUN_ID, 1, "CREATED", "created", {}, NOW)
        return [event] if after < 1 and limit else []

    async def transition(self, *args, **kwargs):
        return self.record


class _Service:
    def __init__(self, store: _Store) -> None:
        self.store = store

    async def create_profile_and_plan(self, **_kwargs):
        return PlannedProfile(profile=SimpleNamespace(), plan=self.store.plan)

    async def start_run(self, **_kwargs):
        return self.store.record

    async def request_cancel(self, run_id: str, **_kwargs):
        assert run_id == RUN_ID
        self.store.record = RunRecord(**{**self.store.record.__dict__, "state": "CANCELLING"})
        return self.store.record

    async def get_run(self, run_id: str):
        raise QualityError("RUN_NOT_FOUND", f"quality run {run_id} does not exist")


class _Snapshots:
    async def read(self, artifact_id: str, checksum: str):
        assert (artifact_id, checksum) == (SNAPSHOT_ID, OTHER_SHA)
        return {"pyproject.toml": "[project]\nname='example'"}


class _Temporal:
    def __init__(self) -> None:
        self.started: list[dict] = []
        self.signals: list[tuple[str, str]] = []

    async def start_quality_run(self, **kwargs):
        self.started.append(kwargs)
        return kwargs["workflow_id"]

    async def signal_quality_run(self, *, workflow_id, signal, payload=None):
        self.signals.append((workflow_id, signal))
        return True

    async def ping(self):
        return None

    async def close(self):
        return None


@pytest.fixture
def wired():
    app = create_app(settings_for_tests())
    with TestClient(app) as client:
        store = _Store()
        temporal = _Temporal()
        app.state.resources.quality = SimpleNamespace(
            store=store,
            service=_Service(store),
            snapshots=_Snapshots(),
            task_queue="iacode-quality",
        )
        app.state.resources.temporal = temporal
        yield client, store, temporal


class QualityApiTests:
    def test_creation_starts_the_owned_workflow_and_hides_commands(self, wired) -> None:
        client, _store, temporal = wired
        response = client.post(
            RUNS,
            json={
                "snapshotId": SNAPSHOT_ID,
                "snapshotDigest": OTHER_SHA,
                "policyId": "default",
                "idempotencyKey": "key-1",
            },
        )
        assert response.status_code == 202
        body = response.json()
        assert body["runId"] == RUN_ID and body["checks"][0]["kind"] == "unit"
        assert "command" not in str(body).lower()
        assert temporal.started[0]["workflow_id"] == f"iacode-quality-run-{RUN_ID}"

    def test_protected_execution_fields_are_refused_before_the_route(self, wired) -> None:
        client, _store, temporal = wired
        response = client.post(
            RUNS,
            json={
                "snapshotId": SNAPSHOT_ID,
                "snapshotDigest": OTHER_SHA,
                "policyId": "default",
                "idempotencyKey": "key-1",
                "configuration": {"command": "do something else"},
            },
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDATION_ERROR"
        assert temporal.started == []

    def test_list_and_events_are_cursor_bounded(self, wired) -> None:
        client, _store, _temporal = wired
        listed = client.get(RUNS, params={"limit": 1}).json()
        assert listed["nextCursor"] == RUN_ID
        events = client.get(f"{RUNS}/{RUN_ID}/events", params={"after": 0, "limit": 1}).json()
        assert events["nextCursor"] == 1 and len(events["events"]) == 1
        assert client.get(RUNS, params={"limit": 101}).status_code == 422

    def test_cancellation_signals_only_the_bound_workflow(self, wired) -> None:
        client, store, temporal = wired
        store.record = RunRecord(
            **{
                **store.record.__dict__,
                "state": "RUNNING",
                "workflow_id": f"iacode-quality-run-{RUN_ID}",
            }
        )
        response = client.post(f"{RUNS}/{RUN_ID}/cancel")
        assert response.status_code == 200 and response.json()["state"] == "CANCELLING"
        assert temporal.signals == [(f"iacode-quality-run-{RUN_ID}", "cancel_quality_run")]

    def test_not_found_errors_keep_code_and_correlation_identity(self, wired) -> None:
        client, _store, _temporal = wired
        response = client.get(
            f"{RUNS}/0199c000-0000-7000-8000-000000000099",
            headers={"X-Correlation-ID": "quality-test-correlation"},
        )
        assert response.status_code == 404
        assert response.json()["code"] == "RUN_NOT_FOUND"
        assert response.json()["correlationId"] == "quality-test-correlation"
        assert response.headers["X-Correlation-ID"] == "quality-test-correlation"
