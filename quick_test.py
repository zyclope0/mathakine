#!/usr/bin/env python3
"""Test rapide de l'API"""

import requests
import time

def test_api():
    try:
        print("🧪 Test de l'API...")
        response = requests.get("http://localhost:8000/api/users/stats", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_dashboard():
    try:
        print("🌐 Test du tableau de bord...")
        response = requests.get("http://localhost:8000/dashboard", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Page accessible")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Tests rapides...")
    time.sleep(2)  # Attendre que le serveur soit prêt
    test_api()
    test_dashboard()
    print("🎉 Tests terminés!") 