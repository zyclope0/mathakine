"""
Database initialization and management for Mathakine.

This module centralizes database operations for the enhanced server,
providing initialization, connection management, and utility functions.

Note: Le DDL (exercises, results, user_stats) est désormais géré par Alembic
(migration 20260222_legacy_tables). init_database() est un no-op au startup :
les migrations s'exécutent via `alembic upgrade head` avant le démarrage du serveur.
"""

import os

import psycopg2
from dotenv import load_dotenv

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

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


def init_database():
    """
    No-op au startup : le DDL est géré par Alembic (migration 20260222_legacy_tables).
    Conservé pour compatibilité avec server/app.py startup.
    """
    logger.info("Database init: DDL géré par Alembic (alembic upgrade head au build)")
