#!/usr/bin/env python3
"""
Script pour vérifier les valeurs acceptées par les enums PostgreSQL.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings
from loguru import logger

def check_enum_values():
    """Vérifie les valeurs acceptées par les enums PostgreSQL."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Vérifier les valeurs de l'enum logicchallengetype
        result = conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = 'logicchallengetype'::regtype
            ORDER BY enumsortorder;
        """))
        
        logger.info("Valeurs acceptées par l'enum logicchallengetype:")
        challenge_types = []
        for row in result:
            challenge_types.append(row.enumlabel)
            logger.info(f"  - '{row.enumlabel}'")
        
        # Vérifier les valeurs de l'enum agegroup
        result = conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = 'agegroup'::regtype
            ORDER BY enumsortorder;
        """))
        
        logger.info("\nValeurs acceptées par l'enum agegroup:")
        age_groups = []
        for row in result:
            age_groups.append(row.enumlabel)
            logger.info(f"  - '{row.enumlabel}'")
        
        logger.info(f"\n✅ Types acceptés: {challenge_types}")
        logger.info(f"✅ Groupes d'âge acceptés: {age_groups}")
    
    engine.dispose()

if __name__ == "__main__":
    check_enum_values()

