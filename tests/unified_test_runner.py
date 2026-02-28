#!/usr/bin/env python
"""
Exécuteur de tests unifié pour le projet Mathakine

Ce script remplace les multiples scripts de test (run_tests.py, run_basic_tests.py, run_full_tests.py)
par une solution unifiée qui offre toutes les fonctionnalités dans un seul outil.

Caractéristiques:
- Exécution de tests par catégorie (unit, api, integration, functional)
- Exécution de tests individuels
- Mode verbeux
- Réparation automatique des problèmes d'énumération avant les tests
- Mode test rapide pour le développement
- Rapports de couverture HTML
- Options pour ignorer les tests lents ou spécifiques à PostgreSQL

Utilisation:
    python tests/unified_test_runner.py [OPTIONS]

Options:
    --all               Exécuter tous les tests
    --unit              Exécuter les tests unitaires
    --api               Exécuter les tests d'API
    --integration       Exécuter les tests d'intégration
    --functional        Exécuter les tests fonctionnels
    --specific PATH     Exécuter un test spécifique
    --verbose           Mode verbeux
    --fix-enums         Corriger les problèmes d'énumération avant les tests
    --fast              Mode rapide (ignorer les tests lents)
    --skip-postgres     Ignorer les tests spécifiques à PostgreSQL
    --no-coverage       Désactiver le rapport de couverture
    --html-report       Générer un rapport HTML détaillé
    --xml-report        Générer un rapport XML pour CI/CD
"""

import argparse
import datetime
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import colorama
from colorama import Fore, Style

# Initialiser colorama
colorama.init()

# Configuration du logging
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# Timestamp pour les fichiers de sortie
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Répertoire du projet (répertoire parent du script)
PROJECT_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = PROJECT_DIR / "tests"

# Répertoire pour les résultats de test (dans le dossier tests)
TEST_RESULTS_DIR = TEST_DIR / "test_results"
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Chemins pour les différents rapports
HTML_REPORT_PATH = TEST_RESULTS_DIR / f"report_{TIMESTAMP}.html"
XML_REPORT_PATH = TEST_RESULTS_DIR / f"junit_{TIMESTAMP}.xml"
LOG_FILE_PATH = TEST_RESULTS_DIR / f"test_run_{TIMESTAMP}.log"
COVERAGE_DIR = TEST_RESULTS_DIR / "coverage"


def setup_file_logging():
    """Configure le logging dans un fichier."""
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    return file_handler


def get_test_directories():
    """Retourne un dictionnaire des répertoires de test."""
    return {
        "unit": TEST_DIR / "unit",
        "api": TEST_DIR / "api",
        "integration": TEST_DIR / "integration",
        "functional": TEST_DIR / "functional",
    }


def fix_enum_issues():
    """Exécute le script de correction des problèmes d'énumération."""
    script_path = PROJECT_DIR / "scripts" / "fix_enum_reference_chain.py"

    if not script_path.exists():
        logger.warning(f"Script de correction non trouvé: {script_path}")
        return False

    logger.info("Correction des problèmes d'énumération...")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        logger.info("Correction terminée avec succès")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la correction: {e}")
        return False


def build_pytest_command(args):
    """Construit la commande pytest en fonction des arguments."""
    cmd = [sys.executable, "-m", "pytest"]

    # Chemins des tests à exécuter
    test_paths = []
    test_dirs = get_test_directories()

    if args.specific:
        test_paths.append(args.specific)
    elif args.unit:
        test_paths.append(str(test_dirs["unit"]))
    elif args.api:
        test_paths.append(str(test_dirs["api"]))
    elif args.integration:
        test_paths.append(str(test_dirs["integration"]))
    elif args.functional:
        test_paths.append(str(test_dirs["functional"]))
    elif args.all:
        for d in test_dirs.values():
            test_paths.append(str(d))
    else:
        # Par défaut, exécuter les tests unitaires
        test_paths.append(str(test_dirs["unit"]))

    # Options de pytest
    if args.verbose:
        cmd.append("-v")

    # Ignorer les tests spécifiques à PostgreSQL si demandé
    if args.skip_postgres:
        cmd.append("-k")
        cmd.append("not postgres and not postgresql")

    # Ignorer les tests lents en mode rapide
    if args.fast:
        cmd.append("-k")
        cmd.append("not slow")

    # Couverture de code
    if not args.no_coverage:
        cmd.append("--cov=app")
        cmd.append(f"--cov-report=html:{COVERAGE_DIR}")

    # Rapport HTML
    if args.html_report:
        cmd.append(f"--html={HTML_REPORT_PATH}")
        cmd.append("--self-contained-html")

    # Rapport XML
    if args.xml_report:
        cmd.append(f"--junitxml={XML_REPORT_PATH}")

    # Ajouter les chemins de test à la fin
    cmd.extend(test_paths)

    return cmd


def run_tests(args):
    """Exécute les tests avec les options spécifiées."""
    start_time = time.time()

    # Corriger les problèmes d'énumération si demandé
    if args.fix_enums:
        fix_enum_issues()

    # Construire et exécuter la commande pytest
    cmd = build_pytest_command(args)
    logger.info(f"Exécution de la commande: {' '.join(cmd)}")

    result = subprocess.run(cmd)
    success = result.returncode == 0

    end_time = time.time()
    duration = datetime.timedelta(seconds=end_time - start_time)

    # Afficher le résultat
    status_str = "SUCCÈS" if success else "ÉCHEC"
    color = Fore.GREEN if success else Fore.RED
    logger.info("=" * 80)
    logger.info(f"{color}RÉSULTAT DES TESTS: {status_str}{Style.RESET_ALL}")
    logger.info(f"Durée totale: {duration}")
    logger.info("\nRapports générés:")

    if not args.no_coverage:
        logger.info(f"- Rapport de couverture: {COVERAGE_DIR / 'index.html'}")

    if args.html_report:
        logger.info(f"- Rapport HTML détaillé: {HTML_REPORT_PATH}")

    if args.xml_report:
        logger.info(f"- Rapport XML: {XML_REPORT_PATH}")

    logger.info(f"- Journal complet: {LOG_FILE_PATH}")
    logger.info("=" * 80)

    return success


def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(
        description="Exécuteur de tests unifié pour Mathakine"
    )

    # Options pour les catégories de tests
    test_group = parser.add_argument_group("Catégories de tests")
    test_group.add_argument(
        "--all", action="store_true", help="Exécuter tous les tests"
    )
    test_group.add_argument(
        "--unit", action="store_true", help="Exécuter les tests unitaires"
    )
    test_group.add_argument(
        "--api", action="store_true", help="Exécuter les tests d'API"
    )
    test_group.add_argument(
        "--integration", action="store_true", help="Exécuter les tests d'intégration"
    )
    test_group.add_argument(
        "--functional", action="store_true", help="Exécuter les tests fonctionnels"
    )
    test_group.add_argument(
        "--specific", type=str, help="Exécuter un test ou module spécifique"
    )

    # Options de comportement
    behavior_group = parser.add_argument_group("Options de comportement")
    behavior_group.add_argument("--verbose", action="store_true", help="Mode verbeux")
    behavior_group.add_argument(
        "--fix-enums",
        action="store_true",
        help="Corriger les problèmes d'énumération avant les tests",
    )
    behavior_group.add_argument(
        "--fast", action="store_true", help="Mode rapide (ignorer les tests lents)"
    )
    behavior_group.add_argument(
        "--skip-postgres",
        action="store_true",
        help="Ignorer les tests spécifiques à PostgreSQL",
    )

    # Options de rapport
    report_group = parser.add_argument_group("Options de rapport")
    report_group.add_argument(
        "--no-coverage", action="store_true", help="Désactiver le rapport de couverture"
    )
    report_group.add_argument(
        "--html-report", action="store_true", help="Générer un rapport HTML détaillé"
    )
    report_group.add_argument(
        "--xml-report", action="store_true", help="Générer un rapport XML pour CI/CD"
    )

    args = parser.parse_args()

    # Configurer le logging dans un fichier
    file_handler = setup_file_logging()

    try:
        success = run_tests(args)
        sys.exit(0 if success else 1)
    finally:
        # Fermer proprement le handler de fichier
        file_handler.close()
        logger.removeHandler(file_handler)


if __name__ == "__main__":
    main()
