#!/usr/bin/env python
"""
Script pour restaurer les tables supprimées par erreur.
Ce script exécute le fichier SQL qui recrée les tables supprimées
avec leurs structures d'origine.
"""
import os
import sys
import logging

# Ajouter le répertoire parent au chemin Python pour pouvoir importer l'application
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('table_restorer')

# Import de la connexion à la base de données
from app.core.config import settings
from app.db.base import engine
from sqlalchemy import text

def restore_tables():
    """Restaure les tables supprimées en exécutant le script SQL."""
    logger.info("Début de la restauration des tables supprimées...")

    # Chemin vers le script SQL
    sql_script_path = os.path.join(script_dir, 'restore_deleted_tables.sql')
    
    # Vérifier que le fichier SQL existe
    if not os.path.exists(sql_script_path):
        logger.error(f"Le fichier SQL {sql_script_path} est introuvable.")
        return False
    
    # Lire le contenu du script SQL
    with open(sql_script_path, 'r') as f:
        sql_script = f.read()
    
    # Exécuter le script SQL
    try:
        with engine.connect() as conn:
            logger.info("Connexion à la base de données établie.")
            
            # Démarrer une transaction
            with conn.begin():
                # PostgreSQL - exécuter le script SQL complet
                if settings.DATABASE_URL.startswith('postgresql'):
                    conn.execute(text(sql_script))
                    logger.info("Script SQL exécuté avec succès sur PostgreSQL.")
                
                # SQLite - exécuter le script SQL ligne par ligne
                elif settings.DATABASE_URL.startswith('sqlite'):
                    # Remplacer SERIAL par INTEGER pour SQLite
                    sql_script = sql_script.replace('SERIAL', 'INTEGER')
                    # Remplacer TIMESTAMP WITH TIME ZONE par TIMESTAMP pour SQLite
                    sql_script = sql_script.replace('TIMESTAMP WITH TIME ZONE', 'TIMESTAMP')
                    # Supprimer les commentaires COMMENT ON (non supportés par SQLite)
                    sql_script = '\n'.join([line for line in sql_script.split('\n') 
                                          if not line.strip().startswith('COMMENT ON')])
                    
                    # Diviser et exécuter chaque commande séparément
                    commands = sql_script.split(';')
                    for cmd in commands:
                        if cmd.strip():
                            conn.execute(text(cmd))
                    logger.info("Script SQL exécuté avec succès sur SQLite.")
                
                else:
                    logger.error(f"Type de base de données non pris en charge: {settings.DATABASE_URL}")
                    return False
                
            logger.info("Transaction terminée avec succès.")
        
        logger.info("Tables restaurées avec succès.")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script SQL: {e}")
        return False

def main():
    """Fonction principale."""
    logger.info("Démarrage du processus de restauration des tables...")
    
    if restore_tables():
        logger.info("Restauration des tables terminée avec succès.")
        
        # Vérifier que les tables ont bien été créées
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['user_stats', 'statistics', 'results', 'schema_version']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            logger.warning(f"Les tables suivantes n'ont pas été créées: {missing_tables}")
        else:
            logger.info("Toutes les tables ont été correctement créées.")
            
            # Afficher la structure des tables
            for table in expected_tables:
                columns = inspector.get_columns(table)
                logger.info(f"Structure de la table '{table}':")
                for col in columns:
                    logger.info(f"  - {col['name']} ({col['type']})")
    else:
        logger.error("Échec de la restauration des tables.")

if __name__ == "__main__":
    main() 