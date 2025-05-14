"""
Script de configuration de l'environnement de validation pour Mathakine.
Ce script installe les dépendances nécessaires pour exécuter les tests et les validations.
"""
import sys
import os
import subprocess
from pathlib import Path
import platform

def main():
    """Fonction principale pour la configuration de l'environnement de validation"""
    print("=== CONFIGURATION DE L'ENVIRONNEMENT DE VALIDATION MATHAKINE ===")
    
    # Vérifier la version de Python
    python_version = platform.python_version()
    print(f"Version Python détectée: {python_version}")
    
    if python_version.startswith("3.13"):
        print("⚠️ Python 3.13 détecté - Des ajustements supplémentaires peuvent être nécessaires")
        print("   Installation des dépendances compatibles avec Python 3.13...")
        
        # Installer les dépendances pour Python 3.13
        install_deps_py313()
    else:
        print("✅ Version de Python compatible détectée")
        print("   Installation des dépendances standard...")
        
        # Installer les dépendances standard
        install_deps_standard()
    
    # Créer les dossiers nécessaires
    setup_directories()
    
    print("\n=== CONFIGURATION TERMINÉE ===")
    print("\nVous pouvez maintenant exécuter les scripts de validation :")
    print("  - python tests/auto_validation.py (validation complète)")
    print("  - python tests/simplified_validation.py (validation légère)")
    print("  - python tests/compatibility_check.py (vérification de compatibilité)")

def install_deps_py313():
    """Installe les dépendances compatibles avec Python 3.13"""
    try:
        # Installer setuptools d'abord (pour pkg_resources)
        subprocess.run([sys.executable, "-m", "pip", "install", "setuptools"], check=True)
        
        # Installer les dépendances de test avec versions compatibles
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "sqlalchemy>=2.0.27",
            "fastapi>=0.100.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "loguru>=0.7.0"
        ], check=True)
        
        print("✅ Dépendances compatibles avec Python 3.13 installées avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        sys.exit(1)

def install_deps_standard():
    """Installe les dépendances standard"""
    try:
        # Installer setuptools d'abord (pour pkg_resources)
        subprocess.run([sys.executable, "-m", "pip", "install", "setuptools"], check=True)
        
        # Installer les dépendances de test
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pytest",
            "pytest-cov",
            "sqlalchemy",
            "fastapi",
            "pydantic",
            "loguru"
        ], check=True)
        
        print("✅ Dépendances standard installées avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        sys.exit(1)

def setup_directories():
    """Configure les dossiers nécessaires pour les tests et validations"""
    # Créer le dossier pour les résultats de test
    Path("test_results").mkdir(exist_ok=True)
    print("✅ Dossier test_results/ créé")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 