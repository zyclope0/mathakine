"""Initial schema snapshot

Revision ID: initial_snapshot
Revises:
Create Date: 2025-05-12 00:35:00.000000

Cette migration crée le schéma de base complet (enums + tables principales).
Elle est idempotente : utilise IF NOT EXISTS / CREATE TYPE IF NOT EXISTS pour
être sûre sur les bases déjà existantes comme sur les bases fraîches (CI).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "initial_snapshot"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Crée le schéma de base complet si la base est vierge.
    Sur une base existante, toutes les opérations sont idempotentes (IF NOT EXISTS).
    """
    # ── Enums PostgreSQL ────────────────────────────────────────────────────
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                CREATE TYPE userrole AS ENUM ('PADAWAN', 'MAITRE', 'GARDIEN', 'ARCHIVISTE');
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'agegroup') THEN
                CREATE TYPE agegroup AS ENUM (
                    'GROUP_6_8', 'GROUP_10_12', 'GROUP_13_15',
                    'GROUP_15_17', 'ADULT', 'ALL_AGES'
                );
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'logicchallengetype') THEN
                CREATE TYPE logicchallengetype AS ENUM (
                    'SEQUENCE', 'PATTERN', 'VISUAL', 'PUZZLE', 'RIDDLE',
                    'DEDUCTION', 'PROBABILITY', 'GRAPH', 'CODING', 'CHESS', 'CUSTOM'
                );
            END IF;
        END $$;
    """)

    # ── Table users ─────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role userrole DEFAULT 'PADAWAN',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_email_verified BOOLEAN DEFAULT FALSE NOT NULL,
            email_verification_token VARCHAR(255),
            email_verification_sent_at TIMESTAMP WITH TIME ZONE,
            password_reset_token VARCHAR(255),
            password_reset_expires_at TIMESTAMP WITH TIME ZONE,
            grade_level INTEGER,
            grade_system VARCHAR(20),
            learning_style VARCHAR(50),
            preferred_difficulty VARCHAR(50),
            onboarding_completed_at TIMESTAMP WITH TIME ZONE,
            learning_goal VARCHAR(100),
            practice_rhythm VARCHAR(50),
            preferred_theme VARCHAR(50),
            accessibility_settings TEXT,
            pinned_badge_ids JSONB,
            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            total_points INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            experience_points INTEGER DEFAULT 0,
            jedi_rank VARCHAR(50) DEFAULT 'youngling',
            avatar_url VARCHAR(255)
        )
    """)

    # ── Table exercises (doit exister avant recommendations, feedback_reports) ─
    op.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            exercise_type VARCHAR(50) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            age_group VARCHAR(50),
            question TEXT NOT NULL,
            correct_answer VARCHAR(255) NOT NULL,
            choices JSONB,
            explanation TEXT,
            hint TEXT,
            tags VARCHAR(255),
            image_url VARCHAR(255),
            audio_url VARCHAR(255),
            context_theme VARCHAR(100),
            complexity INTEGER DEFAULT 1,
            ai_generated BOOLEAN DEFAULT FALSE,
            creator_id INTEGER REFERENCES users(id),
            is_active BOOLEAN DEFAULT TRUE,
            is_archived BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)

    # ── Table logic_challenges ───────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS logic_challenges (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            challenge_type logicchallengetype NOT NULL,
            age_group agegroup NOT NULL,
            difficulty VARCHAR(50),
            content TEXT,
            question TEXT,
            solution TEXT,
            correct_answer VARCHAR(255),
            choices JSON,
            solution_explanation TEXT,
            visual_data JSON,
            hints JSON,
            is_active BOOLEAN DEFAULT TRUE,
            creator_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            difficulty_rating FLOAT DEFAULT 3.0,
            estimated_time_minutes INTEGER DEFAULT 15,
            success_rate FLOAT DEFAULT 0.0,
            image_url VARCHAR,
            source_reference VARCHAR,
            tags VARCHAR,
            is_template BOOLEAN DEFAULT FALSE,
            generation_parameters JSON,
            is_archived BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0
        )
    """)

    # ── Table attempts ───────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            exercise_id INTEGER NOT NULL REFERENCES exercises(id),
            user_answer VARCHAR NOT NULL,
            is_correct BOOLEAN NOT NULL,
            time_spent FLOAT,
            attempt_number INTEGER DEFAULT 1,
            hints_used INTEGER DEFAULT 0,
            device_info VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # ── Table logic_challenge_attempts ───────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS logic_challenge_attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            challenge_id INTEGER NOT NULL REFERENCES logic_challenges(id),
            user_solution TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            time_spent FLOAT,
            hints_used INTEGER DEFAULT 0,
            attempt_number INTEGER DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # ── Table achievements ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id SERIAL PRIMARY KEY,
            code VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            icon_url VARCHAR(255),
            category VARCHAR(50),
            difficulty VARCHAR(50),
            points_reward INTEGER DEFAULT 0,
            is_secret BOOLEAN DEFAULT FALSE,
            requirements JSON,
            star_wars_title VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # ── Table user_achievements ──────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
            earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            progress_data JSON,
            is_displayed BOOLEAN DEFAULT TRUE
        )
    """)

    # ── Table progress ───────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            exercise_type VARCHAR NOT NULL,
            difficulty VARCHAR NOT NULL,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            average_time FLOAT,
            completion_rate FLOAT,
            streak INTEGER DEFAULT 0,
            highest_streak INTEGER DEFAULT 0,
            concept_mastery JSON,
            learning_curve JSON,
            last_active_date TIMESTAMP WITH TIME ZONE,
            mastery_level INTEGER DEFAULT 1,
            awards JSON,
            strengths VARCHAR,
            areas_to_improve VARCHAR,
            recommendations VARCHAR,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # ── Table recommendations ────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
            challenge_id INTEGER REFERENCES logic_challenges(id) ON DELETE SET NULL,
            recommendation_type VARCHAR(20) DEFAULT 'exercise' NOT NULL,
            exercise_type VARCHAR NOT NULL,
            difficulty VARCHAR NOT NULL,
            priority INTEGER DEFAULT 5,
            reason TEXT,
            is_completed BOOLEAN DEFAULT FALSE,
            shown_count INTEGER DEFAULT 0,
            clicked_count INTEGER DEFAULT 0,
            last_clicked_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Note: les tables notifications, user_sessions, settings, feedback_reports,
    # admin_audit_logs, edtech_events, diagnostic_results sont créées par leurs
    # migrations dédiées (20260205, 20260215, 20260216, 20260222, 20260225, 20260304).

    # ── Index de base (uniquement ceux non créés par des migrations suivantes) ──
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_username ON users (username)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    # Note : les index sur exercises, logic_challenges et attempts sont créés
    # par les migrations 20260206_exercises_idx et suivantes.


def downgrade() -> None:
    """
    On ne supporte pas la redescente depuis l'état initial
    """
    raise NotImplementedError("Downgrade not supported from initial state")
