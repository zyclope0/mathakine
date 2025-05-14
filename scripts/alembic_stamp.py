#!/usr/bin/env python
"""
Script pour estampiller la base de données à sa version actuelle avec Alembic.
Ce script marque la base de données comme étant "à jour" avec une révision spécifique,
sans effectuer de migrations.
"""
import os
import sys
import logging
from alembic.config import Config
from alembic import command

# Ajouter le répertoire parent au chemin Python
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('alembic_stamper')

# Import de la configuration
from app.core.config import settings

def stamp_database():
    """Estampiller la base de données avec une révision 'base'."""
    try:
        logger.info(f"Estampillage de la base de données: {settings.DATABASE_URL}")
        
        # Créer une configuration Alembic
        alembic_cfg = Config(os.path.join(parent_dir, "alembic.ini"))
        
        # Surcharger l'URL de la base de données pour s'assurer d'utiliser la bonne
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        
        # Créer une révision de base et marquer la base de données comme étant à cette révision
        logger.info("Création de la révision 'base'...")
        revision = "base"  # La révision sera 'base' (la plus ancienne)
        
        # Estampiller la base de données à cette révision
        command.stamp(alembic_cfg, revision)
        logger.info(f"Base de données estampillée avec succès à la révision '{revision}'.")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'estampillage de la base de données: {e}")
        return False

def main():
    """Fonction principale."""
    logger.info("Démarrage de l'estampillage de la base de données...")
    
    success = stamp_database()
    
    if success:
        logger.info("Estampillage de la base de données terminé avec succès.")
        logger.info("Vous pouvez maintenant exécuter: alembic revision --autogenerate -m 'Première migration'")
    else:
        logger.error("Échec de l'estampillage de la base de données.")

if __name__ == "__main__":
    main() 