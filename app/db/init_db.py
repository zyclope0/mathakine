from loguru import logger
from app.db.base import Base, engine
# Importer les modèles pour assurer qu'ils sont enregistrés par SQLAlchemy
from app.models.all_models import __all__ as models  # Import all models
from app.services.db_init_service import create_tables, populate_test_data

def create_tables_with_test_data():
    """Crée toutes les tables définies dans les modèles et ajoute des données de test."""
    logger.info("Initialisation de la base de données")
    try:
        # Créer les tables
        create_tables()
        
        # Ajouter des données de test si nécessaire
        if "true" == "true":  # Toujours ajouter des données de test en développement
            populate_test_data()
            
        logger.success("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise 