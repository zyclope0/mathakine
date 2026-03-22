"""
IA2b : rate-limit prepare_stream_context sans crash logger ;
échec persistance generate_exercise_stream => SSE error, pas exercise.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import settings
from app.schemas.exercise import GenerateExerciseStreamQuery
from app.services.exercises.exercise_ai_service import generate_exercise_stream
from app.services.exercises.exercise_stream_service import prepare_stream_context


@pytest.fixture
def _stream_query_safe() -> GenerateExerciseStreamQuery:
    return GenerateExerciseStreamQuery(
        exercise_type="addition",
        age_group="6-8",
        prompt="Calcul simple pour enfant",
    )


def test_prepare_stream_context_rate_limit_returns_error_no_exception(
    monkeypatch: pytest.MonkeyPatch,
    _stream_query_safe: GenerateExerciseStreamQuery,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")

    def _blocked(_uid: int):
        return False, "Limite horaire exercices IA (test)."

    monkeypatch.setattr(
        "app.services.exercises.exercise_stream_service.check_exercise_ai_generation_rate_limit",
        _blocked,
    )

    ctx, err = prepare_stream_context(
        _stream_query_safe,
        user_id=42,
        accept_language="fr",
    )
    assert ctx is None
    assert err == "Limite horaire exercices IA (test)."


def _patch_openai_stream(monkeypatch: pytest.MonkeyPatch, json_payload: str) -> None:
    async def _mock_stream():
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = json_payload
        chunk.usage = None
        yield chunk

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=_mock_stream())

    def _async_openai_ctor(**_kwargs):
        return mock_client

    monkeypatch.setattr("openai.AsyncOpenAI", _async_openai_ctor)


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


@pytest.mark.asyncio
async def test_generate_exercise_stream_db_exception_yields_error_not_exercise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
        lambda: "gpt-4o-mini",
    )
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
        lambda **kwargs: {"model": "gpt-4o-mini", "messages": [], "stream": True},
    )
    _patch_openai_stream(monkeypatch, _valid_ai_exercise_json())

    async def _boom(*_a, **_kw):
        raise RuntimeError("db down")

    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.run_db_bound",
        _boom,
    )

    metrics_calls: list = []

    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.generation_metrics.record_generation",
        lambda **kwargs: metrics_calls.append(dict(kwargs)),
    )
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.token_tracker.track_usage",
        lambda **kwargs: None,
    )

    events: list[str] = []
    async for line in generate_exercise_stream(
        "addition", "6-8", "INITIE", "", locale="fr"
    ):
        events.append(line)

    joined = "".join(events)
    assert '"type": "exercise"' not in joined
    assert '"type": "error"' in joined
    assert "enregistrer" in joined.lower() or "Réessayez" in joined

    persist = [c for c in metrics_calls if c.get("error_type") == "persistence_error"]
    assert len(persist) == 1
    assert persist[0]["success"] is False
    assert persist[0]["validation_passed"] is True


@pytest.mark.asyncio
async def test_generate_exercise_stream_no_exercise_id_yields_error_not_exercise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
        lambda: "gpt-4o-mini",
    )
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.build_exercise_ai_stream_kwargs",
        lambda **kwargs: {"model": "gpt-4o-mini", "messages": [], "stream": True},
    )
    _patch_openai_stream(monkeypatch, _valid_ai_exercise_json())

    async def _no_id(*_a, **_kw):
        return None

    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.run_db_bound",
        _no_id,
    )

    metrics_calls: list = []

    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.generation_metrics.record_generation",
        lambda **kwargs: metrics_calls.append(dict(kwargs)),
    )
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.token_tracker.track_usage",
        lambda **kwargs: None,
    )

    events: list[str] = []
    async for line in generate_exercise_stream(
        "addition", "6-8", "INITIE", "", locale="fr"
    ):
        events.append(line)

    joined = "".join(events)
    assert '"type": "exercise"' not in joined
    assert '"type": "error"' in joined

    persist = [c for c in metrics_calls if c.get("error_type") == "persistence_error"]
    assert len(persist) == 1
