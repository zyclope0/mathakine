#!/usr/bin/env python3
"""
Script pour créer une base de données de test séparée.
Ce script crée une nouvelle base PostgreSQL pour les tests et l'initialise avec le schéma.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from urllib.parse import urlparse, urlunparse

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.init_db import create_tables_with_test_data
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def create_test_database():
    """
    Crée une base de données de test séparée.
    
    Si DATABASE_URL pointe vers 'mathakine', crée 'mathakine_test'.
    Sinon, crée une base avec le suffixe '_test'.
    """
    # Récupérer DATABASE_URL
    database_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    
    if not database_url:
        logger.error("DATABASE_URL n'est pas définie")
        return False
    
    # Parser l'URL pour extraire les informations
    parsed = urlparse(database_url)
    
    # Extraire le nom de la base actuelle
    current_db = parsed.path.lstrip('/')
    
    # Créer le nom de la base de test
    if current_db.endswith('_test'):
        logger.warning(f"La base '{current_db}' est déjà une base de test")
        test_db_name = current_db
    else:
        test_db_name = f"{current_db}_test"
    
    # Construire l'URL de connexion à PostgreSQL (sans nom de base)
    # Pour créer une base, on doit se connecter à la base 'postgres' par défaut
    admin_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        '/postgres',  # Se connecter à la base 'postgres' par défaut
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    logger.info(f"Connexion à PostgreSQL pour créer la base '{test_db_name}'...")
    
    try:
        # Se connecter à PostgreSQL
        conn = psycopg2.connect(admin_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Vérifier si la base existe déjà
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (test_db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            logger.warning(f"La base de données '{test_db_name}' existe déjà")
            response = input("Voulez-vous la réinitialiser ? (o/N): ").strip().lower()
            if response == 'o':
                # Terminer les connexions actives
                cursor.execute(
                    f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{test_db_name}' AND pid <> pg_backend_pid()"
                )
                # Supprimer la base
                cursor.execute(f"DROP DATABASE {test_db_name}")
                logger.info(f"Base '{test_db_name}' supprimée")
            else:
                logger.info("Opération annulée")
                cursor.close()
                conn.close()
                return False
        
        # Créer la base de données
        cursor.execute(f'CREATE DATABASE {test_db_name}')
        logger.success(f"Base de données '{test_db_name}' créée avec succès")
        
        cursor.close()
        conn.close()
        
        # Construire l'URL de la base de test
        test_db_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            f'/{test_db_name}',
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        logger.info(f"Initialisation du schéma dans '{test_db_name}'...")
        
        # Initialiser le schéma dans la nouvelle base
        # Temporairement définir DATABASE_URL pour l'initialisation
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = test_db_url
        
        try:
            # Réinitialiser l'engine pour utiliser la nouvelle URL
            from app.db.base import engine
            engine.dispose()  # Fermer les connexions existantes
            
            # Créer les tables et les données de test
            create_tables_with_test_data()
            
            logger.success(f"Base de données de test '{test_db_name}' initialisée avec succès")
            logger.info(f"\n✅ Base de test créée !")
            logger.info(f"   URL: {test_db_url}")
            logger.info(f"\n📝 Pour l'utiliser, définissez dans votre environnement :")
            logger.info(f"   TEST_DATABASE_URL={test_db_url}")
            
            return True
            
        finally:
            # Restaurer l'URL originale
            if original_db_url:
                os.environ["DATABASE_URL"] = original_db_url
            else:
                os.environ.pop("DATABASE_URL", None)
        
    except psycopg2.Error as e:
        logger.error(f"Erreur PostgreSQL lors de la création de la base: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la création de la base de test: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🔧 Création d'une base de données de test")
    print("=" * 60)
    print()
    
    # Vérification de sécurité
    database_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    is_production = (
        os.getenv("NODE_ENV") == "production" or 
        os.getenv("ENVIRONMENT") == "production" or
        os.getenv("MATH_TRAINER_PROFILE") == "prod" or
        "render.com" in database_url.lower()
    )
    
    if is_production:
        print("⚠️  ATTENTION: Vous êtes en environnement de production")
        print(f"   DATABASE_URL: {database_url[:50]}...")
        print()
        response = input("Voulez-vous vraiment créer une base de test en production ? (o/N): ").strip().lower()
        if response != 'o':
            print("Opération annulée")
            return 1
    
    success = create_test_database()
    
    if success:
        print()
        print("=" * 60)
        print("✅ Base de test créée avec succès !")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("❌ Échec de la création de la base de test")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

