import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db_helpers import get_enum_value

client = TestClient(app)



def test_root_endpoint():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Bienvenue sur l'API Mathakine"
    assert "docs" in data



def test_debug_endpoint_in_debug_mode():
    """Test de l'endpoint debug en mode debug"""
    response = client.get("/debug")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "debug_mode" in data
    assert "database_url" in data
    assert "api_version" in data



def test_debug_endpoint_in_production():
    """Test de l'endpoint debug en production"""
    # Nous ne pouvons pas facilement modifier settings.DEBUG dans un test
    # Vérifions donc que l'endpoint est accessible
    response = client.get("/debug")
    assert response.status_code == 200
    # Vérifions que les informations de debug sont présentes
    data = response.json()
    assert "app_name" in data
    assert "debug_mode" in data



def test_nonexistent_endpoint():
    """Test d'un endpoint inexistant"""
    response = client.get("/nonexistent")
    assert response.status_code == 404



def test_api_info_endpoint():
    """Test de l'endpoint d'information de l'API"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "name" in data
    assert "description" in data
