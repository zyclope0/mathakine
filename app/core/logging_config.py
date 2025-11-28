"""
Configuration centralisée de la journalisation pour le projet Mathakine.
Ce module configure loguru pour enregistrer les logs dans un dossier centralisé.
"""

import os
import sys
from pathlib import Path

from loguru import logger

# Chemins pour les logs
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
LOGS_DIR = PROJECT_ROOT / "logs"

# Création du dossier logs s'il n'existe pas
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True)

# Niveaux de log et leurs fichiers correspondants
LOG_LEVELS = {
    "DEBUG": str(LOGS_DIR / "debug.log"),
    "INFO": str(LOGS_DIR / "info.log"),
    "WARNING": str(LOGS_DIR / "warning.log"),
    "ERROR": str(LOGS_DIR / "error.log"),
    "CRITICAL": str(LOGS_DIR / "critical.log"),
}

# Format des logs
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan>\
    - <level>{message}</level>"



def configure_logging(remove_existing_handlers=True):
    """
    Configure la journalisation pour l'application.

    Args:
        remove_existing_handlers (bool): Si True, supprime tous les handlers existants avant de configurer.
    """
    # Supprimer les gestionnaires existants
    if remove_existing_handlers:
        logger.remove()

    # Ajouter la journalisation dans la console
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=os.environ.get("LOG_LEVEL", "INFO"),
        colorize=True,
    )

    # Journalisation des niveaux spécifiques dans des fichiers dédiés
    for level, log_file in LOG_LEVELS.items():
        logger.add(
            log_file,
            format=LOG_FORMAT,
            level=level,
            rotation="10 MB",
            compression="zip",
            retention="30 days",
            enqueue=True,  # Thread-safe
        )

    # Log général pour tous les niveaux
    logger.add(
        str(LOGS_DIR / "all.log"),
        format=LOG_FORMAT,
        level="DEBUG",
        rotation="20 MB",
        compression="zip",
        retention="60 days",
        enqueue=True,
    )

    # Log des erreurs non capturées
    logger.add(
        str(LOGS_DIR / "uncaught_exceptions.log"),
        format=LOG_FORMAT,
        level="ERROR",
        rotation="10 MB",
        compression="zip",
        retention="60 days",
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,  # Capture les exceptions non gérées
    )

    logger.info("Journalisation configurée avec succès")
    logger.debug(f"Dossier des logs: {LOGS_DIR}")

# Configuration automatique lors de l'importation du module
configure_logging()

# Fonction d'assistance pour obtenir un logger nommé


def get_logger(name):
    """
    Renvoie un logger configuré avec un nom spécifique.

    Args:
        name (str): Le nom du logger, généralement __name__ du module appelant.

    Returns:
        loguru.logger: Une instance de logger loguru configurée.
    """
    return logger.bind(name=name)
