"""The ports the gateway needs from the outside, declared by the gateway.

The dependency points inward. The application composes a gateway and hands it a store; the gateway
knows nothing about SQLAlchemy, about the API's session lifecycle or about the database at all. If
the arrow pointed the other way, ``iacode_model_gateway`` would import ``iacode_api``, and the first
consumer that wanted the gateway without the web application would be stuck with FastAPI in its
dependency tree.

Time and randomness are ports for a different reason: a backoff test that waits four seconds is a
test that gets deleted. ``Clock`` and ``Jitter`` let the resilience suite run a ten-minute cooldown
in microseconds while exercising the same code path production runs.
"""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from iacode_model_gateway.contracts import ModelDescriptor

__all__ = [
    "CatalogStore",
    "Clock",
    "Jitter",
    "ModelCallRecord",
    "ModelCallStore",
    "ProviderRecord",
    "RealClock",
    "RealJitter",
    "SyncOutcome",
]


@dataclass(frozen=True)
class ProviderRecord:
    """A provider as the store keeps it.

    There is no credential field, and that is not an omission. `docs/GATE-1-CHECKLIST.md` row 5.2
    requires the registry to hold operational metadata only; a nullable secret column is a place a
    secret eventually lands.
    """

    provider_id: str
    display_name: str
    adapter: str
    enabled: bool
    healthy: bool | None = None
    last_health_check: datetime | None = None
    last_sync: datetime | None = None
    model_count: int = 0
    detail: str | None = None


@dataclass(frozen=True)
class SyncOutcome:
    """What one catalog synchronization changed."""

    provider_id: str
    added: int = 0
    updated: int = 0
    deactivated: int = 0
    unchanged: int = 0
    errors: tuple[str, ...] = ()

    @property
    def total(self) -> int:
        return self.added + self.updated + self.deactivated + self.unchanged


@dataclass(frozen=True)
class ModelCallRecord:
    """The operational facts of one provider attempt.

    Deliberately no prompt, no messages and no completion. `docs/GATE-1-CHECKLIST.md` row 10.4
    keeps content out of this record by default, and the shape of the record is what enforces it:
    a field that does not exist cannot be filled in by accident.
    """

    request_id: str
    provider_id: str
    model_id: str | None
    endpoint: str | None
    route: str | None
    purpose: str
    status: str
    succeeded: bool
    started_at: datetime
    finished_at: datetime
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    reasoning_tokens: int | None = None
    cost: float | None = None
    error_type: str | None = None
    retry_count: int = 0
    fallback_count: int = 0
    correlation_id: str | None = None
    request_fingerprint: str | None = None


@runtime_checkable
class CatalogStore(Protocol):
    """Where provider and model metadata lives."""

    async def list_providers(self) -> list[ProviderRecord]:
        """Every known provider with its operational state."""

    async def upsert_provider(self, record: ProviderRecord) -> None:
        """Create or update a provider's operational state."""

    async def list_models(self, *, provider_id: str | None = None,
                          active: bool | None = None) -> list[ModelDescriptor]:
        """The catalog, optionally narrowed by provider and by active state."""

    async def replace_provider_models(self, provider_id: str,
                                      models: list[ModelDescriptor]) -> SyncOutcome:
        """Apply a complete, already-validated catalog for one provider, atomically.

        The contract is deliberately "replace", not "upsert each": the caller has validated the
        whole answer before calling, and a store that applied models one at a time could leave a
        half-synchronized catalog behind when the eleventh row failed. A model absent from
        ``models`` is deactivated, never deleted, because rows in ``model_calls`` still point at it.
        """


@runtime_checkable
class ModelCallStore(Protocol):
    """Where the record of an attempt lives."""

    async def record(self, call: ModelCallRecord) -> None:
        """Persist one attempt. Must not raise into the caller's result path."""


@runtime_checkable
class Clock(Protocol):
    """Time, as an injectable dependency."""

    def now(self) -> datetime: ...

    def monotonic(self) -> float: ...

    async def sleep(self, seconds: float) -> None: ...


@runtime_checkable
class Jitter(Protocol):
    """Randomness for backoff, as an injectable dependency."""

    def uniform(self, low: float, high: float) -> float: ...


class RealClock:
    """The clock a running process uses."""

    def now(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return time.monotonic()

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)


class RealJitter:
    """Randomness a running process uses.

    ``random`` rather than ``secrets``: this decides how long to wait before retrying, not anything
    an adversary gains from predicting. Using a cryptographic source here would suggest otherwise.
    """

    def uniform(self, low: float, high: float) -> float:
        return random.uniform(low, high)
