"""The API's binding between its configuration and the shared engine.

``packages/persistence`` owns the engine, the session factory, the unit of work and the probe. It
takes values rather than a settings object, so the worker can use it without importing the web
application's configuration model. This module is the one place that knows which of the API's
settings feed it.

Re-exporting :func:`session_scope` and :func:`ping` keeps the application's call sites reading
``db_engine.session_scope(...)`` — the name the dependency layer, the readiness probe and the
existing suites already use — while there is exactly one implementation behind it.
"""

from __future__ import annotations

from iacode_persistence.engine import create_engine as _create_engine
from iacode_persistence.engine import (
    create_session_factory,
    ping,
    session_scope,
)
from sqlalchemy.ext.asyncio import AsyncEngine

from iacode_api.config import Settings

__all__ = [
    "create_engine",
    "create_session_factory",
    "ping",
    "session_scope",
]


def create_engine(settings: Settings) -> AsyncEngine:
    """Build the engine from the application's typed configuration.

    Written out field by field rather than by handing the settings object across the boundary, so a
    key renamed on one side is an error here instead of a default that silently takes over.
    """
    return _create_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        connect_timeout_seconds=settings.database_connect_timeout_seconds,
    )
