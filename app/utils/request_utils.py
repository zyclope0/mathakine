"""
Utilitaires pour le parsing des requêtes HTTP (DRY).
Centralise le pattern await request.json() + validation des champs.
"""

from typing import Any, Dict, Optional, Union

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.constants import Messages
from app.core.logging_config import get_logger
from app.utils.error_handler import api_error_response

logger = get_logger(__name__)

# Type : soit le dict parsé, soit une JSONResponse d'erreur
ParseResult = Union[Dict[str, Any], JSONResponse]


async def parse_json_body_any(request: Request) -> ParseResult:
    """
    Parse le body JSON sans validation de champs.
    Retourne le dict parsé ou JSONResponse 422/400 si invalide.
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.warning(f"parse_json_body_any: body JSON invalide — {e}")
        return api_error_response(422, Messages.JSON_BODY_INVALID)

    if not isinstance(body, dict):
        return api_error_response(400, Messages.JSON_BODY_NOT_OBJECT)
    return body


async def parse_json_body(
    request: Request,
    required: Optional[Dict[str, str]] = None,
    optional: Optional[Dict[str, Any]] = None,
    strip_strings: bool = True,
    no_strip_fields: Optional[set] = None,
) -> ParseResult:
    """
    Parse le body JSON de la requête et valide les champs.

    Args:
        request: Requête Starlette
        required: {nom_champ: message_erreur} — champs obligatoires (non vides)
        optional: {nom_champ: valeur_defaut} — champs optionnels
        strip_strings: Appliquer .strip() sur les valeurs string (défaut: True)
        no_strip_fields: Champs à ne pas strip (ex: {"password"})

    Returns:
        dict avec les champs parsés, ou JSONResponse si erreur (400/422)

    Exemple:
        data_or_err = await parse_json_body(request, required={"email": "Adresse email requise"})
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        email = data_or_err["email"]
    """
    required = required or {}
    optional = optional or {}
    no_strip_fields = no_strip_fields or set()

    try:
        body = await request.json()
    except Exception as e:
        logger.warning(f"parse_json_body: body JSON invalide — {e}")
        return api_error_response(422, Messages.JSON_BODY_INVALID)

    if not isinstance(body, dict):
        return api_error_response(400, Messages.JSON_BODY_NOT_OBJECT)

    def _strip_val(val: Any, field: str) -> Any:
        if isinstance(val, str) and strip_strings and field not in no_strip_fields:
            return val.strip()
        return val

    result: Dict[str, Any] = {}

    # Champs obligatoires
    for field, error_msg in required.items():
        value = body.get(field)
        if value is None:
            return api_error_response(400, error_msg)
        value = _strip_val(value, field)
        if isinstance(value, str) and not value:
            return api_error_response(400, error_msg)
        result[field] = value

    # Champs optionnels
    for field, default in optional.items():
        value = body.get(field, default)
        value = _strip_val(value, field)
        result[field] = value

    return result
