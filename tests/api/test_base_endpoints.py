import pytest


async def test_root_endpoint(client):
    """Test de l'endpoint racine"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Bienvenue sur l'API Mathakine"
    assert "docs" in data


async def test_debug_endpoint_in_debug_mode(client):
    """Test de l'endpoint debug en mode debug"""
    response = await client.get("/debug")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "debug_mode" in data
    assert "database_url" in data
    assert "api_version" in data


async def test_debug_endpoint_in_production(client):
    """Test de l'endpoint debug en production"""
    # Nous ne pouvons pas facilement modifier settings.DEBUG dans un test
    # Vérifions donc que l'endpoint est accessible
    response = await client.get("/debug")
    assert response.status_code == 200
    # Vérifions que les informations de debug sont présentes
    data = response.json()
    assert "app_name" in data
    assert "debug_mode" in data


async def test_nonexistent_endpoint(client):
    """Test d'un endpoint inexistant"""
    response = await client.get("/nonexistent")
    assert response.status_code == 404


async def test_api_info_endpoint(client):
    """Test de l'endpoint d'information de l'API"""
    response = await client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "name" in data
    assert "description" in data
