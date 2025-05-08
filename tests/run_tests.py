import pytest
import sys
import os
from datetime import datetime
from loguru import logger

# Configuration du logger
logger.add(
    "test_results/test_run_{time}.log",
    rotation="10 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def setup_test_environment():
    """Configuration de l'environnement de test"""
    # Créer le dossier des résultats de test s'il n'existe pas
    os.makedirs("test_results", exist_ok=True)
    
    # Configurer les variables d'environnement de test
    os.environ["TESTING"] = "True"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

def run_tests(test_type=None):
    """Exécution des tests selon le type spécifié"""
    setup_test_environment()
    
    start_time = datetime.now()
    logger.info(f"Démarrage des tests à {start_time}")
    
    # Définir les arguments pytest
    pytest_args = [
        "-v",  # Verbose
        "--cov=app",  # Couverture de code
        "--cov-report=html:test_results/coverage",  # Rapport de couverture HTML
        "--cov-report=term-missing",  # Afficher les lignes manquantes
        "--junitxml=test_results/junit.xml",  # Rapport JUnit XML
    ]
    
    # Ajouter le type de test spécifique si fourni
    if test_type:
        test_path = f"tests/{test_type}"
        if not os.path.exists(test_path):
            logger.error(f"Le type de test '{test_type}' n'existe pas")
            return False
        pytest_args.append(test_path)
    else:
        pytest_args.append("tests")
    
    # Exécuter les tests
    try:
        result = pytest.main(pytest_args)
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"Tests terminés en {duration}")
        logger.info(f"Résultat: {'Succès' if result == 0 else 'Échec'}")
        
        return result == 0
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
        return False

if __name__ == "__main__":
    # Parser les arguments de ligne de commande
    test_type = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--type":
            if len(sys.argv) > 2:
                test_type = sys.argv[2]
            else:
                logger.error("Le type de test doit être spécifié après --type")
                sys.exit(1)
    
    # Exécuter les tests
    success = run_tests(test_type)
    sys.exit(0 if success else 1) 