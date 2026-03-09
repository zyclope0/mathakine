"""Add password_changed_at to users for token revocation post-reset

Revision ID: 20260309_password_changed_at
Revises: 20260307_daily
Create Date: 2026-03-09

Marqueur dédié pour invalider les tokens JWT après un reset password réussi.
Les tokens émis avant password_changed_at sont rejetés (iat < password_changed_at).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260309_password_changed_at"
down_revision: Union[str, None] = "20260307_daily"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "password_changed_at" not in cols:
        op.add_column(
            "users",
            sa.Column(
                "password_changed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )


def downgrade() -> None:
    op.drop_column("users", "password_changed_at")
