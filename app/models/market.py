"""
Market ORM model — a binary, time-boxed forecasting question.

Implements the Market concept from CLAUDE.md / the PRD: a market asks a yes/no
question about a research claim, paper, or trial milestone (e.g. "Will the
primary finding of paper X replicate by 2028?"). It carries LMSR market-maker
state and a resolution once the outcome is known.

LMSR note (CLAUDE.md): the maker uses a logarithmic scoring rule with liquidity
parameter ``b`` (default 100, as in DARPA SCORE). All LMSR quantities and prices
are stored as ``Decimal`` (SQLAlchemy ``Numeric``) — never floats — because
floating-point drift silently corrupts pricing and ledger math.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.forecaster import Forecaster

# LMSR liquidity parameter, matching DARPA SCORE (CLAUDE.md → LMSR).
DEFAULT_LIQUIDITY_PARAM_B: int = 100

# Precision for LMSR quantities and prices. 20 total digits, 8 fractional —
# ample headroom for Seed-scale quantities without float error.
_LMSR_NUMERIC = Numeric(precision=20, scale=8)


class MarketDomain(str, enum.Enum):
    """The five MVP research domains (CLAUDE.md → Domains)."""

    hiv_tb_vaccines = "hiv_tb_vaccines"
    computational_biology = "computational_biology"
    biotech_pharma = "biotech_pharma"
    bioprocessing = "bioprocessing"
    bioeconomy = "bioeconomy"


class MarketStatus(str, enum.Enum):
    """
    Lifecycle of a market.

    draft   → created but not yet open for trading
    open    → accepting predictions (between opens_at and closes_at)
    closed  → trading halted, awaiting resolution
    settled → outcome resolved and payouts applied
    voided  → cancelled; no resolution (e.g. question became ill-posed)
    """

    draft = "draft"
    open = "open"
    closed = "closed"
    settled = "settled"
    voided = "voided"


class MarketOutcome(str, enum.Enum):
    """Resolved outcome of a binary market."""

    yes = "yes"
    no = "no"


class Market(Base):
    """A binary, time-boxed forecasting question with LMSR maker state."""

    __tablename__ = "markets"
    __table_args__ = (
        # Time-boxing must be coherent: close after open, settle no earlier
        # than close (settles_at may be null until scheduled).
        CheckConstraint("closes_at > opens_at", name="ck_markets_close_after_open"),
        CheckConstraint(
            "settles_at IS NULL OR settles_at >= closes_at",
            name="ck_markets_settle_after_close",
        ),
        # LMSR invariants: positive liquidity, non-negative quantities.
        CheckConstraint("liquidity_param_b > 0", name="ck_markets_b_positive"),
        CheckConstraint("q_yes >= 0", name="ck_markets_q_yes_non_negative"),
        CheckConstraint("q_no >= 0", name="ck_markets_q_no_non_negative"),
        # A settled market must carry an outcome; an unsettled one must not.
        CheckConstraint(
            "(status = 'settled') = (resolution_outcome IS NOT NULL)",
            name="ck_markets_settled_iff_outcome",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    question: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[MarketDomain] = mapped_column(
        SAEnum(MarketDomain, name="market_domain"), nullable=False
    )

    # Creator is an admin in the MVP; nullable because platform-seeded markets
    # may not map to a forecaster row. SET NULL keeps markets if the creator is
    # removed.
    creator_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("forecasters.id", ondelete="SET NULL"), nullable=True
    )
    creator: Mapped[Forecaster | None] = relationship("Forecaster")

    status: Mapped[MarketStatus] = mapped_column(
        SAEnum(MarketStatus, name="market_status"),
        nullable=False,
        default=MarketStatus.draft,
    )

    # Time-boxing.
    opens_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    settles_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Resolution.
    resolution_source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resolution_outcome: Mapped[MarketOutcome | None] = mapped_column(
        SAEnum(MarketOutcome, name="market_outcome"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # LMSR market-maker state (Decimal, never float).
    liquidity_param_b: Mapped[Decimal] = mapped_column(
        _LMSR_NUMERIC, nullable=False, default=Decimal(DEFAULT_LIQUIDITY_PARAM_B)
    )
    q_yes: Mapped[Decimal] = mapped_column(
        _LMSR_NUMERIC, nullable=False, default=Decimal(0)
    )
    q_no: Mapped[Decimal] = mapped_column(
        _LMSR_NUMERIC, nullable=False, default=Decimal(0)
    )

    # Demo/live feature flag — synthetic markets are removable in one pass.
    is_synthetic: Mapped[bool] = mapped_column(nullable=False, default=False)

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
            f"<Market id={self.id} domain={self.domain.value} "
            f"status={self.status.value} question={self.question!r}>"
        )
