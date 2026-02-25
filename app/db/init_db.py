from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Importer les modèles pour assurer qu'ils sont enregistrés par SQLAlchemy
import app.models.all_models  # noqa: F401
from app.services.db_init_service import create_tables, populate_test_data


def create_tables_with_test_data():
    """Crée toutes les tables définies dans les modèles et ajoute des données de test.

    ATTENTION : Cette fonction ne doit être appelée que dans un contexte de test (CI)
    ou pour initialiser une base de développement vide.
    Ne JAMAIS appeler en production.
    """
    import os

    logger.info("Initialisation de la base de données")
    try:
        # Créer les tables
        create_tables()

        # Ajouter des données de test UNIQUEMENT si TESTING=true ou base vide en dev
        is_testing = os.getenv("TESTING", "false").lower() == "true"
        environment = os.getenv("ENVIRONMENT", "development")

        if is_testing:
            logger.info("Mode test détecté : ajout des données de test")
            populate_test_data()
        elif environment != "production":
            logger.info("Mode développement : ajout des données de test si base vide")
            populate_test_data()
        else:
            logger.info("Mode production : pas de données de test")

        logger.success("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise
