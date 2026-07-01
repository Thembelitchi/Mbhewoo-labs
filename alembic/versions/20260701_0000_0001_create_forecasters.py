"""create forecasters table

Revision ID: 0001_create_forecasters
Revises:
Create Date: 2026-07-01

Initial schema — the ``forecasters`` table (see app/models/forecaster.py).
Kept in sync by hand with the ORM model so `alembic upgrade head` produces
exactly the columns and constraints the application expects.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_create_forecasters"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Postgres enum type backing Forecaster.tier. Declared once so upgrade can
# create it (implicitly, via the table) and downgrade can drop it explicitly.
forecaster_tier = sa.Enum(
    "seedling",
    "sapling",
    "rooted",
    "mfukula",
    "marula",
    name="forecaster_tier",
)


def upgrade() -> None:
    op.create_table(
        "forecasters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("orcid_id", sa.String(length=19), nullable=True),
        sa.Column("institutional_email", sa.String(length=320), nullable=True),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column(
            "seeds_balance",
            sa.Integer(),
            server_default="100",
            nullable=False,
        ),
        sa.Column(
            "tier",
            forecaster_tier,
            server_default="seedling",
            nullable=False,
        ),
        sa.Column(
            "is_synthetic",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
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
        sa.UniqueConstraint("orcid_id", name="uq_forecasters_orcid_id"),
        sa.UniqueConstraint(
            "institutional_email", name="uq_forecasters_institutional_email"
        ),
        sa.CheckConstraint(
            "seeds_balance >= 0", name="ck_forecasters_seeds_non_negative"
        ),
        sa.CheckConstraint(
            "orcid_id IS NOT NULL OR institutional_email IS NOT NULL",
            name="ck_forecasters_identity_present",
        ),
    )


def downgrade() -> None:
    op.drop_table("forecasters")
    forecaster_tier.drop(op.get_bind(), checkfirst=True)
