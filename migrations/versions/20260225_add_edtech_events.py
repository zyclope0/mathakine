"""Add edtech_events table for analytics EdTech

Revision ID: 20260225_edtech
Revises: 20260224_gradesys
Create Date: 2026-02-25

Table pour stocker les événements EdTech : quick_start_click, first_attempt.
Permet la consultation dans l'espace admin.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = "20260225_edtech"
down_revision: Union[str, None] = "20260224_gradesys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "edtech_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("event", sa.String(50), nullable=False, index=True),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_edtech_events_created_at", "edtech_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_edtech_events_created_at", table_name="edtech_events")
    op.drop_table("edtech_events")
