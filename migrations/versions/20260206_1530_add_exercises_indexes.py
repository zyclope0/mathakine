"""Add missing indexes on exercises table for performance optimization

Revision ID: 20260206_exercises_idx
Revises: 20260205_missing_tables_idx
Create Date: 2026-02-06 15:30:00.000000

Cette migration ajoute 8 index manquants sur la table 'exercises' :
- Index simples : creator_id, exercise_type, difficulty, is_active, created_at
- Index composites : (exercise_type, difficulty), (is_active, exercise_type), (creator_id, is_active)

Impact attendu : +30-50% performance sur requêtes de listage exercices.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260206_exercises_idx"
down_revision: Union[str, None] = "20260222_legacy_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing indexes on exercises table"""

    # ── Index simples ───────────────────────────────────────────────────

    # Index sur creator_id (FK) - améliore JOINs et requêtes par créateur
    op.create_index(
        "ix_exercises_creator_id", "exercises", ["creator_id"], unique=False
    )

    # Index sur exercise_type - améliore filtrage par type (ADDITION, MULTIPLICATION, etc.)
    op.create_index(
        "ix_exercises_exercise_type", "exercises", ["exercise_type"], unique=False
    )

    # Index sur difficulty - améliore filtrage par niveau (INITIE, PADAWAN, etc.)
    op.create_index(
        "ix_exercises_difficulty", "exercises", ["difficulty"], unique=False
    )

    # Index sur is_active - améliore filtrage exercices actifs/archivés
    op.create_index("ix_exercises_is_active", "exercises", ["is_active"], unique=False)

    # Index sur created_at - améliore tri chronologique (ORDER BY created_at DESC)
    op.create_index(
        "ix_exercises_created_at", "exercises", ["created_at"], unique=False
    )

    # ── Index composites ────────────────────────────────────────────────

    # Index composite (exercise_type, difficulty) - améliore filtrage combiné
    # Requête fréquente : GET /api/exercises?type=ADDITION&difficulty=PADAWAN
    op.create_index(
        "ix_exercises_type_difficulty",
        "exercises",
        ["exercise_type", "difficulty"],
        unique=False,
    )

    # Index composite (is_active, exercise_type) - améliore filtrage exercices actifs par type
    # Requête fréquente : GET /api/exercises?is_active=true&type=MULTIPLICATION
    op.create_index(
        "ix_exercises_active_type",
        "exercises",
        ["is_active", "exercise_type"],
        unique=False,
    )

    # Index composite (creator_id, is_active) - améliore listage exercices actifs d'un créateur
    # Requête fréquente : GET /api/exercises?creator_id=X&is_active=true
    op.create_index(
        "ix_exercises_creator_active",
        "exercises",
        ["creator_id", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    """Remove added indexes"""

    # ── Index composites (supprimer en premier) ─────────────────────────
    op.drop_index("ix_exercises_creator_active", table_name="exercises")
    op.drop_index("ix_exercises_active_type", table_name="exercises")
    op.drop_index("ix_exercises_type_difficulty", table_name="exercises")

    # ── Index simples ───────────────────────────────────────────────────
    op.drop_index("ix_exercises_created_at", table_name="exercises")
    op.drop_index("ix_exercises_is_active", table_name="exercises")
    op.drop_index("ix_exercises_difficulty", table_name="exercises")
    op.drop_index("ix_exercises_exercise_type", table_name="exercises")
    op.drop_index("ix_exercises_creator_id", table_name="exercises")
