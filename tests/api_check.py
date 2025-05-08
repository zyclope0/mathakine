"""Script de vérification de l'API Mathakine"""
import os
import sys
import requests
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

def main():
    """Fonction principale qui exécute la vérification de l'API"""
    print("=== VÉRIFICATION DE L'API MATHAKINE ===")
    print(f"Date: {datetime.now()}")
    print(f"Répertoire: {os.getcwd()}\n")
    
    # 1. Vérifier les ports utilisés
    check_ports()
    
    # 2. Démarrer le serveur en arrière-plan
    server_process = start_server()
    if not server_process:
        print("  ❌ Impossible de démarrer le serveur")
        return
    
    # Attendre que le serveur démarre
    print("  ⏳ Attente du démarrage du serveur...")
    time.sleep(5)
    
    try:
        # 3. Tester les endpoints de base
        test_base_endpoints()
        
        # 4. Tester les endpoints d'information
        test_info_endpoints()
        
    finally:
        # Arrêter le serveur
        stop_server(server_process)
    
    print("\n=== VÉRIFICATION TERMINÉE ===")

def check_ports():
    """Vérifie si les ports nécessaires sont disponibles"""
    print("1. Vérification des ports:")
    
    # Ports à vérifier
    ports = [8000]  # Port par défaut de FastAPI/Uvicorn
    
    for port in ports:
        try:
            # Vérifier si un processus utilise déjà le port
            # Utiliser netstat pour Windows
            result = subprocess.run(
                f"netstat -ano | findstr :{port}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            if "LISTENING" in result.stdout:
                print(f"  ⚠️ Port {port} déjà utilisé")
                for line in result.stdout.strip().split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        pid = line.strip().split()[-1]
                        print(f"  ℹ️ Processus PID: {pid}")
            else:
                print(f"  ✅ Port {port} disponible")
        except Exception as e:
            print(f"  ❌ Erreur lors de la vérification du port {port}: {e}")

def start_server():
    """Démarre le serveur en mode test"""
    print("\n2. Démarrage du serveur en mode test:")
    
    try:
        # Préparer les variables d'environnement
        env = os.environ.copy()
        env["TESTING"] = "true"
        
        # Démarrer le serveur
        cmd = "uvicorn app.main:app --reload --port 8000"
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"  ✅ Serveur démarré (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"  ❌ Erreur lors du démarrage du serveur: {e}")
        return None

def stop_server(process):
    """Arrête le serveur"""
    print("\n5. Arrêt du serveur:")
    
    if process:
        try:
            # Tuer le processus
            process.terminate()
            process.wait(timeout=5)
            print(f"  ✅ Serveur arrêté (PID: {process.pid})")
        except Exception as e:
            print(f"  ⚠️ Erreur lors de l'arrêt du serveur: {e}")
            # Forcer l'arrêt si nécessaire
            try:
                process.kill()
                print("  ✅ Serveur forcé à s'arrêter")
            except:
                pass
    else:
        print("  ⚠️ Aucun processus de serveur à arrêter")

def test_base_endpoints():
    """Teste les endpoints de base de l'API"""
    print("\n3. Test des endpoints de base:")
    
    endpoints = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    
    base_url = "http://localhost:8000"
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - OK (200)")
            else:
                print(f"  ⚠️ {endpoint} - Statut {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint} - Erreur: {e}")

def test_info_endpoints():
    """Teste les endpoints d'information de l'API"""
    print("\n4. Test des endpoints d'information:")
    
    info_endpoints = [
        "/api/info",
        "/health"
    ]
    
    base_url = "http://localhost:8000"
    
    for endpoint in info_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - OK (200)")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        # Afficher quelques informations clés
                        for key in data:
                            if isinstance(data[key], (str, int, bool, float)):
                                print(f"    - {key}: {data[key]}")
                except:
                    pass
            else:
                print(f"  ⚠️ {endpoint} - Statut {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint} - Erreur: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 