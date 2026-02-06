"""Add missing indexes on exercises table for age_group and is_archived columns

Revision ID: 20260206_exercises_missing_idx
Revises: 20260206_user_achv_idx
Create Date: 2026-02-06 16:00:00.000000

Cette migration ajoute 3 index manquants sur la table 'exercises' :
- Index simple : age_group (filtrage par groupe d'âge)
- Index simple : is_archived (filtrage actifs/archivés - très fréquent)
- Index composite : (is_archived, age_group) (requêtes combinées)

Impact attendu : +15-25% performance sur requêtes de listage exercices.

ROLLBACK: alembic downgrade 20260206_user_achv_idx
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '20260206_exercises_missing_idx'
down_revision: Union[str, None] = '20260206_user_achv_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def index_exists(connection, index_name: str, table_name: str) -> bool:
    """Vérifie si un index existe déjà en base de données"""
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE tablename = :table_name AND indexname = :index_name
        )
    """), {'table_name': table_name, 'index_name': index_name})
    return result.scalar()


def upgrade() -> None:
    """Add missing indexes on exercises table for age_group and is_archived"""
    
    # Obtenir la connexion pour vérifier les index existants
    connection = op.get_bind()
    
    # ── Index simple sur age_group ────────────────────────────────────────
    # Justification : Filtrage fréquent GET /api/exercises?age_group=6-8
    # NOTE: Un index 'idx_exercises_age_group' existe peut-être déjà (préfixe différent)
    age_group_exists = (
        index_exists(connection, 'ix_exercises_age_group', 'exercises') or
        index_exists(connection, 'idx_exercises_age_group', 'exercises')
    )
    if not age_group_exists:
        op.create_index(
            'ix_exercises_age_group',
            'exercises',
            ['age_group'],
            unique=False
        )
        print("  [CREATED] ix_exercises_age_group")
    else:
        print("  [SKIPPED] ix_exercises_age_group (or idx_exercises_age_group already exists)")
    
    # ── Index simple sur is_archived ──────────────────────────────────────
    # Justification : 90%+ des requêtes filtrent is_archived = FALSE
    # NOTE: Un index 'idx_exercises_active' existe mais c'est pour is_active, pas is_archived
    is_archived_exists = (
        index_exists(connection, 'ix_exercises_is_archived', 'exercises') or
        index_exists(connection, 'idx_exercises_is_archived', 'exercises')
    )
    if not is_archived_exists:
        op.create_index(
            'ix_exercises_is_archived',
            'exercises',
            ['is_archived'],
            unique=False
        )
        print("  [CREATED] ix_exercises_is_archived")
    else:
        print("  [SKIPPED] ix_exercises_is_archived (already exists)")
    
    # ── Index composite (is_archived, age_group) ──────────────────────────
    # Justification : Requête combinée très fréquente
    # WHERE is_archived = FALSE AND age_group = 'X'
    archived_age_exists = (
        index_exists(connection, 'ix_exercises_archived_age', 'exercises') or
        index_exists(connection, 'idx_exercises_archived_age', 'exercises')
    )
    if not archived_age_exists:
        op.create_index(
            'ix_exercises_archived_age',
            'exercises',
            ['is_archived', 'age_group'],
            unique=False
        )
        print("  [CREATED] ix_exercises_archived_age")
    else:
        print("  [SKIPPED] ix_exercises_archived_age (already exists)")


def downgrade() -> None:
    """Remove added indexes (ROLLBACK)
    
    NOTE: Cette fonction supprime UNIQUEMENT les index créés par cette migration
    (préfixe 'ix_'). Les index pré-existants avec préfixe 'idx_' ne sont PAS touchés.
    """
    
    # Obtenir la connexion pour vérifier les index existants
    connection = op.get_bind()
    
    # ── Index composite (supprimer en premier) ────────────────────────────
    if index_exists(connection, 'ix_exercises_archived_age', 'exercises'):
        op.drop_index('ix_exercises_archived_age', table_name='exercises')
        print("  [DROPPED] ix_exercises_archived_age")
    else:
        print("  [SKIPPED] ix_exercises_archived_age (not found or not created by this migration)")
    
    # ── Index simples ─────────────────────────────────────────────────────
    if index_exists(connection, 'ix_exercises_is_archived', 'exercises'):
        op.drop_index('ix_exercises_is_archived', table_name='exercises')
        print("  [DROPPED] ix_exercises_is_archived")
    else:
        print("  [SKIPPED] ix_exercises_is_archived (not found or not created by this migration)")
    
    if index_exists(connection, 'ix_exercises_age_group', 'exercises'):
        op.drop_index('ix_exercises_age_group', table_name='exercises')
        print("  [DROPPED] ix_exercises_age_group")
    else:
        print("  [SKIPPED] ix_exercises_age_group (not found or not created by this migration)")
