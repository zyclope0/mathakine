"""
Utilitaires DB pour les handlers (DRY).
Context manager pour session + commit/rollback/close.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.services.enhanced_server_adapter import EnhancedServerAdapter

logger = get_logger(__name__)


@asynccontextmanager
async def db_session() -> AsyncGenerator[Session, None]:
    """
    Context manager async pour une session DB.
    Gère rollback en cas d'exception et close systématique.

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
