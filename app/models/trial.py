"""
Trial model — a clinical trial in the research corpus.

Part of the Mbhewoo Labs "research world". Trials come from PACTR (Pan African
Clinical Trials Registry), ClinicalTrials.gov (NCT), and SANCTR, so each
registry identifier is stored separately and indexed. Trials are the subject of
milestone markets (e.g. "will trial Y advance to Phase 3?") in later work.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Trial(TimestampMixin, Base):
    """A registered clinical trial, keyed by one or more registry identifiers."""

    __tablename__ = "trials"
    __table_args__ = (
        Index("ix_trials_pactr_id", "pactr_id", unique=True),
        Index("ix_trials_nct_id", "nct_id", unique=True),
        Index("ix_trials_sanctr_id", "sanctr_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    pactr_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nct_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sanctr_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    brief_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Phase I/II/III/IV, or "Not Applicable".
    phase: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # not_yet_recruiting/recruiting/active/completed/terminated/withdrawn
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    primary_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Enrolment counts are whole numbers (never floats).
    enrollment_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enrollment_actual: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    sponsor_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # industry/nih/academic/other
    sponsor_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(default=False, nullable=False)
    # Which ingestion source populated this row (pactr/clinicaltrials/sanctr/manual).
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Trial id={self.id} pactr_id={self.pactr_id!r} "
            f"nct_id={self.nct_id!r} title={self.title!r}>"
        )
