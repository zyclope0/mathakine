"""Tests pour le schéma d'erreur API unifié (audit Alpha 2)."""

import json

import pytest

from app.utils.error_handler import (
    API_ERROR_CODES,
    ErrorHandler,
    api_error_json,
    api_error_response,
    get_safe_error_message,
)


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
