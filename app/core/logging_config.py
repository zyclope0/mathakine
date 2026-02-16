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

    # En mode debug/reload (uvicorn --reload), plusieurs processus écrivent dans les mêmes
    # fichiers. Sur Windows, la rotation (rename) provoque PermissionError car un autre
    # processus garde le fichier ouvert. On désactive la rotation en dev.
    _debug_mode = os.environ.get("MATH_TRAINER_DEBUG", "false").lower() == "true"
    _rotation = False if _debug_mode else "10 MB"
    _rotation_all = False if _debug_mode else "20 MB"

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
            rotation=_rotation,
            compression="zip" if _rotation else None,
            retention="30 days" if _rotation else None,
            enqueue=True,  # Thread-safe
        )

    # Log général pour tous les niveaux
    logger.add(
        str(LOGS_DIR / "all.log"),
        format=LOG_FORMAT,
        level="DEBUG",
        rotation=_rotation_all,
        compression="zip" if _rotation_all else None,
        retention="60 days" if _rotation_all else None,
        enqueue=True,
    )

    # Log des erreurs non capturées
    logger.add(
        str(LOGS_DIR / "uncaught_exceptions.log"),
        format=LOG_FORMAT,
        level="ERROR",
        rotation=_rotation,
        compression="zip" if _rotation else None,
        retention="60 days" if _rotation else None,
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
