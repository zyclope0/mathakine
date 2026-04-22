"""Rattrapage review IA 2026-03-22 — honnêteté du tracking OpenAI sur les défis."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.services.challenges.challenge_ai_service import generate_challenge_stream


def _build_stream_chunk(
    *,
    content: str | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    finish_reason: str | None = None,
) -> MagicMock:
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta = MagicMock(content=content)
    chunk.choices[0].finish_reason = finish_reason
    if prompt_tokens is None and completion_tokens is None:
        chunk.usage = None
    else:
        usage = MagicMock()
        usage.prompt_tokens = prompt_tokens
        usage.completion_tokens = completion_tokens
        chunk.usage = usage
    return chunk


async def _yield_chunks(*chunks: MagicMock):
    for chunk in chunks:
        yield chunk


@pytest.mark.asyncio
async def test_validation_hard_stop_still_tracks_primary_usage() -> None:
    async def capture_run_db_bound(_fn, *_args, **_kwargs):
        raise AssertionError("persist must not be called when validation hard-stops")

    primary_client = MagicMock()
    primary_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(
            _build_stream_chunk(
                content='{"title":"T","description":"D","correct_answer":"7"}'
            )
        )
    )
    track_calls: list[dict[str, Any]] = []
    events: list[str] = []

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-usage"),
        patch("openai.AsyncOpenAI", return_value=primary_client),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "gpt-4o-mini",
                "max_tokens": 500,
                "timeout": 60,
                "temperature": 0.5,
            },
        ),
        patch(
            "app.services.challenges.challenge_ai_service.validate_challenge_logic",
            return_value=(False, ["erreur_validation"]),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.auto_correct_challenge",
            side_effect=lambda payload: payload,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.token_tracker.track_usage",
            side_effect=lambda **kwargs: track_calls.append(kwargs) or kwargs,
        ),
    ):
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    joined = "\n".join(events)
    assert '"type": "challenge"' not in joined
    assert '"type": "error"' in joined

    assert len(track_calls) == 1
    assert track_calls[0]["challenge_type"] == "sequence"
    assert track_calls[0]["model"] == "gpt-4o-mini"
    assert track_calls[0]["prompt_tokens"] > 0
    assert track_calls[0]["completion_tokens"] > 0


@pytest.mark.asyncio
async def test_empty_o3_stream_and_fallback_track_separate_usage_events() -> None:
    primary_client = MagicMock()
    primary_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(_build_stream_chunk(content=None))
    )
    fallback_response = MagicMock()
    fallback_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "title": "Défi",
                        "description": "Description",
                        "question": "Question",
                        "correct_answer": "42",
                    }
                )
            )
        )
    ]
    fallback_response.usage = MagicMock(prompt_tokens=111, completion_tokens=37)

    fallback_client = MagicMock()
    fallback_client.chat.completions.create = AsyncMock(return_value=fallback_response)

    track_calls: list[dict[str, Any]] = []
    events: list[str] = []

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-fallback"),
        patch("openai.AsyncOpenAI", side_effect=[primary_client, fallback_client]),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "o3",
                "max_tokens": 500,
                "timeout": 60,
                "reasoning_effort": "medium",
            },
        ),
        patch(
            "app.services.challenges.challenge_ai_service.resolve_challenge_ai_fallback_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.challenges.challenge_ai_service.validate_challenge_logic",
            return_value=(True, []),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            new=AsyncMock(
                return_value={"id": 99, "title": "Défi", "description": "Description"}
            ),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.token_tracker.track_usage",
            side_effect=lambda **kwargs: track_calls.append(kwargs) or kwargs,
        ),
    ):
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test fallback",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    joined = "\n".join(events)
    assert '"type": "challenge"' in joined

    assert len(track_calls) == 2
    assert track_calls[0]["model"] == "o3"
    assert track_calls[0]["challenge_type"] == "sequence"
    assert track_calls[1]["model"] == "gpt-4o-mini"
    assert track_calls[1]["prompt_tokens"] == 111
    assert track_calls[1]["completion_tokens"] == 37


@pytest.mark.asyncio
async def test_persistence_warning_is_recorded_in_generation_metrics() -> None:
    primary_client = MagicMock()
    primary_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(
            _build_stream_chunk(
                content=json.dumps(
                    {
                        "title": "Défi",
                        "description": "Description",
                        "question": "Question",
                        "correct_answer": "5",
                    }
                )
            )
        )
    )
    metric_calls: list[dict[str, Any]] = []
    events: list[str] = []

    def _capture_metric(**kwargs):
        metric_calls.append(kwargs)

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-persist-warning"),
        patch("openai.AsyncOpenAI", return_value=primary_client),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "gpt-4o-mini",
                "max_tokens": 500,
                "timeout": 60,
                "temperature": 0.5,
            },
        ),
        patch(
            "app.services.challenges.challenge_ai_service.validate_challenge_logic",
            return_value=(True, []),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.token_tracker.track_usage",
            return_value={"tokens": 10, "cost": 0.01},
        ),
        patch(
            "app.services.challenges.challenge_ai_service.generation_metrics.record_generation",
            side_effect=_capture_metric,
        ),
    ):
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="persist warning",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    assert any('"type": "challenge"' in line and '"warning"' in line for line in events)
    assert any(
        call.get("error_type") == "challenge_persistence_missing_id"
        and call.get("success") is False
        and call.get("validation_passed") is True
        for call in metric_calls
    )


@pytest.mark.asyncio
async def test_o_series_length_truncation_triggers_fallback_on_challenges() -> None:
    """Lot I — sur o-series, ``finish_reason=length`` déclenche aussi le fallback.

    Avant ce lot : le fallback ne fired que si la réponse était *totalement* vide ;
    un JSON partiellement écrit mais tronqué au token limit passait directement
    au parseur, qui échouait en business validation. Ce test verrouille le bump.
    """
    # Le primary stream émet du contenu partiel puis signale finish_reason=length.
    primary_client = MagicMock()
    primary_client.chat.completions.create = AsyncMock(
        return_value=_yield_chunks(
            _build_stream_chunk(content='{"title":"Partial JSON'),
            _build_stream_chunk(finish_reason="length"),
        )
    )

    fallback_response = MagicMock()
    fallback_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "title": "Défi complet",
                        "description": "Description",
                        "question": "Question",
                        "correct_answer": "42",
                    }
                )
            )
        )
    ]
    fallback_response.usage = MagicMock(prompt_tokens=120, completion_tokens=50)

    fallback_client = MagicMock()
    fallback_client.chat.completions.create = AsyncMock(return_value=fallback_response)

    track_calls: list[dict[str, Any]] = []
    events: list[str] = []

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-challenge-length-fallback"),
        patch("openai.AsyncOpenAI", side_effect=[primary_client, fallback_client]),
        patch.object(
            AIConfig,
            "get_openai_params",
            return_value={
                "model": "o4-mini",
                "max_tokens": 500,
                "timeout": 60,
                "reasoning_effort": "medium",
            },
        ),
        patch(
            "app.services.challenges.challenge_ai_service.resolve_challenge_ai_fallback_model",
            return_value="gpt-4o-mini",
        ),
        patch(
            "app.services.challenges.challenge_ai_service.validate_challenge_logic",
            return_value=(True, []),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            new=AsyncMock(
                return_value={
                    "id": 101,
                    "title": "Défi complet",
                    "description": "Description",
                }
            ),
        ),
        patch(
            "app.services.challenges.challenge_ai_service.token_tracker.track_usage",
            side_effect=lambda **kwargs: track_calls.append(kwargs) or kwargs,
        ),
    ):
        async for line in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test fallback on truncation",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    joined = "\n".join(events)
    # Le fallback a produit un défi valide → émission finale ``type=challenge``.
    assert '"type": "challenge"' in joined
    # Usage tracké pour les DEUX modèles : primary (tronqué) + fallback.
    models_seen = {call["model"] for call in track_calls}
    assert "o4-mini" in models_seen
    assert "gpt-4o-mini" in models_seen
