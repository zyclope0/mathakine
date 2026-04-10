"""SEC-HARDEN-01 : HSTS (prod seulement) + Permissions-Policy sur SecureHeadersMiddleware."""

from unittest.mock import patch

import pytest
from starlette.requests import Request
from starlette.responses import Response

from server.middleware import (
    HSTS_VALUE,
    PERMISSIONS_POLICY_VALUE,
    SECURE_HEADERS_DICT,
    SecureHeadersMiddleware,
)


async def _dummy_asgi_app(scope, receive, send):
    pass


@pytest.fixture
def mock_request() -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/live",
        "headers": [],
        "query_string": b"",
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_secure_headers_stable_and_permissions_policy(
    mock_request: Request,
) -> None:
    mw = SecureHeadersMiddleware(_dummy_asgi_app)

    async def call_next(_req: Request) -> Response:
        return Response("ok")

    with patch("server.middleware.settings") as mock_settings:
        mock_settings.SECURE_HEADERS = True
        with patch("server.middleware._is_production", return_value=False):
            response = await mw.dispatch(mock_request, call_next)

    for key, value in SECURE_HEADERS_DICT.items():
        assert response.headers[key] == value
    assert response.headers["Permissions-Policy"] == PERMISSIONS_POLICY_VALUE
    assert "Strict-Transport-Security" not in response.headers


@pytest.mark.asyncio
async def test_hsts_only_when_production(mock_request: Request) -> None:
    mw = SecureHeadersMiddleware(_dummy_asgi_app)

    async def call_next(_req: Request) -> Response:
        return Response("ok")

    with patch("server.middleware.settings") as mock_settings:
        mock_settings.SECURE_HEADERS = True
        with patch("server.middleware._is_production", return_value=True):
            response = await mw.dispatch(mock_request, call_next)

    assert response.headers["Strict-Transport-Security"] == HSTS_VALUE
    assert response.headers["Permissions-Policy"] == PERMISSIONS_POLICY_VALUE


@pytest.mark.asyncio
async def test_no_security_headers_when_disabled(mock_request: Request) -> None:
    mw = SecureHeadersMiddleware(_dummy_asgi_app)

    async def call_next(_req: Request) -> Response:
        return Response("ok")

    with patch("server.middleware.settings") as mock_settings:
        mock_settings.SECURE_HEADERS = False
        with patch("server.middleware._is_production", return_value=True):
            response = await mw.dispatch(mock_request, call_next)

    for key in SECURE_HEADERS_DICT:
        assert key not in response.headers
    assert "Permissions-Policy" not in response.headers
    assert "Strict-Transport-Security" not in response.headers
