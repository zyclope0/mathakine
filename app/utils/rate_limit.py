"""
Rate limiting pour les endpoints sensibles (audit 3.4).
Protege contre bruteforce (login, forgot-password) et enumeration.

C2: Store distribue Redis en prod. Fallback memoire borne pour dev/test (REDIS_URL vide).
"""

import os
from functools import wraps
from typing import Callable, Optional

from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.utils.rate_limit_store import _get_store

logger = get_logger(__name__)

RATE_LIMIT_WINDOW_SEC = 60
RATE_LIMIT_AUTH_MAX = 5  # login, forgot-password, validate-token
RATE_LIMIT_REGISTER_MAX = 3  # creation de compte
RATE_LIMIT_RESEND_VERIFICATION_MAX = 2  # resend-verification (abus email)
RATE_LIMIT_CHAT_MAX = 15  # chat/stream - cout OpenAI, eviter abus
RATE_LIMIT_AI_MAX_PER_HOUR = 10
RATE_LIMIT_AI_MAX_PER_DAY = 50

# Generation IA exercices (OpenAI) — cles Redis distinctes des defis ; quotas separes.
RATE_LIMIT_EXERCISE_AI_MAX_PER_HOUR = 10
RATE_LIMIT_EXERCISE_AI_MAX_PER_DAY = 50

# Messages d'erreur centralises (429 Too Many Requests)
MSG_RATE_LIMIT_RETRY = "Trop de tentatives. Veuillez reessayer dans une minute."
MSG_CHAT_RATE_LIMIT = "Limite de messages atteinte. Veuillez reessayer dans une minute."
MSG_AI_HOURLY_RATE_LIMIT = "Limite horaire de generation atteinte."
MSG_AI_DAILY_RATE_LIMIT = "Limite journaliere de generation atteinte."
MSG_EXERCISE_AI_HOURLY_RATE_LIMIT = (
    "Limite horaire de generation d'exercices IA atteinte. Reessayez plus tard."
)
MSG_EXERCISE_AI_DAILY_RATE_LIMIT = (
    "Limite journaliere de generation d'exercices IA atteinte. Reessayez demain."
)


def _get_client_ip(request) -> str:
    """Recupere l'IP cliente (X-Forwarded-For si derriere proxy)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return getattr(request.client, "host", "unknown") or "unknown"


def _rate_limit_response(message: str) -> JSONResponse:
    """Retourne une reponse 429 Too Many Requests."""
    from app.utils.error_handler import api_error_response

    return api_error_response(429, message)


def _check_rate_limit(
    key: str,
    max_requests: int,
    window_sec: int = RATE_LIMIT_WINDOW_SEC,
) -> bool:
    """
    Verifie si la requete depasse la limite.
    Returns True si autorise, False si limite.
    Store: Redis en prod (REDIS_URL), memoire en dev/test.
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return True
    return _get_store().check(key=key, max_requests=max_requests, window_sec=window_sec)


def check_ai_generation_rate_limit(user_id: int) -> tuple[bool, Optional[str]]:
    """
    Verifie les limites de generation IA par utilisateur sur 1h et 24h.
    Source de verite: store distribue Redis en prod, fallback memoire en dev/test.
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return True, None

    store = _get_store()
    hourly_key = f"rate_limit:ai_generation:hour:{user_id}"
    daily_key = f"rate_limit:ai_generation:day:{user_id}"

    if not store.check(hourly_key, RATE_LIMIT_AI_MAX_PER_HOUR, 3600):
        return False, MSG_AI_HOURLY_RATE_LIMIT
    if not store.check(daily_key, RATE_LIMIT_AI_MAX_PER_DAY, 86400):
        return False, MSG_AI_DAILY_RATE_LIMIT
    return True, None


def check_exercise_ai_generation_rate_limit(user_id: int) -> tuple[bool, Optional[str]]:
    """
    Limites dediees au flux exercices IA (OpenAI), independantes du compteur defis.

    Meme principe que check_ai_generation_rate_limit : refus explicite, pas de contournement.
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return True, None

    store = _get_store()
    hourly_key = f"rate_limit:exercise_ai_generation:hour:{user_id}"
    daily_key = f"rate_limit:exercise_ai_generation:day:{user_id}"

    if not store.check(hourly_key, RATE_LIMIT_EXERCISE_AI_MAX_PER_HOUR, 3600):
        return False, MSG_EXERCISE_AI_HOURLY_RATE_LIMIT
    if not store.check(daily_key, RATE_LIMIT_EXERCISE_AI_MAX_PER_DAY, 86400):
        return False, MSG_EXERCISE_AI_DAILY_RATE_LIMIT
    return True, None


def rate_limit_auth(endpoint_name: str):
    """Decorateur rate limit pour login/forgot-password (5 req/min)."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapped(request, *args, **kwargs):
            ip = _get_client_ip(request)
            key = f"rate_limit:{endpoint_name}:{ip}"
            if not _check_rate_limit(key, RATE_LIMIT_AUTH_MAX):
                logger.warning(f"Rate limit depasse pour {endpoint_name} depuis {ip}")
                return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
            return await func(request, *args, **kwargs)

        return wrapped

    return decorator


def rate_limit_register(func: Callable):
    """Decorateur rate limit pour creation de compte (3 req/min)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:register:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_REGISTER_MAX):
            logger.warning(f"Rate limit depasse pour register depuis {ip}")
            return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_resend_verification(func: Callable):
    """Decorateur rate limit pour resend-verification (2 req/min par IP)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:resend_verification:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_RESEND_VERIFICATION_MAX):
            logger.warning(f"Rate limit depasse pour resend-verification depuis {ip}")
            return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_chat(func: Callable):
    """Decorateur rate limit pour chat/stream (15 req/min par IP - cout OpenAI)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:chat:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_CHAT_MAX):
            logger.warning(f"Rate limit depasse pour chat depuis {ip}")
            return _rate_limit_response(MSG_CHAT_RATE_LIMIT)
        return await func(request, *args, **kwargs)

    return wrapped
