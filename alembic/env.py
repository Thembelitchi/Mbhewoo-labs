"""
Alembic migration environment (async).

Bridges Alembic's synchronous migration API to our async SQLAlchemy stack:

- The database URL comes from ``app/config.py`` (loaded from ``.env`` via
  pydantic-settings), so no credentials live in ``alembic.ini``.
- ``target_metadata`` is ``Base.metadata``; importing ``app.models`` registers
  every table so autogenerate can see the full schema.
- Online migrations run through an async engine, driving the sync migration
  context via ``connection.run_sync``.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.config import settings
from app.database import Base

# Importing the models package registers all tables on Base.metadata.
import app.models  # noqa: F401

# Alembic Config object — provides access to values in alembic.ini.
config = context.config

# Configure Python logging from the ini file, if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — emit SQL to a script without a DBAPI
    connection. Useful for generating a migration SQL file for review.
    """
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure the migration context on a live connection and run it."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    connectable = create_async_engine(settings.database_url, pool_pre_ping=True)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
