"""Prometheus instruments for the gateway.

Registered into the registry the application already owns, so ``/metrics`` exposes one document and
the Foundation's scrape configuration needs no change. Creating a second registry here would produce
a second endpoint nobody scrapes.

**Every label is bounded and none of them carries content.** The label sets are ``provider``,
``model``, ``endpoint``, ``route``, ``status`` and ``error_type``. Each is drawn from a closed set —
the catalog, the configured routes, the error taxonomy — so the number of series is bounded by
configuration rather than by traffic. A prompt, a completion, a request identifier or a credential
in a label would be both a cardinality explosion and a disclosure, which is why ``route`` is the
alias and not the free-text value a caller sent.

The buckets run from a fast local model to a slow reasoning call. The Prometheus defaults top out at
ten seconds, which puts every interesting inference request into ``+Inf``, where a slow answer and a
timeout look identical.
"""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

__all__ = ["GatewayMetrics", "LATENCY_BUCKETS"]

#: Seconds. A small model answers in under a second; a reasoning model with a large output can take
#: minutes, and the read timeout allows it.
LATENCY_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0, 300.0)

#: What a route label holds when the caller named no alias. A fixed token rather than an empty
#: string, so the series is legible in a query.
NO_ROUTE = "none"

_CIRCUIT_VALUES = {"CLOSED": 0.0, "HALF_OPEN": 1.0, "OPEN": 2.0}


class GatewayMetrics:
    """The gateway's instruments, on the application's registry."""

    def __init__(self, registry: CollectorRegistry, service: str = "iacode-api") -> None:
        self.service = service
        self.requests = Counter(
            "iacode_gateway_requests_total",
            "Gateway inference requests, by provider, model, endpoint, route and outcome.",
            labelnames=("service", "provider", "model", "endpoint", "route", "status"),
            registry=registry,
        )
        self.duration = Histogram(
            "iacode_gateway_request_duration_seconds",
            "End-to-end duration of a gateway request, including retries and fallbacks.",
            labelnames=("service", "provider", "model", "endpoint", "route"),
            buckets=LATENCY_BUCKETS,
            registry=registry,
        )
        self.errors = Counter(
            "iacode_gateway_errors_total",
            "Classified gateway failures, by provider and error type.",
            labelnames=("service", "provider", "error_type"),
            registry=registry,
        )
        self.retries = Counter(
            "iacode_gateway_retries_total",
            "Retries of the same candidate, by provider and the error class that caused them.",
            labelnames=("service", "provider", "error_type"),
            registry=registry,
        )
        self.fallbacks = Counter(
            "iacode_gateway_fallbacks_total",
            "Moves to a different candidate, by provider and the error class that caused them.",
            labelnames=("service", "provider", "error_type"),
            registry=registry,
        )
        self.circuit_state = Gauge(
            "iacode_gateway_circuit_state",
            "Circuit breaker state by scope: 0 closed, 1 half-open, 2 open.",
            labelnames=("service", "scope"),
            registry=registry,
        )
        self.provider_health = Gauge(
            "iacode_gateway_provider_health",
            "Whether a provider answered its last health probe: 1 reachable, 0 not.",
            labelnames=("service", "provider"),
            registry=registry,
        )
        self.catalog_size = Gauge(
            "iacode_model_catalog_size",
            "Models in the catalog, by provider and active state.",
            labelnames=("service", "provider", "active"),
            registry=registry,
        )

    def observe_request(self, *, provider: str, model: str, endpoint: str, route: str | None,
                        status: str, seconds: float) -> None:
        labels = (self.service, provider, model, endpoint, route or NO_ROUTE)
        self.requests.labels(*labels, status).inc()
        self.duration.labels(*labels).observe(seconds)

    def observe_error(self, *, provider: str, error_type: str) -> None:
        self.errors.labels(self.service, provider, error_type).inc()

    def observe_retry(self, *, provider: str, error_type: str) -> None:
        self.retries.labels(self.service, provider, error_type).inc()

    def observe_fallback(self, *, provider: str, error_type: str) -> None:
        self.fallbacks.labels(self.service, provider, error_type).inc()

    def observe_circuit(self, scope: str, state: str) -> None:
        self.circuit_state.labels(self.service, scope).set(_CIRCUIT_VALUES.get(state, 0.0))

    def observe_provider_health(self, provider: str, reachable: bool) -> None:
        self.provider_health.labels(self.service, provider).set(1.0 if reachable else 0.0)

    def observe_catalog(self, provider: str, *, active: int, inactive: int) -> None:
        self.catalog_size.labels(self.service, provider, "true").set(active)
        self.catalog_size.labels(self.service, provider, "false").set(inactive)
