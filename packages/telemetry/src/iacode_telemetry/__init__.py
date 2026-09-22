"""Observability primitives shared by the IACode runtime components.

The package owns the logging contract and the ambient identifier context that fills it. Metrics
live with the component that produces them, because a metric registry is process state rather than
a shared vocabulary.
"""

from iacode_telemetry.context import (
    CONTEXT_FIELDS,
    bind_context,
    current_context,
    get_correlation_id,
    set_context,
)
from iacode_telemetry.logging import JsonLogFormatter, configure_logging, get_logger

__all__ = [
    "CONTEXT_FIELDS",
    "JsonLogFormatter",
    "bind_context",
    "configure_logging",
    "current_context",
    "get_correlation_id",
    "get_logger",
    "set_context",
]
