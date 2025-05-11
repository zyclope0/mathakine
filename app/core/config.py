from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os
from dotenv import load_dotenv
from app.core.logging_config import get_logger

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Chargement des variables d'environnement
load_dotenv()
logger.info("Chargement de la configuration...")



class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Math Trainer"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./math_trainer.db")

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
        logger.debug(f"Configuration initialisée: DATABASE_URL={self.DATABASE_URL}")
        logger.debug(f"Mode debug: {self.DEBUG}")
        logger.debug(f"Hosts autorisés: {self.ALLOWED_HOSTS}")
        logger.debug(f"Niveau de log: {self.LOG_LEVEL}")

settings = Settings()
