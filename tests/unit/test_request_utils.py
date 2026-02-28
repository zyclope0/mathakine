"""
Tests pour app.utils.request_utils (parse_json_body).
Vérifie les messages centralisés Messages.JSON_BODY_* et la validation des champs.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.constants import Messages
from app.utils.request_utils import parse_json_body


def _response_body_text(response):
    """Extrait le texte du body d'une JSONResponse."""
    body = response.body
    return body.decode("utf-8") if isinstance(body, bytes) else str(body)


@pytest.mark.asyncio
async def test_parse_json_body_invalid_json_returns_422():
    """Body JSON invalide → 422 avec Messages.JSON_BODY_INVALID."""
    request = MagicMock()
    request.json = AsyncMock(side_effect=ValueError("Invalid JSON"))

    result = await parse_json_body(request)

    assert result.status_code == 422
    data = json.loads(_response_body_text(result))
    assert data.get("error") == Messages.JSON_BODY_INVALID


@pytest.mark.asyncio
async def test_parse_json_body_not_object_returns_400():
    """Body valide mais pas un objet (liste, string) → 400 avec Messages.JSON_BODY_NOT_OBJECT."""
    request = MagicMock()
    request.json = AsyncMock(return_value=["not", "a", "dict"])

    result = await parse_json_body(request)

    assert result.status_code == 400
    data = json.loads(_response_body_text(result))
    assert data.get("error") == Messages.JSON_BODY_NOT_OBJECT


@pytest.mark.asyncio
async def test_parse_json_body_valid_dict_success():
    """Body objet valide → champs required/optional extraits (pas de 422/400)."""
    request = MagicMock()
    request.json = AsyncMock(return_value={"email": "a@b.com", "extra": "ignored"})

    result = await parse_json_body(
        request, required={"email": "Email requis"}, optional={"name": None}
    )

    assert isinstance(result, dict)
    assert result["email"] == "a@b.com"
    assert result.get("name") is None


@pytest.mark.asyncio
async def test_parse_json_body_required_field_missing_returns_400():
    """Champ requis manquant → 400 avec message personnalisé."""
    request = MagicMock()
    request.json = AsyncMock(return_value={"other": "value"})

    result = await parse_json_body(request, required={"email": "Adresse email requise"})

    assert result.status_code == 400
    data = json.loads(_response_body_text(result))
    assert data.get("error") == "Adresse email requise"
