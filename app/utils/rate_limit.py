"""
Rate limiting pour les endpoints sensibles (audit 3.4).
Protège contre bruteforce (login, forgot-password) et énumération.
"""
import os
import time
from collections import defaultdict
from functools import wraps
from typing import Callable

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Fenêtre glissante : {key: [timestamps]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT_WINDOW_SEC = 60
RATE_LIMIT_AUTH_MAX = 5  # login, forgot-password, validate-token
RATE_LIMIT_REGISTER_MAX = 3  # création de compte
RATE_LIMIT_RESEND_VERIFICATION_MAX = 2  # resend-verification (abus email)
RATE_LIMIT_CHAT_MAX = 15  # chat/stream — coût OpenAI, éviter abus


def _get_client_ip(request) -> str:
    """Récupère l'IP cliente (X-Forwarded-For si derrière proxy)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return getattr(request.client, "host", "unknown") or "unknown"


def _check_rate_limit(
    key: str,
    max_requests: int,
    window_sec: int = RATE_LIMIT_WINDOW_SEC,
) -> bool:
    """
    Vérifie si la requête dépasse la limite.
    Returns True si autorisé, False si limité.
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return True
    now = time.time()
    # Nettoyer les entrées expirées
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < window_sec]
    if len(_rate_limit_store[key]) >= max_requests:
        return False
    _rate_limit_store[key].append(now)
    return True


def rate_limit_auth(endpoint_name: str):
    """Décorateur rate limit pour login/forgot-password (5 req/min)."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapped(request, *args, **kwargs):
            ip = _get_client_ip(request)
            key = f"rate_limit:{endpoint_name}:{ip}"
            if not _check_rate_limit(key, RATE_LIMIT_AUTH_MAX):
                logger.warning(f"Rate limit dépassé pour {endpoint_name} depuis {ip}")
                from starlette.responses import JSONResponse
                return JSONResponse(
                    {"error": "Trop de tentatives. Veuillez réessayer dans une minute."},
                    status_code=429,
                )
            return await func(request, *args, **kwargs)

        return wrapped

    return decorator


def rate_limit_register(func: Callable):
    """Décorateur rate limit pour création de compte (3 req/min)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:register:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_REGISTER_MAX):
            logger.warning(f"Rate limit dépassé pour register depuis {ip}")
            from starlette.responses import JSONResponse
            return JSONResponse(
                {"error": "Trop de tentatives. Veuillez réessayer dans une minute."},
                status_code=429,
            )
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_resend_verification(func: Callable):
    """Décorateur rate limit pour resend-verification (2 req/min par IP)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:resend_verification:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_RESEND_VERIFICATION_MAX):
            logger.warning(f"Rate limit dépassé pour resend-verification depuis {ip}")
            from starlette.responses import JSONResponse
            return JSONResponse(
                {"error": "Trop de tentatives. Veuillez réessayer dans une minute."},
                status_code=429,
            )
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_chat(func: Callable):
    """Décorateur rate limit pour chat/stream (15 req/min par IP — coût OpenAI)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:chat:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_CHAT_MAX):
            logger.warning(f"Rate limit dépassé pour chat depuis {ip}")
            from starlette.responses import JSONResponse
            return JSONResponse(
                {"error": "Limite de messages atteinte. Veuillez réessayer dans une minute."},
                status_code=429,
            )
        return await func(request, *args, **kwargs)

    return wrapped
