"""Politique applicative exercices IA : résolution modèle, matrice, kwargs OpenAI."""

import pytest

from app.core.ai_generation_policy import (
    DEFAULT_EXERCISES_AI_MODEL,
    EXERCISES_AI_ALLOWED_MODEL_IDS,
    MODEL_FAMILY_CAPABILITIES,
    ExerciseAIModelFamily,
    ExerciseAIModelNotAllowedError,
    build_exercise_ai_stream_kwargs,
    classify_exercise_ai_model_family,
    get_model_family_capabilities,
    max_completion_tokens_for_exercise_type,
    normalize_exercise_ai_model_id,
    reasoning_effort_for_exercise_type,
    resolve_exercise_ai_model,
    resolve_exercise_ai_model_for_user,
)
from app.core.config import settings


def test_default_model_and_allowlist_coherent() -> None:
    assert DEFAULT_EXERCISES_AI_MODEL in EXERCISES_AI_ALLOWED_MODEL_IDS


@pytest.mark.parametrize(
    "model_id,expected",
    [
        ("o1", ExerciseAIModelFamily.O1),
        ("o1-mini", ExerciseAIModelFamily.O1),
        ("O3", ExerciseAIModelFamily.O3),
        ("o3-mini", ExerciseAIModelFamily.O3),
        ("gpt-5.1", ExerciseAIModelFamily.GPT5),
        ("gpt-5.4", ExerciseAIModelFamily.GPT5),
        ("gpt-5-mini", ExerciseAIModelFamily.GPT5),
        ("gpt5-nano", ExerciseAIModelFamily.GPT5),
        ("gpt-4o-mini", ExerciseAIModelFamily.CHAT_CLASSIC),
    ],
)
def test_classify_exercise_ai_model_family(
    model_id: str, expected: ExerciseAIModelFamily
) -> None:
    assert classify_exercise_ai_model_family(model_id) is expected


def test_model_family_capabilities_matrix_covers_all_families() -> None:
    for fam in ExerciseAIModelFamily:
        caps = get_model_family_capabilities(fam)
        assert caps is MODEL_FAMILY_CAPABILITIES[fam]
    o1 = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.O1]
    assert o1.supports_response_format_json_object is False
    o3 = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.O3]
    assert o3.supports_reasoning_effort is True
    g5 = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.GPT5]
    assert g5.supports_verbosity is True
    chat = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.CHAT_CLASSIC]
    assert chat.supports_temperature is True


def test_resolve_default_is_policy_o3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert resolve_exercise_ai_model() == DEFAULT_EXERCISES_AI_MODEL == "o3"


def test_resolve_override_beats_legacy_exercises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "gpt-5-mini")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "o3-mini")
    assert resolve_exercise_ai_model() == "gpt-5-mini"


def test_resolve_legacy_openai_model_exercises_when_override_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "o3-mini")
    assert resolve_exercise_ai_model() == "o3-mini"


def test_resolve_rejects_typo_model_not_in_allowlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "gpt-4o-mni")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    with pytest.raises(ExerciseAIModelNotAllowedError, match="non autorisé"):
        resolve_exercise_ai_model()


def test_classify_rejects_unknown_model_not_chat_fallback() -> None:
    with pytest.raises(ExerciseAIModelNotAllowedError, match="non autorisé"):
        classify_exercise_ai_model_family("claude-3-opus")


def test_classify_rejects_gpt4_bare_if_not_allowlisted() -> None:
    with pytest.raises(ExerciseAIModelNotAllowedError, match="non autorisé"):
        classify_exercise_ai_model_family("gpt-4")


def test_build_stream_kwargs_rejects_unlisted_model() -> None:
    with pytest.raises(ExerciseAIModelNotAllowedError, match="non autorisé"):
        build_exercise_ai_stream_kwargs(
            model="o4-mini",
            exercise_type="addition",
            system_content="s",
            user_content="u",
        )


def test_resolve_explicit_o1_override_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "o1-mini")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert resolve_exercise_ai_model() == "o1-mini"


def test_resolve_exercise_ai_model_for_user_delegates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert resolve_exercise_ai_model_for_user(99, "addition") == "o3"


def test_reasoning_effort_and_max_tokens_by_type() -> None:
    assert reasoning_effort_for_exercise_type("addition") == "low"
    assert reasoning_effort_for_exercise_type("mixte") == "high"
    assert reasoning_effort_for_exercise_type("unknown_type") == "medium"
    assert max_completion_tokens_for_exercise_type("addition") == 2800
    assert max_completion_tokens_for_exercise_type("mixte") == 5000
    assert max_completion_tokens_for_exercise_type("unknown") == 4000


def test_build_stream_kwargs_o3_family() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="o3",
        exercise_type="addition",
        system_content="sys",
        user_content="user",
    )
    assert kw["model"] == "o3"
    assert kw["stream_options"] == {"include_usage": True}
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["reasoning_effort"] == "low"
    assert kw["max_completion_tokens"] == 2800
    assert "temperature" not in kw
    assert "verbosity" not in kw


def test_build_stream_kwargs_o1_family() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="o1-mini",
        exercise_type="fractions",
        system_content="sys",
        user_content="user",
    )
    assert kw["model"] == "o1-mini"
    assert "response_format" not in kw
    assert "reasoning_effort" not in kw
    assert kw["max_completion_tokens"] == 4500


def test_build_stream_kwargs_gpt5_family() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="gpt-5-mini",
        exercise_type="mixte",
        system_content="sys",
        user_content="user",
    )
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["reasoning_effort"] == "high"
    assert kw["verbosity"] == "low"
    assert "temperature" not in kw


def test_build_stream_kwargs_gpt5_temperature_when_reasoning_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.core.ai_generation_policy.reasoning_effort_for_exercise_type",
        lambda _et: "none",
    )
    kw = build_exercise_ai_stream_kwargs(
        model="gpt-5.1",
        exercise_type="addition",
        system_content="s",
        user_content="u",
    )
    assert kw["temperature"] == 0.7


def test_build_stream_kwargs_chat_classic_family() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="gpt-4o-mini",
        exercise_type="addition",
        system_content="sys",
        user_content="user",
    )
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["temperature"] == 0.7
    assert "reasoning_effort" not in kw
