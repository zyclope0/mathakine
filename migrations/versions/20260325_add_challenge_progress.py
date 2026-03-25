"""Table challenge_progress — maîtrise agrégée par type de défi (utilisateur).

Revision ID: 20260325_challenge_progress
Revises: 20260324_created_at_default
Create Date: 2026-03-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260325_challenge_progress"
down_revision: Union[str, None] = "20260324_created_at_default"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "challenge_progress" in inspector.get_table_names():
        return

    op.create_table(
        "challenge_progress",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("challenge_type", sa.String(length=50), nullable=False),
        sa.Column("total_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "completion_rate",
            sa.Float(),
            nullable=False,
            server_default="0.0",
        ),
        sa.Column(
            "mastery_level",
            sa.String(length=20),
            nullable=False,
            server_default="novice",
        ),
        sa.Column(
            "last_attempted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.UniqueConstraint(
            "user_id", "challenge_type", name="uq_challenge_progress_user_type"
        ),
    )
    op.create_index(
        "ix_challenge_progress_user_id",
        "challenge_progress",
        ["user_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "challenge_progress" not in inspector.get_table_names():
        return

    op.drop_index("ix_challenge_progress_user_id", table_name="challenge_progress")
    op.drop_table("challenge_progress")
