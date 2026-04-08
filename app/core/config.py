"""
Configuration de l'application via pydantic-settings.
Charge les variables depuis l'environnement (.env en dev, vars injectées en prod).

Source de vérité (lot A44-S4) :
- champs typés et validés : classe ``Settings`` dans ce module ;
- modèle local commenté : ``.env.example`` à la racine du dépôt.

Variables lues ailleurs via ``os.getenv`` (non déclarées dans ``Settings``) :
email SMTP/SendGrid → ``app/services/communication/email_service.py`` ;
Sentry → ``app/core/monitoring.py``.
"""

import os
import secrets
from typing import List
from urllib.parse import urlparse

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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        ge=1,
        description="JWT access token lifetime in minutes (nominal 15; align .env.example).",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UNVERIFIED_GRACE_PERIOD_MINUTES: int = Field(default=45, ge=0)
    ALGORITHM: str = "HS256"

    # Base de données
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="mathakine")
    DATABASE_URL: str = Field(default="")
    TEST_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost/test_mathakine"
    )
    TESTING: bool = Field(default=False)

    DEFAULT_ADMIN_EMAIL: str = Field(default="")
    DEFAULT_ADMIN_PASSWORD: str = Field(default="")

    FRONTEND_URL: str = Field(default="https://mathakine-frontend.onrender.com")

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

    # Redis — rate limit distribue (C2).
    # Dev/test : vide = fallback memoire mono-instance (acceptable).
    # Prod : OBLIGATOIRE — _validate_production_settings() leve ValueError si absent.
    REDIS_URL: str = Field(
        default="",
        description=(
            "URL Redis pour rate limit distribue. "
            "Vide = memoire locale (dev/test uniquement). "
            "OBLIGATOIRE en production (ENVIRONMENT=production) — "
            "le demarrage echoue explicitement si absent. "
            "Ex: redis://localhost:6379/0 | rediss://user:pass@host:6380 (TLS Render)."
        ),
    )
    # FFI-L19C — cle rate-limit auth : X-Forwarded-For seulement si le bord de confiance
    # reecrit/append la chaine (ex. Render). Mettre false si le backend est joignable
    # directement par des clients qui pourraient forger XFF, ou pour forcer la peer IP.
    RATE_LIMIT_TRUST_X_FORWARDED_FOR: bool = Field(
        default=False,
        description=(
            "Si True (opt-in explicite derriere proxy de confiance): premiere IP non vide de "
            "X-Forwarded-For sert de cle rate-limit quand l'en-tete est present. "
            "Si False (defaut conservateur): ignorer X-Forwarded-For et utiliser uniquement request.client.host."
        ),
    )
    SECURE_HEADERS: bool = True

    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    ENABLE_GZIP: bool = True
    GZIP_MINIMUM_SIZE: int = 1024

    OPENAI_API_KEY: str = Field(default="")
    # Legacy optionnel : si non vide et allowlist fail-closed assistant (IA10b), peut piloter assistant_chat.
    # (voir app.core.app_model_policy). Laisser vide = défaut produit gpt-5-mini.
    OPENAI_MODEL: str = Field(
        default="",
        description="Legacy : compat déploiements anciens. Vide recommandé ; override chat explicite = OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE.",
    )
    OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE: str = Field(
        default="",
        description="Override ops : assistant_chat (REST/SSE). Vide = gpt-5-mini. Allowlist fail-closed IA10b : "
        "gpt-5-mini, gpt-5.4, gpt-4o-mini, gpt-4o (voir ASSISTANT_CHAT_ALLOWED_MODEL_IDS).",
    )
    OPENAI_MODEL_REASONING: str = Field(
        default="",
        description="Legacy défis IA seulement (si OPENAI_MODEL_CHALLENGES_OVERRIDE vide). Non nominal : défaut policy code = o3.",
    )
    # Override ops du flux SSE exercices IA (prioritaire sur la policy applicative). Voir app.core.ai_generation_policy.
    OPENAI_MODEL_EXERCISES_OVERRIDE: str = Field(
        default="",
        description="Override opérationnel : modèle OpenAI pour exercices IA (SSE). Vide = policy applicative.",
    )
    OPENAI_MODEL_EXERCISES: str = Field(
        default="",
        description="Déprécié : même rôle qu'OPENAI_MODEL_EXERCISES_OVERRIDE si celui-ci est vide.",
    )
    # Flux SSE défis IA — prioritaire sur OPENAI_MODEL_REASONING (legacy). Vide = policy défis en code.
    OPENAI_MODEL_CHALLENGES_OVERRIDE: str = Field(
        default="",
        description="Override opérationnel : modèle OpenAI pour défis IA (SSE). "
        "Prioritaire sur OPENAI_MODEL_REASONING si non vide. Allowlist = EXERCISES_AI_ALLOWED_MODEL_IDS.",
    )
    OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE: str = Field(
        default="",
        description="Override ops : modèle appelé si le stream défis o3/o3-mini renvoie un contenu vide. "
        "Vide = défaut policy (challenge_ai_model_policy). Allowlist = EXERCISES_AI_ALLOWED_MODEL_IDS.",
    )

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
            # Origines **navigateur** autorisées (frontend), pas le port d’écoute API.
            origins: list = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
            frontend_url = self.FRONTEND_URL
            if frontend_url:
                origins.append(frontend_url)
                try:
                    from urllib.parse import urlparse

                    parsed = urlparse(frontend_url)
                    if parsed.netloc and "." in parsed.netloc:
                        if not parsed.netloc.startswith("www."):
                            origins.append(f"{parsed.scheme}://www.{parsed.netloc}")
                        else:
                            origins.append(f"{parsed.scheme}://{parsed.netloc[4:]}")
                except Exception:
                    pass
                if (
                    "mathakine" in frontend_url.lower()
                    and "render.com" not in frontend_url
                ):
                    origins.append("https://mathakine-frontend.onrender.com")
            object.__setattr__(
                self,
                "BACKEND_CORS_ORIGINS",
                list(dict.fromkeys(o for o in origins if o)),
            )

        # SECRET_KEY : prod = obligatoire ; dev = génération auto si vide
        is_prod = _is_production()
        if not self.SECRET_KEY:
            if is_prod and not self.TESTING:
                raise ValueError(
                    "SECRET_KEY doit être définie en production. "
                    'Générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )
            self.SECRET_KEY = secrets.token_urlsafe(32)
            logger.warning(
                "SECRET_KEY non définie, génération automatique (DEV uniquement)"
            )

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
        logger.warning(
            "LOG_LEVEL=DEBUG détecté en production - Forcé à INFO pour sécurité"
        )
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

    # S3 — audit 03/03/2026 : rejeter les credentials DB par défaut en production.
    # Guard : seulement si DATABASE_URL n'est pas fourni directement (Render l'injecte
    # comme URL complète sans passer par POSTGRES_PASSWORD).
    if (
        os.getenv("ENVIRONMENT") == "production"
        and not settings.TESTING
        and not os.getenv("DATABASE_URL")
        and settings.POSTGRES_PASSWORD in ("", "postgres", "password")
    ):
        raise ValueError(
            "POSTGRES_PASSWORD utilise une valeur par défaut non sécurisée en production. "
            "Définir une valeur forte dans les variables d'environnement Render."
        )

    # C2 — rate limit distribue : en prod, REDIS_URL obligatoire.
    # Source de verite prod = Redis, pas memoire. Fallback memoire = dev/test uniquement.
    if not settings.TESTING and not (settings.REDIS_URL or "").strip():
        raise ValueError(
            "REDIS_URL doit être définie en production pour le rate limit distribue. "
            "Sans Redis, la protection anti-abus reste mono-instance. "
            "Ex: redis://localhost:6379/0"
        )


_validate_production_settings()

if settings.TESTING:
    # S4 — audit 03/03/2026 : ne jamais logger une URL contenant des credentials
    try:
        _parsed = urlparse(settings.SQLALCHEMY_DATABASE_URL)
        _safe_url = _parsed._replace(
            netloc=f"{_parsed.hostname}:{_parsed.port or 5432}"
        ).geturl()
    except Exception:
        _safe_url = "<url non parsable>"
    logger.info(f"Mode test détecté, utilisation de la base: {_safe_url}")
