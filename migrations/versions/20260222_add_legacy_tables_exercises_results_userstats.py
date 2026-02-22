"""Add legacy tables (exercises, results, user_stats) — migration DDL depuis init_database

Revision ID: 20260222_legacy_tables
Revises: 20260205_missing_tables_idx
Create Date: 2026-02-22

Tables créées par init_database(), désormais gérées par Alembic.
Idempotent : CREATE TABLE IF NOT EXISTS, ADD COLUMN IF NOT EXISTS, CREATE INDEX IF NOT EXISTS.
Doit s'exécuter avant 20260206_1530 (index sur exercises).
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "20260222_legacy_tables"
down_revision: Union[str, None] = "20260205_missing_tables_idx"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── Table exercises (FK users doit exister) ─────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS exercises (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            creator_id INTEGER REFERENCES users(id),
            exercise_type VARCHAR(50) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            tags VARCHAR(255),
            question TEXT NOT NULL,
            correct_answer VARCHAR(255) NOT NULL,
            choices JSONB,
            explanation TEXT,
            hint TEXT,
            image_url VARCHAR(255),
            audio_url VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_archived BOOLEAN DEFAULT FALSE,
            ai_generated BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Index exercises (IF NOT EXISTS, partiels)
    for idx_sql in [
        "CREATE INDEX IF NOT EXISTS idx_exercises_type_difficulty ON exercises(exercise_type, difficulty) WHERE is_archived = false",
        "CREATE INDEX IF NOT EXISTS idx_exercises_active ON exercises(is_active, is_archived) WHERE is_archived = false",
        "CREATE INDEX IF NOT EXISTS idx_exercises_creator ON exercises(creator_id) WHERE is_archived = false",
        "CREATE INDEX IF NOT EXISTS idx_exercises_created_at ON exercises(created_at DESC) WHERE is_archived = false",
        "CREATE INDEX IF NOT EXISTS idx_exercises_view_count ON exercises(view_count DESC) WHERE is_archived = false",
        "CREATE INDEX IF NOT EXISTS idx_exercises_ai_generated ON exercises(ai_generated) WHERE is_archived = false",
    ]:
        conn.execute(text(idx_sql))

    # Colonne ai_generated (si table créée par autre source)
    conn.execute(text(
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE"
    ))

    # UPDATE ai_generated pour exercices avec préfixe IA (idempotent)
    from app.core.constants import Messages

    prefix = Messages.AI_EXERCISE_PREFIX
    conn.execute(
        text(
            "UPDATE exercises SET ai_generated = TRUE "
            "WHERE (title LIKE :pat OR question LIKE :pat) AND (ai_generated IS NULL OR ai_generated = false)"
        ),
        {"pat": f"%{prefix}%"},
    )

    # ── Table results ────────────────────────────────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            exercise_id INTEGER NOT NULL,
            is_correct BOOLEAN NOT NULL,
            attempt_count INTEGER,
            time_spent REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # ── Table user_stats ──────────────────────────────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS user_stats (
            id SERIAL PRIMARY KEY,
            exercise_type VARCHAR(50) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))


def downgrade() -> None:
    # Ne pas supprimer les tables : données potentiellement en production.
    # Rollback = no-op pour prévenir perte de données.
    # Pour rollback manuel : DROP TABLE exercises, results, user_stats (à faire manuellement si besoin).
    pass
