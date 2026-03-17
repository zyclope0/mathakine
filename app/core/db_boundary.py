"""
Boundary runtime/data — contrat explicite (F5).

Source unique pour la formalisation du seam entre handlers async et accès DB sync.

Contrat:
    Handler (async) -> run_db_bound(sync_func, *args, **kwargs)
    sync_func s'exécute dans un threadpool.
    sync_func DOIT utiliser sync_db_session() en interne pour tout accès DB.
    sync_db_session est la SEULE source de session pour les services exécutés via run_db_bound.

Chaine active:
    Handler -> run_db_bound -> sync_func (threadpool) -> sync_db_session -> Session -> DB

Usage:
    # Depuis un handler:
    from app.core.db_boundary import run_db_bound
    result = await run_db_bound(some_sync_service_func, arg1, arg2)

    # Depuis un service sync (appelé via run_db_bound):
    from app.core.db_boundary import sync_db_session
    with sync_db_session() as db:
        ...
"""

from typing import Callable, TypeVar

from app.core.runtime import run_db_bound
from app.utils.db_utils import sync_db_session

__all__ = ["run_db_bound", "sync_db_session", "DbBoundSyncCallable"]

T = TypeVar("T")

DbBoundSyncCallable = Callable[..., T]
"""
Type alias pour les fonctions sync exécutées via run_db_bound.
Ces fonctions doivent utiliser sync_db_session() en interne pour tout accès DB.
"""
