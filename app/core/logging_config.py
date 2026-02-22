"""
Configuration centralisée de la journalisation pour le projet Mathakine.
Ce module configure loguru pour enregistrer les logs dans un dossier centralisé.

Politique PII/secrets : voir docs/03-PROJECT/POLITIQUE_REDACTION_LOGS_PII.md
"""
import contextvars
import os
import sys
from pathlib import Path

from loguru import logger

# Contextvar pour request_id (corrélation logs + Sentry, un seul outil)
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

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

# Format des logs (request_id pour corrélation Sentry / agrégation)
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <dim>{extra[request_id]}</dim> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


def _add_request_id_to_record(record):
    """Patcher : injecte request_id dans chaque record (corrélation)."""
    record["extra"]["request_id"] = request_id_ctx.get() or "-"



def configure_logging(remove_existing_handlers=True):
    """
    Configure la journalisation pour l'application.
    Injecte request_id (corrélation) via patcher. Politique PII : POLITIQUE_REDACTION_LOGS_PII.md

    Args:
        remove_existing_handlers (bool): Si True, supprime tous les handlers existants avant de configurer.
    """
    # Supprimer les gestionnaires existants
    if remove_existing_handlers:
        logger.remove()

    # Patcher : request_id dans chaque log (corrélation avec Sentry)
    logger.configure(patcher=_add_request_id_to_record)

    # Sur Windows avec uvicorn --reload : parent + child ouvrent les mêmes fichiers → PermissionError
    # lors de rotation ou écriture concurrente. On n'écrit que vers stderr sur Windows.
    _is_windows = sys.platform == "win32"
    _debug_mode = os.environ.get("MATH_TRAINER_DEBUG", "false").lower() == "true"
    _use_file_logging = not _is_windows and not _debug_mode

    # Journalisation dans la console (toujours)
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=os.environ.get("LOG_LEVEL", "INFO"),
        colorize=True,
    )

    # Fichiers : uniquement hors Windows et hors mode debug
    if _use_file_logging:
        _rotation, _rotation_all = "10 MB", "20 MB"
        for level, log_file in LOG_LEVELS.items():
            logger.add(
                log_file,
                format=LOG_FORMAT,
                level=level,
                rotation=_rotation,
                compression="zip",
                retention="30 days",
                enqueue=True,
            )
        logger.add(
            str(LOGS_DIR / "all.log"),
            format=LOG_FORMAT,
            level="DEBUG",
            rotation=_rotation_all,
            compression="zip",
            retention="60 days",
            enqueue=True,
        )
        logger.add(
            str(LOGS_DIR / "uncaught_exceptions.log"),
            format=LOG_FORMAT,
            level="ERROR",
            rotation=_rotation,
            compression="zip",
            retention="60 days",
            backtrace=True,
            diagnose=True,
            enqueue=True,
            catch=True,
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
