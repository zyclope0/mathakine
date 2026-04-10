"""SEC-HARDEN-01 : politique diagnose sur le sink exceptions (pas de dump locals en prod)."""

import pytest

from app.core.logging_config import _is_production_like_env


def _clear_prod_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NODE_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("MATH_TRAINER_PROFILE", raising=False)


@pytest.mark.parametrize(
    "env_name, env_value, expect_production_like",
    [
        ("ENVIRONMENT", "production", True),
        ("NODE_ENV", "production", True),
        ("MATH_TRAINER_PROFILE", "prod", True),
        ("ENVIRONMENT", "development", False),
        ("ENVIRONMENT", "test", False),
    ],
)
def test_is_production_like_env_matches_flags(
    env_name: str,
    env_value: str,
    expect_production_like: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_prod_env(monkeypatch)
    monkeypatch.setenv(env_name, env_value)
    assert _is_production_like_env() is expect_production_like
