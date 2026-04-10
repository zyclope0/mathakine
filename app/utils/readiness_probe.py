"""
Sondes readiness bornées dans le temps (OPS-HEALTH-02).

Réponses JSON minimales ; aucun secret ni stack trace exposés au client.
"""

from __future__ import annotations

import asyncio
import os
from typing import Dict

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Plafond global par étape (évite une probe qui pendule indéfiniment).
PROBE_TIMEOUT_SEC = 2.0

# Timeouts réseau serrés côté clients sync (Redis) — restent sous PROBE_TIMEOUT_SEC.
_REDIS_SOCKET_TIMEOUT_SEC = 1.5


def _is_production_env() -> bool:
    return (
        os.environ.get("ENVIRONMENT") == "production"
        or os.environ.get("NODE_ENV") == "production"
        or os.environ.get("MATH_TRAINER_PROFILE") == "prod"
    )


def readiness_should_check_redis() -> bool:
    """
    Redis est exigé pour la readiness uniquement en profil prod avec REDIS_URL
    renseignée (aligné sur le contrat rate-limit distribué).
    """
    if settings.TESTING:
        return False
    if not (settings.REDIS_URL or "").strip():
        return False
    return _is_production_env()


def _ping_postgres_sync() -> None:
    from sqlalchemy import text

    from app.db.base import engine

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def _ping_redis_sync(url: str) -> None:
    import redis

    client = redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=_REDIS_SOCKET_TIMEOUT_SEC,
        socket_timeout=_REDIS_SOCKET_TIMEOUT_SEC,
    )
    try:
        client.ping()
    finally:
        client.close()


async def run_readiness_checks() -> tuple[bool, Dict[str, str]]:
    """
    Exécute les vérifications critiques avec timeout.

    Returns:
        (True, checks) si prêt ; (False, checks) avec au moins une clé en
        ``unavailable`` sinon.
    """
    checks: Dict[str, str] = {}

    try:
        await asyncio.wait_for(
            asyncio.to_thread(_ping_postgres_sync),
            timeout=PROBE_TIMEOUT_SEC,
        )
        checks["db"] = "ok"
    except Exception as exc:
        logger.warning(
            "Readiness: PostgreSQL check failed: %s",
            type(exc).__name__,
        )
        checks["db"] = "unavailable"
        return False, checks

    if readiness_should_check_redis():
        url = (settings.REDIS_URL or "").strip()
        try:
            await asyncio.wait_for(
                asyncio.to_thread(_ping_redis_sync, url),
                timeout=PROBE_TIMEOUT_SEC,
            )
            checks["redis"] = "ok"
        except Exception as exc:
            logger.warning(
                "Readiness: Redis check failed: %s",
                type(exc).__name__,
            )
            checks["redis"] = "unavailable"
            return False, checks

    return True, checks
