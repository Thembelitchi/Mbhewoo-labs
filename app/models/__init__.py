"""
SQLAlchemy ORM models.

Importing the models here registers them on ``Base.metadata`` so that Alembic
autogenerate (via ``import app.models`` in ``alembic/env.py``) and
``Base.metadata.create_all`` can see every table.
"""

from app.models.base import Base, TimestampMixin

# Research corpus (the "research world").
from app.models.associations import (
    paper_concept,
    paper_domain,
    paper_researcher,
    researcher_institution,
)
from app.models.concept import Concept
from app.models.domain import Domain
from app.models.institution import Institution
from app.models.paper import Paper
from app.models.researcher import Researcher
from app.models.trial import Trial

# Platform models (built earlier this session).
from app.models.forecaster import (
    STARTER_SEED_ENDOWMENT,
    Forecaster,
    ForecasterTier,
)
from app.models.market import (
    DEFAULT_LIQUIDITY_PARAM_B,
    Market,
    MarketDomain,
    MarketOutcome,
    MarketStatus,
)

__all__ = [
    "Base",
    "TimestampMixin",
    # Research corpus
    "Paper",
    "Researcher",
    "Institution",
    "Domain",
    "Trial",
    "Concept",
    "paper_researcher",
    "paper_domain",
    "paper_concept",
    "researcher_institution",
    # Platform
    "STARTER_SEED_ENDOWMENT",
    "Forecaster",
    "ForecasterTier",
    "DEFAULT_LIQUIDITY_PARAM_B",
    "Market",
    "MarketDomain",
    "MarketOutcome",
    "MarketStatus",
]
