"""
Utilitaires DB pour les handlers (DRY).
Context manager pour session + commit/rollback/close.
"""

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.base import SessionLocal
from app.services.enhanced_server_adapter import EnhancedServerAdapter

logger = get_logger(__name__)


@contextmanager
def sync_db_session() -> Generator[Session, None, None]:
    """
    Context manager sync pour une session DB.
    Utilise par les services sync (LOT A1) executes via run_db_bound().

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


@asynccontextmanager
async def db_session() -> AsyncGenerator[Session, None]:
    """
    Context manager async pour une session DB.
    Gere rollback en cas d'exception et close systematique.

    Usage:
        async with db_session() as db:
            user = db.query(User).filter(...).first()
            db.commit()
            return JSONResponse(...)
    """
    db = EnhancedServerAdapter.get_db_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        EnhancedServerAdapter.close_db_session(db)
