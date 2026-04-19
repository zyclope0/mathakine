"""
F42 Phase 2 — Tier pédagogique 1–12 sur le contenu (âge × difficulté).

Matrice (ROADMAP) : 4 bandes d'âge × 3 niveaux (Découverte / Apprentissage / Consolidation).
tier = age_band_index * 3 + pedagogical_band_index + 1  →  valeurs 1..12
"""

from __future__ import annotations

from typing import Any, Literal, Optional

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
# Chaque entrée combine un descripteur quantitatif (plages numériques, opérations)
# et un marqueur cognitif explicite pour ancrer le LLM au bon niveau :
#   - DOK 1..4 : Webb's Depth of Knowledge (1997)
#   - verbes Bloom : Bloom's revised taxonomy (Anderson & Krathwohl, 2001)
# Le schéma F42 (12 cellules) reste inchangé ; seules les valeurs sont enrichies.
_TIER_CALIBRATION: dict[int, str] = {
    1: "6-8 ans – découverte : nombres 1-10, énoncés courts — DOK 1 (Remember/Understand)",
    2: "6-8 ans – apprentissage : nombres 1-20, une opération, vocabulaire simple — DOK 1-2 (Understand/Apply)",
    3: "6-8 ans – consolidation : nombres 1-50, contexte concret — DOK 2 (Apply)",
    4: "9-11 ans – découverte : nombres jusqu'à 100, opérations de base guidées — DOK 1-2 (Understand/Apply)",
    5: "9-11 ans – apprentissage : nombres jusqu'à 200, raisonnement en deux temps — DOK 2 (Apply)",
    6: "9-11 ans – consolidation : nombres jusqu'à 500, priorité opératoire, fractions simples — DOK 2-3 (Apply/Analyze)",
    7: "12-14 ans – découverte : grands nombres, fractions, introduction pourcentages — DOK 2 (Apply)",
    8: "12-14 ans – apprentissage : calculs intermédiaires, problèmes multi-étapes — DOK 2-3 (Apply/Analyze)",
    9: "12-14 ans – consolidation : raisonnement autonome, problèmes complexes — DOK 3 (Analyze/Evaluate)",
    10: "15-17 ans – découverte : abstraction, algèbre introductive — DOK 2-3 (Apply/Analyze)",
    11: "15-17 ans – apprentissage : problèmes avancés, probabilités, logique — DOK 3 (Analyze/Evaluate)",
    12: "15-17 ans / adultes – consolidation : raisonnement avancé, preuves guidées — DOK 3-4 (Evaluate/Create)",
}

_BAND_FALLBACK_CALIBRATION = {
    0: "découverte : nombres simples, opérations de base",
    1: "apprentissage : calculs intermédiaires, raisonnement guidé",
    2: "consolidation : problèmes complexes, raisonnement autonome",
}

CognitiveGuidanceKind = Literal["atomic", "multistep"]

_ATOMIC_COGNITIVE_EXERCISE_TYPES = frozenset(
    {"addition", "soustraction", "multiplication", "division"}
)
_MULTISTEP_COGNITIVE_EXERCISE_TYPES = frozenset(
    {"texte", "mixte", "fractions", "geometrie", "divers"}
)


def cognitive_guidance_kind_for_exercise_type(
    exercise_type: Optional[str],
) -> Optional[CognitiveGuidanceKind]:
    """Famille de guidance cognitive pour le prompt IA, sans supposer les types inconnus."""
    et = str(exercise_type or "").strip().lower()
    if et in _ATOMIC_COGNITIVE_EXERCISE_TYPES:
        return "atomic"
    if et in _MULTISTEP_COGNITIVE_EXERCISE_TYPES:
        return "multistep"
    return None


# Second axe cognitif (Lot E) : orthogonal à la matrice F42 — ne modifie ni tier 1..12
# ni ``pedagogical_band_index_from_difficulty``.  Consumé uniquement par le prompt IA ;
# ``ExerciseSkillState`` (Feature B) pourra surcharger ``cognitive_hint`` post-beta.
_COGNITIVE_INTENSITY_BY_DIFFICULTY: dict[str, int] = {
    "INITIE": 0,
    "PADAWAN": 1,
    "CHEVALIER": 2,
    "MAITRE": 3,
    "GRAND_MAITRE": 4,
}
_COGNITIVE_INTENSITY_HINTS_MULTISTEP: dict[int, str] = {
    0: "exploration : une règle unique, exemples guidés",
    1: "application directe : procédure standard, vocabulaire simple",
    2: "consolidation : deux étapes minimum, pas de procédure soufflée",
    3: "approfondissement : raisonnement autonome, données à organiser",
    4: (
        "maîtrise : problème non routinier, stratégie à construire, "
        "données potentiellement superflues"
    ),
}
_COGNITIVE_INTENSITY_HINTS_ATOMIC: dict[int, str] = {
    0: "exploration : opération directe guidée",
    1: "application directe : opération standard, calcul mental simple",
    2: (
        "consolidation : opération unique avec nombres moins immédiats, "
        "regroupement ou retenue possible"
    ),
    3: (
        "approfondissement : borne haute de la plage, calcul mental exigeant "
        "mais une seule opération"
    ),
    4: (
        "maîtrise : une opération unique avec grands nombres, calcul non "
        "routinier sans données superflues"
    ),
}


def cognitive_intensity_for_difficulty(
    derived_difficulty: Optional[str],
) -> Optional[int]:
    """Intensité cognitive 0..4 selon la difficulté Jedi ; ``None`` si inconnue."""
    if not derived_difficulty:
        return None
    return _COGNITIVE_INTENSITY_BY_DIFFICULTY.get(
        str(derived_difficulty).strip().upper()
    )


# ---------------------------------------------------------------------------
# Lot F — clamp runtime type-aware (pedagogical floor/ceiling per exercise_type)
# ---------------------------------------------------------------------------
# Matrice : pour chaque type d'exercice, bornes pédagogiques (plancher, plafond)
# sur l'échelle Jedi INITIE..GRAND_MAITRE. Évite les combinaisons faiblement
# pédagogiques (ex. ``addition + GRAND_MAITRE``) tout en restant fail-open pour
# les types/difficultés inconnus. La matrice doit rester LA source unique —
# tout flux de génération (cascade adaptative ou appel IA direct) lit ici.
_TYPE_DIFFICULTY_BOUNDS: dict[str, tuple[str, str]] = {
    "addition": ("INITIE", "CHEVALIER"),
    "soustraction": ("INITIE", "CHEVALIER"),
    "multiplication": ("PADAWAN", "MAITRE"),
    "division": ("PADAWAN", "MAITRE"),
    "fractions": ("PADAWAN", "GRAND_MAITRE"),
    "geometrie": ("PADAWAN", "GRAND_MAITRE"),
    "texte": ("INITIE", "GRAND_MAITRE"),
    "mixte": ("CHEVALIER", "GRAND_MAITRE"),
    "divers": ("PADAWAN", "GRAND_MAITRE"),
}

_DIFFICULTY_ORDER: tuple[str, ...] = (
    "INITIE",
    "PADAWAN",
    "CHEVALIER",
    "MAITRE",
    "GRAND_MAITRE",
)
_DIFFICULTY_RANK: dict[str, int] = {d: i for i, d in enumerate(_DIFFICULTY_ORDER)}


def clamp_difficulty_for_type(
    exercise_type: str,
    requested: str,
) -> tuple[str, Optional[str]]:
    """Clamp la difficulté demandée dans la plage autorisée pour ce type.

    Retourne le couple ``(difficulté_effective, raison)`` où ``raison`` vaut
    ``None`` si aucun clamp n'a été appliqué. Fail-open : type ou difficulté
    inconnus/vides → retour de ``requested`` sans clamp ni raison.

    La raison est une string stable, lisible et non traduite (log interne).
    """
    if not exercise_type or not requested:
        return requested, None
    type_key = str(exercise_type).strip().lower()
    diff_key = str(requested).strip().upper()
    bounds = _TYPE_DIFFICULTY_BOUNDS.get(type_key)
    if bounds is None:
        return requested, None
    rank = _DIFFICULTY_RANK.get(diff_key)
    if rank is None:
        return requested, None
    floor, ceiling = bounds
    floor_rank = _DIFFICULTY_RANK[floor]
    ceiling_rank = _DIFFICULTY_RANK[ceiling]
    if rank < floor_rank:
        return (
            floor,
            f"difficulty_below_type_floor: {diff_key} < {floor} for {type_key}",
        )
    if rank > ceiling_rank:
        return (
            ceiling,
            f"difficulty_above_type_ceiling: {diff_key} > {ceiling} for {type_key}",
        )
    return requested, None


def cognitive_hint_for_exercise_type(
    exercise_type: Optional[str],
    derived_difficulty: Optional[str],
) -> Optional[str]:
    """Phrase d'intensité cognitive compatible avec le type d'exercice."""
    intensity = cognitive_intensity_for_difficulty(derived_difficulty)
    if intensity is None:
        return None

    kind = cognitive_guidance_kind_for_exercise_type(exercise_type)
    if kind == "atomic":
        return _COGNITIVE_INTENSITY_HINTS_ATOMIC.get(intensity)
    if kind == "multistep":
        return _COGNITIVE_INTENSITY_HINTS_MULTISTEP.get(intensity)
    return None


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
      - cognitive_intensity (0–4 or None) — second axe cognitif, indépendant du tier F42
      - cognitive_hint (str or None) — ligne « intensité cognitive » pour le system prompt

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

    cognitive_intensity = cognitive_intensity_for_difficulty(derived_difficulty)
    cognitive_hint = cognitive_hint_for_exercise_type(exercise_type, derived_difficulty)

    return {
        "exercise_type": exercise_type,
        "age_group": age_group,
        "derived_difficulty": derived_difficulty,
        "difficulty_tier": tier,
        "pedagogical_band": band_label,
        "calibration_desc": cal_desc,
        "cognitive_intensity": cognitive_intensity,
        "cognitive_hint": cognitive_hint,
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
