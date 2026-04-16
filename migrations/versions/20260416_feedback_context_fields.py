"""Add context fields to feedback_reports (A1 beta)

Revision ID: 20260416_feedback_context
Revises: 20260327_f04_spaced_repetition
Create Date: 2026-04-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260416_feedback_context"
down_revision: Union[str, None] = "20260327_f04_spaced_repetition"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("feedback_reports", sa.Column("user_role", sa.String(30), nullable=True))
    op.add_column("feedback_reports", sa.Column("active_theme", sa.String(50), nullable=True))
    op.add_column("feedback_reports", sa.Column("ni_state", sa.String(20), nullable=True))
    op.add_column("feedback_reports", sa.Column("component_id", sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column("feedback_reports", "component_id")
    op.drop_column("feedback_reports", "ni_state")
    op.drop_column("feedback_reports", "active_theme")
    op.drop_column("feedback_reports", "user_role")
