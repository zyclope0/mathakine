"""
Script pour appliquer la migration Alembic pour la vérification d'email
À exécuter sur Render ou en local pour ajouter les colonnes nécessaires
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from loguru import logger

def apply_migration():
    """Applique la migration pour ajouter les colonnes de vérification email"""
    
    database_url = settings.DATABASE_URL
    logger.info(f"Connexion à la base de données: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Vérifier si les colonnes existent déjà
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('is_email_verified', 'email_verification_token', 'email_verification_sent_at')
            """)
            
            result = conn.execute(check_query)
            existing_columns = {row[0] for row in result}
            
            logger.info(f"Colonnes existantes: {existing_columns}")
            
            # Ajouter is_email_verified si elle n'existe pas
            if 'is_email_verified' not in existing_columns:
                logger.info("Ajout de la colonne is_email_verified...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_email_verified BOOLEAN NOT NULL DEFAULT false
                """))
                conn.commit()
                logger.info("✅ Colonne is_email_verified ajoutée")
            else:
                logger.info("✅ Colonne is_email_verified existe déjà")
            
            # Ajouter email_verification_token si elle n'existe pas
            if 'email_verification_token' not in existing_columns:
                logger.info("Ajout de la colonne email_verification_token...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email_verification_token VARCHAR(255)
                """))
                conn.commit()
                logger.info("✅ Colonne email_verification_token ajoutée")
            else:
                logger.info("✅ Colonne email_verification_token existe déjà")
            
            # Ajouter email_verification_sent_at si elle n'existe pas
            if 'email_verification_sent_at' not in existing_columns:
                logger.info("Ajout de la colonne email_verification_sent_at...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email_verification_sent_at TIMESTAMP WITH TIME ZONE
                """))
                conn.commit()
                logger.info("✅ Colonne email_verification_sent_at ajoutée")
            else:
                logger.info("✅ Colonne email_verification_sent_at existe déjà")
            
            # Créer l'index si nécessaire
            index_query = text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'users' 
                AND indexname = 'ix_users_email_verification_token'
            """)
            
            result = conn.execute(index_query)
            index_exists = result.fetchone() is not None
            
            if not index_exists:
                logger.info("Création de l'index ix_users_email_verification_token...")
                conn.execute(text("""
                    CREATE INDEX ix_users_email_verification_token 
                    ON users(email_verification_token)
                """))
                conn.commit()
                logger.info("✅ Index créé")
            else:
                logger.info("✅ Index existe déjà")
            
            logger.info("🎉 Migration appliquée avec succès !")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'application de la migration: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    logger.info("Démarrage de l'application de la migration...")
    apply_migration()
    logger.info("Migration terminée.")

