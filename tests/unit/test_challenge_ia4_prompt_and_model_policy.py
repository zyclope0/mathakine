"""IA4 — composition du prompt défis et résolution explicite du modèle."""

from __future__ import annotations

import inspect
import json

import pytest

import app.services.challenges.challenge_ai_service as challenge_ai_service
from app.core.ai_config import AIConfig
from app.core.ai_generation_policy import ExerciseAIModelNotAllowedError
from app.core.config import settings
from app.services.challenges.challenge_ai_model_policy import (
    DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL,
    build_challenge_ai_stream_kwargs,
    resolve_challenge_ai_fallback_model,
    resolve_challenge_ai_model,
)
from app.services.challenges.challenge_prompt_composition import (
    build_challenge_system_prompt,
    build_challenge_user_prompt,
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
    assert "pas une chaîne masquée" in p
    assert (
        "Ne mets pas `keyword_length`, `theme_clue` ni `mapping_known` à la racine" in p
    )
    assert "6. CODING" in p


def test_coding_prompt_requires_hidden_rule_for_high_difficulty() -> None:
    p = build_challenge_system_prompt("coding", "15-17")
    assert "RÈGLE DIFFICULTÉ CODING" in p
    assert "difficulty_rating >= 4.0" in p
    assert "ne pas afficher de décalage César" in p
    assert "pas de clé complète/quasi complète" in p
    assert "le mot-clé supposé" in p
    assert "nombre de caractères" in p


def test_user_prompt_uses_interface_locale_for_output_language() -> None:
    p = build_challenge_user_prompt("coding", "15-17", "", locale="en-US")
    assert "Langue de l'interface : en-US" in p
    assert "rédige les champs visibles en anglais" in p
    assert "`correct_answer` doit être en anglais" in p


def test_user_prompt_falls_back_to_french_for_unknown_locale() -> None:
    p = build_challenge_user_prompt("coding", "15-17", "", locale="zz-ZZ")
    assert "Langue de l'interface : zz-ZZ" in p
    assert "rédige les champs visibles en français" in p


def test_visual_adult_injects_complexity_rule() -> None:
    adult = build_challenge_system_prompt("visual", "adulte")
    assert "COMPLEXITÉ ADULTE" in adult
    child = build_challenge_system_prompt("visual", "9-11")
    assert "COMPLEXITÉ ADULTE" not in child


def test_pattern_prompt_includes_pattern_examples() -> None:
    p = build_challenge_system_prompt("pattern", "9-11")
    assert "EXEMPLES VALIDES DE PATTERNS" in p
    assert "1. PATTERN" in p


def test_pattern_prompt_discourages_revealing_rule_for_harder_grids() -> None:
    p = build_challenge_system_prompt("pattern", "15-17")
    assert "NE PAS dévoiler directement la mécanique exacte du motif" in p
    assert "ne révèle pas la règle exacte dans `description` ni dans `question`" in p
    assert '"carré latin", "décalage cyclique"' in p


def test_probability_prompt_requires_french_visual_text_and_real_4_plus_layer() -> None:
    p = build_challenge_system_prompt("probability", "15-17")
    assert "doivent rester en FRANÇAIS" in p
    assert "un tirage direct dans un seul sac/une urne" in p
    assert "3+ tirages" in p


def test_graph_prompt_requires_weighted_mst_contract() -> None:
    p = build_challenge_system_prompt("graph", "15-17")
    assert '"objective": "minimum_spanning_tree"' in p
    assert '"objective": "shortest_path"' in p
    assert "chaque arête DOIT inclure un poids numérique" in p
    assert "recalcule Kruskal/Prim" in p
    assert "recalcule Dijkstra" in p


def test_puzzle_prompt_prioritizes_complete_compact_visual_data() -> None:
    p = build_challenge_system_prompt("puzzle", "15-17")
    assert "Place `visual_data` tôt dans le JSON" in p
    assert "7 pièces maximum" in p
    assert "5 à 7 étapes courtes" in p


def test_visual_prompt_prioritizes_complete_compact_visual_data() -> None:
    p = build_challenge_system_prompt("visual", "15-17")
    assert "Place `visual_data` tôt dans le JSON" in p
    assert "visual_data.description` court" in p
    assert "2-3 inconnues maximum" in p
    assert "4 à 6 étapes courtes" in p


def test_global_json_contract_places_visual_data_before_explanation() -> None:
    p = build_challenge_system_prompt("graph", "15-17")
    assert p.index('"visual_data"') < p.index('"solution_explanation"')
    assert "Explication concise, suffisante et vérifiable" in p
    assert "Ne produis aucun texte hors JSON" in p


def test_chess_prompt_bounds_position_and_forced_line_contract() -> None:
    p = build_challenge_system_prompt("chess", "15-17")
    assert "4 à 8 pièces maximum" in p
    assert "UNIQUEMENT ces symboles anglais/FEN" in p
    assert "Dame blanche = Q, roi noir = k" in p
    assert "Évite mat_en_3" in p
    assert "mat_en_2 seulement si la ligne forcée est très courte" in p
    assert "Fou blanc en c4 + roi noir en g8 est illégal" in p
    assert "diagonale c4-d5-e6-f7-g8 attaque déjà le roi" in p
    assert "LIGNE FORCÉE complète" in p
    assert '"coup blanc, réponse noire forcée, coup blanc mat"' in p


def test_chess_validation_repair_is_scoped_to_initial_check_errors() -> None:
    assert (
        challenge_ai_service._should_attempt_chess_validation_repair(
            "chess",
            ["CHESS: roi noir déjà en échec alors que c'est aux Blancs de jouer"],
        )
        is True
    )
    assert (
        challenge_ai_service._should_attempt_chess_validation_repair(
            "sequence",
            ["CHESS: roi noir déjà en échec alors que c'est aux Blancs de jouer"],
        )
        is False
    )
    assert (
        challenge_ai_service._should_attempt_chess_validation_repair(
            "chess",
            ["CHESS: board doit avoir 8 rangées, reçu 7"],
        )
        is False
    )


def test_prompt_discourages_under_rating_structurally_complex_challenges() -> None:
    p = build_challenge_system_prompt("sequence", "15-17")
    assert "Ne PAS sous-évaluer" in p
    assert "plusieurs inconnues" in p
    assert "3.5+" in p


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


def test_resolve_challenge_model_default_o4_mini(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "")
    assert resolve_challenge_ai_model("sequence") == "o4-mini"
    assert resolve_challenge_ai_model("unknown_future_type") == "o4-mini"


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
    assert AIConfig.get_model("graph") == "o4-mini"
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


def test_build_challenge_ai_stream_kwargs_o1_no_json_format() -> None:
    kw = build_challenge_ai_stream_kwargs(
        model="o1-mini",
        system_content="S",
        user_content="U",
        ai_params={"model": "o1-mini", "max_tokens": 1234},
    )
    assert kw["model"] == "o1-mini"
    assert kw["stream"] is True
    assert "response_format" not in kw
    assert kw["max_completion_tokens"] == 1234


def test_build_challenge_ai_stream_kwargs_o3_json_and_reasoning() -> None:
    kw = build_challenge_ai_stream_kwargs(
        model="o3",
        system_content="S",
        user_content="U",
        ai_params={
            "model": "o3",
            "max_tokens": 5000,
            "reasoning_effort": "low",
        },
    )
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["max_completion_tokens"] == 5000
    assert kw["reasoning_effort"] == "low"


def test_build_challenge_ai_stream_kwargs_o4_mini_json_and_reasoning() -> None:
    kw = build_challenge_ai_stream_kwargs(
        model="o4-mini",
        system_content="S",
        user_content="U",
        ai_params={
            "model": "o4-mini",
            "max_tokens": 5000,
            "reasoning_effort": "medium",
        },
    )
    assert kw["response_format"] == {"type": "json_object"}
    assert kw["max_completion_tokens"] == 5000
    assert kw["reasoning_effort"] == "medium"


def test_chess_generation_runtime_budget_is_bounded() -> None:
    assert AIConfig.get_reasoning_effort("chess") == "low"
    assert AIConfig.get_max_tokens("chess") == 6000
    assert AIConfig.get_timeout("chess") == 90.0
    assert AIConfig.get_max_retries("chess") == 1
    assert AIConfig.get_max_retries("sequence") == AIConfig.MAX_RETRIES


def test_o_series_reasoning_is_systemically_bounded_for_json_completion_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "")
    assert AIConfig.get_reasoning_effort("pattern") == "high"
    assert AIConfig.get_o_series_reasoning_effort("pattern") == "medium"
    assert AIConfig.get_reasoning_effort("visual") == "high"
    assert AIConfig.get_o_series_reasoning_effort("visual") == "medium"
    assert AIConfig.get_reasoning_effort("deduction") == "high"
    assert AIConfig.get_o_series_reasoning_effort("deduction") == "medium"
    assert AIConfig.get_o_series_reasoning_effort("coding") == "medium"
    assert AIConfig.get_o_series_reasoning_effort("chess") == "low"
    params = AIConfig.get_openai_params("visual")
    assert params["model"] == "o4-mini"
    assert params["reasoning_effort"] == "medium"
    assert params["max_tokens"] == 8000


def test_puzzle_generation_has_extra_completion_budget_for_json_closure() -> None:
    assert AIConfig.get_max_tokens("puzzle") == 6500


def test_challenge_json_parser_rejects_openai_truncation_marker() -> None:
    with pytest.raises(json.JSONDecodeError):
        challenge_ai_service._extract_complete_challenge_json(
            'Model JSON is invalid, check the stop reason\n{"title": "x"'
        )


def test_challenge_json_parser_rejects_incomplete_json_object() -> None:
    with pytest.raises(json.JSONDecodeError):
        challenge_ai_service._extract_complete_challenge_json('{"title": "x"')


def test_build_challenge_ai_stream_kwargs_gpt5_verbosity_and_temp_when_none() -> None:
    kw = build_challenge_ai_stream_kwargs(
        model="gpt-5-mini",
        system_content="S",
        user_content="U",
        ai_params={
            "model": "gpt-5-mini",
            "max_tokens": 4000,
            "reasoning_effort": "none",
            "verbosity": "medium",
            "temperature": 0.42,
        },
    )
    assert kw["max_completion_tokens"] == 4000
    assert kw["reasoning_effort"] == "none"
    assert kw["verbosity"] == "medium"
    assert kw["temperature"] == 0.42


def test_build_challenge_ai_stream_kwargs_gpt5_no_temp_when_reasoning_active() -> None:
    kw = build_challenge_ai_stream_kwargs(
        model="gpt-5",
        system_content="S",
        user_content="U",
        ai_params={
            "model": "gpt-5",
            "max_tokens": 4000,
            "reasoning_effort": "medium",
            "verbosity": "low",
            "temperature": 0.9,
        },
    )
    assert "temperature" not in kw


def test_build_challenge_ai_stream_kwargs_chat_classic_max_tokens() -> None:
    kw = build_challenge_ai_stream_kwargs(
        model="gpt-4o-mini",
        system_content="S",
        user_content="U",
        ai_params={
            "model": "gpt-4o-mini",
            "max_tokens": 2000,
            "temperature": 0.35,
        },
    )
    assert kw["max_tokens"] == 2000
    assert kw["temperature"] == 0.35
    assert kw["response_format"] == {"type": "json_object"}
