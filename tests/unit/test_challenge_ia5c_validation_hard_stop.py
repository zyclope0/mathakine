"""IA5c — pas de persistance ni d'événement challenge si validation finale KO après auto-correction KO."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.services.challenges.challenge_ai_service import (
    CHALLENGE_GENERATION_STATUS_ACCEPTED,
    CHALLENGE_GENERATION_STATUS_REJECTED,
    CHALLENGE_GENERATION_STATUS_REPAIRED,
    CHALLENGE_GENERATION_STATUS_REPAIRED_BY_AI,
    generate_challenge_stream,
)


def _stream_chunk_json(obj: dict) -> MagicMock:
    async def fake_chunks():
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock(content=json.dumps(obj))
        chunk.usage = None
        yield chunk

    return fake_chunks()


@pytest.mark.asyncio
async def test_validation_hard_stop_no_challenge_event_no_persist():
    """Validation KO + auto-correction KO → error SSE, done, pas de type challenge, pas de persistance."""

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create = AsyncMock(
        return_value=_stream_chunk_json(
            {"title": "T", "description": "D", "correct_answer": "x"}
        )
    )

    events: list[str] = []

    async def capture_run_db_bound(_fn, *_args, **_kwargs):
        raise AssertionError("persist must not be called when validation hard-stops")

    auto_correct = MagicMock(side_effect=lambda d: d)

    record_gen = MagicMock()
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
            new=auto_correct,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.generation_metrics.record_generation",
            record_gen,
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

    assert auto_correct.call_count == 1
    assert record_gen.call_count == 1
    kw = record_gen.call_args.kwargs
    assert kw["success"] is False
    assert kw["generation_status"] == CHALLENGE_GENERATION_STATUS_REJECTED
    assert kw["error_type"] == "validation_failed_after_autocorrect"
    assert kw.get("error_codes") == ["validation_unknown"]

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


@pytest.mark.asyncio
async def test_single_generic_autocorrect_then_valid_emits_challenge():
    """Une seule passe auto_correct avant validation; si valide, challenge émis normalement."""

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create = AsyncMock(
        return_value=_stream_chunk_json(
            {"title": "T", "description": "D", "correct_answer": "x"}
        )
    )

    auto_correct = MagicMock(side_effect=lambda d: d)

    async def capture_run_db_bound(_fn, normalized_payload, *_args, **_kwargs):
        return {"id": 42, **normalized_payload}

    events: list[str] = []
    record_gen = MagicMock()

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-ia5c-one-pass"),
        patch("openai.AsyncOpenAI", return_value=mock_client_instance),
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
            "app.services.challenges.challenge_ai_service.auto_correct_challenge",
            new=auto_correct,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.generation_metrics.record_generation",
            record_gen,
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

    assert auto_correct.call_count == 1
    assert record_gen.call_count == 1
    assert record_gen.call_args.kwargs["generation_status"] == (
        CHALLENGE_GENERATION_STATUS_ACCEPTED
    )
    joined = "\n".join(events)
    assert '"type": "challenge"' in joined
    assert '"type": "error"' not in joined


@pytest.mark.asyncio
async def test_autocorrect_changes_payload_tracks_repaired_status():
    """auto_correct modifie le JSON → ``repaired`` si validation OK derrière."""
    base = {
        "title": "T",
        "description": "D",
        "correct_answer": "x",
    }

    def mutating_ac(d):
        o = dict(d)
        o["_ac"] = True
        return o

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create = AsyncMock(
        return_value=_stream_chunk_json(base)
    )
    auto_correct = MagicMock(side_effect=mutating_ac)
    record_gen = MagicMock()

    async def capture_run_db_bound(_fn, normalized_payload, *_args, **_kwargs):
        return {"id": 1, **normalized_payload}

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-ia5c-rep"),
        patch("openai.AsyncOpenAI", return_value=mock_client_instance),
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
            "app.services.challenges.challenge_ai_service.auto_correct_challenge",
            new=auto_correct,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.generation_metrics.record_generation",
            record_gen,
        ),
    ):
        async for _ in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            pass

    assert record_gen.call_count == 1
    assert record_gen.call_args.kwargs["generation_status"] == (
        CHALLENGE_GENERATION_STATUS_REPAIRED
    )
    assert record_gen.call_args.kwargs["success"] is True


@pytest.mark.asyncio
async def test_persistence_missing_id_records_failure_with_pipeline_status():
    """Échec DB après validation OK : success False mais statut pipeline non ``rejected``."""
    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create = AsyncMock(
        return_value=_stream_chunk_json(
            {"title": "T", "description": "D", "correct_answer": "x"}
        )
    )
    record_gen = MagicMock()

    async def persist_none(_fn, *_args, **_kwargs):
        return None

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-ia5c-persist"),
        patch("openai.AsyncOpenAI", return_value=mock_client_instance),
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
            "app.services.challenges.challenge_ai_service.auto_correct_challenge",
            side_effect=lambda d: d,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=persist_none,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.generation_metrics.record_generation",
            record_gen,
        ),
    ):
        async for _ in generate_challenge_stream(
            challenge_type="sequence",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            pass

    assert record_gen.call_count == 1
    kw = record_gen.call_args.kwargs
    assert kw["success"] is False
    assert kw["generation_status"] == CHALLENGE_GENERATION_STATUS_ACCEPTED
    assert kw["error_type"] == "challenge_persistence_missing_id"


@pytest.mark.asyncio
async def test_chess_targeted_repair_after_single_autocorrect_still_invalid():
    """Après une seule auto-correction générique et validation KO, la réparation CHESS reste invoquée."""

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create = AsyncMock(
        return_value=_stream_chunk_json(
            {"title": "T", "description": "D", "correct_answer": "e4"}
        )
    )

    auto_correct = MagicMock(side_effect=lambda d: d)

    validate = MagicMock(
        side_effect=[
            (False, ["roi noir déjà en échec avant le coup"]),
            (True, []),
        ]
    )

    repaired = {
        "title": "T2",
        "description": "D2",
        "correct_answer": "Nf3",
        "challenge_type": "chess",
    }

    repair = AsyncMock(return_value=(repaired, None))

    async def capture_run_db_bound(_fn, normalized_payload, *_args, **_kwargs):
        return {"id": 99, **normalized_payload}

    events: list[str] = []
    record_gen = MagicMock()

    with (
        patch.object(settings, "OPENAI_API_KEY", "sk-test-ia5c-chess"),
        patch("openai.AsyncOpenAI", return_value=mock_client_instance),
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
            new=validate,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.auto_correct_challenge",
            new=auto_correct,
        ),
        patch(
            "app.services.challenges.challenge_ai_service._repair_chess_validation_failure_with_openai",
            new=repair,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.run_db_bound",
            side_effect=capture_run_db_bound,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.generation_metrics.record_generation",
            record_gen,
        ),
    ):
        async for line in generate_challenge_stream(
            challenge_type="chess",
            age_group="9-11",
            prompt="test",
            user_id=1,
            locale="fr",
        ):
            events.append(line)

    assert auto_correct.call_count == 1
    assert record_gen.call_count == 1
    assert record_gen.call_args.kwargs["generation_status"] == (
        CHALLENGE_GENERATION_STATUS_REPAIRED_BY_AI
    )
    assert repair.await_count == 1
    repair_call = repair.call_args.kwargs
    assert repair_call["challenge_data"] is validate.call_args_list[0].args[0]
    assert validate.call_count == 2

    joined = "\n".join(events)
    assert '"type": "challenge"' in joined
