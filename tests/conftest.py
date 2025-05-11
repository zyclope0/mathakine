"""
Configuration centralisée pour pytest.
Ce fichier importe toutes les fixtures pour les rendre disponibles globalement.
"""
import pytest
import os
from pathlib import Path

# Ajouter le répertoire racine au path pour faciliter les imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer les fixtures depuis les fichiers de fixtures
from tests.fixtures.model_fixtures import (
    test_user,
    test_maitre_user,
    test_exercise,
    test_exercises,
    test_attempt,
    test_attempts,
    test_logic_challenge,
    test_logic_challenges
)

from tests.fixtures.db_fixtures import (
    get_database_url,
    db_engine,
    db_session,
    empty_db_session,
    populated_db_session,
    has_tables,
    valid_values
)

# Configuration de l'environnement pour les tests
@pytest.fixture(scope="session", autouse=True)


def setup_test_environment():
    """Configure l'environnement de test automatiquement au début de la session."""
    # Créer le dossier de résultats s'il n'existe pas
    Path("test_results").mkdir(exist_ok=True)

    # Définir les variables d'environnement pour les tests
    os.environ["TESTING"] = "true"

    # Utiliser SQLite par défaut pour les tests
    if "TEST_DATABASE_URL" not in os.environ:
        os.environ["TEST_DATABASE_URL"] = "sqlite:///./test.db"

    yield  # Exécuter les tests

    # Nettoyage après les tests
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except (PermissionError, OSError):
            # Le fichier peut être verrouillé par un processus, ne pas échouer dans ce cas
            pass

# Configuration des fixtures
@pytest.fixture(scope="session")


def test_app():
    """Fixture pour configurer l'application de test"""
    from app.main import app

    # Configurer l'environnement de test
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

    # Retourner l'application
    return app

@pytest.fixture(scope="session")


def test_client():
    """Fixture pour créer un client de test"""
    from fastapi.testclient import TestClient
    from app.main import app

    # Configurer l'environnement de test
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

    # Créer un client de test
    client = TestClient(app)
    return client
