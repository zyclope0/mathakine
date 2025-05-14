#!/usr/bin/env python
"""
CLI d'administration pour Mathakine
Fournit des commandes pour initialiser, démarrer, tester et maintenir l'application
"""
import os
import sys
import argparse
import subprocess
import platform
from loguru import logger

# Configuration de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")

# Configuration du logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>")




def setup_parser():
    """
    Configure le parseur d'arguments.
    """
    parser = argparse.ArgumentParser(description="Outil d'administration Mathakine")
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")

    # Commande: run
    run_parser = subparsers.add_parser("run", help="Lancer le serveur de développement")
    run_parser.add_argument("--reload", action="store_true", help="Activer le rechargement à chaud")
    run_parser.add_argument("--port", type=int, default=8081, help="Port à utiliser (défaut: 8081)")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host à utiliser (défaut: 127.0.0.1)")
    run_parser.add_argument("--debug", action="store_true", help="Activer le mode debug")
    run_parser.add_argument("--api-only", action="store_true", help="Lancer le serveur API sans interface graphique")

    # Commande: init
    init_parser = subparsers.add_parser("init", help="Initialiser la base de données")
    init_parser.add_argument("--force", action="store_true", help="Forcer la réinitialisation de la base de données")

    # Commande: test
    test_parser = subparsers.add_parser("test", help="Exécuter les tests")
    test_parser.add_argument("--type", choices=["unit", "api", "integration", "functional", "all"],
                          default="all", help="Type de tests à exécuter")
    test_parser.add_argument("--coverage", action="store_true", help="Générer un rapport de couverture")
    test_parser.add_argument("--unit", action="store_true", help="Exécuter seulement les tests unitaires")
    test_parser.add_argument("--functional", action="store_true", help="Exécuter seulement les tests fonctionnels")
    test_parser.add_argument("--integration", action="store_true", help="Exécuter seulement les tests d'intégration")
    test_parser.add_argument("--api", action="store_true", help="Exécuter seulement les tests API")

    # Commande: validate
    validate_parser = subparsers.add_parser("validate", help="Valider l'application")
    validate_parser.add_argument("--level", choices=["simple", "full", "compatibility"],
                               default="simple", help="Niveau de validation")

    # Commande: shell
    subparsers.add_parser("shell", help="Démarrer un shell Python interactif avec le contexte de l'application")

    # Commande: setup
    setup_parser = subparsers.add_parser("setup", help="Configurer l'environnement de développement")
    setup_parser.add_argument("--python", default="python", help="Interpréteur Python à utiliser")
    setup_parser.add_argument("--full", action="store_true", help="Installation complète avec tests et validation")

    return parser




def run_command(command_args, shell=False):
    """
    Exécute une commande système.

    Args:
        command_args: Liste d'arguments de la commande à exécuter
        shell: Utiliser un shell pour l'exécution

    Returns:
        Tuple (code de retour, sortie, erreur)
    """
    process = subprocess.Popen(
        command_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
        text=True,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr




def activate_venv():
    """
    Active l'environnement virtuel si nécessaire.
    """
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.debug("Environnement virtuel déjà activé")
        return True

    if not os.path.exists(VENV_DIR):
        logger.warning(f"Environnement virtuel non trouvé dans {VENV_DIR}")
        return False

    # L'activation directe de l'environnement virtuel ne fonctionne pas de la même manière
    # que source venv/bin/activate. Nous devons plutôt modifier PATH et PYTHONPATH.
    is_win = platform.system() == "Windows"
    bin_dir = os.path.join(VENV_DIR, "Scripts" if is_win else "bin")

    # Ajouter le répertoire bin au début de PATH
    os.environ["PATH"] = os.pathsep.join([bin_dir, os.environ.get("PATH", "")])

    # Définir VIRTUAL_ENV pour que certains outils sachent qu'un environnement virtuel est activé
    os.environ["VIRTUAL_ENV"] = VENV_DIR

    logger.info(f"Environnement virtuel activé: {VENV_DIR}")
    return True




def cmd_run(args):
    """
    Démarre l'application.
    """
    logger.info("Démarrage de l'application Mathakine")

    # Configurer les variables d'environnement
    os.environ["MATH_TRAINER_DEBUG"] = "true" if args.debug else "false"
    os.environ["MATH_TRAINER_PORT"] = str(args.port)
    os.environ["MATH_TRAINER_PROFILE"] = "dev"  # Toujours utiliser l'environnement de développement par défaut

    # Par défaut, lancer le serveur amélioré sauf si --api-only est utilisé
    if not args.api_only:
        logger.info("Lancement du serveur amélioré (enhanced_server.py) avec interface graphique complète")
        try:
            # Vérifier que enhanced_server.py existe
            if not os.path.exists("enhanced_server.py"):
                logger.error("Le fichier enhanced_server.py n'existe pas!")
                return 1
                
            logger.info(f"Exécution de: {sys.executable} enhanced_server.py")
            process = subprocess.Popen([sys.executable, "enhanced_server.py"])
            logger.success("Serveur amélioré démarré avec succès")
            logger.info("Appuyez sur Ctrl+C pour arrêter le serveur")
            process.wait()
        except KeyboardInterrupt:
            logger.info("Arrêt du serveur Mathakine")
            process.terminate()
            process.wait()
    else:
        logger.info("Lancement du serveur API uniquement")
        try:
            # Utiliser uvicorn directement pour lancer l'application FastAPI
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "app.main:app",
                "--host", "0.0.0.0", "--port", str(args.port), "--reload" if args.debug else ""
            ])
            logger.success("Serveur API démarré avec succès")
            logger.info("Appuyez sur Ctrl+C pour arrêter le serveur")
            process.wait()
        except KeyboardInterrupt:
            logger.info("Arrêt du serveur Mathakine API")
            process.terminate()
            process.wait()




def cmd_init(args):
    """
    Initialise la base de données.
    """
    logger.info("Initialisation de la base de données")

    # Vérifier si la base de données existe déjà
    db_path = os.path.join(BASE_DIR, "math_trainer.db")
    if os.path.exists(db_path) and not args.force:
        logger.warning(f"La base de données existe déjà: {db_path}")
        logger.info("Utilisez --force pour réinitialiser la base de données")
        return 0

    if os.path.exists(db_path) and args.force:
        try:
            logger.warning(f"Suppression de la base de données existante: {db_path}")
            os.remove(db_path)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la base de données: {e}")
            return 1

    # Ajouter le répertoire courant au PYTHONPATH pour permettre l'importation des modules
    sys.path.insert(0, BASE_DIR)

    try:
        from app.db.init_db import create_tables_with_test_data

        logger.info("Création des tables et ajout des données de test")
        create_tables_with_test_data()
        logger.success("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return 1

    return 0




def cmd_test(args):
    """
    Exécute les tests.
    """
    logger.info(f"Exécution des tests: {args.type}")

    # Construire la commande pytest
    cmd = ["pytest"]

    if args.type != "all":
        if args.type == "unit":
            cmd.append("tests/unit/")
        elif args.type == "api":
            cmd.append("tests/api/")
        elif args.type == "integration":
            cmd.append("tests/integration/")
        elif args.type == "functional":
            cmd.append("tests/functional/")

    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])

    cmd.extend(["-v"])

    logger.info(f"Exécution de: {' '.join(cmd)}")

    try:
        returncode, stdout, stderr = run_command(cmd)

        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        if returncode == 0:
            logger.success("Tests réussis")
        else:
            logger.error("Tests échoués")

        if args.coverage:
            logger.info("Rapport de couverture généré dans htmlcov/index.html")

        return returncode
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {e}")
        return 1




def cmd_validate(args):
    """
    Valide l'application.
    """
    logger.info(f"Validation de l'application: {args.level}")

    try:
        if args.level == "simple":
            returncode, stdout, stderr = run_command(["python", "tests/simplified_validation.py"])
        elif args.level == "full":
            returncode, stdout, stderr = run_command(["python", "tests/auto_validation.py"])
        elif args.level == "compatibility":
            returncode, stdout, stderr = run_command(["python", "tests/compatibility_check.py"])

        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        if returncode == 0:
            logger.success("Validation réussie")
        else:
            logger.error("Validation échouée")

        return returncode
    except Exception as e:
        logger.error(f"Erreur lors de la validation: {e}")
        return 1




def cmd_shell(args):
    """
    Démarre un shell Python interactif avec le contexte de l'application.
    """
    logger.info("Démarrage du shell interactif")

    # Ajouter le répertoire courant au PYTHONPATH pour permettre l'importation des modules
    sys.path.insert(0, BASE_DIR)

    # Importer les modules nécessaires
    import code
    from app.db.base import SessionLocal
    from app.models.all_models import __all__ as all_models

    # Créer une session de base de données
    session = SessionLocal()

    # Récupérer les modèles importés
    model_classes = {}
    for model_name in all_models:
        module_name, class_name = model_name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        model_class = getattr(module, class_name)
        model_classes[class_name] = model_class

    # Variables à exposer dans le shell
    context = {
        "session": session,
        **model_classes
    }

    # Afficher des informations utiles
    print("\n=== Shell Interactif Mathakine ===")
    print("Variables disponibles:")
    print("  session - Session SQLAlchemy")
    for class_name in model_classes:
        print(f"  {class_name} - Modèle {class_name}")
    print("\nExemples d'utilisation:")
    print("  session.query(User).all()  # Liste tous les utilisateurs")
    print("  session.query(Exercise).filter_by(difficulty='INITIE').all()  # Liste les exercices faciles")
    print("=================================\n")

    # Démarrer le shell interactif
    code.interact(local=context, banner="")

    # Fermer la session
    session.close()

    return 0




def cmd_setup(args):
    """
    Configure l'environnement de développement.
    """
    logger.info("Configuration de l'environnement de développement")

    # Vérifier si l'environnement virtuel existe déjà
    if os.path.exists(VENV_DIR):
        logger.warning(f"L'environnement virtuel existe déjà: {VENV_DIR}")
        response = input("Voulez-vous le recréer? (o/n) [n]: ").lower()
        if response != "o":
            logger.info("Configuration annulée")
            return 0

        # Supprimer l'environnement virtuel existant
        try:
            import shutil
            logger.warning(f"Suppression de l'environnement virtuel existant: {VENV_DIR}")
            shutil.rmtree(VENV_DIR)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'environnement virtuel: {e}")
            return 1

    # Créer l'environnement virtuel
    logger.info(f"Création de l'environnement virtuel: {VENV_DIR}")
    try:
        returncode, stdout, stderr = run_command([args.python, "-m", "venv", VENV_DIR])
        if returncode != 0:
            logger.error(f"Erreur lors de la création de l'environnement virtuel: {stderr}")
            return 1
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'environnement virtuel: {e}")
        return 1

    # Activer l'environnement virtuel
    activate_venv()

    # Installer les dépendances
    logger.info("Installation des dépendances")
    try:
        returncode, stdout, stderr = run_command([sys.executable, "-m", "pip", "install"
            , "-r", "requirements.txt"])
        if returncode != 0:
            logger.error(f"Erreur lors de l'installation des dépendances: {stderr}")
            return 1
    except Exception as e:
        logger.error(f"Erreur lors de l'installation des dépendances: {e}")
        return 1

    # Installer les dépendances spécifiques à Python 3.13
    python_version = platform.python_version()
    if python_version.startswith("3.13"):
        logger.info("Installation des dépendances spécifiques à Python 3.13")
        try:
            returncode, stdout, stderr = run_command([sys.executable, "-m", "pip", "install",
                                                  "sqlalchemy>=2.0.27",
                                                  "fastapi>=0.100.0",
                                                  "pydantic>=2.0.0",
                                                  "pydantic-settings"])
            if returncode != 0:
                logger.error(f"Erreur lors de l'installation des dépendances spécifiques: {stderr}")
                return 1
        except Exception as e:
            logger.error(f"Erreur lors de l'installation des dépendances spécifiques: {e}")
            return 1

    # Installer les dépendances supplémentaires pour les tests et la validation
    if args.full:
        logger.info("Installation des dépendances pour les tests et la validation")
        try:
            returncode, stdout, stderr = run_command([sys.executable, "-m", "pip", "install",
                                                  "pytest", "pytest-cov", "black"\
                                                      , "flake8", "mypy"])
            if returncode != 0:
                logger.error(f"Erreur lors de l'installation des dépendances de test: {stderr}")
                return 1
        except Exception as e:
            logger.error(f"Erreur lors de l'installation des dépendances de test: {e}")
            return 1

    # Initialisation de la base de données
    logger.info("Initialisation de la base de données")
    result = cmd_init(argparse.Namespace(force=True))
    if result != 0:
        return result

    logger.success("Environment de développement configuré avec succès")
    logger.info(f"Pour activer l'environnement virtuel:")

    if platform.system() == "Windows":
        logger.info(f"  {VENV_DIR}\\Scripts\\activate")
    else:
        logger.info(f"  source {VENV_DIR}/bin/activate")

    logger.info(f"Pour démarrer l'application:")
    logger.info(f"  python {sys.argv[0]} run")

    return 0




def main():
    """
    Fonction principale du CLI.
    """
    parser = setup_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    # Activer l'environnement virtuel si nécessaire, sauf pour la commande setup
    if args.command != "setup":
        activate_venv()

    # Exécuter la commande appropriée
    if args.command == "run":
        return cmd_run(args)
    elif args.command == "init":
        return cmd_init(args)
    elif args.command == "test":
        return cmd_test(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "shell":
        return cmd_shell(args)
    elif args.command == "setup":
        return cmd_setup(args)
    else:
        logger.error(f"Commande inconnue: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
