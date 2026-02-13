"""
Helper pour la gestion standardisée des erreurs dans les handlers.
"""
import os
import traceback
from typing import Any, Dict, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.responses import JSONResponse

from app.core.config import settings
from app.utils.json_utils import make_json_serializable

# Message générique pour ne pas exposer les détails techniques en production
GENERIC_ERROR_MESSAGE = "Une erreur est survenue. Veuillez réessayer."


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
        include_details: bool = None
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
        display_error = user_message or (error_message if include_details else GENERIC_ERROR_MESSAGE)

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
        field: str,
        message: str,
        status_code: int = 400
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
        resource_type: str,
        resource_id: Any,
        status_code: int = 404
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

