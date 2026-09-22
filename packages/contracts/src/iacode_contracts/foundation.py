"""The response contracts of the Foundation endpoints.

These models are the API's promise to its callers, and they live in a package of their own because
later Gates will have more than one producer: the CLI and the orchestrator will report health with
the same vocabulary the API uses. Defining the shapes next to the FastAPI routes would make every
future consumer import the web application to learn what a readiness report looks like.

The contract distinguishes two questions that are often collapsed into one:

``/health``  is this process alive? Answered without touching any external dependency, because a
             liveness probe that fails when the database is down asks an orchestrator to restart a
             perfectly healthy process.
``/ready``   can this process accept work? Answered by probing every mandatory dependency. An
             unavailable dependency produces ``NOT_READY`` and a non-2xx status, never a reassuring
             answer with a warning buried in the payload.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ServiceStatus(StrEnum):
    """Liveness of the process itself."""

    UP = "UP"
    DOWN = "DOWN"


class ReadinessStatus(StrEnum):
    """Whether the service may accept work."""

    READY = "READY"
    NOT_READY = "NOT_READY"


class DependencyStatus(StrEnum):
    """Outcome of probing one dependency.

    ``SKIPPED`` exists for a dependency that configuration declares optional. It is never used to
    hide a failing mandatory dependency: an optional dependency is declared optional in
    configuration, before it is probed, and never because the probe failed.
    """

    UP = "UP"
    DOWN = "DOWN"
    SKIPPED = "SKIPPED"


class DependencyReport(BaseModel):
    """One dependency, its outcome, how long the probe took and why it failed."""

    name: str = Field(description="Dependency identifier, for example 'postgres'.")
    status: DependencyStatus
    mandatory: bool = Field(description="Whether readiness requires this dependency.")
    latencyMs: float | None = Field(
        default=None, description="Probe duration in milliseconds; absent when not probed.")
    detail: str | None = Field(
        default=None,
        description="Why the probe failed, redacted. Absent when the dependency is UP.")


class HealthResponse(BaseModel):
    """Process liveness. Deliberately independent of every external dependency."""

    service: str
    status: ServiceStatus
    version: str
    commit: str
    timestamp: str = Field(description="RFC 3339 UTC instant the answer was produced.")


class ReadinessResponse(BaseModel):
    """Whether the service can accept work, with the evidence behind the verdict."""

    service: str
    status: ReadinessStatus
    version: str
    commit: str
    timestamp: str
    dependencies: list[DependencyReport]


class VersionResponse(BaseModel):
    """Build identity. Carries nothing that could be a credential."""

    service: str
    version: str
    commit: str
    buildTimestamp: str | None = Field(
        default=None, description="When the image was built; absent outside a built image.")
    pythonVersion: str
    environment: str = Field(description="The configuration profile in force, for example 'local'.")


class ErrorResponse(BaseModel):
    """The single error shape every failing endpoint returns.

    Small on purpose. ``code`` is a stable machine token, ``message`` is safe for a human, and
    ``correlationId`` is how an operator finds the log record that does carry the detail. Nothing
    here ever contains a traceback, an internal path or a dependency error verbatim.
    """

    code: str = Field(description="Stable, machine-readable error token.")
    message: str = Field(description="Safe human-readable summary, free of internal detail.")
    correlationId: str | None = Field(
        default=None, description="Correlation identifier of the request that failed.")
    details: dict[str, object] | None = Field(
        default=None, description="Structured, non-sensitive context such as validation errors.")
