"""
Forecaster ORM model — a user who places predictions on the platform.

Implements the Forecaster concept from CLAUDE.md / the PRD: forecasters are
identified by a verified ORCID iD or an institutional email (at least one is
required, enforced by a DB check constraint), hold a whole-number balance of
Seeds (never a float), and carry a track-record tier.

Synthetic demo forecasters are tagged with ``is_synthetic = True`` so the entire
demo population can be removed cleanly before live launch.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# Starter endowment granted to every new forecaster (Seeds are integers).
STARTER_SEED_ENDOWMENT: int = 100


class ForecasterTier(str, enum.Enum):
    """
    Track-record tiers, ordered from newcomer to top expert.

    Tier is earned through resolved-market count and Brier accuracy (see
    CLAUDE.md), not by Seed balance. New forecasters start at ``seedling``.
    """

    seedling = "seedling"
    sapling = "sapling"
    rooted = "rooted"
    mfukula = "mfukula"
    marula = "marula"


class Forecaster(Base):
    """A registered forecaster who places predictions on markets."""

    __tablename__ = "forecasters"
    __table_args__ = (
        UniqueConstraint("orcid_id", name="uq_forecasters_orcid_id"),
        UniqueConstraint("institutional_email", name="uq_forecasters_institutional_email"),
        # Seeds must never go negative — a forecaster cannot spend what they lack.
        CheckConstraint("seeds_balance >= 0", name="ck_forecasters_seeds_non_negative"),
        # Defence in depth: at least one verified identity must be present.
        CheckConstraint(
            "orcid_id IS NOT NULL OR institutional_email IS NOT NULL",
            name="ck_forecasters_identity_present",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identity — an ORCID iD is 16 digits in four hyphen-separated groups
    # (e.g. "0000-0002-1825-0097"), so 19 characters including hyphens.
    orcid_id: Mapped[str | None] = mapped_column(String(19), nullable=True)
    institutional_email: Mapped[str | None] = mapped_column(String(320), nullable=True)

    display_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Seeds are whole numbers — integer column, never float. Defaults applied at
    # both the ORM layer (default) and the DB layer (server_default in the
    # migration) so direct SQL inserts still receive the starter endowment.
    seeds_balance: Mapped[int] = mapped_column(
        Integer, nullable=False, default=STARTER_SEED_ENDOWMENT
    )

    tier: Mapped[ForecasterTier] = mapped_column(
        SAEnum(ForecasterTier, name="forecaster_tier"),
        nullable=False,
        default=ForecasterTier.seedling,
    )

    # Demo/live feature flag — synthetic forecasters are removable in one pass.
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Forecaster id={self.id} display_name={self.display_name!r} "
            f"tier={self.tier.value} synthetic={self.is_synthetic}>"
        )
