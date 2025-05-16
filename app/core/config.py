from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os
from dotenv import load_dotenv
from app.core.logging_config import get_logger
import secrets

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Chargement des variables d'environnement
load_dotenv(override=True)  # Forcer le rechargement des variables d'environnement
logger.info("Chargement de la configuration...")



class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Math Trainer"

    # Database - forcer le rechargement depuis .env
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./math_trainer.db")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Front-end React/Vue
        "http://localhost:8080",
    ]

    # Security
    ALLOWED_HOSTS: List[str] = ["*"] if os.getenv("DEBUG", "True").lower() == "true" else [
        "localhost",
        "127.0.0.1",
        os.getenv("DOMAIN", "localhost")
    ]
    
    # JWT Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))  # 7 jours

    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # API Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: str = os.getenv("API_KEY", "dev-key")

    # Logs
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "logs")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Forcer la relecture depuis l'environnement
        self.DATABASE_URL = os.environ.get("DATABASE_URL", self.DATABASE_URL)
        
        logger.debug(f"Configuration initialisée: DATABASE_URL={self.DATABASE_URL}")
        logger.info(f"URL de la base de données: {self.DATABASE_URL}")
        logger.debug(f"Mode debug: {self.DEBUG}")
        logger.debug(f"Hosts autorisés: {self.ALLOWED_HOSTS}")
        logger.debug(f"Niveau de log: {self.LOG_LEVEL}")

# Création d'une instance unique des paramètres
settings = Settings()
