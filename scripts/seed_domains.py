"""
scripts/seed_domains.py — seed the five core MVP domains.

Inserts the five MVP research domains from CLAUDE.md into Postgres (as Domain
rows) and mirrors them into Neo4j (as :Domain nodes), all marked
``is_core_mvp = True``.

Idempotent by design:
- Postgres uses INSERT ... ON CONFLICT (slug) DO UPDATE, so re-running updates
  rather than duplicating.
- Neo4j uses MERGE on ``slug``, so nodes are created once and updated after.

Run from the project root:

    python scripts/seed_domains.py
"""

from __future__ import annotations

import asyncio

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config import settings
from app.database import (
    AsyncSessionLocal,
    close_neo4j_driver,
    engine,
    get_neo4j_driver,
)
from app.models import Domain

# (slug, display_name) for the five core MVP domains (CLAUDE.md → Domains).
MVP_DOMAINS: list[tuple[str, str]] = [
    ("hiv-tb-vaccines", "HIV and TB Vaccines & Prevention"),
    ("computational-biology", "Computational Biology & Bioinformatics"),
    ("biotech-pharma", "Biotech & Pharmaceutical Sciences"),
    ("bioprocessing", "Bioprocessing"),
    ("bioeconomy-translational", "Bioeconomy & Translational Research"),
]


async def seed_postgres() -> int:
    """Upsert the MVP domains into Postgres. Returns the number processed."""
    if AsyncSessionLocal is None:
        print("✗ DATABASE_URL is not set — skipping Postgres seeding.")
        return 0

    async with AsyncSessionLocal() as session:
        for slug, display_name in MVP_DOMAINS:
            statement = pg_insert(Domain).values(
                slug=slug, display_name=display_name, is_core_mvp=True
            )
            statement = statement.on_conflict_do_update(
                index_elements=["slug"],
                set_={"display_name": display_name, "is_core_mvp": True},
            )
            await session.execute(statement)
        await session.commit()

    print(f"✓ Postgres: upserted {len(MVP_DOMAINS)} core MVP domains.")
    return len(MVP_DOMAINS)


async def seed_neo4j() -> int:
    """MERGE the MVP domains as :Domain nodes in Neo4j. Returns count processed."""
    if not settings.neo4j_uri:
        print("✗ NEO4J_URI is not set — skipping Neo4j seeding.")
        return 0

    driver = get_neo4j_driver()
    try:
        async with driver.session(database=settings.neo4j_database) as session:
            for slug, display_name in MVP_DOMAINS:
                await session.run(
                    "MERGE (d:Domain {slug: $slug}) "
                    "SET d.display_name = $display_name, d.is_core_mvp = true",
                    slug=slug,
                    display_name=display_name,
                )
    finally:
        await close_neo4j_driver()

    print(f"✓ Neo4j: merged {len(MVP_DOMAINS)} :Domain nodes.")
    return len(MVP_DOMAINS)


async def main() -> None:
    """Seed both stores, then release connections."""
    try:
        await seed_postgres()
        await seed_neo4j()
    finally:
        if engine is not None:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
