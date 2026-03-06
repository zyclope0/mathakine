"""Add daily_challenges table for F02 — Défis quotidiens

Revision ID: 20260307_daily
Revises: 20260304_diagnostic
Create Date: 2026-03-07

Table pour stocker les défis quotidiens par utilisateur.
Types : volume_exercises, specific_type, logic_challenge.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260307_daily"
down_revision: Union[str, None] = "20260304_diagnostic"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "daily_challenges" in inspector.get_table_names():
        return

    op.create_table(
        "daily_challenges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("challenge_type", sa.String(50), nullable=False),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("target_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("completed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("bonus_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_daily_challenges_user_date",
        "daily_challenges",
        ["user_id", "date"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "daily_challenges" not in inspector.get_table_names():
        return

    op.drop_index("ix_daily_challenges_user_date", table_name="daily_challenges")
    op.drop_table("daily_challenges")
