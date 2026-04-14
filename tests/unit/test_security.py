"""
Tests pour app.core.security (decode_token, create_access_token, etc.).
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from jose import jwt

from app.core.config import settings
from app.core.constants import SecurityConfig
from app.core.security import (
    create_access_token,
    decode_token,
    get_cookie_config,
    validate_password_strength,
)


def test_decode_token_accepts_access_token():
    """decode_token accepte un access token valide."""
    token = create_access_token({"sub": "testuser", "role": "padawan"})
    payload = decode_token(token)
    assert payload["sub"] == "testuser"
    assert payload["type"] == "access"
    assert payload.get("role") == "padawan"


def test_decode_token_rejects_refresh_token():
    """decode_token rejette un refresh token (type != access)."""
    from starlette.exceptions import HTTPException

    refresh_token = jwt.encode(
        {
            "sub": "testuser",
            "role": "padawan",
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        },
        settings.SECRET_KEY,
        algorithm=SecurityConfig.ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_token(refresh_token)
    assert exc_info.value.status_code == 401


def test_get_cookie_config_uses_production_flag_true():
    """AUTH-HARDEN-02 : alignement sur _is_production() — prod => none + Secure."""
    with patch("app.core.security._is_production", return_value=True):
        assert get_cookie_config() == ("none", True)


def test_get_cookie_config_uses_production_flag_false():
    """AUTH-HARDEN-02 : hors prod => lax, pas Secure."""
    with patch("app.core.security._is_production", return_value=False):
        assert get_cookie_config() == ("lax", False)


def test_validate_password_strength_rejects_without_special_char():
    """
    SEC-PASS-01 : au moins un caractère non alphanumérique requis.
    """
    err = validate_password_strength("NoSpecial1")
    assert isinstance(err, str)
    assert "spécial" in err


def test_validate_password_strength_accepts_with_special_char():
    # "Valid1!" has 7 chars; min length is 8 (e.g. Valid12!).
    assert validate_password_strength("Valid12!") is None


def test_decode_token_rejects_token_without_type():
    """decode_token rejette un token sans claim type (legacy ou malformé)."""
    from starlette.exceptions import HTTPException

    token = jwt.encode(
        {
            "sub": "testuser",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.SECRET_KEY,
        algorithm=SecurityConfig.ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401
