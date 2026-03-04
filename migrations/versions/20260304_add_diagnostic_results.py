"""Add diagnostic_results table for F03 — Diagnostic initial

Revision ID: 20260304_diagnostic
Revises: 20260225_edtech
Create Date: 2026-03-04

Table pour stocker les résultats de sessions de diagnostic adaptatif (IRT
simplifié). Un enregistrement par session complétée, scores JSONB par type
d'exercice, déclencheur (onboarding | settings).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260304_diagnostic"
down_revision: Union[str, None] = "20260225_edtech"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "diagnostic_results" in inspector.get_table_names():
        return  # Idempotent — table déjà présente

    op.create_table(
        "diagnostic_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("triggered_from", sa.String(20), nullable=False, server_default="onboarding"),
        sa.Column("scores", JSONB, nullable=False, server_default="{}"),
        sa.Column("questions_asked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    # ix_diagnostic_results_user_id est créé implicitement via index=True sur la FK
    op.create_index(
        "ix_diagnostic_results_completed_at",
        "diagnostic_results",
        ["completed_at"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "diagnostic_results" not in inspector.get_table_names():
        return

    op.drop_index("ix_diagnostic_results_completed_at", table_name="diagnostic_results")
    op.drop_table("diagnostic_results")
