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
from loguru import logger

from app.db.queries import ExerciseQueries, ResultQueries, UserStatsQueries

# Charger les variables d'environnement depuis .env
load_dotenv(override=True)

def get_database_url() -> str:
    """
    Get the database URL from environment variables.
    
    Returns:
        Database URL as a string
    """
    # Essayer d'abord la variable d'environnement DATABASE_URL
    db_url = os.environ.get("DATABASE_URL", "")
    
    # Si pas définie, construire depuis les variables individuelles
    if not db_url:
        postgres_server = os.getenv("POSTGRES_SERVER", "localhost")
        postgres_user = os.getenv("POSTGRES_USER", "postgres")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
        postgres_db = os.getenv("POSTGRES_DB", "mathakine")
        db_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}/{postgres_db}"
        logger.info(f"Using default DATABASE_URL: postgresql://{postgres_user}:***@{postgres_server}/{postgres_db}")
    
    if not db_url:
        logger.error("DATABASE_URL environment variable not set and no defaults available")
        sys.exit(1)
    
    return db_url

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
    Initialize the database if necessary.
    
    This function creates tables if they don't exist and
    performs other initialization tasks.
    """
    logger.info("Initializing database")
    
    try:
        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Create exercises table if it doesn't exist
            cursor.execute(ExerciseQueries.CREATE_TABLE)

            # Add ai_generated column if it doesn't exist
            try:
                cursor.execute("""
                ALTER TABLE exercises ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE
                """)
                conn.commit()
            except Exception as e:
                logger.warning(f"Note: {str(e)}")
                conn.rollback()
                
            # Update existing exercises that contain the AI prefix
            from app.core.constants import Messages
            try:
                cursor.execute(f"""
                UPDATE exercises
                SET ai_generated = TRUE
                WHERE title LIKE '%{Messages.AI_EXERCISE_PREFIX}%' OR question LIKE '%{Messages.AI_EXERCISE_PREFIX}%'
                """)
                conn.commit()
            except Exception as e:
                logger.warning(f"Note: {str(e)}")
                conn.rollback()
                
            # Create results table if it doesn't exist
            cursor.execute(ResultQueries.CREATE_TABLE)
            
            # Create user_stats table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id SERIAL PRIMARY KEY,
                exercise_type VARCHAR(50) NOT NULL,
                difficulty VARCHAR(50) NOT NULL,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            logger.success("Database initialized successfully")
            
        finally:
            # Always close the connection
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        traceback.print_exc()
        sys.exit(1) 