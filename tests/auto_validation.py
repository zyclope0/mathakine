import pytest
import sys
import os
from datetime import datetime
from loguru import logger
import subprocess
from pathlib import Path

# Configuration du logger
logger.remove()
logger.add(
    f"test_results/auto_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    rotation="10 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def setup_test_environment():
    """Configure l'environnement de test"""
    try:
        # Créer le dossier de résultats s'il n'existe pas
        Path("test_results").mkdir(exist_ok=True)
        
        # Définir les variables d'environnement pour les tests
        os.environ["TESTING"] = "true"
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        
        # Vérifier que les dossiers nécessaires existent
        required_dirs = ["app", "tests"]
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                logger.error(f"Le dossier {dir_name} n'existe pas")
                return False
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de l'environnement: {str(e)}")
        return False

def run_tests(test_type=None):
    """Exécute les tests avec les options appropriées"""
    start_time = datetime.now()
    logger.info(f"Démarrage des tests à {start_time}")

    # Arguments de base pour pytest
    pytest_args = [
        "-v",  # Verbose
        "--cov=app",  # Couverture de code
        "--cov-report=html:test_results/coverage",  # Rapport HTML
        "--cov-report=term-missing",  # Afficher les lignes manquantes
        "--junitxml=test_results/junit.xml",  # Rapport JUnit
    ]

    # Ajouter le type de test si spécifié
    if test_type:
        test_path = Path("tests") / test_type
        if not test_path.exists():
            logger.error(f"Le dossier de tests {test_path} n'existe pas")
            return False
        pytest_args.append(str(test_path))
    else:
        pytest_args.append("tests")

    try:
        # Exécuter les tests
        result = pytest.main(pytest_args)
        
        # Vérifier le résultat
        if result == 0:
            logger.success("Tous les tests ont réussi")
        else:
            logger.error(f"Les tests ont échoué avec le code {result}")
        
        # Calculer la durée
        duration = datetime.now() - start_time
        logger.info(f"Tests terminés en {duration}")
        
        return result == 0
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
        return False

def validate_changes():
    """Valide les changements récents"""
    logger.info("Démarrage de la validation des changements")
    
    # Vérifier l'environnement
    if not setup_test_environment():
        return False
    
    # 1. Vérifier la syntaxe Python
    logger.info("Vérification de la syntaxe Python...")
    try:
        # Compiler tous les fichiers Python dans app/
        for py_file in Path("app").rglob("*.py"):
            try:
                subprocess.run([sys.executable, "-m", "py_compile", str(py_file)], 
                             check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Erreur de syntaxe dans {py_file}: {e.stderr}")
                return False
        logger.success("Syntaxe Python valide")
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la syntaxe: {str(e)}")
        return False

    # 2. Exécuter les tests unitaires
    logger.info("Exécution des tests unitaires...")
    if not run_tests("unit"):
        logger.error("Les tests unitaires ont échoué")
        return False

    # 3. Exécuter les tests API
    logger.info("Exécution des tests API...")
    if not run_tests("api"):
        logger.error("Les tests API ont échoué")
        return False

    # 4. Exécuter les tests d'intégration
    logger.info("Exécution des tests d'intégration...")
    if not run_tests("integration"):
        logger.error("Les tests d'intégration ont échoué")
        return False

    # 5. Exécuter les tests fonctionnels
    logger.info("Exécution des tests fonctionnels...")
    if not run_tests("functional"):
        logger.error("Les tests fonctionnels ont échoué")
        return False

    logger.success("Validation complète réussie")
    return True

if __name__ == "__main__":
    try:
        success = validate_changes()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        sys.exit(1) 