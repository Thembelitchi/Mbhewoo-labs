"""
Association tables for many-to-many relationships in the research corpus.

These are Core ``Table`` objects (not ORM classes) because the relationships
between corpus entities are edges, some carrying a little payload (author
position, concept score, affiliation dates). They model the "research world"
graph in Postgres; the same edges are mirrored into Neo4j.

All foreign keys cascade on delete so removing a corpus entity cleanly removes
its edges. All indexes and constraints are explicitly named.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    Table,
    UniqueConstraint,
    Uuid,
)

from app.models.base import Base

# Paper ↔ Researcher (authorship). Carries the author's ordinal position and
# whether they are the corresponding author.
paper_researcher = Table(
    "paper_researcher",
    Base.metadata,
    Column(
        "paper_id",
        Uuid,
        ForeignKey("papers.id", ondelete="CASCADE", name="fk_paper_researcher_paper"),
        primary_key=True,
    ),
    Column(
        "researcher_id",
        Uuid,
        ForeignKey(
            "researchers.id",
            ondelete="CASCADE",
            name="fk_paper_researcher_researcher",
        ),
        primary_key=True,
    ),
    Column("author_position", Integer, nullable=True),
    Column("is_corresponding", Boolean, nullable=False, default=False),
)

# Paper ↔ Domain (which MVP/other domains a paper belongs to).
paper_domain = Table(
    "paper_domain",
    Base.metadata,
    Column(
        "paper_id",
        Uuid,
        ForeignKey("papers.id", ondelete="CASCADE", name="fk_paper_domain_paper"),
        primary_key=True,
    ),
    Column(
        "domain_id",
        Uuid,
        ForeignKey("domains.id", ondelete="CASCADE", name="fk_paper_domain_domain"),
        primary_key=True,
    ),
)

# Paper ↔ Concept (OpenAlex concept tagging, with a relevance score in [0, 1]).
# ``score`` is a relevance weight, not a countable quantity, so a float is fine.
paper_concept = Table(
    "paper_concept",
    Base.metadata,
    Column(
        "paper_id",
        Uuid,
        ForeignKey("papers.id", ondelete="CASCADE", name="fk_paper_concept_paper"),
        primary_key=True,
    ),
    Column(
        "concept_id",
        Uuid,
        ForeignKey("concepts.id", ondelete="CASCADE", name="fk_paper_concept_concept"),
        primary_key=True,
    ),
    Column("score", Float, nullable=True),
)

# Researcher ↔ Institution (affiliation history, with dates and a current flag).
researcher_institution = Table(
    "researcher_institution",
    Base.metadata,
    Column(
        "researcher_id",
        Uuid,
        ForeignKey(
            "researchers.id",
            ondelete="CASCADE",
            name="fk_researcher_institution_researcher",
        ),
        primary_key=True,
    ),
    Column(
        "institution_id",
        Uuid,
        ForeignKey(
            "institutions.id",
            ondelete="CASCADE",
            name="fk_researcher_institution_institution",
        ),
        primary_key=True,
    ),
    Column("from_date", Date, nullable=True),
    Column("to_date", Date, nullable=True),
    Column("is_current", Boolean, nullable=False, default=False),
    UniqueConstraint(
        "researcher_id",
        "institution_id",
        "from_date",
        name="uq_researcher_institution_period",
    ),
)
