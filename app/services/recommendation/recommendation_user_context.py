"""
Contexte utilisateur pour le moteur de recommandations exercices (lot R2).

Remplace le tuple opaque (age_group, default_difficulty, ...) par une structure
explicite, avec difficultés diagnostiques **par type** (clés normalisées R1).

- ``global_default_difficulty`` : fallback transverse (âge + médiane diagnostic si dispo).
- ``diagnostic_difficulty_by_type`` : ``normalize_exercise_type_key`` -> difficulté IRT.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.core.constants import AgeGroups, get_difficulty_from_age_group
from app.core.difficulty_tier import compute_user_target_difficulty_tier
from app.core.logging_config import get_logger
from app.core.user_age_group import normalized_age_group_from_user_profile
from app.utils.exercise_type_normalization import normalize_exercise_type_key

logger = get_logger(__name__)

# Même grille que diagnostic_service (F03) — import local pour éviter cycles
_GRADE_TO_AGE_GROUP = {
    (1, 3): AgeGroups.GROUP_6_8,
    (4, 6): AgeGroups.GROUP_9_11,
    (7, 9): AgeGroups.GROUP_12_14,
    (10, 12): AgeGroups.GROUP_15_17,
}


def _normalize_difficulty_string(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    return s.upper()


@dataclass(frozen=True)
class RecommendationUserContext:
    """Contexte figé pour une génération de recommandations exercices."""

    age_group: str
    global_default_difficulty: str
    learning_goal: str
    practice_rhythm: str
    #: Clés = ``normalize_exercise_type_key`` ; valeurs = difficulté (ex. INITIE, CHEVALIER)
    diagnostic_difficulty_by_type: Dict[str, str]
    #: F42 — tier 1..12 pour l'utilisateur (âge résolu × difficulté globale) ; ``None`` si ALL_AGES
    target_difficulty_tier: Optional[int]


def get_target_difficulty_for_type(
    ctx: RecommendationUserContext,
    exercise_type_norm: str,
    progress_difficulty: Optional[str] = None,
) -> str:
    """
    Difficulté cible pour un type d'exercice.

    Priorité :
      1. Progress (niveau actuellement suivi) si fourni.
      2. Score diagnostic pour ce type (si présent).
      3. ``global_default_difficulty`` (âge + médiane diagnostic transverse).
    """
    if progress_difficulty:
        return str(progress_difficulty).strip()
    d = ctx.diagnostic_difficulty_by_type.get(exercise_type_norm)
    if d:
        return d
    return ctx.global_default_difficulty


def build_recommendation_user_context(user, db) -> RecommendationUserContext:
    """
    Construit le contexte à partir du profil, du diagnostic F03 (par type) et de la médiane globale.
    """
    age_group = normalized_age_group_from_user_profile(user)
    if not age_group and getattr(user, "preferred_difficulty", None):
        val = str(user.preferred_difficulty).lower().strip()
        if val in (
            AgeGroups.GROUP_6_8,
            AgeGroups.GROUP_9_11,
            AgeGroups.GROUP_12_14,
            AgeGroups.GROUP_15_17,
            AgeGroups.ADULT,
            AgeGroups.ALL_AGES,
        ):
            age_group = val
        elif val in ("6-8", "9-11", "12-14", "15-17", "adulte", "tous-ages"):
            age_group = val

    if not age_group and getattr(user, "grade_level", None) is not None:
        try:
            gl = int(user.grade_level)
            for (lo, hi), ag in _GRADE_TO_AGE_GROUP.items():
                if lo <= gl <= hi:
                    age_group = ag
                    break
        except (TypeError, ValueError):
            pass

    age_group = age_group or AgeGroups.ALL_AGES
    default_difficulty = get_difficulty_from_age_group(age_group)

    diagnostic_by_type: Dict[str, str] = {}

    if db is not None:
        try:
            from app.services.diagnostic.diagnostic_service import (
                _DIFFICULTY_TO_ORDINAL,
                _ORDINAL_TO_DIFFICULTY,
                get_latest_score,
            )

            latest = get_latest_score(db, user.id)
            if latest and latest.get("scores"):
                scores = latest["scores"]
                if isinstance(scores, dict):
                    for raw_key, payload in scores.items():
                        nk = normalize_exercise_type_key(raw_key)
                        if not nk:
                            continue
                        diff = None
                        if isinstance(payload, dict):
                            diff = _normalize_difficulty_string(
                                payload.get("difficulty")
                            )
                        if diff:
                            diagnostic_by_type[nk] = diff

                    ordinals = []
                    for payload in scores.values():
                        if isinstance(payload, dict) and payload.get("difficulty"):
                            ordinals.append(
                                _DIFFICULTY_TO_ORDINAL.get(
                                    str(payload.get("difficulty", "")).upper(), 1
                                )
                            )
                    if ordinals:
                        median_ordinal = sorted(ordinals)[len(ordinals) // 2]
                        default_difficulty = _ORDINAL_TO_DIFFICULTY.get(
                            median_ordinal, default_difficulty
                        )
                        logger.debug(
                            "Recommandations user=%%s: difficulté globale (médiane diagnostic) → %%s (ordinal %%s), par_type=%%s",
                            user.id,
                            default_difficulty,
                            median_ordinal,
                            diagnostic_by_type,
                        )
        except Exception as diag_err:
            logger.debug(
                "Impossible de lire le diagnostic pour user=%s: %s",
                user.id,
                diag_err,
            )

    learning_goal = getattr(user, "learning_goal", None) or ""
    practice_rhythm = getattr(user, "practice_rhythm", None) or ""

    target_tier = compute_user_target_difficulty_tier(age_group, default_difficulty)

    return RecommendationUserContext(
        age_group=age_group,
        global_default_difficulty=default_difficulty,
        learning_goal=learning_goal,
        practice_rhythm=practice_rhythm,
        diagnostic_difficulty_by_type=dict(diagnostic_by_type),
        target_difficulty_tier=target_tier,
    )
