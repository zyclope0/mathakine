from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger.info(f"Initialisation de la base de données: {settings.SQLALCHEMY_DATABASE_URL}")

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
