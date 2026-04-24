"""Sûreté des erreurs SSE pour le flux défis IA."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from openai import RateLimitError

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.services.challenges.challenge_ai_service import (
    CHALLENGE_AI_GENERIC_ERROR_MESSAGE,
    CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE,
    generate_challenge_stream,
)
from app.utils.circuit_breaker import openai_workload_circuit_breaker


def _parse_sse_payloads(events: list[str]) -> list[dict]:
    payloads: list[dict] = []
    for line in events:
        if not line.startswith("data: "):
            continue
        payloads.append(json.loads(line[6:]))
    return payloads


def _rate_limit_error(message: str = "secret quota detail") -> RateLimitError:
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(429, request=request)
    return RateLimitError(message, response=response, body={"detail": message})


def _build_stream_chunk(content: str) -> MagicMock:
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta = MagicMock(content=content)
    chunk.usage = None
    return chunk


async def _yield_chunks(*chunks: MagicMock):
    for chunk in chunks:
        yield chunk


@pytest.mark.asyncio
async def test_generate_challenge_stream_transient_failure_uses_safe_message():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=_rate_limit_error("secret rate limit detail")
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-safe"),
        patch.object(AIConfig, "MAX_RETRIES", 2),
        patch.object(AIConfig, "RETRY_BACKOFF_MULTIPLIER", 0.0),
        patch.object(AIConfig, "RETRY_MIN_WAIT", 0.0),
        patch.object(AIConfig, "RETRY_MAX_WAIT", 0.0),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "gpt-4o-mini",
                "max_tokens": 500,
                "timeout": 30,
                "temperature": 0.5,
            },
        ),
    ):
        events: list[str] = []
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    error_payload = next(payload for payload in payloads if payload["type"] == "error")
    assert error_payload["message"] == CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE
    assert mock_client.chat.completions.create.await_count == 2


@pytest.mark.asyncio
async def test_generate_challenge_stream_unexpected_error_uses_safe_message():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(
            _build_stream_chunk(
                json.dumps(
                    {
                        "title": "Défi",
                        "description": "Description",
                        "question": "Question",
                        "correct_answer": "42",
                    }
                )
            )
        )
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-generic"),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "gpt-4o-mini",
                "max_tokens": 500,
                "timeout": 30,
                "temperature": 0.5,
            },
        ),
        patch(
            "app.services.challenges.challenge_ai_service.validate_challenge_logic",
            return_value=(True, []),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.normalize_generated_challenge",
            side_effect=RuntimeError("secret normalization detail"),
        ),
    ):
        events: list[str] = []
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    error_payload = next(payload for payload in payloads if payload["type"] == "error")
    assert error_payload["message"] == CHALLENGE_AI_GENERIC_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_generate_challenge_stream_normalizes_recoverable_difficulty_before_validation():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(
            _build_stream_chunk(
                json.dumps(
                    {
                        "title": "Code César facile",
                        "description": "Décode ce message.",
                        "question": "Quel est le mot ?",
                        "correct_answer": "EUREKA",
                        "difficulty_rating": 4.4,
                        "visual_data": {
                            "type": "caesar",
                            "encoded_message": "HXUHPD",
                            "shift": 3,
                        },
                    }
                )
            )
        )
    )

    normalized_challenge = {
        "challenge_type": "coding",
        "age_group": "15-17",
        "title": "Le message chiffré",
        "description": "Décode ce message.",
        "question": "Quel est le mot ?",
        "correct_answer": "EUREKA",
        "solution_explanation": "Décale les lettres dans le bon sens.",
        "hints": ["Observe le décalage."],
        "visual_data": {
            "type": "caesar",
            "encoded_message": "HXUHPD",
            "shift": 3,
        },
        "difficulty_rating": 3.0,
        "difficulty_tier": None,
        "estimated_time_minutes": 10,
        "tags": "ai,generated,mathélogique",
        "choices": None,
        "response_mode": "open_text",
        "difficulty_calibration": {
            "applied_rules": ["coding_caesar_explicit_shift_cap_3_0"]
        },
    }
    persisted_payloads: list[dict] = []

    def validate_side_effect(payload: dict):
        if float(payload["difficulty_rating"]) >= 4.0:
            return (
                False,
                [
                    "CODING Caesar : un décalage explicite ne justifie pas difficulty_rating >= 4.0."
                ],
            )
        return (True, [])

    async def capture_run_db_bound(_fn, normalized_payload, *_args, **_kwargs):
        persisted_payloads.append(normalized_payload)
        return {"id": 123, **normalized_payload}

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-normalized"),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "gpt-4o-mini",
                "max_tokens": 500,
                "timeout": 30,
                "temperature": 0.5,
            },
        ),
        patch(
            "app.services.challenges.challenge_ai_service.normalize_generated_challenge",
            return_value=normalized_challenge,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.auto_correct_challenge",
            side_effect=lambda payload: payload,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.validate_challenge_logic",
            side_effect=validate_side_effect,
        ) as validate_mock,
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
        ),
    ):
        events: list[str] = []
        async for line in generate_challenge_stream(
            challenge_type="coding",
            age_group="15-17",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    joined = "\n".join(events)
    assert '"type": "error"' not in joined
    assert '"type": "challenge"' in joined
    assert persisted_payloads
    assert persisted_payloads[0]["difficulty_rating"] == 3.0
    assert validate_mock.call_count >= 1
    assert validate_mock.call_args_list[0].args[0]["difficulty_rating"] == 3.0


@pytest.mark.asyncio
async def test_o_series_fallback_non_countable_failure_yields_safe_error_and_stops():
    """Fallback après stream vide : exception hors famille OpenAI countable → SSE erreur, pas de succès."""

    async def stream_no_text():
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock(content=None)
        chunk.choices[0].finish_reason = None
        chunk.usage = MagicMock(prompt_tokens=321, completion_tokens=0)
        yield chunk

    main_client = MagicMock()
    main_client.chat.completions.create = AsyncMock(return_value=stream_no_text())
    fallback_client = MagicMock()
    fallback_client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("secret fallback transport")
    )
    clients: list[MagicMock] = [main_client, fallback_client]
    track_calls: list[dict] = []

    def openai_factory(*_a, **_kw) -> MagicMock:
        return clients.pop(0)

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-o-series-fallback-fail"),
        patch("openai.AsyncOpenAI", side_effect=openai_factory),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "o4-mini",
                "max_tokens": 500,
                "timeout": 30,
                "temperature": 0.5,
                "reasoning_effort": "medium",
            },
        ),
        patch.object(AIConfig, "MAX_RETRIES", 2),
        patch.object(AIConfig, "RETRY_BACKOFF_MULTIPLIER", 0.0),
        patch.object(AIConfig, "RETRY_MIN_WAIT", 0.0),
        patch.object(AIConfig, "RETRY_MAX_WAIT", 0.0),
        patch.object(openai_workload_circuit_breaker, "record_success") as record_ok,
        patch(
            "app.services.challenges.challenge_ai_service.token_tracker.track_usage",
            side_effect=lambda **kwargs: track_calls.append(kwargs) or kwargs,
        ),
    ):
        events: list[str] = []
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    assert payloads[-1]["type"] == "error"
    assert payloads[-1]["message"] == CHALLENGE_AI_GENERIC_ERROR_MESSAGE
    assert not any(p.get("type") == "challenge" for p in payloads)
    record_ok.assert_not_called()
    assert len(track_calls) == 1
    assert track_calls[0]["model"] == "o4-mini"
    assert track_calls[0]["challenge_type"] == "sequence"
    assert track_calls[0]["prompt_tokens"] == 321
    assert track_calls[0]["completion_tokens"] == 0
