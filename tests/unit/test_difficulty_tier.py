"""Tests unitaires — F42 matrice difficulty_tier (1–12).

Deux sections :

1. Tests métier historiques : comportement public des fonctions
   ``compute_difficulty_tier_for_exercise_strings``,
   ``compute_user_target_difficulty_tier``,
   ``pedagogical_band_index_from_difficulty``,
   ``exercise_tier_filter_expression``,
   ``compute_difficulty_tier_for_logic_challenge``.
2. Tests d'enrichissement cognitif (Lot B — DOK / Bloom) : invariants du dict
   ``_TIER_CALIBRATION`` et intégration via ``build_exercise_generation_profile``.

Sources académiques citées dans le code :
  - Webb's Depth of Knowledge (1997)
  - Bloom's revised taxonomy (Anderson & Krathwohl, 2001)
"""

from __future__ import annotations

import re

from app.core.constants import AgeGroups
from app.core.difficulty_tier import (
    DIFFICULTY_TIER_MAX,
    DIFFICULTY_TIER_MIN,
    _TIER_CALIBRATION,
    build_exercise_generation_profile,
    clamp_difficulty_for_type,
    cognitive_guidance_kind_for_exercise_type,
    cognitive_hint_for_exercise_type,
    cognitive_intensity_for_difficulty,
    compute_difficulty_tier_for_exercise_strings,
    compute_user_target_difficulty_tier,
    exercise_tier_filter_expression,
    pedagogical_band_index_from_difficulty,
)
from app.models.logic_challenge import AgeGroup as ChAge

# ---------------------------------------------------------------------------
# Section 1 — Tests métier F42 (historiques)
# ---------------------------------------------------------------------------


def test_compute_tier_exercise_6_8_initie():
    assert compute_difficulty_tier_for_exercise_strings("6-8", "INITIE") == 1


def test_compute_tier_exercise_9_11_padawan():
    assert compute_difficulty_tier_for_exercise_strings("9-11", "PADAWAN") == 5


def test_compute_tier_exercise_tous_ages_none():
    assert compute_difficulty_tier_for_exercise_strings("tous-ages", "PADAWAN") is None


def test_user_target_tier_all_ages_none():
    assert compute_user_target_difficulty_tier(AgeGroups.ALL_AGES, "PADAWAN") is None


def test_user_target_tier_15_plus_grand_maitre():
    assert compute_user_target_difficulty_tier("15+", "GRAND_MAITRE") == 12


def test_pedagogical_band_easy_medium_hard():
    assert pedagogical_band_index_from_difficulty("easy") == 0
    assert pedagogical_band_index_from_difficulty("medium") == 1
    assert pedagogical_band_index_from_difficulty("hard") == 2


def test_exercise_tier_filter_expression_none_tier_legacy_only():
    expr = exercise_tier_filter_expression(None, "PADAWAN")
    # SQLAlchemy BinaryExpression — compare key column
    assert "difficulty" in str(expr).lower()


def test_logic_challenge_age_group_mapping_import():
    from app.core.difficulty_tier import compute_difficulty_tier_for_logic_challenge

    t = compute_difficulty_tier_for_logic_challenge(ChAge.GROUP_10_12, "PADAWAN", 3.0)
    assert t == 5


def test_cognitive_intensity_all_five_levels() -> None:
    assert cognitive_intensity_for_difficulty("INITIE") == 0
    assert cognitive_intensity_for_difficulty("PADAWAN") == 1
    assert cognitive_intensity_for_difficulty("CHEVALIER") == 2
    assert cognitive_intensity_for_difficulty("MAITRE") == 3
    assert cognitive_intensity_for_difficulty("GRAND_MAITRE") == 4
    assert cognitive_intensity_for_difficulty(" padawan ") == 1


def test_cognitive_intensity_returns_none_for_empty_or_unknown() -> None:
    assert cognitive_intensity_for_difficulty(None) is None
    assert cognitive_intensity_for_difficulty("") is None
    assert cognitive_intensity_for_difficulty("   ") is None
    assert cognitive_intensity_for_difficulty("NOT_A_JEDI_LEVEL") is None


def test_cognitive_guidance_kind_is_type_aware() -> None:
    assert cognitive_guidance_kind_for_exercise_type("addition") == "atomic"
    assert cognitive_guidance_kind_for_exercise_type(" division ") == "atomic"
    assert cognitive_guidance_kind_for_exercise_type("texte") == "multistep"
    assert cognitive_guidance_kind_for_exercise_type("GEOMETRIE") == "multistep"
    assert cognitive_guidance_kind_for_exercise_type("unknown") is None


def test_cognitive_hint_for_atomic_type_never_requires_multistep_reasoning() -> None:
    hint = cognitive_hint_for_exercise_type("addition", "CHEVALIER")
    assert hint is not None
    assert "étapes" not in hint
    assert "données" not in hint
    assert "opération" in hint


def test_cognitive_hint_for_multistep_type_keeps_reasoning_depth() -> None:
    hint = cognitive_hint_for_exercise_type("texte", "CHEVALIER")
    assert hint == "consolidation : deux étapes minimum, pas de procédure soufflée"


# ---------------------------------------------------------------------------
# Section 2 — Tests d'enrichissement cognitif Lot B (DOK / Bloom)
# ---------------------------------------------------------------------------

_DOK_MARKER_RE = re.compile(r"DOK\s*\d")
_BLOOM_VERBS = ("Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create")


def test_tier_calibration_has_12_entries() -> None:
    assert len(_TIER_CALIBRATION) == 12
    assert set(_TIER_CALIBRATION.keys()) == set(
        range(DIFFICULTY_TIER_MIN, DIFFICULTY_TIER_MAX + 1)
    )


def test_tier_calibration_each_entry_has_dok_marker() -> None:
    for tier, desc in _TIER_CALIBRATION.items():
        assert _DOK_MARKER_RE.search(
            desc
        ), f"tier {tier} manque le marqueur DOK : {desc!r}"


def test_tier_calibration_each_entry_has_bloom_marker() -> None:
    for tier, desc in _TIER_CALIBRATION.items():
        matched = [verb for verb in _BLOOM_VERBS if verb in desc]
        assert matched, (
            f"tier {tier} manque au moins un verbe Bloom révisé "
            f"parmi {_BLOOM_VERBS} : {desc!r}"
        )


def test_tier_calibration_all_12_entries_distinct() -> None:
    values = list(_TIER_CALIBRATION.values())
    assert (
        len(set(values)) == 12
    ), "les 12 calibrations doivent être textuellement distinctes"


def test_tier_calibration_non_empty_and_str() -> None:
    # Garde-fou additionnel : aucun tier ne doit avoir une valeur vide ou non-str.
    for tier, desc in _TIER_CALIBRATION.items():
        assert isinstance(desc, str), f"tier {tier} : valeur non-str ({type(desc)})"
        assert desc.strip(), f"tier {tier} : calibration vide"


def test_build_exercise_generation_profile_exposes_enriched_calibration() -> None:
    # Intégration : le profil généré pour (9-11, CHEVALIER) → tier 6 → doit contenir DOK.
    profile = build_exercise_generation_profile("ADDITION", "9-11", "CHEVALIER")
    assert profile["difficulty_tier"] == 6
    cal = profile["calibration_desc"]
    assert "DOK" in cal, f"calibration_desc ne contient pas DOK : {cal!r}"
    # Sanity : un verbe Bloom est bien présent côté profil exposé.
    assert any(
        verb in cal for verb in _BLOOM_VERBS
    ), f"calibration_desc ne contient aucun verbe Bloom : {cal!r}"


def test_generation_profile_exposes_cognitive_intensity_for_chevalier_group_9_11() -> (
    None
):
    p = build_exercise_generation_profile("ADDITION", "9-11", "CHEVALIER")
    assert p["difficulty_tier"] == 6
    assert p["cognitive_intensity"] == 2
    assert p["cognitive_hint"] == (
        "consolidation : opération unique avec nombres moins immédiats, "
        "regroupement ou retenue possible"
    )


def test_build_exercise_generation_profile_preserves_age_and_band_keywords() -> None:
    # Non-régression : les tests existants s'appuient sur la présence de
    # 'découverte' / 'consolidation' dans calibration_desc — l'enrichissement
    # DOK/Bloom ne doit pas avoir retiré ces ancres pédagogiques.
    p_disc = build_exercise_generation_profile(
        "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="discovery"
    )
    p_cons = build_exercise_generation_profile(
        "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="consolidation"
    )
    assert "découverte" in p_disc["calibration_desc"].lower()
    assert "consolidation" in p_cons["calibration_desc"].lower()


# ---------------------------------------------------------------------------
# Section 3 — Lot F : clamp runtime type × difficulté
# ---------------------------------------------------------------------------


def test_clamp_unknown_type_noop() -> None:
    eff, reason = clamp_difficulty_for_type("unknown_type_xyz", "GRAND_MAITRE")
    assert eff == "GRAND_MAITRE"
    assert reason is None


def test_clamp_unknown_difficulty_noop() -> None:
    eff, reason = clamp_difficulty_for_type("addition", "JEDI_SUPREME")
    assert eff == "JEDI_SUPREME"
    assert reason is None


def test_clamp_empty_type_or_difficulty_noop() -> None:
    assert clamp_difficulty_for_type("", "GRAND_MAITRE") == ("GRAND_MAITRE", None)
    assert clamp_difficulty_for_type("addition", "") == ("", None)
    assert clamp_difficulty_for_type("", "") == ("", None)


def test_clamp_addition_grand_maitre_to_chevalier_with_reason() -> None:
    eff, reason = clamp_difficulty_for_type("addition", "GRAND_MAITRE")
    assert eff == "CHEVALIER"
    assert reason is not None
    assert "difficulty_above_type_ceiling" in reason
    assert "GRAND_MAITRE" in reason and "CHEVALIER" in reason and "addition" in reason


def test_clamp_soustraction_maitre_to_chevalier_with_reason() -> None:
    eff, reason = clamp_difficulty_for_type("soustraction", "MAITRE")
    assert eff == "CHEVALIER"
    assert reason is not None
    assert "difficulty_above_type_ceiling" in reason


def test_clamp_multiplication_initie_to_padawan_with_reason() -> None:
    eff, reason = clamp_difficulty_for_type("multiplication", "INITIE")
    assert eff == "PADAWAN"
    assert reason is not None
    assert "difficulty_below_type_floor" in reason


def test_clamp_division_grand_maitre_to_maitre_with_reason() -> None:
    eff, reason = clamp_difficulty_for_type("division", "GRAND_MAITRE")
    assert eff == "MAITRE"
    assert reason is not None
    assert "difficulty_above_type_ceiling" in reason


def test_clamp_mixte_initie_to_chevalier_with_reason() -> None:
    eff, reason = clamp_difficulty_for_type("mixte", "INITIE")
    assert eff == "CHEVALIER"
    assert reason is not None
    assert "difficulty_below_type_floor" in reason


def test_clamp_geometrie_grand_maitre_respects_ceiling() -> None:
    # GAP-2 Feature A : geometrie seedé GRAND_MAITRE reste autorisé.
    eff, reason = clamp_difficulty_for_type("geometrie", "GRAND_MAITRE")
    assert eff == "GRAND_MAITRE"
    assert reason is None


def test_clamp_texte_grand_maitre_respects_ceiling() -> None:
    eff, reason = clamp_difficulty_for_type("texte", "GRAND_MAITRE")
    assert eff == "GRAND_MAITRE"
    assert reason is None


def test_clamp_is_case_insensitive_on_type_and_difficulty() -> None:
    # Garde-fou supplémentaire : l'API admin peut envoyer des casses variables.
    eff_up, reason_up = clamp_difficulty_for_type("ADDITION", "grand_maitre")
    assert eff_up == "CHEVALIER"
    assert reason_up is not None
