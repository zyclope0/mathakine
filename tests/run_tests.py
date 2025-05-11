import pytest
import sys
import os
from datetime import datetime
from loguru import logger
from pathlib import Path

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

    # Déterminer le chemin de base des tests
    # Si on est dans le dossier 'tests', le chemin relatif est '.'
    # Si on est à la racine, le chemin relatif est 'tests'
    if Path.cwd().name == "tests":
        base_path = "."
    else:
        base_path = "tests"

    # Ajouter le type de test spécifique si fourni
    if test_type:
        if test_type in ["unit", "api", "integration", "functional"]:
            test_path = f"{base_path}/{test_type}"
        else:
            test_path = test_type  # Permettre des chemins personnalisés

        if not os.path.exists(test_path):
            logger.error(f"Le type de test '{test_type}' n'existe pas au chemin {test_path}")
            return False
        pytest_args.append(test_path)
    else:
        pytest_args.append(base_path)

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
    verbose = False

    # Traiter les arguments
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
            test_type = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--verbose":
            verbose = True
            i += 1
        else:
            # Supporter le passage direct du type de test
            if test_type is None and sys.argv[i] not in ["--help"]:
                test_type = sys.argv[i]
            i += 1

    # Afficher l'aide si demandé
    if "--help" in sys.argv:
        print("Usage: python run_tests.py [--type TYPE] [--verbose]")
        print("Types disponibles: unit, api, integration, functional")
        sys.exit(0)

    # Exécuter les tests
    success = run_tests(test_type)
    sys.exit(0 if success else 1)
