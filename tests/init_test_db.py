#!/usr/bin/env python
"""
Script d'initialisation de la base de données de test pour Mathakine.
Ce script réinitialise la base de données et la remplit avec des données de test.
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.services.db_init_service import (
    create_test_users,
    create_test_exercises,
    create_test_attempts,
    create_test_logic_challenges
)



def initialize_test_database():
    """
    Initialise la base de données de test avec des tables et des données.
    """
    print("Initialisation de la base de données de test...")

    # Configurer l'environnement de test
    os.environ["TESTING"] = "true"

    # Déterminer l'URL de la base de données
    db_url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")

    if not db_url:
        # Utiliser SQLite par défaut si aucune URL n'est spécifiée
        db_url = "sqlite:///./test.db"
        print(f"Aucune URL de base de données spécifiée, utilisation de SQLite: {db_url}")
    else:
        print(f"Utilisation de la base de données: {db_url}")

    # Créer le moteur et les sessions
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(db_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Créer les tables
    print("Création des tables...")
    Base.metadata.drop_all(bind=engine)  # Supprimer toutes les tables existantes
    Base.metadata.create_all(bind=engine)

    # Créer une session
    db = SessionLocal()

    try:
        # Créer les données de test
        print("Création des utilisateurs de test...")
        create_test_users(db)

        print("Création des exercices de test...")
        create_test_exercises(db)

        print("Création des tentatives de test...")
        create_test_attempts(db)

        print("Création des défis logiques de test...")
        create_test_logic_challenges(db)

        # Valider les modifications
        db.commit()
        print("Base de données initialisée avec succès!")

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_test_database()
