"""The gateway itself: one entry point for every model invocation.

Everything else in this package is a part; this is the assembly. It owns the sequence that turns a
request into an answer — limits, routing, circuit, attempt, retry, fallback, normalization,
persistence, telemetry — and it owns it **once**, so the streaming path and the non-streaming path
cannot drift apart. `docs/GATE-1-CHECKLIST.md` row 9.1 forbids a second architecture for streaming,
and the way to satisfy it is not discipline but structure: both paths call the same router, the same
circuit, the same retry policy, the same provider objects and the same recorder.

The one place they differ is the rule that makes streaming safe, and it is a rule about time rather
than about code:

    Automatic fallback and retry are permitted **until the first event reaches the consumer**, and
    never after.

Before the first event, a failure is invisible to the caller and another candidate — or another
attempt — can answer as though nothing happened. After it, the caller already holds output from one
model, and continuing with a second would splice two models' prose into one answer that reads as
though one model wrote it. Nobody downstream could detect that, which is exactly why it must be
impossible. After the first event, a failure is propagated as an error event carrying what the
caller already received.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Callable
from contextlib import aclosing
from dataclasses import dataclass, field, replace
from datetime import datetime

from iacode_common.redaction import redact_text
from iacode_telemetry.logging import get_logger

from iacode_model_gateway.catalog.sync import CatalogSynchroniser
from iacode_model_gateway.config import (
    GatewaySettings,
    ProviderConfig,
    RoutePolicy,
    resolve_provider,
)
from iacode_model_gateway.contracts import (
    Endpoint,
    FinishReason,
    GatewayRequest,
    GatewayResponse,
    ModelDescriptor,
    RouteAttempt,
    RouteDecision,
    RouteReason,
    StreamEvent,
    StreamEventType,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.fingerprint import request_fingerprint
from iacode_model_gateway.ports import (
    CatalogStore,
    Clock,
    Jitter,
    ModelCallRecord,
    ModelCallStore,
    ProviderRecord,
    RealClock,
    RealJitter,
    SyncOutcome,
)
from iacode_model_gateway.pricing import PricingTable, estimate_cost
from iacode_model_gateway.protocols import select_endpoint
from iacode_model_gateway.protocols.base import ParsedCompletion
from iacode_model_gateway.providers.base import ModelProvider, ProviderHealth
from iacode_model_gateway.resilience.circuit import CircuitBreaker, CircuitSettings, scope_keys
from iacode_model_gateway.resilience.limits import effective_output_tokens, enforce_limits
from iacode_model_gateway.resilience.retry import RetryPolicy
from iacode_model_gateway.routing.policy import may_fall_back
from iacode_model_gateway.routing.router import Candidate, RoutePlan, Router
from iacode_model_gateway.telemetry.logs import call_fields
from iacode_model_gateway.telemetry.metrics import GatewayMetrics

__all__ = ["ModelGateway", "ProviderFactory", "default_provider_factory"]

logger = get_logger(__name__)

#: Builds a provider object from its configuration. Injected so the suite can supply a deterministic
#: double without the gateway knowing that such a thing exists.
ProviderFactory = Callable[[ProviderConfig], ModelProvider]

#: Failures that say nothing about a provider's health, so they never open a circuit. A request we
#: malformed, a prompt too long, or a model that does not exist is our problem or the caller's;
#: counting it would take a working provider out of service because of our own bug.
_NOT_THE_PROVIDERS_FAULT = frozenset({
    GatewayErrorType.INVALID_REQUEST,
    GatewayErrorType.CONTEXT_LIMIT,
    GatewayErrorType.MODEL_NOT_FOUND,
    GatewayErrorType.INTERNAL_GATEWAY_ERROR,
})


@dataclass
class _Attempt:
    """What one candidate produced, whether or not it worked."""

    started_at: datetime
    finished_at: datetime
    latency_ms: float
    retries: int = 0
    error: GatewayError | None = None
    completion: ParsedCompletion | None = None
    usage: Usage = field(default_factory=Usage)


@dataclass
class ModelGateway:
    """The provider-neutral boundary for model invocation."""

    settings: GatewaySettings
    providers: dict[str, ProviderConfig]
    route_policy: RoutePolicy
    catalog_store: CatalogStore
    call_store: ModelCallStore
    provider_factory: ProviderFactory
    metrics: GatewayMetrics | None = None
    pricing: PricingTable = field(default_factory=PricingTable)
    clock: Clock = field(default_factory=RealClock)
    jitter: Jitter = field(default_factory=RealJitter)
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        self._router = Router(self.route_policy, self.settings)
        self._retry = RetryPolicy(
            max_attempts=self.settings.max_attempts,
            initial_backoff_seconds=self.settings.retry_initial_backoff_seconds,
            max_backoff_seconds=self.settings.retry_max_backoff_seconds,
            max_retry_after_seconds=self.settings.retry_max_retry_after_seconds,
        )
        self._circuit = CircuitBreaker(
            settings=CircuitSettings(
                failure_threshold=self.settings.circuit_failure_threshold,
                cooldown_seconds=self.settings.circuit_cooldown_seconds,
                half_open_successes=self.settings.circuit_half_open_successes,
            ),
            clock=self.clock,
        )
        self._synchroniser = CatalogSynchroniser(self.catalog_store, self.clock)

    # -- catalog and health ---------------------------------------------------------------------

    async def synchronise_catalog(self, provider_id: str | None = None) -> list[SyncOutcome]:
        """Refresh the catalog from the providers' own discovery endpoints.

        A provider that fails is recorded as failed and the others still run: one unreachable
        provider must not stop the rest of the catalog being refreshed.
        """
        outcomes: list[SyncOutcome] = []
        for config in self._selected(provider_id):
            try:
                provider = self.provider_factory(config)
                discovered = await provider.list_models()
                outcome = await self._synchroniser.apply(
                    discovered, display_name=config.display_name, adapter=config.adapter,
                    enabled=config.enabled,
                    provider_capabilities=config.capabilities,
                    provider_endpoints=config.protocols,
                    provider_reasoning_levels=config.reasoning_levels)
            except GatewayError as error:
                await self._synchroniser.record_failure(
                    config.provider_id, display_name=config.display_name, adapter=config.adapter,
                    enabled=config.enabled, detail=error.message)
                outcomes.append(SyncOutcome(provider_id=config.provider_id,
                                            errors=(error.message,)))
                self._metric_error(config.provider_id, error)
                logger.warning("catalog synchronisation failed", extra=call_fields(
                    provider=config.provider_id, status="FAILED",
                    error_type=str(error.error_type)))
                continue
            outcomes.append(outcome)
            await self._publish_catalog_size(config.provider_id)
            logger.info("catalog synchronised", extra=call_fields(
                provider=config.provider_id, status="SUCCEEDED"))
        return outcomes

    async def provider_health(self, provider_id: str | None = None) -> list[ProviderHealth]:
        """Probe every selected provider, without letting one failure hide the others.

        A provider with no credential configured is reported as unreachable with that as the
        reason rather than raising: "not configured here" is an operational state the page exists
        to show, not an exception.
        """
        results: list[ProviderHealth] = []
        for config in self._selected(provider_id):
            try:
                provider = self.provider_factory(config)
                health = await provider.health()
            except GatewayError as error:
                health = ProviderHealth(config.provider_id, False, error.message)
            results.append(health)
            self._metric_health(config.provider_id, health.reachable)
            models = await self.catalog_store.list_models(provider_id=config.provider_id)
            await self.catalog_store.upsert_provider(ProviderRecord(
                provider_id=config.provider_id,
                display_name=config.display_name,
                adapter=config.adapter,
                enabled=config.enabled,
                healthy=health.reachable,
                last_health_check=self.clock.now(),
                last_sync=None,
                model_count=len(models),
                detail=health.detail,
            ))
        return results

    def circuit_snapshot(self) -> dict[str, str]:
        """Every circuit scope and its state, for the health endpoint and the metrics."""
        snapshot = {key: str(state) for key, state in self._circuit.snapshot().items()}
        if self.metrics is not None:
            for scope, state in snapshot.items():
                self.metrics.observe_circuit(scope, state)
        return snapshot

    # -- inference ------------------------------------------------------------------------------

    async def infer(self, request: GatewayRequest) -> GatewayResponse:
        """Answer a request in one response, with bounded retries and bounded fallback."""
        enforce_limits(request, self.settings)
        plan = await self._plan(request)
        fingerprint = request_fingerprint(request)
        started = time.perf_counter()

        chain: list[RouteAttempt] = []
        last_error: GatewayError | None = None

        for index, candidate in enumerate(plan.candidates):
            remaining = len(plan.candidates) - index - 1
            endpoint = self._endpoint_for(candidate, chain, index)
            if endpoint is None:
                continue
            blocked = self._circuit_block(candidate, chain, index, endpoint)
            if blocked is not None:
                last_error = blocked
                if not may_fall_back(blocked, remaining)[0]:
                    raise self._with_route(blocked, plan, chain, "the circuit is open")
                self._metric_fallback(candidate.provider.provider_id, blocked)
                continue

            attempt = await self._call(request, candidate, endpoint, plan.output_tokens)
            chain.append(self._attempt_record(candidate, endpoint, index, attempt))
            await self._record(request, candidate, endpoint, plan, attempt, fingerprint, index)
            self._metric_request(candidate, endpoint, plan,
                                 "SUCCEEDED" if attempt.error is None else "FAILED",
                                 time.perf_counter() - started)

            if attempt.error is None and attempt.completion is not None:
                completion = attempt.completion
                return GatewayResponse(
                    request_id=request.request_id,
                    ref=candidate.ref,
                    endpoint=endpoint,
                    content=completion.content,
                    tool_calls=completion.tool_calls,
                    finish_reason=completion.finish_reason,
                    usage=attempt.usage,
                    latency_ms=round((time.perf_counter() - started) * 1000, 2),
                    route=self._decision(plan, chain),
                    cost=estimate_cost(attempt.usage,
                                       self.pricing.for_model(candidate.ref.qualified)),
                )

            error = attempt.error or GatewayError(
                GatewayErrorType.INTERNAL_GATEWAY_ERROR,
                "the provider returned neither an answer nor a failure",
                provider=candidate.provider.provider_id, model=candidate.ref.model_id)
            last_error = error
            self._metric_error(candidate.provider.provider_id, error)

            allowed, why = may_fall_back(error, remaining)
            if not allowed:
                raise self._with_route(error, plan, chain, why)
            self._metric_fallback(candidate.provider.provider_id, error)

        raise self._exhausted(last_error, plan, chain)

    # -- streaming ------------------------------------------------------------------------------

    async def stream(self, request: GatewayRequest) -> AsyncIterator[StreamEvent]:
        """Answer a request incrementally.

        ``delivered`` is the whole of row 9.3: once one event has left this generator, neither a
        retry nor a fallback may produce another. A counter rather than a convention, so a later
        edit cannot forget it.
        """
        enforce_limits(request, self.settings)
        plan = await self._plan(request)
        fingerprint = request_fingerprint(request)
        started = time.perf_counter()

        chain: list[RouteAttempt] = []
        sequence = 0
        delivered = 0
        last_error: GatewayError | None = None

        for index, candidate in enumerate(plan.candidates):
            remaining = len(plan.candidates) - index - 1
            endpoint = self._endpoint_for(candidate, chain, index)
            if endpoint is None:
                continue
            blocked = self._circuit_block(candidate, chain, index, endpoint)
            if blocked is not None:
                last_error = blocked
                if not may_fall_back(blocked, remaining)[0]:
                    raise self._with_route(blocked, plan, chain, "the circuit is open")
                self._metric_fallback(candidate.provider.provider_id, blocked)
                continue

            provider = self.provider_factory(candidate.provider)
            attempt_number = 1
            retries = 0

            while True:
                started_at = self.clock.now()
                attempt_clock = time.perf_counter()
                received = 0
                usage = Usage()
                finish = FinishReason.UNKNOWN
                error: GatewayError | None = None

                try:
                    # ``aclosing`` rather than a bare ``async for``: when the consumer stops
                    # reading, this generator is closed, and without it the upstream generator
                    # would only be finalised whenever the event loop got round to it. The
                    # difference is whether the provider stops generating tokens now or in a
                    # while, and tokens cost money.
                    upstream = provider.stream(
                        request, candidate.model, endpoint, output_tokens=plan.output_tokens)
                    async with aclosing(upstream) as chunks:
                        async for chunk in chunks:
                            if received == 0:
                                yield StreamEvent(
                                    type=StreamEventType.START, request_id=request.request_id,
                                    sequence=sequence, ref=candidate.ref, endpoint=endpoint,
                                    route=self._decision(plan, chain))
                                sequence += 1
                                delivered += 1
                            received += 1
                            if chunk.text:
                                yield StreamEvent(
                                    type=StreamEventType.TEXT_DELTA,
                                    request_id=request.request_id, sequence=sequence,
                                    text=chunk.text)
                                sequence += 1
                                delivered += 1
                            if chunk.tool_call_delta is not None:
                                yield StreamEvent(
                                    type=StreamEventType.TOOL_CALL_DELTA,
                                    request_id=request.request_id, sequence=sequence,
                                    tool_call_delta=chunk.tool_call_delta)
                                sequence += 1
                                delivered += 1
                            if chunk.usage is not None:
                                usage = chunk.usage
                            if chunk.finish_reason is not None:
                                finish = chunk.finish_reason
                except GatewayError as failure:
                    error = failure
                except Exception as failure:  # noqa: BLE001 - classified inside the gateway
                    error = GatewayError(
                        GatewayErrorType.INTERNAL_GATEWAY_ERROR,
                        f"the gateway failed while streaming ({type(failure).__name__})",
                        provider=candidate.provider.provider_id, model=candidate.ref.model_id)

                attempt = _Attempt(
                    started_at=started_at, finished_at=self.clock.now(),
                    latency_ms=round((time.perf_counter() - attempt_clock) * 1000, 2),
                    retries=retries, error=error, usage=usage)

                if error is not None:
                    self._circuit_failure(candidate, error)
                    decision = self._retry.decide(error, attempt_number, self.jitter)
                    # A retry after output has been delivered would repeat the beginning of the
                    # answer, which is the same defect as a fallback after output: two generations
                    # concatenated into one that reads as a single answer.
                    if decision.retry and received == 0 and delivered == 0:
                        self._metric_retry(candidate.provider.provider_id, error)
                        logger.info("retrying a streaming call", extra=call_fields(
                            request_id=request.request_id,
                            provider=candidate.provider.provider_id,
                            model=candidate.ref.model_id, endpoint=str(endpoint),
                            attempt=attempt_number, error_type=str(error.error_type)))
                        await self._retry.wait(decision, self.clock)
                        retries += 1
                        attempt_number += 1
                        continue
                else:
                    for scope in scope_keys(candidate.provider.provider_id,
                                            candidate.ref.model_id):
                        self._circuit.record_success(scope)

                chain.append(self._attempt_record(candidate, endpoint, index, attempt))
                await self._record(request, candidate, endpoint, plan, attempt, fingerprint,
                                   index)
                self._metric_request(candidate, endpoint, plan,
                                     "SUCCEEDED" if error is None else "FAILED",
                                     time.perf_counter() - started)
                break

            if error is None:
                if not usage.empty:
                    yield StreamEvent(type=StreamEventType.USAGE,
                                      request_id=request.request_id, sequence=sequence,
                                      usage=usage)
                    sequence += 1
                yield StreamEvent(
                    type=StreamEventType.END, request_id=request.request_id, sequence=sequence,
                    finish_reason=finish, usage=usage if not usage.empty else None,
                    ref=candidate.ref, endpoint=endpoint, route=self._decision(plan, chain),
                    latency_ms=round((time.perf_counter() - started) * 1000, 2))
                return

            last_error = error
            self._metric_error(candidate.provider.provider_id, error)

            if delivered:
                yield StreamEvent(
                    type=StreamEventType.ERROR, request_id=request.request_id, sequence=sequence,
                    error=self._with_route(
                        error, plan, chain,
                        "output had already been delivered, so no other model may continue it"
                    ).to_dict(),
                    ref=candidate.ref, endpoint=endpoint, finish_reason=FinishReason.ERROR,
                    route=self._decision(plan, chain))
                return

            allowed, why = may_fall_back(error, remaining)
            if not allowed:
                raise self._with_route(error, plan, chain, why)
            self._metric_fallback(candidate.provider.provider_id, error)

        raise self._exhausted(last_error, plan, chain)

    # -- internals ------------------------------------------------------------------------------

    def _selected(self, provider_id: str | None) -> list[ProviderConfig]:
        if provider_id is None:
            return sorted((config for config in self.providers.values() if config.enabled),
                          key=lambda item: item.provider_id)
        chosen = self.providers.get(provider_id)
        if chosen is None:
            raise GatewayError(
                GatewayErrorType.INVALID_REQUEST,
                f"provider {provider_id!r} is not configured",
                details={"provider": provider_id})
        return [chosen]

    async def _plan(self, request: GatewayRequest) -> RoutePlan:
        """Route the request, then tighten the output cap to the chosen model's own limit.

        Two passes because the model's cap is only knowable once a model has been chosen, and the
        context filter needs a cap to subtract from the window. The first pass uses the gateway's
        cap, which is never larger than what the second pass produces, so tightening afterwards
        cannot turn an accepted candidate into a rejected one.
        """
        models = await self.catalog_store.list_models(active=True)
        plan = self._router.plan(
            request, models, self.providers,
            output_tokens=effective_output_tokens(request, self.settings, None))
        chosen = plan.candidates[0]
        tightened = effective_output_tokens(request, self.settings, chosen.model.max_output_tokens)
        return plan if tightened == plan.output_tokens else replace(plan, output_tokens=tightened)

    def _endpoint_for(self, candidate: Candidate, chain: list[RouteAttempt],
                      index: int) -> Endpoint | None:
        """Pick the protocol, or record the candidate as skipped when none fits."""
        try:
            return select_endpoint(candidate.model, candidate.provider).endpoint
        except GatewayError as error:
            chain.append(RouteAttempt(
                ref=candidate.ref, endpoint=None, attempt=index + 1, outcome="SKIPPED",
                error_type=str(error.error_type)))
            return None

    def _circuit_block(self, candidate: Candidate, chain: list[RouteAttempt], index: int,
                       endpoint: Endpoint) -> GatewayError | None:
        for scope in scope_keys(candidate.provider.provider_id, candidate.ref.model_id):
            if self._circuit.allow(scope):
                continue
            error = GatewayError(
                GatewayErrorType.CIRCUIT_OPEN,
                f"the circuit for {scope} is open after repeated failures",
                provider=candidate.provider.provider_id, model=candidate.ref.model_id,
                details={"scope": scope})
            chain.append(RouteAttempt(
                ref=candidate.ref, endpoint=endpoint, attempt=index + 1, outcome="SKIPPED",
                error_type=str(error.error_type)))
            self._metric_error(candidate.provider.provider_id, error)
            return error
        return None

    async def _call(self, request: GatewayRequest, candidate: Candidate, endpoint: Endpoint,
                    output_tokens: int) -> _Attempt:
        """Call one candidate, retrying within the policy, and report what happened."""
        provider = self.provider_factory(candidate.provider)
        started_at = self.clock.now()
        clock_started = time.perf_counter()
        retries = 0
        attempt_number = 1

        while True:
            error: GatewayError
            try:
                completion = await provider.generate(
                    request, candidate.model, endpoint, output_tokens=output_tokens)
            except GatewayError as failure:
                error = failure
            except Exception as failure:  # noqa: BLE001 - classified inside the gateway
                error = GatewayError(
                    GatewayErrorType.INTERNAL_GATEWAY_ERROR,
                    f"the gateway failed while calling the provider ({type(failure).__name__})",
                    provider=candidate.provider.provider_id, model=candidate.ref.model_id)
            else:
                for scope in scope_keys(candidate.provider.provider_id, candidate.ref.model_id):
                    self._circuit.record_success(scope)
                return _Attempt(
                    started_at=started_at, finished_at=self.clock.now(),
                    latency_ms=round((time.perf_counter() - clock_started) * 1000, 2),
                    retries=retries, completion=completion, usage=completion.usage)

            self._circuit_failure(candidate, error)
            decision = self._retry.decide(error, attempt_number, self.jitter)
            if not decision.retry:
                return _Attempt(
                    started_at=started_at, finished_at=self.clock.now(),
                    latency_ms=round((time.perf_counter() - clock_started) * 1000, 2),
                    retries=retries, error=error)
            self._metric_retry(candidate.provider.provider_id, error)
            logger.info("retrying a provider call", extra=call_fields(
                request_id=request.request_id, provider=candidate.provider.provider_id,
                model=candidate.ref.model_id, endpoint=str(endpoint), attempt=attempt_number,
                error_type=str(error.error_type)))
            await self._retry.wait(decision, self.clock)
            retries += 1
            attempt_number += 1

    def _circuit_failure(self, candidate: Candidate, error: GatewayError) -> None:
        if error.error_type in _NOT_THE_PROVIDERS_FAULT:
            return
        for scope in scope_keys(candidate.provider.provider_id, candidate.ref.model_id):
            self._circuit.record_failure(scope)

    def _attempt_record(self, candidate: Candidate, endpoint: Endpoint, index: int,
                        attempt: _Attempt) -> RouteAttempt:
        return RouteAttempt(
            ref=candidate.ref, endpoint=endpoint, attempt=index + 1,
            outcome="FAILED" if attempt.error else "SUCCEEDED",
            error_type=str(attempt.error.error_type) if attempt.error else None,
            retries=attempt.retries, latency_ms=attempt.latency_ms)

    def _decision(self, plan: RoutePlan, chain: list[RouteAttempt]) -> RouteDecision:
        reason = RouteReason.FALLBACK if len(chain) > 1 else plan.reason
        return RouteDecision(reason=reason, route=plan.route, considered=plan.considered,
                             rejected=plan.rejected, chain=tuple(chain))

    def _with_route(self, error: GatewayError, plan: RoutePlan, chain: list[RouteAttempt],
                    why: str) -> GatewayError:
        """Return the failure with the routing context attached, and nothing else added."""
        decision = self._decision(plan, chain)
        details = dict(error.details)
        details.update({
            "route": decision.route,
            "routeReason": str(decision.reason),
            "fallbackCount": decision.fallback_count,
            "fallbackStopped": why,
            "chain": [attempt.model_dump(mode="json") for attempt in decision.chain],
        })
        return GatewayError(
            error.error_type, redact_text(error.message), provider=error.provider,
            model=error.model, status_code=error.status_code,
            retry_after_seconds=error.retry_after_seconds, details=details)

    def _exhausted(self, last_error: GatewayError | None, plan: RoutePlan,
                   chain: list[RouteAttempt]) -> GatewayError:
        return self._with_route(
            last_error or GatewayError(
                GatewayErrorType.NO_CANDIDATE,
                "every candidate was refused before it could be called"),
            plan, chain, "the candidate list is exhausted")

    async def _record(self, request: GatewayRequest, candidate: Candidate, endpoint: Endpoint,
                      plan: RoutePlan, attempt: _Attempt, fingerprint: str, index: int) -> None:
        """Persist one attempt's operational metadata.

        Wrapped so a storage failure never turns a successful inference into an error: the answer is
        already correct and losing the record is the lesser failure. It is logged, loudly.
        """
        record = ModelCallRecord(
            request_id=request.request_id,
            provider_id=candidate.provider.provider_id,
            model_id=candidate.ref.model_id,
            endpoint=str(endpoint),
            route=plan.route,
            purpose=str(plan.reason),
            status="SUCCEEDED" if attempt.error is None else "FAILED",
            succeeded=attempt.error is None,
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            latency_ms=int(attempt.latency_ms),
            input_tokens=attempt.usage.input_tokens,
            output_tokens=attempt.usage.output_tokens,
            cached_input_tokens=attempt.usage.cached_input_tokens,
            reasoning_tokens=attempt.usage.reasoning_tokens,
            cost=estimate_cost(attempt.usage, self.pricing.for_model(candidate.ref.qualified)),
            error_type=str(attempt.error.error_type) if attempt.error else None,
            retry_count=attempt.retries,
            fallback_count=index,
            correlation_id=self.correlation_id,
            request_fingerprint=fingerprint,
        )
        try:
            await self.call_store.record(record)
        except Exception as error:  # noqa: BLE001 - recording must not fail the call
            logger.error("the model call could not be recorded", exc_info=error,
                         extra=call_fields(request_id=request.request_id,
                                           provider=candidate.provider.provider_id,
                                           model=candidate.ref.model_id))

    # -- telemetry ------------------------------------------------------------------------------

    def _metric_request(self, candidate: Candidate, endpoint: Endpoint, plan: RoutePlan,
                        status: str, seconds: float) -> None:
        if self.metrics is not None:
            self.metrics.observe_request(
                provider=candidate.provider.provider_id, model=candidate.ref.model_id,
                endpoint=str(endpoint), route=plan.route, status=status, seconds=seconds)

    def _metric_error(self, provider_id: str, error: GatewayError) -> None:
        if self.metrics is not None:
            self.metrics.observe_error(provider=provider_id, error_type=str(error.error_type))

    def _metric_retry(self, provider_id: str, error: GatewayError) -> None:
        if self.metrics is not None:
            self.metrics.observe_retry(provider=provider_id, error_type=str(error.error_type))

    def _metric_fallback(self, provider_id: str, error: GatewayError) -> None:
        if self.metrics is not None:
            self.metrics.observe_fallback(provider=provider_id, error_type=str(error.error_type))

    def _metric_health(self, provider_id: str, reachable: bool) -> None:
        if self.metrics is not None:
            self.metrics.observe_provider_health(provider_id, reachable)

    async def _publish_catalog_size(self, provider_id: str) -> None:
        if self.metrics is None:
            return
        models: list[ModelDescriptor] = await self.catalog_store.list_models(
            provider_id=provider_id)
        active = sum(1 for model in models if model.active)
        self.metrics.observe_catalog(provider_id, active=active, inactive=len(models) - active)


def default_provider_factory(settings: GatewaySettings, transport=None) -> ProviderFactory:
    """The factory a running process uses: resolve the environment, build the HTTP provider.

    Defined beside the gateway so the composition is one import away from the thing that needs it,
    and so a test can supply a transport without the application growing a parameter only tests use.
    """
    from iacode_model_gateway.protocols import build_adapters
    from iacode_model_gateway.providers.http_provider import HttpModelProvider

    def factory(config: ProviderConfig) -> ModelProvider:
        resolved = resolve_provider(config)
        adapters = build_adapters(config.protocols, config.protocol_options)
        return HttpModelProvider(resolved, adapters, settings, transport=transport)

    return factory
