"""
F42 Phase 2 — Tier pédagogique 1–12 sur le contenu (âge × difficulté).

Matrice (ROADMAP) : 4 bandes d'âge × 3 niveaux (Découverte / Apprentissage / Consolidation).
tier = age_band_index * 3 + pedagogical_band_index + 1  →  valeurs 1..12
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.constants import AgeGroups, normalize_age_group

DIFFICULTY_TIER_MIN = 1
DIFFICULTY_TIER_MAX = 12

_ALL_AGES_LITERALS = frozenset(
    {
        "tous-ages",
        "tous ages",
        "all_ages",
        "all ages",
        "all",
    }
)


def age_band_index_from_canonical_age_group(canonical: str) -> Optional[int]:
    """Index 0..3 pour la matrice F42 ; ``None`` si indéterminé ou ``ALL_AGES``."""
    if not canonical or canonical == AgeGroups.ALL_AGES:
        return None
    if canonical == AgeGroups.GROUP_6_8:
        return 0
    if canonical == AgeGroups.GROUP_9_11:
        return 1
    if canonical == AgeGroups.GROUP_12_14:
        return 2
    if canonical in (AgeGroups.GROUP_15_17, AgeGroups.ADULT):
        return 3
    return None


def pedagogical_band_index_from_difficulty(difficulty: Optional[str]) -> Optional[int]:
    """
    Mappe la difficulté stockée (Jedi ou easy/medium/hard) vers 0/1/2.
    """
    if difficulty is None:
        return None
    d = str(difficulty).strip().upper()
    if not d:
        return None
    if d in ("INITIE", "EASY", "E"):
        return 0
    if d in ("PADAWAN", "MEDIUM", "M"):
        return 1
    if d in ("CHEVALIER", "MAITRE", "GRAND_MAITRE", "HARD", "H"):
        return 2
    return None


def pedagogical_band_index_from_rating(rating: Optional[float]) -> int:
    """Fallback défis : échelle 1–5 → bande 0/1/2."""
    if rating is None:
        return 1
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return 1
    if r <= 2.0:
        return 0
    if r <= 3.5:
        return 1
    return 2


def compute_tier_from_bands(
    age_band_index: Optional[int], pedagogical_band_index: Optional[int]
) -> Optional[int]:
    if age_band_index is None or pedagogical_band_index is None:
        return None
    if age_band_index < 0 or age_band_index > 3:
        return None
    if pedagogical_band_index < 0 or pedagogical_band_index > 2:
        return None
    tier = age_band_index * 3 + pedagogical_band_index + 1
    if tier < DIFFICULTY_TIER_MIN or tier > DIFFICULTY_TIER_MAX:
        return None
    return tier


def compute_difficulty_tier_for_exercise_strings(
    age_group_raw: Optional[str], difficulty_raw: Optional[str]
) -> Optional[int]:
    """
    Tier pour un exercice à partir des colonnes ``age_group`` / ``difficulty``.
    ``tous-ages`` explicite → ``None`` (pas de cellule unique).
    """
    raw = str(age_group_raw or "").lower().strip()
    if raw.replace(" ", "") in _ALL_AGES_LITERALS:
        return None
    if not str(age_group_raw or "").strip():
        return None
    canon = normalize_age_group(age_group_raw)
    age_idx = age_band_index_from_canonical_age_group(canon)
    diff_idx = pedagogical_band_index_from_difficulty(difficulty_raw)
    return compute_tier_from_bands(age_idx, diff_idx)


def compute_user_target_difficulty_tier(
    user_age_group: str, target_difficulty: str
) -> Optional[int]:
    """
    Tier côté utilisateur pour le filtrage reco (fenêtre ±1 sur le tier).
    ``ALL_AGES`` → ``None`` (comportement historique : pas de filtre tier).
    """
    if not user_age_group or user_age_group == AgeGroups.ALL_AGES:
        return None
    canon = normalize_age_group(user_age_group)
    age_idx = age_band_index_from_canonical_age_group(canon)
    diff_idx = pedagogical_band_index_from_difficulty(target_difficulty)
    return compute_tier_from_bands(age_idx, diff_idx)


def age_band_index_from_logic_challenge_age_group(age_group: Any) -> Optional[int]:
    """Mappe l'enum ``AgeGroup`` des défis logiques vers 0..3."""
    from app.models.logic_challenge import AgeGroup as ChAge

    if age_group is None:
        return None
    if age_group == ChAge.GROUP_6_8:
        return 0
    if age_group == ChAge.GROUP_10_12:
        return 1
    if age_group == ChAge.GROUP_13_15:
        return 2
    if age_group in (ChAge.GROUP_15_17, ChAge.ADULT):
        return 3
    if age_group == ChAge.ALL_AGES:
        return None
    return None


def compute_difficulty_tier_for_logic_challenge(
    age_group: Any,
    difficulty: Optional[str],
    difficulty_rating: Optional[float],
) -> Optional[int]:
    """Tier pour un ``LogicChallenge`` (difficulty string prioritaire, sinon rating)."""
    age_idx = age_band_index_from_logic_challenge_age_group(age_group)
    diff_idx = pedagogical_band_index_from_difficulty(difficulty)
    if diff_idx is None:
        diff_idx = pedagogical_band_index_from_rating(difficulty_rating)
    return compute_tier_from_bands(age_idx, diff_idx)


def assign_exercise_difficulty_tier(exercise: Any) -> None:
    """Met à jour ``exercise.difficulty_tier`` en place (ORM)."""
    tier = compute_difficulty_tier_for_exercise_strings(
        getattr(exercise, "age_group", None),
        getattr(exercise, "difficulty", None),
    )
    exercise.difficulty_tier = tier


def assign_logic_challenge_difficulty_tier(challenge: Any) -> None:
    """Met à jour ``challenge.difficulty_tier`` en place (ORM)."""
    tier = compute_difficulty_tier_for_logic_challenge(
        getattr(challenge, "age_group", None),
        getattr(challenge, "difficulty", None),
        getattr(challenge, "difficulty_rating", None),
    )
    challenge.difficulty_tier = tier


def exercise_tier_filter_expression(user_tier: Optional[int], target_difficulty: str):
    """Expression de filtre pour ``Exercise`` (requêtes recommandations)."""
    from sqlalchemy import and_, or_

    from app.models.exercise import Exercise

    td = target_difficulty
    if user_tier is None:
        return Exercise.difficulty == td
    lo = max(DIFFICULTY_TIER_MIN, user_tier - 1)
    hi = min(DIFFICULTY_TIER_MAX, user_tier + 1)
    return or_(
        and_(Exercise.difficulty_tier.is_(None), Exercise.difficulty == td),
        Exercise.difficulty_tier.between(lo, hi),
    )
