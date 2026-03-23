"""Résilience et sûreté des erreurs SSE pour le flux exercices IA."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from openai import APITimeoutError

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.services.exercises.exercise_ai_service import (
    EXERCISE_AI_GENERIC_ERROR_MESSAGE,
    EXERCISE_AI_TRANSIENT_ERROR_MESSAGE,
    generate_exercise_stream,
)


def _parse_sse_payloads(events: list[str]) -> list[dict]:
    payloads: list[dict] = []
    for line in events:
        if not line.startswith("data: "):
            continue
        payloads.append(json.loads(line[6:]))
    return payloads


def _valid_ai_exercise_json() -> str:
    return json.dumps(
        {
            "title": "Titre test",
            "question": "Question assez longue pour passer le validateur metier sans souci.",
            "correct_answer": "2",
            "choices": ["2", "3", "4", "5"],
            "explanation": "E" * 45,
            "hint": "Un indice assez long pour guider sans reveler la solution finale ici.",
        }
    )


def _build_stream_chunk(content: str) -> MagicMock:
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = content
    chunk.usage = None
    return chunk


async def _yield_chunks(*chunks: MagicMock):
    for chunk in chunks:
        yield chunk


def _timeout_error(message: str = "transient secret detail") -> APITimeoutError:
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    error = APITimeoutError(request=request)
    error.args = (message,)
    return error


@pytest.mark.asyncio
async def test_generate_exercise_stream_retries_transient_openai_error_then_succeeds():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            _timeout_error(),
            _yield_chunks(_build_stream_chunk(_valid_ai_exercise_json())),
        ]
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-exercise-retry"),
        patch.object(AIConfig, "MAX_RETRIES", 2),
        patch.object(AIConfig, "RETRY_BACKOFF_MULTIPLIER", 0.0),
        patch.object(AIConfig, "RETRY_MIN_WAIT", 0.0),
        patch.object(AIConfig, "RETRY_MAX_WAIT", 0.0),
        patch("openai.AsyncOpenAI", return_value=mock_client) as openai_ctor,
        patch(
            "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
            return_value={"model": "gpt-4o-mini", "messages": [], "stream": True},
        ),
        patch(
            "app.services.exercises.exercise_ai_service.run_db_bound",
            new=AsyncMock(return_value=123),
        ),
        patch(
            "app.services.exercises.exercise_ai_service.token_tracker.track_usage",
            return_value={"tokens": 10, "cost": 0.01},
        ),
    ):
        events: list[str] = []
        async for line in generate_exercise_stream(
            "addition", "6-8", "INITIE", "", locale="fr"
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    assert any(payload.get("type") == "exercise" for payload in payloads)
    assert payloads[-1].get("type") == "done"
    assert sum(1 for p in payloads if p.get("type") == "done") == 1
    assert mock_client.chat.completions.create.await_count == 2
    assert openai_ctor.call_args.kwargs["timeout"] == AIConfig.DEFAULT_TIMEOUT


@pytest.mark.asyncio
async def test_generate_exercise_stream_transient_failure_uses_safe_message():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=_timeout_error("secret upstream timeout detail")
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-exercise-timeout"),
        patch.object(AIConfig, "MAX_RETRIES", 2),
        patch.object(AIConfig, "RETRY_BACKOFF_MULTIPLIER", 0.0),
        patch.object(AIConfig, "RETRY_MIN_WAIT", 0.0),
        patch.object(AIConfig, "RETRY_MAX_WAIT", 0.0),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch(
            "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
            return_value={"model": "gpt-4o-mini", "messages": [], "stream": True},
        ),
    ):
        events: list[str] = []
        async for line in generate_exercise_stream(
            "addition", "6-8", "INITIE", "", locale="fr"
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    error_payload = next(payload for payload in payloads if payload["type"] == "error")
    assert error_payload["message"] == EXERCISE_AI_TRANSIENT_ERROR_MESSAGE
    assert mock_client.chat.completions.create.await_count == 2


@pytest.mark.asyncio
async def test_generate_exercise_stream_unexpected_error_uses_safe_message():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(_build_stream_chunk(_valid_ai_exercise_json()))
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-exercise-generic"),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch(
            "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
            return_value={"model": "gpt-4o-mini", "messages": [], "stream": True},
        ),
        patch(
            "app.services.exercises.exercise_ai_service.sanitize_exercise_text_fields",
            side_effect=RuntimeError("secret internal stack detail"),
        ),
    ):
        events: list[str] = []
        async for line in generate_exercise_stream(
            "addition", "6-8", "INITIE", "", locale="fr"
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    error_payload = next(payload for payload in payloads if payload["type"] == "error")
    assert error_payload["message"] == EXERCISE_AI_GENERIC_ERROR_MESSAGE
    assert not any(p.get("type") == "done" for p in payloads)


@pytest.mark.asyncio
async def test_generate_exercise_stream_validation_failure_yields_error_then_done():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(_build_stream_chunk(_valid_ai_exercise_json()))
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-exercise-validation"),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch(
            "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
            return_value={"model": "gpt-4o-mini", "messages": [], "stream": True},
        ),
        patch(
            "app.services.exercises.exercise_ai_service.validate_exercise_ai_output",
            return_value=(False, ["question_trop_courte"]),
        ),
        patch(
            "app.services.exercises.exercise_ai_service.format_validation_error_message",
            return_value="Message validation test",
        ),
        patch(
            "app.services.exercises.exercise_ai_service.token_tracker.track_usage",
            return_value={"tokens": 10, "cost": 0.01},
        ),
    ):
        events: list[str] = []
        async for line in generate_exercise_stream(
            "addition", "6-8", "INITIE", "", locale="fr"
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    types = [p.get("type") for p in payloads]
    assert "error" in types
    assert types[-1] == "done"
    assert sum(1 for t in types if t == "done") == 1
    err = next(p for p in payloads if p.get("type") == "error")
    assert err.get("message") == "Message validation test"
