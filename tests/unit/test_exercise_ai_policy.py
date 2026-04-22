"""Politique applicative exercices IA : résolution modèle, matrice, kwargs OpenAI."""

import pytest

from app.core.ai_generation_policy import (
    DEFAULT_EXERCISES_AI_MODEL,
    EXERCISES_AI_ALLOWED_MODEL_IDS,
    MODEL_FAMILY_CAPABILITIES,
    VERBOSITY_BY_EXERCISE_TYPE_GPT5,
    ExerciseAIModelFamily,
    ExerciseAIModelNotAllowedError,
    build_exercise_ai_stream_kwargs,
    classify_exercise_ai_model_family,
    get_model_family_capabilities,
    max_completion_tokens_for_exercise_type,
    normalize_exercise_ai_model_id,
    o_series_reasoning_effort_for_exercise_type,
    reasoning_effort_for_exercise_type,
    resolve_exercise_ai_model,
    resolve_exercise_ai_model_for_user,
    verbosity_for_exercise_type_gpt5,
)
from app.core.config import settings


def test_default_model_and_allowlist_coherent() -> None:
    assert DEFAULT_EXERCISES_AI_MODEL in EXERCISES_AI_ALLOWED_MODEL_IDS


@pytest.mark.parametrize(
    "model_id,expected",
    [
        ("o1", ExerciseAIModelFamily.O1),
        ("o1-mini", ExerciseAIModelFamily.O1),
        ("O3", ExerciseAIModelFamily.O_SERIES),
        ("o3-mini", ExerciseAIModelFamily.O_SERIES),
        ("o4-mini", ExerciseAIModelFamily.O_SERIES),
        ("gpt-5.1", ExerciseAIModelFamily.GPT5),
        ("gpt-5.4", ExerciseAIModelFamily.GPT5),
        ("gpt-5-mini", ExerciseAIModelFamily.GPT5),
        ("gpt5-nano", ExerciseAIModelFamily.GPT5),
        ("gpt-4.1", ExerciseAIModelFamily.CHAT_CLASSIC),
        ("gpt-4.1-mini", ExerciseAIModelFamily.CHAT_CLASSIC),
        ("gpt-4.1-nano", ExerciseAIModelFamily.CHAT_CLASSIC),
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
    o_series = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.O_SERIES]
    assert o_series.supports_reasoning_effort is True
    g5 = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.GPT5]
    assert g5.supports_verbosity is True
    chat = MODEL_FAMILY_CAPABILITIES[ExerciseAIModelFamily.CHAT_CLASSIC]
    assert chat.supports_temperature is True


def test_resolve_default_is_policy_o4_mini(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert resolve_exercise_ai_model() == DEFAULT_EXERCISES_AI_MODEL == "o4-mini"


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


def test_build_stream_kwargs_o4_mini_uses_reasoning_series() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="o4-mini",
        exercise_type="geometrie",
        system_content="s",
        user_content="u",
    )
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["reasoning_effort"] == "medium"
    # o-series : budget ×1.4 pour compenser les reasoning tokens cachés.
    assert kw["max_completion_tokens"] == int(3200 * 1.4)


def test_build_stream_kwargs_o4_mini_mixte_caps_hidden_reasoning_budget() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="o4-mini",
        exercise_type="mixte",
        system_content="s",
        user_content="u",
    )
    assert kw["reasoning_effort"] == "medium"
    # o-series : budget ×1.4 pour compenser les reasoning tokens cachés.
    assert kw["max_completion_tokens"] == int(6500 * 1.4)


def test_resolve_explicit_o1_override_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "o1-mini")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert resolve_exercise_ai_model() == "o1-mini"


def test_resolve_exercise_ai_model_for_user_delegates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert resolve_exercise_ai_model_for_user(99, "addition") == "o4-mini"


def test_reasoning_effort_and_max_tokens_by_type() -> None:
    assert reasoning_effort_for_exercise_type("addition") == "low"
    assert reasoning_effort_for_exercise_type("geometrie") == "medium"
    assert reasoning_effort_for_exercise_type("mixte") == "high"
    assert o_series_reasoning_effort_for_exercise_type("mixte") == "medium"
    assert reasoning_effort_for_exercise_type("unknown_type") == "medium"
    # Base (sans modèle) — valeurs historiques.
    assert max_completion_tokens_for_exercise_type("addition") == 2800
    assert max_completion_tokens_for_exercise_type("geometrie") == 3200
    assert max_completion_tokens_for_exercise_type("mixte") == 6500
    assert max_completion_tokens_for_exercise_type("unknown") == 4000


def test_max_completion_tokens_applies_o_series_multiplier_when_model_provided() -> (
    None
):
    # o4-mini / o3 → multiplicateur ×1.4 pour compenser les reasoning tokens.
    assert max_completion_tokens_for_exercise_type("addition", model="o4-mini") == int(
        2800 * 1.4
    )
    assert max_completion_tokens_for_exercise_type("mixte", model="o3") == int(
        6500 * 1.4
    )
    assert max_completion_tokens_for_exercise_type("geometrie", model="o3-mini") == int(
        3200 * 1.4
    )


def test_max_completion_tokens_no_multiplier_for_non_o_series_families() -> None:
    # Chat classique, GPT-5 et o1 : pas de bump dans ce lot (non-goal explicite).
    assert (
        max_completion_tokens_for_exercise_type("addition", model="gpt-4o-mini") == 2800
    )
    assert (
        max_completion_tokens_for_exercise_type("addition", model="gpt-4.1-mini")
        == 2800
    )
    assert (
        max_completion_tokens_for_exercise_type("addition", model="gpt-5-mini") == 2800
    )
    assert max_completion_tokens_for_exercise_type("fractions", model="o1") == 4500


def test_max_completion_tokens_fails_open_on_unknown_model() -> None:
    # Garde-fou : un modèle hors allowlist ne doit pas casser, juste renvoyer la base.
    assert (
        max_completion_tokens_for_exercise_type("addition", model="unknown-model-xyz")
        == 2800
    )
    assert max_completion_tokens_for_exercise_type("addition", model="") == 2800


def test_build_stream_kwargs_o3_geometrie_uses_medium_reasoning_effort() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="o3",
        exercise_type="geometrie",
        system_content="sys",
        user_content="user",
    )
    assert kw["reasoning_effort"] == "medium"
    # o-series : budget multiplié ×1.4 pour compenser les reasoning tokens cachés.
    assert kw["max_completion_tokens"] == int(3200 * 1.4)


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
    # o-series : budget multiplié ×1.4.
    assert kw["max_completion_tokens"] == int(2800 * 1.4)
    assert "temperature" not in kw
    assert "verbosity" not in kw


def test_build_stream_kwargs_o4_mini_applies_o_series_multiplier() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="o4-mini",
        exercise_type="mixte",
        system_content="sys",
        user_content="user",
    )
    # mixte base = 6500 ; o4-mini → ×1.4.
    assert kw["max_completion_tokens"] == int(6500 * 1.4)
    assert kw["reasoning_effort"] == "medium"  # high borné à medium sur o-series


def test_build_stream_kwargs_gpt41_mini_chat_classic_family() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="gpt-4.1-mini",
        exercise_type="addition",
        system_content="sys",
        user_content="user",
    )
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["temperature"] == 0.7
    assert "reasoning_effort" not in kw


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
    # Lot J : mixte → verbosity medium (explications multi-opérations à préserver).
    assert kw["verbosity"] == "medium"
    assert "temperature" not in kw


def test_verbosity_for_exercise_type_gpt5_per_type_map() -> None:
    # Types à opération directe → concis ``low`` (JSON court, pas de perte).
    assert verbosity_for_exercise_type_gpt5("addition") == "low"
    assert verbosity_for_exercise_type_gpt5("soustraction") == "low"
    assert verbosity_for_exercise_type_gpt5("multiplication") == "low"
    assert verbosity_for_exercise_type_gpt5("division") == "low"
    assert verbosity_for_exercise_type_gpt5("divers") == "low"
    # Types pédagogiquement plus riches → ``medium`` pour préserver explication/hint.
    assert verbosity_for_exercise_type_gpt5("fractions") == "medium"
    assert verbosity_for_exercise_type_gpt5("geometrie") == "medium"
    assert verbosity_for_exercise_type_gpt5("texte") == "medium"
    assert verbosity_for_exercise_type_gpt5("mixte") == "medium"
    # Fallback : ``low`` pour type inconnu.
    assert verbosity_for_exercise_type_gpt5("type_futur_inconnu") == "low"
    assert verbosity_for_exercise_type_gpt5("") == "low"


def test_verbosity_map_covers_all_canonical_exercise_types() -> None:
    # Invariant : les 9 types canoniques doivent être mappés explicitement.
    canonical = {
        "addition",
        "soustraction",
        "multiplication",
        "division",
        "fractions",
        "geometrie",
        "texte",
        "mixte",
        "divers",
    }
    assert canonical <= set(VERBOSITY_BY_EXERCISE_TYPE_GPT5.keys())


def test_build_stream_kwargs_gpt5_verbosity_low_on_simple_ops() -> None:
    kw = build_exercise_ai_stream_kwargs(
        model="gpt-5-mini",
        exercise_type="addition",
        system_content="sys",
        user_content="user",
    )
    assert kw["verbosity"] == "low"


def test_build_stream_kwargs_gpt5_verbosity_medium_on_rich_types() -> None:
    for rich_type in ("fractions", "geometrie", "texte"):
        kw = build_exercise_ai_stream_kwargs(
            model="gpt-5-mini",
            exercise_type=rich_type,
            system_content="sys",
            user_content="user",
        )
        assert kw["verbosity"] == "medium", f"{rich_type} devrait être medium"


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
