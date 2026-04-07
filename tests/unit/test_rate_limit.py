"""
Tests pour app.utils.rate_limit.
Vérifie _check_rate_limit, _get_client_ip, _rate_limit_response et les décorateurs.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.utils.rate_limit import (
    MSG_AI_DAILY_RATE_LIMIT,
    MSG_AI_HOURLY_RATE_LIMIT,
    MSG_CHAT_RATE_LIMIT,
    MSG_EXERCISE_AI_DAILY_RATE_LIMIT,
    MSG_EXERCISE_AI_HOURLY_RATE_LIMIT,
    MSG_RATE_LIMIT_RETRY,
    VALIDATE_TOKEN_CALLER_HEADER,
    _check_rate_limit,
    _get_client_ip,
    _rate_limit_response,
    auth_request_rate_limit_diagnostics,
    check_ai_generation_rate_limit,
    check_exercise_ai_generation_rate_limit,
    get_client_ip_for_request,
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


def test_get_client_ip_for_request_matches_get_client_ip():
    """Alias public aligne sur _get_client_ip."""
    request = MagicMock()
    request.headers = {"X-Forwarded-For": "198.51.100.2, 10.0.0.1"}
    request.client = MagicMock(host="127.0.0.1")
    assert get_client_ip_for_request(request) == _get_client_ip(request)


def test_auth_request_rate_limit_diagnostics_truncates_and_includes_caller():
    """Diagnostics auth: UA, referer, XFF, validate_caller (tronques)."""
    request = MagicMock()
    long_ua = "A" * 300
    request.headers = {
        "user-agent": long_ua,
        "referer": "https://app.example/path",
        "x-forwarded-for": "203.0.113.1, 10.0.0.1",
        VALIDATE_TOKEN_CALLER_HEADER: "routeSession",
    }
    diag = auth_request_rate_limit_diagnostics(request)
    assert "routeSession" in diag
    assert long_ua not in diag
    assert "A" * 50 in diag


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
async def test_rate_limit_auth_decorator_logs_diagnostics_when_blocked(monkeypatch):
    """429 auth: log WARNING avec UA / referer / XFF / validate_caller."""
    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setattr(
        "app.utils.rate_limit._check_rate_limit", lambda key, max_requests: False
    )

    @rate_limit_auth("validate-token")
    async def handler(request):
        return {"ok": True}

    request = MagicMock()
    request.headers = {
        "user-agent": "DiagUA/1.0",
        "referer": "https://example.com/challenges",
        "X-Forwarded-For": "203.0.113.9, 10.0.0.1",
        # Diagnostics use lowercase keys (Starlette normalizes; plain dict mocks need both).
        "x-forwarded-for": "203.0.113.9, 10.0.0.1",
        VALIDATE_TOKEN_CALLER_HEADER: "syncCookie",
    }
    request.client = MagicMock(host="127.0.0.1")

    with patch("app.utils.rate_limit.logger") as mock_logger:
        result = await handler(request)

    assert result.status_code == 429
    mock_logger.warning.assert_called_once()
    _fmt, endpoint, ip, diag = mock_logger.warning.call_args[0]
    assert endpoint == "validate-token"
    assert ip == "203.0.113.9"
    assert "DiagUA" in diag
    assert "challenges" in diag
    assert "203.0.113.9" in diag
    assert "syncCookie" in diag


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


def test_check_ai_generation_rate_limit_hourly(monkeypatch):
    """La limite horaire IA retourne le message horaire attendu."""
    monkeypatch.setenv("TESTING", "false")

    class StubStore:
        def __init__(self):
            self.calls = 0

        def check(self, key, max_requests, window_sec):
            self.calls += 1
            return self.calls != 1 and True

    monkeypatch.setattr("app.utils.rate_limit._get_store", lambda: StubStore())
    allowed, reason = check_ai_generation_rate_limit(123)
    assert allowed is False
    assert reason == MSG_AI_HOURLY_RATE_LIMIT


def test_check_ai_generation_rate_limit_daily(monkeypatch):
    """La limite journaliere IA retourne le message journalier attendu."""
    monkeypatch.setenv("TESTING", "false")

    class StubStore:
        def __init__(self):
            self.calls = 0

        def check(self, key, max_requests, window_sec):
            self.calls += 1
            return self.calls == 1

    monkeypatch.setattr("app.utils.rate_limit._get_store", lambda: StubStore())
    allowed, reason = check_ai_generation_rate_limit(123)
    assert allowed is False
    assert reason == MSG_AI_DAILY_RATE_LIMIT


def test_check_exercise_ai_generation_rate_limit_hourly(monkeypatch):
    """Limite horaire exercices IA : cles distinctes, message dedie."""
    monkeypatch.setenv("TESTING", "false")
    seen_keys = []

    class StubStore:
        def __init__(self):
            self.calls = 0

        def check(self, key, max_requests, window_sec):
            seen_keys.append(key)
            self.calls += 1
            return self.calls != 1

    monkeypatch.setattr("app.utils.rate_limit._get_store", lambda: StubStore())
    allowed, reason = check_exercise_ai_generation_rate_limit(456)
    assert allowed is False
    assert reason == MSG_EXERCISE_AI_HOURLY_RATE_LIMIT
    assert any("exercise_ai_generation" in k for k in seen_keys)


def test_check_exercise_ai_generation_rate_limit_daily(monkeypatch):
    """Limite journaliere exercices IA : message dedie."""
    monkeypatch.setenv("TESTING", "false")

    class StubStore:
        def __init__(self):
            self.calls = 0

        def check(self, key, max_requests, window_sec):
            self.calls += 1
            return self.calls == 1

    monkeypatch.setattr("app.utils.rate_limit._get_store", lambda: StubStore())
    allowed, reason = check_exercise_ai_generation_rate_limit(456)
    assert allowed is False
    assert reason == MSG_EXERCISE_AI_DAILY_RATE_LIMIT
