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


_PEDAGOGICAL_BAND_LABELS = ("discovery", "learning", "consolidation")

# Tier-specific calibration: 12 cells (age_band 0-3 × ped_band 0-2 = tier 1-12).
# Each entry gives a human-readable calibration hint for the OpenAI prompt.
_TIER_CALIBRATION: dict[int, str] = {
    1: "6-8 ans – découverte : nombres 1-10, opérations très simples, énoncés courts",
    2: "6-8 ans – apprentissage : nombres 1-20, une opération, vocabulaire simple",
    3: "6-8 ans – consolidation : nombres 1-50, légère complexité, contexte concret",
    4: "9-11 ans – découverte : nombres jusqu'à 100, opérations de base guidées",
    5: "9-11 ans – apprentissage : nombres jusqu'à 200, raisonnement en deux temps",
    6: "9-11 ans – consolidation : nombres jusqu'à 500, priorité opératoire, fractions simples",
    7: "12-14 ans – découverte : grands nombres, fractions, introduction pourcentages",
    8: "12-14 ans – apprentissage : calculs intermédiaires, problèmes multi-étapes",
    9: "12-14 ans – consolidation : raisonnement autonome, problèmes complexes",
    10: "15-17 ans – découverte : abstraction, algèbre introductive",
    11: "15-17 ans – apprentissage : problèmes avancés, probabilités, logique",
    12: "15-17 ans / adultes – consolidation : grands nombres, raisonnement avancé",
}

_BAND_FALLBACK_CALIBRATION = {
    0: "découverte : nombres simples, opérations de base",
    1: "apprentissage : calculs intermédiaires, raisonnement guidé",
    2: "consolidation : problèmes complexes, raisonnement autonome",
}


def compute_tier_from_age_group_and_band(
    age_group_raw: Optional[str], pedagogical_band: str
) -> Optional[int]:
    """Compute the F42 tier (1–12) directly from an age_group and a band label.

    This is the correct way to compute the tier when the pedagogical band comes
    from a second-axis signal (e.g. mastery data) rather than from
    ``derived_difficulty``.  Two learners with the same ``age_group`` but
    different bands will receive different tiers.
    """
    from app.core.constants import normalize_age_group

    age_group = normalize_age_group(age_group_raw)
    age_idx = age_band_index_from_canonical_age_group(age_group)
    if age_idx is None:
        return None
    if pedagogical_band not in _PEDAGOGICAL_BAND_LABELS:
        return None
    band_idx = _PEDAGOGICAL_BAND_LABELS.index(pedagogical_band)
    return compute_tier_from_bands(age_idx, band_idx)


def build_exercise_generation_profile(
    exercise_type: str,
    age_group_raw: Optional[str],
    derived_difficulty: str,
    *,
    pedagogical_band_override: Optional[str] = None,
) -> dict:
    """Build an F42 generation profile usable by both local and AI generators.

    Returns a plain dict with:
      - exercise_type, age_group, derived_difficulty (legacy compat)
      - difficulty_tier (1–12 or None)
      - pedagogical_band (str: discovery / learning / consolidation)
      - calibration_desc (tier-specific hint for prompts; two distinct tiers → two distinct descs)

    When ``pedagogical_band_override`` is supplied (mastery-resolved second axis):
      - the band label is replaced by the override,
      - ``difficulty_tier`` is **recomputed** from (age_group, override_band) so that
        the tier reflects the real F42 cell, not the legacy derived_difficulty bucket,
      - ``calibration_desc`` is selected from the recomputed tier.
    """
    from app.core.constants import normalize_age_group

    age_group = normalize_age_group(age_group_raw)
    band_idx = pedagogical_band_index_from_difficulty(derived_difficulty)
    if band_idx is None:
        band_idx = 1
    band_label = _PEDAGOGICAL_BAND_LABELS[band_idx]

    if pedagogical_band_override in _PEDAGOGICAL_BAND_LABELS:
        # Second-axis path: band comes from mastery, not from derived_difficulty.
        # Recompute tier using the real (age_group × override_band) cell.
        band_label = pedagogical_band_override
        band_idx = _PEDAGOGICAL_BAND_LABELS.index(pedagogical_band_override)
        tier = compute_tier_from_age_group_and_band(age_group, band_label)
    else:
        # Legacy path: tier derived from age_group × derived_difficulty.
        tier = compute_difficulty_tier_for_exercise_strings(
            age_group, derived_difficulty
        )

    # Select calibration description from the real tier (or band fallback).
    if tier is not None:
        cal_desc = _TIER_CALIBRATION.get(tier, _BAND_FALLBACK_CALIBRATION[band_idx])
    else:
        cal_desc = _BAND_FALLBACK_CALIBRATION[band_idx]
    return {
        "exercise_type": exercise_type,
        "age_group": age_group,
        "derived_difficulty": derived_difficulty,
        "difficulty_tier": tier,
        "pedagogical_band": band_label,
        "calibration_desc": cal_desc,
    }


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
