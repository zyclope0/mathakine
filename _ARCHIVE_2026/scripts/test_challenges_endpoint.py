#!/usr/bin/env python3
"""
Script pour tester l'endpoint /api/challenges
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import requests
import json
from loguru import logger

def test_challenges_endpoint():
    """Teste l'endpoint /api/challenges"""
    try:
        # Tester sans authentification d'abord
        logger.info("Test 1: Sans authentification")
        r = requests.get('http://localhost:10000/api/challenges?limit=20&active_only=true')
        logger.info(f"Status: {r.status_code}")
        logger.info(f"Response: {r.text[:500]}")
        
        # Pour tester avec authentification, il faudrait un vrai token
        # Mais d'abord, vérifions si le backend répond
        if r.status_code == 401:
            logger.info("✅ Backend répond correctement avec 401 (non authentifié)")
        elif r.status_code == 500:
            logger.error(f"❌ Erreur 500: {r.text}")
        else:
            logger.info(f"Status inattendu: {r.status_code}")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Impossible de se connecter au backend. Vérifiez qu'il est démarré sur http://localhost:10000")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_challenges_endpoint()

