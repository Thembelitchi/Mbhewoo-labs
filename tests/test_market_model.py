"""
Tests for the Market ORM model.

Run against in-memory SQLite (no network, no Supabase, no extra deps). These
lock down the credibility-sensitive pieces: Decimal LMSR state (never float),
the default liquidity parameter, sane time-boxing, and the settled/outcome
invariant.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base
from app.models import (
    DEFAULT_LIQUIDITY_PARAM_B,
    Market,
    MarketDomain,
    MarketStatus,
)


@pytest.fixture()
def session() -> Session:
    """A throwaway in-memory SQLite session with the schema created."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def _times() -> tuple[datetime, datetime]:
    opens = datetime(2027, 1, 1, tzinfo=timezone.utc)
    closes = opens + timedelta(days=365)
    return opens, closes


def test_new_market_defaults(session: Session) -> None:
    opens, closes = _times()
    market = Market(
        question="Will the primary finding of paper X replicate by 2028?",
        domain=MarketDomain.hiv_tb_vaccines,
        opens_at=opens,
        closes_at=closes,
    )
    session.add(market)
    session.commit()
    session.refresh(market)

    assert isinstance(market.id, uuid.UUID)
    assert market.status is MarketStatus.draft
    assert market.is_synthetic is False
    assert market.resolution_outcome is None

    # LMSR state must be Decimal, never float.
    assert isinstance(market.liquidity_param_b, Decimal)
    assert market.liquidity_param_b == Decimal(DEFAULT_LIQUIDITY_PARAM_B)
    assert isinstance(market.q_yes, Decimal)
    assert market.q_yes == Decimal(0)
    assert market.q_no == Decimal(0)


def test_close_must_follow_open(session: Session) -> None:
    opens, closes = _times()
    market = Market(
        question="Ill-timed market",
        domain=MarketDomain.bioprocessing,
        opens_at=closes,   # deliberately inverted
        closes_at=opens,
    )
    session.add(market)
    with pytest.raises(IntegrityError):
        session.commit()


def test_settled_requires_outcome(session: Session) -> None:
    """A market marked settled with no outcome must be rejected."""
    opens, closes = _times()
    market = Market(
        question="Settled without an outcome",
        domain=MarketDomain.bioeconomy,
        opens_at=opens,
        closes_at=closes,
        status=MarketStatus.settled,
        resolution_outcome=None,
    )
    session.add(market)
    with pytest.raises(IntegrityError):
        session.commit()
