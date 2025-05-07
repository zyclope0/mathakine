from loguru import logger
from app.db.base import Base, engine
# Importer les modèles pour assurer qu'ils sont enregistrés par SQLAlchemy
from app.models.all_models import __all__ as models  # Import all models

def create_tables():
    """Crée toutes les tables définies dans les modèles."""
    logger.info("Tentative de création des tables dans la base de données")
    try:
        Base.metadata.create_all(bind=engine)
        logger.success("Tables créées avec succès (ou déjà existantes)")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables: {e}")
        raise 