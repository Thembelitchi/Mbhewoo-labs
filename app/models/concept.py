"""
Concept model — an OpenAlex concept in the research corpus.

Part of the Mbhewoo Labs "research world". Concepts are OpenAlex's hierarchical
subject tags (levels 0–5), used to characterise what a paper is about. The
hierarchy is self-referential via ``parent_concept_id``. Concepts tag Papers
through the ``paper_concept`` association (with a relevance score).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import paper_concept
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.paper import Paper


class Concept(TimestampMixin, Base):
    """An OpenAlex concept node, hierarchical and self-referential."""

    __tablename__ = "concepts"
    __table_args__ = (Index("ix_concepts_openalex_id", "openalex_id", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    openalex_id: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    # OpenAlex concept hierarchy level, 0 (broadest) to 5 (most specific).
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    works_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent_concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL", name="fk_concepts_parent"),
        nullable=True,
    )

    # Self-referential hierarchy.
    parent: Mapped[Optional["Concept"]] = relationship(
        "Concept", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Concept"]] = relationship(
        "Concept", back_populates="parent"
    )

    papers: Mapped[list["Paper"]] = relationship(
        secondary=paper_concept,
        back_populates="concepts",
    )

    def __repr__(self) -> str:
        return (
            f"<Concept id={self.id} openalex_id={self.openalex_id!r} "
            f"display_name={self.display_name!r} level={self.level}>"
        )
