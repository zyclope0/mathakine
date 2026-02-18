"""Add streak columns to users (série d'entraînement)

Revision ID: 20260217_streak
Revises: 20260216_pinned
Create Date: 2026-02-17

Colonnes : current_streak (jours consécutifs), best_streak (record), last_activity_date (dernier jour d'activité).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260217_streak"
down_revision: Union[str, None] = "20260216_pinned"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "current_streak" not in cols:
        op.add_column("users", sa.Column("current_streak", sa.Integer(), nullable=True, server_default="0"))
    if "best_streak" not in cols:
        op.add_column("users", sa.Column("best_streak", sa.Integer(), nullable=True, server_default="0"))
    if "last_activity_date" not in cols:
        op.add_column("users", sa.Column("last_activity_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "current_streak")
    op.drop_column("users", "best_streak")
    op.drop_column("users", "last_activity_date")
