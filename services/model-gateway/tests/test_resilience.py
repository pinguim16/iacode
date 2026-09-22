"""Retries, backoff, the circuit breaker and the request limits."""

from __future__ import annotations

import pytest
from fixtures.doubles import (
    FakeClock,
    FakeJitter,
    InMemoryCatalogStore,
    InMemoryModelCallStore,
    ScriptedProvider,
    build_gateway,
    completion,
    descriptor,
    failure,
    request as build_request,
    settings as build_settings,
)
from iacode_model_gateway.contracts import GatewayMessage, MessageRole, ToolDefinition
from iacode_model_gateway.errors import (
    FALLBACKABLE_ERRORS,
    RETRYABLE_ERRORS,
    GatewayError,
    GatewayErrorType,
)
from iacode_model_gateway.resilience.circuit import (
    CircuitBreaker,
    CircuitSettings,
    CircuitState,
    scope_keys,
)
from iacode_model_gateway.resilience.limits import (
    effective_output_tokens,
    enforce_limits,
    request_size_bytes,
)
from iacode_model_gateway.resilience.retry import RetryPolicy


class ErrorTaxonomyTests:
    """The vocabulary every adapter maps onto, and the two properties derived from it."""

    def test_every_class_the_gate_requires_exists(self) -> None:
        required = {
            "AUTHENTICATION_ERROR", "AUTHORIZATION_ERROR", "RATE_LIMITED", "MODEL_NOT_FOUND",
            "INVALID_REQUEST", "CONTEXT_LIMIT", "PROVIDER_UNAVAILABLE", "PROVIDER_TIMEOUT",
            "TRANSIENT_PROVIDER_ERROR", "PERMANENT_PROVIDER_ERROR", "CIRCUIT_OPEN", "CANCELLED",
            "INTERNAL_GATEWAY_ERROR",
        }

        assert required <= {str(item) for item in GatewayErrorType}

    def test_retryability_is_a_property_of_the_class(self) -> None:
        assert failure(GatewayErrorType.RATE_LIMITED).retryable
        assert failure(GatewayErrorType.PROVIDER_TIMEOUT).retryable
        assert not failure(GatewayErrorType.AUTHENTICATION_ERROR).retryable
        assert not failure(GatewayErrorType.INVALID_REQUEST).retryable
        assert not failure(GatewayErrorType.CONTEXT_LIMIT).retryable

    def test_fallback_is_wider_than_retry_and_not_universal(self) -> None:
        """A credential is per provider, so another provider may answer; a bad payload may not."""
        assert RETRYABLE_ERRORS < FALLBACKABLE_ERRORS
        assert GatewayErrorType.AUTHENTICATION_ERROR in FALLBACKABLE_ERRORS
        assert GatewayErrorType.INVALID_REQUEST not in FALLBACKABLE_ERRORS
        assert GatewayErrorType.CONTEXT_LIMIT not in FALLBACKABLE_ERRORS

    def test_a_classified_failure_carries_no_credential_shaped_field(self) -> None:
        payload = failure(GatewayErrorType.RATE_LIMITED, status_code=429).to_dict()

        assert set(payload) <= {"errorType", "message", "provider", "model", "statusCode",
                                "retryAfterSeconds", "details"}


class RetryClassificationTests:
    """Which failures are tried again, and which are not."""

    policy = RetryPolicy(max_attempts=3, initial_backoff_seconds=0.1, max_backoff_seconds=1.0,
                         max_retry_after_seconds=5.0)

    def test_rate_limiting_is_retried(self) -> None:
        decision = self.policy.decide(failure(GatewayErrorType.RATE_LIMITED), 1, FakeJitter())
        assert decision.retry

    def test_a_server_failure_is_retried(self) -> None:
        assert self.policy.decide(
            failure(GatewayErrorType.TRANSIENT_PROVIDER_ERROR), 1, FakeJitter()).retry

    def test_a_timeout_is_retried(self) -> None:
        assert self.policy.decide(
            failure(GatewayErrorType.PROVIDER_TIMEOUT), 1, FakeJitter()).retry

    def test_an_unreachable_provider_is_retried(self) -> None:
        assert self.policy.decide(
            failure(GatewayErrorType.PROVIDER_UNAVAILABLE), 1, FakeJitter()).retry

    def test_authentication_is_not_retried(self) -> None:
        decision = self.policy.decide(
            failure(GatewayErrorType.AUTHENTICATION_ERROR), 1, FakeJitter())

        assert not decision.retry
        assert "cannot be resolved" in decision.reason

    def test_an_invalid_request_is_not_retried(self) -> None:
        assert not self.policy.decide(
            failure(GatewayErrorType.INVALID_REQUEST), 1, FakeJitter()).retry

    def test_a_context_limit_is_not_retried(self) -> None:
        assert not self.policy.decide(
            failure(GatewayErrorType.CONTEXT_LIMIT), 1, FakeJitter()).retry

    def test_an_unknown_model_is_not_retried(self) -> None:
        assert not self.policy.decide(
            failure(GatewayErrorType.MODEL_NOT_FOUND), 1, FakeJitter()).retry

    def test_the_attempt_budget_is_a_bound(self) -> None:
        decision = self.policy.decide(failure(GatewayErrorType.RATE_LIMITED), 3, FakeJitter())

        assert not decision.retry
        assert "budget" in decision.reason


def test_retry_after_is_bounded() -> None:
    """A hint is honoured; an unreasonable one is refused rather than obeyed."""
    policy = RetryPolicy(max_attempts=10, max_retry_after_seconds=5.0)

    honoured = policy.decide(
        failure(GatewayErrorType.RATE_LIMITED, retry_after_seconds=2.0), 1, FakeJitter())
    assert honoured.retry
    assert honoured.delay_seconds == 2.0

    refused = policy.decide(
        failure(GatewayErrorType.RATE_LIMITED, retry_after_seconds=3600.0), 1, FakeJitter())
    assert not refused.retry
    assert "3600" in refused.reason


def test_backoff_is_exponential_with_jitter() -> None:
    """Full jitter: the delay is drawn from a growing range, capped."""
    # A budget wide enough that the exponent is what ends the series, not the attempt cap.
    policy = RetryPolicy(max_attempts=10, initial_backoff_seconds=0.5, max_backoff_seconds=2.0)
    jitter = FakeJitter(factor=1.0)

    delays = [policy.decide(failure(GatewayErrorType.RATE_LIMITED), attempt, jitter).delay_seconds
              for attempt in (1, 2, 3)]

    assert delays == [0.5, 1.0, 2.0]
    assert all(low == 0.0 for low, _high in jitter.ranges)
    assert policy.decide(
        failure(GatewayErrorType.RATE_LIMITED), 9, FakeJitter()).delay_seconds <= 2.0

    # The range is the same; the value drawn from it is not.
    low_jitter = FakeJitter(factor=0.0)
    assert policy.decide(
        failure(GatewayErrorType.RATE_LIMITED), 2, low_jitter).delay_seconds == 0.0


async def test_the_suite_controls_time_rather_than_waiting() -> None:
    clock = FakeClock()
    policy = RetryPolicy(max_attempts=10, initial_backoff_seconds=30.0,
                         max_backoff_seconds=30.0)
    decision = policy.decide(failure(GatewayErrorType.RATE_LIMITED), 1, FakeJitter())

    await policy.wait(decision, clock)

    assert clock.slept == [30.0]


class CircuitBreakerTests:
    """Closed, open, half-open, and the asymmetry between them."""

    def _breaker(self, clock: FakeClock, **overrides) -> CircuitBreaker:
        values = {"failure_threshold": 2, "cooldown_seconds": 10.0, "half_open_successes": 1}
        values.update(overrides)
        return CircuitBreaker(settings=CircuitSettings(**values), clock=clock)

    def test_it_starts_closed(self) -> None:
        breaker = self._breaker(FakeClock())

        assert breaker.state("provider:alpha") is CircuitState.CLOSED
        assert breaker.allow("provider:alpha")

    def test_the_threshold_opens_it(self) -> None:
        breaker = self._breaker(FakeClock())

        breaker.record_failure("provider:alpha")
        assert breaker.state("provider:alpha") is CircuitState.CLOSED
        breaker.record_failure("provider:alpha")

        assert breaker.state("provider:alpha") is CircuitState.OPEN

    def test_a_success_clears_the_run(self) -> None:
        """Scattered failures are normal; only a run of them is a signal."""
        breaker = self._breaker(FakeClock())

        breaker.record_failure("provider:alpha")
        breaker.record_success("provider:alpha")
        breaker.record_failure("provider:alpha")

        assert breaker.state("provider:alpha") is CircuitState.CLOSED

    def test_an_open_circuit_fails_fast(self) -> None:
        breaker = self._breaker(FakeClock())
        breaker.record_failure("provider:alpha")
        breaker.record_failure("provider:alpha")

        assert not breaker.allow("provider:alpha")

    def test_the_cooldown_moves_it_to_half_open(self) -> None:
        clock = FakeClock()
        breaker = self._breaker(clock)
        breaker.record_failure("provider:alpha")
        breaker.record_failure("provider:alpha")

        clock.advance(9.0)
        assert breaker.state("provider:alpha") is CircuitState.OPEN
        clock.advance(2.0)
        assert breaker.state("provider:alpha") is CircuitState.HALF_OPEN

    def test_half_open_admits_one_probe_at_a_time(self) -> None:
        clock = FakeClock()
        breaker = self._breaker(clock)
        breaker.record_failure("provider:alpha")
        breaker.record_failure("provider:alpha")
        clock.advance(11.0)

        assert breaker.allow("provider:alpha")
        assert not breaker.allow("provider:alpha")

    def test_a_successful_probe_closes_it(self) -> None:
        clock = FakeClock()
        breaker = self._breaker(clock)
        breaker.record_failure("provider:alpha")
        breaker.record_failure("provider:alpha")
        clock.advance(11.0)
        breaker.allow("provider:alpha")

        breaker.record_success("provider:alpha")

        assert breaker.state("provider:alpha") is CircuitState.CLOSED
        assert breaker.allow("provider:alpha")

    def test_a_failed_probe_reopens_and_restarts_the_cooldown(self) -> None:
        clock = FakeClock()
        breaker = self._breaker(clock)
        breaker.record_failure("provider:alpha")
        breaker.record_failure("provider:alpha")
        clock.advance(11.0)
        breaker.allow("provider:alpha")

        breaker.record_failure("provider:alpha")

        assert breaker.state("provider:alpha") is CircuitState.OPEN
        clock.advance(9.0)
        assert breaker.state("provider:alpha") is CircuitState.OPEN

    def test_the_scope_is_the_provider_and_the_pair(self) -> None:
        assert scope_keys("alpha", "model-one") == ("provider:alpha", "model:alpha:model-one")
        assert scope_keys("alpha", None) == ("provider:alpha",)

    def test_one_models_failures_do_not_close_another_models_circuit(self) -> None:
        breaker = self._breaker(FakeClock())

        breaker.record_failure("model:alpha:model-one")
        breaker.record_failure("model:alpha:model-one")

        assert breaker.state("model:alpha:model-one") is CircuitState.OPEN
        assert breaker.state("model:alpha:model-two") is CircuitState.CLOSED


async def test_an_open_circuit_produces_a_fallback_eligible_failure() -> None:
    """Fast failure is only useful if the router can act on it."""
    store = InMemoryCatalogStore()
    store.seed(descriptor(model_id="model-one"))
    provider = ScriptedProvider(
        "alpha", completions=[failure(GatewayErrorType.PROVIDER_UNAVAILABLE),
                              failure(GatewayErrorType.PROVIDER_UNAVAILABLE)])
    gateway = build_gateway(catalog=store, factory=lambda config: provider,
                            max_attempts=1, circuit_failure_threshold=2)

    for _ in range(2):
        with pytest.raises(GatewayError):
            await gateway.infer(build_request())

    with pytest.raises(GatewayError) as error:
        await gateway.infer(build_request())

    assert error.value.error_type is GatewayErrorType.CIRCUIT_OPEN
    assert error.value.fallbackable


async def test_our_own_mistake_does_not_open_a_circuit() -> None:
    """A malformed request says nothing about a provider's health."""
    store = InMemoryCatalogStore()
    store.seed(descriptor())
    provider = ScriptedProvider(
        "alpha", completions=[failure(GatewayErrorType.INVALID_REQUEST),
                              failure(GatewayErrorType.INVALID_REQUEST),
                              completion()])
    gateway = build_gateway(catalog=store, factory=lambda config: provider,
                            max_attempts=1, circuit_failure_threshold=2)

    for _ in range(2):
        with pytest.raises(GatewayError):
            await gateway.infer(build_request())

    answer = await gateway.infer(build_request())
    assert answer.content == "hello"


async def test_a_retry_happens_and_is_counted() -> None:
    store = InMemoryCatalogStore()
    store.seed(descriptor())
    calls = InMemoryModelCallStore()
    provider = ScriptedProvider(
        "alpha", completions=[failure(GatewayErrorType.RATE_LIMITED), completion()])
    clock = FakeClock()
    gateway = build_gateway(catalog=store, calls=calls, factory=lambda config: provider,
                            clock=clock, max_attempts=3)

    answer = await gateway.infer(build_request())

    assert answer.content == "hello"
    assert calls.calls[0].retry_count == 1
    assert clock.slept


class RequestLimitTests:
    """Guard rails against an accident, checked before anything leaves the process."""

    settings = build_settings(max_messages=2, max_tools=1, max_output_tokens=100,
                              max_request_bytes=1024)

    def test_too_many_messages_is_refused(self) -> None:
        request = build_request(messages=tuple(
            GatewayMessage(role=MessageRole.USER, content=str(index)) for index in range(3)))

        with pytest.raises(GatewayError) as error:
            enforce_limits(request, self.settings)
        assert error.value.details["limit"] == "messages"

    def test_too_many_tools_is_refused(self) -> None:
        request = build_request(tools=(ToolDefinition(name="a"), ToolDefinition(name="b")))

        with pytest.raises(GatewayError) as error:
            enforce_limits(request, self.settings)
        assert error.value.details["limit"] == "tools"

    def test_too_large_an_output_cap_is_refused(self) -> None:
        with pytest.raises(GatewayError) as error:
            enforce_limits(build_request(max_output_tokens=1000), self.settings)
        assert error.value.details["limit"] == "maxOutputTokens"

    def test_too_large_a_payload_is_refused(self) -> None:
        request = build_request(messages=(
            GatewayMessage(role=MessageRole.USER, content="x" * 4000),))

        with pytest.raises(GatewayError) as error:
            enforce_limits(request, self.settings)
        assert error.value.details["limit"] == "requestBytes"

    def test_size_is_measured_in_bytes_not_characters(self) -> None:
        latin = build_request(messages=(
            GatewayMessage(role=MessageRole.USER, content="a" * 10),))
        other = build_request(messages=(
            GatewayMessage(role=MessageRole.USER, content="ü" * 10),))

        assert request_size_bytes(other) > request_size_bytes(latin)

    def test_the_output_cap_is_the_smallest_of_the_three(self) -> None:
        settings = build_settings(max_output_tokens=100)

        assert effective_output_tokens(build_request(), settings, None) == 100
        assert effective_output_tokens(build_request(max_output_tokens=50), settings, None) == 50
        assert effective_output_tokens(build_request(), settings, 20) == 20
        assert effective_output_tokens(build_request(max_output_tokens=50), settings, 20) == 20

    def test_a_request_within_every_limit_passes(self) -> None:
        enforce_limits(build_request(), self.settings)
