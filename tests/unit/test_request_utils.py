"""
Tests pour app.utils.request_utils (parse_json_body, parse_json_body_any).
Vérifie les messages centralisés Messages.JSON_BODY_* et la validation des champs.
D2: Tests 413 Payload Too Large.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.core.constants import Messages
from app.utils.request_utils import (
    PAYLOAD_TOO_LARGE_MESSAGE,
    parse_json_body,
    parse_json_body_any,
)


def _response_body_text(response):
    """Extrait le texte du body d'une JSONResponse."""
    body = response.body
    return body.decode("utf-8") if isinstance(body, bytes) else str(body)


def _make_request_with_body(body_bytes: bytes, content_length: str | None = None):
    """Construit un mock Request avec stream et headers pour D2."""

    async def stream():
        yield body_bytes

    request = MagicMock()
    request.stream = stream
    request.headers.get = MagicMock(return_value=content_length)
    return request


@pytest.mark.asyncio
async def test_parse_json_body_invalid_json_returns_422():
    """Body JSON invalide → 422 avec Messages.JSON_BODY_INVALID."""
    request = _make_request_with_body(b"not valid json")

    result = await parse_json_body(request)

    assert result.status_code == 422
    data = json.loads(_response_body_text(result))
    assert data.get("error") == Messages.JSON_BODY_INVALID


@pytest.mark.asyncio
async def test_parse_json_body_not_object_returns_400():
    """Body valide mais pas un objet (liste, string) → 400 avec Messages.JSON_BODY_NOT_OBJECT."""
    request = _make_request_with_body(b'["not", "a", "dict"]')

    result = await parse_json_body(request)

    assert result.status_code == 400
    data = json.loads(_response_body_text(result))
    assert data.get("error") == Messages.JSON_BODY_NOT_OBJECT


@pytest.mark.asyncio
async def test_parse_json_body_valid_dict_success():
    """Body objet valide → champs required/optional extraits (pas de 422/400)."""
    request = _make_request_with_body(b'{"email": "a@b.com", "extra": "ignored"}')

    result = await parse_json_body(
        request, required={"email": "Email requis"}, optional={"name": None}
    )

    assert isinstance(result, dict)
    assert result["email"] == "a@b.com"
    assert result.get("name") is None


@pytest.mark.asyncio
async def test_parse_json_body_required_field_missing_returns_400():
    """Champ requis manquant → 400 avec message personnalisé."""
    request = _make_request_with_body(b'{"other": "value"}')

    result = await parse_json_body(request, required={"email": "Adresse email requise"})

    assert result.status_code == 400
    data = json.loads(_response_body_text(result))
    assert data.get("error") == "Adresse email requise"


# --- D2: Payload size enforcement ---


@pytest.mark.asyncio
async def test_parse_json_body_content_length_exceeds_limit_returns_413():
    """D2: Content-Length > MAX_CONTENT_LENGTH → 413 sans lire le body."""
    with patch.object(settings, "MAX_CONTENT_LENGTH", 100):
        request = MagicMock()
        request.headers.get = MagicMock(return_value="101")
        # stream jamais appelé si Content-Length rejeté

        async def empty_stream():
            yield b""

        request.stream = empty_stream

        result = await parse_json_body(request)

    assert result.status_code == 413
    data = json.loads(_response_body_text(result))
    assert data.get("message") == PAYLOAD_TOO_LARGE_MESSAGE


@pytest.mark.asyncio
async def test_parse_json_body_stream_exceeds_limit_returns_413():
    """D2: Stream dépasse MAX_CONTENT_LENGTH → 413."""
    with patch.object(settings, "MAX_CONTENT_LENGTH", 100):

        async def big_stream():
            yield b"x" * 101

        request = MagicMock()
        request.headers.get = MagicMock(return_value=None)
        request.stream = big_stream

        result = await parse_json_body(request)

    assert result.status_code == 413
    data = json.loads(_response_body_text(result))
    assert data.get("message") == PAYLOAD_TOO_LARGE_MESSAGE


@pytest.mark.asyncio
async def test_parse_json_body_any_content_length_exceeds_limit_returns_413():
    """D2: parse_json_body_any rejette aussi payload trop grand."""
    with patch.object(settings, "MAX_CONTENT_LENGTH", 50):
        request = MagicMock()
        request.headers.get = MagicMock(return_value="51")

        async def empty_stream():
            yield b""

        request.stream = empty_stream

        result = await parse_json_body_any(request)

    assert result.status_code == 413
    data = json.loads(_response_body_text(result))
    assert data.get("message") == PAYLOAD_TOO_LARGE_MESSAGE


@pytest.mark.asyncio
async def test_parse_json_body_at_limit_accepted():
    """D2: Payload exactement à la limite → accepté."""
    body = b'{"email": "a@b.com"}'
    with patch.object(settings, "MAX_CONTENT_LENGTH", len(body)):
        request = _make_request_with_body(body)

        result = await parse_json_body(request, required={"email": "Email requis"})

    assert isinstance(result, dict)
    assert result["email"] == "a@b.com"
