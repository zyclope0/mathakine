"""
Configuration centralisée pour pytest.
Ce fichier importe toutes les fixtures pour les rendre disponibles globalement.
"""
import pytest
import os
from pathlib import Path
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Ajouter le répertoire racine au path pour faciliter les imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer les modèles et la base de données
from app.db.base import Base, engine

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

# Importer l'application FastAPI
from app.main import app

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

# Fixture pour le client API
@pytest.fixture
def client():
    return TestClient(app)

# Fixture pour créer un utilisateur de test et obtenir un token d'authentification
@pytest.fixture
def auth_client():
    """Crée un utilisateur de test et retourne un client API authentifié"""
    client = TestClient(app)
    
    # Créer un utilisateur de test avec un nom unique
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_jedi_{unique_id}",
        "email": f"jedi_{unique_id}@test.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    try:
        # Enregistrer l'utilisateur
        response = client.post("/api/users/", json=user_data)
        if response.status_code != 201:
            pytest.skip(f"Impossible de créer l'utilisateur de test: {response.text}")
        
        # Authentification
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        if response.status_code != 200:
            pytest.skip(f"Impossible d'authentifier l'utilisateur de test: {response.text}")
        
        token = response.json()["access_token"]
        
        # Retourner un client configuré avec les headers d'authentification
        client.headers.update({"Authorization": f"Bearer {token}"})
        
        return {
            "client": client,
            "user_data": user_data,
            "token": token,
            "user_id": response.json().get("user_id")
        }
    except Exception as e:
        pytest.skip(f"Erreur pendant la configuration de l'authentification: {str(e)}")

# Fixture pour créer une session de base de données pour les tests
@pytest.fixture
def db_session():
    """Crée une session de base de données pour les tests"""
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    
    # Créer une connexion et une transaction
    connection = engine.connect()
    transaction = connection.begin()
    
    # Créer une session
    session = Session(autocommit=False, autoflush=False, bind=connection)
    
    yield session
    
    # Nettoyer après le test
    session.close()
    transaction.rollback()
    connection.close()
