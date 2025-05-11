#!/usr/bin/env python
"""
Script principal d'exécution et de validation des tests pour le projet Mathakine.
Ce script unifie les fonctionnalités des scripts existants (run_tests.py, auto_validation.py, etc.)
tout en conservant le même format de rapports.
"""
import argparse
import sys
import os
import pytest
import platform
import subprocess
import time
from pathlib import Path
from datetime import datetime
from loguru import logger
import json
from dotenv import dotenv_values
import atexit

# Configurer le dossier des résultats
RESULTS_DIR = "tests/test_results"

# S'assurer que le dossier existe
Path(RESULTS_DIR).mkdir(exist_ok=True, parents=True)

# Variables globales pour les handlers loguru
file_handler_id = None
console_handler_id = None

# Fonction pour nettoyer les handlers à la sortie


def cleanup_handlers():
    """Nettoie les gestionnaires de log avant de quitter"""
    global file_handler_id, console_handler_id
    try:
        if file_handler_id is not None:
            logger.remove(file_handler_id)
    except (ValueError, OSError):
        pass

    try:
        if console_handler_id is not None:
            logger.remove(console_handler_id)
    except (ValueError, OSError):
        pass

# Enregistrer la fonction de nettoyage pour être exécutée à la sortie
atexit.register(cleanup_handlers)

# Configuration du logger
log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
logger.remove()  # Supprimer le logger par défaut

# Ajouter un gestionnaire de fichier
log_file = f"{RESULTS_DIR}/auto_validation_{log_timestamp}.log"
try:
    file_handler_id = logger.add(
        log_file,
        rotation="10 MB",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=True,  # Utiliser une file d'attente pour éviter les problèmes de thread
        catch=True     # Attraper les exceptions
    )
except Exception as e:
    print(f"Erreur lors de la configuration du logger fichier: {str(e)}")
    file_handler_id = None

# Ajouter un gestionnaire de console avec moins de verbosité
try:
    console_handler_id = logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
        colorize=True,
        catch=True     # Attraper les exceptions
    )
except Exception as e:
    print(f"Erreur lors de la configuration du logger console: {str(e)}")
    console_handler_id = None




def setup_environment():
    """Configure l'environnement pour les tests"""
    logger.info("Configuration de l'environnement de test")

    # Vérifier la version de Python
    python_version = platform.python_version()
    logger.info(f"Version Python: {python_version}")

    # Définir les variables d'environnement pour les tests
    os.environ["TESTING"] = "true"

    # Déterminer la base de données à utiliser
    if "TEST_DATABASE_URL" not in os.environ:
        # Vérifier si DATABASE_URL est défini dans .env
        if "DATABASE_URL" in os.environ and os.environ["DATABASE_URL"].startswith("postgresql://"):
            os.environ["TEST_DATABASE_URL"] = os.environ["DATABASE_URL"]
            logger.info("Utilisation de la base de données PostgreSQL depuis .env")
        else:
            # Par défaut, utiliser SQLite pour les tests
            os.environ["TEST_DATABASE_URL"] = "sqlite:///./test.db"
            logger.info("Utilisation de SQLite pour les tests")

    logger.info(f"Base de données de test: {os.environ.get('TEST_DATABASE_URL').split('://')[0]}")

    # Vérifier que les dossiers nécessaires existent
    required_dirs = ["app", "tests", "tests/unit", "tests/api", "tests/integration"\
        , "tests/functional"]
    missing_dirs = [dir_name for dir_name in required_dirs if not Path(dir_name).exists()]

    if missing_dirs:
        for dir_name in missing_dirs:
            logger.error(f"Le dossier {dir_name} n'existe pas")
        return False

    return True




def setup_test_database():
    """Initialise la base de données avec des données de test."""
    logger.info("Initialisation de la base de données de test")
    try:
        # Importer le module d'initialisation
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from init_test_db import initialize_test_database

        # Initialiser la base de données
        initialize_test_database()
        logger.success("Base de données de test initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False




def run_tests(test_type=None, verbose=False, coverage=True, junit=True):
    """Exécute les tests avec les options spécifiées"""
    start_time = datetime.now()
    logger.info(f"Démarrage des tests à {start_time}")

    # Arguments de base pour pytest
    pytest_args = ["-v"] if verbose else []

    # Ajouter la couverture de code si demandé
    if coverage:
        pytest_args.extend([
            "--cov=app",
            f"--cov-report=html:{RESULTS_DIR}/coverage",
            "--cov-report=term-missing",
        ])

    # Ajouter le rapport JUnit si demandé
    if junit:
        if test_type:
            junit_file = f"{RESULTS_DIR}/junit_{test_type}.xml"
        else:
            junit_file = f"{RESULTS_DIR}/junit.xml"
        pytest_args.append(f"--junitxml={junit_file}")

    # Déterminer quels tests exécuter
    if test_type:
        # Si un type spécifique de test est demandé
        if test_type in ["unit", "api", "integration", "functional"]:
            test_path = f"tests/{test_type}"
        else:
            # Si c'est un chemin de fichier spécifique
            test_path = test_type
    else:
        # Exécuter tous les tests
        test_path = "tests"

    pytest_args.append(test_path)

    # Exécuter les tests
    try:
        logger.info(f"Exécution des tests: pytest {' '.join(pytest_args)}")
        result = pytest.main(pytest_args)

        # Calculer la durée
        duration = datetime.now() - start_time
        logger.info(f"Tests terminés en {duration}")

        # Enregistrer le résultat
        if result == 0:
            logger.success(f"Tests réussis: {test_type or 'tous'}")
            return True
        else:
            logger.error(f"Tests échoués: {test_type or 'tous'} avec code {result}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
        return False




def check_syntax():
    """Vérifie la syntaxe Python de tous les fichiers du projet"""
    logger.info("Vérification de la syntaxe Python")

    errors = []
    for py_file in Path("app").rglob("*.py"):
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                check=True, capture_output=True, text=True
            )
            logger.debug(f"Syntaxe valide: {py_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur de syntaxe dans {py_file}: {e.stderr}")
            errors.append((str(py_file), e.stderr))

    if errors:
        logger.error(f"{len(errors)} fichiers avec des erreurs de syntaxe")
        return False
    else:
        logger.success("Syntaxe Python valide pour tous les fichiers")
        return True




def generate_compatibility_report():
    """Génère un rapport de compatibilité"""
    logger.info("Génération du rapport de compatibilité")

    report_file = f"{RESULTS_DIR}/compatibility_report_{log_timestamp}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=== RAPPORT DE COMPATIBILITÉ MATHAKINE ===\n")
        f.write(f"Date: {datetime.now()}\n\n")

        # Environnement Python
        f.write("1. Environnement Python:\n")
        f.write(f"   - Version: {platform.python_version()}\n")
        f.write(f"   - Architecture: {platform.architecture()[0]}\n")
        f.write(f"   - Système: {platform.system()} {platform.release()}\n")
        f.write(f"   - Environnement virtuel: {os.environ.get('VIRTUAL_ENV', 'Non')}\n\n")

        # Dépendances
        f.write("2. Dépendances installées:\n")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True, text=True, check=True
            )
            installed_packages = result.stdout.strip().split('\n')

            # Lire requirements.txt si disponible
            required_packages = {}
            if Path("requirements.txt").exists():
                with open("requirements.txt", "r") as req_file:
                    for line in req_file:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "==" in line:
                                name, version = line.split("==", 1)
                                required_packages[name.strip()] = version.strip()

            # Comparer avec les packages installés
            for package in installed_packages:
                if "==" in package:
                    name, version = package.split("==", 1)
                    name = name.strip()
                    version = version.strip()

                    req_version = required_packages.get(name)
                    if req_version:
                        match = "✅" if req_version == version else "❌"
                        f.write(f"   - {name}: installé ({version}), requis ({req_version}) {match}\n")
                    else:
                        f.write(f"   - {name}: installé ({version}), non requis\n")
        except Exception as e:
            f.write(f"   Erreur lors de la récupération des dépendances: {str(e)}\n")

        # Database
        f.write("\n3. Configuration de la base de données:\n")
        db_url = os.environ.get("TEST_DATABASE_URL", "Non défini")
        db_type = db_url.split(":")[0] if ":" in db_url else "Inconnu"
        f.write(f"   - Type: {db_type}\n")

        # Recommandations
        f.write("\n4. Recommandations:\n")
        if platform.python_version().startswith("3.13"):
            f.write("   - Utiliser Python 3.11 ou 3.12 pour une meilleure compatibilité\n")
            f.write("   - Mettre à jour SQLAlchemy à la version 2.0.27 ou supérieure pour Python 3.13\n")

        f.write("\n=== FIN DU RAPPORT ===\n")

    logger.info(f"Rapport de compatibilité généré: {report_file}")
    return report_file




def generate_validation_report(all_tests_passed, individual_results):
    """Génère un rapport de validation au format JSON"""
    logger.info("Génération du rapport de validation JSON")

    report_file = f"{RESULTS_DIR}/validation_{log_timestamp}.json"

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "status": "success" if all_tests_passed else "failure",
        "python_version": platform.python_version(),
        "os": f"{platform.system()} {platform.release()}",
        "test_results": individual_results
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    logger.info(f"Rapport de validation généré: {report_file}")
    return report_file




def generate_full_report(all_tests_passed, individual_results, compatibility_report=None):
    """Génère un rapport complet au format Markdown"""
    logger.info("Génération du rapport complet au format Markdown")

    report_file = f"{RESULTS_DIR}/rapport_complet_{log_timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Rapport de Validation Mathakine\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Status général
        status = "✅ Succès" if all_tests_passed else "❌ Échec"
        f.write(f"## Status: {status}\n\n")

        # 1. Environnement Python
        f.write("## 1. Environnement Python\n\n")
        f.write(f"- **Version**: {platform.python_version()}\n")
        f.write(f"- **Exécutable**: {sys.executable}\n")
        f.write(f"- **Architecture**: {platform.architecture()[0]}\n")
        f.write(f"- **Système**: {platform.system()} {platform.release()}\n")
        venv_path = os.environ.get('VIRTUAL_ENV', 'Non')
        f.write(f"- **Environnement virtuel**: {venv_path}\n")
        is_compatible = "Oui" if not platform.python_version().startswith("3.13") else "Non"
        f.write(f"- **Compatible**: {is_compatible}\n\n")

        # 2. Fichiers Essentiels
        f.write("## 2. Fichiers Essentiels\n\n")
        f.write("| Fichier | Statut | Taille | Dernière modification |\n")
        f.write("|---------|--------|--------|----------------------|\n")

        # Liste des fichiers essentiels à vérifier
        essential_files = [
            "app/main.py",
            "app/core/config.py",
            "requirements.txt",
            "app/db/base.py",
            "app/models/user.py",
            ".env",
            ".env.example",
            "tests/conftest.py"
        ]

        for file_path in essential_files:
            try:
                file_stat = Path(file_path).stat()
                file_size = file_stat.st_size
                file_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"| {file_path} | ✅ | {file_size} octets | {file_time} |\n")
            except FileNotFoundError:
                f.write(f"| {file_path} | ❌ | - | - |\n")

        f.write("\n")

        # 3. Configuration
        f.write("## 3. Configuration\n\n")
        env_exists = Path(".env").exists()
        f.write(f"Fichier .env trouvé {'✅' if env_exists else '❌'}\n\n")

        if env_exists:
            f.write("### Variables d'environnement\n\n")
            f.write("| Variable | Valeur |\n")
            f.write("|----------|--------|\n")

            # Lire le fichier .env avec protection des données sensibles
            env_data = dotenv_values(".env")

            for key, value in env_data.items():
                # Masquer les valeurs sensibles comme les secrets et mots de passe
                displayed_value = value
                if any(sensitive in key.lower() for sensitive in ["key", "secret"
                    , "password", "token"]):
                    displayed_value = value[:3] + "..."
                # Pour l'URL de base de données, ne montrer que le type
                elif "database_url" in key.lower():
                    if "://" in value:
                        displayed_value = value.split("://")[0] + "...db"
                    else:
                        displayed_value = value

                f.write(f"| {key} | {displayed_value} |\n")

            # Déterminer le type de base de données
            db_url = env_data.get("DATABASE_URL", os.environ.get("DATABASE_URL", ""))
            db_type = "SQLite"
            if "postgresql" in db_url.lower():
                db_type = "PostgreSQL"
            elif "mysql" in db_url.lower():
                db_type = "MySQL"
            elif "mssql" in db_url.lower():
                db_type = "SQL Server"
            elif "oracle" in db_url.lower():
                db_type = "Oracle"
            elif "sqlite" not in db_url.lower():
                db_type = "Autre"

            f.write(f"\nType de base de données: **{db_type}**\n\n")

        # 4. Dépendances
        f.write("## 4. Dépendances\n\n")
        f.write("| Package | Version requise | Version installée | Statut |\n")
        f.write("|---------|----------------|-------------------|--------|\n")

        # Lire requirements.txt
        req_versions = {}
        if Path("requirements.txt").exists():
            with open("requirements.txt", "r") as req_file:
                for line in req_file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "==" in line:
                            name, version = line.split("==", 1)
                            req_versions[name.strip()] = version.strip()

        # Obtenir les versions installées
        try:
            installed_packages = subprocess.check_output([sys.executable, "-m", "pip", "freeze"],
                                                        universal_newlines=True).strip().split('\n')
            installed_versions = {}
            for package in installed_packages:
                if "==" in package:
                    name, version = package.split("==", 1)
                    installed_versions[name.strip()] = version.strip()

            # Lister les dépendances importantes
            important_deps = [
                "starlette", "uvicorn", "jinja2", "aiofiles", "sqlalchemy",
                "python-dotenv", "requests", "openai", "loguru", "pytest",
                "beautifulsoup4", "pytest-cov", "sphinx"
            ]

            for dep in important_deps:
                req_version = req_versions.get(dep, "-")
                installed_version = installed_versions.get(dep, "-")

                status = "✅"
                if installed_version == "-":
                    status = "❌"
                elif req_version != "-" and req_version != installed_version:
                    status = "⚠️"

                f.write(f"| {dep} | {req_version} | {installed_version} | {status} |\n")

        except Exception as e:
            f.write(f"*Erreur lors de la récupération des dépendances: {str(e)}*\n\n")

        # Résultats des tests
        f.write("\n## 5. Résultats des tests\n\n")

        f.write("| Type de test | Statut | Durée | Nombre de tests |\n")
        f.write("|-------------|--------|-------|----------------|\n")

        for test_type, result in individual_results.items():
            status_icon = "✅" if result["status"] else "❌"

            # Obtenir le nombre de tests exécutés
            test_count = "-"
            junit_file = f"{RESULTS_DIR}/junit_{test_type}.xml"
            if Path(junit_file).exists():
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(junit_file)
                    root = tree.getroot()
                    test_count = root.attrib.get('tests', '-')
                except:
                    test_count = "-"

            f.write(f"| {test_type} | {status_icon} | {result.get('duration', 'N/A')} | {test_count} |\n")

        # Recommandations
        f.write("\n## 6. Recommandations\n\n")

        # Python
        if platform.python_version().startswith("3.13"):
            f.write("### 1. Python (🔴 Haute)\n\n")
            f.write("**Problème**: Python 3.13 est incompatible avec certaines dépendances (notamment SQLAlchemy)\n\n")
            f.write("**Solution**: Utiliser Python 3.11 ou 3.12 avec un environnement virtuel\n\n")
            f.write("**Commandes**:\n")
            f.write("```\n")
            f.write("python3.11 -m venv venv_py311\n")
            f.write("```\n")
            f.write("```\n")
            f.write("venv_py311\\Scripts\\activate   # Windows\n")
            f.write("```\n")
            f.write("```\n")
            f.write("source venv_py311/bin/activate  # Linux/Mac\n")
            f.write("```\n")
            f.write("```\n")
            f.write("pip install -r requirements.txt\n")
            f.write("```\n\n")

        # SQLAlchemy
        if platform.python_version().startswith("3.13"):
            f.write("### 2. Dépendances (🔴 Haute)\n\n")
            f.write("**Problème**: SQLAlchemy 2.0.26 est incompatible avec Python 3.13\n\n")
            f.write("**Solution**: Mettre à jour SQLAlchemy à la version 2.0.27 ou supérieure\n\n")
            f.write("**Commandes**:\n")
            f.write("```\n")
            f.write("pip install sqlalchemy>=2.0.27\n")
            f.write("```\n")
            f.write("```\n")
            f.write("pip install -r requirements.txt\n")
            f.write("```\n\n")

        # Configuration
        if env_exists and "SECRET_KEY" not in env_data:
            f.write("### 3. Configuration (🟠 Moyenne)\n\n")
            f.write("**Problème**: La variable SECRET_KEY n'est pas définie dans le fichier .env\n\n")
            f.write("**Solution**: Ajouter une clé secrète au fichier .env pour renforcer la sécurité\n\n")
            f.write("**Commandes**:\n")
            f.write("```\n")
            f.write("Ajouter au fichier .env : SECRET_KEY=votre_cle_secrete_complexe\n")
            f.write("```\n\n")

        # Général
        f.write("### 4. Général (🟢 Basse)\n\n")
        f.write("**Problème**: Mettre à jour régulièrement les dépendances\n\n")
        f.write("**Solution**: Exécuter pip install --upgrade pour maintenir les dépendances à jour\n\n")
        f.write("**Commandes**:\n")
        f.write("```\n")
        f.write("pip install -r requirements.txt --upgrade\n")
        f.write("```\n\n")

        # Informations supplémentaires
        f.write("\n## 7. Informations supplémentaires\n\n")
        f.write(f"- Journal détaillé: `{RESULTS_DIR}/auto_validation_{log_timestamp}.log`\n")

        if compatibility_report:
            f.write(f"- Rapport de compatibilité: `{compatibility_report}`\n")

        # Conclusion
        f.write("\n## Conclusion\n\n")
        if all_tests_passed:
            f.write("✅ **L'application est prête pour le déploiement.**\n")
        else:
            f.write("❌ **Des corrections sont nécessaires avant le déploiement.**\n")

    logger.info(f"Rapport complet généré: {report_file}")
    return report_file




def run_full_validation():
    """Exécute la validation complète de l'application"""
    logger.info("=== DÉMARRAGE DE LA VALIDATION COMPLÈTE ===")

    # Configurer l'environnement
    if not setup_environment():
        logger.error("Échec de la configuration de l'environnement")
        return False

    # Vérifier la syntaxe
    syntax_valid = check_syntax()

    # Exécuter tous les types de tests
    test_types = ["unit", "api", "integration", "functional"]
    individual_results = {}

    for test_type in test_types:
        start_time = time.time()
        status = run_tests(test_type=test_type, verbose=True)
        duration = f"{time.time() - start_time:.2f}s"

        individual_results[test_type] = {
            "status": status,
            "duration": duration
        }

    # Déterminer si tous les tests ont réussi
    all_tests_passed = syntax_valid and all(result["status"] for result in individual_results.values())

    # Générer les rapports
    compatibility_report = generate_compatibility_report()
    validation_report = generate_validation_report(all_tests_passed, individual_results)
    full_report = generate_full_report(all_tests_passed, individual_results, compatibility_report)

    # Afficher le résultat final
    if all_tests_passed:
        logger.success("=== VALIDATION COMPLÈTE RÉUSSIE ===")
    else:
        logger.error("=== VALIDATION COMPLÈTE ÉCHOUÉE ===")

    logger.info(f"Rapports générés dans le dossier {RESULTS_DIR}/")
    logger.info(f"Rapport complet: {full_report}")

    return all_tests_passed




def run_basic_validation():
    """Exécute une validation de base de l'application"""
    logger.info("=== DÉMARRAGE DE LA VALIDATION DE BASE ===")

    # Configurer l'environnement
    if not setup_environment():
        logger.error("Échec de la configuration de l'environnement")
        return False

    # Vérifier la syntaxe
    syntax_valid = check_syntax()

    # Exécuter uniquement les tests unitaires et API
    test_types = ["unit", "api"]
    individual_results = {}

    for test_type in test_types:
        start_time = time.time()
        status = run_tests(test_type=test_type, verbose=False)
        duration = f"{time.time() - start_time:.2f}s"

        individual_results[test_type] = {
            "status": status,
            "duration": duration
        }

    # Déterminer si tous les tests ont réussi
    basic_validation_passed = syntax_valid and all(result["status"] for result in individual_results.values())

    # Générer un rapport simplifié
    validation_report = generate_validation_report(basic_validation_passed, individual_results)

    # Afficher le résultat final
    if basic_validation_passed:
        logger.success("=== VALIDATION DE BASE RÉUSSIE ===")
    else:
        logger.error("=== VALIDATION DE BASE ÉCHOUÉE ===")

    logger.info(f"Rapport généré: {validation_report}")

    return basic_validation_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exécution et validation des tests pour Mathakine")
    parser.add_argument("--type", choices=["unit", "api", "integration", "functional"],
                        help="Type de tests à exécuter")
    parser.add_argument("--file", help="Chemin vers un fichier de test spécifique")
    parser.add_argument("--full", action="store_true", help="Exécuter la validation complète")
    parser.add_argument("--basic", action="store_true", help="Exécuter la validation de base")
    parser.add_argument("--report", action="store_true", help="Générer uniquement les rapports")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    parser.add_argument("--no-coverage", action="store_true", help="Désactiver la couverture de code")
    parser.add_argument("--setup-db", action="store_true", help="Initialiser la base de données avant les tests")

    args = parser.parse_args()

    try:
        # Si l'option setup-db est spécifiée, initialiser la base de données
        if args.setup_db:
            setup_success = setup_test_database()
            if not setup_success:
                sys.exit(1)

        # Si aucun argument spécifié, afficher l'aide
        if not any([args.type, args.file, args.full, args.basic, args.report, args.setup_db]):
            parser.print_help()
            success = False
        else:
            # Exécuter les tests selon les arguments
            if args.full:
                success = run_full_validation()
            elif args.basic:
                success = run_basic_validation()
            elif args.report:
                # TODO: Implémenter la génération de rapports uniquement
                print("Génération de rapports non implémentée")
                success = True
            elif args.file:
                success = run_tests(test_type=args.file, verbose=args.verbose,
                                coverage=not args.no_coverage)
            elif args.type:
                success = run_tests(test_type=args.type, verbose=args.verbose,
                                coverage=not args.no_coverage)
            else:
                success = False

        # Sortir avec le code approprié
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("Interruption par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        sys.exit(1)
    finally:
        # Les handlers seront nettoyés par atexit
        pass
