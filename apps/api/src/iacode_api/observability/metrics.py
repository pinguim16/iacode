"""Prometheus metrics for the API.

Four instruments, chosen so the Foundation dashboard can answer the only questions it needs to:
how much traffic, how slow, how many failures, and is each dependency up.

The label sets are deliberately small. ``method``, ``path`` and ``status`` on requests; ``name`` on
dependencies. The decisive rule is that **``path`` is the route template, never the raw URL**: a
counter labelled with ``/projects/7f3c...`` creates one time series per identifier, and a metric
that grows a series per request is the standard way to take down a Prometheus.

A registry is created per application rather than using the process-global default. The global one
is module state: a second application in the same interpreter — which is what a test suite is —
raises ``Duplicated timeseries`` on the second instantiation.
"""

from __future__ import annotations

import time

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Buckets in seconds, from a fast local call to a request in trouble. The default Prometheus
# buckets top out at 10s, which puts every slow request into ``+Inf`` where it cannot be
# distinguished from a timeout.
LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)

UNMATCHED_PATH = "<unmatched>"


class Metrics:
    """The instrument set of one application."""

    def __init__(self, service: str, version: str) -> None:
        self.registry = CollectorRegistry()
        self.service = service

        self.requests = Counter(
            "iacode_http_requests_total",
            "HTTP requests handled, by method, route template and status code.",
            labelnames=("service", "method", "path", "status"),
            registry=self.registry,
        )
        self.latency = Histogram(
            "iacode_http_request_duration_seconds",
            "HTTP request duration in seconds, by method and route template.",
            labelnames=("service", "method", "path"),
            buckets=LATENCY_BUCKETS,
            registry=self.registry,
        )
        self.in_flight = Gauge(
            "iacode_http_requests_in_flight",
            "HTTP requests currently being handled.",
            labelnames=("service",),
            registry=self.registry,
        )
        self.dependency_up = Gauge(
            "iacode_dependency_up",
            "Whether a dependency answered its last readiness probe: 1 up, 0 down.",
            labelnames=("service", "name"),
            registry=self.registry,
        )
        self.build = Gauge(
            "iacode_build_info",
            "Always 1; the labels carry the build identity.",
            labelnames=("service", "version"),
            registry=self.registry,
        )
        self.build.labels(service=service, version=version).set(1)

    def record_dependency(self, name: str, up: bool) -> None:
        self.dependency_up.labels(service=self.service, name=name).set(1 if up else 0)

    def render(self) -> tuple[bytes, str]:
        # The body and the content type must come from the same exposition format. Rendering
        # the text format while advertising OpenMetrics made Prometheus reject every scrape
        # with "data does not end with # EOF", which reads like a truncated response rather
        # than like a header that does not match its body.
        return generate_latest(self.registry), CONTENT_TYPE_LATEST


def route_template(request: Request) -> str:
    """The template of the route that handled the request, or one bucket for anything unmatched.

    The value is read from ``scope["route"]``, which the router sets on the route it actually
    matched. That is only available *after* the request has been handled, which is why this is
    called in the middleware's ``finally`` rather than before ``call_next``.

    Re-matching the request against ``app.routes`` was the obvious alternative and it was wrong:
    FastAPI wraps an included router in a single object, so the top-level list does not contain the
    routes the routers own, and every request was labelled ``<unmatched>`` while the metrics
    endpoint looked like it was working.

    Anything genuinely unmatched collapses into one series, because an unmatched path is
    attacker-controlled: a scanner probing ten thousand URLs would otherwise create ten thousand
    time series.
    """
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) and path else UNMATCHED_PATH


class MetricsMiddleware(BaseHTTPMiddleware):
    """Count every request, time it, and keep the in-flight gauge honest."""

    def __init__(self, app, metrics: Metrics) -> None:
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        self.metrics.in_flight.labels(service=self.metrics.service).inc()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            # ``finally`` rather than the success path: an exception that escapes the handler must
            # still decrement the gauge and still be counted, otherwise a burst of failures leaves
            # the API permanently reporting requests that finished long ago.
            elapsed = time.perf_counter() - started
            # Read after handling: the router records the matched route on the scope, and before
            # ``call_next`` there is nothing to read.
            path = route_template(request)
            self.metrics.in_flight.labels(service=self.metrics.service).dec()
            self.metrics.latency.labels(
                service=self.metrics.service, method=request.method, path=path).observe(elapsed)
            self.metrics.requests.labels(
                service=self.metrics.service, method=request.method, path=path,
                status=str(status_code)).inc()
