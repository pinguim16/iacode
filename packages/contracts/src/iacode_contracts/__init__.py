"""Shared API contracts.

The package holds the shapes that cross a process boundary. A model here is a promise to a caller
the producer does not control, so changing one is an API change and belongs in an ADR.
"""

from iacode_contracts.foundation import (
    DependencyReport,
    DependencyStatus,
    ErrorResponse,
    HealthResponse,
    ReadinessResponse,
    ReadinessStatus,
    ServiceStatus,
    VersionResponse,
)

__all__ = [
    "DependencyReport",
    "DependencyStatus",
    "ErrorResponse",
    "HealthResponse",
    "ReadinessResponse",
    "ReadinessStatus",
    "ServiceStatus",
    "VersionResponse",
]
