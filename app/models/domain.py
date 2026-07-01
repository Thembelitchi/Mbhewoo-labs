"""
Domain model — a research domain the platform tracks.

Part of the Mbhewoo Labs research corpus. The five core MVP domains from
CLAUDE.md (HIV/TB vaccines, computational biology, biotech/pharma,
bioprocessing, bioeconomy) are marked with ``is_core_mvp = True``; the model is
open to additional domains beyond the MVP five.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import paper_domain
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.paper import Paper


class Domain(TimestampMixin, Base):
    """A research domain, identified by a URL-friendly slug."""

    __tablename__ = "domains"
    __table_args__ = (Index("ix_domains_slug", "slug", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_core_mvp: Mapped[bool] = mapped_column(default=False, nullable=False)

    papers: Mapped[list["Paper"]] = relationship(
        secondary=paper_domain,
        back_populates="domains",
    )

    def __repr__(self) -> str:
        return (
            f"<Domain id={self.id} slug={self.slug!r} "
            f"is_core_mvp={self.is_core_mvp}>"
        )
