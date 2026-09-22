"""The Agent Runtime HTTP API, exercised through the application.

The application is real: the router, the error handler, the serialisation and the middleware are
the code that serves a request. What is replaced is the layer below the route — the service and the
Temporal client — because those are the two things that need a database and a workflow engine, and
both are exercised for real in ``tests/integration`` and in the durability scenario.

What this file is about is the HTTP contract: which status a failure gets, what a caller may and may
not send, that creation answers immediately, that the event stream resumes from a cursor, and that
nothing here offers a way to execute a tool.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_api.config import Settings, settings_for_tests
from iacode_api.main import create_app
from iacode_contracts.agent_runtime import (
    AgentProfileSummary,
    AgentRunCreated,
    AgentRunDetail,
    BudgetView,
    RunEventPage,
    RunEventPayload,
    TeamProfileSummary,
    TeamStageSummary,
    ToolRequestView,
)

RUNS = "/api/v1/agent-runs"
RUN_ID = "0199aa00-0000-7000-8000-000000000001"
TASK_ID = "0199aa00-0000-7000-8000-000000000002"


def budget() -> BudgetView:
    return BudgetView(maxTurns=4, maxModelCalls=6, maxDurationSeconds=60,
                      toolWaitTimeoutSeconds=30)


def detail(state: str = "RUNNING", **overrides) -> AgentRunDetail:
    values = {
        "runId": RUN_ID, "taskId": TASK_ID, "task": "Say IACODE_AGENT_OK.",
        "team": "single-agent", "state": state,
        "createdAt": "2026-09-22T12:00:00.000Z", "budget": budget()}
    values.update(overrides)
    return AgentRunDetail(**values)


class _Plan:
    """What the route hands to Temporal. Its content is the service's business, not the route's."""

    def to_dict(self) -> dict:
        return {"runId": RUN_ID}


class _Service:
    """A service double that records what the route asked of it."""

    def __init__(self) -> None:
        self.created: list = []
        self.cancelled: list[str] = []
        self.submitted: list = []
        self.queued: list[tuple[str, str]] = []
        self.event_reads: list[tuple[str, int]] = []
        self.events_by_cursor: dict[int, list[RunEventPayload]] = {}
        self.detail_state = "RUNNING"
        self.detail_overrides: dict = {}
        self.create_error: Exception | None = None
        self.detail_error: Exception | None = None
        self.submit_error: Exception | None = None
        self.replay = False

    async def create_run(self, payload, *, correlation_id=None):
        if self.create_error:
            raise self.create_error
        self.created.append(payload)
        return _Plan(), AgentRunCreated(
            runId=RUN_ID, taskId=TASK_ID, state="CREATED", team=payload.team,
            createdAt="2026-09-22T12:00:00.000Z", idempotentReplay=self.replay)

    async def mark_queued(self, run_id: str, workflow_id: str) -> None:
        self.queued.append((run_id, workflow_id))

    async def detail(self, run_id: str) -> AgentRunDetail:
        if self.detail_error:
            raise self.detail_error
        return detail(self.detail_state, **self.detail_overrides)

    async def list_runs(self, limit: int = 25):
        return [detail("SUCCEEDED")]

    async def events(self, run_id: str, *, after: int = 0, limit: int = 500) -> RunEventPage:
        self.event_reads.append((run_id, after))
        events = self.events_by_cursor.get(after, [])
        cursor = events[-1].sequence if events else after
        return RunEventPage(runId=run_id, total=len(events), nextCursor=cursor, events=events)

    async def request_cancellation(self, run_id: str) -> AgentRunDetail:
        self.cancelled.append(run_id)
        return detail("CANCELLED")

    async def submit_tool_result(self, run_id: str, submission):
        if self.submit_error:
            raise self.submit_error
        self.submitted.append((run_id, submission))
        return submission

    def agent_summaries(self):
        return [AgentProfileSummary(
            agent="generalist", name="Generalist", role="generalist", description="",
            version="1.0.0", defaultRoute=None, maxTurns=4, allowedActions=[],
            promptTemplate="agents/prompts/generalist.v1.md", promptTemplateVersion="v1",
            promptTemplateHash="0" * 64, enabled=True)]

    def team_summaries(self):
        return [TeamProfileSummary(
            team="single-agent", name="Single agent", description="", version="1.0.0",
            enabled=True,
            stages=[TeamStageSummary(index=0, name="answer", agent="generalist",
                                     inputs=["task"], outputName="answer")])]


class _Store:
    def __init__(self) -> None:
        self.states: list[tuple[str, str]] = []

    async def set_run_state(self, run_id: str, state: str, **fields) -> str:
        self.states.append((run_id, state))
        return state


class _Temporal:
    """A Temporal double. Signals are recorded, not delivered."""

    def __init__(self) -> None:
        self.started: list[dict] = []
        self.signals: list[tuple[str, str]] = []
        self.start_error: Exception | None = None
        self.signal_delivered = True

    async def start_agent_run(self, *, workflow, workflow_id, payload, task_queue,
                              execution_timeout_seconds):
        if self.start_error:
            raise self.start_error
        self.started.append({"workflow": workflow, "workflowId": workflow_id,
                             "taskQueue": task_queue,
                             "timeout": execution_timeout_seconds})
        return workflow_id

    async def signal_agent_run(self, *, workflow_id, signal, payload=None):
        self.signals.append((workflow_id, signal))
        return self.signal_delivered

    async def ping(self) -> None:
        return None

    async def close(self) -> None:
        return None


@pytest.fixture
def wired() -> Iterator[tuple[TestClient, _Service, _Temporal, _Store]]:
    settings: Settings = settings_for_tests()
    app = create_app(settings)
    with TestClient(app) as client:
        resources = app.state.resources
        service, temporal, store = _Service(), _Temporal(), _Store()
        resources.agent_runtime.service = service
        resources.agent_runtime.store = store
        resources.temporal = temporal
        yield client, service, temporal, store


class AgentRunApiTests:
    """Creation, reading, listing, streaming, cancelling and answering a tool request."""

    def test_the_declared_endpoints_are_served(self, wired) -> None:
        client, _, _, _ = wired
        paths = set(client.app.openapi()["paths"])
        for path in (RUNS, f"{RUNS}/{{run_id}}", f"{RUNS}/{{run_id}}/events",
                     f"{RUNS}/{{run_id}}/events/stream", f"{RUNS}/{{run_id}}/cancel",
                     f"{RUNS}/{{run_id}}/tool-results", "/api/v1/agents",
                     "/api/v1/agent-teams"):
            assert path in paths, f"{path} is not served"

    def test_no_endpoint_executes_a_tool(self, wired) -> None:
        """The tool-results endpoint is an inbox. There is no endpoint that runs one."""
        client, _, _, _ = wired
        paths = " ".join(client.app.openapi()["paths"]).lower()
        for forbidden in ("execute", "run-tool", "shell", "exec", "command"):
            assert forbidden not in paths

    def test_reading_a_run_returns_its_detail(self, wired) -> None:
        client, _, _, _ = wired
        response = client.get(f"{RUNS}/{RUN_ID}")
        assert response.status_code == 200
        assert response.json()["runId"] == RUN_ID

    def test_listing_answers_with_the_most_recent_runs(self, wired) -> None:
        client, _, _, _ = wired
        body = client.get(RUNS).json()
        assert body["total"] == 1
        assert body["runs"][0]["state"] == "SUCCEEDED"

    def test_cancelling_records_the_request_and_signals_the_workflow(self, wired) -> None:
        client, service, temporal, _ = wired
        response = client.post(f"{RUNS}/{RUN_ID}/cancel")
        assert response.status_code == 200
        assert response.json()["state"] == "CANCELLED"
        assert service.cancelled == [RUN_ID]
        assert temporal.signals == [(f"iacode-agent-run-{RUN_ID}", "cancel")]


def test_creation_answers_immediately(wired) -> None:
    """The run exists and has been accepted for execution that has not happened yet."""
    client, service, temporal, _ = wired
    response = client.post(RUNS, json={"task": "Say IACODE_AGENT_OK.", "team": "single-agent"})

    assert response.status_code == 202
    body = response.json()
    assert body["runId"] == RUN_ID
    assert body["state"] == "QUEUED"
    assert "result" not in body
    assert temporal.started[0]["workflowId"] == f"iacode-agent-run-{RUN_ID}"
    assert service.queued == [(RUN_ID, f"iacode-agent-run-{RUN_ID}")]


def test_an_idempotent_replay_does_not_start_a_second_workflow(wired) -> None:
    client, service, temporal, _ = wired
    service.replay = True
    response = client.post(RUNS, json={"task": "x", "idempotencyKey": "key-1"})

    assert response.status_code == 202
    assert response.json()["idempotentReplay"] is True
    assert temporal.started == []


def test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created(
        wired) -> None:
    client, _, temporal, store = wired
    temporal.start_error = RuntimeError("temporal is unreachable")

    response = client.post(RUNS, json={"task": "x"})

    assert response.status_code == 503
    assert response.json()["code"] == str(AgentRuntimeErrorType.WORKFLOW_ERROR)
    assert store.states == [(RUN_ID, "FAILED")]


REFUSED_CREATION_PAYLOADS = (
    {"task": "x", "baseUrl": "https://evil.example"},
    {"task": "x", "apiKey": "sk-live-1234"},
    # The value is the repository's own redaction marker: the field is what must be refused, and
    # a credential-shaped literal would trip the repository secret scan for no benefit.
    {"task": "x", "headers": {"Authorization": "[REDACTED]"}},
    {"task": "x", "provider": "somewhere"},
)


def test_creation_cannot_supply_a_credential_or_address(wired) -> None:
    """An address a request can supply is an address an attacker can supply.

    Written as a loop rather than as a parametrisation: the TESTS denominator is derived
    statically from the source, and a runtime expansion cannot be counted that way.
    """
    client, service, _, _ = wired
    for payload in REFUSED_CREATION_PAYLOADS:
        response = client.post(RUNS, json=payload)
        assert response.status_code == 422, payload
        assert service.created == [], payload


def test_creation_refuses_an_empty_task(wired) -> None:
    client, _, _, _ = wired
    assert client.post(RUNS, json={"task": ""}).status_code == 422


def test_run_status_carries_the_declared_fields(wired) -> None:
    client, service, _, _ = wired
    service.detail_state = "WAITING_FOR_TOOL"
    service.detail_overrides = {
        "currentStage": "answer",
        "pendingToolRequest": ToolRequestView(
            toolRequestId="tr-1", agentRunId="ar-1", name="repo.read",
            arguments={"path": "README.md"}, status="PENDING",
            createdAt="2026-09-22T12:00:01.000Z"),
    }

    body = client.get(f"{RUNS}/{RUN_ID}").json()

    for field in ("state", "currentStage", "createdAt", "budget", "stages", "summary",
                  "pendingToolRequest", "trainingAllowed"):
        assert field in body
    assert body["state"] == "WAITING_FOR_TOOL"
    assert body["pendingToolRequest"]["name"] == "repo.read"
    assert body["trainingAllowed"] is False


def test_failure_summary_is_safe(wired) -> None:
    """Error type, safe message, failed stage, correlation identifier. Never a traceback."""
    client, service, _, _ = wired
    service.detail_error = AgentRuntimeError(
        AgentRuntimeErrorType.INVALID_AGENT_OUTPUT,
        "the agent answered with an invalid envelope twice",
        stage="answer", details={"repairAttempted": True, "internalPath": "/app/src/x.py"})

    response = client.get(f"{RUNS}/{RUN_ID}")

    assert response.status_code == 502
    body = response.json()
    assert body["code"] == "INVALID_AGENT_OUTPUT"
    assert body["message"] == "the agent answered with an invalid envelope twice"
    assert body["details"]["stage"] == "answer"
    assert "internalPath" not in body["details"], "an internal detail must not reach a caller"
    assert "Traceback" not in json.dumps(body)
    assert response.headers.get("X-Correlation-ID")


CLASSIFIED_FAILURE_STATUSES = (
    (AgentRuntimeErrorType.TEAM_NOT_FOUND, 404),
    (AgentRuntimeErrorType.PROFILE_NOT_FOUND, 404),
    (AgentRuntimeErrorType.INVALID_REQUEST, 400),
    (AgentRuntimeErrorType.PAYLOAD_TOO_LARGE, 413),
    (AgentRuntimeErrorType.TOOL_RESULT_INVALID, 409),
    (AgentRuntimeErrorType.TOOL_NOT_PERMITTED, 403),
    (AgentRuntimeErrorType.BUDGET_EXCEEDED, 409),
    (AgentRuntimeErrorType.GATEWAY_ERROR, 502),
    (AgentRuntimeErrorType.RUN_DEADLINE_EXCEEDED, 504),
    (AgentRuntimeErrorType.WORKFLOW_ERROR, 503),
    (AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR, 500),
)


def test_every_classified_failure_has_one_status(wired) -> None:
    client, service, _, _ = wired
    for error_type, expected in CLASSIFIED_FAILURE_STATUSES:
        service.detail_error = AgentRuntimeError(error_type, "refused")
        assert client.get(f"{RUNS}/{RUN_ID}").status_code == expected, error_type


def test_oversized_task_is_refused(wired) -> None:
    client, service, _, _ = wired
    service.create_error = AgentRuntimeError(
        AgentRuntimeErrorType.PAYLOAD_TOO_LARGE, "the task is 90000 bytes, above 65536",
        details={"limit": 65536, "size": 90000})

    response = client.post(RUNS, json={"task": "x" * 100})

    assert response.status_code == 413
    assert response.json()["details"]["limit"] == 65536


# ---------------------------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------------------------


def event(sequence: int, event_type: str = "MODEL_CALL_STARTED") -> RunEventPayload:
    return RunEventPayload(runId=RUN_ID, sequence=sequence, type=event_type,
                           createdAt="2026-09-22T12:00:00.000Z", payload={"turn": sequence})


def test_events_are_readable_as_page_and_stream(wired) -> None:
    client, service, _, _ = wired
    service.detail_state = "SUCCEEDED"
    service.events_by_cursor = {0: [event(1), event(2, "RUN_COMPLETED")]}

    page = client.get(f"{RUNS}/{RUN_ID}/events").json()
    assert [item["sequence"] for item in page["events"]] == [1, 2]
    assert page["nextCursor"] == 2

    with client.stream("GET", f"{RUNS}/{RUN_ID}/events/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())
    assert "event: MODEL_CALL_STARTED" in body
    assert "id: 1" in body
    assert "event: RUN_COMPLETED" in body


def test_event_stream_resumes_from_a_cursor(wired) -> None:
    client, service, _, _ = wired
    service.detail_state = "SUCCEEDED"
    service.events_by_cursor = {7: [event(8), event(9, "RUN_COMPLETED")]}

    with client.stream("GET", f"{RUNS}/{RUN_ID}/events/stream?after=7") as response:
        body = "".join(response.iter_text())

    assert "id: 8" in body
    assert "id: 9" in body
    assert service.event_reads[0] == (RUN_ID, 7)


def test_the_stream_accepts_the_standard_reconnect_header(wired) -> None:
    client, service, _, _ = wired
    service.detail_state = "SUCCEEDED"
    service.events_by_cursor = {4: [event(5, "RUN_COMPLETED")]}

    with client.stream("GET", f"{RUNS}/{RUN_ID}/events/stream",
                       headers={"Last-Event-ID": "4"}) as response:
        body = "".join(response.iter_text())

    assert "id: 5" in body
    assert service.event_reads[0] == (RUN_ID, 4)


def test_the_larger_of_the_two_cursors_wins(wired) -> None:
    client, service, _, _ = wired
    service.detail_state = "SUCCEEDED"
    service.events_by_cursor = {9: [event(10, "RUN_COMPLETED")]}

    with client.stream("GET", f"{RUNS}/{RUN_ID}/events/stream?after=9",
                       headers={"Last-Event-ID": "2"}) as response:
        "".join(response.iter_text())

    assert service.event_reads[0] == (RUN_ID, 9)


def test_a_malformed_reconnect_header_is_ignored_rather_than_fatal(wired) -> None:
    client, service, _, _ = wired
    service.detail_state = "SUCCEEDED"
    service.events_by_cursor = {0: [event(1, "RUN_COMPLETED")]}

    with client.stream("GET", f"{RUNS}/{RUN_ID}/events/stream",
                       headers={"Last-Event-ID": "not-a-number"}) as response:
        assert response.status_code == 200
        "".join(response.iter_text())

    assert service.event_reads[0] == (RUN_ID, 0)


def test_reconnection_creates_no_event(wired) -> None:
    """Reading is a read. Two consumers and three reconnections add nothing to the history."""
    client, service, _, _ = wired
    service.detail_state = "SUCCEEDED"
    service.events_by_cursor = {0: [event(1, "RUN_COMPLETED")]}

    for _ in range(3):
        with client.stream("GET", f"{RUNS}/{RUN_ID}/events/stream") as response:
            "".join(response.iter_text())
    client.get(f"{RUNS}/{RUN_ID}/events")

    assert service.created == []
    assert service.submitted == []
    # The service double has no write path at all for a read, which is the point: the route asks
    # only for events.
    assert all(read[0] == RUN_ID for read in service.event_reads)


def test_a_stream_for_an_unknown_run_fails_with_a_status_rather_than_an_empty_stream(
        wired) -> None:
    client, service, _, _ = wired
    service.detail_error = AgentRuntimeError(
        AgentRuntimeErrorType.INVALID_REQUEST, "no run with that identifier")

    assert client.get(f"{RUNS}/{RUN_ID}/events/stream").status_code == 400


# ---------------------------------------------------------------------------------------------
# Tool results
# ---------------------------------------------------------------------------------------------


def test_a_tool_result_is_validated_then_signalled(wired) -> None:
    client, service, temporal, _ = wired
    response = client.post(f"{RUNS}/{RUN_ID}/tool-results", json={
        "toolRequestId": "tr-1", "status": "SUCCEEDED", "output": {"body": "hello"}})

    assert response.status_code == 200
    assert service.submitted[0][0] == RUN_ID
    assert temporal.signals == [(f"iacode-agent-run-{RUN_ID}", "tool_result")]


def test_a_refused_tool_result_never_reaches_the_workflow(wired) -> None:
    """Validated against the store first. A design that signalled first could be forged awake."""
    client, service, temporal, _ = wired
    service.submit_error = AgentRuntimeError(
        AgentRuntimeErrorType.TOOL_RESULT_INVALID, "that tool request belongs to a different run")

    response = client.post(f"{RUNS}/{RUN_ID}/tool-results", json={
        "toolRequestId": "tr-1", "status": "SUCCEEDED"})

    assert response.status_code == 409
    assert temporal.signals == []


def test_a_tool_result_with_an_unknown_status_is_refused(wired) -> None:
    client, service, temporal, _ = wired
    service.submit_error = AgentRuntimeError(
        AgentRuntimeErrorType.TOOL_RESULT_INVALID, "'OK' is not a tool result status")
    assert client.post(f"{RUNS}/{RUN_ID}/tool-results", json={
        "toolRequestId": "tr-1", "status": "OK"}).status_code == 409
    assert temporal.signals == []


def test_a_tool_result_may_not_carry_an_unknown_field(wired) -> None:
    client, _, temporal, _ = wired
    assert client.post(f"{RUNS}/{RUN_ID}/tool-results", json={
        "toolRequestId": "tr-1", "status": "SUCCEEDED",
        "executeNow": True}).status_code == 422
    assert temporal.signals == []


# ---------------------------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------------------------


def test_profiles_and_teams_are_enumerable(wired) -> None:
    client, _, _, _ = wired
    agents = client.get("/api/v1/agents").json()
    teams = client.get("/api/v1/agent-teams").json()

    assert agents[0]["agent"] == "generalist"
    assert agents[0]["promptTemplateHash"]
    assert teams[0]["team"] == "single-agent"
    assert teams[0]["stages"][0]["agent"] == "generalist"


def test_a_profile_listing_carries_no_credential(wired) -> None:
    client, _, _, _ = wired
    body = json.dumps(client.get("/api/v1/agents").json()).lower()
    for forbidden in ("api_key", "apikey", "secret", "token", "authorization", "base_url"):
        assert forbidden not in body
