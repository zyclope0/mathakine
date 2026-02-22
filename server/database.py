"""
Database initialization and management for Mathakine.

This module centralizes database operations for the enhanced server,
providing initialization, connection management, and utility functions.
"""
import os
import sys
import traceback

import psycopg2
from dotenv import load_dotenv
from sqlalchemy import text

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

from app.db.base import engine
from app.db.queries import ExerciseQueries, ResultQueries, UserStatsQueries

# Charger les variables d'environnement (ignorer .env en prod - sécurité)
if os.environ.get("ENVIRONMENT") != "production":
    load_dotenv(override=False)


def get_database_url() -> str:
    """
    Get the database URL (unifié avec SQLAlchemy : respecte TESTING, TEST_DATABASE_URL).
    """
    return settings.SQLALCHEMY_DATABASE_URL


def get_db_connection():
    """
    Obtient une connexion à la base de données PostgreSQL.

    Returns:
        Une connexion psycopg2
    """
    try:
        conn = psycopg2.connect(get_database_url())
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à PostgreSQL: {e}")
        raise e


def _execute_ddl_statements(conn, sql: str) -> None:
    """Exécute les requêtes DDL séparées par ';'."""
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt and not stmt.startswith("--"):
            conn.execute(text(stmt))


def init_database():
    """
    Initialize the database if necessary.

    Uses SQLAlchemy engine (same as app) — no psycopg2 direct for init.
    Creates tables if they don't exist and performs other initialization tasks.
    """
    logger.info("Initializing database")

    try:
        with engine.connect() as conn:
            # Create exercises table + indexes
            _execute_ddl_statements(conn, ExerciseQueries.CREATE_TABLE)
            conn.commit()

            # Add ai_generated column if it doesn't exist
            try:
                conn.execute(
                    text(
                        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE"
                    )
                )
                conn.commit()
            except Exception as e:
                logger.warning(f"Note: {str(e)}")
                conn.rollback()

            # Update existing exercises that contain the AI prefix
            from app.core.constants import Messages

            prefix = Messages.AI_EXERCISE_PREFIX
            try:
                conn.execute(
                    text(
                        "UPDATE exercises SET ai_generated = TRUE "
                        "WHERE title LIKE :pat OR question LIKE :pat"
                    ),
                    {"pat": f"%{prefix}%"},
                )
                conn.commit()
            except Exception as e:
                logger.warning(f"Note: {str(e)}")
                conn.rollback()

            # Create results table
            _execute_ddl_statements(conn, ResultQueries.CREATE_TABLE)
            conn.commit()

            # Create user_stats table
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS user_stats (
                        id SERIAL PRIMARY KEY,
                        exercise_type VARCHAR(50) NOT NULL,
                        difficulty VARCHAR(50) NOT NULL,
                        total_attempts INTEGER DEFAULT 0,
                        correct_attempts INTEGER DEFAULT 0,
                        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )
            conn.commit()

        logger.success("Database initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        traceback.print_exc()
        sys.exit(1)