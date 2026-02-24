"""Add grade_system column for Swiss / unified choice

Revision ID: 20260224_gradesys
Revises: 20260223_onboarding
Create Date: 2026-02-24

Système scolaire au choix :
- suisse : 1H, 2H, ... 11H (Harmos)
- unifie : 1, 2, ... 12 (système international unifié)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260224_gradesys"
down_revision: Union[str, None] = "20260223_onboarding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "grade_system" not in cols:
        op.add_column(
            "users",
            sa.Column("grade_system", sa.String(20), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("users", "grade_system")
