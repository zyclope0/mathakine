"""Add onboarding columns for Quick Win #2 — Onboarding pédagogique

Revision ID: 20260223_onboarding
Revises: 20260222_feedback
Create Date: 2026-02-23

Colonnes pour contenu adaptatif :
- onboarding_completed_at : date de complétion du mini-diagnostic (null = pas encore fait)
- learning_goal : objectif pédagogique court (réviser, préparer examen, progresser, etc.)
- practice_rhythm : rythme souhaité (10min/jour, 30min/semaine, etc.)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260223_onboarding"
down_revision: Union[str, None] = "20260222_feedback"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "onboarding_completed_at" not in cols:
        op.add_column(
            "users",
            sa.Column(
                "onboarding_completed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )
    if "learning_goal" not in cols:
        op.add_column(
            "users",
            sa.Column("learning_goal", sa.String(100), nullable=True),
        )
    if "practice_rhythm" not in cols:
        op.add_column(
            "users",
            sa.Column("practice_rhythm", sa.String(50), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("users", "onboarding_completed_at")
    op.drop_column("users", "learning_goal")
    op.drop_column("users", "practice_rhythm")
