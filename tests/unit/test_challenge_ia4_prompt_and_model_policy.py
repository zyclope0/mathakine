"""IA4 — composition du prompt défis et résolution explicite du modèle."""

from __future__ import annotations

import inspect

import pytest

import app.services.challenges.challenge_ai_service as challenge_ai_service
from app.core.ai_config import AIConfig
from app.core.ai_generation_policy import ExerciseAIModelNotAllowedError
from app.core.config import settings
from app.services.challenges.challenge_ai_model_policy import (
    DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL,
    resolve_challenge_ai_fallback_model,
    resolve_challenge_ai_model,
)
from app.services.challenges.challenge_prompt_composition import (
    build_challenge_system_prompt,
    challenge_system_prompt_stats,
)

# Référence pilotage (prompt monolithique avant IA4)
MONOLITHIC_CHALLENGE_PROMPT_BASELINE_CHARS = 23690


def test_sequence_prompt_excludes_other_types_heavy_contracts() -> None:
    p = build_challenge_system_prompt("sequence", "9-11")
    assert "mat_en_1" not in p
    assert "board[0] = rangée 8" not in p
    assert "VISUAL_DATA OBLIGATOIRE (type sequence)" in p
    assert "2. SEQUENCE" in p


def test_coding_prompt_includes_crypto_contract() -> None:
    p = build_challenge_system_prompt("coding", "12-14")
    assert "VISUAL_DATA OBLIGATOIRE (type coding" in p
    assert "caesar" in p.lower()
    assert "6. CODING" in p


def test_visual_adult_injects_complexity_rule() -> None:
    adult = build_challenge_system_prompt("visual", "adulte")
    assert "COMPLEXITÉ ADULTE" in adult
    child = build_challenge_system_prompt("visual", "9-11")
    assert "COMPLEXITÉ ADULTE" not in child


def test_pattern_prompt_includes_pattern_examples() -> None:
    p = build_challenge_system_prompt("pattern", "9-11")
    assert "EXEMPLES VALIDES DE PATTERNS" in p
    assert "1. PATTERN" in p


def test_spatial_uses_same_tail_as_visual_after_type_lock() -> None:
    ps = build_challenge_system_prompt("spatial", "9-11")
    pv = build_challenge_system_prompt("visual", "9-11")
    marker = "GROUPE D'ÂGE CIBLE"
    assert ps.split(marker, 1)[1] == pv.split(marker, 1)[1]


def test_prompt_size_well_below_monolith_for_representative_types() -> None:
    for ctype in ("sequence", "coding", "visual", "deduction"):
        n = challenge_system_prompt_stats(ctype, "9-11")["chars"]
        assert (
            n < MONOLITHIC_CHALLENGE_PROMPT_BASELINE_CHARS - 4000
        ), f"{ctype} devrait être nettement plus court que le monolithe ({n} >= baseline-4000)"


def test_resolve_challenge_model_default_o3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "")
    assert resolve_challenge_ai_model("sequence") == "o3"
    assert resolve_challenge_ai_model("unknown_future_type") == "o3"


def test_challenges_override_beats_reasoning_legacy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "gpt-4o-mini")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "o1")
    assert resolve_challenge_ai_model("chess") == "gpt-4o-mini"


def test_reasoning_legacy_used_when_challenges_override_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", " gpt-4o ")
    assert resolve_challenge_ai_model("puzzle") == "gpt-4o"


def test_disallowed_challenge_model_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "not-a-real-openai-model"
    )
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "")
    with pytest.raises(ExerciseAIModelNotAllowedError):
        resolve_challenge_ai_model("sequence")


def test_ai_config_get_model_delegates_to_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "")
    assert AIConfig.get_model("graph") == "o3"
    assert AIConfig.get_model("graph") == resolve_challenge_ai_model("graph")


def test_resolve_challenge_ai_fallback_model_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE", "")
    assert (
        resolve_challenge_ai_fallback_model("sequence")
        == DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL
    )


def test_resolve_challenge_ai_fallback_model_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE", "gpt-4o")
    assert resolve_challenge_ai_fallback_model("chess") == "gpt-4o"


def test_resolve_challenge_ai_fallback_disallowed_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE",
        "totally-unknown-model-xyz",
    )
    with pytest.raises(ExerciseAIModelNotAllowedError):
        resolve_challenge_ai_fallback_model("puzzle")


def test_generate_challenge_stream_uses_fallback_policy_not_advanced_model() -> None:
    src = inspect.getsource(challenge_ai_service.generate_challenge_stream)
    assert "resolve_challenge_ai_fallback_model" in src
    assert "ADVANCED_MODEL" not in src
