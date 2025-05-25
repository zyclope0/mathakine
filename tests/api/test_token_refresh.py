import json
"""
Tests du mécanisme de rafraîchissement des tokens.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.utils.db_helpers import get_enum_value

client = TestClient(app)

def test_refresh_token_valid(refresh_token_client):
    """Teste le rafraîchissement d'un token avec un refresh token valide."""
    # Récupérer le client et le refresh token
    client = refresh_token_client["client"]
    refresh_token = refresh_token_client["refresh_token"]
    
    # Appeler l'endpoint de rafraîchissement
    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    
    # Vérifier que le rafraîchissement a réussi
    assert response.status_code == 200, f"Le code d'état devrait être 200, reçu {response.status_code}"
    
    # Vérifier la structure de la réponse
    data = response.json()
    assert "access_token" in data, "La réponse devrait contenir un nouveau token d'accès"
    assert "token_type" in data, "La réponse devrait contenir le type de token"
    assert data["token_type"] == "bearer", "Le type de token devrait être 'bearer'"
    
    # Vérifier que le nouveau token est valide
    new_token = data["access_token"]
    headers = {"Authorization": f"Bearer {new_token}"}
    
    # Essayer d'accéder à une ressource protégée avec le nouveau token
    resource_response = client.get("/api/exercises/", headers=headers)
    assert resource_response.status_code == 200, "Le nouveau token devrait permettre l'accès aux ressources protégées"

def test_refresh_token_invalid():
    """Teste le rafraîchissement avec un refresh token invalide."""
    # Créer un token invalid (format valide mais non signé correctement)
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnZhbGlkX3VzZXIiLCJyb2xlIjoicGFkYXdhbiIsInR5cGUiOiJyZWZyZXNoIn0.invalid_signature"
    
    # Appeler l'endpoint de rafraîchissement
    response = client.post("/api/auth/refresh", json={"refresh_token": invalid_token})
    
    # Vérifier que le rafraîchissement a échoué
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    assert any(keyword in data["detail"].lower() for keyword in ["invalide", "invalid"]), "Le message devrait indiquer que le token est invalide"

def test_refresh_token_wrong_type(refresh_token_client):
    """Teste le rafraîchissement avec un token d'accès au lieu d'un refresh token."""
    # Récupérer le client et le token d'accès (pas le refresh token)
    client = refresh_token_client["client"]
    access_token = refresh_token_client["access_token"]
    
    # Appeler l'endpoint de rafraîchissement avec le mauvais type de token
    response = client.post("/api/auth/refresh", json={"refresh_token": access_token})
    
    # Vérifier que le rafraîchissement a échoué
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    assert any(keyword in data["detail"].lower() for keyword in ["invalide", "invalid", "type"]), "Le message devrait indiquer que le token est du mauvais type"

def test_refresh_token_expired():
    """Teste le rafraîchissement avec un refresh token expiré."""
    # Créer un refresh token expiré (avec une date d'expiration dans le passé)
    payload = {
        "sub": "test_user_expired",
        "role": "padawan",
        "type": "refresh",
        "exp": datetime.now(timezone.utc) - timedelta(days=1)  # Expiré depuis 1 jour
    }
    
    # Encoder le token avec la clé secrète
    expired_refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Appeler l'endpoint de rafraîchissement
    response = client.post("/api/auth/refresh", json={"refresh_token": expired_refresh_token})
    
    # Vérifier que le rafraîchissement a échoué
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    assert any(keyword in data["detail"].lower() for keyword in ["expiré", "expired"]), "Le message devrait indiquer que le token est expiré" 