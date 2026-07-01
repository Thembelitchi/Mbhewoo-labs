"""
Paper model — a scholarly work in the research corpus.

The central entity of the Mbhewoo Labs "research world": the papers whose
findings forecasters predict will (or won't) replicate. Canonical identifiers
are the DOI and OpenAlex iD (both nullable — not every work has a DOI). Papers
link to Researchers (authorship), Domains, and Concepts, and carry retraction
signals from Retraction Watch.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import paper_concept, paper_domain, paper_researcher
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.concept import Concept
    from app.models.domain import Domain
    from app.models.researcher import Researcher


class Paper(TimestampMixin, Base):
    """A scholarly work, identified canonically by DOI and/or OpenAlex iD."""

    __tablename__ = "papers"
    __table_args__ = (
        Index("ix_papers_doi", "doi", unique=True),
        Index("ix_papers_openalex_id", "openalex_id", unique=True),
        Index("ix_papers_publication_year", "publication_year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    openalex_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # Denormalised from publication_date for fast year-range queries.
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    journal_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    venue_issn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # green/gold/hybrid/closed
    open_access_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    citation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Retraction signals (Retraction Watch).
    is_retracted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    retraction_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    retraction_source_url: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True
    )

    # Which ingestion source populated this row (openalex/crossref/manual).
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships.
    authors: Mapped[list["Researcher"]] = relationship(
        secondary=paper_researcher,
        back_populates="papers",
    )
    domains: Mapped[list["Domain"]] = relationship(
        secondary=paper_domain,
        back_populates="papers",
    )
    concepts: Mapped[list["Concept"]] = relationship(
        secondary=paper_concept,
        back_populates="papers",
    )

    def __repr__(self) -> str:
        return (
            f"<Paper id={self.id} doi={self.doi!r} title={self.title!r} "
            f"year={self.publication_year}>"
        )
