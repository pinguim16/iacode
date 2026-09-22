"""Catalog synchronization: fetch, validate, normalize, then commit — in that order.

The order is the safety property. `docs/GATE-1-CHECKLIST.md` row 6.7 requires that a failed or
partial synchronization leave the previous catalog usable, and the way to get that is to do every
fallible thing *before* touching the store:

    fetch  ->  validate the whole answer  ->  normalize every record  ->  one atomic replace

A loop that upserted each model as it parsed it would leave the catalog half-applied the first time
record eleven of forty turned out to be malformed, and the operator would be left with a catalog
that is neither the old one nor the new one.

Two answers are refused rather than applied.

**An empty answer.** A provider returning zero models over a 200 is indistinguishable from a
provider having a bad day, and applying it would deactivate every model in the catalog and take the
gateway offline. The previous catalog stays, the outcome records the refusal, and an operator
decides.

**A duplicated identifier.** Applying it would make the surviving record depend on iteration order.

A model that is genuinely gone from a *valid* answer is deactivated, never deleted, because rows in
``model_calls`` point at it and a deleted model turns recorded history into dangling references.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iacode_model_gateway.catalog.normalize import normalise_models
from iacode_model_gateway.contracts import Capability, CapabilityState, ModelDescriptor
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.ports import CatalogStore, Clock, ProviderRecord, SyncOutcome

__all__ = ["CatalogSynchroniser", "DiscoveredCatalog"]


@dataclass(frozen=True)
class DiscoveredCatalog:
    """What a provider answered when asked for its models."""

    provider_id: str
    entries: tuple[tuple[str, dict[str, Any]], ...]


class CatalogSynchroniser:
    """Applies a provider's discovery answer to the catalog, atomically or not at all."""

    def __init__(self, store: CatalogStore, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    async def apply(self, discovered: DiscoveredCatalog, *, display_name: str, adapter: str,
                    enabled: bool,
                    overrides: dict[str, dict[Capability, CapabilityState]] | None = None,
                    provider_capabilities: dict[Capability, CapabilityState] | None = None,
                    provider_endpoints: tuple[Any, ...] = (),
                    provider_reasoning_levels: tuple[Any, ...] = ()) -> SyncOutcome:
        """Validate, normalize and commit one provider's catalog."""
        if not discovered.entries:
            raise GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                f"provider {discovered.provider_id!r} listed no model; the previous catalog is "
                f"kept rather than deactivated wholesale",
                provider=discovered.provider_id)

        now = self._clock.now()
        try:
            models: list[ModelDescriptor] = normalise_models(
                discovered.provider_id, discovered.entries, synced_at=now, overrides=overrides,
                provider_capabilities=provider_capabilities,
                provider_endpoints=provider_endpoints,
                provider_reasoning_levels=provider_reasoning_levels)
        except ValueError as error:
            raise GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                f"the catalog answer from {discovered.provider_id!r} could not be normalised: "
                f"{error}",
                provider=discovered.provider_id) from error

        outcome = await self._store.replace_provider_models(discovered.provider_id, models)
        await self._store.upsert_provider(ProviderRecord(
            provider_id=discovered.provider_id,
            display_name=display_name,
            adapter=adapter,
            enabled=enabled,
            healthy=True,
            last_health_check=now,
            last_sync=now,
            model_count=len(models),
            detail=None,
        ))
        return outcome

    async def record_failure(self, provider_id: str, *, display_name: str, adapter: str,
                             enabled: bool, detail: str) -> None:
        """Record that a provider could not be synchronized, without touching its models.

        ``detail`` is the classified message, never the provider's raw body: a provider that echoes
        a request header into an error would otherwise put an authorization value into a row that
        the API serves to anyone who can reach it.
        """
        now = self._clock.now()
        existing = {record.provider_id: record for record in await self._store.list_providers()}
        previous = existing.get(provider_id)
        await self._store.upsert_provider(ProviderRecord(
            provider_id=provider_id,
            display_name=display_name,
            adapter=adapter,
            enabled=enabled,
            healthy=False,
            last_health_check=now,
            last_sync=previous.last_sync if previous else None,
            model_count=previous.model_count if previous else 0,
            detail=detail,
        ))
