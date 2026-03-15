"""
Tests des endpoints API chat (/api/chat, /api/chat/stream).
Valident les branches erreur : OpenAI indisponible, cle manquante, message invalide.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


async def test_chat_openai_unavailable(client):
    """POST /api/chat sans OpenAI -> 503."""
    with patch("server.handlers.chat_handlers.OPENAI_AVAILABLE", False):
        response = await client.post("/api/chat", json={"message": "Bonjour"})
    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert "OpenAI" in data["error"]


async def test_chat_openai_key_missing(client):
    """POST /api/chat sans OPENAI_API_KEY -> 503."""
    with (
        patch("server.handlers.chat_handlers.OPENAI_AVAILABLE", True),
        patch("server.handlers.chat_handlers.settings") as mock_settings,
    ):
        mock_settings.OPENAI_API_KEY = ""
        response = await client.post("/api/chat", json={"message": "Bonjour"})
    assert response.status_code == 503
    data = response.json()
    assert "error" in data


async def test_chat_message_required(client):
    """POST /api/chat sans message -> 400 (parse_json_body required)."""
    with (
        patch("server.handlers.chat_handlers.OPENAI_AVAILABLE", True),
        patch("server.handlers.chat_handlers.settings") as mock_settings,
    ):
        mock_settings.OPENAI_API_KEY = "sk-test"
        response = await client.post("/api/chat", json={})
    assert response.status_code == 400


async def test_chat_stream_openai_unavailable(client):
    """POST /api/chat/stream sans OpenAI -> 200 avec SSE error."""
    with patch("server.handlers.chat_handlers.OPENAI_AVAILABLE", False):
        response = await client.post("/api/chat/stream", json={"message": "Bonjour"})
    assert response.status_code == 200
    text = response.text
    assert "error" in text and "OpenAI" in text


async def test_chat_stream_message_required(client):
    """POST /api/chat/stream sans message -> 200 avec SSE error."""
    with (
        patch("server.handlers.chat_handlers.OPENAI_AVAILABLE", True),
        patch("server.handlers.chat_handlers.settings") as mock_settings,
    ):
        mock_settings.OPENAI_API_KEY = "sk-test"
        response = await client.post("/api/chat/stream", json={})
    assert response.status_code == 200
    text = response.text
    assert "error" in text and "Message requis" in text


async def test_chat_unsafe_prompt_rejected(client):
    """POST /api/chat avec prompt invalide (safety) -> 400."""
    with (
        patch("server.handlers.chat_handlers.OPENAI_AVAILABLE", True),
        patch("server.handlers.chat_handlers.settings") as mock_settings,
        patch(
            "app.utils.prompt_sanitizer.validate_prompt_safety",
            return_value=(False, "Contenu bloqué"),
        ),
    ):
        mock_settings.OPENAI_API_KEY = "sk-test"
        response = await client.post(
            "/api/chat", json={"message": "prompt malveillant"}
        )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "invalide" in data["error"].lower() and "bloqué" in data["error"].lower()
