"""The asynchronous SQLAlchemy engine and its session factory.

One engine per process, created at startup and disposed at shutdown. Creating an engine per
request would open a connection pool per request, which is the opposite of what a pool is for.

The pool is small by default (five connections, five overflow). A local Foundation talks to one
PostgreSQL container, and an oversized pool hides connection leaks instead of surfacing them: with
ten permitted connections a leak exhausts the pool in seconds and shows up in a test, while with a
hundred it shows up in production months later.

``pool_pre_ping`` is on. The stack is restarted constantly during development, and a pooled
connection to a database container that has gone away fails on first use with an error that looks
like a bug in the query. One round trip per checkout is worth not debugging that.

**The parameters are values, not a settings object.** Gate 1 built this around the API's
``Settings`` class, which made the engine unusable to the worker without importing the web
application's
configuration model. Two processes need the same engine and have different configuration shapes,
so the shared thing takes the four numbers it actually reads and each process passes its own.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

__all__ = [
    "create_engine",
    "create_session_factory",
    "ping",
    "session_scope",
]


def create_engine(
    url: str,
    *,
    pool_size: int = 5,
    max_overflow: int = 5,
    connect_timeout_seconds: float = 10.0,
) -> AsyncEngine:
    """Build the engine. It connects lazily, so this cannot fail because PostgreSQL is down."""
    return create_async_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"timeout": connect_timeout_seconds},
        echo=False,
        future=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )


@asynccontextmanager
async def session_scope(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """A unit of work: commit on success, roll back on any exception, always close.

    The rollback is not decoration. Without it a failed request leaves its session holding an
    aborted transaction, and the next checkout of that pooled connection fails with
    ``InFailedSQLTransaction`` — an error about the previous request, raised inside the next one.
    """
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise


async def ping(engine: AsyncEngine) -> None:
    """Prove the database answers. Raises when it does not, which is what readiness needs.

    ``SELECT 1`` is the whole probe on purpose: a readiness check that queries a table couples
    liveness to that table's existence, so a pending migration would report the database as down.
    """
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
