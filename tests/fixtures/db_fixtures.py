"""
Fixtures de base de données pour les tests,
facilitant les tests avec PostgreSQL.
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.utils.db_helpers import get_enum_value


def get_test_database_url():
    """Récupère l'URL de la base de données depuis l'environnement ou utilise PostgreSQL par défaut."""
    return settings.TEST_DATABASE_URL


@pytest.fixture(scope="session")
def test_database_url():
    """Fixture qui fournit l'URL de la base de données de test."""
    return get_test_database_url()


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Crée le moteur de base de données pour les tests."""
    engine = create_engine(
        test_database_url,
        # PostgreSQL ne nécessite pas de configuration spéciale pour le threading
        pool_pre_ping=True,
        echo=False,  # Mettre à True pour voir les requêtes SQL
    )
    return engine


@pytest.fixture(scope="session")
def create_test_tables(test_engine):
    """Crée les tables de test."""
    # PostgreSQL utilise des schémas avancés
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_session(test_engine, create_test_tables):
    """Crée une session de test avec rollback automatique."""
    connection = test_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
