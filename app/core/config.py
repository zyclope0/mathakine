import os
import secrets
from typing import List

from dotenv import load_dotenv
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

from app.core.logging_config import get_logger

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Chargement des variables d'environnement
load_dotenv(override=True)  # Forcer le rechargement des variables d'environnement
logger.info("Chargement de la configuration...")

# Base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/mathakine")

# Fichier temporaire supprimé, utilisation exclusive de PostgreSQL
# SQLALCHEMY_DATABASE_URL = DATABASE_URL if "test" not in DATABASE_URL else DATABASE_URL

# Pour les tests, utiliser une URL spécifique
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost/test_mathakine")

# Classe de configuration
class Settings:
    """
    Classe contenant les paramètres de configuration de l'application.
    """
    PROJECT_NAME: str = "Mathakine"
    PROJECT_VERSION: str = "1.5.0"
    
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    if not SECRET_KEY:
        if (
            os.getenv("ENVIRONMENT") == "production"
            and os.getenv("TESTING", "false").lower() != "true"
        ):
            raise ValueError(
                "SECRET_KEY doit être définie en production. "
                "Générer avec: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        SECRET_KEY = secrets.token_urlsafe(32)
        logger.warning("SECRET_KEY non définie, génération automatique (DEV uniquement)")
    
    # 15 minutes (best-practice: court pour limiter la fenêtre si volé)
    # Le refresh automatique prolonge la session sans re-login
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    # 7 jours (best-practice: refresh token plus long mais rotation à chaque utilisation)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Algorithme de chiffrement pour JWT
    ALGORITHM: str = "HS256"
    
    # Configuration de la base de données
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "mathakine")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}")
    
    # URL pour les tests
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost/test_mathakine")
    
    # Mode de test
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    # Utilisez cette URL pour les tests
    SQLALCHEMY_DATABASE_URL: str = TEST_DATABASE_URL if TESTING else DATABASE_URL
    
    # Utilisateurs par défaut
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@mathakine.com")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
    
    # Paramètres CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_URL", ""),
    ]
    
    # Configuration de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/mathakine.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Nombre d'exercices par page
    EXERCISES_PER_PAGE: int = 10
    
    # Nombre d'exercices générés automatiquement
    AUTO_GENERATE_EXERCISES: int = 50
    
    # Pourcentage d'exercices générés par IA
    AI_GENERATED_PERCENT: int = 20
    
    # Configuration d'optimisation performance
    ENABLE_QUERY_CACHE: bool = os.getenv("ENABLE_QUERY_CACHE", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes
    MAX_CONNECTIONS_POOL: int = int(os.getenv("MAX_CONNECTIONS_POOL", "20"))
    POOL_RECYCLE_SECONDS: int = int(os.getenv("POOL_RECYCLE_SECONDS", "3600"))  # 1 heure
    
    # Configuration sécurité
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB
    SECURE_HEADERS: bool = os.getenv("SECURE_HEADERS", "true").lower() == "true"
    
    # Configuration monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Configuration compression
    ENABLE_GZIP: bool = os.getenv("ENABLE_GZIP", "true").lower() == "true"
    GZIP_MINIMUM_SIZE: int = int(os.getenv("GZIP_MINIMUM_SIZE", "1024"))  # 1KB
    
    # Configuration OpenAI pour génération IA
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Modèle par défaut (exercices)
    # Modèle o1/o1-mini pour raisonnement mathématique - MÊME CLÉ API
    # Si défini : défis logiques (séquences, patterns) + exercices fractions. o1-mini = moins cher, o1 = plus capable.
    OPENAI_MODEL_REASONING: str = os.getenv("OPENAI_MODEL_REASONING", "")  # ex: "o3", "o1-mini"
    
    class Config:
        case_sensitive = True

settings = Settings()

# Validation post-initialisation pour la sécurité en production
def validate_production_settings():
    """Valide les paramètres de sécurité en production après initialisation"""
    is_production = (
        os.getenv("NODE_ENV") == "production" or 
        os.getenv("ENVIRONMENT") == "production" or
        os.getenv("MATH_TRAINER_PROFILE") == "prod"
    )
    
    if is_production:
        # Forcer LOG_LEVEL à INFO minimum en production
        if settings.LOG_LEVEL.upper() == "DEBUG":
            logger.warning("LOG_LEVEL=DEBUG détecté en production - Forcé à INFO pour sécurité")
            settings.LOG_LEVEL = "INFO"
        
        # SECRET_KEY : blocage au démarrage si vide (voir init Settings)
        # 3.3 DEFAULT_ADMIN_PASSWORD : bloquer si faible en prod (évite compte admin exploitable)
        # Uniquement si ENVIRONMENT=production (Render), pas MATH_TRAINER_PROFILE (peut être prod en local)
        if (
            os.getenv("ENVIRONMENT") == "production"
            and os.getenv("TESTING", "false").lower() != "true"
            and (
                not settings.DEFAULT_ADMIN_PASSWORD
                or settings.DEFAULT_ADMIN_PASSWORD == "admin"
            )
        ):
            raise ValueError(
                "DEFAULT_ADMIN_PASSWORD doit être définie et différente de 'admin' en production. "
                "Définir une valeur forte dans les variables d'environnement Render."
            )

# Valider les paramètres au chargement du module
validate_production_settings()

# Configuration pour les tests
if settings.TESTING:
    logger.info(f"Mode test détecté, utilisation de l'URL de base de données: {settings.SQLALCHEMY_DATABASE_URL}")
    # Autres configurations spécifiques aux tests
