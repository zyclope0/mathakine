"""
Store de rate limit distribue (C2).
Source de verite prod: Redis. Fallback memoire borne pour dev/test quand REDIS_URL vide.

Usage:
  store = get_rate_limit_store()
  allowed = store.check(key="rate_limit:login:1.2.3.4", max_requests=5, window_sec=60)
"""

import os
import time
from collections import defaultdict
from typing import Optional

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RateLimitStore:
    """Interface du store de rate limit."""

    def check(self, key: str, max_requests: int, window_sec: int) -> bool:
        """
        Verifie et incremente le compteur.
        Returns True si autorise, False si limite depassee.
        """
        raise NotImplementedError


class MemoryRateLimitStore(RateLimitStore):
    """
    Store en memoire — mono-instance.
    Fallback dev/test uniquement. Ne pas utiliser en prod multi-instance.
    """

    def __init__(self):
        self._store: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, max_requests: int, window_sec: int) -> bool:
        now = time.time()
        self._store[key] = [t for t in self._store[key] if now - t < window_sec]
        if not self._store[key]:
            del self._store[key]
        if len(self._store.get(key, [])) >= max_requests:
            return False
        self._store[key].append(now)
        return True


class RedisRateLimitStore(RateLimitStore):
    """
    Store Redis — distribue, source de verite prod.
    Fenetre fixe par intervalle (window_sec).
    """

    def __init__(self, redis_url: str):
        import redis

        self._client = redis.from_url(redis_url, decode_responses=True)
        self._lua_script = """
        local k = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local current = redis.call('INCR', k)
        if current == 1 then
            redis.call('EXPIRE', k, window + 1)
        end
        return current <= limit and 1 or 0
        """
        self._script_sha: Optional[str] = None

    def _get_redis_key(self, key: str, window_sec: int) -> str:
        """Cle Redis avec identifiant de fenetre pour fenetre fixe."""
        window_id = int(time.time() / window_sec)
        return f"rl:{key}:{window_id}"

    def check(self, key: str, max_requests: int, window_sec: int) -> bool:
        """
        Verifie et incremente le compteur Redis.
        Sur erreur Redis : fail-closed (return False) — ne pas autoriser silencieusement.
        """
        redis_key = self._get_redis_key(key, window_sec)
        try:
            result = self._client.eval(
                self._lua_script, 1, redis_key, str(window_sec), str(max_requests)
            )
            return bool(result)
        except Exception as exc:
            logger.warning(
                "Redis rate limit check failed, refusing request (fail-closed): %s",
                exc,
            )
            return False


def _is_production() -> bool:
    """Prod = NODE_ENV, ENVIRONMENT ou MATH_TRAINER_PROFILE."""
    import os

    return (
        os.getenv("NODE_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
        or os.getenv("MATH_TRAINER_PROFILE") == "prod"
    )


def get_rate_limit_store() -> RateLimitStore:
    """
    Retourne le store de rate limit actif.

    - Prod : REDIS_URL obligatoire (valide au demarrage). Redis indisponible -> raise.
    - Dev/test : REDIS_URL vide ou Redis indisponible -> MemoryRateLimitStore.

    Fallback memoire = dev/test uniquement. Jamais source de verite en prod.
    """
    redis_url = (settings.REDIS_URL or "").strip()
    if not redis_url:
        # Prod sans REDIS_URL = deja bloque par config._validate_production_settings
        logger.info("Rate limit store: Memory (dev/test, REDIS_URL vide)")
        return MemoryRateLimitStore()

    try:
        store = RedisRateLimitStore(redis_url)
        store._client.ping()
        logger.info("Rate limit store: Redis (distribue)")
        return store
    except Exception as exc:
        if _is_production() and not settings.TESTING:
            raise RuntimeError(
                f"Redis rate limit requis en production mais indisponible: {exc}. "
                "Configurer REDIS_URL et s'assurer que Redis est accessible."
            ) from exc
        logger.warning(
            "Redis rate limit unavailable (%s), using memory fallback (dev/test).",
            exc,
        )
        return MemoryRateLimitStore()


# Instance singleton — initialisee au premier acces
_rate_limit_store_instance: Optional[RateLimitStore] = None


def _get_store() -> RateLimitStore:
    """Acces au store (singleton)."""
    global _rate_limit_store_instance
    if _rate_limit_store_instance is None:
        _rate_limit_store_instance = get_rate_limit_store()
    return _rate_limit_store_instance
