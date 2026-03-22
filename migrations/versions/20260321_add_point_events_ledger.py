"""Ledger gamification — table point_events (sources badge / daily challenge / futur).

Revision ID: 20260321_point_events
Revises: 20260320_rec_reason_i18n
Create Date: 2026-03-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260321_point_events"
down_revision: Union[str, None] = "20260320_rec_reason_i18n"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "point_events" in inspector.get_table_names():
        return

    op.create_table(
        "point_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("points_delta", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("details", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_point_events_user_id", "point_events", ["user_id"])
    op.create_index("ix_point_events_source_type", "point_events", ["source_type"])
    op.create_index("ix_point_events_source_id", "point_events", ["source_id"])
    op.create_index(
        "ix_point_events_user_created",
        "point_events",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "point_events" not in inspector.get_table_names():
        return

    op.drop_index("ix_point_events_user_created", table_name="point_events")
    op.drop_index("ix_point_events_source_id", table_name="point_events")
    op.drop_index("ix_point_events_source_type", table_name="point_events")
    op.drop_index("ix_point_events_user_id", table_name="point_events")
    op.drop_table("point_events")
