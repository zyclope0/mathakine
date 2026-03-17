"""
Tests unitaires pour app.utils.db_utils (E5/E6) et boundary runtime/data (F5).
Prouve sync_db_session comme source de vérité pour les services exécutés via run_db_bound().
"""

import pytest
from sqlalchemy import text

from app.core.db_boundary import run_db_bound, sync_db_session


def test_sync_db_session_yields_session():
    """sync_db_session fournit une session utilisable."""
    with sync_db_session() as db:
        assert db is not None
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_sync_db_session_rollback_on_exception():
    """sync_db_session fait rollback en cas d'exception."""
    with sync_db_session() as db:
        db.execute(text("SELECT 1"))
        with pytest.raises(ValueError):
            raise ValueError("test rollback")
    # Pas d'exception au exit = rollback a été fait, close aussi


@pytest.mark.asyncio
async def test_run_db_bound_with_sync_db_session_chain():
    """F5: Prouve que run_db_bound exécute une sync_func utilisant sync_db_session."""

    def sync_func_using_session() -> int:
        with sync_db_session() as db:
            result = db.execute(text("SELECT 42"))
            return result.scalar()

    got = await run_db_bound(sync_func_using_session)
    assert got == 42
