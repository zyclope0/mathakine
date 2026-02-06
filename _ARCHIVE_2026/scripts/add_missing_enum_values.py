#!/usr/bin/env python3
"""
Script pour ajouter les valeurs manquantes aux enums PostgreSQL.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au path Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings
from loguru import logger

def add_missing_enum_values():
    """Ajoute les valeurs manquantes aux enums PostgreSQL."""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Ajouter VISUAL à logicchallengetype
            logger.info("Ajout de 'VISUAL' à logicchallengetype...")
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_enum 
                        WHERE enumlabel = 'VISUAL' 
                        AND enumtypid = 'logicchallengetype'::regtype
                    ) THEN
                        ALTER TYPE logicchallengetype ADD VALUE 'VISUAL';
                    END IF;
                END $$;
            """))
            conn.commit()
            logger.info("✅ 'VISUAL' ajouté avec succès")
            
            # Ajouter RIDDLE à logicchallengetype
            logger.info("Ajout de 'RIDDLE' à logicchallengetype...")
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_enum 
                        WHERE enumlabel = 'RIDDLE' 
                        AND enumtypid = 'logicchallengetype'::regtype
                    ) THEN
                        ALTER TYPE logicchallengetype ADD VALUE 'RIDDLE';
                    END IF;
                END $$;
            """))
            conn.commit()
            logger.info("✅ 'RIDDLE' ajouté avec succès")
            
            # Vérifier les valeurs finales
            logger.info("\nVérification des valeurs finales...")
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = 'logicchallengetype'::regtype
                ORDER BY enumsortorder;
            """))
            
            values = [row[0] for row in result]
            logger.info(f"✅ Valeurs finales dans logicchallengetype: {values}")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout des valeurs: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    logger.info("🚀 Ajout des valeurs manquantes aux enums PostgreSQL...")
    add_missing_enum_values()
    logger.info("✅ Terminé !")

