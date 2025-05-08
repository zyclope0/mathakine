from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os
from dotenv import load_dotenv
from loguru import logger

# Configuration du logger
logger.add("debug.log", rotation="10 MB", level="DEBUG")
logger.info("Chargement de la configuration...")

# Chargement des variables d'environnement
load_dotenv()

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

settings = Settings() 