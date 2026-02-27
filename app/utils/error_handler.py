"""
Helper pour la gestion standardisée des erreurs dans les handlers.

Schéma d'erreur API unifié (audit Alpha 2):
- code: code machine-readable (NOT_FOUND, VALIDATION_ERROR, etc.)
- message: message utilisateur principal
- error: alias de message (rétrocompatibilité frontend)
- path, trace_id, field_errors: optionnels
"""

import os
import traceback
import uuid
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.responses import JSONResponse

from app.core.config import settings
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


def get_safe_error_message(exc: Exception, default: str = None) -> str:
    """
    Retourne un message d'erreur sûr pour l'utilisateur.
    En production ou hors DEBUG : message générique.
    En DEBUG (développement) : message de l'exception.
    """
    if os.getenv("ENVIRONMENT") == "production":
        return default or GENERIC_ERROR_MESSAGE
    if settings.LOG_LEVEL.upper() != "DEBUG":
        return default or GENERIC_ERROR_MESSAGE
    return str(exc)


class ErrorHandler:
    """
    Classe utilitaire pour gérer les erreurs de manière standardisée.
    """

    @staticmethod
    def create_error_response(
        error: Exception,
        status_code: int = 500,
        user_message: Optional[str] = None,
        include_details: bool = None,
    ) -> JSONResponse:
        """
        Crée une réponse d'erreur JSON standardisée.

        Args:
            error: Exception levée
            status_code: Code HTTP d'erreur (défaut: 500)
            user_message: Message à afficher à l'utilisateur (si None, utilise le message de l'exception)
            include_details: Inclure les détails techniques (défaut: True si DEBUG, False sinon)

        Returns:
            JSONResponse avec le format d'erreur standardisé
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Ne jamais exposer traceback/détails en production
        if include_details is None:
            include_details = (
                settings.LOG_LEVEL.upper() == "DEBUG"
                and os.getenv("ENVIRONMENT") != "production"
            )

        # Message utilisateur : générique en prod pour éviter fuite d'info
        display_error = user_message or (
            error_message if include_details else GENERIC_ERROR_MESSAGE
        )

        # Construire la réponse
        response_data: Dict[str, Any] = {
            "error": display_error,
            "error_type": error_type,
        }

        # Ajouter les détails techniques uniquement en dev
        if include_details:
            response_data["error_message"] = error_message
            response_data["details"] = traceback.format_exc()

        # Logger l'erreur
        logger.error(f"{error_type}: {error_message}")
        if include_details:
            logger.debug(f"Traceback complet:\n{traceback.format_exc()}")

        # Nettoyer les données pour sérialisation JSON (gère les MagicMock dans les tests)
        response_data = make_json_serializable(response_data)

        return JSONResponse(response_data, status_code=status_code)

    @staticmethod
    def create_validation_error(
        field: str, message: str, status_code: int = 400
    ) -> JSONResponse:
        """
        Crée une réponse d'erreur de validation.

        Args:
            field: Nom du champ en erreur
            message: Message d'erreur
            status_code: Code HTTP (défaut: 400)

        Returns:
            JSONResponse avec le format d'erreur de validation
        """
        response_data = {
            "error": "Erreur de validation",
            "field": field,
            "message": message,
        }

        logger.warning(f"Erreur de validation pour le champ '{field}': {message}")

        return JSONResponse(response_data, status_code=status_code)

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
        response_data = {
            "error": f"{resource_type.capitalize()} non trouvé",
            "resource_type": resource_type,
            "resource_id": str(resource_id),
        }

        logger.warning(f"{resource_type.capitalize()} non trouvé: ID {resource_id}")

        return JSONResponse(response_data, status_code=status_code)
