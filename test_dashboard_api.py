#!/usr/bin/env python3
"""
Script de test pour vérifier l'API du tableau de bord
"""
import requests
import json

def test_dashboard_api():
    """Test de l'API du tableau de bord avec authentification"""
    base_url = "http://localhost:8000"
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    print("🔍 Test de l'API du tableau de bord...")
    
    # 1. Tester l'accès sans authentification
    print("\n1. Test sans authentification:")
    response = session.get(f"{base_url}/api/users/stats")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:100]}")
    
    # 2. Se connecter avec l'utilisateur de test
    print("\n2. Connexion avec l'utilisateur de test:")
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    
    # Désactiver le suivi automatique des redirections pour voir la réponse
    response = session.post(f"{base_url}/api/auth/login", json=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✅ Connexion réussie (redirection)")
        print(f"   Redirection vers: {response.headers.get('location', 'N/A')}")
        
        # Vérifier que les cookies sont définis
        cookies = session.cookies
        print(f"   Cookies reçus: {list(cookies.keys())}")
        
    else:
        print(f"   ❌ Échec de la connexion: {response.text[:200]}")
        return
    
    # 3. Tester l'API avec authentification
    print("\n3. Test avec authentification:")
    response = session.get(f"{base_url}/api/users/stats")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("   ✅ Données reçues:")
            print(f"      - Exercices totaux: {data.get('total_exercises', 0)}")
            print(f"      - Réponses correctes: {data.get('correct_answers', 0)}")
            print(f"      - Taux de réussite: {data.get('success_rate', 0)}%")
            print(f"      - Points d'expérience: {data.get('experience_points', 0)}")
            
            # Vérifier les performances par type
            perf_by_type = data.get('performance_by_type', {})
            if perf_by_type:
                print("      - Performances par type:")
                for ex_type, stats in perf_by_type.items():
                    print(f"        * {ex_type}: {stats.get('completed', 0)} exercices, {stats.get('success_rate', 0)}% réussite")
            else:
                print("      - Aucune performance par type")
                
        except json.JSONDecodeError:
            print(f"   ❌ Erreur de décodage JSON: {response.text[:200]}")
    else:
        print(f"   ❌ Erreur API: {response.text}")

if __name__ == "__main__":
    test_dashboard_api() 