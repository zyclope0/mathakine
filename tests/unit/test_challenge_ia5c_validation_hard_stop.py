"""IA5c — pas de persistance ni d'événement challenge si validation finale KO après auto-correction KO."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.services.challenges.challenge_ai_service import generate_challenge_stream


@pytest.mark.asyncio
async def test_validation_hard_stop_no_challenge_event_no_persist():
    """Validation KO + auto-correction KO → error SSE, done, pas de type challenge, pas de persistance."""

    async def fake_chunks():
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock(
            content='{"title":"T","description":"D","correct_answer":"x"}'
        )
        chunk.usage = None
        yield chunk

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create = AsyncMock(return_value=fake_chunks())

    events: list[str] = []

    async def capture_run_db_bound(_fn, *_args, **_kwargs):
        raise AssertionError("persist must not be called when validation hard-stops")

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-ia5c"),
        # Surcharge le blocage session conftest sur openai.AsyncOpenAI
        patch(
            "openai.AsyncOpenAI",
            return_value=mock_client_instance,
        ),
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
            side_effect=lambda d: d,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
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

    parsed = []
    for line in events:
        if line.startswith("data: "):
            try:
                parsed.append(json.loads(line[6:].strip()))
            except json.JSONDecodeError:
                pass

    types_found = [p.get("type") for p in parsed]
    assert "challenge" not in types_found
    assert "error" in types_found
    assert types_found[-1] == "done"
