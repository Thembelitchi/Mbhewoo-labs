"""initial research corpus schema

Revision ID: 0003_research_corpus
Revises: 0002_create_markets
Create Date: 2026-07-01

Creates the research-corpus tables (papers, researchers, institutions, domains,
trials, concepts) and their association tables. Hand-written to match the ORM
models in app/models/ exactly (this environment can't reach the live database to
autogenerate). Kept additive on top of the existing platform migrations.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_research_corpus"
down_revision: str | None = "0002_create_markets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── institutions ─────────────────────────────────────────────────────────
    op.create_table(
        "institutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ror_id", sa.String(length=255), nullable=True),
        sa.Column("openalex_id", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=500), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.Column("country_name", sa.String(length=255), nullable=True),
        sa.Column("institution_type", sa.String(length=50), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_institutions_ror_id", "institutions", ["ror_id"], unique=True)
    op.create_index("ix_institutions_openalex_id", "institutions", ["openalex_id"], unique=True)

    # ── domains ──────────────────────────────────────────────────────────────
    op.create_table(
        "domains",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_core_mvp", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_domains_slug", "domains", ["slug"], unique=True)

    # ── concepts (self-referential) ──────────────────────────────────────────
    op.create_table(
        "concepts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("openalex_id", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=500), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("works_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("parent_concept_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["parent_concept_id"], ["concepts.id"],
            name="fk_concepts_parent", ondelete="SET NULL",
        ),
    )
    op.create_index("ix_concepts_openalex_id", "concepts", ["openalex_id"], unique=True)

    # ── researchers (fk → institutions) ──────────────────────────────────────
    op.create_table(
        "researchers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("orcid", sa.String(length=19), nullable=True),
        sa.Column("openalex_id", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=500), nullable=False),
        sa.Column("given_name", sa.String(length=255), nullable=True),
        sa.Column("family_name", sa.String(length=255), nullable=True),
        sa.Column("current_affiliation_id", sa.Uuid(), nullable=True),
        sa.Column("h_index", sa.Integer(), nullable=True),
        sa.Column("works_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cited_by_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["current_affiliation_id"], ["institutions.id"],
            name="fk_researchers_current_affiliation", ondelete="SET NULL",
        ),
    )
    op.create_index("ix_researchers_orcid", "researchers", ["orcid"], unique=True)
    op.create_index("ix_researchers_openalex_id", "researchers", ["openalex_id"], unique=True)

    # ── trials ───────────────────────────────────────────────────────────────
    op.create_table(
        "trials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("pactr_id", sa.String(length=100), nullable=True),
        sa.Column("nct_id", sa.String(length=100), nullable=True),
        sa.Column("sanctr_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=1000), nullable=False),
        sa.Column("brief_summary", sa.Text(), nullable=True),
        sa.Column("phase", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("primary_completion_date", sa.Date(), nullable=True),
        sa.Column("completion_date", sa.Date(), nullable=True),
        sa.Column("enrollment_target", sa.Integer(), nullable=True),
        sa.Column("enrollment_actual", sa.Integer(), nullable=True),
        sa.Column("sponsor_name", sa.String(length=500), nullable=True),
        sa.Column("sponsor_type", sa.String(length=50), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trials_pactr_id", "trials", ["pactr_id"], unique=True)
    op.create_index("ix_trials_nct_id", "trials", ["nct_id"], unique=True)
    op.create_index("ix_trials_sanctr_id", "trials", ["sanctr_id"], unique=True)

    # ── papers ───────────────────────────────────────────────────────────────
    op.create_table(
        "papers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("doi", sa.String(length=255), nullable=True),
        sa.Column("openalex_id", sa.String(length=255), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("journal_name", sa.String(length=500), nullable=True),
        sa.Column("venue_issn", sa.String(length=50), nullable=True),
        sa.Column("open_access_status", sa.String(length=20), nullable=True),
        sa.Column("citation_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_retracted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("retraction_date", sa.Date(), nullable=True),
        sa.Column("retraction_source_url", sa.String(length=1000), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_papers_doi", "papers", ["doi"], unique=True)
    op.create_index("ix_papers_openalex_id", "papers", ["openalex_id"], unique=True)
    op.create_index("ix_papers_publication_year", "papers", ["publication_year"], unique=False)

    # ── association tables ───────────────────────────────────────────────────
    op.create_table(
        "paper_researcher",
        sa.Column("paper_id", sa.Uuid(), nullable=False),
        sa.Column("researcher_id", sa.Uuid(), nullable=False),
        sa.Column("author_position", sa.Integer(), nullable=True),
        sa.Column("is_corresponding", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(
            ["paper_id"], ["papers.id"],
            name="fk_paper_researcher_paper", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["researcher_id"], ["researchers.id"],
            name="fk_paper_researcher_researcher", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("paper_id", "researcher_id"),
    )
    op.create_table(
        "paper_domain",
        sa.Column("paper_id", sa.Uuid(), nullable=False),
        sa.Column("domain_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["paper_id"], ["papers.id"],
            name="fk_paper_domain_paper", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["domain_id"], ["domains.id"],
            name="fk_paper_domain_domain", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("paper_id", "domain_id"),
    )
    op.create_table(
        "paper_concept",
        sa.Column("paper_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paper_id"], ["papers.id"],
            name="fk_paper_concept_paper", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"], ["concepts.id"],
            name="fk_paper_concept_concept", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("paper_id", "concept_id"),
    )
    op.create_table(
        "researcher_institution",
        sa.Column("researcher_id", sa.Uuid(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.Column("from_date", sa.Date(), nullable=True),
        sa.Column("to_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(
            ["researcher_id"], ["researchers.id"],
            name="fk_researcher_institution_researcher", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["institutions.id"],
            name="fk_researcher_institution_institution", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("researcher_id", "institution_id"),
        sa.UniqueConstraint(
            "researcher_id", "institution_id", "from_date",
            name="uq_researcher_institution_period",
        ),
    )


def downgrade() -> None:
    op.drop_table("researcher_institution")
    op.drop_table("paper_concept")
    op.drop_table("paper_domain")
    op.drop_table("paper_researcher")
    op.drop_table("papers")
    op.drop_table("trials")
    op.drop_table("researchers")
    op.drop_table("concepts")
    op.drop_table("domains")
    op.drop_table("institutions")
