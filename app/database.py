"""
Database connection setup — Postgres (via SQLAlchemy async) and Neo4j (async driver).

Both connections are created once at startup and torn down at shutdown via
FastAPI's lifespan context manager (see main.py).
"""

from collections.abc import AsyncGenerator

from neo4j import AsyncDriver, AsyncGraphDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Postgres ─────────────────────────────────────────────────────────────────

def _make_engine():
    """
    Deferred engine creation so the module can be imported without a DATABASE_URL
    present (e.g. during tests that don't touch Postgres).
    """
    if not settings.database_url:
        return None
    return create_async_engine(
        settings.database_url,
        echo=settings.app_debug,
        pool_pre_ping=True,
    )


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
) if engine else None


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a database session and closes it when done."""
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured.")
    async with AsyncSessionLocal() as session:
        yield session


# ── Neo4j ────────────────────────────────────────────────────────────────────

_neo4j_driver: AsyncDriver | None = None


def get_neo4j_driver() -> AsyncDriver:
    """
    Return the shared Neo4j async driver, creating it on first use.

    Lazily initialised (mirroring the SQLAlchemy engine above) so importing this
    module never opens a connection. The driver is hosting-agnostic: it accepts
    any URI scheme (``bolt://``, ``neo4j://``, ``neo4j+s://``) unchanged, so the
    same code works with Neo4j Sandbox, AuraDB, or a self-hosted instance.

    Note: constructing the driver does not connect — the first query does.
    """
    global _neo4j_driver
    if _neo4j_driver is None:
        if not settings.neo4j_uri:
            raise RuntimeError("NEO4J_URI is not configured.")
        _neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
    return _neo4j_driver


async def close_neo4j_driver() -> None:
    """Close the shared Neo4j driver, if one was created. Safe to call anytime."""
    global _neo4j_driver
    if _neo4j_driver is not None:
        await _neo4j_driver.close()
        _neo4j_driver = None
