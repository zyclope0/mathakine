"""Script de validation simplifié pour l'application Mathakine"""
import sys
import os
from pathlib import Path
from datetime import datetime

def main():
    """Fonction principale qui exécute toutes les vérifications"""
    print("=== VALIDATION SIMPLIFIÉE DE MATHAKINE ===")
    print(f"Date: {datetime.now()}")
    print(f"Répertoire: {os.getcwd()}\n")
    
    # 1. Vérifier la structure des dossiers
    check_directories()
    
    # 2. Vérifier les fichiers principaux
    check_main_files()
    
    # 3. Vérifier les dépendances
    check_dependencies()
    
    print("\n=== VALIDATION TERMINÉE ===")

def check_directories():
    """Vérifie la présence des répertoires essentiels"""
    print("1. Vérification des répertoires:")
    directories = ["app", "app/models", "app/core", "app/schemas", "tests"]
    
    for directory in directories:
        path = Path(directory)
        if path.exists() and path.is_dir():
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} - Manquant")

def check_main_files():
    """Vérifie la présence des fichiers principaux"""
    print("\n2. Vérification des fichiers principaux:")
    main_files = [
        "app/main.py", 
        "app/core/config.py", 
        "requirements.txt", 
        ".env"
    ]
    
    for file in main_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✅ {file} ({size} octets)")
        else:
            print(f"  ❌ {file} - Manquant")

def check_dependencies():
    """Vérifie les dépendances principales dans requirements.txt"""
    print("\n3. Vérification des dépendances:")
    
    if not Path("requirements.txt").exists():
        print("  ❌ requirements.txt non trouvé")
        return
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        key_deps = ["starlette", "uvicorn", "sqlalchemy", "pytest", "loguru"]
        
        for dep in key_deps:
            if dep in content:
                print(f"  ✅ {dep}")
            else:
                print(f"  ❌ {dep} - Non trouvé")
                
    except Exception as e:
        print(f"  ❌ Erreur lors de la lecture de requirements.txt: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc() 