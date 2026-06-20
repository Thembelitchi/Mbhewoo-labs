from collections.abc import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from neo4j import GraphDatabase, Driver

from app.config import settings

# --- SQLAlchemy Setup ---
# Create async engine for PostgreSQL (using asyncpg)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "dev" else False,
    future=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base class for models
Base = declarative_base()


# Dependency injection helper for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a new SQLAlchemy AsyncSession.
    Ensures safe automatic closure when the request lifecycle ends.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- Neo4j Setup ---
# Instantiate the Neo4j Driver (Graph Database)
# Driver objects handle connection pools internally and should be instantiated globally
neo4j_driver: Driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
)


def get_neo4j() -> Generator[Driver, None, None]:
    """
    Get the Neo4j global driver instance.
    The driver is a thread-safe singleton that coordinates connection pools.
    """
    try:
        yield neo4j_driver
    finally:
        # Usually we keep the driver open for the app context,
        # but yield allows endpoint injection or overrides
        pass
