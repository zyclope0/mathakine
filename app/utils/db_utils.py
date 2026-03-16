"""
Utilitaires DB pour les handlers (DRY).
Context manager sync pour session + commit/rollback/close.

Vérité runtime: sync_db_session est la source unique pour les services exécutés
via run_db_bound(). Aucun context manager async legacy.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.db.base import SessionLocal


@contextmanager
def sync_db_session() -> Generator[Session, None, None]:
    """
    Context manager sync pour une session DB.
    Utilisé par les services sync (LOT A1) exécutés via run_db_bound().

    Usage:
        with sync_db_session() as db:
            result = some_sync_use_case(db, ...)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
