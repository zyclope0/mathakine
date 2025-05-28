#!/usr/bin/env python3
"""
Test direct de l'endpoint /api/submit-answer
"""

import requests
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from app.models.exercise import Exercise
from loguru import logger

def test_submit_endpoint():
    """Teste l'endpoint /api/submit-answer directement."""
    logger.info("🧪 Test de l'endpoint /api/submit-answer...")
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    base_url = "http://localhost:8000"
    
    try:
        # 1. Récupérer un exercice depuis la base
        db = SessionLocal()
        try:
            exercise = db.query(Exercise).filter(Exercise.is_active == True).first()
            if not exercise:
                logger.error("❌ Aucun exercice actif trouvé")
                return False
            
            logger.info(f"✅ Exercice trouvé - ID: {exercise.id}, Question: {exercise.question}")
            logger.info(f"   Réponse correcte: {exercise.correct_answer}")
        finally:
            db.close()
        
        # 2. Tester sans authentification
        logger.info("📡 Test 1: Sans authentification")
        response = session.post(f"{base_url}/api/submit-answer", json={
            "exercise_id": exercise.id,
            "answer": exercise.correct_answer,
            "time_spent": 10.0
        })
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text[:200]}...")
        
        # 3. Essayer de se connecter avec ObiWan
        logger.info("🔐 Test 2: Connexion avec ObiWan")
        
        # Essayer plusieurs mots de passe
        passwords = ["jedi123", "password", "obiwan", "ObiWan", "starwars"]
        login_success = False
        
        for password in passwords:
            logger.info(f"   Essai avec mot de passe: {password}")
            
            login_response = session.post(f"{base_url}/api/auth/login", json={
                "username": "ObiWan",
                "password": password
            })
            
            logger.info(f"   Status: {login_response.status_code}")
            
            if login_response.status_code in [200, 302]:
                logger.success(f"✅ Connexion réussie avec: {password}")
                login_success = True
                break
            else:
                logger.info(f"   ❌ Échec avec: {password}")
        
        if not login_success:
            logger.error("❌ Impossible de se connecter avec ObiWan")
            return False
        
        # 4. Tester avec authentification
        logger.info("📡 Test 3: Avec authentification")
        response = session.post(f"{base_url}/api/submit-answer", json={
            "exercise_id": exercise.id,
            "answer": exercise.correct_answer,
            "time_spent": 15.0
        })
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            logger.success("✅ Soumission réussie !")
            logger.info(f"   Correct: {data.get('is_correct')}")
            logger.info(f"   Attempt ID: {data.get('attempt_id')}")
            return True
        else:
            logger.error(f"❌ Échec de la soumission: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale."""
    logger.info("🚀 Test de l'endpoint de soumission...")
    
    print("="*60)
    print("🧪 TEST ENDPOINT SUBMIT-ANSWER")
    print("="*60)
    
    success = test_submit_endpoint()
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    if success:
        print("✅ SUCCÈS: L'endpoint fonctionne correctement")
        print("🎯 Le problème est probablement côté frontend/JavaScript")
    else:
        print("❌ ÉCHEC: Problème avec l'endpoint ou l'authentification")
        print("🔧 Vérifier la configuration du serveur")
    
    logger.success("🎉 Test terminé!")

if __name__ == "__main__":
    main() 