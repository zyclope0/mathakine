#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table logic_challenges dans PostgreSQL.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings
from loguru import logger

def check_table_structure():
    """Vérifie la structure de la table logic_challenges."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Vérifier le type de la colonne challenge_type
        result = conn.execute(text("""
            SELECT 
                column_name, 
                data_type, 
                udt_name,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'logic_challenges' 
            AND column_name IN ('challenge_type', 'age_group')
            ORDER BY column_name;
        """))
        
        logger.info("Structure des colonnes challenge_type et age_group:")
        for row in result:
            logger.info(f"  {row.column_name}: {row.data_type} (udt: {row.udt_name})")
        
        # Vérifier s'il y a une contrainte CHECK
        result = conn.execute(text("""
            SELECT 
                conname as constraint_name,
                pg_get_constraintdef(oid) as constraint_definition
            FROM pg_constraint
            WHERE conrelid = 'logic_challenges'::regclass
            AND contype = 'c';
        """))
        
        logger.info("\nContraintes CHECK sur logic_challenges:")
        for row in result:
            logger.info(f"  {row.constraint_name}: {row.constraint_definition}")
        
        # Vérifier les valeurs existantes (s'il y en a)
        result = conn.execute(text("""
            SELECT DISTINCT challenge_type, age_group 
            FROM logic_challenges 
            LIMIT 10;
        """))
        
        logger.info("\nValeurs existantes dans la table:")
        for row in result:
            logger.info(f"  challenge_type: '{row.challenge_type}', age_group: '{row.age_group}'")
    
    engine.dispose()

if __name__ == "__main__":
    check_table_structure()

