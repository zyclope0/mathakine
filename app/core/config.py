"""
Configuration de l'application via pydantic-settings.
Charge les variables depuis l'environnement (.env en dev, vars injectées en prod).
"""
import os
import secrets
from typing import List

from dotenv import load_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Chargement .env en dev (prod : vars injectées par l'hôte uniquement)
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv(override=False)
logger.info("Chargement de la configuration...")


def _is_production() -> bool:
    return (
        os.getenv("NODE_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
        or os.getenv("MATH_TRAINER_PROFILE") == "prod"
    )


class Settings(BaseSettings):
    """
    Configuration de l'application. Hérite de pydantic-settings pour
    typage, validation et chargement depuis les variables d'environnement.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Mathakine"
    PROJECT_VERSION: str = "2.1.0"
    API_V1_STR: str = "/api"

    SECRET_KEY: str = Field(default="", description="Clé secrète JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UNVERIFIED_GRACE_PERIOD_MINUTES: int = Field(default=45, ge=0)
    ALGORITHM: str = "HS256"

    # Base de données
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="mathakine")
    DATABASE_URL: str = Field(default="")
    TEST_DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost/test_mathakine")
    TESTING: bool = Field(default=False)

    DEFAULT_ADMIN_EMAIL: str = Field(default="")
    DEFAULT_ADMIN_PASSWORD: str = Field(default="")

    # CORS : liste de base + FRONTEND_URL si défini
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)

    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/mathakine.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    EXERCISES_PER_PAGE: int = 10
    AUTO_GENERATE_EXERCISES: int = 50
    AI_GENERATED_PERCENT: int = 20

    ENABLE_QUERY_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 300
    MAX_CONNECTIONS_POOL: int = 20
    POOL_RECYCLE_SECONDS: int = 3600

    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_CONTENT_LENGTH: int = 16_777_216
    SECURE_HEADERS: bool = True

    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    ENABLE_GZIP: bool = True
    GZIP_MINIMUM_SIZE: int = 1024

    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_MODEL_REASONING: str = Field(default="")

    @model_validator(mode="after")
    def build_computed_and_validate(self):
        # DATABASE_URL : construire depuis POSTGRES_* si non fourni
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

        # BACKEND_CORS_ORIGINS : valeur par défaut si vide
        if not self.BACKEND_CORS_ORIGINS:
            self.BACKEND_CORS_ORIGINS = [
                "http://localhost:8000",
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
            if os.getenv("FRONTEND_URL"):
                self.BACKEND_CORS_ORIGINS.append(os.getenv("FRONTEND_URL", ""))

        # SECRET_KEY : prod = obligatoire ; dev = génération auto si vide
        is_prod = _is_production()
        if not self.SECRET_KEY:
            if is_prod and not self.TESTING:
                raise ValueError(
                    "SECRET_KEY doit être définie en production. "
                    'Générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )
            self.SECRET_KEY = secrets.token_urlsafe(32)
            logger.warning("SECRET_KEY non définie, génération automatique (DEV uniquement)")

        return self

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """URL de la base : TEST_DATABASE_URL en mode test, sinon DATABASE_URL."""
        return self.TEST_DATABASE_URL if self.TESTING else self.DATABASE_URL


settings = Settings()

# Validation post-initialisation pour la sécurité en production
def _validate_production_settings():
    if not _is_production():
        return
    if settings.LOG_LEVEL.upper() == "DEBUG":
        logger.warning("LOG_LEVEL=DEBUG détecté en production - Forcé à INFO pour sécurité")
        object.__setattr__(settings, "LOG_LEVEL", "INFO")
    if (
        os.getenv("ENVIRONMENT") == "production"
        and not settings.TESTING
        and (
            not settings.DEFAULT_ADMIN_PASSWORD
            or settings.DEFAULT_ADMIN_PASSWORD in ("admin", "password", "123456")
        )
    ):
        raise ValueError(
            "DEFAULT_ADMIN_PASSWORD doit être définie et forte en production "
            "(éviter admin, password, 123456). Définir dans les variables Render."
        )


_validate_production_settings()

if settings.TESTING:
    logger.info(f"Mode test détecté, utilisation de l'URL: {settings.SQLALCHEMY_DATABASE_URL}")
