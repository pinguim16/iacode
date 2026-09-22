"""The error contract and request correlation.

The two are tested together because they meet in the same place: a failing request must return a
safe body *and* the correlation identifier that leads to the log record holding the unsafe detail.
"""

from __future__ import annotations

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from iacode_api.config import Settings, settings_for_tests
from iacode_api.errors import INTERNAL_MESSAGE, ApiError
from iacode_api.main import create_app
from iacode_api.middleware.correlation import REQUEST_ID_HEADER

SECRET_IN_MESSAGE = "postgresql://iacode:hunter2@db:5432/iacode"


@pytest.fixture
def failing_client(settings: Settings) -> TestClient:
    """An application with routes that fail in each of the ways the contract covers."""
    app = create_app(settings)
    router = APIRouter()

    @router.get("/_test/boom")
    async def boom() -> None:
        # The kind of failure that carries internal detail: a driver error quoting a DSN.
        raise RuntimeError(f"could not connect to {SECRET_IN_MESSAGE}")

    @router.get("/_test/declared")
    async def declared() -> None:
        raise ApiError(code="TEAPOT", message="A declared failure.", http_status=418)

    @router.get("/_test/validated")
    async def validated(count: int) -> dict[str, int]:
        return {"count": count}

    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


def test_internal_error_leaks_nothing(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert body["message"] == INTERNAL_MESSAGE
    # The three things that must never cross the boundary.
    assert "hunter2" not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text


def test_internal_error_still_carries_a_correlation_identifier(
    failing_client: TestClient,
) -> None:
    """Without it the safe message would be unactionable: nothing to quote, nothing to search."""
    response = failing_client.get("/_test/boom")

    correlation_id = response.json()["correlationId"]
    assert correlation_id
    assert response.headers["X-Correlation-ID"] == correlation_id


def test_a_declared_error_keeps_its_code_and_message(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/declared")

    assert response.status_code == 418
    assert response.json()["code"] == "TEAPOT"
    assert response.json()["message"] == "A declared failure."


def test_validation_errors_describe_the_callers_own_input(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/validated?count=not-a-number")

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["details"]["errors"][0]["location"] == ["query", "count"]


def test_validation_errors_do_not_echo_the_submitted_value(failing_client: TestClient) -> None:
    """Echoing input back is how a mistyped credential lands in somebody's log."""
    response = failing_client.get("/_test/validated?count=hunter2-was-typed-here")

    assert response.status_code == 422
    assert "hunter2-was-typed-here" not in response.text


def test_a_missing_route_uses_the_error_contract(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_correlation_identifier_is_generated_when_absent(client: TestClient) -> None:
    response = client.get("/health")

    correlation_id = response.headers["X-Correlation-ID"]
    assert correlation_id
    assert response.headers[REQUEST_ID_HEADER]
    assert correlation_id != response.headers[REQUEST_ID_HEADER]


def test_correlation_identifier_is_propagated(client: TestClient) -> None:
    supplied = "trace-0123456789abcdef"

    response = client.get("/health", headers={"X-Correlation-ID": supplied})

    assert response.headers["X-Correlation-ID"] == supplied


def test_a_malformed_correlation_identifier_is_replaced(client: TestClient) -> None:
    """A header echoed into a response and into logs cannot be arbitrary caller input."""
    for hostile in ("short", "with space", "with\nnewline", "x" * 200):
        response = client.get("/health", headers={"X-Correlation-ID": hostile})

        returned = response.headers["X-Correlation-ID"]
        assert returned != hostile
        assert "\n" not in returned
        assert " " not in returned


def test_the_request_identifier_differs_per_request(client: TestClient) -> None:
    shared = "trace-0123456789abcdef"

    first = client.get("/health", headers={"X-Correlation-ID": shared})
    second = client.get("/health", headers={"X-Correlation-ID": shared})

    assert first.headers["X-Correlation-ID"] == second.headers["X-Correlation-ID"]
    assert first.headers[REQUEST_ID_HEADER] != second.headers[REQUEST_ID_HEADER]


def test_the_correlation_header_name_is_configurable() -> None:
    settings = settings_for_tests(correlation_header="X-IACode-Trace")
    with TestClient(create_app(settings)) as client:
        response = client.get("/health", headers={"X-IACode-Trace": "trace-0123456789abcdef"})

    assert response.headers["X-IACode-Trace"] == "trace-0123456789abcdef"
