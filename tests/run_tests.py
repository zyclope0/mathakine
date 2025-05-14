import pytest
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Créer le dossier des résultats de test s'il n'existe pas
os.makedirs("test_results", exist_ok=True)

# Configuration du logger standard
def setup_logger():
    log_path = f"test_results/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configurer le logger
    logger = logging.getLogger("test_runner")
    logger.setLevel(logging.DEBUG)
    
    # Supprimer les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Ajouter un FileHandler
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # Définir le format
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    file_handler.setFormatter(formatter)
    
    # Ajouter le handler au logger
    logger.addHandler(file_handler)
    
    return logger

def setup_test_environment():
    """Configuration de l'environnement de test"""
    # Configurer les variables d'environnement de test
    os.environ["TESTING"] = "True"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

def run_tests(test_type=None):
    """Exécution des tests selon le type spécifié"""
    setup_test_environment()
    
    # Configurer le logger
    logger = setup_logger()
    
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

    # Ajouter le type de test spécifique si fourni et si ce n'est pas "all"
    if test_type and test_type != "all":
        if test_type in ["unit", "api", "integration", "functional"]:
            test_path = f"{base_path}/{test_type}"
        else:
            test_path = test_type  # Permettre des chemins personnalisés

        if not os.path.exists(test_path):
            logger.error(f"Le type de test '{test_type}' n'existe pas au chemin {test_path}")
            return False
        pytest_args.append(test_path)
    else:
        # Pour "all" ou None, exécuter tous les tests du dossier de base
        pytest_args.append(base_path)

    # Exécuter les tests
    try:
        result = pytest.main(pytest_args)
        end_time = datetime.now()
        duration = end_time - start_time

        try:
            logger.info(f"Tests terminés en {duration}")
            logger.info(f"Résultat: {'Succès' if result == 0 else 'Échec'}")
        except Exception as log_e:
            print(f"Erreur de log: {log_e}")

        # Fermer proprement les handlers de log
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        return result == 0
    except Exception as e:
        try:
            logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
            # Fermer proprement les handlers de log
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        except Exception:
            print(f"Erreur lors de l'exécution des tests: {str(e)}")
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
