"""
CHAT-DEFENSE-01 : défense en profondeur sur les handlers chat (décorateurs locaux).

Ces tests appellent les handlers enveloppés en court-circuitant le middleware HTTP,
pour vérifier le comportement des décorateurs ``require_auth`` / ``require_auth_sse``.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request

from server.handlers import chat_handlers


@pytest.mark.asyncio
async def test_chat_api_handler_returns_401_when_get_current_user_empty():
    """Couche handler : sans utilisateur → JSON 401 (sans dépendre du middleware)."""
    request = MagicMock(spec=Request)
    with patch("server.auth.get_current_user", new=AsyncMock(return_value=None)):
        response = await chat_handlers.chat_api(request)
    assert response.status_code == 401
    data = json.loads(response.body.decode("utf-8"))
    assert data.get("code") == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_chat_api_stream_handler_returns_sse_error_when_get_current_user_empty():
    """Couche handler : sans utilisateur → flux SSE d'erreur (require_auth_sse)."""
    request = MagicMock(spec=Request)
    with patch("server.auth.get_current_user", new=AsyncMock(return_value=None)):
        response = await chat_handlers.chat_api_stream(request)
    assert response.status_code == 200
    chunks: list[bytes] = []
    async for chunk in response.body_iterator:
        chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode("utf-8"))
    payload = b"".join(chunks).decode("utf-8")
    assert "Authentification requise" in payload
    assert '"type"' in payload and "error" in payload
