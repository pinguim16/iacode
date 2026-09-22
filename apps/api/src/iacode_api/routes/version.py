"""Build identity, and the metrics endpoint.

``GET /version`` answers "what exactly is running here", which is the first question of every
incident. It carries the application version, the commit the image was built from, when it was
built, the interpreter version and the configuration profile.

It carries **nothing else**. The temptation is to make it a diagnostics dump — the configuration,
the resolved URLs, the environment — and that is how an unauthenticated endpoint starts serving a
database password. The response model in ``packages/contracts`` is closed, so adding a field is a
contract change rather than an afternoon's convenience.

``GET /metrics`` is here rather than in ``health.py`` because it is exposition, not a probe.
"""

from __future__ import annotations

from fastapi import APIRouter, Response
from iacode_contracts.foundation import VersionResponse

from iacode_api.dependencies import ResourcesDep

router = APIRouter(tags=["foundation"])


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Build identity",
    description=(
        "Reports the running version, the commit it was built from and the configuration profile "
        "in force. Carries no configuration value and no credential."
    ),
)
async def version(resources: ResourcesDep) -> VersionResponse:
    settings = resources.settings
    return VersionResponse(
        service=settings.service_name,
        version=settings.version,
        commit=settings.commit,
        buildTimestamp=settings.build_timestamp,
        pythonVersion=settings.python_version,
        environment=settings.environment,
    )


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    include_in_schema=False,
    description="Prometheus exposition of the request, latency and dependency instruments.",
)
async def metrics(resources: ResourcesDep) -> Response:
    # Excluded from the OpenAPI schema: it is an operational surface for the scraper, not part of
    # the API contract a client programs against, and its body is not JSON.
    payload, content_type = resources.metrics.render()
    return Response(content=payload, media_type=content_type)
