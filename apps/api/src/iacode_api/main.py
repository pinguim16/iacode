"""The IACode API application.

Everything the process is, assembled in one place: configuration, logging, middleware, error
handlers and routes. :func:`create_app` takes its settings as an argument so a test builds an
application with explicit configuration instead of mutating the environment and hoping no cache
survived.

Middleware order is a decision, not an accident. Starlette runs middleware outermost-first:

    CORS -> correlation -> metrics -> routes

* **CORS outermost** so a rejected pre-flight is answered before anything else runs, and so the
  headers are present on error responses too — a browser that cannot read a 500 reports it as a
  CORS failure, which sends the reader hunting in the wrong place.
* **Correlation before metrics** so the identifier is already bound when the metrics layer logs.
* **Metrics innermost** so the duration it observes is the handler's, not the middleware stack's.

Gate 0 exposed health, readiness, version and metrics. Gate 1 added the Model Gateway under
``/api/v1/gateway``. Gate 2 adds the agent runtime under ``/api/v1/agent-runs``: creating a run,
reading it, streaming its events, cancelling it and answering a tool request, plus the declared
agents and teams. There is still no endpoint over the remaining domain tables, because the
capabilities that would fill them belong to later Gates.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from iacode_telemetry.logging import configure_logging, get_logger

from iacode_api.config import Settings, get_settings
from iacode_api.errors import register_error_handlers
from iacode_api.lifespan import lifespan
from iacode_api.middleware.correlation import REQUEST_ID_HEADER, CorrelationMiddleware
from iacode_api.observability.metrics import Metrics, MetricsMiddleware
from iacode_api.routes import agent_runs, gateway, health, version

logger = get_logger(__name__)

DESCRIPTION = """
The IACode Foundation API.

Gate 0 delivered the runtime foundation: configuration, persistence, cache, object storage,
durable workflows and observability. Gate 1 adds the Model Gateway: one provider-neutral boundary
for model discovery, routing and invocation, with streaming, retries, a circuit breaker and a
bounded fallback chain.

Gate 2 adds the agent runtime: durable agent runs, a team of agents, budgets, cancellation and a
tool-request lifecycle that pauses a run and waits. **Nothing here executes a tool.** The
sandbox that will belongs to Gate 3.
""".strip()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an application instance from explicit settings."""
    settings = settings or get_settings()
    configure_logging(
        service=settings.service_name, level=settings.log_level, version=settings.version)

    app = FastAPI(
        title="IACode API",
        version=settings.version,
        description=DESCRIPTION,
        root_path=settings.root_path,
        lifespan=lifespan,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url=None,
    )

    metrics = Metrics(service=settings.service_name, version=settings.version)
    app.state.settings = settings
    app.state.metrics = metrics
    app.state.resources = None

    app.add_middleware(MetricsMiddleware, metrics=metrics)
    app.add_middleware(CorrelationMiddleware, header_name=settings.correlation_header)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[settings.correlation_header, "Content-Type", "Accept"],
        expose_headers=[settings.correlation_header, REQUEST_ID_HEADER],
        max_age=600,
    )

    register_error_handlers(app)
    # Registered after the Foundation handlers and from here rather than from ``errors.py``: the
    # Foundation error module knows nothing about the gateway, and the direction of that dependency
    # is what keeps Gate 0 independent of Gate 1.
    gateway.register_gateway_errors(app)
    agent_runs.register_agent_runtime_errors(app)
    app.include_router(health.router)
    app.include_router(version.router)
    app.include_router(gateway.router)
    app.include_router(agent_runs.router)
    return app


# No module-level ``app``. Building one at import time would read the environment as a side effect
# of importing this module, so every test that imports ``create_app`` would first construct an
# application from the ambient configuration. The server is started with uvicorn's ``--factory``
# flag against :func:`create_app` instead, which is the same wiring without the import-time read.
