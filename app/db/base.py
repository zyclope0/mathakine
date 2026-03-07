from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

REDACTED_PLACEHOLDER = "[redacted-db-url]"


def redact_database_url_for_log(raw_url: str) -> str:
    """
    Retourne une version sûre de l'URL DB pour les logs.
    Ne jamais exposer : password, username complet, query params.
    """
    if not raw_url or not isinstance(raw_url, str):
        return REDACTED_PLACEHOLDER
    raw_url = raw_url.strip()
    if not raw_url:
        return REDACTED_PLACEHOLDER
    try:
        parsed = urlparse(raw_url)
        scheme = (parsed.scheme or "").lower()
        if not scheme or scheme not in ("postgresql", "postgres", "mysql"):
            if scheme == "sqlite":
                return "sqlite://[redacted]"
            return REDACTED_PLACEHOLDER
        netloc = parsed.hostname or "unknown"
        port = f":{parsed.port}" if parsed.port else ""
        path = parsed.path or "/"
        safe_netloc = f"<redacted>@{netloc}{port}" if netloc else "<redacted>"
        return f"{scheme}://{safe_netloc}{path}"
    except Exception:
        return REDACTED_PLACEHOLDER


logger.info(
    f"Initialisation de la base de données: {redact_database_url_for_log(settings.SQLALCHEMY_DATABASE_URL)}"
)

try:
    # Configuration pour PostgreSQL avec pool de connexions optimisé
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        echo=settings.LOG_LEVEL
        == "DEBUG",  # Affiche les requêtes SQL dans les logs si niveau DEBUG
        pool_pre_ping=True,  # Vérifie les connexions avant utilisation (évite les erreurs de connexion)
        pool_size=settings.MAX_CONNECTIONS_POOL,  # Nombre de connexions dans le pool
        max_overflow=settings.MAX_CONNECTIONS_POOL
        * 2,  # Nombre max de connexions supplémentaires
        pool_recycle=settings.POOL_RECYCLE_SECONDS,  # Recycle les connexions après X secondes
        pool_timeout=30,  # Timeout pour obtenir une connexion du pool
    )
    logger.success("Moteur SQLAlchemy (PostgreSQL) créé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation du moteur SQLAlchemy: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.debug("Session SQLAlchemy configurée")

Base = declarative_base()
logger.debug("Base déclarative configurée")


# Helper pour obtenir une session de base de données
def get_db():
    """Générateur pour obtenir une session de base de données avec nettoyage automatique."""
    logger.debug("Ouverture d'une nouvelle session de base de données")
    db = SessionLocal()
    try:
        yield db
    except Exception as db_error:
        # Rollback en cas d'erreur
        logger.warning(f"Erreur dans la session DB, rollback: {db_error}")
        db.rollback()
        raise
    finally:
        # Toujours fermer la session
        try:
            logger.debug("Fermeture de la session de base de données")
            db.close()
        except Exception as close_error:
            logger.error(f"Erreur lors de la fermeture de la session: {close_error}")
