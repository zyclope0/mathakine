from pydantic import BaseSettings
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
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Configuration initialisée: DATABASE_URL={self.DATABASE_URL}")
        logger.debug(f"Mode debug: {self.DEBUG}")

settings = Settings() 