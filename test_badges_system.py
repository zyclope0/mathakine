#!/usr/bin/env python3
"""
Script de test pour le système de badges et achievements
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "TestBadges",
    "password": "Test123!"
}

def test_login():
    """Tester la connexion"""
    print("🔐 Test de connexion...")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
    
    if response.status_code == 302:
        print("✅ Connexion réussie")
        # Récupérer les cookies de session
        cookies = response.cookies
        return cookies
    else:
        print(f"❌ Échec de connexion: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def test_badges_endpoints(cookies):
    """Tester les endpoints de badges"""
    print("\n🎖️ Test des endpoints de badges...")
    
    # Test 1: Récupérer les badges de l'utilisateur
    print("1. Test GET /api/badges/user")
    response = requests.get(f"{BASE_URL}/api/badges/user", cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Badges utilisateur récupérés")
        print(f"   - Badges obtenus: {len(data.get('data', {}).get('earned_badges', []))}")
        user_stats = data.get('data', {}).get('user_stats', {})
        print(f"   - Points: {user_stats.get('total_points', 0)}")
        print(f"   - Niveau: {user_stats.get('current_level', 1)}")
        print(f"   - Rang Jedi: {user_stats.get('jedi_rank', 'youngling')}")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")
    
    # Test 2: Récupérer les badges disponibles
    print("\n2. Test GET /api/badges/available")
    response = requests.get(f"{BASE_URL}/api/badges/available", cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        badges = data.get('data', [])
        print(f"✅ {len(badges)} badges disponibles")
        for badge in badges[:3]:  # Afficher les 3 premiers
            print(f"   - {badge['name']}: {badge['description']}")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")
    
    # Test 3: Vérification forcée des badges
    print("\n3. Test POST /api/badges/check")
    response = requests.post(f"{BASE_URL}/api/badges/check", cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Vérification des badges réussie")
        print(f"   - Nouveaux badges: {data.get('badges_earned', 0)}")
        print(f"   - Message: {data.get('message', 'Aucun message')}")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")
    
    # Test 4: Statistiques de gamification
    print("\n4. Test GET /api/badges/stats")
    response = requests.get(f"{BASE_URL}/api/badges/stats", cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Statistiques de gamification récupérées")
        stats_data = data.get('data', {})
        user_stats = stats_data.get('user_stats', {})
        performance = stats_data.get('performance', {})
        print(f"   - Points Force: {user_stats.get('total_points', 0)}")
        print(f"   - Tentatives totales: {performance.get('total_attempts', 0)}")
        print(f"   - Taux de réussite: {performance.get('success_rate', 0)}%")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")

def test_page_badges(cookies):
    """Tester l'accès à la page badges"""
    print("\n🌐 Test de la page badges...")
    
    response = requests.get(f"{BASE_URL}/badges", cookies=cookies)
    
    if response.status_code == 200:
        print("✅ Page badges accessible")
        if "Mes Badges" in response.text:
            print("✅ Contenu de la page correct")
        else:
            print("⚠️ Contenu de la page inattendu")
    else:
        print(f"❌ Erreur d'accès à la page: {response.status_code}")

def test_exercise_submission(cookies):
    """Tester la soumission d'un exercice pour déclencher les badges"""
    print("\n📝 Test de soumission d'exercice pour déclencher les badges...")
    
    # Simuler la soumission d'une réponse
    exercise_data = {
        "exercise_id": 1,  # ID d'un exercice existant
        "answer": "5",     # Réponse correcte
        "time_spent": 3    # Temps en secondes
    }
    
    response = requests.post(f"{BASE_URL}/api/submit-answer", json=exercise_data, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Réponse soumise avec succès")
        print(f"   - Réponse correcte: {data.get('is_correct', False)}")
        
        # Vérifier si des badges ont été obtenus
        new_badges = data.get('new_badges', [])
        if new_badges:
            print(f"🎉 {len(new_badges)} nouveaux badges obtenus!")
            for badge in new_badges:
                print(f"   - {badge['name']}: {badge['star_wars_title']}")
        else:
            print("   - Aucun nouveau badge cette fois")
    else:
        print(f"❌ Erreur de soumission: {response.status_code} - {response.text}")

def main():
    """Fonction principale de test"""
    print("🚀 Test du système de badges Mathakine")
    print("=" * 50)
    
    # Test de connexion
    cookies = test_login()
    if not cookies:
        print("❌ Impossible de continuer sans connexion")
        return
    
    # Tests des endpoints
    test_badges_endpoints(cookies)
    
    # Test de la page web
    test_page_badges(cookies)
    
    # Test de soumission d'exercice
    test_exercise_submission(cookies)
    
    print("\n" + "=" * 50)
    print("🎯 Tests terminés!")
    print("\n💡 Pour tester manuellement:")
    print(f"   - Ouvrez {BASE_URL}/badges dans votre navigateur")
    print(f"   - Connectez-vous avec {TEST_USER['username']}")
    print(f"   - Résolvez quelques exercices pour débloquer des badges")

if __name__ == "__main__":
    main() 