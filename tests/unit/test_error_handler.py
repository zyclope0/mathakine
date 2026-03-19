"""Tests pour le schéma d'erreur API unifié (audit Alpha 2)."""

import json
import sys
import types
from contextlib import contextmanager

import pytest

from app.utils.error_handler import (
    API_ERROR_CODES,
    GENERIC_ERROR_MESSAGE,
    ErrorHandler,
    api_error_json,
    api_error_response,
    capture_internal_error_response,
    get_safe_error_message,
)


def _install_fake_sentry(monkeypatch):
    captured: dict = {
        "exceptions": [],
        "tags": {},
        "contexts": {},
    }

    class _FakeScope:
        def set_tag(self, key, value):
            captured["tags"][key] = value

        def set_context(self, key, value):
            captured["contexts"][key] = value

    @contextmanager
    def _push_scope():
        yield _FakeScope()

    fake_module = types.SimpleNamespace(
        push_scope=_push_scope,
        capture_exception=lambda exc: captured["exceptions"].append(exc),
    )
    monkeypatch.setitem(sys.modules, "sentry_sdk", fake_module)
    return captured


class TestApiErrorJson:
    """Tests api_error_json — format JSON standardisé."""

    def test_basic_400(self):
        payload = api_error_json(400, "Données invalides")
        assert payload["code"] == "BAD_REQUEST"
        assert payload["message"] == "Données invalides"
        assert payload["error"] == "Données invalides"

    def test_404_with_path(self):
        payload = api_error_json(
            404, "Ressource non trouvée", path="/api/exercises/999"
        )
        assert payload["code"] == "NOT_FOUND"
        assert payload["path"] == "/api/exercises/999"

    def test_500_with_trace_id(self):
        payload = api_error_json(500, "Erreur serveur", trace_id="abc123")
        assert payload["code"] == "INTERNAL_ERROR"
        assert payload["trace_id"] == "abc123"

    def test_400_with_field_errors(self):
        payload = api_error_json(
            400,
            "Erreur de validation",
            field_errors=[
                {"field": "email", "message": "Email invalide"},
                {"field": "password", "message": "Trop court"},
            ],
        )
        assert payload["field_errors"] == [
            {"field": "email", "message": "Email invalide"},
            {"field": "password", "message": "Trop court"},
        ]

    def test_no_error_alias(self):
        payload = api_error_json(404, "Not found", include_error_alias=False)
        assert "error" not in payload
        assert payload["message"] == "Not found"

    def test_api_error_codes_mapping(self):
        assert API_ERROR_CODES[400] == "BAD_REQUEST"
        assert API_ERROR_CODES[404] == "NOT_FOUND"
        assert API_ERROR_CODES[500] == "INTERNAL_ERROR"


class TestApiErrorResponse:
    """Tests api_error_response — JSONResponse avec schéma unifié."""

    def test_returns_json_response(self):
        resp = api_error_response(404, "Not found", path="/api/foo")
        assert resp.status_code == 404
        # Body est bytes, on vérifie le contenu
        import json

        data = json.loads(resp.body.decode())
        assert data["code"] == "NOT_FOUND"
        assert data["message"] == "Not found"
        assert data["path"] == "/api/foo"


class TestGetSafeErrorMessage:
    """Tests get_safe_error_message — pas de régression."""

    def test_returns_string(self):
        msg = get_safe_error_message(ValueError("e"), default="Erreur")
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_never_exposes_exception_message_d1(self):
        """D1: Ne jamais exposer le message brut de l'exception dans les réponses API."""
        msg = get_safe_error_message(ValueError("secret internal detail"))
        assert msg == GENERIC_ERROR_MESSAGE
        assert "secret" not in msg

    def test_captures_exception_to_sentry(self, monkeypatch):
        captured = _install_fake_sentry(monkeypatch)
        err = ValueError("internal detail")

        msg = get_safe_error_message(err)

        assert msg == GENERIC_ERROR_MESSAGE
        assert captured["exceptions"] == [err]
        assert captured["tags"]["handled"] == "true"
        assert captured["tags"]["status_code"] == "500"
        assert captured["tags"]["capture_path"] == "get_safe_error_message"


class TestCreateValidationError:
    """Tests ErrorHandler.create_validation_error — modes (field, message) et (errors, user_message)."""

    def test_mode_field_message_retrocompatibilite(self):
        """Mode classique (field, message) — rétrocompatibilité."""
        resp = ErrorHandler.create_validation_error(
            field="email", message="Email invalide", status_code=400
        )
        assert resp.status_code == 400
        data = json.loads(resp.body.decode())
        assert data["code"] == "BAD_REQUEST"
        assert data["message"] == "Email invalide"
        assert data["field"] == "email"
        assert data["field_errors"] == [{"field": "email", "message": "Email invalide"}]

    def test_mode_errors_user_message_challenge_handlers(self):
        """Mode (errors, user_message) — utilisé par challenge_handlers."""
        resp = ErrorHandler.create_validation_error(
            errors=["Paramètre limit invalide"],
            user_message="Les paramètres de filtrage sont invalides.",
        )
        assert resp.status_code == 400
        data = json.loads(resp.body.decode())
        assert data["code"] == "BAD_REQUEST"
        assert data["message"] == "Les paramètres de filtrage sont invalides."
        assert data["field_errors"] == [
            {"field": "params", "message": "Paramètre limit invalide"}
        ]

    def test_mode_errors_multiple(self):
        """Mode (errors, user_message) avec plusieurs erreurs."""
        resp = ErrorHandler.create_validation_error(
            errors=["Erreur 1", "Erreur 2"],
            user_message="Validation échouée.",
        )
        data = json.loads(resp.body.decode())
        assert len(data["field_errors"]) == 2
        assert data["field_errors"][0]["message"] == "Erreur 1"
        assert data["field_errors"][1]["message"] == "Erreur 2"

    def test_missing_args_raises_typeerror(self):
        """Appel sans args valides lève TypeError."""
        with pytest.raises(TypeError, match="create_validation_error.*requis"):
            ErrorHandler.create_validation_error()


class TestCreateErrorResponseD1:
    """Tests ErrorHandler.create_error_response — D1: pas de traceback/details en JSON."""

    def test_never_exposes_error_type_or_details_in_payload(self):
        """D1: Les payloads JSON ne doivent jamais contenir error_type ni details."""
        resp = ErrorHandler.create_error_response(
            ValueError("secret traceback content"), status_code=500
        )
        data = json.loads(resp.body.decode())
        assert "error_type" not in data
        assert "details" not in data
        assert "traceback" not in str(data).lower()
        assert "secret" not in data.get("message", "")
        assert data["message"] == GENERIC_ERROR_MESSAGE

    def test_uses_user_message_when_provided(self):
        """user_message explicite est affiché, pas le message de l'exception."""
        resp = ErrorHandler.create_error_response(
            ValueError("internal"), status_code=500, user_message="Erreur côté serveur"
        )
        data = json.loads(resp.body.decode())
        assert data["message"] == "Erreur côté serveur"
        assert "error_type" not in data
        assert "details" not in data

    def test_create_error_response_captures_exception_to_sentry(self, monkeypatch):
        captured = _install_fake_sentry(monkeypatch)
        err = RuntimeError("boom")

        resp = ErrorHandler.create_error_response(
            err, status_code=500, user_message="Erreur serveur"
        )

        assert resp.status_code == 500
        assert captured["exceptions"] == [err]
        assert captured["tags"]["capture_path"] == "ErrorHandler.create_error_response"
        assert captured["contexts"]["api_response"]["message"] == "Erreur serveur"

    def test_handler_log_context_tags_sentry_and_payload_still_d1(self, monkeypatch):
        """I6: chemin handlers — un seul log contextualisé, payload sans fuite D1."""
        captured = _install_fake_sentry(monkeypatch)
        err = RuntimeError("secret internal")

        resp = ErrorHandler.create_error_response(
            err,
            status_code=500,
            user_message=None,
            handler_log_context="GET /api/challenges — recuperation liste",
        )

        data = json.loads(resp.body.decode())
        assert data["message"] == GENERIC_ERROR_MESSAGE
        assert "secret" not in data.get("message", "")
        assert captured["exceptions"] == [err]
        assert captured["tags"]["handler_context"].startswith("GET /api/challenges")


class TestCaptureInternalErrorResponse:
    def test_returns_500_and_captures_exception(self, monkeypatch):
        captured = _install_fake_sentry(monkeypatch)
        err = RuntimeError("db down")

        resp = capture_internal_error_response(
            err,
            "Erreur serveur",
            tags={"handler": "tests.fake_handler"},
        )

        data = json.loads(resp.body.decode())
        assert resp.status_code == 500
        assert data["message"] == "Erreur serveur"
        assert captured["exceptions"] == [err]
        assert captured["tags"]["handler"] == "tests.fake_handler"
