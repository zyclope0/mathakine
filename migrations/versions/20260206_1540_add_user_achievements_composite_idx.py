"""Add composite index on user_achievements table to prevent duplicates

Revision ID: 20260206_user_achv_idx
Revises: 20260206_users_idx
Create Date: 2026-02-06 15:40:00.000000

Cette migration ajoute 1 index composite UNIQUE sur la table 'user_achievements' :
- Index unique : (user_id, achievement_id) - empêche doublons + optimise requêtes

Impact attendu : +5% performance + intégrité données (pas de badges dupliqués).
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20260206_user_achv_idx'
down_revision: Union[str, None] = '20260206_users_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique composite index on user_achievements table"""
    
    # Index composite UNIQUE (user_id, achievement_id)
    # Empêche qu'un utilisateur obtienne le même badge plusieurs fois
    # Optimise aussi la requête : "L'utilisateur a-t-il ce badge ?"
    op.create_index(
        'ix_user_achievements_user_achievement',
        'user_achievements',
        ['user_id', 'achievement_id'],
        unique=True
    )


def downgrade() -> None:
    """Remove added index"""
    op.drop_index('ix_user_achievements_user_achievement', table_name='user_achievements')
