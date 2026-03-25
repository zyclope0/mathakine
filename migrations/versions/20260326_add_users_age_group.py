"""Add users.age_group (F42 phase 1) + backfill depuis grade_level

Revision ID: 20260326_users_age_group
Revises: 20260325_fix_lca_created_at
Create Date: 2026-03-26

Colonne nullable ; backfill uniquement pour lignes ``age_group IS NULL``,
d'après ``grade_level`` (système suisse Harmos exclu).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260326_users_age_group"
down_revision: Union[str, None] = "20260325_fix_lca_created_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "age_group" not in cols:
        op.add_column(
            "users",
            sa.Column("age_group", sa.String(10), nullable=True),
        )

    # Backfill : Harmos → pas de tranche ; sinon mapping par grade unifié
    op.execute(sa.text("""
            UPDATE users
            SET age_group = CASE
                WHEN grade_system = 'suisse' THEN NULL
                WHEN grade_level IS NULL THEN NULL
                WHEN grade_level BETWEEN 1 AND 3 THEN '6-8'
                WHEN grade_level BETWEEN 4 AND 6 THEN '9-11'
                WHEN grade_level BETWEEN 7 AND 9 THEN '12-14'
                WHEN grade_level >= 10 THEN '15+'
                ELSE NULL
            END
            WHERE age_group IS NULL
            """))


def downgrade() -> None:
    op.drop_column("users", "age_group")
