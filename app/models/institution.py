"""
Institution model — a research organisation (university, hospital, company…).

Part of the Mbhewoo Labs research corpus (the "research world"). Institutions
anchor researchers geographically and organisationally, which matters for the
graph-powered conflict-of-interest checks and for African-research visibility.
Canonical identifier is the ROR iD; OpenAlex iD is kept for ingestion linkage.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import researcher_institution
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.researcher import Researcher


class Institution(TimestampMixin, Base):
    """A research organisation, identified canonically by its ROR iD."""

    __tablename__ = "institutions"
    __table_args__ = (
        Index("ix_institutions_ror_id", "ror_id", unique=True),
        Index("ix_institutions_openalex_id", "openalex_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    ror_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    openalex_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    country_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # education/healthcare/government/nonprofit/company/facility/archive/other
    institution_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Affiliation history — researchers who are or were affiliated here.
    researchers: Mapped[list["Researcher"]] = relationship(
        secondary=researcher_institution,
        back_populates="institutions",
    )

    def __repr__(self) -> str:
        return (
            f"<Institution id={self.id} ror_id={self.ror_id!r} "
            f"display_name={self.display_name!r} country={self.country_code!r}>"
        )
