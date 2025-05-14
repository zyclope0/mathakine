"""Script de vérification basique pour le projet Mathakine"""
import os
import sys
import platform
from pathlib import Path
from datetime import datetime

def main():
    """Fonction principale pour la vérification basique"""
    print("=== VÉRIFICATION BASIQUE MATHAKINE ===")
    print(f"Date: {datetime.now()}")
    print(f"Répertoire: {os.getcwd()}\n")
    
    # 1. Vérifier l'environnement Python
    check_python()
    
    # 2. Vérifier les fichiers essentiels
    check_essential_files()
    
    # 3. Vérifier le fichier .env
    check_env_file()
    
    # 4. Générer un rapport simple
    generate_report()
    
    print("\n=== VÉRIFICATION TERMINÉE ===")

def check_python():
    """Vérifie l'environnement Python"""
    print("1. Environnement Python:")
    print(f"  • Version: {platform.python_version()}")
    print(f"  • Exécutable: {sys.executable}")
    print(f"  • Architecture: {platform.architecture()[0]}")
    print(f"  • Système: {platform.system()} {platform.release()}")
    
    # Vérifier si version incompatible
    if platform.python_version().startswith("3.13"):
        print("\n  ⚠️ AVERTISSEMENT: Vous utilisez Python 3.13")
        print("  Cette version peut causer des problèmes de compatibilité avec certaines dépendances.")
        print("  Recommandation: Utiliser Python 3.11 ou 3.12 pour ce projet.")

def check_essential_files():
    """Vérifie la présence des fichiers essentiels"""
    print("\n2. Fichiers essentiels:")
    
    essential_files = [
        "app/main.py",
        "app/core/config.py",
        "requirements.txt",
        "app/db/base.py",
        "app/models/user.py"
    ]
    
    for file_path in essential_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✅ {file_path} - {size} octets")
        else:
            print(f"  ❌ {file_path} - Non trouvé")

def check_env_file():
    """Vérifie le fichier .env"""
    print("\n3. Configuration (.env):")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("  ❌ Fichier .env non trouvé")
        return
    
    print("  ✅ Fichier .env trouvé")
    
    # Lire le fichier de manière sécurisée
    try:
        with open(env_path, "r") as f:
            env_content = f.read()
        
        # Vérifier les clés importantes
        important_keys = ["DATABASE_URL", "DEBUG", "SECRET_KEY"]
        found_keys = []
        
        for key in important_keys:
            if key + "=" in env_content:
                found_keys.append(key)
                print(f"  ✅ Configuration {key} trouvée")
            else:
                print(f"  ❌ Configuration {key} manquante")
        
        if "DATABASE_URL" in found_keys:
            # Déterminer le type de base de données
            if "sqlite" in env_content:
                print("  ℹ️ Type de base de données: SQLite")
            elif "postgresql" in env_content:
                print("  ℹ️ Type de base de données: PostgreSQL")
            else:
                print("  ℹ️ Type de base de données: Autre")
    
    except Exception as e:
        print(f"  ❌ Erreur lors de la lecture du fichier .env: {str(e)}")

def generate_report():
    """Génère un rapport simple"""
    print("\n4. Recommandations:")
    
    # Vérifier Python
    if platform.python_version().startswith("3.13"):
        print("  • Problème: Python 3.13 peut causer des problèmes de compatibilité")
        print("    ↳ Solution: Utiliser Python 3.11 ou 3.12 avec un environnement virtuel")
        print("    ↳ Commande: python -m venv venv_py311 (avec Python 3.11)")
    
    # Vérifier SQLAlchemy
    print("  • Problème: SQLAlchemy peut être incompatible avec Python 3.13")
    print("    ↳ Solution: Mettre à jour SQLAlchemy à la dernière version")
    print("    ↳ Commande: pip install sqlalchemy>=2.0.27")
    
    # Recommandations générales
    print("\n  • Recommandations générales:")
    print("    ↳ Exécuter: pip install -r requirements.txt --upgrade")
    print("    ↳ Utiliser un environnement virtuel dédié pour le projet")
    print("    ↳ Vérifier la documentation des dépendances pour les problèmes connus")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 