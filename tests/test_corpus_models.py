"""
Async tests for the research-corpus models (Step 6).

Covers, for each model: creation with minimum required fields, creation with
all fields, and the unique constraints on canonical identifiers. Also covers the
association tables (paper↔researcher, paper↔domain, paper↔concept, and
researcher↔institution) including their payload columns.

Run with pytest (asyncio_mode=auto); uses the async in-memory db_session
fixture from conftest.py.
"""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Concept,
    Domain,
    Institution,
    Paper,
    Researcher,
    Trial,
)
from app.models.associations import (
    paper_concept,
    paper_researcher,
    researcher_institution,
)


# ── Minimum-required-field creation ──────────────────────────────────────────


async def test_paper_minimum_fields(db_session: AsyncSession) -> None:
    paper = Paper(title="A replication study of X", source="openalex")
    db_session.add(paper)
    await db_session.commit()
    await db_session.refresh(paper)

    assert paper.id is not None
    assert paper.citation_count == 0      # default
    assert paper.is_retracted is False    # default
    assert paper.is_synthetic is False    # default
    assert paper.created_at is not None
    assert paper.doi is None              # nullable


async def test_researcher_minimum_fields(db_session: AsyncSession) -> None:
    researcher = Researcher(display_name="Dr Nomsa Dlamini")
    db_session.add(researcher)
    await db_session.commit()
    await db_session.refresh(researcher)

    assert researcher.id is not None
    assert researcher.works_count == 0
    assert researcher.cited_by_count == 0
    assert researcher.is_synthetic is False


async def test_institution_minimum_fields(db_session: AsyncSession) -> None:
    institution = Institution(display_name="University of the Witwatersrand")
    db_session.add(institution)
    await db_session.commit()
    await db_session.refresh(institution)

    assert institution.id is not None
    assert institution.is_synthetic is False


async def test_domain_minimum_fields(db_session: AsyncSession) -> None:
    domain = Domain(slug="hiv-tb-vaccines", display_name="HIV and TB Vaccines & Prevention")
    db_session.add(domain)
    await db_session.commit()
    await db_session.refresh(domain)

    assert domain.id is not None
    assert domain.is_core_mvp is False


async def test_concept_minimum_fields(db_session: AsyncSession) -> None:
    concept = Concept(openalex_id="C71924100", display_name="Medicine", level=0)
    db_session.add(concept)
    await db_session.commit()
    await db_session.refresh(concept)

    assert concept.id is not None
    assert concept.works_count == 0
    assert concept.parent_concept_id is None


async def test_trial_minimum_fields(db_session: AsyncSession) -> None:
    trial = Trial(title="A phase III TB vaccine trial", source="pactr")
    db_session.add(trial)
    await db_session.commit()
    await db_session.refresh(trial)

    assert trial.id is not None
    assert trial.is_synthetic is False


# ── All-field creation ───────────────────────────────────────────────────────


async def test_paper_all_fields(db_session: AsyncSession) -> None:
    paper = Paper(
        doi="10.1000/abc123",
        openalex_id="W123",
        title="Full paper",
        abstract="An abstract.",
        publication_date=date(2024, 1, 15),
        publication_year=2024,
        journal_name="Nature",
        venue_issn="0028-0836",
        open_access_status="gold",
        citation_count=42,
        is_retracted=True,
        retraction_date=date(2025, 6, 1),
        retraction_source_url="https://retractionwatch.com/xyz",
        source="crossref",
        is_synthetic=True,
    )
    db_session.add(paper)
    await db_session.commit()
    await db_session.refresh(paper)

    assert paper.publication_year == 2024
    assert paper.citation_count == 42
    assert paper.is_retracted is True
    assert paper.is_synthetic is True


async def test_researcher_all_fields(db_session: AsyncSession) -> None:
    institution = Institution(display_name="SAMRC", ror_id="https://ror.org/00", country_code="ZA")
    db_session.add(institution)
    await db_session.flush()

    researcher = Researcher(
        orcid="0000-0002-1825-0097",
        openalex_id="A123",
        display_name="Dr Nomsa Dlamini",
        given_name="Nomsa",
        family_name="Dlamini",
        current_affiliation_id=institution.id,
        h_index=12,
        works_count=57,
        cited_by_count=1500,
        is_synthetic=True,
    )
    db_session.add(researcher)
    await db_session.commit()
    await db_session.refresh(researcher)

    assert researcher.current_affiliation_id == institution.id
    assert researcher.h_index == 12
    assert researcher.cited_by_count == 1500


# ── Unique constraints ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("factory_a", "factory_b"),
    [
        (
            lambda: Paper(doi="10.1/dup", title="One", source="openalex"),
            lambda: Paper(doi="10.1/dup", title="Two", source="openalex"),
        ),
        (
            lambda: Researcher(display_name="A", orcid="0000-0000-0000-0001"),
            lambda: Researcher(display_name="B", orcid="0000-0000-0000-0001"),
        ),
        (
            lambda: Institution(display_name="A", ror_id="https://ror.org/dup"),
            lambda: Institution(display_name="B", ror_id="https://ror.org/dup"),
        ),
        (
            lambda: Domain(slug="dup", display_name="A"),
            lambda: Domain(slug="dup", display_name="B"),
        ),
        (
            lambda: Concept(openalex_id="Cdup", display_name="A", level=1),
            lambda: Concept(openalex_id="Cdup", display_name="B", level=1),
        ),
        (
            lambda: Trial(title="A", source="pactr", pactr_id="PACTR-DUP"),
            lambda: Trial(title="B", source="pactr", pactr_id="PACTR-DUP"),
        ),
    ],
)
async def test_unique_constraint_violation(db_session, factory_a, factory_b) -> None:
    """Two rows sharing a canonical identifier must be rejected."""
    db_session.add(factory_a())
    await db_session.commit()

    db_session.add(factory_b())
    with pytest.raises(IntegrityError):
        await db_session.commit()


# ── Association tables ───────────────────────────────────────────────────────


async def test_paper_researcher_association(db_session: AsyncSession) -> None:
    paper = Paper(title="Co-authored work", source="openalex")
    researcher = Researcher(display_name="Dr A")
    paper.authors.append(researcher)
    db_session.add(paper)
    await db_session.commit()

    # Verify the edge from both directions.
    fetched = (
        await db_session.execute(
            select(Paper).options(selectinload(Paper.authors)).where(Paper.id == paper.id)
        )
    ).scalar_one()
    assert [r.id for r in fetched.authors] == [researcher.id]

    # Payload columns on the association row.
    await db_session.execute(
        insert(paper_researcher)
        .values(paper_id=paper.id, researcher_id=researcher.id, author_position=1, is_corresponding=True)
        .prefix_with("OR REPLACE")  # sqlite upsert of the composite-PK row
    )
    await db_session.commit()
    row = (
        await db_session.execute(
            select(paper_researcher.c.author_position, paper_researcher.c.is_corresponding).where(
                paper_researcher.c.paper_id == paper.id
            )
        )
    ).one()
    assert row.author_position == 1
    assert bool(row.is_corresponding) is True


async def test_paper_domain_association(db_session: AsyncSession) -> None:
    paper = Paper(title="Domain-tagged work", source="openalex")
    domain = Domain(slug="hiv-tb-vaccines", display_name="HIV and TB")
    paper.domains.append(domain)
    db_session.add(paper)
    await db_session.commit()

    fetched = (
        await db_session.execute(
            select(Paper).options(selectinload(Paper.domains)).where(Paper.id == paper.id)
        )
    ).scalar_one()
    assert [d.slug for d in fetched.domains] == ["hiv-tb-vaccines"]


async def test_paper_concept_association_with_score(db_session: AsyncSession) -> None:
    paper = Paper(title="Concept-tagged work", source="openalex")
    concept = Concept(openalex_id="C42", display_name="Virology", level=2)
    db_session.add_all([paper, concept])
    await db_session.flush()

    await db_session.execute(
        insert(paper_concept).values(paper_id=paper.id, concept_id=concept.id, score=0.87)
    )
    await db_session.commit()

    score = (
        await db_session.execute(
            select(paper_concept.c.score).where(
                paper_concept.c.paper_id == paper.id,
                paper_concept.c.concept_id == concept.id,
            )
        )
    ).scalar_one()
    assert score == pytest.approx(0.87)


async def test_researcher_institution_association(db_session: AsyncSession) -> None:
    researcher = Researcher(display_name="Dr A")
    institution = Institution(display_name="Wits RHI")
    db_session.add_all([researcher, institution])
    await db_session.flush()

    await db_session.execute(
        insert(researcher_institution).values(
            researcher_id=researcher.id,
            institution_id=institution.id,
            from_date=date(2020, 1, 1),
            to_date=None,
            is_current=True,
        )
    )
    await db_session.commit()

    row = (
        await db_session.execute(
            select(researcher_institution.c.is_current, researcher_institution.c.from_date).where(
                researcher_institution.c.researcher_id == researcher.id
            )
        )
    ).one()
    assert bool(row.is_current) is True
    assert row.from_date == date(2020, 1, 1)
