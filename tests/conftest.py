import sys
import os
import pytest
from pathlib import Path

# Ajouter le répertoire parent au sys.path pour permettre l'import de app
sys.path.insert(0, str(Path(__file__).parent.parent))

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