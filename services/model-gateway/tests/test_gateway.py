"""The assembled gateway: fallback, persistence, cost, telemetry and the log contract."""

from __future__ import annotations

import json

import pytest
from fixtures.doubles import (
    FakeClock,
    InMemoryCatalogStore,
    InMemoryModelCallStore,
    ScriptedProvider,
    build_gateway,
    completion,
    descriptor,
    failure,
    provider_config,
    request as build_request,
    route_policy,
)
from iacode_model_gateway.config import RouteAlias
from iacode_model_gateway.contracts import (
    GatewayMessage,
    MessageRole,
    RouteReason,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.fingerprint import request_fingerprint
from iacode_model_gateway.pricing import ModelPricing, PricingTable, estimate_cost
from iacode_model_gateway.telemetry.logs import CONTRACT_FIELDS, call_fields
from iacode_model_gateway.telemetry.metrics import GatewayMetrics
from prometheus_client import CollectorRegistry, generate_latest


def _pair_store() -> InMemoryCatalogStore:
    store = InMemoryCatalogStore()
    store.seed(descriptor("alpha", "first"), descriptor("beta", "second"))
    return store


def _pair_gateway(first: ScriptedProvider, second: ScriptedProvider, **overrides):
    return build_gateway(
        providers={"alpha": provider_config("alpha"), "beta": provider_config("beta")},
        catalog=_pair_store(),
        factory=lambda config: first if config.provider_id == "alpha" else second,
        policy=route_policy(RouteAlias(alias="pair",
                                       candidates=("alpha:first", "beta:second"))),
        **overrides)


async def test_a_successful_call_returns_the_normalised_answer() -> None:
    provider = ScriptedProvider("alpha", completions=[completion()])
    gateway = build_gateway(factory=lambda config: provider)

    answer = await gateway.infer(build_request())

    assert answer.content == "hello"
    assert answer.ref.qualified == "alpha:model-one"
    assert answer.route.reason is RouteReason.DEFAULT_MODEL
    assert answer.latency_ms >= 0


async def test_fallback_chain_is_bounded_and_recorded() -> None:
    first = ScriptedProvider("alpha", completions=[failure(GatewayErrorType.PROVIDER_UNAVAILABLE)])
    second = ScriptedProvider("beta", completions=[completion("recovered")])
    gateway = _pair_gateway(first, second, max_attempts=1)

    answer = await gateway.infer(build_request(route="pair"))

    assert answer.content == "recovered"
    assert answer.route.reason is RouteReason.FALLBACK
    assert answer.route.fallback_count == 1
    assert [attempt.outcome for attempt in answer.route.chain] == ["FAILED", "SUCCEEDED"]


class FallbackSemanticsTests:
    """Which failures are worth another candidate, and which are the same failure twice."""

    async def test_provider_unavailability_falls_back(self) -> None:
        first = ScriptedProvider("alpha",
                                 completions=[failure(GatewayErrorType.PROVIDER_UNAVAILABLE)])
        second = ScriptedProvider("beta", completions=[completion("recovered")])

        answer = await _pair_gateway(first, second, max_attempts=1).infer(
            build_request(route="pair"))

        assert answer.content == "recovered"

    async def test_a_providers_authentication_failure_falls_back(self) -> None:
        """A credential is per provider; the second provider's key is a different fact."""
        first = ScriptedProvider("alpha",
                                 completions=[failure(GatewayErrorType.AUTHENTICATION_ERROR)])
        second = ScriptedProvider("beta", completions=[completion("recovered")])

        answer = await _pair_gateway(first, second, max_attempts=1).infer(
            build_request(route="pair"))

        assert answer.content == "recovered"

    async def test_an_invalid_request_does_not_fall_back(self) -> None:
        """The second model refuses it identically; the fallback only makes it slower."""
        first = ScriptedProvider("alpha", completions=[failure(GatewayErrorType.INVALID_REQUEST)])
        second = ScriptedProvider("beta", completions=[completion("never")])

        with pytest.raises(GatewayError) as error:
            await _pair_gateway(first, second, max_attempts=1).infer(build_request(route="pair"))

        assert error.value.error_type is GatewayErrorType.INVALID_REQUEST
        assert second.calls == []
        assert "fail identically" in error.value.details["fallbackStopped"]

    async def test_a_context_limit_does_not_fall_back(self) -> None:
        first = ScriptedProvider("alpha", completions=[failure(GatewayErrorType.CONTEXT_LIMIT)])
        second = ScriptedProvider("beta", completions=[completion("never")])

        with pytest.raises(GatewayError):
            await _pair_gateway(first, second, max_attempts=1).infer(build_request(route="pair"))

        assert second.calls == []

    async def test_exhausting_the_chain_reports_the_last_failure(self) -> None:
        first = ScriptedProvider("alpha", completions=[failure(GatewayErrorType.RATE_LIMITED)])
        second = ScriptedProvider("beta",
                                  completions=[failure(GatewayErrorType.PROVIDER_TIMEOUT)])

        with pytest.raises(GatewayError) as error:
            await _pair_gateway(first, second, max_attempts=1).infer(build_request(route="pair"))

        assert error.value.error_type is GatewayErrorType.PROVIDER_TIMEOUT
        assert "exhausted" in error.value.details["fallbackStopped"]
        assert len(error.value.details["chain"]) == 2

    async def test_the_same_candidate_is_never_tried_twice_as_a_fallback(self) -> None:
        store = InMemoryCatalogStore()
        store.seed(descriptor("alpha", "first"))
        provider = ScriptedProvider("alpha", completions=[
            failure(GatewayErrorType.PROVIDER_UNAVAILABLE)])
        gateway = build_gateway(
            catalog=store, factory=lambda config: provider, max_attempts=1,
            policy=route_policy(RouteAlias(
                alias="repeat", candidates=("alpha:first", "alpha:first", "alpha:first"))))

        with pytest.raises(GatewayError):
            await gateway.infer(build_request(route="repeat"))

        assert len(provider.calls) == 1


async def test_model_call_records_the_operational_metadata() -> None:
    calls = InMemoryModelCallStore()
    provider = ScriptedProvider("alpha", completions=[
        completion(usage=Usage(input_tokens=11, output_tokens=3, reasoning_tokens=2))])
    gateway = build_gateway(calls=calls, factory=lambda config: provider,
                            clock=FakeClock())

    await gateway.infer(build_request())

    record = calls.calls[0]
    assert record.provider_id == "alpha"
    assert record.model_id == "model-one"
    assert record.endpoint == "openai-chat-completions"
    assert record.status == "SUCCEEDED"
    assert record.succeeded
    assert record.input_tokens == 11
    assert record.reasoning_tokens == 2
    assert record.latency_ms is not None
    assert record.finished_at >= record.started_at
    assert record.request_fingerprint


async def test_a_failed_attempt_is_recorded_too() -> None:
    calls = InMemoryModelCallStore()
    provider = ScriptedProvider("alpha", completions=[failure(GatewayErrorType.RATE_LIMITED)])
    gateway = build_gateway(calls=calls, factory=lambda config: provider, max_attempts=1)

    with pytest.raises(GatewayError):
        await gateway.infer(build_request())

    assert calls.calls[0].status == "FAILED"
    assert calls.calls[0].error_type == "RATE_LIMITED"


async def test_a_storage_failure_does_not_fail_a_successful_call() -> None:
    """The answer is already correct; losing the record is the lesser failure."""
    calls = InMemoryModelCallStore(fail=True)
    provider = ScriptedProvider("alpha", completions=[completion()])
    gateway = build_gateway(calls=calls, factory=lambda config: provider)

    answer = await gateway.infer(build_request())

    assert answer.content == "hello"
    assert calls.calls == []


class PromptCaptureTests:
    """Content is not persisted by default, and the default is the shipped configuration."""

    async def test_prompt_is_not_persisted_by_default(self) -> None:
        calls = InMemoryModelCallStore()
        provider = ScriptedProvider("alpha", completions=[completion("a secret answer")])
        gateway = build_gateway(calls=calls, factory=lambda config: provider)

        await gateway.infer(build_request(messages=(
            GatewayMessage(role=MessageRole.USER, content="a confidential question"),)))

        rendered = json.dumps([record.__dict__ for record in calls.calls], default=str)
        assert "confidential question" not in rendered
        assert "secret answer" not in rendered

    def test_the_record_has_no_field_that_could_hold_content(self) -> None:
        from iacode_model_gateway.ports import ModelCallRecord

        fields = set(ModelCallRecord.__dataclass_fields__)
        assert not fields & {"prompt", "messages", "completion", "response", "content",
                             "reasoning"}

    def test_the_capture_setting_defaults_to_off(self) -> None:
        from iacode_model_gateway.config import GatewaySettings

        assert GatewaySettings().persist_prompts is False

    def test_no_reasoning_content_is_persisted(self) -> None:
        """Only the count the provider reported; a model's deliberation is not ours to keep."""
        from iacode_model_gateway.ports import ModelCallRecord

        annotations = ModelCallRecord.__dataclass_fields__
        assert annotations["reasoning_tokens"].type in ("int | None", int | None)
        assert "reasoning_content" not in annotations


def test_request_fingerprint_is_stable_and_carries_no_content() -> None:
    first = build_request(messages=(
        GatewayMessage(role=MessageRole.USER, content="a confidential question"),))
    same = build_request(request_id="different", messages=(
        GatewayMessage(role=MessageRole.USER, content="a confidential question"),))
    other = build_request(messages=(
        GatewayMessage(role=MessageRole.USER, content="a different question"),))

    digest = request_fingerprint(first)

    assert digest == request_fingerprint(same)
    assert digest != request_fingerprint(other)
    assert len(digest) == 64
    assert "confidential" not in digest


def test_the_fingerprint_ignores_how_the_answer_is_delivered() -> None:
    """Two calls that differ only in streaming asked the same question."""
    assert request_fingerprint(build_request()) == request_fingerprint(build_request(stream=True))


class UsageNormalisationTests:
    """What the provider reported, and nothing else."""

    async def test_reported_usage_reaches_the_answer(self) -> None:
        provider = ScriptedProvider("alpha", completions=[
            completion(usage=Usage(input_tokens=7, output_tokens=2, cached_input_tokens=1))])
        gateway = build_gateway(factory=lambda config: provider)

        answer = await gateway.infer(build_request())

        assert answer.usage.input_tokens == 7
        assert answer.usage.total_tokens == 9
        assert answer.usage.cached_input_tokens == 1

    async def test_absent_usage_is_absent_rather_than_zero(self) -> None:
        provider = ScriptedProvider("alpha", completions=[completion(usage=Usage())])
        gateway = build_gateway(factory=lambda config: provider)

        answer = await gateway.infer(build_request())

        assert answer.usage.empty
        assert answer.usage.input_tokens is None


def test_unknown_cost_is_absent_not_zero() -> None:
    """Zero means the call was free, which is a different claim and usually a wrong one."""
    usage = Usage(input_tokens=1000, output_tokens=500)

    assert estimate_cost(usage, None) is None
    assert estimate_cost(usage, ModelPricing()) is None
    assert estimate_cost(usage, ModelPricing(input_per_million=1.0)) is None
    assert estimate_cost(Usage(), ModelPricing(input_per_million=1.0,
                                               output_per_million=2.0)) is None


def test_a_configured_price_is_applied() -> None:
    usage = Usage(input_tokens=1_000_000, output_tokens=500_000)
    pricing = ModelPricing(input_per_million=2.0, output_per_million=6.0)

    assert estimate_cost(usage, pricing) == 5.0


def test_cached_input_is_not_billed_twice() -> None:
    usage = Usage(input_tokens=1_000_000, cached_input_tokens=500_000, output_tokens=0)
    pricing = ModelPricing(input_per_million=2.0, output_per_million=6.0,
                           cached_input_per_million=0.5)

    assert estimate_cost(usage, pricing) == 1.25


def test_the_pricing_table_ships_empty() -> None:
    """This project has agreed no price list with anyone."""
    assert len(PricingTable()) == 0
    assert PricingTable().for_model("alpha:model-one") is None


async def test_a_priced_model_records_its_cost() -> None:
    calls = InMemoryModelCallStore()
    provider = ScriptedProvider("alpha", completions=[
        completion(usage=Usage(input_tokens=1_000_000, output_tokens=0))])
    gateway = build_gateway(calls=calls, factory=lambda config: provider)
    gateway.pricing = PricingTable({"alpha:model-one": ModelPricing(input_per_million=3.0,
                                                                    output_per_million=1.0)})

    answer = await gateway.infer(build_request())

    assert answer.cost == 3.0
    assert calls.calls[0].cost == 3.0


class GatewayMetricsTests:
    """The instruments, and the labels they are allowed to carry."""

    def _metrics(self) -> tuple[GatewayMetrics, CollectorRegistry]:
        registry = CollectorRegistry()
        return GatewayMetrics(registry), registry

    def test_every_required_instrument_exists(self) -> None:
        metrics, registry = self._metrics()
        metrics.observe_request(provider="alpha", model="model-one",
                                endpoint="openai-chat-completions", route=None,
                                status="SUCCEEDED", seconds=0.2)
        metrics.observe_error(provider="alpha", error_type="RATE_LIMITED")
        metrics.observe_retry(provider="alpha", error_type="RATE_LIMITED")
        metrics.observe_fallback(provider="alpha", error_type="RATE_LIMITED")
        metrics.observe_circuit("provider:alpha", "OPEN")
        metrics.observe_provider_health("alpha", True)
        metrics.observe_catalog("alpha", active=3, inactive=1)

        rendered = generate_latest(registry).decode("utf-8")
        for name in ("iacode_gateway_requests_total", "iacode_gateway_request_duration_seconds",
                     "iacode_gateway_errors_total", "iacode_gateway_retries_total",
                     "iacode_gateway_fallbacks_total", "iacode_gateway_circuit_state",
                     "iacode_gateway_provider_health", "iacode_model_catalog_size"):
            assert name in rendered

    def test_metric_labels_are_bounded_and_carry_no_content(self) -> None:
        metrics, registry = self._metrics()
        metrics.observe_request(provider="alpha", model="model-one",
                                endpoint="openai-chat-completions", route=None,
                                status="SUCCEEDED", seconds=0.2)

        rendered = generate_latest(registry).decode("utf-8")

        assert 'route="none"' in rendered
        assert "Say hello" not in rendered
        for collector in (metrics.requests, metrics.duration, metrics.errors, metrics.retries,
                          metrics.fallbacks, metrics.circuit_state, metrics.provider_health,
                          metrics.catalog_size):
            assert not set(collector._labelnames) & {
                "prompt", "content", "request_id", "credential", "message"}

    def test_the_circuit_state_is_a_number_a_dashboard_can_alert_on(self) -> None:
        metrics, registry = self._metrics()

        metrics.observe_circuit("provider:alpha", "CLOSED")
        assert 'iacode_gateway_circuit_state{scope="provider:alpha",service="iacode-api"} 0.0' \
            in generate_latest(registry).decode("utf-8")

        metrics.observe_circuit("provider:alpha", "OPEN")
        assert 'iacode_gateway_circuit_state{scope="provider:alpha",service="iacode-api"} 2.0' \
            in generate_latest(registry).decode("utf-8")

    async def test_a_call_is_observed(self) -> None:
        registry = CollectorRegistry()
        metrics = GatewayMetrics(registry)
        provider = ScriptedProvider("alpha", completions=[completion()])
        gateway = build_gateway(factory=lambda config: provider, metrics=metrics)

        await gateway.infer(build_request())

        rendered = generate_latest(registry).decode("utf-8")
        assert 'status="SUCCEEDED"' in rendered
        assert 'model="model-one"' in rendered


def test_gateway_log_contract() -> None:
    """One field list, used by every call site, so a record is readable end to end."""
    fields = call_fields(request_id="req", provider="alpha", model="model-one",
                         endpoint="openai-chat-completions", route="fast", attempt=1,
                         fallback_index=0, latency_ms=12.5, status="SUCCEEDED",
                         error_type=None)

    assert set(fields) <= set(CONTRACT_FIELDS)
    assert "errorType" not in fields  # absent rather than null
    assert fields["fallbackIndex"] == 0  # zero is a position, not an absence
    assert call_fields() == {}
