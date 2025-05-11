"""
Fixtures pour les sessions de base de données à utiliser dans les tests.
Ce module fournit des sessions de base de données préconfigurées,
facilitant les tests avec SQLite ou PostgreSQL.
"""
import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.services.db_init_service import create_test_users, create_test_exercises




def get_database_url():
    """Récupère l'URL de la base de données depuis l'environnement ou utilise SQLite par défaut."""
    return os.environ.get("TEST_DATABASE_URL", "sqlite:///./test.db")


@pytest.fixture(scope="session")


def db_engine():
    """Crée un moteur de base de données pour les tests."""
    database_url = get_database_url()

    # Créer le moteur avec NullPool pour éviter les problèmes de connexions persistantes
    engine = create_engine(
        database_url,
        poolclass=NullPool,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )

    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Nettoyer après les tests
    if database_url.startswith("sqlite"):
        Base.metadata.drop_all(bind=engine)


@pytest.fixture


def db_session(db_engine):
    """Fournit une session de base de données pour les tests."""
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()  # Annuler les modifications non validées
        session.close()


@pytest.fixture


def empty_db_session(db_engine):
    """Fournit une session de base de données vide."""
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    try:
        # Supprimer toutes les données existantes
        tables = Base.metadata.tables.keys()
        for table in reversed(list(tables)):
            session.execute(text(f"DELETE FROM {table}"))
        session.commit()

        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture


def populated_db_session(db_engine):
    """Fournit une session de base de données préremplie avec des données de test."""
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    try:
        # Supprimer toutes les données existantes
        tables = Base.metadata.tables.keys()
        for table in reversed(list(tables)):
            session.execute(text(f"DELETE FROM {table}"))
        session.commit()

        # Créer des données de test
        create_test_users(session)
        create_test_exercises(session)

        # Valider les modifications
        session.commit()

        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture


def has_tables(db_engine):
    """Vérifie quelles tables existent dans la base de données."""
    inspector = db_engine.dialect.inspector
    existing_tables = inspector.get_table_names()

    table_exists = {
        "users": "users" in existing_tables,
        "exercises": "exercises" in existing_tables,
        "attempts": "attempts" in existing_tables,
        "logic_challenges": "logic_challenges" in existing_tables
    }

    return table_exists


@pytest.fixture


def valid_values():
    """Retourne les valeurs valides pour les champs énumérés."""
    return {
        "roles": [role.value.lower() for role in UserRole],
        "exercise_types": [e_type.value.lower() for e_type in ExerciseType],
        "difficulties": [level.value.lower() for level in DifficultyLevel],
        "challenge_types": [c_type.value.lower() for c_type in LogicChallengeType],
        "age_groups": [group.value.lower() for group in AgeGroup]
    }
