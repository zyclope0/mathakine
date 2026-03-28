"""
F42-C2 — Bridge progression / évaluation (legacy DB) → tier 1–12.

La persistance reste sur ``Progress.mastery_level`` (1–5), ``Progress.difficulty``,
``ChallengeProgress.mastery_level`` (string), scores diagnostic IRT ; ce module projette
ces signaux vers ``pedagogical_band`` et ``difficulty_tier`` sans migration.

Source unique pour la bande issue de ``Progress.mastery_level`` : alignée sur
``adaptive_difficulty_service`` / C1A (``MASTERY_LEVEL_TO_PEDAGOGICAL_BAND``).

Le calcul numérique du tier réutilise ``difficulty_tier.compute_tier_from_age_group_and_band``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.core.constants import AgeGroups, DifficultyLevels
from app.core.difficulty_tier import (
    DIFFICULTY_TIER_MAX,
    DIFFICULTY_TIER_MIN,
    compute_tier_from_age_group_and_band,
    pedagogical_band_index_from_difficulty,
)
from app.core.logging_config import get_logger
from app.core.user_age_group import normalized_age_group_from_user_profile

logger = get_logger(__name__)

# Doit rester identique à l’ordre utilisé dans difficulty_tier (bandes 0/1/2).
_PEDAGOGICAL_BANDS: tuple[str, ...] = ("discovery", "learning", "consolidation")

# Aligné sur C1A / adaptive_difficulty_service._MASTERY_TO_BAND (second axe génération).
MASTERY_LEVEL_TO_PEDAGOGICAL_BAND: Dict[int, str] = {
    1: "discovery",
    2: "discovery",
    3: "learning",
    4: "consolidation",
    5: "consolidation",
}

_ORDINAL_TO_AGE_GROUP: Dict[int, str] = {
    0: AgeGroups.GROUP_6_8,
    1: AgeGroups.GROUP_9_11,
    2: AgeGroups.GROUP_12_14,
    3: AgeGroups.GROUP_15_17,
    4: AgeGroups.ADULT,
}

_PREF_DIFFICULTY_TO_ORDINAL: Dict[str, int] = {
    DifficultyLevels.INITIE: 0,
    DifficultyLevels.PADAWAN: 1,
    DifficultyLevels.CHEVALIER: 2,
    DifficultyLevels.MAITRE: 3,
    DifficultyLevels.GRAND_MAITRE: 4,
    AgeGroups.GROUP_6_8: 0,
    AgeGroups.GROUP_9_11: 1,
    AgeGroups.GROUP_12_14: 2,
    AgeGroups.GROUP_15_17: 3,
    AgeGroups.ADULT: 4,
}

_GRADE_TO_ORDINAL: Dict[int, int] = {
    1: 0,
    2: 0,
    3: 0,
    4: 1,
    5: 1,
    6: 1,
    7: 2,
    8: 2,
    9: 2,
    10: 3,
    11: 3,
    12: 4,
}

DEFAULT_AGE_GROUP_FALLBACK: str = AgeGroups.GROUP_9_11


def mastery_level_int_to_pedagogical_band(mastery_level: Optional[int]) -> str:
    """``Progress.mastery_level`` (1–5) → bande C1A. Défaut ``learning`` si inconnu."""
    if mastery_level is None:
        return "learning"
    try:
        key = int(mastery_level)
    except (TypeError, ValueError):
        return "learning"
    return MASTERY_LEVEL_TO_PEDAGOGICAL_BAND.get(key, "learning")


def difficulty_string_to_pedagogical_band(difficulty: Optional[str]) -> Optional[str]:
    """``DifficultyLevels`` / easy|medium|hard → bande ; ``None`` si non mappable."""
    idx = pedagogical_band_index_from_difficulty(difficulty)
    if idx is None:
        return None
    return _PEDAGOGICAL_BANDS[idx]


def challenge_mastery_string_to_pedagogical_band(level: Optional[str]) -> str:
    """
    ``ChallengeProgress.mastery_level`` (novice / apprentice / adept / expert) → bande.

    Ordre monotone novice < apprentice < adept < expert pour l’indice de bande.
    """
    key = (level or "").strip().lower()
    mapping = {
        "novice": "discovery",
        "apprentice": "learning",
        "adept": "learning",
        "expert": "consolidation",
    }
    return mapping.get(key, "learning")


def canonical_age_group_from_user(user: Any) -> Optional[str]:
    """
    Groupe d’âge canonique sans fallback final.

    Priorité : ``users.age_group`` persisté → ``preferred_difficulty`` → ``grade_level``.
    Pas de mapping spécifique ``grade_system=suisse`` au-delà de ce que ``grade_level``
    fournit déjà (même logique que la cascade adaptative).
    """
    if user is None:
        return None
    persisted = normalized_age_group_from_user_profile(user)
    if persisted:
        return persisted

    preferred = getattr(user, "preferred_difficulty", None)
    if preferred:
        ordinal = _PREF_DIFFICULTY_TO_ORDINAL.get(preferred)
        if ordinal is not None:
            return _ORDINAL_TO_AGE_GROUP.get(ordinal)

    grade = getattr(user, "grade_level", None)
    if grade is not None and isinstance(grade, int):
        ordinal = _GRADE_TO_ORDINAL.get(grade)
        if ordinal is not None:
            return _ORDINAL_TO_AGE_GROUP.get(ordinal)
    return None


def canonical_age_group_with_fallback(user: Any) -> str:
    """Même cascade que ``canonical_age_group_from_user`` puis ``GROUP_9_11``."""
    resolved = canonical_age_group_from_user(user)
    return resolved if resolved else DEFAULT_AGE_GROUP_FALLBACK


def mastery_to_tier(
    mastery_level: Optional[int], age_group: Optional[str]
) -> Optional[int]:
    """Projete ``mastery_level`` 1–5 + tranche d’âge → tier 1–12."""
    if not age_group:
        return None
    band = mastery_level_int_to_pedagogical_band(mastery_level)
    raw = compute_tier_from_age_group_and_band(age_group, band)
    if raw is None:
        return None
    if DIFFICULTY_TIER_MIN <= raw <= DIFFICULTY_TIER_MAX:
        return raw
    logger.warning(
        "mastery_to_tier: tier out of bounds, clamping: raw=%s age_group=%s "
        "mastery_level=%s (expected %s..%s)",
        raw,
        age_group,
        mastery_level,
        DIFFICULTY_TIER_MIN,
        DIFFICULTY_TIER_MAX,
    )
    return max(DIFFICULTY_TIER_MIN, min(DIFFICULTY_TIER_MAX, int(raw)))


def tier_from_diagnostic_difficulty(
    difficulty: Optional[str], age_group: Optional[str]
) -> Optional[int]:
    """Score IRT (champ ``difficulty``) + âge → tier."""
    if not age_group:
        return None
    band = difficulty_string_to_pedagogical_band(difficulty) or "learning"
    return compute_tier_from_age_group_and_band(age_group, band)


def project_exercise_progress_f42(progress: Any, user: Any) -> Dict[str, Any]:
    """Snapshot F42 pour une ligne ``Progress`` et un utilisateur (lecture seule)."""
    canon = canonical_age_group_with_fallback(user)
    ml = getattr(progress, "mastery_level", None)
    band = mastery_level_int_to_pedagogical_band(ml)
    tier = mastery_to_tier(ml, canon)
    return {
        "canonical_age_group": canon,
        "pedagogical_band": band,
        "difficulty_tier": tier,
        "mastery_level": ml,
        "progress_difficulty_legacy": getattr(progress, "difficulty", None),
    }


def enrich_diagnostic_scores_f42(
    scores: Dict[str, Any], *, canonical_age_group: str
) -> Dict[str, Any]:
    """
    Copie enrichie des scores diagnostic : ajoute ``pedagogical_band`` et
    ``difficulty_tier`` par type (sans retirer les champs legacy).
    """
    out: Dict[str, Any] = {}
    for key, raw in scores.items():
        if not isinstance(raw, dict):
            out[key] = raw
            continue
        cell = dict(raw)
        diff = cell.get("difficulty")
        cell["pedagogical_band"] = (
            difficulty_string_to_pedagogical_band(diff) or "learning"
        )
        cell["difficulty_tier"] = tier_from_diagnostic_difficulty(
            str(diff) if diff is not None else None,
            canonical_age_group,
        )
        out[key] = cell
    return out


def project_challenge_progress_row_f42(row: Any, user: Any) -> Dict[str, Any]:
    """Snapshot F42 pour une ligne ``ChallengeProgress``."""
    canon = canonical_age_group_with_fallback(user)
    band = challenge_mastery_string_to_pedagogical_band(
        getattr(row, "mastery_level", None)
    )
    tier = compute_tier_from_age_group_and_band(canon, band)
    return {
        "canonical_age_group": canon,
        "pedagogical_band": band,
        "difficulty_tier": tier,
        "mastery_level_challenge": getattr(row, "mastery_level", None),
    }
