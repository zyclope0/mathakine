#!/usr/bin/env python
"""
Script pour corriger les migrations Alembic et intégrer les tables existantes.
Ce script va créer des modèles SQLAlchemy pour les tables restaurées
afin qu'Alembic puisse les reconnaître.
"""
import os
import sys
import logging
from sqlalchemy import inspect, Column, Integer, String, Float, Boolean, DateTime, text, Table, MetaData

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
logger = logging.getLogger('alembic_fixer')

# Import de la connexion à la base de données et des modèles
from app.core.config import settings
from app.db.base import engine, Base
from sqlalchemy.ext.declarative import declared_attr

# Créer des modèles pour les tables restaurées
class UserStats(Base):
    """Modèle pour la table user_stats."""
    __tablename__ = 'user_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    total_attempts = Column(Integer, server_default=text('0'))
    correct_attempts = Column(Integer, server_default=text('0'))
    last_updated = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    @declared_attr
    def __table_args__(cls):
        return {'comment': 'Table restaurée pour le suivi des statistiques utilisateur par type d\'exercice et difficulté'}

class Statistics(Base):
    """Modèle pour la table statistics."""
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(255), nullable=False)
    exercise_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    total_attempts = Column(Integer, server_default=text('0'), nullable=False)
    correct_attempts = Column(Integer, server_default=text('0'), nullable=False)
    avg_time = Column(Float, server_default=text('0'), nullable=False)
    last_updated = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    @declared_attr
    def __table_args__(cls):
        return {'comment': 'Table restaurée pour le suivi des statistiques par session'}

class Results(Base):
    """Modèle pour la table results."""
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempt_count = Column(Integer, server_default=text('1'))
    time_spent = Column(Float)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    @declared_attr
    def __table_args__(cls):
        return {'comment': 'Table restaurée pour les résultats des exercices'}

class SchemaVersion(Base):
    """Modèle pour la table schema_version."""
    __tablename__ = 'schema_version'
    
    version = Column(Integer, primary_key=True)
    
    @declared_attr
    def __table_args__(cls):
        return {'comment': 'Table restaurée pour le suivi de version du schéma'}

def verify_models_match_tables():
    """Vérifier que les modèles correspondent aux tables dans la base de données."""
    logger.info("Vérification de la correspondance entre les modèles et les tables...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    models_to_check = [
        (UserStats, 'user_stats'),
        (Statistics, 'statistics'),
        (Results, 'results'),
        (SchemaVersion, 'schema_version')
    ]
    
    for model, table_name in models_to_check:
        if table_name not in tables:
            logger.warning(f"Table {table_name} non trouvée dans la base de données!")
            continue
        
        # Vérifier les colonnes
        db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        model_columns = {col.name: col for col in model.__table__.columns}
        
        missing_columns = set(model_columns.keys()) - set(db_columns.keys())
        extra_columns = set(db_columns.keys()) - set(model_columns.keys())
        
        if missing_columns:
            logger.warning(f"Colonnes définies dans le modèle mais absentes de la base: {missing_columns}")
        
        if extra_columns:
            logger.warning(f"Colonnes présentes dans la base mais non définies dans le modèle: {extra_columns}")
        
        if not missing_columns and not extra_columns:
            logger.info(f"Modèle {model.__name__} correspond parfaitement à la table {table_name}")
    
    logger.info("Vérification terminée.")

def update_env_py():
    """Mettre à jour le fichier env.py d'Alembic pour inclure les nouveaux modèles."""
    logger.info("Mise à jour du fichier env.py d'Alembic...")
    
    env_py_path = os.path.join(parent_dir, 'migrations', 'env.py')
    
    if not os.path.exists(env_py_path):
        logger.error(f"Le fichier {env_py_path} n'existe pas!")
        return False
    
    with open(env_py_path, 'r') as f:
        content = f.read()
    
    # Vérifier si les modèles sont déjà importés
    if 'from scripts.fix_alembic_migration import' in content:
        logger.info("Les modèles sont déjà importés dans env.py")
        return True
    
    # Ajouter l'import des modèles
    import_line = "from app.models.logic_challenge import LogicChallenge"
    new_import = import_line + "\nfrom scripts.fix_alembic_migration import UserStats, Statistics, Results, SchemaVersion"
    
    updated_content = content.replace(import_line, new_import)
    
    with open(env_py_path, 'w') as f:
        f.write(updated_content)
    
    logger.info("Fichier env.py mis à jour avec succès")
    return True

def main():
    """Fonction principale."""
    logger.info("Démarrage de la correction des migrations Alembic...")
    
    # Vérifier que les modèles correspondent aux tables
    verify_models_match_tables()
    
    # Mettre à jour env.py
    if update_env_py():
        logger.info("Mise à jour de l'environnement Alembic terminée avec succès.")
        logger.info("Vous pouvez maintenant exécuter: alembic revision --autogenerate -m 'Initial schema'")
    else:
        logger.error("Échec de la mise à jour de l'environnement Alembic.")

if __name__ == "__main__":
    main() 