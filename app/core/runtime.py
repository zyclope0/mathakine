"""
Helper unique pour executer du code sync (DB, use cases) hors de l'event loop.

Modele d'execution LOT A1:
- Handlers Starlette restent async
- DB et use cases restent sync
- Les appels DB/metier sync passent par run_db_bound() (threadpool)

Usage:
    result = await run_db_bound(some_sync_func, arg1, arg2, kw=val)
"""

import asyncio
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def run_db_bound(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Execute une fonction sync dans un threadpool pour ne pas bloquer l'event loop.

    Args:
        func: Fonction sync a executer (ex: perform_login, perform_refresh)
        *args: Arguments positionnels
        **kwargs: Arguments nommes

    Returns:
        Le resultat de func(*args, **kwargs)
    """
    return await asyncio.to_thread(func, *args, **kwargs)
