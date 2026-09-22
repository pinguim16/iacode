"""The application itself: how it starts, what it holds, what it exposes and how it stops."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient
from iacode_api.config import Settings, settings_for_tests
from iacode_api.dependencies import build_probes, get_resources
from iacode_api.lifespan import build_resources, release_resources
from iacode_api.main import create_app
from iacode_api.observability.metrics import Metrics


def test_application_starts(settings: Settings) -> None:
    """Start-up performs no I/O, so the API comes up while its dependencies are still coming up.

    An API that refuses to start without its database turns a ten-second dependency delay into a
    restart storm. Readiness exists precisely so start-up does not have to wait.
    """
    app = create_app(settings)

    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert app.state.resources is not None


def test_dependencies_are_held_on_application_state(settings: Settings) -> None:
    """No module-level client. Two applications in one interpreter must not share a pool."""
    first = create_app(settings)
    second = create_app(settings)

    with TestClient(first), TestClient(second):
        assert first.state.resources is not second.state.resources
        assert first.state.resources.engine is not second.state.resources.engine
        assert first.state.metrics is not second.state.metrics


def test_resources_are_released_after_shutdown(settings: Settings) -> None:
    app = create_app(settings)
    with TestClient(app):
        pass

    assert app.state.resources is None


def test_shutdown_releases_every_client(settings: Settings) -> None:
    """Every client is released, and a failure in one does not strand the rest."""

    async def exercise() -> list[str]:
        resources = build_resources(settings, Metrics(service="iacode-api", version="0.0.0-test"))

        class Exploding:
            async def close(self) -> None:
                raise RuntimeError("this client refuses to close")

        resources.temporal = Exploding()  # type: ignore[assignment]
        return await release_resources(resources)

    failures = asyncio.run(exercise())

    # The failing client is reported, and the ones after it were still released: `release_resources`
    # returns only the names that failed.
    assert failures == ["temporal"]


def test_every_mandatory_dependency_is_probed(settings: Settings) -> None:
    app = create_app(settings)
    with TestClient(app) as client:
        resources = get_resources(_request_of(client, app))
        probes = build_probes(resources)

    assert {probe.name for probe in probes} == {"postgres", "redis", "minio", "temporal"}
    assert all(probe.mandatory for probe in probes)


def _request_of(client: TestClient, app):
    """A minimal request object carrying the application, for dependency providers."""
    from starlette.requests import Request

    return Request({"type": "http", "app": app, "headers": [], "method": "GET", "path": "/"})


def test_version_exposes_no_secret(settings: Settings) -> None:
    """`/version` answers what is running, and nothing about how it authenticates."""
    settings = settings_for_tests(
        database_url="postgresql+asyncpg://iacode:hunter2@db:5432/iacode",
        minio_secret_key="a-real-looking-secret",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/version")

    body = response.json()
    assert response.status_code == 200
    assert set(body) == {
        "service", "version", "commit", "buildTimestamp", "pythonVersion", "environment"}
    text = response.text
    for forbidden in ("hunter2", "a-real-looking-secret", "postgresql", "minio", "redis"):
        assert forbidden not in text, f"/version exposes {forbidden!r}"


def test_openapi_documents_the_foundation_endpoints(client: TestClient) -> None:
    document = client.get("/openapi.json").json()

    paths = set(document["paths"])
    assert {"/health", "/ready", "/version"} <= paths
    assert document["info"]["title"] == "IACode API"
    for path in ("/health", "/ready", "/version"):
        assert document["paths"][path]["get"]["description"], f"{path} is undocumented"


def test_metrics_is_not_part_of_the_api_contract(client: TestClient) -> None:
    """It is an operational surface for the scraper, and its body is not JSON."""
    document = client.get("/openapi.json").json()

    assert "/metrics" not in document["paths"]
    assert client.get("/metrics").status_code == 200


def test_readiness_documents_its_failure_response(client: TestClient) -> None:
    """A caller has to know 503 is an answer with a body, not a transport failure."""
    document = client.get("/openapi.json").json()

    assert "503" in document["paths"]["/ready"]["get"]["responses"]


def test_cors_is_explicit_and_not_wildcard() -> None:
    settings = settings_for_tests(cors_allow_origins=["http://localhost:18081"])
    with TestClient(create_app(settings)) as client:
        allowed = client.get("/health", headers={"Origin": "http://localhost:18081"})
        refused = client.get("/health", headers={"Origin": "http://evil.example"})

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:18081"
    # Not `*`, and not the requesting origin echoed back: an origin that was not listed gets no
    # CORS header at all, which is what makes the list mean something.
    assert "access-control-allow-origin" not in refused.headers


def test_cors_allows_the_local_frontend_to_read_the_correlation_header() -> None:
    """Without the expose header a browser cannot read the identifier it is told to quote."""
    settings = settings_for_tests(cors_allow_origins=["http://localhost:18081"])
    with TestClient(create_app(settings)) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:18081"})

    exposed = response.headers.get("access-control-expose-headers", "")
    assert "X-Correlation-ID" in exposed
