from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Importer les modèles pour assurer qu'ils sont enregistrés par SQLAlchemy (Base.metadata.create_all)
import app.models.achievement  # noqa: F401
import app.models.admin_audit_log  # noqa: F401
import app.models.attempt  # noqa: F401
import app.models.daily_challenge  # noqa: F401
import app.models.diagnostic_result  # noqa: F401
import app.models.edtech_event  # noqa: F401
import app.models.exercise  # noqa: F401
import app.models.feedback_report  # noqa: F401
import app.models.logic_challenge  # noqa: F401
import app.models.notification  # noqa: F401
import app.models.progress  # noqa: F401
import app.models.recommendation  # noqa: F401
import app.models.setting  # noqa: F401
import app.models.user  # noqa: F401
import app.models.user_session  # noqa: F401
from app.services.core.db_init_service import create_tables, populate_test_data


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
        logger.error("Erreur lors de l'initialisation de la base de données: %s", e)
        raise
