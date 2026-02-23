"""Add feedback_reports table for user feedback / signalements

Revision ID: 20260222_feedback
Revises: 20260217_streak
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260222_feedback"
down_revision: Union[str, None] = "20260217_streak"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing = set(insp.get_table_names())
    if "feedback_reports" not in existing:
        op.create_table(
            "feedback_reports",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("feedback_type", sa.String(20), nullable=False),
            sa.Column("page_url", sa.Text(), nullable=True),
            sa.Column("exercise_id", sa.Integer(), nullable=True),
            sa.Column("challenge_id", sa.Integer(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="new"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_feedback_reports_user_id", "feedback_reports", ["user_id"])
        op.create_index("ix_feedback_reports_feedback_type", "feedback_reports", ["feedback_type"])
        op.create_index("ix_feedback_reports_created_at", "feedback_reports", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_feedback_reports_created_at", table_name="feedback_reports")
    op.drop_index("ix_feedback_reports_feedback_type", table_name="feedback_reports")
    op.drop_index("ix_feedback_reports_user_id", table_name="feedback_reports")
    op.drop_table("feedback_reports")
