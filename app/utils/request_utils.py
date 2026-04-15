"""
Utilitaires pour le parsing des requêtes HTTP (DRY).
Centralise le pattern await request.json() + validation des champs.

D2: Contrôle central MAX_CONTENT_LENGTH avant parsing JSON.
"""

import json
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.constants import Messages
from app.core.logging_config import get_logger
from app.utils.error_handler import api_error_response

logger = get_logger(__name__)

# Type : soit le dict parsé, soit une JSONResponse d'erreur
ParseResult = Union[Dict[str, Any], JSONResponse]

PAYLOAD_TOO_LARGE_MESSAGE = "Payload too large"


async def read_body_with_limit(
    request: Request,
) -> Tuple[Optional[bytes], Optional[JSONResponse]]:
    """
    Lit le body avec limite MAX_CONTENT_LENGTH (D2/D2b).
    Retourne (body_bytes, None) ou (None, json_response_413) si trop grand.
    Gère Content-Length présent et absent/invalide.
    Public pour les handlers qui lisent le body hors parse_json_body*.
    """
    max_size = settings.MAX_CONTENT_LENGTH

    # Fast path: Content-Length présent et > limite → rejet sans lire
    cl_raw = request.headers.get("content-length")
    if cl_raw is not None:
        try:
            cl = int(cl_raw)
            if cl < 0:
                raise ValueError("negative")
            if cl > max_size:
                logger.warning(
                    "Payload too large: Content-Length=%s > %s", cl, max_size
                )
                return None, api_error_response(413, PAYLOAD_TOO_LARGE_MESSAGE)
        except (ValueError, TypeError):
            pass  # invalide, fallback lecture stream

    # Lecture stream avec limite (Content-Length absent ou invalide)
    total = 0
    chunks = []
    async for chunk in request.stream():
        total += len(chunk)
        if total > max_size:
            logger.warning("Payload too large: stream exceeded %s bytes", max_size)
            return None, api_error_response(413, PAYLOAD_TOO_LARGE_MESSAGE)
        chunks.append(chunk)
    return b"".join(chunks), None


async def parse_json_body_any(request: Request) -> ParseResult:
    """
    Parse le body JSON sans validation de champs.
    Applique MAX_CONTENT_LENGTH avant parsing (D2).
    Retourne le dict parsé ou JSONResponse 413/422/400 si invalide.
    """
    body_bytes, err = await read_body_with_limit(request)
    if err is not None:
        return err

    try:
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception as e:
        logger.warning("parse_json_body_any: body JSON invalide — %s", e)
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

    body_bytes, err = await read_body_with_limit(request)
    if err is not None:
        return err

    try:
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception as e:
        logger.warning("parse_json_body: body JSON invalide — %s", e)
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


TModel = TypeVar("TModel", bound=BaseModel)


async def parse_json_body_as_model(
    request: Request,
    model_cls: Type[TModel],
) -> Union[TModel, JSONResponse]:
    """
    Parse le body JSON (limite MAX_CONTENT_LENGTH) et valide avec un modèle Pydantic.

    Retourne l'instance validée ou une JSONResponse 422 avec ``error`` + ``detail`` (errors Pydantic).
    """
    raw = await parse_json_body_any(request)
    if isinstance(raw, JSONResponse):
        return raw
    try:
        return model_cls.model_validate(raw)
    except ValidationError as e:
        logger.warning(
            "parse_json_body_as_model: validation %s — %s", model_cls.__name__, e
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": "Requête invalide",
                "detail": e.errors(include_url=False),
            },
        )
