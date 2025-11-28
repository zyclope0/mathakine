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
        SECRET_KEY = secrets.token_urlsafe(32)
    
    # 60 minutes * 24 heures * 7 jours = 7 jours
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # Nombre de jours pour l'expiration du refresh token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
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
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Modèle par défaut
    
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
        
        # Vérifier que SECRET_KEY n'est pas vide
        if not settings.SECRET_KEY or settings.SECRET_KEY == "":
            logger.error("SECRET_KEY non défini en production - CRITIQUE")
            # Ne pas lever d'exception ici pour permettre le démarrage avec génération auto
            # mais logger l'erreur pour alerter l'administrateur

# Valider les paramètres au chargement du module
validate_production_settings()

# Configuration pour les tests
if settings.TESTING:
    print(f"Mode test détecté, utilisation de l'URL de base de données: {settings.SQLALCHEMY_DATABASE_URL}")
    # Autres configurations spécifiques aux tests
