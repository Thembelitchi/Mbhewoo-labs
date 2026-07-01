"""create markets table

Revision ID: 0002_create_markets
Revises: 0001_create_forecasters
Create Date: 2026-07-01

Adds the ``markets`` table (see app/models/market.py) with LMSR maker state,
time-boxing, and resolution. Kept in sync by hand with the ORM model.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_create_markets"
down_revision: str | None = "0001_create_forecasters"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Postgres enum types backing the Market columns.
market_domain = sa.Enum(
    "hiv_tb_vaccines",
    "computational_biology",
    "biotech_pharma",
    "bioprocessing",
    "bioeconomy",
    name="market_domain",
)
market_status = sa.Enum(
    "draft",
    "open",
    "closed",
    "settled",
    "voided",
    name="market_status",
)
market_outcome = sa.Enum(
    "yes",
    "no",
    name="market_outcome",
)

# LMSR quantities/prices: 20 total digits, 8 fractional (matches the model).
_LMSR_NUMERIC = sa.Numeric(precision=20, scale=8)


def upgrade() -> None:
    op.create_table(
        "markets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", market_domain, nullable=False),
        sa.Column("creator_id", sa.Uuid(), nullable=True),
        sa.Column("status", market_status, server_default="draft", nullable=False),
        sa.Column("opens_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closes_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("settles_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_source", sa.String(length=500), nullable=True),
        sa.Column("resolution_outcome", market_outcome, nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "liquidity_param_b",
            _LMSR_NUMERIC,
            server_default="100",
            nullable=False,
        ),
        sa.Column("q_yes", _LMSR_NUMERIC, server_default="0", nullable=False),
        sa.Column("q_no", _LMSR_NUMERIC, server_default="0", nullable=False),
        sa.Column(
            "is_synthetic",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["forecasters.id"],
            name="fk_markets_creator_id_forecasters",
            ondelete="SET NULL",
        ),
        sa.CheckConstraint("closes_at > opens_at", name="ck_markets_close_after_open"),
        sa.CheckConstraint(
            "settles_at IS NULL OR settles_at >= closes_at",
            name="ck_markets_settle_after_close",
        ),
        sa.CheckConstraint("liquidity_param_b > 0", name="ck_markets_b_positive"),
        sa.CheckConstraint("q_yes >= 0", name="ck_markets_q_yes_non_negative"),
        sa.CheckConstraint("q_no >= 0", name="ck_markets_q_no_non_negative"),
        sa.CheckConstraint(
            "(status = 'settled') = (resolution_outcome IS NOT NULL)",
            name="ck_markets_settled_iff_outcome",
        ),
    )


def downgrade() -> None:
    op.drop_table("markets")
    market_outcome.drop(op.get_bind(), checkfirst=True)
    market_status.drop(op.get_bind(), checkfirst=True)
    market_domain.drop(op.get_bind(), checkfirst=True)
