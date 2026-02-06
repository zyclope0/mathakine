#!/usr/bin/env python3
"""
Migration pour ajouter les colonnes success_count et attempt_count à logic_challenges.
Utilisé pour l'optimisation PERF-3.1.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.base import SessionLocal
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def add_challenge_counters():
    """Ajoute les colonnes success_count et attempt_count"""
    db = SessionLocal()
    
    try:
        # Vérifier si les colonnes existent déjà
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'logic_challenges' 
            AND column_name IN ('success_count', 'attempt_count')
        """)
        existing_columns = [row[0] for row in db.execute(check_query).fetchall()]
        
        if 'success_count' not in existing_columns:
            logger.info("Ajout de la colonne success_count...")
            db.execute(text("""
                ALTER TABLE logic_challenges 
                ADD COLUMN success_count INTEGER DEFAULT 0
            """))
            db.commit()
            logger.info("Colonne success_count ajoutée avec succès")
        else:
            logger.info("Colonne success_count existe déjà")
        
        if 'attempt_count' not in existing_columns:
            logger.info("Ajout de la colonne attempt_count...")
            db.execute(text("""
                ALTER TABLE logic_challenges 
                ADD COLUMN attempt_count INTEGER DEFAULT 0
            """))
            db.commit()
            logger.info("Colonne attempt_count ajoutée avec succès")
        else:
            logger.info("Colonne attempt_count existe déjà")
        
        # Initialiser les valeurs existantes
        logger.info("Initialisation des compteurs existants...")
        db.execute(text("""
            UPDATE logic_challenges lc
            SET attempt_count = (
                SELECT COUNT(*) 
                FROM logic_challenge_attempts lca 
                WHERE lca.challenge_id = lc.id
            ),
            success_count = (
                SELECT COUNT(*) 
                FROM logic_challenge_attempts lca 
                WHERE lca.challenge_id = lc.id AND lca.is_correct = true
            ),
            success_rate = CASE 
                WHEN (
                    SELECT COUNT(*) 
                    FROM logic_challenge_attempts lca 
                    WHERE lca.challenge_id = lc.id
                ) > 0 
                THEN ROUND((
                    SELECT COUNT(*) 
                    FROM logic_challenge_attempts lca 
                    WHERE lca.challenge_id = lc.id AND lca.is_correct = true
                )::float / (
                    SELECT COUNT(*) 
                    FROM logic_challenge_attempts lca 
                    WHERE lca.challenge_id = lc.id
                )::float * 100, 2)
                ELSE 0
            END
        """))
        db.commit()
        logger.info("Compteurs et success_rate initialisés avec succès")
        
        return 0
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la migration: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 MIGRATION: Ajout des compteurs de challenges")
    print("=" * 80)
    print()
    sys.exit(add_challenge_counters())

