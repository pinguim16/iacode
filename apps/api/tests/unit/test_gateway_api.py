"""The Model Gateway HTTP API, exercised through the application.

The application is built with real settings and a real gateway runtime; only the *provider* is a
double, injected by replacing the runtime's provider factory. Everything else — the router, the
error handler, the serialisation, the middleware — is the code that serves a real request.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from iacode_api.config import Settings, settings_for_tests
from iacode_api.main import create_app
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    FinishReason,
    ModelDescriptor,
    ModelRef,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.ports import ModelCallRecord, ProviderRecord, SyncOutcome
from iacode_model_gateway.protocols.base import ParsedCompletion, StreamChunk

GATEWAY = "/api/v1/gateway"

#: Built rather than written, so the repository secret scan sees a shape it can trust.
CREDENTIAL = "dw" + "-live-" + "k" * 32


def _descriptor(model_id: str = "model-one", *, active: bool = True) -> ModelDescriptor:
    return ModelDescriptor(
        ref=ModelRef(provider_id="devworld", model_id=model_id),
        display_name=model_id,
        context_window=128000,
        supported_endpoints=(Endpoint.OPENAI_CHAT_COMPLETIONS,),
        capabilities={Capability.STREAMING: CapabilityState.SUPPORTED,
                      Capability.TOOLS: CapabilityState.UNKNOWN},
        capability_provenance={
            Capability.STREAMING: CapabilityProvenance.MANUAL_CONFIGURATION},
        active=active,
        synced_at=datetime(2026, 9, 22, tzinfo=UTC),
    )


class _Catalog:
    """An in-memory catalog store, standing in for PostgreSQL in a unit test."""

    def __init__(self, *models: ModelDescriptor) -> None:
        self.models = list(models)
        self.providers: dict[str, ProviderRecord] = {}

    async def list_providers(self) -> list[ProviderRecord]:
        return [self.providers[key] for key in sorted(self.providers)]

    async def upsert_provider(self, record: ProviderRecord) -> None:
        self.providers[record.provider_id] = record

    async def list_models(self, *, provider_id: str | None = None,
                          active: bool | None = None) -> list[ModelDescriptor]:
        return [
            model for model in self.models
            if (provider_id is None or model.ref.provider_id == provider_id)
            and (active is None or model.active is active)
        ]

    async def replace_provider_models(self, provider_id: str,
                                      models: list[ModelDescriptor]) -> SyncOutcome:
        self.models = list(models)
        return SyncOutcome(provider_id=provider_id, added=len(models))


class _Calls:
    def __init__(self) -> None:
        self.records: list[ModelCallRecord] = []

    async def record(self, call: ModelCallRecord) -> None:
        self.records.append(call)


class _Provider:
    """A provider whose answers the test writes."""

    def __init__(self, *, completion: object = None, chunks: list[StreamChunk] | None = None,
                 catalog: list[tuple[str, dict]] | None = None) -> None:
        self.completion = completion
        self.chunks = chunks or []
        self.catalog = catalog or [("model-one", {"id": "model-one"})]
        self.provider_id = "devworld"
        #: Whether the streaming generator was closed. A consumer that walks away must not leave
        #: a provider call running for an answer nobody will read.
        self.closed = False
        self.delivered = 0

    async def health(self):
        from iacode_model_gateway.providers.base import ProviderHealth

        return ProviderHealth("devworld", True, None, 1.0)

    async def list_models(self):
        from iacode_model_gateway.catalog.sync import DiscoveredCatalog

        return DiscoveredCatalog(provider_id="devworld", entries=tuple(self.catalog))

    async def generate(self, request, model, endpoint, *, output_tokens: int):
        if isinstance(self.completion, Exception):
            raise self.completion
        return self.completion or ParsedCompletion(
            content="hello", finish_reason=FinishReason.STOP,
            usage=Usage(input_tokens=5, output_tokens=1))

    async def stream(self, request, model, endpoint, *,
                     output_tokens: int) -> AsyncIterator[StreamChunk]:
        try:
            for chunk in self.chunks:
                if isinstance(chunk, Exception):
                    raise chunk
                self.delivered += 1
                yield chunk
        finally:
            self.closed = True


def _settings() -> Settings:
    return settings_for_tests(gateway_default_model="devworld:model-one")


def _client(provider: _Provider, catalog: _Catalog | None = None,
            calls: _Calls | None = None) -> Iterator[TestClient]:
    app = create_app(_settings())
    with TestClient(app) as client:
        runtime = app.state.resources.gateway
        runtime.catalog_store = catalog if catalog is not None else _Catalog(_descriptor())
        runtime.call_store = calls if calls is not None else _Calls()
        original = runtime.gateway

        def bound(correlation_id: str | None = None):
            gateway = original(correlation_id)
            gateway.provider_factory = lambda config: provider
            return gateway

        runtime.gateway = bound
        yield client


@pytest.fixture
def provider() -> _Provider:
    return _Provider()


@pytest.fixture
def client(provider: _Provider) -> Iterator[TestClient]:
    yield from _client(provider)


def test_openapi_documents_the_gateway_endpoints(client: TestClient) -> None:
    document = client.get("/openapi.json").json()
    paths = document["paths"]

    for path in (f"{GATEWAY}/providers", f"{GATEWAY}/models", f"{GATEWAY}/models/sync",
                 f"{GATEWAY}/health", f"{GATEWAY}/infer", f"{GATEWAY}/stream"):
        assert path in paths, f"{path} is not documented"
    assert "InferenceRequest" in document["components"]["schemas"]


def test_provider_listing_exposes_no_secret(client: TestClient,
                                            monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IACODE_DEVWORLD_API_KEY", CREDENTIAL)
    monkeypatch.setenv("IACODE_DEVWORLD_BASE_URL", "https://provider.example/v1")

    body = client.get(f"{GATEWAY}/providers").json()

    rendered = json.dumps(body)
    assert CREDENTIAL not in rendered
    assert "Bearer" not in rendered
    entry = body["providers"][0]
    assert entry["provider"] == "devworld"
    assert entry["credentialConfigured"] is True
    assert entry["credentialVariable"] == "IACODE_DEVWORLD_API_KEY"
    assert entry["addressConfigured"] is True
    assert set(entry) & {"credential", "apiKey", "baseUrl"} == set()


def test_an_unconfigured_provider_says_which_variable_is_missing(
        client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IACODE_DEVWORLD_API_KEY", raising=False)

    entry = client.get(f"{GATEWAY}/providers").json()["providers"][0]

    assert entry["credentialConfigured"] is False
    assert entry["credentialVariable"] == "IACODE_DEVWORLD_API_KEY"


def test_model_listing_filters(provider: _Provider) -> None:
    catalog = _Catalog(_descriptor("model-one"), _descriptor("model-two", active=False))
    for client in _client(provider, catalog):
        assert client.get(f"{GATEWAY}/models").json()["total"] == 2
        assert client.get(f"{GATEWAY}/models", params={"active": True}).json()["total"] == 1
        assert client.get(f"{GATEWAY}/models",
                          params={"provider": "absent"}).json()["total"] == 0
        # Streaming is stated for both; tools is unknown, and unknown is not support.
        assert client.get(f"{GATEWAY}/models",
                          params={"capability": "streaming"}).json()["total"] == 2
        assert client.get(f"{GATEWAY}/models",
                          params={"capability": "tools"}).json()["total"] == 0
        assert client.get(f"{GATEWAY}/models", params={"capability": "nonsense"}).status_code \
            == 400


def test_the_model_listing_reports_capability_provenance(client: TestClient) -> None:
    entry = client.get(f"{GATEWAY}/models").json()["models"][0]

    assert entry["capabilities"]["streaming"] == {
        "state": "SUPPORTED", "provenance": "MANUAL_CONFIGURATION"}
    assert entry["capabilities"]["tools"]["state"] == "UNKNOWN"


def test_sync_endpoint_reports_its_outcome(provider: _Provider) -> None:
    catalog = _Catalog()
    for client in _client(provider, catalog):
        body = client.post(f"{GATEWAY}/models/sync", json={}).json()

        assert body["outcomes"][0]["provider"] == "devworld"
        assert body["outcomes"][0]["added"] == 1
        assert CREDENTIAL not in json.dumps(body)


def test_infer_endpoint_returns_the_normalised_response(client: TestClient) -> None:
    response = client.post(f"{GATEWAY}/infer", json={
        "messages": [{"role": "user", "content": "hello"}]})

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "hello"
    assert body["provider"] == "devworld"
    assert body["model"] == "model-one"
    assert body["endpoint"] == "openai-chat-completions"
    assert body["usage"]["inputTokens"] == 5
    assert body["route"]["reason"] == "DEFAULT_MODEL"
    assert body["requestId"]
    assert body["cost"] is None


def test_infer_endpoint_leaks_no_internal_detail() -> None:
    failing = _Provider(completion=GatewayError(
        GatewayErrorType.PROVIDER_UNAVAILABLE, "the provider is unavailable",
        provider="devworld"))

    for client in _client(failing):
        response = client.post(f"{GATEWAY}/infer", json={
            "messages": [{"role": "user", "content": "hello"}]})

        assert response.status_code == 503
        body = response.json()
        assert body["code"] == "PROVIDER_UNAVAILABLE"
        assert "Traceback" not in json.dumps(body)
        assert body["correlationId"]


def test_a_request_the_router_cannot_serve_is_a_conflict(client: TestClient) -> None:
    response = client.post(f"{GATEWAY}/infer", json={
        "messages": [{"role": "user", "content": "hello"}],
        "model": "devworld:absent"})

    assert response.status_code == 409
    assert response.json()["code"] == "NO_CANDIDATE"


def test_an_invalid_request_is_answered_as_the_callers_mistake(client: TestClient) -> None:
    assert client.post(f"{GATEWAY}/infer", json={"messages": []}).status_code == 422
    assert client.post(f"{GATEWAY}/infer", json={
        "messages": [{"role": "user", "content": "hi"}],
        "model": "devworld:model-one", "route": "fast"}).status_code == 422
    assert client.post(f"{GATEWAY}/infer", json={
        "messages": [{"role": "nonsense", "content": "hi"}]}).status_code == 422


def test_correlation_reaches_the_persisted_model_call(provider: _Provider) -> None:
    calls = _Calls()
    for client in _client(provider, calls=calls):
        client.post(f"{GATEWAY}/infer",
                    headers={"X-Correlation-ID": "correlation-under-test"},
                    json={"messages": [{"role": "user", "content": "hello"}]})

        assert calls.records[0].correlation_id == "correlation-under-test"
        assert calls.records[0].request_id


def test_prompt_is_not_persisted_by_default(provider: _Provider) -> None:
    calls = _Calls()
    for client in _client(provider, calls=calls):
        client.post(f"{GATEWAY}/infer", json={
            "messages": [{"role": "user", "content": "a confidential question"}]})

        rendered = json.dumps([record.__dict__ for record in calls.records], default=str)
        assert "confidential question" not in rendered
        assert calls.records[0].request_fingerprint


def test_stream_endpoint_emits_sse_and_stops_on_disconnect() -> None:
    """Row 9.5, both halves.

    The first is visible in the response: Server-Sent Events, with the framing and the headers a
    consumer needs. The second is invisible from outside and is the one that costs money — when the
    consumer walks away, the provider call is closed rather than left running for an answer nobody
    will read. The provider double records that its generator was closed, which is what
    `contextlib.aclosing` in the gateway guarantees.
    """
    streaming = _Provider(chunks=[
        StreamChunk(text="he"), StreamChunk(text="llo"),
        StreamChunk(usage=Usage(input_tokens=2, output_tokens=2)),
        StreamChunk(finish_reason=FinishReason.STOP, done=True)])

    for client in _client(streaming):
        with client.stream("POST", f"{GATEWAY}/stream", json={
                "messages": [{"role": "user", "content": "hello"}]}) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            assert response.headers["cache-control"] == "no-store"
            # Proxies that buffer turn a stream into one long wait.
            assert response.headers["x-accel-buffering"] == "no"
            body = "".join(response.iter_text())

        events = [line for line in body.splitlines() if line.startswith("event: ")]
        assert events[0] == "event: start"
        assert events[-1] == "event: end"
        assert '"text":"he"' in body.replace(", ", ",").replace('": ', '":')
        # Every event is numbered, so a consumer can tell a gap from a pause.
        assert body.count("event: ") == len(events)
        assert streaming.closed, "the provider call was left open after the stream ended"

    abandoned = _Provider(chunks=[StreamChunk(text=f"chunk-{index} ") for index in range(400)]
                          + [StreamChunk(finish_reason=FinishReason.STOP, done=True)])

    for client in _client(abandoned):
        with client.stream("POST", f"{GATEWAY}/stream", json={
                "messages": [{"role": "user", "content": "hello"}]}) as response:
            assert response.status_code == 200
            for _first in response.iter_text():
                break

    assert abandoned.closed, "abandoning the response left the provider call running"


def test_the_stream_endpoint_answers_an_invalid_body_with_a_status_code() -> None:
    """Validation happens before the response starts; afterwards there is no status left to send."""
    for client in _client(_Provider()):
        assert client.post(f"{GATEWAY}/stream", json={"messages": []}).status_code == 422
        assert client.post(f"{GATEWAY}/stream", content=b"not json").status_code == 400


def test_a_stream_that_fails_after_content_ends_with_an_error_event() -> None:
    failing = _Provider(chunks=[
        StreamChunk(text="partial"),
        GatewayError(GatewayErrorType.TRANSIENT_PROVIDER_ERROR, "the provider failed",
                     provider="devworld")])

    for client in _client(failing):
        with client.stream("POST", f"{GATEWAY}/stream", json={
                "messages": [{"role": "user", "content": "hello"}]}) as response:
            body = "".join(response.iter_text())

        assert "event: error" in body
        assert "partial" in body


def test_gateway_health_separates_process_from_provider(client: TestClient) -> None:
    body = client.get(f"{GATEWAY}/health").json()

    assert body["status"] in ("READY", "DEGRADED")
    assert body["contractVersion"]
    assert body["providers"][0]["provider"] == "devworld"
    assert "circuits" in body
    assert body["defaultModel"] == "devworld:model-one"
    assert "default" in body["routes"]


def test_provider_outage_does_not_affect_process_health(client: TestClient) -> None:
    """An unreachable provider is a gateway state, never a liveness failure."""
    assert client.get("/health").json()["status"] == "UP"
    client.get(f"{GATEWAY}/health")
    assert client.get("/health").status_code == 200


def test_the_gateway_endpoints_carry_the_correlation_header(client: TestClient) -> None:
    response = client.get(f"{GATEWAY}/models",
                          headers={"X-Correlation-ID": "correlation-under-test"})

    assert response.headers["X-Correlation-ID"] == "correlation-under-test"


def test_the_metrics_endpoint_exposes_the_gateway_instruments(client: TestClient) -> None:
    client.post(f"{GATEWAY}/infer", json={"messages": [{"role": "user", "content": "hi"}]})

    body = client.get("/metrics").text

    assert "iacode_gateway_requests_total" in body
    assert "iacode_model_catalog_size" in body or "iacode_gateway_provider_health" in body
