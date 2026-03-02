"""
Cache TTL simple en mémoire pour endpoints badges/stats et badges/rarity.
Sans dépendance externe, aligné avec rate_limiter (stockage mémoire mono-instance).

Note Python 3.10+ : asyncio.Lock() peut être instancié au niveau module sans
nécessiter une event loop active — le binding à la loop se fait au premier await.
"""

import asyncio
import time
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")

# Stockage: {clé: (valeur, timestamp)}
_cache: dict[str, tuple[Any, float]] = {}

# Lock module-level — safe en Python 3.10+ (pas besoin de lazy init).
# Élimine le TOCTOU de l'ancienne initialisation lazy _get_lock() (M6 audit).
_lock = asyncio.Lock()


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
    async with _lock:
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
