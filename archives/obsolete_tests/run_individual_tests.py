#!/usr/bin/env python
"""Script pour exécuter des tests individuels et générer des rapports détaillés"""
import argparse
import sys
import os
import pytest
from pathlib import Path
from datetime import datetime
from loguru import logger

# Configuration du logger
logger.remove()
logger.add(
    f"test_results/individual_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    rotation="10 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def validate_test_exists(test_path):
    """Valide que le fichier de test existe"""
    test_file = Path(test_path)
    if not test_file.exists():
        logger.error(f"Le fichier de test {test_path} n'existe pas")
        return False
    return True

def run_individual_test(test_path, verbose=False):
    """Exécute un test individuel"""
    if not validate_test_exists(test_path):
        return False
    
    logger.info(f"Exécution du test: {test_path}")
    
    # Ajouter le répertoire parent au path pour permettre l'import de app
    sys.path.insert(0, str(Path.cwd()))
    
    # Arguments pour pytest
    pytest_args = [
        "-v" if verbose else "-q",  # Niveau de verbosité
        "--cov=app",  # Couverture de code
        "--cov-report=html:test_results/coverage",  # Rapport HTML
        "--cov-report=term-missing",  # Afficher les lignes manquantes
        f"--junitxml=test_results/junit_{Path(test_path).stem}.xml",  # Rapport JUnit
        test_path  # Chemin du test à exécuter
    ]
    
    try:
        # Exécuter le test avec pytest
        result = pytest.main(pytest_args)
        
        if result == 0:
            logger.success(f"Test {test_path} réussi")
        else:
            logger.error(f"Test {test_path} échoué avec code {result}")
        
        return result == 0
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du test {test_path}: {str(e)}")
        return False

def run_predefined_tests():
    """Exécute des tests prédéfinis pour valider le système"""
    logger.info("Exécution des tests prédéfinis")
    
    # Créer le dossier de résultats s'il n'existe pas
    Path("test_results").mkdir(exist_ok=True)
    
    # Configurer l'environnement
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    # Définir les tests essentiels
    core_tests = [
        "tests/api/test_base_endpoints.py",
        "tests/unit/test_models.py"
    ]
    
    # Exécuter chaque test
    results = []
    for test in core_tests:
        results.append((test, run_individual_test(test, verbose=True)))
    
    # Afficher le résumé
    logger.info("Résumé des tests:")
    all_passed = True
    for test, result in results:
        status = "✅ Réussi" if result else "❌ Échoué"
        logger.info(f"{test}: {status}")
        if not result:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exécute des tests individuels")
    parser.add_argument("-t", "--test", help="Chemin vers le fichier de test à exécuter")
    parser.add_argument("-v", "--verbose", action="store_true", help="Afficher les détails des tests")
    parser.add_argument("--auto", action="store_true", help="Exécuter automatiquement les tests essentiels")
    
    args = parser.parse_args()
    
    if args.auto:
        success = run_predefined_tests()
    elif args.test:
        success = run_individual_test(args.test, args.verbose)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1) 