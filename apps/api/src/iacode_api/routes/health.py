"""Liveness and readiness.

The two endpoints answer different questions and are wired to different things on purpose.

``GET /health``  is about the process. It touches no dependency, so it stays ``UP`` while
                 PostgreSQL is restarting. A liveness probe that fails when a dependency fails asks
                 the orchestrator to kill a healthy process, which turns a recoverable outage into
                 a restart loop.

``GET /ready``   is about the work. It probes every mandatory dependency for real and returns
                 ``503`` when any of them is down, so a load balancer stops sending traffic that
                 cannot be served. The payload names the failing dependency, because "not ready"
                 without a reason turns every incident into a guessing game.

Readiness also feeds the ``iacode_dependency_up`` gauge, so the same probe that decides the verdict
is the one Prometheus reports. A separate scraping path would eventually disagree with the endpoint.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from iacode_contracts.foundation import (
    DependencyStatus,
    HealthResponse,
    ReadinessResponse,
    ReadinessStatus,
    ServiceStatus,
)

from iacode_api.dependencies import ResourcesDep, build_probes
from iacode_api.readiness import run_probes

router = APIRouter(tags=["foundation"])


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Process liveness",
    description=(
        "Reports whether this process is alive. Answered without contacting any dependency, so a "
        "dependency outage never makes a healthy process look dead."
    ),
)
async def health(resources: ResourcesDep) -> HealthResponse:
    settings = resources.settings
    return HealthResponse(
        service=settings.service_name,
        status=ServiceStatus.UP,
        version=settings.version,
        commit=settings.commit,
        timestamp=_now(),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness to accept work",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ReadinessResponse,
            "description": "At least one mandatory dependency is unavailable.",
        }
    },
    description=(
        "Probes PostgreSQL, Redis, MinIO and Temporal. Returns 503 when any mandatory dependency "
        "is unavailable, naming the dependency and why the probe failed."
    ),
)
async def ready(resources: ResourcesDep, response: Response) -> ReadinessResponse:
    settings = resources.settings
    outcome = await run_probes(build_probes(resources), settings.readiness_timeout_seconds)

    for report in outcome.reports:
        resources.metrics.record_dependency(report.name, report.status is DependencyStatus.UP)

    if not outcome.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        service=settings.service_name,
        status=ReadinessStatus.READY if outcome.ready else ReadinessStatus.NOT_READY,
        version=settings.version,
        commit=settings.commit,
        timestamp=_now(),
        dependencies=outcome.reports,
    )
