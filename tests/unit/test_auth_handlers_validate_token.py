"""Tests cibles : mapping erreurs handlers auth (A44-S2)."""

import json
from unittest.mock import patch

import pytest
from starlette.requests import Request

from server.handlers.auth_handlers import api_refresh_token, api_validate_token


@pytest.fixture
def auth_http_scope():
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "path": "/api/auth/validate-token",
        "raw_path": b"/api/auth/validate-token",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 80),
        "scheme": "http",
    }


def _request_with_json(scope: dict, payload: dict) -> Request:
    body = json.dumps(payload).encode()

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(scope, receive)


@pytest.mark.asyncio
async def test_api_validate_token_success_logs_diagnostic_info(auth_http_scope):
    """Succes validate-token : INFO avec indices client (pas de token dans le log)."""
    scope = {
        **auth_http_scope,
        "headers": [
            (b"user-agent", b"TestValidateUA/1"),
            (b"x-mathakine-validate-caller", b"routeSession"),
        ],
    }
    request = _request_with_json(scope, {"token": "dummy.jwt.token"})

    with (
        patch("server.handlers.auth_handlers.logger") as mock_logger,
        patch(
            "server.handlers.auth_handlers.run_db_bound",
            return_value={"valid": True, "user_id": "alice"},
        ),
    ):
        response = await api_validate_token(request)

    assert response.status_code == 200
    mock_logger.info.assert_called_once()
    _fmt, ip, diag = mock_logger.info.call_args[0]
    assert ip == "127.0.0.1"
    assert "TestValidateUA" in diag
    assert "routeSession" in diag
    assert "dummy" not in diag.lower()


@pytest.mark.asyncio
async def test_api_validate_token_malformed_jwt_returns_401(auth_http_scope):
    """JWT illisible -> HTTPException decode_token -> 401."""
    request = _request_with_json(
        auth_http_scope, {"token": "not.a.valid.jwt.structure"}
    )

    response = await api_validate_token(request)

    assert response.status_code == 401
    payload = json.loads(response.body.decode())
    assert payload.get("code") == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_api_validate_token_unexpected_error_returns_500(auth_http_scope):
    """Erreur hors périmètre JWT -> 500."""
    request = _request_with_json(auth_http_scope, {"token": "x"})

    with patch(
        "server.handlers.auth_handlers.run_db_bound",
        side_effect=RuntimeError("unexpected infrastructure failure"),
    ):
        response = await api_validate_token(request)

    assert response.status_code == 500
    payload = json.loads(response.body.decode())
    assert payload.get("code") == "INTERNAL_ERROR"


@pytest.mark.asyncio
async def test_api_refresh_token_unexpected_error_returns_500(auth_http_scope):
    """Erreur inattendue côté refresh -> 500, pas faux 401."""
    request = _request_with_json(
        auth_http_scope, {"refresh_token": "dummy-refresh-token"}
    )

    with (
        patch(
            "server.handlers.auth_handlers._extract_refresh_token_from_request",
            return_value="dummy-refresh-token",
        ),
        patch(
            "server.handlers.auth_handlers.run_db_bound",
            side_effect=RuntimeError("unexpected refresh failure"),
        ),
    ):
        response = await api_refresh_token(request)

    assert response.status_code == 500
    payload = json.loads(response.body.decode())
    assert payload.get("code") == "INTERNAL_ERROR"
