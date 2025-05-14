#!/usr/bin/env python
"""
Script pour vérifier la structure de la base de données restaurée.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, inspect, text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('db_structure_checker')

# Ajouter le répertoire parent au chemin Python
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Import de la configuration
from app.core.config import settings

def check_db_structure():
    """Vérifier la structure de la base de données."""
    logger.info(f"Connexion à la base de données: {settings.DATABASE_URL}")
    
    # Créer une connexion
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Obtenir un inspecteur
        inspector = inspect(engine)
        
        # Obtenir les tables
        tables = sorted(inspector.get_table_names())
        logger.info(f"Tables dans la base de données ({len(tables)}):")
        for table in tables:
            logger.info(f"  - {table}")
        
        # Pour chaque table, afficher ses colonnes
        for table in tables:
            columns = inspector.get_columns(table)
            logger.info(f"\nColonnes de la table '{table}':")
            for column in columns:
                nullable = "NULL" if column.get('nullable') else "NOT NULL"
                default = f"DEFAULT {column.get('default')}" if column.get('default') else ""
                logger.info(f"  - {column['name']} ({column['type']}) {nullable} {default}")
        
        # Vérifier si des tables importantes existent
        important_tables = ['results', 'statistics', 'user_stats']
        missing_tables = [t for t in important_tables if t not in tables]
        
        if missing_tables:
            logger.warning(f"Tables importantes manquantes: {missing_tables}")
        else:
            logger.info("\nToutes les tables importantes sont présentes.")
        
        # Vérifier les relations entre les tables
        for table in tables:
            foreign_keys = inspector.get_foreign_keys(table)
            if foreign_keys:
                logger.info(f"\nClés étrangères pour la table '{table}':")
                for fk in foreign_keys:
                    logger.info(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la structure de la base de données: {e}")
        return False

def main():
    """Fonction principale."""
    logger.info("Démarrage de la vérification de la structure de la base de données...")
    
    success = check_db_structure()
    
    if success:
        logger.info("Vérification terminée avec succès.")
    else:
        logger.error("Échec de la vérification.")

if __name__ == "__main__":
    main() 