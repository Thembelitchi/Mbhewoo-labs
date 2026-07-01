"""
Researcher model — an author in the research corpus.

Part of the Mbhewoo Labs "research world". A Researcher here is the *subject* of
scholarship (an author of papers/trials), distinct from a platform Forecaster
who places predictions. Canonical identifier is the ORCID iD; OpenAlex iD is
kept for ingestion linkage. Researchers link to Institutions via an affiliation
history and to Papers via authorship.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import paper_researcher, researcher_institution
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.paper import Paper


class Researcher(TimestampMixin, Base):
    """An author of scholarly work, identified canonically by ORCID."""

    __tablename__ = "researchers"
    __table_args__ = (
        Index("ix_researchers_orcid", "orcid", unique=True),
        Index("ix_researchers_openalex_id", "openalex_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    orcid: Mapped[Optional[str]] = mapped_column(String(19), nullable=True)
    openalex_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    given_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    family_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    current_affiliation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "institutions.id",
            ondelete="SET NULL",
            name="fk_researchers_current_affiliation",
        ),
        nullable=True,
    )

    # Bibliometrics — all whole counts (never floats).
    h_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    works_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_synthetic: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships.
    current_affiliation: Mapped[Optional["Institution"]] = relationship(
        "Institution", foreign_keys=[current_affiliation_id]
    )
    institutions: Mapped[list["Institution"]] = relationship(
        secondary=researcher_institution,
        back_populates="researchers",
    )
    papers: Mapped[list["Paper"]] = relationship(
        secondary=paper_researcher,
        back_populates="authors",
    )

    def __repr__(self) -> str:
        return (
            f"<Researcher id={self.id} orcid={self.orcid!r} "
            f"display_name={self.display_name!r}>"
        )
