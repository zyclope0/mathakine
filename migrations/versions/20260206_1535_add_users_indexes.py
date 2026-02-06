"""Add missing indexes on users table for admin dashboard optimization

Revision ID: 20260206_users_idx
Revises: 20260206_exercises_idx
Create Date: 2026-02-06 15:35:00.000000

Cette migration ajoute 2 index manquants sur la table 'users' :
- Index simple : created_at (tri chronologique nouveaux utilisateurs)
- Index simple : is_active (filtrage utilisateurs actifs/désactivés)

Impact attendu : +10-20% performance sur requêtes admin dashboard.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20260206_users_idx'
down_revision: Union[str, None] = '20260206_exercises_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing indexes on users table"""
    
    # Index sur created_at - améliore tri chronologique (nouveaux utilisateurs)
    # Requête fréquente : Dashboard admin, stats utilisateurs récents
    op.create_index(
        'ix_users_created_at',
        'users',
        ['created_at'],
        unique=False
    )
    
    # Index sur is_active - améliore filtrage utilisateurs actifs/désactivés
    # Requête fréquente : Dashboard admin, liste utilisateurs actifs
    op.create_index(
        'ix_users_is_active',
        'users',
        ['is_active'],
        unique=False
    )


def downgrade() -> None:
    """Remove added indexes"""
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_created_at', table_name='users')
