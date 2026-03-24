"""Tests causaux du circuit-breaker OpenAI (P5) et intégration SSE minimale."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from openai import APITimeoutError, BadRequestError

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.services.challenges.challenge_ai_service import generate_challenge_stream
from app.services.exercises.exercise_ai_service import generate_exercise_stream
from app.utils.circuit_breaker import (
    OPENAI_CIRCUIT_COOLDOWN_SECONDS,
    OPENAI_CIRCUIT_FAILURE_THRESHOLD,
    OPENAI_CIRCUIT_FAILURE_WINDOW_SECONDS,
    OPENAI_CIRCUIT_OPEN_USER_MESSAGE,
    OpenAiWorkloadCircuitBreaker,
    is_countable_openai_failure,
    openai_workload_circuit_breaker,
)


@pytest.fixture(autouse=True)
def _reset_openai_circuit_breaker():
    openai_workload_circuit_breaker.reset_for_testing()
    yield
    openai_workload_circuit_breaker.reset_for_testing()


def test_openai_breaker_opens_after_threshold_failures_in_window():
    clock = {"t": 0.0}

    def time_fn() -> float:
        return clock["t"]

    cb = OpenAiWorkloadCircuitBreaker(
        failure_threshold=3,
        failure_window_s=100.0,
        cooldown_s=50.0,
        time_fn=time_fn,
    )

    for i in range(3):
        assert cb.check_allow() is True
        cb.record_countable_failure()
        clock["t"] += 1.0

    assert cb.check_allow() is False

    clock["t"] += 51.0
    assert cb.check_allow() is True
    assert cb.check_allow() is False

    cb.record_success()
    assert cb.check_allow() is True


def test_openai_breaker_half_open_failure_reopens():
    clock = {"t": 200.0}

    def time_fn() -> float:
        return clock["t"]

    cb = OpenAiWorkloadCircuitBreaker(
        failure_threshold=2,
        failure_window_s=100.0,
        cooldown_s=10.0,
        time_fn=time_fn,
    )

    assert cb.check_allow() is True
    cb.record_countable_failure()
    assert cb.check_allow() is True
    cb.record_countable_failure()
    assert cb.check_allow() is False

    clock["t"] += 11.0
    assert cb.check_allow() is True
    cb.record_countable_failure()
    assert cb.check_allow() is False


def test_is_countable_timeout_vs_bad_request():
    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    resp_400 = httpx.Response(400, request=req)
    assert is_countable_openai_failure(APITimeoutError(request=req)) is True
    assert (
        is_countable_openai_failure(
            BadRequestError("bad", response=resp_400, body=None)
        )
        is False
    )


def test_default_constants_match_backlog_example():
    assert OPENAI_CIRCUIT_FAILURE_THRESHOLD == 5
    assert OPENAI_CIRCUIT_FAILURE_WINDOW_SECONDS == 120.0
    assert OPENAI_CIRCUIT_COOLDOWN_SECONDS == 60.0


def _parse_sse_payloads(events: list[str]) -> list[dict]:
    out: list[dict] = []
    for line in events:
        if line.startswith("data: "):
            out.append(json.loads(line[6:]))
    return out


def _build_stream_chunk(content: str) -> MagicMock:
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = content
    chunk.usage = None
    return chunk


async def _yield_chunks(*chunks: MagicMock):
    for c in chunks:
        yield c


@pytest.mark.asyncio
async def test_generate_exercise_stream_circuit_open_skips_openai():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(_build_stream_chunk("{}"))
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-circuit"),
        patch(
            "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
            return_value={"model": "gpt-4o-mini", "messages": [], "stream": True},
        ),
        patch(
            "app.services.exercises.exercise_ai_service.openai_workload_circuit_breaker.check_allow",
            return_value=False,
        ),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch(
            "app.services.exercises.exercise_ai_service.generation_metrics.record_generation",
        ) as rec,
    ):
        events: list[str] = []
        async for line in generate_exercise_stream(
            "addition", "6-8", "INITIE", "", locale="fr"
        ):
            events.append(line)

    payloads = _parse_sse_payloads(events)
    err = next(p for p in payloads if p.get("type") == "error")
    assert err.get("message") == OPENAI_CIRCUIT_OPEN_USER_MESSAGE
    mock_client.chat.completions.create.assert_not_called()
    assert any(
        getattr(c, "kwargs", {}).get("error_type") == "openai_circuit_open"
        for c in rec.call_args_list
    )


@pytest.mark.asyncio
async def test_generate_challenge_stream_circuit_open_skips_openai():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(_build_stream_chunk("{}"))
    )

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-circuit"),
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
            "app.services.challenges.challenge_ai_service.openai_workload_circuit_breaker.check_allow",
            return_value=False,
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
    err = next(p for p in payloads if p.get("type") == "error")
    assert err.get("message") == OPENAI_CIRCUIT_OPEN_USER_MESSAGE
    mock_client.chat.completions.create.assert_not_called()
