"""
Tests de caractérisation pour exercise_generator.

Valident le comportement de generate_simple_exercise et generate_ai_exercise
AVANT toute extraction de helpers communs.

Phase 3, item 3.4a — audit architecture 03/2026.
"""

import random

import pytest

from server.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)


def _assert_valid_exercise(ex, *, expected_type=None, ai_generated=None):
    """Assertions structurelles communes à tout exercice généré."""
    assert isinstance(ex, dict), "Le résultat doit être un dict"
    for key in (
        "exercise_type",
        "age_group",
        "difficulty",
        "title",
        "question",
        "correct_answer",
        "choices",
        "explanation",
    ):
        assert key in ex, f"Clé manquante: {key}"

    assert isinstance(ex["choices"], list), "choices doit être une liste"
    assert len(ex["choices"]) >= 2, "Au moins 2 choix requis"

    choices_str = [str(c) for c in ex["choices"]]
    assert (
        str(ex["correct_answer"]) in choices_str
    ), f"correct_answer '{ex['correct_answer']}' absent de choices {choices_str}"

    assert ex["title"], "Le titre ne doit pas être vide"
    assert ex["question"], "La question ne doit pas être vide"

    if expected_type:
        assert ex["exercise_type"] == expected_type
    if ai_generated is not None:
        assert ex.get("ai_generated") == ai_generated


# ── generate_simple_exercise ──────────────────────────────────────────────


class TestGenerateSimpleExercise:
    """Tests couvrant tous les types pour generate_simple_exercise."""

    def test_addition(self):
        random.seed(42)
        ex = generate_simple_exercise("ADDITION", "9-11")
        _assert_valid_exercise(ex, expected_type="ADDITION", ai_generated=False)

    def test_soustraction(self):
        random.seed(42)
        ex = generate_simple_exercise("SOUSTRACTION", "9-11")
        _assert_valid_exercise(ex, expected_type="SOUSTRACTION", ai_generated=False)

    def test_multiplication(self):
        random.seed(42)
        ex = generate_simple_exercise("MULTIPLICATION", "9-11")
        _assert_valid_exercise(ex, expected_type="MULTIPLICATION", ai_generated=False)

    def test_division(self):
        random.seed(42)
        ex = generate_simple_exercise("DIVISION", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVISION", ai_generated=False)

    def test_fractions(self):
        random.seed(42)
        ex = generate_simple_exercise("FRACTIONS", "12-14")
        _assert_valid_exercise(ex, expected_type="FRACTIONS", ai_generated=False)

    def test_geometrie(self):
        random.seed(42)
        ex = generate_simple_exercise("GEOMETRIE", "12-14")
        _assert_valid_exercise(ex, expected_type="GEOMETRIE", ai_generated=False)

    def test_mixte(self):
        random.seed(42)
        ex = generate_simple_exercise("MIXTE", "12-14")
        _assert_valid_exercise(ex, expected_type="MIXTE", ai_generated=False)

    def test_texte(self):
        random.seed(42)
        ex = generate_simple_exercise("TEXTE", "9-11")
        _assert_valid_exercise(ex, expected_type="TEXTE", ai_generated=False)

    def test_divers(self):
        random.seed(42)
        ex = generate_simple_exercise("DIVERS", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVERS", ai_generated=False)

    def test_unknown_type_falls_back(self):
        random.seed(42)
        ex = generate_simple_exercise("UNKNOWN_TYPE", "9-11")
        _assert_valid_exercise(ex, ai_generated=False)

    def test_young_age_group(self):
        random.seed(42)
        ex = generate_simple_exercise("ADDITION", "6-8")
        _assert_valid_exercise(ex, expected_type="ADDITION", ai_generated=False)

    def test_adult_age_group(self):
        random.seed(42)
        ex = generate_simple_exercise("MULTIPLICATION", "adulte")
        _assert_valid_exercise(ex, expected_type="MULTIPLICATION", ai_generated=False)


# ── generate_ai_exercise ─────────────────────────────────────────────────


class TestGenerateAiExercise:
    """Tests couvrant tous les types pour generate_ai_exercise."""

    def test_addition(self):
        random.seed(42)
        ex = generate_ai_exercise("ADDITION", "9-11")
        _assert_valid_exercise(ex, expected_type="ADDITION", ai_generated=True)

    def test_soustraction(self):
        random.seed(42)
        ex = generate_ai_exercise("SOUSTRACTION", "9-11")
        _assert_valid_exercise(ex, expected_type="SOUSTRACTION", ai_generated=True)

    def test_multiplication(self):
        random.seed(42)
        ex = generate_ai_exercise("MULTIPLICATION", "9-11")
        _assert_valid_exercise(ex, expected_type="MULTIPLICATION", ai_generated=True)

    def test_division(self):
        random.seed(42)
        ex = generate_ai_exercise("DIVISION", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVISION", ai_generated=True)

    def test_fractions(self):
        random.seed(42)
        ex = generate_ai_exercise("FRACTIONS", "12-14")
        _assert_valid_exercise(ex, expected_type="FRACTIONS", ai_generated=True)

    def test_geometrie(self):
        random.seed(42)
        ex = generate_ai_exercise("GEOMETRIE", "12-14")
        _assert_valid_exercise(ex, expected_type="GEOMETRIE", ai_generated=True)

    def test_mixte(self):
        random.seed(42)
        ex = generate_ai_exercise("MIXTE", "12-14")
        _assert_valid_exercise(ex, expected_type="MIXTE", ai_generated=True)

    def test_texte(self):
        random.seed(42)
        ex = generate_ai_exercise("TEXTE", "9-11")
        _assert_valid_exercise(ex, expected_type="TEXTE", ai_generated=True)

    def test_divers(self):
        random.seed(42)
        ex = generate_ai_exercise("DIVERS", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVERS", ai_generated=True)

    def test_unknown_type_falls_back(self):
        random.seed(42)
        ex = generate_ai_exercise("UNKNOWN_TYPE", "9-11")
        _assert_valid_exercise(ex, ai_generated=True)


# ── ensure_explanation ────────────────────────────────────────────────────


class TestEnsureExplanation:
    def test_adds_explanation_if_missing(self):
        ex = {"exercise_type": "ADDITION", "correct_answer": "42"}
        result = ensure_explanation(ex)
        assert result.get("explanation"), "Doit ajouter une explication"

    def test_keeps_existing_explanation(self):
        ex = {
            "exercise_type": "ADDITION",
            "correct_answer": "42",
            "explanation": "Custom explanation.",
        }
        result = ensure_explanation(ex)
        assert result["explanation"] == "Custom explanation."

    def test_replaces_empty_explanation(self):
        ex = {
            "exercise_type": "MULTIPLICATION",
            "correct_answer": "10",
            "explanation": "",
        }
        result = ensure_explanation(ex)
        assert result["explanation"] != ""


# ── F42 generation profile ───────────────────────────────────────────────


class TestBuildExerciseGenerationProfile:
    """build_exercise_generation_profile() doit retourner un profil F42 cohérent."""

    def test_profile_returns_expected_keys(self):
        from app.core.difficulty_tier import build_exercise_generation_profile

        p = build_exercise_generation_profile("ADDITION", "9-11", "PADAWAN")
        assert p["exercise_type"] == "ADDITION"
        assert p["age_group"] == "9-11"
        assert p["derived_difficulty"] == "PADAWAN"
        assert isinstance(p["difficulty_tier"], int)
        assert p["pedagogical_band"] in ("discovery", "learning", "consolidation")
        assert p["calibration_desc"]

    def test_tier_varies_with_age_group(self):
        from app.core.difficulty_tier import build_exercise_generation_profile

        p1 = build_exercise_generation_profile("ADDITION", "6-8", "INITIE")
        p2 = build_exercise_generation_profile("ADDITION", "12-14", "CHEVALIER")
        assert p1["difficulty_tier"] != p2["difficulty_tier"]
        assert p1["difficulty_tier"] < p2["difficulty_tier"]

    def test_band_discovery_for_initie(self):
        from app.core.difficulty_tier import build_exercise_generation_profile

        p = build_exercise_generation_profile("ADDITION", "6-8", "INITIE")
        assert p["pedagogical_band"] == "discovery"

    def test_band_consolidation_for_chevalier(self):
        from app.core.difficulty_tier import build_exercise_generation_profile

        p = build_exercise_generation_profile("ADDITION", "12-14", "CHEVALIER")
        assert p["pedagogical_band"] == "consolidation"


# ── F42 local generator uses spatial narratives ──────────────────────────


class TestF42SpatialNarratives:
    """Exercices générés ne doivent plus contenir de tags/narrations Star Wars."""

    _SW_KEYWORDS = {
        "star wars",
        "jedi",
        "padawan",
        "yoda",
        "sith",
        "kyber",
        "x-wing",
        "tie fighter",
        "stormtrooper",
        "faucon millenium",
        "étoile de la mort",
        "lightsaber",
        "sabre laser",
    }

    def _has_star_wars(self, text: str) -> bool:
        low = text.lower()
        return any(kw in low for kw in self._SW_KEYWORDS)

    def test_ai_exercise_tags_no_starwars(self):
        random.seed(42)
        ex = generate_ai_exercise("ADDITION", "9-11")
        tags = ex.get("tags", "")
        assert "starwars" not in tags.lower()

    def test_ai_exercise_narrative_no_starwars(self):
        random.seed(42)
        for etype in ("ADDITION", "SOUSTRACTION", "MULTIPLICATION", "DIVISION"):
            ex = generate_ai_exercise(etype, "9-11")
            for field in ("question", "explanation", "title"):
                assert not self._has_star_wars(
                    ex.get(field, "")
                ), f"Star Wars found in {field} for {etype}: {ex.get(field, '')[:80]}"

    def test_simple_exercise_tags_no_starwars(self):
        random.seed(42)
        ex = generate_simple_exercise("ADDITION", "9-11")
        tags = ex.get("tags", "")
        assert "starwars" not in tags.lower()


# ── F42 OpenAI prompt builder ────────────────────────────────────────────


class TestBuildExerciseSystemPromptF42:
    """Le prompt système OpenAI doit porter le calibrage F42 et pas Star Wars."""

    def test_prompt_contains_calibration(self):
        from app.services.exercises.exercise_ai_service import (
            build_exercise_system_prompt,
        )

        prompt = build_exercise_system_prompt(
            "ADDITION",
            "PADAWAN",
            "9-11",
            {"desc": "nombres jusqu'à 100"},
            "spatial",
            calibration_desc="calculs intermédiaires, raisonnement guidé",
        )
        assert "calculs intermédiaires" in prompt

    def test_prompt_no_star_wars_by_default(self):
        from app.services.exercises.exercise_ai_service import (
            build_exercise_system_prompt,
        )

        prompt = build_exercise_system_prompt(
            "ADDITION",
            "PADAWAN",
            "9-11",
            {"desc": "nombres jusqu'à 100"},
            "spatial/galactique",
        )
        assert "Star Wars" not in prompt

    def test_two_different_tiers_produce_distinct_calibration(self):
        """Même bande pédagogique, tiers différents → calibration_desc distincte."""
        from app.core.difficulty_tier import build_exercise_generation_profile

        # Tier 4 (9-11 ans, discovery) vs tier 7 (12-14 ans, discovery)
        p_tier4 = build_exercise_generation_profile("ADDITION", "9-11", "INITIE")
        p_tier7 = build_exercise_generation_profile("ADDITION", "12-14", "INITIE")
        assert p_tier4["pedagogical_band"] == p_tier7["pedagogical_band"] == "discovery"
        assert p_tier4["difficulty_tier"] != p_tier7["difficulty_tier"]
        assert p_tier4["calibration_desc"] != p_tier7["calibration_desc"]


# ── F42 local wiring (init_exercise_context returns profile) ─────────────


class TestAdjustTypeLimitsForF42Profile:
    """adjust_type_limits_for_f42_profile() doit modifier les bornes selon la bande."""

    def _profile(self, band: str) -> dict:
        return {
            "pedagogical_band": band,
            "difficulty_tier": 5,
            "calibration_desc": "test",
        }

    def test_learning_band_is_identity(self):
        from app.utils.exercise_generator_helpers import (
            adjust_type_limits_for_f42_profile,
        )

        base = {"min": 10, "max": 50}
        result = adjust_type_limits_for_f42_profile(base, self._profile("learning"))
        assert result == base

    def test_discovery_reduces_max(self):
        from app.utils.exercise_generator_helpers import (
            adjust_type_limits_for_f42_profile,
        )

        base = {"min": 10, "max": 50}
        result = adjust_type_limits_for_f42_profile(base, self._profile("discovery"))
        # max should decrease: 10 + 60% of (50-10) = 10 + 24 = 34
        assert result["max"] < base["max"]
        assert result["min"] == base["min"]

    def test_consolidation_raises_min(self):
        from app.utils.exercise_generator_helpers import (
            adjust_type_limits_for_f42_profile,
        )

        base = {"min": 10, "max": 50}
        result = adjust_type_limits_for_f42_profile(
            base, self._profile("consolidation")
        )
        # min should increase: 10 + 40% of (50-10) = 10 + 16 = 26
        assert result["min"] > base["min"]
        assert result["max"] == base["max"]

    def test_discovery_vs_consolidation_produce_different_limits(self):
        from app.utils.exercise_generator_helpers import (
            adjust_type_limits_for_f42_profile,
        )

        base = {"min": 10, "max": 100}
        discovery = adjust_type_limits_for_f42_profile(base, self._profile("discovery"))
        consolidation = adjust_type_limits_for_f42_profile(
            base, self._profile("consolidation")
        )
        assert discovery["max"] < consolidation["max"]

    def test_non_int_values_passed_through(self):
        from app.utils.exercise_generator_helpers import (
            adjust_type_limits_for_f42_profile,
        )

        base = {"min": 1, "max": 10, "operations": 3}
        result = adjust_type_limits_for_f42_profile(base, self._profile("discovery"))
        assert result["operations"] == 3


class TestF42LocalWiring:
    """Le runtime local doit consommer le profil F42 via init_exercise_context."""

    def test_init_exercise_context_returns_f42_profile(self):
        from app.utils.exercise_generator_helpers import init_exercise_context

        result = init_exercise_context("ADDITION", "9-11")
        assert len(result) == 5, "init_exercise_context doit retourner 5 éléments"
        _, _, _, _, f42_profile = result
        assert isinstance(f42_profile, dict)
        assert "difficulty_tier" in f42_profile
        assert "pedagogical_band" in f42_profile
        assert "calibration_desc" in f42_profile

    def test_type_limits_are_adjusted_by_f42_profile(self):
        """Les bornes retournées par init_exercise_context doivent refléter le profil F42."""
        from unittest.mock import patch

        from app.utils.exercise_generator_helpers import (
            adjust_type_limits_for_f42_profile,
            init_exercise_context,
        )

        called_with = {}

        original = adjust_type_limits_for_f42_profile

        def spy(limits, profile):
            called_with["limits"] = limits
            called_with["profile"] = profile
            return original(limits, profile)

        with patch(
            "app.utils.exercise_generator_helpers.adjust_type_limits_for_f42_profile",
            side_effect=spy,
        ):
            init_exercise_context("ADDITION", "9-11")

        assert (
            "profile" in called_with
        ), "adjust_type_limits_for_f42_profile doit être appelé"
        assert called_with["profile"]["pedagogical_band"] in (
            "discovery",
            "learning",
            "consolidation",
        )

    def test_generated_exercise_carries_difficulty_tier(self):
        """generate_ai_exercise et generate_simple_exercise exposent difficulty_tier."""
        random.seed(42)
        ai_ex = generate_ai_exercise("ADDITION", "9-11")
        assert "difficulty_tier" in ai_ex
        assert ai_ex["difficulty_tier"] is not None

        random.seed(42)
        simple_ex = generate_simple_exercise("ADDITION", "9-11")
        assert "difficulty_tier" in simple_ex

    def test_profile_is_consistent_with_age_group(self):
        """Le tier retourné est cohérent avec le groupe d'âge : 6-8 < 12-14."""
        from app.utils.exercise_generator_helpers import init_exercise_context

        _, _, _, _, p_young = init_exercise_context("ADDITION", "6-8")
        _, _, _, _, p_older = init_exercise_context("ADDITION", "12-14")
        if p_young["difficulty_tier"] and p_older["difficulty_tier"]:
            assert p_young["difficulty_tier"] < p_older["difficulty_tier"]

    def test_discovery_band_max_is_lower_than_consolidation(self):
        """Dans la même difficulté legacy, discovery → bornes plus basses que consolidation."""
        from unittest.mock import patch

        from app.utils.exercise_generator_helpers import init_exercise_context

        def make_profile_with_band(band):
            def build_profile(
                exercise_type,
                age_group_raw,
                derived_difficulty,
                *,
                pedagogical_band_override=None,
            ):
                from app.core.difficulty_tier import build_exercise_generation_profile

                p = build_exercise_generation_profile(
                    exercise_type,
                    age_group_raw,
                    derived_difficulty,
                )
                p["pedagogical_band"] = band
                return p

            return build_profile

        with patch(
            "app.utils.exercise_generator_helpers.build_exercise_generation_profile",
            side_effect=make_profile_with_band("discovery"),
        ):
            _, _, _, limits_discovery, _ = init_exercise_context("ADDITION", "9-11")

        with patch(
            "app.utils.exercise_generator_helpers.build_exercise_generation_profile",
            side_effect=make_profile_with_band("consolidation"),
        ):
            _, _, _, limits_consolidation, _ = init_exercise_context("ADDITION", "9-11")

        assert limits_discovery["max"] < limits_consolidation["max"]


# ── Comprehensive anti-Star Wars parametrized test ───────────────────────


class TestAllGeneratorTypesNoStarWars:
    """Tous les types d'exercices ne doivent produire aucune référence Star Wars/Jedi."""

    _ALL_TYPES = [
        "ADDITION",
        "SOUSTRACTION",
        "MULTIPLICATION",
        "DIVISION",
        "FRACTIONS",
        "GEOMETRIE",
        "DIVERS",
        "MIXTE",
        "TEXTE",
    ]
    _AGE_GROUPS = ["6-8", "9-11", "12-14"]
    _SW_KEYWORDS = {
        "star wars",
        "jedi",
        "padawan",
        "yoda",
        "sith",
        "kyber",
        "x-wing",
        "tie fighter",
        "stormtrooper",
        "étoile de la mort",
        "faucon millenium",
        "sabre laser",
        "luke",
        "leia",
        "anakin",
        "dark vador",
        "dark vader",
        "obi-wan",
        "r2-d2",
        "c-3po",
        "tatooine",
        "cantina",
        "mos eisley",
        "temple jedi",
        "alliance rebelle",
    }

    def _assert_no_star_wars(self, text: str, context: str) -> None:
        low = text.lower()
        for kw in self._SW_KEYWORDS:
            assert (
                kw not in low
            ), f"Star Wars term '{kw}' found in {context}: {text[:120]}"

    def test_generate_ai_exercise_all_types_no_starwars(self):
        for age in self._AGE_GROUPS:
            for etype in self._ALL_TYPES:
                random.seed(0)
                try:
                    ex = generate_ai_exercise(etype, age)
                except Exception:
                    continue  # Skip if type not supported for this age
                ctx = f"generate_ai_exercise({etype}, {age})"
                for field in ("title", "question", "explanation", "tags"):
                    self._assert_no_star_wars(str(ex.get(field, "")), f"{ctx}.{field}")

    def test_generate_simple_exercise_all_types_no_starwars(self):
        for age in self._AGE_GROUPS:
            for etype in self._ALL_TYPES:
                random.seed(0)
                try:
                    ex = generate_simple_exercise(etype, age)
                except Exception:
                    continue
                ctx = f"generate_simple_exercise({etype}, {age})"
                for field in ("title", "question", "explanation", "tags"):
                    self._assert_no_star_wars(str(ex.get(field, "")), f"{ctx}.{field}")


# ── F42 second axis: mastery-driven band runtime tests ────────────────────


class TestF42SecondAxisRuntime:
    """
    Prove that a SAME age_group can produce MULTIPLE pedagogical bands and thus
    different type_limits, when pedagogical_band_override is provided.

    These tests use the public generator API with the keyword argument introduced
    as the second axis; they do NOT mock final helpers (no mock of
    build_exercise_generation_profile or adjust_type_limits_for_f42_profile).
    """

    def test_same_age_group_three_bands_via_override(self):
        """9-11 ans avec discovery/learning/consolidation → bandes ET tiers différents."""
        from app.utils.exercise_generator_helpers import init_exercise_context

        _, _, _, limits_disc, profile_disc = init_exercise_context(
            "ADDITION", "9-11", pedagogical_band_override="discovery"
        )
        _, _, _, limits_learn, profile_learn = init_exercise_context(
            "ADDITION", "9-11", pedagogical_band_override="learning"
        )
        _, _, _, limits_cons, profile_cons = init_exercise_context(
            "ADDITION", "9-11", pedagogical_band_override="consolidation"
        )

        # All three use the same age_group — bands must differ
        assert profile_disc["pedagogical_band"] == "discovery"
        assert profile_learn["pedagogical_band"] == "learning"
        assert profile_cons["pedagogical_band"] == "consolidation"

        # Calibration bounds differ: discovery < learning/no-change <= consolidation
        assert limits_disc["max"] < limits_learn["max"]
        assert limits_cons["min"] > limits_learn["min"]

        # CRITICAL: difficulty_tier must vary with the band (not be constant)
        assert profile_disc["difficulty_tier"] != profile_learn["difficulty_tier"]
        assert profile_learn["difficulty_tier"] != profile_cons["difficulty_tier"]
        # Tiers for 9-11: discovery=4, learning=5, consolidation=6
        assert profile_disc["difficulty_tier"] == 4
        assert profile_learn["difficulty_tier"] == 5
        assert profile_cons["difficulty_tier"] == 6

        # calibration_desc must also vary
        assert profile_disc["calibration_desc"] != profile_learn["calibration_desc"]
        assert profile_learn["calibration_desc"] != profile_cons["calibration_desc"]

    def test_generator_receives_band_via_override(self):
        """generate_simple_exercise transmet le band override : tiers cohérents."""
        random.seed(42)
        ex_disc = generate_simple_exercise(
            "ADDITION", "9-11", pedagogical_band_override="discovery"
        )
        random.seed(42)
        ex_cons = generate_simple_exercise(
            "ADDITION", "9-11", pedagogical_band_override="consolidation"
        )
        # Both carry difficulty_tier — and they must differ
        assert ex_disc.get("difficulty_tier") is not None
        assert ex_cons.get("difficulty_tier") is not None
        assert ex_disc["difficulty_tier"] != ex_cons["difficulty_tier"]
        # 9-11 discovery=4, consolidation=6
        assert ex_disc["difficulty_tier"] == 4
        assert ex_cons["difficulty_tier"] == 6

    def test_ai_exercise_receives_band_via_override(self):
        """generate_ai_exercise transmet le band override au profil F42."""
        random.seed(0)
        ex = generate_ai_exercise(
            "ADDITION", "9-11", pedagogical_band_override="consolidation"
        )
        assert ex.get("difficulty_tier") is not None

    def test_fallback_without_override_is_learning(self):
        """Sans override, la bande par défaut pour PADAWAN est 'learning'."""
        from app.utils.exercise_generator_helpers import init_exercise_context

        _, _, _, _, profile = init_exercise_context("ADDITION", "9-11")
        assert profile["pedagogical_band"] == "learning"


class TestAdaptiveContextBandResolution:
    """
    Prove that AdaptiveGenerationContext can return different bands for the
    same age_group based on mastery data — the real second-axis runtime path.
    """

    def test_low_mastery_gives_discovery_band(self):
        """mastery_level=1 → discovery band (weak learner in their age group)."""
        from datetime import datetime, timezone
        from unittest.mock import MagicMock, patch

        from app.services.exercises.adaptive_difficulty_service import (
            AdaptiveGenerationContext,
            resolve_adaptive_context,
        )

        # User with age_group 9-11 but low mastery
        user = MagicMock()
        user.id = 42
        user.age_group = "9-11"
        user.preferred_difficulty = None
        user.grade_level = None

        progress = MagicMock()
        progress.total_attempts = 10
        progress.mastery_level = 1  # Low mastery → discovery
        progress.completion_rate = 40.0
        progress.streak = 0
        # last_active_date must be a real datetime to compare with window_start
        progress.last_active_date = datetime.now(timezone.utc)

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = progress

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value="9-11",
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert isinstance(ctx, AdaptiveGenerationContext)
        # With the fixed implementation, age_group is stable (from profile, not mastery)
        assert ctx.age_group == "9-11"
        assert ctx.pedagogical_band == "discovery"
        assert ctx.mastery_source == "progress_mastery"

    def test_high_mastery_gives_consolidation_band(self):
        """mastery_level=5 → consolidation band."""
        from datetime import datetime, timezone
        from unittest.mock import MagicMock, patch

        from app.services.exercises.adaptive_difficulty_service import (
            AdaptiveGenerationContext,
            resolve_adaptive_context,
        )

        user = MagicMock()
        user.id = 99
        user.age_group = "9-11"
        user.preferred_difficulty = None
        user.grade_level = None

        progress = MagicMock()
        progress.total_attempts = 20
        progress.mastery_level = 5  # High mastery → consolidation
        progress.completion_rate = 96.0
        progress.streak = 5
        progress.last_active_date = datetime.now(timezone.utc)

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = progress

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value="9-11",
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert isinstance(ctx, AdaptiveGenerationContext)
        assert ctx.pedagogical_band == "consolidation"

    def test_no_progress_gives_fallback_learning(self):
        """Sans données de maîtrise, bande par défaut = learning."""
        from unittest.mock import MagicMock, patch

        from app.services.exercises.adaptive_difficulty_service import (
            AdaptiveGenerationContext,
            resolve_adaptive_context,
        )

        user = MagicMock()
        user.id = 7
        user.age_group = "9-11"
        user.preferred_difficulty = None
        user.grade_level = None

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value="9-11",
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert isinstance(ctx, AdaptiveGenerationContext)
        assert ctx.pedagogical_band == "learning"
        assert ctx.mastery_source == "fallback"

    def test_same_age_group_different_mastery_different_band(self):
        """MÊME tranche d'âge, MAÎTRISE différente → BANDES différentes."""
        from datetime import datetime, timezone
        from unittest.mock import MagicMock, patch

        from app.services.exercises.adaptive_difficulty_service import (
            resolve_adaptive_context,
        )

        def _make_ctx(mastery_level):
            user = MagicMock()
            user.id = mastery_level * 10
            user.age_group = "9-11"
            user.preferred_difficulty = None
            user.grade_level = None

            progress = MagicMock()
            progress.total_attempts = 15
            progress.mastery_level = mastery_level
            progress.completion_rate = 50.0
            progress.streak = 1
            progress.last_active_date = datetime.now(timezone.utc)

            db = MagicMock()
            db.query.return_value.filter.return_value.first.return_value = progress

            with (
                patch(
                    "app.services.exercises.adaptive_difficulty_service."
                    "normalized_age_group_from_user_profile",
                    return_value="9-11",
                ),
                patch(
                    "app.services.diagnostic.diagnostic_service.get_latest_score",
                    return_value=None,
                ),
            ):
                return resolve_adaptive_context(db, user, "ADDITION")

        ctx_low = _make_ctx(1)  # mastery 1 → discovery
        ctx_high = _make_ctx(5)  # mastery 5 → consolidation

        # CRITICAL invariant: SAME age_group, DIFFERENT bands
        assert ctx_low.age_group == ctx_high.age_group == "9-11"
        assert ctx_low.pedagogical_band != ctx_high.pedagogical_band
        assert ctx_low.pedagogical_band == "discovery"
        assert ctx_high.pedagogical_band == "consolidation"


class TestF42TierCalibrationsCoherence:
    """
    Prove that difficulty_tier and calibration_desc vary with the band
    when pedagogical_band_override is used (the F42 second axis).

    These tests do NOT mock build_exercise_generation_profile or
    adjust_type_limits_for_f42_profile.
    """

    def test_tier_varies_with_band_same_age_group(self):
        """For 9-11 ans: discovery→4, learning→5, consolidation→6."""
        from app.core.difficulty_tier import build_exercise_generation_profile

        p_disc = build_exercise_generation_profile(
            "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="discovery"
        )
        p_learn = build_exercise_generation_profile(
            "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="learning"
        )
        p_cons = build_exercise_generation_profile(
            "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="consolidation"
        )

        assert p_disc["difficulty_tier"] == 4
        assert p_learn["difficulty_tier"] == 5
        assert p_cons["difficulty_tier"] == 6

    def test_calibration_desc_varies_with_tier(self):
        """calibration_desc must be distinct for each tier."""
        from app.core.difficulty_tier import build_exercise_generation_profile

        p_disc = build_exercise_generation_profile(
            "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="discovery"
        )
        p_cons = build_exercise_generation_profile(
            "ADDITION", "9-11", "PADAWAN", pedagogical_band_override="consolidation"
        )

        assert p_disc["calibration_desc"] != p_cons["calibration_desc"]
        # Tier 4 description should mention "découverte"
        assert "découverte" in p_disc["calibration_desc"].lower()
        # Tier 6 description should mention "consolidation"
        assert "consolidation" in p_cons["calibration_desc"].lower()

    def test_legacy_path_unchanged(self):
        """Without override, tier is derived from age_group × derived_difficulty."""
        from app.core.difficulty_tier import build_exercise_generation_profile

        p = build_exercise_generation_profile("ADDITION", "9-11", "PADAWAN")
        # PADAWAN → band_idx=1 (learning) → tier=5 for 9-11
        assert p["difficulty_tier"] == 5
        assert p["pedagogical_band"] == "learning"

    def test_tier_coherent_in_generated_exercise(self):
        """The exercise dict carries a tier coherent with the band used."""
        random.seed(7)
        ex_disc = generate_simple_exercise(
            "ADDITION", "9-11", pedagogical_band_override="discovery"
        )
        random.seed(7)
        ex_cons = generate_simple_exercise(
            "ADDITION", "9-11", pedagogical_band_override="consolidation"
        )

        assert ex_disc["difficulty_tier"] == 4
        assert ex_cons["difficulty_tier"] == 6
