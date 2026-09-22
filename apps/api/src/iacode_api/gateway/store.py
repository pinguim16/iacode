"""The database behind the gateway's ports.

The gateway declares what it needs — :class:`~iacode_model_gateway.ports.CatalogStore` and
:class:`~iacode_model_gateway.ports.ModelCallStore` — and this module is the application's answer in
SQLAlchemy. The dependency points this way on purpose: the gateway has no idea a database exists,
and the first consumer that wants it without the web application does not inherit one.

Each store owns a session factory and opens a short session per operation, rather than borrowing the
request's session. A streaming response outlives the handler that started it, and a store bound to
the request's unit of work would be writing into a session that had already been closed under it.

``replace_provider_models`` is the only interesting one. It is a single transaction by contract,
because a catalog applied model-by-model can be left half-applied, and the operator is then holding
a catalog that is neither the old one nor the new one. A model absent from the incoming set is
deactivated rather than deleted: ``model_calls`` rows point at it, and deleting it would turn
recorded history into a dangling reference.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from iacode_model_gateway.contracts import (
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    ModelDescriptor,
    ModelRef,
    ReasoningEffort,
)
from iacode_model_gateway.ports import ModelCallRecord, ProviderRecord, SyncOutcome
from iacode_persistence.models import Model, ModelCall, Provider
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

__all__ = ["SqlCatalogStore", "SqlModelCallStore", "descriptor_from_row"]


def _enum_list(values: Any, factory) -> tuple:
    """Read a JSONB list back into a tuple of enum members, dropping anything unrecognised.

    Dropping rather than raising: a value written by a newer revision of the gateway must not make
    an older one unable to read its own catalog, and the alternative — refusing to load — takes the
    whole catalog offline because of one unfamiliar string.
    """
    if not isinstance(values, list):
        return ()
    result = []
    for value in values:
        try:
            member = factory(value)
        except ValueError:
            continue
        if member not in result:
            result.append(member)
    return tuple(result)


def descriptor_from_row(row: Model, provider_slug: str) -> ModelDescriptor:
    """Turn one ``models`` row into the catalog descriptor the gateway reads."""
    capabilities: dict[Capability, CapabilityState] = {}
    for key, value in (row.capabilities or {}).items():
        try:
            capabilities[Capability(key)] = CapabilityState(value)
        except ValueError:
            continue
    provenance: dict[Capability, CapabilityProvenance] = {}
    for key, value in (row.capability_provenance or {}).items():
        try:
            provenance[Capability(key)] = CapabilityProvenance(value)
        except ValueError:
            continue
    return ModelDescriptor(
        ref=ModelRef(provider_id=provider_slug, model_id=row.slug),
        display_name=row.display_name,
        family=row.family,
        context_window=row.context_window,
        max_output_tokens=row.max_output_tokens,
        supported_endpoints=_enum_list(row.supported_endpoints, Endpoint),
        capabilities=capabilities,
        capability_provenance=provenance,
        reasoning_levels=_enum_list(row.reasoning_levels, ReasoningEffort),
        active=row.active,
        raw_metadata=row.raw_metadata or {},
        synced_at=row.synced_at,
    )


def _apply_descriptor(row: Model, descriptor: ModelDescriptor) -> None:
    row.display_name = descriptor.display_name
    row.family = descriptor.family
    row.context_window = descriptor.context_window
    row.max_output_tokens = descriptor.max_output_tokens
    row.supported_endpoints = [str(item) for item in descriptor.supported_endpoints]
    row.capabilities = {str(key): str(value) for key, value in descriptor.capabilities.items()}
    row.capability_provenance = {
        str(key): str(value) for key, value in descriptor.capability_provenance.items()}
    row.reasoning_levels = [str(item) for item in descriptor.reasoning_levels]
    row.active = descriptor.active
    row.raw_metadata = descriptor.raw_metadata
    row.synced_at = descriptor.synced_at


def _catalog_identity(row: Model) -> tuple:
    """The part of a row that decides whether a synchronisation changed anything.

    ``synced_at`` is excluded: it changes on every run, and including it would report every model as
    updated every time, which would make idempotence unobservable.
    """
    return (
        row.display_name, row.family, row.context_window, row.max_output_tokens,
        tuple(row.supported_endpoints or []), tuple(sorted((row.capabilities or {}).items())),
        tuple(sorted((row.capability_provenance or {}).items())),
        tuple(row.reasoning_levels or []), row.active, row.raw_metadata,
    )


class SqlCatalogStore:
    """Providers and models, in PostgreSQL."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def list_providers(self) -> list[ProviderRecord]:
        async with self._sessions() as session:
            rows = (await session.execute(select(Provider).order_by(Provider.slug))).scalars().all()
            return [
                ProviderRecord(
                    provider_id=row.slug,
                    display_name=row.name,
                    adapter=row.adapter or row.kind,
                    enabled=row.enabled,
                    healthy=row.healthy,
                    last_health_check=row.last_health_check,
                    last_sync=row.last_sync,
                    model_count=row.model_count,
                    detail=row.detail,
                )
                for row in rows
            ]

    async def upsert_provider(self, record: ProviderRecord) -> None:
        async with self._sessions() as session, session.begin():
            row = await self._provider_row(session, record.provider_id)
            if row is None:
                row = Provider(slug=record.provider_id, name=record.display_name, kind="http-api")
                session.add(row)
            row.name = record.display_name
            row.adapter = record.adapter
            row.enabled = record.enabled
            row.healthy = record.healthy
            if record.last_health_check is not None:
                row.last_health_check = record.last_health_check
            if record.last_sync is not None:
                row.last_sync = record.last_sync
            row.model_count = record.model_count
            row.detail = record.detail

    async def list_models(self, *, provider_id: str | None = None,
                          active: bool | None = None) -> list[ModelDescriptor]:
        async with self._sessions() as session:
            statement = select(Model, Provider.slug).join(
                Provider, Model.provider_id == Provider.id)
            if provider_id is not None:
                statement = statement.where(Provider.slug == provider_id)
            if active is not None:
                statement = statement.where(Model.active.is_(active))
            statement = statement.order_by(Provider.slug, Model.slug)
            rows = (await session.execute(statement)).all()
            return [descriptor_from_row(model, slug) for model, slug in rows]

    async def replace_provider_models(self, provider_id: str,
                                      models: list[ModelDescriptor]) -> SyncOutcome:
        """Apply a complete catalog for one provider in one transaction."""
        added = updated = unchanged = deactivated = 0
        async with self._sessions() as session, session.begin():
            provider = await self._provider_row(session, provider_id)
            if provider is None:
                provider = Provider(slug=provider_id, name=provider_id, kind="http-api")
                session.add(provider)
                await session.flush()

            existing = {
                row.slug: row
                for row in (await session.execute(
                    select(Model).where(Model.provider_id == provider.id))).scalars().all()
            }
            incoming = {descriptor.ref.model_id: descriptor for descriptor in models}

            for model_id, descriptor in incoming.items():
                row = existing.get(model_id)
                if row is None:
                    row = Model(provider_id=provider.id, slug=model_id,
                                display_name=descriptor.display_name)
                    session.add(row)
                    _apply_descriptor(row, descriptor)
                    added += 1
                    continue
                before = _catalog_identity(row)
                _apply_descriptor(row, descriptor)
                if _catalog_identity(row) == before:
                    unchanged += 1
                else:
                    updated += 1

            for model_id, row in existing.items():
                if model_id in incoming or not row.active:
                    continue
                row.active = False
                deactivated += 1

        return SyncOutcome(provider_id=provider_id, added=added, updated=updated,
                           deactivated=deactivated, unchanged=unchanged)

    @staticmethod
    async def _provider_row(session: AsyncSession, provider_id: str) -> Provider | None:
        return (await session.execute(
            select(Provider).where(Provider.slug == provider_id))).scalars().first()


class SqlModelCallStore:
    """The append-only record of every attempt, in PostgreSQL."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def record(self, call: ModelCallRecord) -> None:
        async with self._sessions() as session, session.begin():
            provider = (await session.execute(
                select(Provider).where(Provider.slug == call.provider_id))).scalars().first()
            model_row_id = None
            if provider is not None and call.model_id is not None:
                model_row_id = (await session.execute(
                    select(Model.id).where(Model.provider_id == provider.id,
                                           Model.slug == call.model_id))).scalars().first()
            session.add(ModelCall(
                model_id=model_row_id,
                provider_id=provider.id if provider is not None else None,
                request_id=call.request_id,
                correlation_id=call.correlation_id,
                request_fingerprint=call.request_fingerprint,
                endpoint=call.endpoint,
                route=call.route,
                purpose=call.purpose,
                status=call.status,
                started_at=call.started_at,
                finished_at=call.finished_at,
                input_tokens=call.input_tokens,
                output_tokens=call.output_tokens,
                cached_input_tokens=call.cached_input_tokens,
                reasoning_tokens=call.reasoning_tokens,
                cost=Decimal(str(call.cost)) if call.cost is not None else None,
                latency_ms=call.latency_ms,
                retry_count=call.retry_count,
                fallback_count=call.fallback_count,
                succeeded=call.succeeded,
                error_code=call.error_type,
            ))
