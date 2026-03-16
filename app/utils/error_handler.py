"""
Helper pour la gestion standardisée des erreurs dans les handlers.

Schéma d'erreur API unifié (audit Alpha 2):
- code: code machine-readable (NOT_FOUND, VALIDATION_ERROR, etc.)
- message: message utilisateur principal
- error: alias de message (rétrocompatibilité frontend)
- path, trace_id, field_errors: optionnels
"""

import traceback
import uuid
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.responses import JSONResponse

from app.utils.json_utils import make_json_serializable

# Message générique pour ne pas exposer les détails techniques en production
GENERIC_ERROR_MESSAGE = "Une erreur est survenue. Veuillez réessayer."

# Codes d'erreur standardisés (alignés frontend: client.ts lit message || detail || error)
API_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def capture_exception_for_sentry(
    exc: Exception,
    *,
    status_code: int = 500,
    user_message: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Capture une exception dans Sentry si le SDK est initialisé.

    Utile pour les erreurs déjà catchées puis mappées vers une réponse JSON,
    qui n'atteignent sinon pas StarletteIntegration.
    """
    try:
        import sentry_sdk

        with sentry_sdk.push_scope() as scope:
            scope.set_tag("handled", "true")
            scope.set_tag("status_code", str(status_code))
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)
            if user_message:
                scope.set_context("api_response", {"message": user_message})
            if extra_context:
                for key, value in extra_context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(exc)
    except ImportError:
        return
    except Exception as sentry_capture_error:
        logger.debug(f"Capture Sentry ignorée: {sentry_capture_error}")


def api_error_json(
    status_code: int,
    message: str,
    *,
    path: Optional[str] = None,
    trace_id: Optional[str] = None,
    field_errors: Optional[List[Dict[str, str]]] = None,
    include_error_alias: bool = True,
) -> Dict[str, Any]:
    """
    Construit un corps JSON d'erreur standardisé.

    Args:
        status_code: Code HTTP (400, 401, 404, 500, etc.)
        message: Message utilisateur principal
        path: Chemin de la requête (optionnel)
        trace_id: ID de traçabilité pour 500 (optionnel)
        field_errors: Erreurs de validation par champ (optionnel)
        include_error_alias: Inclure "error" = message pour rétrocompatibilité frontend

    Returns:
        Dictionnaire prêt pour JSONResponse
    """
    code = API_ERROR_CODES.get(status_code, f"HTTP_{status_code}")
    payload: Dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if include_error_alias:
        payload["error"] = message
    if path:
        payload["path"] = path
    if trace_id:
        payload["trace_id"] = trace_id
    if field_errors:
        payload["field_errors"] = field_errors
    return payload


def api_error_response(
    status_code: int,
    message: str,
    *,
    path: Optional[str] = None,
    trace_id: Optional[str] = None,
    field_errors: Optional[List[Dict[str, str]]] = None,
) -> JSONResponse:
    """
    Retourne une JSONResponse avec le schéma d'erreur unifié.
    Utilisable par les handlers et error_handlers globaux.
    """
    payload = api_error_json(
        status_code, message, path=path, trace_id=trace_id, field_errors=field_errors
    )
    return JSONResponse(payload, status_code=status_code)


def get_safe_error_message(exc: Exception, default: Optional[str] = None) -> str:
    """
    Retourne un message d'erreur sûr pour l'utilisateur.
    Ne jamais exposer le message brut de l'exception dans les réponses API externes.
    Les détails techniques restent dans les logs uniquement.
    """
    capture_exception_for_sentry(
        exc,
        status_code=500,
        user_message=default or GENERIC_ERROR_MESSAGE,
        tags={"capture_path": "get_safe_error_message"},
    )
    return default or GENERIC_ERROR_MESSAGE


def capture_internal_error_response(
    error: Exception,
    message: str,
    *,
    path: Optional[str] = None,
    trace_id: Optional[str] = None,
    field_errors: Optional[List[Dict[str, str]]] = None,
    tags: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Retourne une réponse 500 standardisée après capture Sentry de l'exception.
    """
    capture_exception_for_sentry(
        error,
        status_code=500,
        user_message=message,
        tags=tags,
    )
    return api_error_response(
        500,
        message,
        path=path,
        trace_id=trace_id,
        field_errors=field_errors,
    )


class ErrorHandler:
    """
    Classe utilitaire pour gérer les erreurs de manière standardisée.
    """

    @staticmethod
    def create_error_response(
        error: Exception,
        status_code: int = 500,
        user_message: Optional[str] = None,
        include_details: Optional[bool] = None,
    ) -> JSONResponse:
        """
        Crée une réponse d'erreur JSON standardisée.

        Les réponses API externes ne contiennent jamais traceback ni error_type.
        Les détails techniques restent dans les logs uniquement (D1 hardening).

        Args:
            error: Exception levée
            status_code: Code HTTP d'erreur (défaut: 500)
            user_message: Message à afficher à l'utilisateur (si None, message générique)
            include_details: Ignoré — conservé pour rétrocompatibilité, jamais appliqué au payload
        """
        error_type = type(error).__name__
        error_message = str(error)

        # D1 : ne jamais exposer traceback/error_type/details dans les payloads JSON
        display_error = user_message or GENERIC_ERROR_MESSAGE

        logger.error(f"{error_type}: {error_message}")
        logger.debug(f"Traceback complet:\n{traceback.format_exc()}")
        capture_exception_for_sentry(
            error,
            status_code=status_code,
            user_message=display_error,
            tags={"capture_path": "ErrorHandler.create_error_response"},
        )

        payload = api_error_json(status_code, display_error)
        payload = make_json_serializable(payload)

        return JSONResponse(payload, status_code=status_code)

    @staticmethod
    def create_validation_error(
        field: Optional[str] = None,
        message: Optional[str] = None,
        status_code: int = 400,
        *,
        errors: Optional[List[str]] = None,
        user_message: Optional[str] = None,
    ) -> JSONResponse:
        """
        Crée une réponse d'erreur de validation.

        Deux modes d'appel :
        1) (field, message) : erreur sur un champ donné — rétrocompatibilité
        2) (errors=[...], user_message=...) : erreurs multiples (ex. paramètres filtrage)

        Args:
            field: Nom du champ en erreur (mode 1)
            message: Message d'erreur (mode 1)
            status_code: Code HTTP (défaut: 400)
            errors: Liste de messages d'erreur (mode 2)
            user_message: Message principal utilisateur (mode 2)

        Returns:
            JSONResponse avec le format d'erreur de validation
        """
        if errors is not None and user_message is not None:
            # Mode 2 : erreurs multiples (challenge_handlers, etc.)
            field_errors = [{"field": "params", "message": e} for e in errors]
            logger.warning(f"Erreur de validation: {user_message} — {errors}")
            payload = api_error_json(
                status_code,
                user_message,
                field_errors=field_errors,
            )
            return JSONResponse(payload, status_code=status_code)
        if field and message:
            # Mode 1 : champ unique — rétrocompatibilité
            logger.warning(f"Erreur de validation pour le champ '{field}': {message}")
            payload = api_error_json(
                status_code,
                message,
                field_errors=[{"field": field, "message": message}],
            )
            payload["field"] = field  # rétrocompatibilité
            return JSONResponse(payload, status_code=status_code)
        raise TypeError(
            "create_validation_error: (field, message) ou (errors=..., user_message=...) requis"
        )

    @staticmethod
    def create_not_found_error(
        resource_type: str, resource_id: Any, status_code: int = 404
    ) -> JSONResponse:
        """
        Crée une réponse d'erreur "ressource non trouvée".

        Args:
            resource_type: Type de ressource (ex: "exercice", "utilisateur")
            resource_id: ID de la ressource
            status_code: Code HTTP (défaut: 404)

        Returns:
            JSONResponse avec le format d'erreur "non trouvé"
        """
        message = f"{resource_type.capitalize()} non trouvé"
        logger.warning(f"{message}: ID {resource_id}")
        payload = api_error_json(status_code, message)
        payload["resource_type"] = resource_type
        payload["resource_id"] = str(resource_id)
        return JSONResponse(payload, status_code=status_code)
