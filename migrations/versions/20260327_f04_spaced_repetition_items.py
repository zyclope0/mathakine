"""F04-P1 — spaced_repetition_items (SM-2 foundation for exercise attempts)

Revision ID: 20260327_f04_spaced_repetition
Revises: 20260327_content_difficulty_tier
Create Date: 2026-03-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260327_f04_spaced_repetition"
down_revision: Union[str, None] = "20260327_content_difficulty_tier"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "spaced_repetition_items" in insp.get_table_names():
        raise RuntimeError(
            "spaced_repetition_items already exists: refusing silent no-op. "
            "Drop the table on a dev database if it is an orphan from a previous "
            "draft migration, or add a follow-up migration to reconcile schema."
        )

    op.create_table(
        "spaced_repetition_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("ease_factor", sa.Float(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
        sa.Column("next_review_date", sa.Date(), nullable=False),
        sa.Column("repetition_count", sa.Integer(), nullable=False),
        sa.Column("last_quality", sa.Integer(), nullable=True),
        sa.Column("last_attempt_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exercise_id", name="uq_sri_user_exercise"),
    )
    op.create_index(
        op.f("ix_spaced_repetition_items_exercise_id"),
        "spaced_repetition_items",
        ["exercise_id"],
    )
    op.create_index(
        op.f("ix_spaced_repetition_items_id"), "spaced_repetition_items", ["id"]
    )
    op.create_index(
        op.f("ix_spaced_repetition_items_last_attempt_id"),
        "spaced_repetition_items",
        ["last_attempt_id"],
    )
    op.create_index(
        op.f("ix_spaced_repetition_items_next_review_date"),
        "spaced_repetition_items",
        ["next_review_date"],
    )
    op.create_index(
        op.f("ix_spaced_repetition_items_user_id"),
        "spaced_repetition_items",
        ["user_id"],
    )
    op.create_index(
        "ix_sri_user_next_review",
        "spaced_repetition_items",
        ["user_id", "next_review_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_sri_user_next_review", table_name="spaced_repetition_items")
    op.drop_index(
        op.f("ix_spaced_repetition_items_user_id"), table_name="spaced_repetition_items"
    )
    op.drop_index(
        op.f("ix_spaced_repetition_items_next_review_date"),
        table_name="spaced_repetition_items",
    )
    op.drop_index(
        op.f("ix_spaced_repetition_items_last_attempt_id"),
        table_name="spaced_repetition_items",
    )
    op.drop_index(
        op.f("ix_spaced_repetition_items_id"), table_name="spaced_repetition_items"
    )
    op.drop_index(
        op.f("ix_spaced_repetition_items_exercise_id"),
        table_name="spaced_repetition_items",
    )
    op.drop_table("spaced_repetition_items")
