"""Composing the gateway for this process.

One function, called once per request, that turns the application's settings into a
:class:`~iacode_model_gateway.gateway.ModelGateway`. It is where the two halves meet: the
application's typed configuration on one side, the gateway's own settings object on the other, and
the stores in between.

Built per request rather than held on the application, for one reason: the correlation identifier.
A gateway carries the identifier of the request that is using it so that every provider attempt and
every persisted row can be traced back to the HTTP call that caused it, and an object shared between
concurrent requests could not carry it truthfully. Everything expensive — the session factory, the
metrics registry, the parsed policy — is created once and handed in, so building the wrapper is a
few attribute reads.

The provider policy is read from disk on each build and cached by modification time, because an
operator who edits ``providers.json`` expects the next request to see it and should not have to
restart the API to enable a provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from iacode_model_gateway.config import (
    GatewaySettings,
    ProviderConfig,
    RoutePolicy,
    load_provider_configs,
    load_route_policy,
)
from iacode_model_gateway.gateway import ModelGateway, default_provider_factory
from iacode_model_gateway.telemetry.metrics import GatewayMetrics
from prometheus_client import CollectorRegistry

from iacode_api.config import Settings
from iacode_api.gateway.store import SqlCatalogStore, SqlModelCallStore

__all__ = ["GatewayRuntime", "build_gateway_settings", "build_runtime"]


def build_gateway_settings(settings: Settings) -> GatewaySettings:
    """Translate the application's configuration into the gateway's.

    Written out field by field rather than by copying a prefix, so a key added to one side without
    the other is a name error here instead of a setting that silently keeps its default.
    """
    return GatewaySettings(
        policy_dir=Path(settings.gateway_policy_dir),
        default_model=settings.gateway_default_model,
        smoke_model=settings.gateway_smoke_model,
        connect_timeout_seconds=settings.gateway_connect_timeout_seconds,
        read_timeout_seconds=settings.gateway_read_timeout_seconds,
        max_attempts=settings.gateway_max_attempts,
        retry_initial_backoff_seconds=settings.gateway_retry_initial_backoff_seconds,
        retry_max_backoff_seconds=settings.gateway_retry_max_backoff_seconds,
        retry_max_retry_after_seconds=settings.gateway_retry_max_retry_after_seconds,
        circuit_failure_threshold=settings.gateway_circuit_failure_threshold,
        circuit_cooldown_seconds=settings.gateway_circuit_cooldown_seconds,
        circuit_half_open_successes=settings.gateway_circuit_half_open_successes,
        max_fallbacks=settings.gateway_max_fallbacks,
        max_request_bytes=settings.gateway_max_request_bytes,
        max_messages=settings.gateway_max_messages,
        max_tools=settings.gateway_max_tools,
        max_output_tokens=settings.gateway_max_output_tokens,
        max_response_bytes=settings.gateway_max_response_bytes,
        persist_prompts=settings.gateway_persist_prompts,
    )


@dataclass
class GatewayRuntime:
    """Everything a gateway needs that is worth building once per process."""

    settings: GatewaySettings
    providers: dict[str, ProviderConfig]
    route_policy: RoutePolicy
    catalog_store: SqlCatalogStore
    call_store: SqlModelCallStore
    metrics: GatewayMetrics

    def gateway(self, correlation_id: str | None = None) -> ModelGateway:
        """A gateway bound to one request's correlation identifier."""
        return ModelGateway(
            settings=self.settings,
            providers=self.providers,
            route_policy=self.route_policy,
            catalog_store=self.catalog_store,
            call_store=self.call_store,
            provider_factory=default_provider_factory(self.settings),
            metrics=self.metrics,
            correlation_id=correlation_id,
        )


def build_runtime(settings: Settings, session_factory, registry: CollectorRegistry,
                  ) -> GatewayRuntime:
    """Read the policy, wire the stores and register the instruments.

    Called from the application lifespan. A failure to read the policy is a start-up failure, which
    is deliberate: an API that started with no providers would answer every inference request with
    "no candidate" and look like a routing bug rather than a missing file.
    """
    gateway_settings = build_gateway_settings(settings)
    configs = load_provider_configs(gateway_settings.policy_dir)
    return GatewayRuntime(
        settings=gateway_settings,
        providers={config.provider_id: config for config in configs},
        route_policy=load_route_policy(gateway_settings.policy_dir),
        catalog_store=SqlCatalogStore(session_factory),
        call_store=SqlModelCallStore(session_factory),
        metrics=GatewayMetrics(registry, service=settings.service_name),
    )
