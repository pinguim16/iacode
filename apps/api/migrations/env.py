"""Alembic environment.

Two decisions worth stating.

**The URL comes from the application's own configuration.** ``alembic.ini`` carries no
``sqlalchemy.url``, so there is one place a database address is defined and no committed file can
hold a password.

**Migrations run synchronously.** The application uses ``asyncpg``; Alembic's autogenerate and its
offline mode are synchronous, and driving an async engine from them means running an event loop
inside a callback that does not expect one. The async URL is therefore translated to ``psycopg``
here. The two drivers speak the same protocol to the same server, so the schema they produce is
identical, and the migration process is short-lived and single-threaded, which is exactly the shape
a synchronous driver is good at.
"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

SOURCE = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from iacode_api.config import get_settings
from iacode_api.db import (
    models,  # noqa: F401  (imported for its side effect: table registration)
)
from iacode_api.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_url() -> str:
    """The configured database URL with a synchronous driver."""
    return get_settings().database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)


def run_migrations_offline() -> None:
    context.configure(
        url=_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_sync_url(), poolclass=pool.NullPool, future=True)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
