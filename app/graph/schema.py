"""
Neo4j graph schema — constraints and indexes for the research corpus.

Mirrors the Postgres corpus (papers, researchers, institutions, trials,
domains, concepts) as a property graph. Postgres is the source of truth; Neo4j
holds the same entities as nodes so we can traverse authorship/affiliation/
citation edges cheaply (e.g. for conflict-of-interest checks).

``initialise_graph_schema()`` is idempotent: every statement uses
``IF NOT EXISTS``, so it can be run repeatedly and on every deploy safely.
"""

from __future__ import annotations

from neo4j import AsyncDriver

from app.config import settings
from app.database import get_neo4j_driver

# Uniqueness constraints on the canonical identifier of each node label. A
# uniqueness constraint also creates a backing index, so lookups by these
# properties are fast. (name, label, property)
UNIQUENESS_CONSTRAINTS: list[tuple[str, str, str]] = [
    ("paper_doi_unique", "Paper", "doi"),
    ("researcher_orcid_unique", "Researcher", "orcid"),
    ("institution_ror_unique", "Institution", "ror_id"),
    ("trial_pactr_unique", "Trial", "pactr_id"),
    ("domain_slug_unique", "Domain", "slug"),
    ("concept_openalex_unique", "Concept", "openalex_id"),
]

# Secondary indexes on frequently-queried, non-unique properties.
# (name, label, property)
PROPERTY_INDEXES: list[tuple[str, str, str]] = [
    # Alternate identifiers used during ingestion joins.
    ("paper_openalex_idx", "Paper", "openalex_id"),
    ("researcher_openalex_idx", "Researcher", "openalex_id"),
    ("institution_openalex_idx", "Institution", "openalex_id"),
    ("trial_nct_idx", "Trial", "nct_id"),
    # Common filters.
    ("paper_publication_year_idx", "Paper", "publication_year"),
    ("paper_is_retracted_idx", "Paper", "is_retracted"),
    ("institution_country_code_idx", "Institution", "country_code"),
    ("concept_level_idx", "Concept", "level"),
    ("domain_is_core_mvp_idx", "Domain", "is_core_mvp"),
    ("trial_status_idx", "Trial", "status"),
]


def _constraint_statement(name: str, label: str, prop: str) -> str:
    return (
        f"CREATE CONSTRAINT {name} IF NOT EXISTS "
        f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
    )


def _index_statement(name: str, label: str, prop: str) -> str:
    return f"CREATE INDEX {name} IF NOT EXISTS FOR (n:{label}) ON (n.{prop})"


async def initialise_graph_schema(driver: AsyncDriver | None = None) -> dict[str, int]:
    """
    Idempotently create all uniqueness constraints and property indexes.

    Uses the shared driver from ``app.database`` unless one is passed in (handy
    for tests). Returns a small summary of how many of each were applied.
    """
    driver = driver or get_neo4j_driver()

    async with driver.session(database=settings.neo4j_database) as session:
        for name, label, prop in UNIQUENESS_CONSTRAINTS:
            await session.run(_constraint_statement(name, label, prop))
        for name, label, prop in PROPERTY_INDEXES:
            await session.run(_index_statement(name, label, prop))

    return {
        "constraints": len(UNIQUENESS_CONSTRAINTS),
        "indexes": len(PROPERTY_INDEXES),
    }


async def list_graph_schema(driver: AsyncDriver | None = None) -> dict[str, list[str]]:
    """Return the names of constraints and indexes currently in the database."""
    driver = driver or get_neo4j_driver()

    async with driver.session(database=settings.neo4j_database) as session:
        constraints = [
            record["name"]
            async for record in await session.run("SHOW CONSTRAINTS YIELD name")
        ]
        indexes = [
            record["name"]
            async for record in await session.run("SHOW INDEXES YIELD name")
        ]

    return {"constraints": sorted(constraints), "indexes": sorted(indexes)}
