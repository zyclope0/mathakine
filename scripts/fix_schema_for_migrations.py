#!/usr/bin/env python
"""
Script pour vérifier et corriger le schéma de la base de données pour les migrations Alembic.
Ce script analyse la base de données actuelle, la compare aux modèles SQLAlchemy et effectue
les corrections nécessaires.
"""
import os
import sys
import logging
from sqlalchemy import inspect, text

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
logger = logging.getLogger('schema_fixer')

# Import des modèles et connexion à la base de données
from app.core.config import settings
from app.db.base import engine, Base
from app.models.user import User
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.logic_challenge import LogicChallenge
from app.models.setting import Setting

def get_existing_tables():
    """Obtenir la liste des tables existantes dans la base de données."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_model_tables():
    """Obtenir la liste des tables définies dans les modèles SQLAlchemy."""
    return Base.metadata.tables.keys()

def verify_column_exists(table_name, column_name):
    """Vérifier si une colonne existe dans une table."""
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def add_column(table_name, column_name, column_type):
    """Ajouter une colonne à une table existante."""
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))
        logger.info(f"Colonne {column_name} ajoutée à la table {table_name}")

def remove_column(table_name, column_name):
    """Supprimer une colonne d'une table existante."""
    with engine.begin() as conn:
        # PostgreSQL
        if settings.DATABASE_URL.startswith('postgresql'):
            conn.execute(text(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}"))
        # SQLite (ne supporte pas DROP COLUMN)
        elif settings.DATABASE_URL.startswith('sqlite'):
            logger.warning(f"SQLite ne supporte pas la suppression directe de colonnes. "
                          f"La colonne {column_name} dans {table_name} ne sera pas supprimée.")
        logger.info(f"Colonne {column_name} supprimée de la table {table_name}")

def remove_table(table_name):
    """Supprimer une table complète si elle n'est plus utilisée."""
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        logger.info(f"Table {table_name} supprimée")

def check_and_fix_specific_issues():
    """Vérifier et corriger des problèmes spécifiques connus."""
    existing_tables = get_existing_tables()
    
    # Vérifier et supprimer les tables obsolètes
    obsolete_tables = ['sqlite_sequence', 'results', 'statistics', 'user_stats', 'schema_version']
    for table in obsolete_tables:
        if table in existing_tables:
            if table == 'sqlite_sequence' and settings.DATABASE_URL.startswith('sqlite'):
                logger.info(f"Table {table} est une table système SQLite, ne pas la supprimer")
                continue
            user_input = input(f"Supprimer la table obsolète {table}? (o/n): ")
            if user_input.lower() == 'o':
                remove_table(table)
    
    # Vérifier la colonne ai_generated dans exercises
    if 'exercises' in existing_tables and verify_column_exists('exercises', 'ai_generated'):
        user_input = input("Supprimer la colonne obsolète 'ai_generated' de la table 'exercises'? (o/n): ")
        if user_input.lower() == 'o':
            remove_column('exercises', 'ai_generated')

def main():
    """Fonction principale du script."""
    logger.info("Démarrage de la vérification et correction du schéma de la base de données")
    
    existing_tables = get_existing_tables()
    model_tables = get_model_tables()
    
    logger.info(f"Tables existantes: {existing_tables}")
    logger.info(f"Tables définies dans les modèles: {model_tables}")
    
    # Tables existantes mais non définies dans les modèles
    extra_tables = set(existing_tables) - set(model_tables)
    if extra_tables:
        logger.warning(f"Tables présentes dans la base de données mais non définies dans les modèles: {extra_tables}")
    
    # Tables définies dans les modèles mais non existantes
    missing_tables = set(model_tables) - set(existing_tables)
    if missing_tables:
        logger.warning(f"Tables définies dans les modèles mais absentes de la base de données: {missing_tables}")
        logger.info("Ces tables seront créées automatiquement par Alembic")
    
    # Vérifier et corriger des problèmes spécifiques
    check_and_fix_specific_issues()
    
    logger.info("Vérification et correction du schéma terminées")
    logger.info("Vous pouvez maintenant exécuter: alembic revision --autogenerate -m 'Initial schema'")

if __name__ == "__main__":
    main() 