"""Structured logging, redaction in logs, and the metrics contract."""

from __future__ import annotations

import json
import logging

from fastapi.testclient import TestClient
from iacode_api.config import Settings
from iacode_api.main import create_app
from iacode_api.observability.metrics import UNMATCHED_PATH, Metrics
from iacode_telemetry.context import bind_context
from iacode_telemetry.logging import JsonLogFormatter


def _record_with_extra(message: str, extra: dict[str, object] | None = None) -> logging.LogRecord:
    record = logging.LogRecord(
        name="iacode.test", level=logging.INFO, pathname=__file__, lineno=1,
        msg=message, args=(), exc_info=None,
    )
    for key, value in (extra or {}).items():
        setattr(record, key, value)
    return record


def _record(message: str) -> logging.LogRecord:
    return _record_with_extra(message)


def test_structured_log_contract() -> None:
    formatter = JsonLogFormatter(service="iacode-api", version="0.1.0")

    payload = json.loads(formatter.format(_record("started")))

    assert payload["level"] == "INFO"
    assert payload["service"] == "iacode-api"
    assert payload["message"] == "started"
    assert payload["version"] == "0.1.0"
    assert payload["timestamp"].endswith("Z")


def test_a_field_with_no_value_is_absent_rather_than_null() -> None:
    """Gate 0 has no task, run or agent. Recording them as null teaches readers to ignore them."""
    formatter = JsonLogFormatter(service="iacode-api")

    payload = json.loads(formatter.format(_record("started")))

    for absent in ("taskId", "runId", "agentId", "correlationId", "requestId", "traceId"):
        assert absent not in payload


def test_the_ambient_context_reaches_the_record() -> None:
    formatter = JsonLogFormatter(service="iacode-api")

    with bind_context(correlationId="corr-1", requestId="req-1"):
        payload = json.loads(formatter.format(_record("handled")))

    assert payload["correlationId"] == "corr-1"
    assert payload["requestId"] == "req-1"
    assert "taskId" not in payload


def test_the_context_does_not_outlive_its_block() -> None:
    formatter = JsonLogFormatter(service="iacode-api")

    with bind_context(correlationId="corr-1"):
        pass
    payload = json.loads(formatter.format(_record("later")))

    assert "correlationId" not in payload


def test_secrets_are_redacted_in_logs_and_errors() -> None:
    formatter = JsonLogFormatter(service="iacode-api")

    payload = json.loads(formatter.format(_record_with_extra(
        "connecting to postgresql://iacode:hunter2@db:5432/iacode",
        {"config": {"minio_secret_key": "a-real-secret", "host": "minio"}},
    )))

    assert "hunter2" not in json.dumps(payload)
    assert "a-real-secret" not in json.dumps(payload)
    assert payload["context"]["config"]["minio_secret_key"] == "[REDACTED]"
    # Redaction that removed the host would make the log useless for diagnosis.
    assert payload["context"]["config"]["host"] == "minio"
    assert "db:5432/iacode" in payload["message"]


def test_an_exception_keeps_its_traceback_in_the_log() -> None:
    """The operator's copy is the one place the detail belongs."""
    formatter = JsonLogFormatter(service="iacode-api")
    try:
        raise ValueError("connection to postgresql://iacode:hunter2@db:5432/iacode refused")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="iacode.test", level=logging.ERROR, pathname=__file__, lineno=1,
            msg="failed", args=(), exc_info=sys.exc_info(),
        )
        payload = json.loads(formatter.format(record))

    assert payload["error"]["type"] == "ValueError"
    assert "Traceback" in payload["error"]["traceback"]
    assert "hunter2" not in json.dumps(payload)


def test_metrics_endpoint_exposes_request_metrics(client: TestClient) -> None:
    client.get("/health")

    body = client.get("/metrics").text

    assert "iacode_http_requests_total" in body
    assert "iacode_http_request_duration_seconds_bucket" in body
    assert 'iacode_build_info{service="iacode-api",version="0.0.0-test"} 1.0' in body
    assert 'path="/health"' in body


def test_metrics_label_routes_by_template_not_by_url(client: TestClient) -> None:
    """One time series per identifier is the standard way to take down a Prometheus."""
    for suffix in ("alpha", "beta", "gamma"):
        client.get(f"/does-not-exist/{suffix}")

    body = client.get("/metrics").text

    assert "alpha" not in body
    assert f'path="{UNMATCHED_PATH}"' in body


def test_readiness_updates_the_dependency_gauge(client: TestClient) -> None:
    client.get("/ready")

    body = client.get("/metrics").text

    assert 'iacode_dependency_up{name="postgres",service="iacode-api"} 0.0' in body
    assert 'iacode_dependency_up{name="temporal",service="iacode-api"} 0.0' in body


def test_a_failing_request_is_still_counted(settings: Settings) -> None:
    """Counting only on the success path leaves the in-flight gauge climbing forever."""
    from fastapi import APIRouter

    app = create_app(settings)
    router = APIRouter()

    @router.get("/_test/boom")
    async def boom() -> None:
        raise RuntimeError("no")

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        client.get("/_test/boom")
        body = client.get("/metrics").text

    assert 'status="500"' in body
    # The gauge reads 1 because the /metrics request that is rendering this body is itself in
    # flight. What matters is that the failed request decremented: without the ``finally`` it
    # would read 2 here and keep climbing with every failure.
    assert 'iacode_http_requests_in_flight{service="iacode-api"} 1.0' in body


def test_each_application_owns_its_registry(settings: Settings) -> None:
    """A process-global registry raises on the second application in the same interpreter."""
    first = Metrics(service="iacode-api", version="0.1.0")
    second = Metrics(service="iacode-api", version="0.1.0")

    assert first.registry is not second.registry
