"""Tests unitaires pour app.utils.readiness_probe (OPS-HEALTH-02)."""

from unittest.mock import patch

import pytest

from app.utils import readiness_probe


@pytest.mark.asyncio
async def test_run_readiness_checks_db_failure_marks_unavailable():
    with patch.object(
        readiness_probe,
        "_ping_postgres_sync",
        side_effect=RuntimeError("simulated"),
    ):
        ok, checks = await readiness_probe.run_readiness_checks()
    assert ok is False
    assert checks.get("db") == "unavailable"


@pytest.mark.asyncio
async def test_run_readiness_checks_db_ok_skips_redis_when_not_required():
    with (
        patch.object(readiness_probe, "_ping_postgres_sync"),
        patch.object(
            readiness_probe, "readiness_should_check_redis", return_value=False
        ),
    ):
        ok, checks = await readiness_probe.run_readiness_checks()
    assert ok is True
    assert checks.get("db") == "ok"
    assert "redis" not in checks


@pytest.mark.asyncio
async def test_run_readiness_checks_redis_failure_when_required():
    with (
        patch.object(readiness_probe, "_ping_postgres_sync"),
        patch.object(
            readiness_probe, "readiness_should_check_redis", return_value=True
        ),
        patch.object(
            readiness_probe, "_ping_redis_sync", side_effect=OSError("simulated")
        ),
    ):
        ok, checks = await readiness_probe.run_readiness_checks()
    assert ok is False
    assert checks.get("db") == "ok"
    assert checks.get("redis") == "unavailable"


@pytest.mark.asyncio
async def test_run_readiness_checks_redis_ok_when_required():
    with (
        patch.object(readiness_probe, "_ping_postgres_sync"),
        patch.object(
            readiness_probe, "readiness_should_check_redis", return_value=True
        ),
        patch.object(readiness_probe, "_ping_redis_sync"),
    ):
        ok, checks = await readiness_probe.run_readiness_checks()
    assert ok is True
    assert checks.get("db") == "ok"
    assert checks.get("redis") == "ok"
