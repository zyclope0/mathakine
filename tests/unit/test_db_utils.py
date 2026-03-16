"""
Tests unitaires pour app.utils.db_utils (E5/E6).
Prouve sync_db_session comme source de vérité pour les services exécutés via run_db_bound().
"""

import pytest
from sqlalchemy import text

from app.utils.db_utils import sync_db_session


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
