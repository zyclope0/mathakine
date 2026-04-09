"""
Tests unitaires pour le middleware CSRF centralisé (audit H6).

Couvre :
- Configuration (exemptions, méthodes mutantes)
- Comportement fonctionnel (bypass GET, bypass exempt, blocage 403, validation)

Note : conftest.py mock validate_csrf_token (session-scoped, autouse) pour les
tests d'intégration. Ici on restaure la vraie fonction pour tester le middleware
en isolation — la référence est capturée à l'import (avant le patch session).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.csrf import validate_csrf_token as _real_validate_csrf_token
from server.middleware import (
    _CSRF_EXEMPT_NORMALIZED,
    _CSRF_MUTATING_METHODS,
    CsrfMiddleware,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_request(method: str, path: str, cookies=None, headers=None) -> Request:
    """Construit un faux objet Request Starlette pour tester le middleware."""
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": b"",
        "root_path": "",
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in (headers or {}).items()
        ],
    }
    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        scope["headers"].append((b"cookie", cookie_str.encode()))
    return Request(scope)


async def _ok_handler(request):
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# 1. Configuration tests
# ---------------------------------------------------------------------------


class TestCsrfExemptRoutes:
    """Vérifie la cohérence de la configuration des exemptions."""

    def test_login_is_exempt(self):
        assert "/api/auth/login" in _CSRF_EXEMPT_NORMALIZED

    def test_register_is_exempt(self):
        assert "/api/users" in _CSRF_EXEMPT_NORMALIZED

    def test_refresh_is_exempt(self):
        assert "/api/auth/refresh" in _CSRF_EXEMPT_NORMALIZED

    def test_logout_is_exempt(self):
        assert "/api/auth/logout" in _CSRF_EXEMPT_NORMALIZED

    def test_forgot_password_is_exempt(self):
        assert "/api/auth/forgot-password" in _CSRF_EXEMPT_NORMALIZED

    def test_reset_password_is_not_exempt(self):
        assert "/api/auth/reset-password" not in _CSRF_EXEMPT_NORMALIZED

    def test_submit_attempt_is_not_exempt(self):
        assert "/api/exercises/1/attempt" not in _CSRF_EXEMPT_NORMALIZED

    def test_update_profile_is_not_exempt(self):
        assert "/api/users/me" not in _CSRF_EXEMPT_NORMALIZED


class TestCsrfMutatingMethods:
    """Vérifie que les méthodes mutantes sont correctement définies."""

    def test_post_is_mutating(self):
        assert "POST" in _CSRF_MUTATING_METHODS

    def test_put_is_mutating(self):
        assert "PUT" in _CSRF_MUTATING_METHODS

    def test_patch_is_mutating(self):
        assert "PATCH" in _CSRF_MUTATING_METHODS

    def test_delete_is_mutating(self):
        assert "DELETE" in _CSRF_MUTATING_METHODS

    def test_get_is_not_mutating(self):
        assert "GET" not in _CSRF_MUTATING_METHODS

    def test_options_is_not_mutating(self):
        assert "OPTIONS" not in _CSRF_MUTATING_METHODS


# ---------------------------------------------------------------------------
# 2. Functional tests (middleware dispatch logic)
# ---------------------------------------------------------------------------


class TestCsrfMiddlewareDispatch:
    """Teste le comportement réel du middleware CSRF.

    Restaure la vraie validate_csrf_token pour cette classe — le conftest.py
    session fixture la mock globalement pour les tests d'intégration.
    """

    @pytest.fixture(autouse=True)
    def _restore_real_csrf(self):
        """Annule le mock global et utilise la vraie validation CSRF."""
        with patch("app.utils.csrf.validate_csrf_token", _real_validate_csrf_token):
            yield

    @pytest.mark.asyncio
    async def test_get_request_passes_without_csrf(self):
        """GET ne devrait jamais être bloqué par le CSRF."""
        mw = CsrfMiddleware(app=None)
        req = _make_request("GET", "/api/exercises")
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        call_next.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exempt_post_passes_without_csrf(self):
        """POST sur une route exemptée (login) passe sans token CSRF."""
        mw = CsrfMiddleware(app=None)
        req = _make_request("POST", "/api/auth/login")
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        call_next.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_protected_post_without_auth_skips_csrf_and_calls_next(self):
        """Sans credentials auth, le CSRF laisse l'auth produire le 401 canonique."""
        mw = CsrfMiddleware(app=None)
        req = _make_request("POST", "/api/chat")
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        assert resp.status_code == 200
        call_next.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_non_api_post_passes_without_csrf(self):
        """POST sur une route non-API (webhook, etc.) passe sans CSRF."""
        mw = CsrfMiddleware(app=None)
        req = _make_request("POST", "/health")
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        call_next.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_protected_post_without_csrf_returns_403(self):
        """POST sur un endpoint protégé sans token CSRF -> 403."""
        mw = CsrfMiddleware(app=None)
        req = _make_request(
            "POST", "/api/exercises/1/attempt", cookies={"access_token": "jwt-test"}
        )
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        assert resp.status_code == 403
        call_next.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_protected_put_without_csrf_returns_403(self):
        """PUT sur un endpoint protégé sans token CSRF -> 403."""
        mw = CsrfMiddleware(app=None)
        req = _make_request("PUT", "/api/users/me", cookies={"access_token": "jwt-test"})
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        assert resp.status_code == 403
        call_next.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_protected_delete_without_csrf_returns_403(self):
        """DELETE sur un endpoint protégé sans token CSRF -> 403."""
        mw = CsrfMiddleware(app=None)
        req = _make_request("DELETE", "/api/users/me", cookies={"access_token": "jwt-test"})
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        assert resp.status_code == 403
        call_next.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_protected_post_with_valid_csrf_passes(self):
        """POST protégé avec cookie + header CSRF valide -> passe."""
        token = "test-csrf-token-abc123"
        mw = CsrfMiddleware(app=None)
        req = _make_request(
            "POST",
            "/api/exercises/1/attempt",
            cookies={"access_token": "jwt-test", "csrf_token": token},
            headers={"X-CSRF-Token": token},
        )
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        call_next.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_protected_post_with_mismatched_csrf_returns_403(self):
        """POST protégé avec cookie != header -> 403."""
        mw = CsrfMiddleware(app=None)
        req = _make_request(
            "POST",
            "/api/exercises/1/attempt",
            cookies={"access_token": "jwt-test", "csrf_token": "token-a"},
            headers={"X-CSRF-Token": "token-b"},
        )
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        assert resp.status_code == 403
        call_next.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_testing_env_does_not_bypass_csrf(self, monkeypatch):
        """TESTING=true ne bypass PAS le CSRF (S1 — audit 03/03/2026).

        Le bypass par variable d'environnement a été supprimé pour éviter
        qu'un attaquant qui contrôle l'env puisse désactiver la protection CSRF.
        Les tests utilisent unittest.mock.patch sur validate_csrf_token.
        """
        monkeypatch.setenv("TESTING", "true")
        mw = CsrfMiddleware(app=None)
        req = _make_request(
            "POST", "/api/exercises/1/attempt", cookies={"access_token": "jwt-test"}
        )
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        resp = await mw.dispatch(req, call_next)
        # Le middleware doit bloquer la requête malgré TESTING=true
        assert resp.status_code == 403
        call_next.assert_not_awaited()
