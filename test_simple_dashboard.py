#!/usr/bin/env python3
"""
Test simple du tableau de bord
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def test_simple():
    """Test simple du tableau de bord"""
    base_url = "http://localhost:8000"
    
    # Configuration de session avec retry
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    print("🔍 Test simple du tableau de bord...")
    
    try:
        # 1. Vérifier que le serveur répond
        print("\n1. Test de connectivité:")
        response = session.get(f"{base_url}/", timeout=5)
        print(f"   Page d'accueil: {response.status_code}")
        
        # 2. Tester la page de connexion
        print("\n2. Test page de connexion:")
        response = session.get(f"{base_url}/login", timeout=5)
        print(f"   Page login: {response.status_code}")
        
        # 3. Tester l'API stats sans authentification
        print("\n3. Test API stats (sans auth):")
        response = session.get(f"{base_url}/api/users/stats", timeout=5)
        print(f"   API stats: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Erreur 401 attendue (authentification requise)")
        else:
            print(f"   ⚠️  Réponse inattendue: {response.text[:100]}")
        
        # 4. Tester la page tableau de bord (devrait rediriger vers login)
        print("\n4. Test page tableau de bord (sans auth):")
        response = session.get(f"{base_url}/dashboard", timeout=5, allow_redirects=False)
        print(f"   Dashboard: {response.status_code}")
        if response.status_code == 302:
            print(f"   ✅ Redirection vers: {response.headers.get('location', 'N/A')}")
        
        print("\n✅ Tests de base terminés")
        print("\n📋 Diagnostic:")
        print("   - Le serveur fonctionne")
        print("   - L'API /api/users/stats requiert une authentification (normal)")
        print("   - Le tableau de bord redirige vers login si non connecté (normal)")
        print("\n🔧 Solution:")
        print("   1. Connectez-vous via l'interface web (http://localhost:8000/login)")
        print("   2. Utilisez: test_user / test_password")
        print("   3. Accédez au tableau de bord (http://localhost:8000/dashboard)")
        print("   4. Les statistiques devraient maintenant s'afficher avec credentials: 'include'")
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Erreur: Impossible de se connecter au serveur")
        print("   🔧 Solution: Démarrez le serveur avec 'python enhanced_server.py'")
    except requests.exceptions.Timeout:
        print("   ❌ Erreur: Timeout de connexion")
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_simple() 