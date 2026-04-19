"""
Tests unitaires pour app/services/adaptive_difficulty_service.py  -  F05.

Couvre :
- Cascade de priorites (IRT > progression > profil > fallback)
- Logique de boost (completion_rate > 85 % ET streak >= 3)
- Logique de descente (completion_rate < 50 % ET streak = 0)
- Cas edge : diagnostic expire, profil vide, grade_level
- Isolation : Mock de Session SQLAlchemy et de get_latest_score
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

import app.services.exercises.adaptive_difficulty_service as adaptive_difficulty_module
from app.core.constants import AgeGroups, DifficultyLevels, ExerciseTypes
from app.models.progress import Progress
from app.models.user import User
from app.services.exercises.adaptive_difficulty_service import (
    COLD_START_PEDAGOGICAL_BAND,
    IRT_SEEDED_TYPES,
    AdaptiveGenerationContext,
    _adjust_for_realtime_progress,
    _irt_ordinal_for_type,
    _mastery_to_ordinal,
    _ordinal_to_age_group,
    resolve_adaptive_context,
    resolve_adaptive_difficulty,
    resolve_irt_level,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_db(progress=None):
    """Cree un mock de Session SQLAlchemy qui retourne un Progress."""
    db = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    filter_mock.first.return_value = progress
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock
    return db


def _make_user(
    user_id=1,
    preferred_difficulty=None,
    grade_level=None,
    age_group=None,
):
    user = MagicMock()
    user.id = user_id
    user.preferred_difficulty = preferred_difficulty
    user.grade_level = grade_level
    user.age_group = age_group
    return user


class _ProfileUser:
    """Profil minimal pour tests du prior seedé (évite MagicMock truthy sur age_group)."""

    __slots__ = ("id", "preferred_difficulty", "grade_level", "age_group")

    def __init__(
        self,
        user_id: int,
        preferred_difficulty=None,
        grade_level=None,
        age_group=None,
    ) -> None:
        self.id = user_id
        self.preferred_difficulty = preferred_difficulty
        self.grade_level = grade_level
        self.age_group = age_group


def _make_db_with_user(user, progress=None):
    """Session mock : ``query(User)`` → ``user`` ; ``query(Progress)`` → ``progress``."""
    db = MagicMock()

    def query_side_effect(model):
        q = MagicMock()
        if model is User:
            q.filter.return_value.first.return_value = user
        elif model is Progress:
            q.filter.return_value.first.return_value = progress
        else:
            q.filter.return_value.first.return_value = None
        return q

    db.query.side_effect = query_side_effect
    return db


def _make_progress(
    total_attempts=10,
    completion_rate=70.0,
    streak=1,
    mastery_level=2,
    days_ago=3,
):
    """Cree un mock de Progress avec last_active_date recente."""
    p = MagicMock()
    p.total_attempts = total_attempts
    p.completion_rate = completion_rate
    p.streak = streak
    p.mastery_level = mastery_level
    p.last_active_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return p


def _make_irt_score(difficulty="PADAWAN", days_ago=5):
    """Cree un score IRT valide (< 30 jours)."""
    completed_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {
        "completed_at": completed_at.isoformat(),
        "scores": {
            "addition": {
                "difficulty": difficulty,
                "level": 1,
                "correct": 3,
                "total": 4,
            }
        },
    }


# ---------------------------------------------------------------------------
# Tests _ordinal_to_age_group
# ---------------------------------------------------------------------------


class TestOrdinalToAgeGroup:
    def test_ordinal_0_returns_group_6_8(self):
        assert _ordinal_to_age_group(0) == AgeGroups.GROUP_6_8

    def test_ordinal_1_returns_group_9_11(self):
        assert _ordinal_to_age_group(1) == AgeGroups.GROUP_9_11

    def test_ordinal_2_returns_group_12_14(self):
        assert _ordinal_to_age_group(2) == AgeGroups.GROUP_12_14

    def test_ordinal_3_returns_group_15_17(self):
        assert _ordinal_to_age_group(3) == AgeGroups.GROUP_15_17

    def test_ordinal_4_returns_adult(self):
        assert _ordinal_to_age_group(4) == AgeGroups.ADULT

    def test_ordinal_above_4_clamped_to_adult(self):
        assert _ordinal_to_age_group(10) == AgeGroups.ADULT

    def test_ordinal_below_0_clamped_to_group_6_8(self):
        assert _ordinal_to_age_group(-1) == AgeGroups.GROUP_6_8


# ---------------------------------------------------------------------------
# Tests _mastery_to_ordinal
# ---------------------------------------------------------------------------


class TestMasteryToOrdinal:
    def test_mastery_1_returns_0(self):
        assert _mastery_to_ordinal(1) == 0

    def test_mastery_3_returns_2(self):
        assert _mastery_to_ordinal(3) == 2

    def test_mastery_5_returns_4(self):
        assert _mastery_to_ordinal(5) == 4

    def test_mastery_0_clamped_to_0(self):
        assert _mastery_to_ordinal(0) == 0

    def test_mastery_6_clamped_to_4(self):
        assert _mastery_to_ordinal(6) == 4


# ---------------------------------------------------------------------------
# Tests _adjust_for_realtime_progress
# ---------------------------------------------------------------------------


class TestAdjustForRealtimeProgress:
    def test_boost_when_high_rate_and_streak(self):
        progress = _make_progress(total_attempts=10, completion_rate=90.0, streak=5)
        db = _make_db(progress=progress)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=2)
        assert result == 3  # boost de 2 ? 3

    def test_no_boost_at_max_ordinal(self):
        progress = _make_progress(total_attempts=10, completion_rate=90.0, streak=5)
        db = _make_db(progress=progress)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=4)
        assert result == 4  # plafonne

    def test_descent_when_low_rate_and_no_streak(self):
        progress = _make_progress(total_attempts=10, completion_rate=40.0, streak=0)
        db = _make_db(progress=progress)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=2)
        assert result == 1  # descente de 2 ? 1

    def test_no_descent_at_min_ordinal(self):
        progress = _make_progress(total_attempts=10, completion_rate=40.0, streak=0)
        db = _make_db(progress=progress)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=0)
        assert result == 0  # plancher

    def test_no_change_in_normal_range(self):
        progress = _make_progress(total_attempts=10, completion_rate=70.0, streak=2)
        db = _make_db(progress=progress)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=2)
        assert result == 2  # inchange

    def test_no_change_when_not_enough_attempts(self):
        progress = _make_progress(total_attempts=3, completion_rate=90.0, streak=5)
        db = _make_db(progress=progress)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=1)
        assert result == 1  # pas assez de tentatives

    def test_no_change_when_no_progress(self):
        db = _make_db(progress=None)
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=2)
        assert result == 2

    def test_exception_returns_base_ordinal(self):
        db = MagicMock()
        db.query.side_effect = Exception("DB error")
        result = _adjust_for_realtime_progress(db, 1, "addition", base_ordinal=2)
        assert result == 2


# ---------------------------------------------------------------------------
# Tests resolve_adaptive_difficulty - cascade de priorites
# ---------------------------------------------------------------------------


class TestResolveAdaptiveDifficulty:
    """Teste la cascade IRT ? progression ? profil ? fallback."""

    def test_priority1_irt_returns_adapted_age_group(self):
        """IRT recent et valide ? utilise la difficulte IRT."""
        irt_score = _make_irt_score(difficulty=DifficultyLevels.CHEVALIER, days_ago=5)
        db = _make_db(progress=None)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_score,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        # CHEVALIER = ordinal 2 ? GROUP_12_14
        assert result == AgeGroups.GROUP_12_14

    def test_priority1_irt_expired_falls_to_priority2(self):
        """IRT > 30 jours ? ignore, passe au niveau 2."""
        irt_score = _make_irt_score(
            difficulty=DifficultyLevels.GRAND_MAITRE, days_ago=35
        )
        progress = _make_progress(
            total_attempts=10, completion_rate=70.0, streak=2, mastery_level=2
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_score,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        # IRT expire ? progression : mastery=2 ? ordinal 1 ? GROUP_9_11
        assert result == AgeGroups.GROUP_9_11

    def test_priority1_irt_type_not_evaluated_falls_to_priority2(self):
        """IRT ne couvre pas le type ? passe au niveau 2."""
        irt_score = {
            "completed_at": (
                datetime.now(timezone.utc) - timedelta(days=5)
            ).isoformat(),
            "scores": {
                "soustraction": {
                    "difficulty": DifficultyLevels.MAITRE,
                    "correct": 4,
                    "total": 4,
                }
            },
        }
        progress = _make_progress(
            total_attempts=8, completion_rate=60.0, streak=1, mastery_level=3
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_score,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        # IRT ne couvre pas addition ? progression : mastery=3 ? ordinal 2 ? GROUP_12_14
        assert result == AgeGroups.GROUP_12_14

    def test_priority2_realtime_progress_used_when_no_irt(self):
        """Pas d'IRT ? utilise la progression temps reel."""
        progress = _make_progress(
            total_attempts=10, completion_rate=72.0, streak=2, mastery_level=4
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "MULTIPLICATION")

        # mastery=4 ? ordinal 3 ? GROUP_15_17
        assert result == AgeGroups.GROUP_15_17

    def test_priority2_not_enough_attempts_falls_to_priority3(self):
        """Pas assez de tentatives ? passe au profil utilisateur."""
        progress = _make_progress(
            total_attempts=2, completion_rate=80.0, streak=2, mastery_level=3
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.CHEVALIER)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        # Pas assez tentatives ? profil ? CHEVALIER ? ordinal 2 ? GROUP_12_14
        assert result == AgeGroups.GROUP_12_14

    def test_priority3_preferred_difficulty_used(self):
        """Profil utilisateur avec preferred_difficulty ? utilise comme fallback."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.MAITRE)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "DIVISION")

        # MAITRE ? ordinal 3 ? GROUP_15_17
        assert result == AgeGroups.GROUP_15_17

    def test_priority3_users_age_group_overrides_preferred_difficulty(self):
        """F42 — users.age_group prime sur preferred_difficulty (axes séparés)."""
        db = _make_db(progress=None)
        user = _make_user(
            user_id=1,
            age_group="6-8",
            preferred_difficulty=DifficultyLevels.GRAND_MAITRE,
        )

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        assert result == AgeGroups.GROUP_6_8

    def test_priority3_users_age_group_15_plus_maps_to_canonical(self):
        """Profil API 15+ → forme canonique 15-17 pour la cascade."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, age_group="15+")

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            # TEXTE : plafond GRAND_MAITRE → cascade non clampée (Lot F).
            result = resolve_adaptive_difficulty(db, user, "TEXTE")

        assert result == AgeGroups.GROUP_15_17

    def test_priority3_grade_level_used_when_no_preferred_difficulty(self):
        """Profil utilisateur avec grade_level ? utilise si pas de preferred_difficulty."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, grade_level=9)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "FRACTIONS")

        # grade 9 ? ordinal 2 ? GROUP_12_14
        assert result == AgeGroups.GROUP_12_14

    def test_priority4_fallback_when_no_data(self):
        """Aucune donnee ? fallback GROUP_9_11."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        assert result == AgeGroups.GROUP_9_11

    def test_irt_with_boost_applied(self):
        """IRT valide + boost temps reel ? niveau monte."""
        irt_score = _make_irt_score(difficulty=DifficultyLevels.PADAWAN, days_ago=10)
        # Progression avec boost (rate > 85 %, streak >= 3)
        progress = _make_progress(
            total_attempts=15, completion_rate=92.0, streak=4, mastery_level=2
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_score,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        # PADAWAN = ordinal 1, boost ? 2 ? GROUP_12_14
        assert result == AgeGroups.GROUP_12_14

    def test_irt_with_descent_applied(self):
        """IRT valide + descente temps reel ? niveau descendu."""
        irt_score = _make_irt_score(difficulty=DifficultyLevels.CHEVALIER, days_ago=10)
        # Progression avec descente (rate < 50 %, streak = 0)
        progress = _make_progress(
            total_attempts=10, completion_rate=35.0, streak=0, mastery_level=3
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_score,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        # CHEVALIER = ordinal 2, descente ? 1 ? GROUP_9_11
        assert result == AgeGroups.GROUP_9_11

    def test_no_user_id_returns_fallback(self):
        """Utilisateur sans id ? fallback GROUP_9_11."""
        db = _make_db(progress=None)
        user = MagicMock()
        user.id = None

        result = resolve_adaptive_difficulty(db, user, "ADDITION")
        assert result == AgeGroups.GROUP_9_11

    def test_irt_exception_falls_through_to_fallback(self):
        """Exception dans get_latest_score ? continue vers fallback."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1)

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            side_effect=Exception("Service unavailable"),
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")

        assert result == AgeGroups.GROUP_9_11


class TestResolveAdaptiveContext:
    """Le chemin F42 doit garder l'âge stable et réutiliser IRT en fallback de bande."""

    def test_progress_mastery_changes_band_but_not_age_group(self):
        progress = _make_progress(
            total_attempts=12,
            completion_rate=80.0,
            streak=2,
            mastery_level=5,
        )
        db = _make_db(progress=progress)
        user = _make_user(user_id=1, age_group="9-11")

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert isinstance(ctx, AdaptiveGenerationContext)
        assert ctx.age_group == AgeGroups.GROUP_9_11
        assert ctx.pedagogical_band == "consolidation"
        assert ctx.mastery_source == "progress_mastery"

    def test_irt_fallback_changes_band_but_not_age_group(self):
        db = _make_db(progress=None)
        user = _make_user(user_id=1, age_group="9-11")
        irt_score = _make_irt_score(
            difficulty=DifficultyLevels.GRAND_MAITRE, days_ago=5
        )

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_score,
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert isinstance(ctx, AdaptiveGenerationContext)
        assert ctx.age_group == AgeGroups.GROUP_9_11
        assert ctx.pedagogical_band == "consolidation"
        assert ctx.mastery_source == "irt_diagnostic"

    def test_no_progress_and_no_irt_falls_back_to_learning(self):
        # Fallback band is "learning" — neutral legacy-compatible default.
        # Changing this is a product decision (F42-P2), not a trivial fix.
        db = _make_db(progress=None)
        user = _make_user(user_id=1, age_group="9-11")

        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert isinstance(ctx, AdaptiveGenerationContext)
        assert ctx.age_group == AgeGroups.GROUP_9_11
        assert ctx.pedagogical_band == "learning"
        assert ctx.mastery_source == "fallback"


# ---------------------------------------------------------------------------
# Tests _PREF_DIFFICULTY_TO_ORDINAL e mapping elargi (age_group + DifficultyLevel)
# ---------------------------------------------------------------------------


class TestPrefDifficultyToOrdinal:
    def test_age_group_adulte_resolves_to_adult(self):
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty="adulte")
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            # TEXTE : plafond GRAND_MAITRE → pas de clamp (Lot F).
            result = resolve_adaptive_difficulty(db, user, "TEXTE")
        assert result == AgeGroups.ADULT

    def test_age_group_9_11_resolves_to_group_9_11(self):
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty="9-11")
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")
        assert result == AgeGroups.GROUP_9_11

    def test_age_group_12_14_resolves_to_group_12_14(self):
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty="12-14")
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")
        assert result == AgeGroups.GROUP_12_14

    def test_age_group_15_17_resolves_to_group_15_17(self):
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty="15-17")
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            # TEXTE : plafond GRAND_MAITRE → pas de clamp (Lot F).
            result = resolve_adaptive_difficulty(db, user, "TEXTE")
        assert result == AgeGroups.GROUP_15_17

    def test_difficulty_level_grand_maitre_still_works(self):
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.GRAND_MAITRE)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            # TEXTE : plafond GRAND_MAITRE → mapping GRAND_MAITRE→ADULT préservé (Lot F).
            result = resolve_adaptive_difficulty(db, user, "TEXTE")
        assert result == AgeGroups.ADULT


# ---------------------------------------------------------------------------
# Tests _irt_ordinal_for_type e resolution directe et proxy
# ---------------------------------------------------------------------------


def _make_full_irt_scores(
    addition="CHEVALIER",
    soustraction="CHEVALIER",
    multiplication="MAITRE",
    division="PADAWAN",
):
    return {
        "addition": {"difficulty": addition, "level": 2, "correct": 3, "total": 4},
        "soustraction": {
            "difficulty": soustraction,
            "level": 2,
            "correct": 3,
            "total": 4,
        },
        "multiplication": {
            "difficulty": multiplication,
            "level": 3,
            "correct": 4,
            "total": 4,
        },
        "division": {"difficulty": division, "level": 1, "correct": 2, "total": 4},
    }


class TestIrtOrdinalForType:
    def test_direct_addition(self):
        assert (
            _irt_ordinal_for_type(
                _make_full_irt_scores(addition="CHEVALIER"), "addition"
            )
            == 2
        )

    def test_direct_multiplication(self):
        assert (
            _irt_ordinal_for_type(
                _make_full_irt_scores(multiplication="MAITRE"), "multiplication"
            )
            == 3
        )

    def test_direct_grand_maitre(self):
        assert (
            _irt_ordinal_for_type(
                _make_full_irt_scores(addition="GRAND_MAITRE"), "addition"
            )
            == 4
        )

    def test_proxy_mixte_returns_minimum(self):
        scores = _make_full_irt_scores(
            addition="CHEVALIER",
            soustraction="MAITRE",
            multiplication="MAITRE",
            division="PADAWAN",
        )
        assert _irt_ordinal_for_type(scores, "mixte") == 1

    def test_proxy_mixte_all_grand_maitre(self):
        scores = _make_full_irt_scores(
            addition="GRAND_MAITRE",
            soustraction="GRAND_MAITRE",
            multiplication="GRAND_MAITRE",
            division="GRAND_MAITRE",
        )
        assert _irt_ordinal_for_type(scores, "mixte") == 4

    def test_proxy_fractions_uses_division_level(self):
        scores = _make_full_irt_scores(multiplication="MAITRE", division="PADAWAN")
        assert (
            _irt_ordinal_for_type(scores, "fractions") == 1
        )  # PADAWAN (division seule)

    def test_proxy_fractions_both_grand_maitre(self):
        scores = _make_full_irt_scores(
            multiplication="GRAND_MAITRE", division="GRAND_MAITRE"
        )
        assert _irt_ordinal_for_type(scores, "fractions") == 4

    def test_no_proxy_geometrie_returns_none(self):
        assert _irt_ordinal_for_type(_make_full_irt_scores(), "geometrie") is None

    def test_no_proxy_texte_returns_none(self):
        assert _irt_ordinal_for_type(_make_full_irt_scores(), "texte") is None

    def test_no_proxy_divers_returns_none(self):
        assert _irt_ordinal_for_type(_make_full_irt_scores(), "divers") is None

    def test_unknown_type_returns_none(self):
        assert _irt_ordinal_for_type({}, "unknown_type") is None

    def test_proxy_mixte_partial_scores(self):
        partial = {
            "addition": {
                "difficulty": "CHEVALIER",
                "level": 2,
                "correct": 3,
                "total": 4,
            },
            "multiplication": {
                "difficulty": "MAITRE",
                "level": 3,
                "correct": 4,
                "total": 4,
            },
        }
        assert _irt_ordinal_for_type(partial, "mixte") == 2


# ---------------------------------------------------------------------------
# Tests resolve_irt_level e point d'entree public
# ---------------------------------------------------------------------------


class TestResolveIrtLevel:
    def _make_db_with_irt(self, scores, days_ago=5):
        completed_at = (
            datetime.now(timezone.utc) - timedelta(days=days_ago)
        ).isoformat()
        irt_data = {"completed_at": completed_at, "scores": scores}
        return _make_db(progress=None), irt_data

    def test_returns_difficulty_for_direct_type(self):
        scores = _make_full_irt_scores(addition="CHEVALIER")
        db, irt_data = self._make_db_with_irt(scores)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db, user_id=1, exercise_type="ADDITION")
        assert result == DifficultyLevels.CHEVALIER

    def test_returns_none_for_geometrie_without_seed_profile(self):
        """IRT couvre les 4 types de base mais pas géométrie ; pas de profil seedable (mock)."""
        scores = _make_full_irt_scores()
        db, irt_data = self._make_db_with_irt(scores)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db, user_id=1, exercise_type="GEOMETRIE")
        assert result is None

    def test_geometrie_seeded_prior_from_preferred_maitre(self):
        scores = _make_full_irt_scores()
        db, irt_data = self._make_db_with_irt(scores)
        profile = _ProfileUser(
            1, preferred_difficulty=DifficultyLevels.MAITRE, grade_level=None
        )
        db_user = _make_db_with_user(profile)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db_user, user_id=1, exercise_type="GEOMETRIE")
        assert result == DifficultyLevels.MAITRE

    def test_texte_seeded_prior_from_grade_level_without_preferred(self):
        scores = _make_full_irt_scores()
        db, irt_data = self._make_db_with_irt(scores)
        profile = _ProfileUser(
            2, preferred_difficulty=None, grade_level=9, age_group=None
        )
        db_user = _make_db_with_user(profile)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db_user, user_id=2, exercise_type="TEXTE")
        assert result == DifficultyLevels.CHEVALIER

    def test_texte_seeded_prior_clamps_grand_maitre_to_maitre(self):
        scores = _make_full_irt_scores()
        db, irt_data = self._make_db_with_irt(scores)
        profile = _ProfileUser(3, preferred_difficulty=DifficultyLevels.GRAND_MAITRE)
        db_user = _make_db_with_user(profile)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db_user, user_id=3, exercise_type="TEXTE")
        assert result == DifficultyLevels.MAITRE

    def test_divers_no_user_signals_returns_none(self):
        scores = _make_full_irt_scores()
        db, irt_data = self._make_db_with_irt(scores)
        profile = _ProfileUser(4)
        db_user = _make_db_with_user(profile)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db_user, user_id=4, exercise_type="DIVERS")
        assert result is None

    def test_addition_direct_irt_priority_over_profile(self):
        scores = _make_full_irt_scores(addition="CHEVALIER")
        db, irt_data = self._make_db_with_irt(scores)
        profile = _ProfileUser(5, preferred_difficulty=DifficultyLevels.GRAND_MAITRE)
        db_user = _make_db_with_user(profile)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db_user, user_id=5, exercise_type="ADDITION")
        assert result == DifficultyLevels.CHEVALIER

    def test_irt_seeded_types_frozen_set(self):
        assert IRT_SEEDED_TYPES == frozenset(
            {
                ExerciseTypes.GEOMETRIE.lower(),
                ExerciseTypes.TEXTE.lower(),
                ExerciseTypes.DIVERS.lower(),
            }
        )

    def test_returns_none_when_no_diagnostic(self):
        db = _make_db(progress=None)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_irt_level(db, user_id=1, exercise_type="ADDITION")
        assert result is None

    def test_returns_none_when_irt_expired(self):
        scores = _make_full_irt_scores(addition="GRAND_MAITRE")
        db, irt_data = self._make_db_with_irt(scores, days_ago=35)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db, user_id=1, exercise_type="ADDITION")
        assert result is None

    def test_mixte_returns_minimum_difficulty(self):
        scores = _make_full_irt_scores(
            addition="CHEVALIER",
            soustraction="MAITRE",
            multiplication="MAITRE",
            division="INITIE",
        )
        db, irt_data = self._make_db_with_irt(scores)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=irt_data,
        ):
            result = resolve_irt_level(db, user_id=1, exercise_type="MIXTE")
        assert result == DifficultyLevels.INITIE


# ---------------------------------------------------------------------------
# F42-P2 — cold-start decision, TTL cache
# ---------------------------------------------------------------------------


class TestF42P2ColdStartAndCache:
    """P2a documented fallback ; P2b in-process cache (no product change)."""

    def test_p2a_cold_start_age_6_8_stable_band_learning(self):
        """Sans progression ni IRT : âge profil 6–8 + bande cold-start = learning."""
        db = _make_db(progress=None)
        user = _make_user(user_id=501, age_group="6-8")

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value=AgeGroups.GROUP_6_8,
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            ctx = resolve_adaptive_context(db, user, "ADDITION")

        assert ctx.age_group == AgeGroups.GROUP_6_8
        assert ctx.pedagogical_band == COLD_START_PEDAGOGICAL_BAND == "learning"
        assert ctx.mastery_source == "fallback"

    def test_p2b_resolve_adaptive_context_cache_hit_same_user_type(self, monkeypatch):
        monkeypatch.setattr(adaptive_difficulty_module.time, "monotonic", lambda: 0.0)
        db = _make_db(progress=None)
        user = _make_user(user_id=502, age_group="9-11")
        impl = adaptive_difficulty_module._resolve_adaptive_context_impl

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value=AgeGroups.GROUP_9_11,
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
            patch.object(
                adaptive_difficulty_module,
                "_resolve_adaptive_context_impl",
                wraps=impl,
            ) as spy,
        ):
            resolve_adaptive_context(db, user, "ADDITION")
            resolve_adaptive_context(db, user, "ADDITION")

        assert spy.call_count == 1

    def test_p2b_cache_distinct_exercise_type(self, monkeypatch):
        monkeypatch.setattr(adaptive_difficulty_module.time, "monotonic", lambda: 0.0)
        db = _make_db(progress=None)
        user = _make_user(user_id=503, age_group="9-11")
        impl = adaptive_difficulty_module._resolve_adaptive_context_impl

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value=AgeGroups.GROUP_9_11,
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
            patch.object(
                adaptive_difficulty_module,
                "_resolve_adaptive_context_impl",
                wraps=impl,
            ) as spy,
        ):
            resolve_adaptive_context(db, user, "ADDITION")
            resolve_adaptive_context(db, user, "DIVISION")

        assert spy.call_count == 2

    def test_p2b_cache_expires_after_ttl(self, monkeypatch):
        times = iter([0.0, 400.0])

        def _mono():
            return next(times)

        monkeypatch.setattr(adaptive_difficulty_module.time, "monotonic", _mono)
        db = _make_db(progress=None)
        user = _make_user(user_id=504, age_group="9-11")
        impl = adaptive_difficulty_module._resolve_adaptive_context_impl

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value=AgeGroups.GROUP_9_11,
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
            patch.object(
                adaptive_difficulty_module,
                "_resolve_adaptive_context_impl",
                wraps=impl,
            ) as spy,
        ):
            resolve_adaptive_context(db, user, "ADDITION")
            resolve_adaptive_context(db, user, "ADDITION")

        assert spy.call_count == 2

    def test_cache_bypassed_when_user_id_none(self, monkeypatch):
        monkeypatch.setattr(adaptive_difficulty_module.time, "monotonic", lambda: 0.0)
        db = _make_db(progress=None)
        user = MagicMock(spec=["age_group", "preferred_difficulty", "grade_level"])
        user.id = None
        user.age_group = "9-11"
        user.preferred_difficulty = None
        user.grade_level = None
        impl = adaptive_difficulty_module._resolve_adaptive_context_impl

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value=AgeGroups.GROUP_9_11,
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
            patch.object(
                adaptive_difficulty_module,
                "_resolve_adaptive_context_impl",
                wraps=impl,
            ) as spy,
        ):
            resolve_adaptive_context(db, user, "ADDITION")
            resolve_adaptive_context(db, user, "ADDITION")

        assert spy.call_count == 2


class TestF43A1AdaptiveObservabilityLogs:
    """F43-A1 — journalisation ``f43_adaptive_context`` au remplissage du cache."""

    @patch.object(adaptive_difficulty_module, "logger")
    def test_f43_adaptive_log_once_per_cache_fill(self, mock_log, monkeypatch):
        adaptive_difficulty_module.clear_resolve_adaptive_context_cache()
        monkeypatch.setattr(adaptive_difficulty_module.time, "monotonic", lambda: 0.0)
        db = _make_db(progress=None)
        user = _make_user(user_id=601, age_group="9-11")

        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service."
                "normalized_age_group_from_user_profile",
                return_value=AgeGroups.GROUP_9_11,
            ),
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            resolve_adaptive_context(db, user, "ADDITION")
            resolve_adaptive_context(db, user, "ADDITION")

        f43_calls = [
            c
            for c in mock_log.info.call_args_list
            if c.args and "f43_adaptive_context" in c.args[0]
        ]
        assert len(f43_calls) == 1
        assert f43_calls[0].args[1] == 601
        assert f43_calls[0].args[2] == "addition"
        assert f43_calls[0].args[3] == "fallback"
        assert f43_calls[0].args[4] == "learning"


# ---------------------------------------------------------------------------
# Lot F — clamp type × difficulté runtime (cascade adaptative)
# ---------------------------------------------------------------------------


class TestResolveAdaptiveDifficultyTypeClamp:
    """Le clamp type-aware est appliqué avant chaque retour de la cascade."""

    def test_clamp_geometrie_seed_grand_maitre_still_returns_grand_maitre(self):
        """GAP-2 Feature A : geometrie + seed GRAND_MAITRE non clampé."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.GRAND_MAITRE)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "GEOMETRIE")
        # GRAND_MAITRE → ordinal 4 → ADULT (plafond geometrie = GRAND_MAITRE)
        assert result == AgeGroups.ADULT

    def test_clamp_addition_seed_grand_maitre_returns_chevalier(self):
        """addition + seed GRAND_MAITRE est clampé à CHEVALIER (plafond addition)."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.GRAND_MAITRE)
        with patch(
            "app.services.diagnostic.diagnostic_service.get_latest_score",
            return_value=None,
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")
        # GRAND_MAITRE (ordinal 4) clampé → CHEVALIER (ordinal 2) → GROUP_12_14
        assert result == AgeGroups.GROUP_12_14

    def test_resolve_adaptive_difficulty_emits_clamp_log_on_effect(self):
        """Un clamp effectif produit un log ``type_difficulty_clamp``."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.GRAND_MAITRE)
        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service.logger"
            ) as mock_log,
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            resolve_adaptive_difficulty(db, user, "ADDITION")

        clamp_calls = [
            c
            for c in mock_log.info.call_args_list
            if c.args and "type_difficulty_clamp" in c.args[0]
        ]
        assert (
            len(clamp_calls) == 1
        ), f"attendu 1 log clamp, obtenu {len(clamp_calls)} : {clamp_calls!r}"
        args = clamp_calls[0].args
        assert args[1] == 1  # user_id
        assert args[2] == "ADDITION"  # exercise_type
        assert args[3] == DifficultyLevels.GRAND_MAITRE
        assert args[4] == DifficultyLevels.CHEVALIER
        assert "difficulty_above_type_ceiling" in args[5]

    def test_no_clamp_log_when_within_bounds(self):
        """Aucun log clamp si la cascade est déjà dans la plage autorisée."""
        db = _make_db(progress=None)
        user = _make_user(user_id=1, preferred_difficulty=DifficultyLevels.CHEVALIER)
        with (
            patch(
                "app.services.exercises.adaptive_difficulty_service.logger"
            ) as mock_log,
            patch(
                "app.services.diagnostic.diagnostic_service.get_latest_score",
                return_value=None,
            ),
        ):
            result = resolve_adaptive_difficulty(db, user, "ADDITION")
        assert result == AgeGroups.GROUP_12_14
        clamp_calls = [
            c
            for c in mock_log.info.call_args_list
            if c.args and "type_difficulty_clamp" in c.args[0]
        ]
        assert clamp_calls == []
