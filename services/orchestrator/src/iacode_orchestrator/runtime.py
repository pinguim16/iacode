"""The Temporal SDK runtime, configured to expose Prometheus metrics.

The SDK's core emits workflow, activity and task-queue metrics of its own. Exposing those is worth
more than any counter the application could add at this Gate: they answer whether tasks are being
polled, whether activities are failing and how long the worker waits, which is precisely what an
operator wants to know about a worker and precisely what a hand-rolled counter around one smoke
workflow would not say.

The runtime is a process-level singleton because the SDK binds a metrics listener to a port.
Creating a second one raises an address-in-use error that surfaces, confusingly, as a client
connection failure.
"""

from __future__ import annotations

from temporalio.runtime import PrometheusConfig, Runtime, TelemetryConfig

# Internal to the Compose network. It is not published to the host: Prometheus scrapes it over the
# stack's own network, and publishing it would expose an unauthenticated metrics endpoint for no
# operator benefit.
METRICS_BIND_ADDRESS = "0.0.0.0:9100"

_runtime: Runtime | None = None


def get_runtime(bind_address: str = METRICS_BIND_ADDRESS) -> Runtime:
    """The process-wide SDK runtime, created once."""
    global _runtime
    if _runtime is None:
        _runtime = Runtime(
            telemetry=TelemetryConfig(
                metrics=PrometheusConfig(bind_address=bind_address),
            )
        )
    return _runtime
