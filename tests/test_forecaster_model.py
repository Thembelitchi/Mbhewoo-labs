"""
Tests for the Forecaster ORM model.

Run against an in-memory SQLite database so they need no network, no Supabase,
and no extra dependencies. These check the credibility-sensitive defaults and
constraints: integer Seed balance, starter endowment, tier default, the
synthetic flag, and the "at least one identity" check constraint.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base
from app.models import STARTER_SEED_ENDOWMENT, Forecaster, ForecasterTier


@pytest.fixture()
def session() -> Session:
    """A throwaway in-memory SQLite session with the schema created."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_new_forecaster_defaults(session: Session) -> None:
    forecaster = Forecaster(
        display_name="Dr Nomsa Dlamini",
        orcid_id="0000-0002-1825-0097",
    )
    session.add(forecaster)
    session.commit()
    session.refresh(forecaster)

    assert isinstance(forecaster.id, uuid.UUID)
    # Seeds are integers, and every new forecaster starts with the endowment.
    assert forecaster.seeds_balance == STARTER_SEED_ENDOWMENT
    assert isinstance(forecaster.seeds_balance, int)
    assert forecaster.tier is ForecasterTier.seedling
    assert forecaster.is_synthetic is False
    assert forecaster.is_active is True
    assert forecaster.created_at is not None


def test_synthetic_flag_can_be_set(session: Session) -> None:
    forecaster = Forecaster(
        display_name="Synthetic Forecaster 001",
        institutional_email="synth001@demo.mbhewoolabs.com",
        is_synthetic=True,
    )
    session.add(forecaster)
    session.commit()

    assert forecaster.is_synthetic is True


def test_identity_required(session: Session) -> None:
    """A forecaster with neither ORCID nor email must be rejected."""
    forecaster = Forecaster(display_name="Anonymous")
    session.add(forecaster)

    with pytest.raises(IntegrityError):
        session.commit()
