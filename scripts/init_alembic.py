#!/usr/bin/env python
"""
Script pour initialiser Alembic dans une base de données existante.
Ce script va:
1. Créer la table alembic_version si elle n'existe pas
2. Marquer la dernière migration comme appliquée
"""
import os
import sys
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.core.config import settings
from alembic.config import Config
from alembic import command
from loguru import logger

def init_alembic():
    """
    Initialise Alembic dans la base de données existante
    """
    logger.info(f"Initialisation d'Alembic pour la base de données: {settings.DATABASE_URL}")
    
    # Vérifier si la table alembic_version existe déjà
    engine = create_engine(settings.DATABASE_URL)
    inspect_query = text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
    )
    
    with engine.connect() as conn:
        result = conn.execute(inspect_query).scalar()
        
        if result:
            logger.info("La table alembic_version existe déjà")
        else:
            logger.info("La table alembic_version n'existe pas, création...")
            
            # Créer la table alembic_version
            create_table_query = text(
                "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
            )
            conn.execute(create_table_query)
            logger.success("Table alembic_version créée avec succès")
    
    # Configurer et exécuter la commande Alembic stamp
    alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
    
    try:
        # Marquer la dernière révision comme appliquée
        command.stamp(alembic_cfg, "head")
        logger.success("Base de données marquée avec la dernière révision Alembic")
    except Exception as e:
        logger.error(f"Erreur lors du marquage de la base de données: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_alembic()
    if success:
        logger.info("Initialisation d'Alembic terminée avec succès")
        sys.exit(0)
    else:
        logger.error("Échec de l'initialisation d'Alembic")
        sys.exit(1) 