"""Standardize userrole enum to uppercase (ARCHIVISTE, GARDIEN)

Revision ID: 20260216_userrole
Revises: 20260215_userrole
Create Date: 2026-02-15 21:00:00.000000

Convention: valeurs enum en MAJUSCULES (PADAWAN, MAITRE, GARDIEN, ARCHIVISTE).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260216_userrole"
down_revision: Union[str, None] = "20260215_userrole"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter ARCHIVISTE et GARDIEN (uppercase) si absents
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

    # Migrer les utilisateurs de lowercase vers uppercase
    op.execute(
        "UPDATE users SET role = 'ARCHIVISTE'::userrole WHERE role::text = 'archiviste'"
    )
    op.execute(
        "UPDATE users SET role = 'GARDIEN'::userrole WHERE role::text = 'gardien'"
    )


def downgrade() -> None:
    # Migrer retour (si nécessaire)
    op.execute(
        "UPDATE users SET role = 'archiviste'::userrole WHERE role::text = 'ARCHIVISTE'"
    )
    op.execute(
        "UPDATE users SET role = 'gardien'::userrole WHERE role::text = 'GARDIEN'"
    )
    # Note: valeurs uppercase restent dans l'enum (PostgreSQL ne permet pas de les supprimer)
