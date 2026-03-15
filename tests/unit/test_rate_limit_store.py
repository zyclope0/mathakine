"""
Tests pour app.utils.rate_limit_store.
Verifie MemoryRateLimitStore, RedisRateLimitStore (fail-closed), get_rate_limit_store.
"""

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from app.utils.rate_limit_store import (
    MemoryRateLimitStore,
    RedisRateLimitStore,
    get_rate_limit_store,
)


def test_memory_store_enforces_limit():
    """MemoryRateLimitStore applique la limite correctement."""
    store = MemoryRateLimitStore()
    key = f"test_{uuid.uuid4()}"
    assert store.check(key, max_requests=2, window_sec=60) is True
    assert store.check(key, max_requests=2, window_sec=60) is True
    assert store.check(key, max_requests=2, window_sec=60) is False


def test_memory_store_resets_after_window():
    """MemoryRateLimitStore expire les timestamps hors fenetre."""
    import time

    store = MemoryRateLimitStore()
    key = f"test_{uuid.uuid4()}"
    assert store.check(key, max_requests=1, window_sec=1) is True
    assert store.check(key, max_requests=1, window_sec=1) is False
    time.sleep(1.1)
    assert store.check(key, max_requests=1, window_sec=1) is True


def test_get_rate_limit_store_returns_memory_when_redis_url_empty(monkeypatch):
    """Sans REDIS_URL, get_rate_limit_store retourne MemoryRateLimitStore (dev/test)."""
    monkeypatch.setattr("app.utils.rate_limit_store.settings.REDIS_URL", "")
    import app.utils.rate_limit_store as mod

    mod._rate_limit_store_instance = None
    store = get_rate_limit_store()
    assert isinstance(store, MemoryRateLimitStore)


def test_redis_store_fail_closed_on_error():
    """RedisRateLimitStore.check() retourne False (refus) sur erreur Redis."""
    store = RedisRateLimitStore("redis://localhost:6379/0")
    from unittest.mock import patch

    with patch.object(store._client, "eval", side_effect=ConnectionError("Redis down")):
        result = store.check("test:key", max_requests=5, window_sec=60)
    assert result is False


def test_config_prod_requires_redis_url():
    """Prod sans REDIS_URL -> ValueError au demarrage (subprocess isole)."""
    root = Path(__file__).resolve().parent.parent.parent
    env = {
        **os.environ,
        "TESTING": "false",
        "ENVIRONMENT": "production",
        "REDIS_URL": "",
        "SECRET_KEY": "test-secret-key-for-config-validation-test",
        "DEFAULT_ADMIN_PASSWORD": "StrongPwd123!",
        "DATABASE_URL": os.environ.get("DATABASE_URL", "postgresql://u:p@localhost/db"),
    }
    result = subprocess.run(
        [sys.executable, "-c", "from app.core.config import settings"],
        capture_output=True,
        text=True,
        cwd=str(root),
        env=env,
        timeout=10,
    )
    assert result.returncode != 0
    assert "REDIS_URL" in (result.stderr or result.stdout or "")
