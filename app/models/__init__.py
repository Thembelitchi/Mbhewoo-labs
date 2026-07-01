"""
SQLAlchemy ORM models.

Importing the models here registers them on ``Base.metadata`` so that Alembic
autogenerate (via ``import app.models`` in ``alembic/env.py``) and
``Base.metadata.create_all`` can see every table.
"""

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
    "STARTER_SEED_ENDOWMENT",
    "Forecaster",
    "ForecasterTier",
    "DEFAULT_LIQUIDITY_PARAM_B",
    "Market",
    "MarketDomain",
    "MarketOutcome",
    "MarketStatus",
]
