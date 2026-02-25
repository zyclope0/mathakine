"""
Tests pour app.utils.rate_limit.
Vérifie _check_rate_limit, _get_client_ip, _rate_limit_response et les décorateurs.
"""
import uuid
from unittest.mock import MagicMock

import pytest

from app.utils.rate_limit import (
    MSG_CHAT_RATE_LIMIT,
    MSG_RATE_LIMIT_RETRY,
    _check_rate_limit,
    _get_client_ip,
    _rate_limit_response,
    rate_limit_auth,
    rate_limit_register,
)


@pytest.fixture(autouse=True)
def ensure_testing_bypass(monkeypatch):
    """Par défaut, garder TESTING=true pour ne pas bloquer les autres tests."""
    monkeypatch.setenv("TESTING", "true")


def test_rate_limit_response_returns_429():
    """_rate_limit_response retourne une réponse 429 avec le message."""
    resp = _rate_limit_response("Message custom")
    assert resp.status_code == 429
    import json
    body = json.loads(resp.body)
    assert body["error"] == "Message custom"


def test_rate_limit_response_uses_constants():
    """Les constantes MSG_* sont utilisables avec _rate_limit_response."""
    resp = _rate_limit_response(MSG_RATE_LIMIT_RETRY)
    assert resp.status_code == 429
    import json
    assert json.loads(resp.body)["error"] == MSG_RATE_LIMIT_RETRY

    resp2 = _rate_limit_response(MSG_CHAT_RATE_LIMIT)
    assert json.loads(resp2.body)["error"] == MSG_CHAT_RATE_LIMIT


def test_get_client_ip_from_request_client():
    """_get_client_ip utilise request.client.host quand pas de X-Forwarded-For."""
    request = MagicMock()
    request.headers = {}
    request.client = MagicMock()
    request.client.host = "192.168.1.1"
    assert _get_client_ip(request) == "192.168.1.1"


def test_get_client_ip_from_x_forwarded_for():
    """_get_client_ip utilise la première IP de X-Forwarded-For (proxy)."""
    request = MagicMock()
    request.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2, 10.0.0.3"}
    assert _get_client_ip(request) == "10.0.0.1"


def test_get_client_ip_x_forwarded_for_strips_spaces():
    """_get_client_ip strip les espaces de X-Forwarded-For."""
    request = MagicMock()
    request.headers = {"X-Forwarded-For": "  10.0.0.1  , 10.0.0.2"}
    assert _get_client_ip(request) == "10.0.0.1"


def test_get_client_ip_fallback_unknown():
    """_get_client_ip retourne 'unknown' si pas de client."""
    request = MagicMock()
    request.headers = {}
    request.client = None
    assert _get_client_ip(request) == "unknown"


def test_check_rate_limit_bypassed_when_testing_true(monkeypatch):
    """Quand TESTING=true, _check_rate_limit autorise toujours."""
    monkeypatch.setenv("TESTING", "true")
    key = f"test_bypass_{uuid.uuid4()}"
    for _ in range(100):
        assert _check_rate_limit(key, max_requests=1) is True


def test_check_rate_limit_enforces_limit_when_testing_false(monkeypatch):
    """Quand TESTING=false, _check_rate_limit applique la limite."""
    monkeypatch.setenv("TESTING", "false")
    key = f"test_limit_{uuid.uuid4()}"
    max_req = 2
    assert _check_rate_limit(key, max_req) is True
    assert _check_rate_limit(key, max_req) is True
    assert _check_rate_limit(key, max_req) is False


@pytest.mark.asyncio
async def test_rate_limit_auth_decorator_allows_when_testing():
    """rate_limit_auth laisse passer quand TESTING=true (comportement tests)."""
    @rate_limit_auth("login")
    async def handler(request):
        return {"ok": True}

    request = MagicMock()
    request.headers = {}
    request.client = MagicMock(host="127.0.0.1")
    result = await handler(request)
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_rate_limit_register_decorator_allows_when_testing():
    """rate_limit_register laisse passer quand TESTING=true."""
    @rate_limit_register
    async def handler(request):
        return {"ok": True}

    request = MagicMock()
    request.headers = {}
    request.client = MagicMock(host="127.0.0.1")
    result = await handler(request)
    assert result == {"ok": True}
