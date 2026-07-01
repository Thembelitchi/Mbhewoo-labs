"""
Shared declarative base and mixins for all ORM models.

This module is the canonical import location for the declarative ``Base``. To
keep a single ``MetaData`` registry across the whole application (so Alembic and
``create_all`` see every table), it re-exports the ``Base`` already defined in
``app/database.py`` rather than declaring a second one.

Import ``Base`` (and optionally ``TimestampMixin``) from here in every model.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

# Re-export the single application-wide declarative base.
from app.database import Base

__all__ = ["Base", "TimestampMixin"]


class TimestampMixin:
    """
    Adds ``created_at`` / ``updated_at`` columns to a model.

    Timestamps are set application-side from ``datetime.utcnow`` and
    ``updated_at`` auto-refreshes on every update, per the research-corpus
    modelling conventions.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
