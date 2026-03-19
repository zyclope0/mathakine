"""
Stockage serveur de l'état « pending » du diagnostic (référence opaque).

Responsabilité : persistance temporaire des métadonnées de question (dont
correct_answer) entre deux appels HTTP, sans embarquer la bonne réponse dans
le token client. Redis en production si configuré, sinon dictionnaire mémoire
avec TTL (dev/tests).

Extrait de diagnostic_service (lot I7) pour réduire la densité du service principal.
"""

import json
import secrets
import time
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

_PENDING_STATE_TTL_SEC = 60 * 60
_pending_state_memory: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_pending_state_redis_client = None


def _is_production() -> bool:
    return (
        settings.ENVIRONMENT == "production"
        or settings.NODE_ENV == "production"
        or settings.MATH_TRAINER_PROFILE == "prod"
    )


def _get_pending_state_redis_client():
    global _pending_state_redis_client

    if _pending_state_redis_client is not None:
        return _pending_state_redis_client

    redis_url = (settings.REDIS_URL or "").strip()
    if not redis_url:
        return None

    try:
        import redis

        _pending_state_redis_client = redis.from_url(redis_url, decode_responses=True)
        return _pending_state_redis_client
    except Exception as exc:
        if _is_production() and not settings.TESTING:
            raise RuntimeError(
                f"Redis requis pour le pending diagnostic en production: {exc}"
            ) from exc
        logger.warning(
            "Pending diagnostic Redis indisponible (%s), fallback memoire dev/test",
            exc,
        )
        return None


def _cleanup_pending_state_memory(now: Optional[float] = None) -> None:
    current = now or time.time()
    expired_refs = [
        pending_ref
        for pending_ref, (expires_at, _) in _pending_state_memory.items()
        if expires_at <= current
    ]
    for pending_ref in expired_refs:
        _pending_state_memory.pop(pending_ref, None)


def store_pending_state(pending: Dict[str, Any]) -> str:
    """
    Stocke l'état pending côté serveur et retourne une référence opaque.
    correct_answer n'est jamais embarqué dans le token client.
    """
    pending_ref = secrets.token_urlsafe(24)
    redis_client = _get_pending_state_redis_client()
    if redis_client is not None:
        redis_client.setex(
            f"diagnostic:pending:{pending_ref}",
            _PENDING_STATE_TTL_SEC,
            json.dumps(pending),
        )
        return pending_ref

    expires_at = time.time() + _PENDING_STATE_TTL_SEC
    _cleanup_pending_state_memory(expires_at)
    _pending_state_memory[pending_ref] = (expires_at, pending)
    return pending_ref


def load_pending_state(pending_ref: str) -> Optional[Dict[str, Any]]:
    """Charge l'état pending stocké côté serveur."""
    redis_client = _get_pending_state_redis_client()
    if redis_client is not None:
        raw = redis_client.get(f"diagnostic:pending:{pending_ref}")
        return json.loads(raw) if raw else None

    _cleanup_pending_state_memory()
    entry = _pending_state_memory.get(pending_ref)
    if entry is None:
        return None
    expires_at, pending = entry
    if expires_at <= time.time():
        _pending_state_memory.pop(pending_ref, None)
        return None
    return pending


def delete_pending_state(pending_ref: str) -> None:
    """Supprime l'état pending une fois la question consommée."""
    redis_client = _get_pending_state_redis_client()
    if redis_client is not None:
        redis_client.delete(f"diagnostic:pending:{pending_ref}")
        return
    _pending_state_memory.pop(pending_ref, None)


def get_pending_state(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Résout la référence opaque pending_ref vers le pending stocké côté serveur."""
    pending_ref = state.get("pending_ref")
    if not pending_ref or not isinstance(pending_ref, str):
        return None
    return load_pending_state(pending_ref)
