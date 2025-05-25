from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger

from app.core.config import settings

logger.info(f"Initialisation de la base de données: {settings.DATABASE_URL}")

try:
    # Configuration pour PostgreSQL
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        echo=settings.LOG_LEVEL == "DEBUG"  # Affiche les requêtes SQL dans les logs si niveau DEBUG
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
    logger.debug("Ouverture d'une nouvelle session de base de données")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Fermeture de la session de base de données")
        db.close()
