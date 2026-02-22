"""
Tests pour app.core.security (decode_token, create_access_token, etc.).
"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.security import decode_token, create_access_token
from app.core.config import settings
from app.core.constants import SecurityConfig


def test_decode_token_accepts_access_token():
    """decode_token accepte un access token valide."""
    token = create_access_token({"sub": "testuser", "role": "padawan"})
    payload = decode_token(token)
    assert payload["sub"] == "testuser"
    assert payload["type"] == "access"
    assert payload.get("role") == "padawan"


def test_decode_token_rejects_refresh_token():
    """decode_token rejette un refresh token (type != access)."""
    from fastapi import HTTPException

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


def test_decode_token_rejects_token_without_type():
    """decode_token rejette un token sans claim type (legacy ou malformé)."""
    from fastapi import HTTPException

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
