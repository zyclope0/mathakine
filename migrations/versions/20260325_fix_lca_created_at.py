"""Fix logic_challenge_attempts.created_at — add server_default + backfill NULLs.

La table existait avant initial_snapshot.py (CREATE TABLE IF NOT EXISTS skipped).
Le schéma legacy n'avait pas DEFAULT NOW() sur created_at → toutes les tentatives
ont created_at = NULL → timeline F07 les exclut silencieusement.

Revision ID: 20260325_fix_lca_created_at
Revises: 20260325_challenge_progress
Create Date: 2026-03-25
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect, text

revision: str = "20260325_fix_lca_created_at"
down_revision: Union[str, None] = "20260325_challenge_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "logic_challenge_attempts" not in inspector.get_table_names():
        return

    # 1. Backfill existing NULL created_at with NOW() (approximation acceptable —
    #    les tentatives historiques n'ont pas de timestamp fiable).
    op.execute(
        text(
            "UPDATE logic_challenge_attempts "
            "SET created_at = NOW() AT TIME ZONE 'UTC' "
            "WHERE created_at IS NULL"
        )
    )

    # 2. Ajouter le DEFAULT NOW() pour les futures insertions.
    #    ALTER COLUMN … SET DEFAULT ne touche pas les lignes existantes.
    op.execute(
        text(
            "ALTER TABLE logic_challenge_attempts "
            "ALTER COLUMN created_at SET DEFAULT NOW()"
        )
    )

    # 3. Rendre la colonne NOT NULL maintenant que les NULLs sont backfillés.
    op.execute(
        text(
            "ALTER TABLE logic_challenge_attempts "
            "ALTER COLUMN created_at SET NOT NULL"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "logic_challenge_attempts" not in inspector.get_table_names():
        return

    op.execute(
        text(
            "ALTER TABLE logic_challenge_attempts "
            "ALTER COLUMN created_at DROP NOT NULL"
        )
    )
    op.execute(
        text(
            "ALTER TABLE logic_challenge_attempts "
            "ALTER COLUMN created_at DROP DEFAULT"
        )
    )
