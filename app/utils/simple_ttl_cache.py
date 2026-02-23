"""
Cache TTL simple en mémoire pour endpoints badges/stats et badges/rarity.
Sans dépendance externe, aligné avec rate_limiter (stockage mémoire mono-instance).
"""

import asyncio
import time
from typing import Any, Awaitable, Callable, Optional, TypeVar

T = TypeVar("T")

# Stockage: {clé: (valeur, timestamp)}
_cache: dict[str, tuple[Any, float]] = {}
_lock: Optional[asyncio.Lock] = None


def _get_lock() -> asyncio.Lock:
    """Initialisation lazy du lock (éviter création avant loop)."""
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock


async def get_or_set(
    key: str, ttl_sec: float, factory: Callable[[], Awaitable[Any]]
) -> Any:
    """
    Retourne la valeur en cache si valide, sinon exécute factory() et met en cache.

    Args:
        key: Clé de cache
        ttl_sec: Durée de validité en secondes
        factory: Coroutine appelée si cache miss (pas d'argument)

    Returns:
        Valeur (depuis cache ou factory)
    """
    now = time.monotonic()
    async with _get_lock():
        entry = _cache.get(key)
        if entry is not None:
            val, stored_at = entry
            if (now - stored_at) < ttl_sec:
                return val
        # Cache miss ou expiré
        val = await factory()
        _cache[key] = (val, now)
        return val


def clear_all() -> None:
    """Vide le cache (utile pour les tests)."""
    global _cache
    _cache = {}
