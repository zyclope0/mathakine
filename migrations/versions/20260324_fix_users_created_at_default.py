"""Fix users.created_at missing server default in production.

Revision ID: 20260324_created_at_default
Revises: 20260322_ai_eval_harness
Create Date: 2026-03-24

The users table was created before the migration system was in place.
The column exists but lacks DEFAULT NOW(), causing NULL values on any
INSERT that does not explicitly set created_at.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260324_created_at_default"
down_revision: Union[str, None] = "20260322_ai_eval_harness"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # Skip if legacy schema has no users.created_at (non-prod / partial DB)
    cols = {c["name"]: c for c in insp.get_columns("users")}
    if "created_at" not in cols:
        return

    # Idempotent: (re)apply server default to match ORM server_default=func.now()
    op.execute("ALTER TABLE users ALTER COLUMN created_at SET DEFAULT NOW()")

    # Backfill NULL rows so no record stays without a timestamp
    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN created_at DROP DEFAULT")
