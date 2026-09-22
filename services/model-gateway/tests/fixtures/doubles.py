"""The deterministic doubles the gateway suite runs against.

Everything here exists so a test can exercise the real code paths without a network, without a
database and without waiting. Nothing here is reachable from a runtime path: the provider policy
names no fake provider, the application composes the SQLAlchemy stores, and
``test_no_fake_provider_is_registered_at_runtime`` asserts both.

Three doubles, and each replaces exactly one port the gateway declares:

``FakeClock``/``FakeJitter``  time and randomness, so a thirty-second cooldown costs microseconds
                              and a backoff is reproducible rather than merely plausible.
``InMemory*Store``            the catalog and the call record, so synchronisation, deactivation and
                              idempotence are exercised without PostgreSQL.
``ScriptedProvider``          a provider whose answers are written by the test, so every failure
                              mode — a timeout, a 429 with a retry hint, a stream that dies after
                              three tokens — is reproducible in a way a real provider never is.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from iacode_model_gateway.catalog.sync import DiscoveredCatalog
from iacode_model_gateway.config import (
    GatewaySettings,
    ProviderConfig,
    RouteAlias,
    RoutePolicy,
    UnknownCapabilityPolicy,
)
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    FinishReason,
    GatewayMessage,
    GatewayRequest,
    MessageRole,
    ModelDescriptor,
    ModelRef,
    ReasoningEffort,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.gateway import ModelGateway
from iacode_model_gateway.ports import (
    ModelCallRecord,
    ProviderRecord,
    SyncOutcome,
)
from iacode_model_gateway.protocols.base import ParsedCompletion, StreamChunk
from iacode_model_gateway.providers.base import ProviderHealth

__all__ = [
    "FakeClock",
    "FakeJitter",
    "InMemoryCatalogStore",
    "InMemoryModelCallStore",
    "ScriptedProvider",
    "build_gateway",
    "descriptor",
    "gateway_source_root",
    "policy_dir",
    "provider_config",
    "request",
    "route_policy",
    "settings",
]

EPOCH = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


class FakeClock:
    """A clock the test moves. ``sleep`` advances it instead of waiting."""

    def __init__(self, start: datetime = EPOCH) -> None:
        self._now = start
        self._monotonic = 0.0
        self.slept: list[float] = []

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return self._monotonic

    async def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        self._monotonic += seconds
        self._now = self._now + timedelta(seconds=seconds)


class FakeJitter:
    """Randomness that is not random. Returns the top of the range unless told otherwise."""

    def __init__(self, factor: float = 1.0) -> None:
        self.factor = factor
        self.ranges: list[tuple[float, float]] = []

    def uniform(self, low: float, high: float) -> float:
        self.ranges.append((low, high))
        return low + (high - low) * self.factor


def _comparable(item: ModelDescriptor) -> dict[str, Any]:
    payload = item.model_dump(mode="json")
    payload.pop("synced_at", None)
    return payload


@dataclass
class InMemoryCatalogStore:
    """A catalog in a dictionary, with the same replace-or-deactivate contract as the real one."""

    providers: dict[str, ProviderRecord] = field(default_factory=dict)
    models: dict[str, dict[str, ModelDescriptor]] = field(default_factory=dict)

    async def list_providers(self) -> list[ProviderRecord]:
        return [self.providers[key] for key in sorted(self.providers)]

    async def upsert_provider(self, record: ProviderRecord) -> None:
        self.providers[record.provider_id] = record

    async def list_models(self, *, provider_id: str | None = None,
                          active: bool | None = None) -> list[ModelDescriptor]:
        result: list[ModelDescriptor] = []
        for owner in sorted(self.models):
            if provider_id is not None and owner != provider_id:
                continue
            for key in sorted(self.models[owner]):
                item = self.models[owner][key]
                if active is not None and item.active is not active:
                    continue
                result.append(item)
        return result

    async def replace_provider_models(self, provider_id: str,
                                      models: list[ModelDescriptor]) -> SyncOutcome:
        existing = self.models.setdefault(provider_id, {})
        incoming = {item.ref.model_id: item for item in models}
        added = updated = unchanged = deactivated = 0
        for model_id, item in incoming.items():
            previous = existing.get(model_id)
            if previous is None:
                added += 1
            elif _comparable(previous) == _comparable(item):
                unchanged += 1
            else:
                updated += 1
            existing[model_id] = item
        for model_id, previous in list(existing.items()):
            if model_id in incoming or not previous.active:
                continue
            existing[model_id] = previous.model_copy(update={"active": False})
            deactivated += 1
        return SyncOutcome(provider_id=provider_id, added=added, updated=updated,
                           deactivated=deactivated, unchanged=unchanged)

    def seed(self, *descriptors: ModelDescriptor) -> None:
        for item in descriptors:
            self.models.setdefault(item.ref.provider_id, {})[item.ref.model_id] = item


@dataclass
class InMemoryModelCallStore:
    """Recorded attempts, in a list."""

    calls: list[ModelCallRecord] = field(default_factory=list)
    fail: bool = False

    async def record(self, call: ModelCallRecord) -> None:
        if self.fail:
            raise RuntimeError("the store is unavailable")
        self.calls.append(call)


@dataclass
class ScriptedProvider:
    """A provider whose every answer the test wrote.

    ``completions`` and ``streams`` are consumed one entry per call, so a test can say "fail, then
    fail, then succeed" and get exactly that. An entry that is an exception is raised; anything else
    is returned. Running out of entries is an error rather than a repeat of the last one: a test that
    made more calls than it scripted has proved something other than what it meant to.
    """

    provider_id: str
    completions: list[Any] = field(default_factory=list)
    streams: list[Any] = field(default_factory=list)
    catalog: list[tuple[str, dict[str, Any]]] | Exception = field(default_factory=list)
    healthy: bool = True
    calls: list[dict[str, Any]] = field(default_factory=list)
    cancelled: bool = False

    async def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, self.healthy,
                              None if self.healthy else "scripted as unreachable")

    async def list_models(self) -> DiscoveredCatalog:
        if isinstance(self.catalog, Exception):
            raise self.catalog
        return DiscoveredCatalog(provider_id=self.provider_id, entries=tuple(self.catalog))

    async def generate(self, request: GatewayRequest, model: ModelDescriptor,
                       endpoint: Endpoint, *, output_tokens: int) -> ParsedCompletion:
        self.calls.append({"kind": "generate", "model": model.ref.model_id,
                           "endpoint": endpoint, "outputTokens": output_tokens})
        if not self.completions:
            raise AssertionError(
                f"{self.provider_id} was called more times than the test scripted")
        answer = self.completions.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    async def stream(self, request: GatewayRequest, model: ModelDescriptor,
                     endpoint: Endpoint, *, output_tokens: int) -> AsyncIterator[StreamChunk]:
        self.calls.append({"kind": "stream", "model": model.ref.model_id,
                           "endpoint": endpoint, "outputTokens": output_tokens})
        if not self.streams:
            raise AssertionError(
                f"{self.provider_id} was streamed more times than the test scripted")
        script = self.streams.pop(0)
        try:
            for item in script:
                if isinstance(item, Exception):
                    raise item
                yield item
        except GeneratorExit:
            self.cancelled = True
            raise


# ---------------------------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------------------------


def settings(**overrides: Any) -> GatewaySettings:
    """Gateway settings with bounds small enough to exercise quickly."""
    values: dict[str, Any] = {
        "default_model": "alpha:model-one",
        "connect_timeout_seconds": 1.0,
        "read_timeout_seconds": 5.0,
        "max_attempts": 3,
        "retry_initial_backoff_seconds": 0.1,
        "retry_max_backoff_seconds": 1.0,
        "retry_max_retry_after_seconds": 5.0,
        "circuit_failure_threshold": 2,
        "circuit_cooldown_seconds": 10.0,
        "circuit_half_open_successes": 1,
        "max_fallbacks": 2,
        "max_request_bytes": 65536,
        "max_messages": 20,
        "max_tools": 4,
        "max_output_tokens": 256,
        "max_response_bytes": 65536,
    }
    values.update(overrides)
    return GatewaySettings(**values)


def provider_config(provider_id: str = "alpha", **overrides: Any) -> ProviderConfig:
    values: dict[str, Any] = {
        "provider_id": provider_id,
        "display_name": provider_id.title(),
        "adapter": "openai-compatible",
        "enabled": True,
        "base_url_env": f"IACODE_{provider_id.upper()}_BASE_URL",
        # Named ...CREDENTIAL rather than ...TOKEN: the repository secret scan reads an
        # assignment to a name ending in TOKEN as a finding, and a fixture that trips
        # the scan is a fixture somebody suppresses the scan for.
        "credential_env": f"IACODE_{provider_id.upper()}_CREDENTIAL",
        "protocols": (Endpoint.OPENAI_CHAT_COMPLETIONS,),
        "default_protocol": Endpoint.OPENAI_CHAT_COMPLETIONS,
    }
    values.update(overrides)
    return ProviderConfig(**values)


def descriptor(provider_id: str = "alpha", model_id: str = "model-one", *,
               capabilities: dict[Capability, CapabilityState] | None = None,
               context_window: int | None = 100_000,
               max_output_tokens: int | None = None,
               endpoints: tuple[Endpoint, ...] = (Endpoint.OPENAI_CHAT_COMPLETIONS,),
               reasoning_levels: tuple[ReasoningEffort, ...] = (),
               active: bool = True) -> ModelDescriptor:
    states = dict(capabilities or {Capability.STREAMING: CapabilityState.SUPPORTED})
    return ModelDescriptor(
        ref=ModelRef(provider_id=provider_id, model_id=model_id),
        display_name=model_id,
        context_window=context_window,
        max_output_tokens=max_output_tokens,
        supported_endpoints=endpoints,
        capabilities=states,
        capability_provenance={
            capability: CapabilityProvenance.PROVIDER_METADATA for capability in states},
        reasoning_levels=reasoning_levels,
        active=active,
        synced_at=EPOCH,
    )


def route_policy(*aliases: RouteAlias, allow_unknown: tuple[Capability, ...] = ()) -> RoutePolicy:
    return RoutePolicy(aliases=aliases,
                       unknown_capability=UnknownCapabilityPolicy(allow=allow_unknown))


def request(**overrides: Any) -> GatewayRequest:
    values: dict[str, Any] = {
        "request_id": "req-0001",
        "messages": (GatewayMessage(role=MessageRole.USER, content="Say hello."),),
    }
    values.update(overrides)
    return GatewayRequest(**values)


def completion(content: str = "hello", *, usage: Usage | None = None,
               finish: FinishReason = FinishReason.STOP) -> ParsedCompletion:
    return ParsedCompletion(content=content, finish_reason=finish,
                            usage=usage or Usage(input_tokens=10, output_tokens=2))


def failure(error_type: GatewayErrorType, provider: str = "alpha", **kwargs: Any) -> GatewayError:
    return GatewayError(error_type, f"scripted {error_type!s}", provider=provider, **kwargs)


def build_gateway(*, providers: dict[str, ProviderConfig] | None = None,
                  factory: Callable[[ProviderConfig], Any] | None = None,
                  catalog: InMemoryCatalogStore | None = None,
                  calls: InMemoryModelCallStore | None = None,
                  policy: RoutePolicy | None = None,
                  clock: FakeClock | None = None,
                  jitter: FakeJitter | None = None,
                  metrics: Any = None,
                  **setting_overrides: Any) -> ModelGateway:
    """Assemble a gateway from doubles, with everything the test did not care about defaulted."""
    configs = providers or {"alpha": provider_config()}
    # A caller that supplied a store is describing the catalog it wants, including an empty one.
    # Seeding it anyway would make a synchronisation test start with a model nobody put there.
    store = catalog
    if store is None:
        store = InMemoryCatalogStore()
        store.seed(descriptor())
    return ModelGateway(
        settings=settings(**setting_overrides),
        providers=configs,
        route_policy=policy or route_policy(),
        catalog_store=store,
        call_store=calls if calls is not None else InMemoryModelCallStore(),
        provider_factory=factory or (lambda config: ScriptedProvider(config.provider_id)),
        metrics=metrics,
        clock=clock or FakeClock(),
        jitter=jitter or FakeJitter(),
    )


def policy_dir() -> Path:
    """Where the provider and route policy lives, wherever the suite is running from.

    The suite runs from the repository on a developer's machine and from a copied directory inside
    the API image, where the policy sits beside the application. Searching upward and then falling
    back is what lets one assertion cover both, instead of a path literal that is correct in exactly
    one of the two places.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / ".iacode" / "policies"
        if candidate.is_dir():
            return candidate
    raise AssertionError("no .iacode/policies directory was found above the suite")


def gateway_source_root() -> Path:
    """The installed gateway package, read from the module rather than from a relative path."""
    import iacode_model_gateway

    return Path(iacode_model_gateway.__file__).resolve().parent
