"""Add gardien and archiviste to userrole enum

Revision ID: 20260215_userrole
Revises: 20260210_rec_challenge
Create Date: 2026-02-15 20:00:00.000000

Permet l'accès admin via le rôle archiviste.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260215_userrole"
down_revision: Union[str, None] = "20260210_rec_challenge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter GARDIEN et ARCHIVISTE (uppercase) à l'enum userrole si absents
    for value in ("GARDIEN", "ARCHIVISTE"):
        op.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = '{value}'
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole')
                ) THEN
                    ALTER TYPE userrole ADD VALUE '{value}';
                END IF;
            END $$;
        """)


def downgrade() -> None:
    # PostgreSQL ne permet pas de supprimer des valeurs d'enum directement
    pass
