"""
Utilitaires pour le parsing des requêtes HTTP (DRY).
Centralise le pattern await request.json() + validation des champs.
"""
from typing import Any, Dict, Optional, Union

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Type : soit le dict parsé, soit une JSONResponse d'erreur
ParseResult = Union[Dict[str, Any], JSONResponse]


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
        return JSONResponse(
            {"error": "Corps de requête JSON invalide ou manquant"},
            status_code=422,
        )

    if not isinstance(body, dict):
        return JSONResponse(
            {"error": "Le corps doit être un objet JSON"},
            status_code=400,
        )

    def _strip_val(val: Any, field: str) -> Any:
        if isinstance(val, str) and strip_strings and field not in no_strip_fields:
            return val.strip()
        return val

    result: Dict[str, Any] = {}

    # Champs obligatoires
    for field, error_msg in required.items():
        value = body.get(field)
        if value is None:
            return JSONResponse({"error": error_msg}, status_code=400)
        value = _strip_val(value, field)
        if isinstance(value, str) and not value:
            return JSONResponse({"error": error_msg}, status_code=400)
        result[field] = value

    # Champs optionnels
    for field, default in optional.items():
        value = body.get(field, default)
        value = _strip_val(value, field)
        result[field] = value

    return result
