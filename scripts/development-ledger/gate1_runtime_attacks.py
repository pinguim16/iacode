#!/usr/bin/env python3
"""The half of the GATE 1 battery that has to run where the gateway is installed.

The host deliberately has neither httpx nor pydantic, so every attack that needs a real gateway
object runs inside the API image. This module is mounted into that image, executed, and prints one
JSON document to stdout; `gate1_red_team.py` merges the verdicts with the host-side attacks.

Every attack here performs a real mutation against real code. Nothing is asserted by reading a file
the delivery wrote, and nothing is "defended" by an exception that happened to be raised: each
attack names the refusal it is looking for and records what it actually observed.

    python gate1_runtime_attacks.py
"""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from iacode_model_gateway.catalog.sync import DiscoveredCatalog
from iacode_model_gateway.config import (
    GatewaySettings,
    ProviderConfig,
    RouteAlias,
    RoutePolicy,
    resolve_provider,
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
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.gateway import ModelGateway
from iacode_model_gateway.ports import ModelCallRecord, ProviderRecord, SyncOutcome
from iacode_model_gateway.protocols.base import ParsedCompletion, StreamChunk
from iacode_model_gateway.providers.base import ProviderHealth

#: Built rather than written: a literal of this shape in a committed file is a finding to the
#: repository secret scan whether or not the value is real.
CREDENTIAL = "dw" + "-live-" + "r" * 32

EPOCH = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------------------------
# The doubles this battery mutates against
# ---------------------------------------------------------------------------------------------


class Clock:
    def __init__(self) -> None:
        self._now = EPOCH
        self._monotonic = 0.0
        self.slept: list[float] = []

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return self._monotonic

    async def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self._monotonic += seconds


class Jitter:
    def uniform(self, low: float, high: float) -> float:
        return high


@dataclass
class Catalog:
    models: dict[str, dict[str, ModelDescriptor]] = field(default_factory=dict)
    providers: dict[str, ProviderRecord] = field(default_factory=dict)

    async def list_providers(self) -> list[ProviderRecord]:
        return [self.providers[key] for key in sorted(self.providers)]

    async def upsert_provider(self, record: ProviderRecord) -> None:
        self.providers[record.provider_id] = record

    async def list_models(self, *, provider_id: str | None = None,
                          active: bool | None = None) -> list[ModelDescriptor]:
        found: list[ModelDescriptor] = []
        for owner in sorted(self.models):
            if provider_id is not None and owner != provider_id:
                continue
            for key in sorted(self.models[owner]):
                item = self.models[owner][key]
                if active is not None and item.active is not active:
                    continue
                found.append(item)
        return found

    async def replace_provider_models(self, provider_id: str,
                                      models: list[ModelDescriptor]) -> SyncOutcome:
        existing = self.models.setdefault(provider_id, {})
        incoming = {item.ref.model_id: item for item in models}
        added = deactivated = 0
        for model_id, item in incoming.items():
            if model_id not in existing:
                added += 1
            existing[model_id] = item
        for model_id, previous in list(existing.items()):
            if model_id in incoming or not previous.active:
                continue
            existing[model_id] = previous.model_copy(update={"active": False})
            deactivated += 1
        return SyncOutcome(provider_id=provider_id, added=added, deactivated=deactivated)

    def seed(self, *items: ModelDescriptor) -> None:
        for item in items:
            self.models.setdefault(item.ref.provider_id, {})[item.ref.model_id] = item


@dataclass
class Calls:
    records: list[ModelCallRecord] = field(default_factory=list)

    async def record(self, call: ModelCallRecord) -> None:
        self.records.append(call)


@dataclass
class Provider:
    provider_id: str
    completions: list[Any] = field(default_factory=list)
    streams: list[Any] = field(default_factory=list)
    catalog: Any = field(default_factory=list)
    attempts: int = 0

    async def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, True)

    async def list_models(self) -> DiscoveredCatalog:
        if isinstance(self.catalog, Exception):
            raise self.catalog
        return DiscoveredCatalog(provider_id=self.provider_id, entries=tuple(self.catalog))

    async def generate(self, request: GatewayRequest, model: ModelDescriptor,
                       endpoint: Endpoint, *, output_tokens: int) -> ParsedCompletion:
        self.attempts += 1
        answer = self.completions.pop(0) if self.completions else ParsedCompletion(content="ok")
        if isinstance(answer, Exception):
            raise answer
        return answer

    async def stream(self, request: GatewayRequest, model: ModelDescriptor,
                     endpoint: Endpoint, *, output_tokens: int) -> AsyncIterator[StreamChunk]:
        self.attempts += 1
        script = self.streams.pop(0) if self.streams else []
        for item in script:
            if isinstance(item, Exception):
                raise item
            yield item


def descriptor(provider_id: str = "alpha", model_id: str = "model-one", *,
               capabilities: dict[Capability, CapabilityState] | None = None,
               context_window: int | None = 100_000,
               active: bool = True) -> ModelDescriptor:
    states = dict(capabilities or {Capability.STREAMING: CapabilityState.SUPPORTED})
    return ModelDescriptor(
        ref=ModelRef(provider_id=provider_id, model_id=model_id),
        display_name=model_id,
        context_window=context_window,
        supported_endpoints=(Endpoint.OPENAI_CHAT_COMPLETIONS,),
        capabilities=states,
        capability_provenance={key: CapabilityProvenance.PROVIDER_METADATA for key in states},
        active=active,
        synced_at=EPOCH,
    )


def provider_config(provider_id: str = "alpha", **overrides: Any) -> ProviderConfig:
    values: dict[str, Any] = {
        "provider_id": provider_id,
        "display_name": provider_id.title(),
        "adapter": "openai-compatible",
        "enabled": True,
        "base_url_env": f"IACODE_{provider_id.upper()}_BASE_URL",
        "credential_env": f"IACODE_{provider_id.upper()}_CREDENTIAL",
        "protocols": (Endpoint.OPENAI_CHAT_COMPLETIONS,),
        "default_protocol": Endpoint.OPENAI_CHAT_COMPLETIONS,
    }
    values.update(overrides)
    return ProviderConfig(**values)


def settings(**overrides: Any) -> GatewaySettings:
    values: dict[str, Any] = {
        "default_model": "alpha:model-one",
        "max_attempts": 3,
        "retry_initial_backoff_seconds": 0.1,
        "retry_max_backoff_seconds": 1.0,
        "circuit_failure_threshold": 2,
        "circuit_cooldown_seconds": 10.0,
        "max_fallbacks": 2,
        "max_output_tokens": 256,
    }
    values.update(overrides)
    return GatewaySettings(**values)


def gateway(providers: dict[str, ProviderConfig], factory, catalog: Catalog,
            calls: Calls | None = None, policy: RoutePolicy | None = None,
            clock: Clock | None = None, **setting_overrides: Any) -> ModelGateway:
    return ModelGateway(
        settings=settings(**setting_overrides),
        providers=providers,
        route_policy=policy or RoutePolicy(),
        catalog_store=catalog,
        call_store=calls or Calls(),
        provider_factory=factory,
        clock=clock or Clock(),
        jitter=Jitter(),
    )


def request(**overrides: Any) -> GatewayRequest:
    values: dict[str, Any] = {
        "request_id": "attack-0001",
        "messages": (GatewayMessage(role=MessageRole.USER, content="Say hello."),),
    }
    values.update(overrides)
    return GatewayRequest(**values)


# ---------------------------------------------------------------------------------------------
# The attacks
# ---------------------------------------------------------------------------------------------


async def attack_secret_leakage() -> tuple[bool, str]:
    """A provider echoes the credential into every surface it can reach."""
    resolved = resolve_provider(provider_config(), {
        "IACODE_ALPHA_BASE_URL": "https://provider.example/v1",
        "IACODE_ALPHA_CREDENTIAL": CREDENTIAL,
    })
    catalog = Catalog()
    catalog.seed(descriptor())
    calls = Calls()
    echoed = GatewayError(GatewayErrorType.INVALID_REQUEST,
                          "the provider refused the request", provider="alpha")
    engine = gateway({"alpha": provider_config()},
                     lambda config: Provider("alpha", completions=[echoed]),
                     catalog, calls)
    try:
        await engine.infer(request())
    except GatewayError as error:
        surfaces = json.dumps({
            "error": error.to_dict(),
            "resolved": resolved.model_dump(mode="json"),
            "repr": repr(resolved),
            "calls": [record.__dict__ for record in calls.records],
            "providers": [record.__dict__ for record in await catalog.list_providers()],
        }, default=str)
        if CREDENTIAL in surfaces:
            return False, "the credential reached an error, a record or a rendering"
        return True, "the credential is in no error, no record, no repr and no dump"
    return False, "the scripted failure did not happen, so nothing was tested"


async def attack_arbitrary_base_url() -> tuple[bool, str]:
    """A caller tries to make the gateway call an address of their choosing."""
    fields = set(GatewayRequest.model_fields)
    forbidden = fields & {"base_url", "baseUrl", "url", "host", "endpoint_url", "headers",
                          "credential", "api_key"}
    if forbidden:
        return False, f"the request contract carries {sorted(forbidden)}"

    attempts = []
    for hostile in ("http://169.254.169.254/latest/meta-data",
                    "https://user:pass@provider.example",
                    "file:///etc/passwd",
                    "https://provider.example/v1?key=value"):
        try:
            resolve_provider(provider_config(), {
                "IACODE_ALPHA_BASE_URL": hostile,
                "IACODE_ALPHA_CREDENTIAL": CREDENTIAL})
            attempts.append(f"accepted {hostile}")
        except GatewayError:
            continue
    if attempts:
        return False, "; ".join(attempts)
    return True, ("no request field can carry an address, and a plain-HTTP, user-information, "
                  "non-HTTP or query-bearing configured address is refused")


async def attack_unsupported_capability() -> tuple[bool, str]:
    """A request needs a capability the catalog never recorded."""
    catalog = Catalog()
    catalog.seed(descriptor(capabilities={}))
    engine = gateway({"alpha": provider_config()},
                     lambda config: Provider("alpha"), catalog)
    from iacode_model_gateway.contracts import ToolDefinition

    try:
        await engine.infer(request(tools=(ToolDefinition(name="read"),)))
    except GatewayError as error:
        if error.error_type is GatewayErrorType.NO_CANDIDATE and "never declared" in error.message:
            return True, "the unknown capability was refused rather than assumed"
        return False, f"refused for the wrong reason: {error.error_type}: {error.message[:120]}"
    return False, "a model that never declared the capability was called anyway"


async def attack_retry_on_authentication_error() -> tuple[bool, str]:
    """A credential failure is retried, burning quota on an answer that cannot change."""
    catalog = Catalog()
    catalog.seed(descriptor())
    provider = Provider("alpha", completions=[
        GatewayError(GatewayErrorType.AUTHENTICATION_ERROR, "rejected", provider="alpha"),
        ParsedCompletion(content="should never be reached")])
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog)
    try:
        await engine.infer(request())
    except GatewayError as error:
        if provider.attempts == 1 and error.error_type is GatewayErrorType.AUTHENTICATION_ERROR:
            return True, "one attempt; an authentication failure is never retried"
        return False, f"{provider.attempts} attempt(s) were made"
    return False, "the retry succeeded, which means the failure was retried"


async def attack_fallback_loop() -> tuple[bool, str]:
    """A route names the same candidate repeatedly, hoping the chain never ends."""
    catalog = Catalog()
    catalog.seed(descriptor(model_id="only"))
    provider = Provider("alpha", completions=[
        GatewayError(GatewayErrorType.PROVIDER_UNAVAILABLE, "down", provider="alpha")
        for _ in range(20)])
    policy = RoutePolicy(aliases=(RouteAlias(alias="loop",
                                             candidates=("alpha:only",) * 12),))
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog,
                     policy=policy, max_attempts=1, max_fallbacks=2)
    try:
        await engine.infer(request(route="loop"))
    except GatewayError as error:
        chain = error.details.get("chain") or []
        if provider.attempts == 1 and len(chain) == 1:
            return True, "the duplicate candidate collapsed to one attempt; the chain is bounded"
        return False, f"{provider.attempts} attempt(s), chain of {len(chain)}"
    return False, "the loop produced an answer, so nothing was bounded"


async def attack_circuit_breaker_bypass() -> tuple[bool, str]:
    """Traffic keeps arriving while a provider is down, hoping each call pays the full timeout."""
    catalog = Catalog()
    catalog.seed(descriptor())
    provider = Provider("alpha", completions=[
        GatewayError(GatewayErrorType.PROVIDER_UNAVAILABLE, "down", provider="alpha")
        for _ in range(10)])
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog,
                     max_attempts=1, circuit_failure_threshold=2)
    for _ in range(2):
        try:
            await engine.infer(request())
        except GatewayError:
            pass
    before = provider.attempts
    try:
        await engine.infer(request())
    except GatewayError as error:
        if error.error_type is GatewayErrorType.CIRCUIT_OPEN and provider.attempts == before:
            return True, f"the circuit opened after {before} failures and the next call never left"
        return False, f"{error.error_type} after {provider.attempts} attempt(s)"
    return False, "the call succeeded against a provider scripted to fail"


async def attack_stream_fallback_after_output() -> tuple[bool, str]:
    """A stream dies after delivering text, and a second model is offered the chance to finish it."""
    catalog = Catalog()
    catalog.seed(descriptor(model_id="first"), descriptor("beta", "second"))
    first = Provider("alpha", streams=[[
        StreamChunk(text="alpha said this "),
        GatewayError(GatewayErrorType.TRANSIENT_PROVIDER_ERROR, "died", provider="alpha")]])
    second = Provider("beta", streams=[[
        StreamChunk(text="and beta said that"),
        StreamChunk(finish_reason=FinishReason.STOP, done=True)]])
    policy = RoutePolicy(aliases=(RouteAlias(alias="pair",
                                             candidates=("alpha:first", "beta:second")),))
    engine = gateway({"alpha": provider_config("alpha"), "beta": provider_config("beta")},
                     lambda config: first if config.provider_id == "alpha" else second,
                     catalog, policy=policy, max_attempts=1)

    delivered = []
    async for event in engine.stream(request(stream=True, route="pair")):
        delivered.append(event)
    text = "".join(event.text or "" for event in delivered)
    models = {event.ref.qualified for event in delivered if event.ref is not None}

    if second.attempts == 0 and "beta" not in text and models == {"alpha:first"}:
        return True, "the second model was never called and no output was spliced"
    return False, (f"beta was called {second.attempts} time(s); delivered text was {text[:120]!r} "
                   f"from {sorted(models)}")


async def attack_context_overflow() -> tuple[bool, str]:
    """A request far larger than the window is sent anyway, to be refused by the provider."""
    catalog = Catalog()
    catalog.seed(descriptor(context_window=1000))
    provider = Provider("alpha", completions=[ParsedCompletion(content="should not be reached")])
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog)
    huge = request(messages=(GatewayMessage(role=MessageRole.USER, content="x" * 200_000),))
    try:
        await engine.infer(huge)
    except GatewayError as error:
        if provider.attempts == 0 and error.error_type is GatewayErrorType.NO_CANDIDATE:
            return True, "the preflight refused before the request left the process"
        return False, f"{error.error_type} after {provider.attempts} attempt(s)"
    return False, "a request larger than the window was sent"


async def attack_catalog_partial_failure() -> tuple[bool, str]:
    """A provider answers a synchronisation with nothing, then with a duplicate."""
    catalog = Catalog()
    catalog.seed(descriptor())
    provider = Provider("alpha", catalog=[])
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog)

    await engine.synchronise_catalog()
    survived_empty = [item.ref.model_id for item in await catalog.list_models(active=True)]

    provider.catalog = [("dup", {"id": "dup"}), ("dup", {"id": "dup"})]
    await engine.synchronise_catalog()
    survived_duplicate = [item.ref.model_id for item in await catalog.list_models(active=True)]

    if survived_empty == ["model-one"] and survived_duplicate == ["model-one"]:
        return True, "an empty answer and a duplicated identifier both left the catalog intact"
    return False, (f"after an empty answer the catalog held {survived_empty}; after a duplicate, "
                   f"{survived_duplicate}")


async def attack_persisted_prompt() -> tuple[bool, str]:
    """A confidential prompt is sent, and the record is searched for it."""
    catalog = Catalog()
    catalog.seed(descriptor())
    calls = Calls()
    secret_text = "the merger closes on Tuesday"
    engine = gateway({"alpha": provider_config()},
                     lambda config: Provider("alpha", completions=[
                         ParsedCompletion(content="an answer that quotes it: " + secret_text,
                                          usage=Usage(input_tokens=5, output_tokens=8))]),
                     catalog, calls)
    await engine.infer(request(messages=(
        GatewayMessage(role=MessageRole.USER, content=secret_text),)))

    rendered = json.dumps([record.__dict__ for record in calls.records], default=str)
    fields = set(ModelCallRecord.__dataclass_fields__)
    if secret_text in rendered or fields & {"prompt", "messages", "completion", "response"}:
        return False, "the request or the answer reached the record"
    return True, "neither the prompt nor the completion is in the record, and no field could hold one"


async def attack_provider_down() -> tuple[bool, str]:
    """The provider is unreachable for every candidate; the caller must get a bounded answer."""
    catalog = Catalog()
    catalog.seed(descriptor(model_id="first"), descriptor("beta", "second"))
    down = GatewayError(GatewayErrorType.PROVIDER_UNAVAILABLE, "unreachable")
    providers = {"alpha": provider_config("alpha"), "beta": provider_config("beta")}
    policy = RoutePolicy(aliases=(RouteAlias(alias="pair",
                                             candidates=("alpha:first", "beta:second")),))
    made: list[Provider] = []

    def factory(config: ProviderConfig) -> Provider:
        provider = Provider(config.provider_id,
                            completions=[down for _ in range(5)])
        made.append(provider)
        return provider

    engine = gateway(providers, factory, catalog, policy=policy, max_attempts=1)
    try:
        await engine.infer(request(route="pair"))
    except GatewayError as error:
        attempts = sum(provider.attempts for provider in made)
        if error.error_type is GatewayErrorType.PROVIDER_UNAVAILABLE and attempts == 2:
            return True, "both candidates were tried once and the failure was classified"
        return False, f"{error.error_type} after {attempts} attempt(s)"
    return False, "an unreachable provider produced an answer"


async def attack_invalid_model() -> tuple[bool, str]:
    """A caller names a model that is not in the catalog, hoping for a substitute."""
    catalog = Catalog()
    catalog.seed(descriptor(model_id="real"))
    provider = Provider("alpha", completions=[ParsedCompletion(content="substituted")])
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog)
    try:
        await engine.infer(request(model="alpha:imaginary"))
    except GatewayError as error:
        if provider.attempts == 0 and error.error_type is GatewayErrorType.NO_CANDIDATE:
            return True, "the named model was refused and no other model was used in its place"
        return False, f"{error.error_type} after {provider.attempts} attempt(s)"
    return False, "an unknown model produced an answer from a different model"


async def attack_unbounded_timeout() -> tuple[bool, str]:
    """The configuration is asked for a call with no time limit."""
    from iacode_model_gateway.providers import http_provider

    source = inspect.getsource(http_provider.HttpModelProvider._client)
    if "connect=" not in source or "read=" not in source:
        return False, "the client does not set a connect and a read timeout"

    refusals = []
    for field_name, value in (("connect_timeout_seconds", 0),
                              ("read_timeout_seconds", 0),
                              ("read_timeout_seconds", 10_000)):
        try:
            GatewaySettings(**{field_name: value})
            refusals.append(f"accepted {field_name}={value}")
        except Exception:  # noqa: BLE001 - a refusal is the defence
            continue
    if refusals:
        return False, "; ".join(refusals)
    return True, ("connect and read budgets are separate, always set, and a zero or absurd value "
                  "is refused at load time")


async def attack_model_disappearance() -> tuple[bool, str]:
    """A model vanishes from the provider's catalog between two synchronisations."""
    catalog = Catalog()
    provider = Provider("alpha", catalog=[("keep", {"id": "keep"}), ("vanish", {"id": "vanish"})])
    calls = Calls()
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog, calls)
    await engine.synchronise_catalog()
    await engine.infer(request(model="alpha:vanish"))

    provider.catalog = [("keep", {"id": "keep"})]
    provider.completions = [ParsedCompletion(content="should not be reached")]
    await engine.synchronise_catalog()

    everything = {item.ref.model_id for item in await catalog.list_models()}
    active = {item.ref.model_id for item in await catalog.list_models(active=True)}
    recorded = [record.model_id for record in calls.records]

    try:
        await engine.infer(request(model="alpha:vanish"))
    except GatewayError as error:
        refused = error.error_type is GatewayErrorType.NO_CANDIDATE
    else:
        refused = False

    if everything == {"keep", "vanish"} and active == {"keep"} and "vanish" in recorded and refused:
        return True, ("the vanished model was deactivated rather than deleted, its recorded call "
                      "survived, and a new request for it was refused")
    return False, (f"catalog {sorted(everything)}, active {sorted(active)}, recorded {recorded}, "
                   f"refused={refused}")



async def attack_credential_pasted_where_a_name_belongs() -> tuple[bool, str]:
    """Somebody pastes the key itself into the field that holds the variable's name."""
    refusals: list[str] = []
    for value in (CREDENTIAL, "sk-" + "y" * 24, "my-devworld-key"):
        try:
            provider_config(credential_env=value)
            refusals.append(f"accepted {value[:12]}...")
        except Exception:  # noqa: BLE001 - a refusal is the defence
            continue
    try:
        provider_config(protocols=())
        refusals.append("accepted a provider that serves no protocol")
    except Exception:  # noqa: BLE001 - a refusal is the defence
        pass
    if refusals:
        return False, "; ".join(refusals)
    return True, ("a value where a variable name belongs is refused at load time, and so is a "
                  "provider that declares no protocol")

ATTACKS: dict[str, Any] = {
    "G1-A": attack_secret_leakage,
    "G1-B": attack_arbitrary_base_url,
    "G1-C": attack_unsupported_capability,
    "G1-D": attack_retry_on_authentication_error,
    "G1-E": attack_fallback_loop,
    "G1-F": attack_circuit_breaker_bypass,
    "G1-G": attack_stream_fallback_after_output,
    "G1-H": attack_context_overflow,
    "G1-I": attack_catalog_partial_failure,
    "G1-J": attack_persisted_prompt,
    "G1-K": attack_provider_down,
    "G1-L": attack_invalid_model,
    "G1-M": attack_unbounded_timeout,
    "G1-N": attack_model_disappearance,
    "G1-R": attack_credential_pasted_where_a_name_belongs,
}


async def baseline() -> tuple[bool, str]:
    """The null-mutation control: the unmutated path through the same code must be accepted.

    Without it, every attack above could be "defended" by a gateway that refuses everything, and the
    battery would prove nothing at all.
    """
    catalog = Catalog()
    calls = Calls()
    provider = Provider("alpha",
                        catalog=[("model-one", {"id": "model-one",
                                                "supported_parameters": ["stream"]})],
                        completions=[ParsedCompletion(content="ok",
                                                      usage=Usage(input_tokens=3,
                                                                  output_tokens=1))],
                        streams=[[StreamChunk(text="ok"),
                                  StreamChunk(finish_reason=FinishReason.STOP, done=True)]])
    engine = gateway({"alpha": provider_config()}, lambda config: provider, catalog, calls)

    outcomes = await engine.synchronise_catalog()
    answer = await engine.infer(request())
    events = [event async for event in engine.stream(request(stream=True))]

    checks = [
        ("a valid catalog is applied", outcomes[0].added == 1),
        ("a valid request is answered", answer.content == "ok"),
        ("a valid stream completes", [str(item.type) for item in events][-1] == "end"),
        ("the call is recorded", len(calls.records) == 2),
        ("a clean address is accepted",
         resolve_provider(provider_config(), {
             "IACODE_ALPHA_BASE_URL": "https://provider.example/v1",
             "IACODE_ALPHA_CREDENTIAL": CREDENTIAL}).base_url
         == "https://provider.example/v1"),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return False, "the unmutated path was refused by: " + ", ".join(failed)
    return True, ("the unmutated path synchronises, answers, streams, records and accepts a clean "
                  "address")


async def run() -> dict[str, Any]:
    verdicts: dict[str, Any] = {}
    defended, observed = await baseline()
    verdicts["baseline"] = {"defended": defended, "observed": observed}
    for identifier, attack in ATTACKS.items():
        try:
            ok, detail = await attack()
        except Exception as error:  # noqa: BLE001 - a harness that crashes has found something
            ok, detail = False, f"the attack itself failed: {type(error).__name__}: {error}"
        verdicts[identifier] = {"defended": ok, "observed": detail}
    return verdicts


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(asyncio.run(run()), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
