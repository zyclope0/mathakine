"""Add pinned_badge_ids to users (A-4 épingler)

Revision ID: 20260216_pinned
Revises: 20260216_settings
Create Date: 2026-02-16

Option « Épingler » 1-3 badges — stockage des IDs épinglés par l'utilisateur.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260216_pinned"
down_revision: Union[str, None] = "20260216_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "pinned_badge_ids" not in cols:
        op.add_column(
            "users",
            sa.Column("pinned_badge_ids", postgresql.JSONB(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("users", "pinned_badge_ids")
