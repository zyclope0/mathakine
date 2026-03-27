"""
F42 — contexte métier pour la génération IA des défis (personnalisation profil).

Réutilise ``build_recommendation_user_context`` pour l'âge / difficulté globale ;
ne duplique pas la résolution d'âge ou de bande pédagogique.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from app.core.constants import AgeGroups, normalize_age_group
from app.core.difficulty_tier import (
    build_exercise_generation_profile,
    pedagogical_band_index_from_difficulty,
)
from app.schemas.logic_challenge import ChallengeStreamPersonalizationMeta
from app.services.recommendation.recommendation_user_context import (
    build_recommendation_user_context,
)
from app.utils.enum_mapping import age_group_exercise_from_api

_PEDAGOGICAL_BAND_LABELS = ("discovery", "learning", "consolidation")


def _band_label_from_difficulty(difficulty: str) -> str:
    idx = pedagogical_band_index_from_difficulty(difficulty)
    if idx is None:
        return "learning"
    return _PEDAGOGICAL_BAND_LABELS[idx]


def tier_to_difficulty_rating_hint(tier: Optional[int]) -> Optional[float]:
    """Mappe un tier F42 1–12 vers une cote 1.0–5.0 (hint calibration)."""
    if tier is None:
        return None
    t = int(tier)
    if t < 1 or t > 12:
        return None
    return round(1.0 + (t - 1) * (4.0 / 11.0), 2)


def _tier_and_calibration(
    resolved_age: str,
    band_label: str,
    derived_fallback: str,
) -> tuple[Optional[int], str]:
    profile = build_exercise_generation_profile(
        "sequence",
        resolved_age,
        derived_fallback,
        pedagogical_band_override=band_label,
    )
    return profile["difficulty_tier"], str(profile["calibration_desc"])


@dataclass(frozen=True)
class ChallengeGenerationUserContext:
    """Contexte figé pour prompts + calibration difficulté (audit interne)."""

    explicit_age_group: Optional[str]
    resolved_age_group: str
    age_group_source: Literal["explicit", "profile", "fallback"]
    user_context_age_group: str
    user_target_difficulty_tier: Optional[int]
    resolved_target_tier: Optional[int]
    target_pedagogical_band: str
    target_difficulty_rating_hint: Optional[float]
    calibration_text: str


def personalization_meta_from_context(
    ctx: ChallengeGenerationUserContext,
) -> ChallengeStreamPersonalizationMeta:
    return ChallengeStreamPersonalizationMeta(
        explicit_age_group=ctx.explicit_age_group,
        user_context_age_group=ctx.user_context_age_group,
        age_group_source=ctx.age_group_source,
        target_pedagogical_band=ctx.target_pedagogical_band,
        user_target_difficulty_tier=ctx.user_target_difficulty_tier,
        resolved_target_tier=ctx.resolved_target_tier,
        target_difficulty_rating_hint=ctx.target_difficulty_rating_hint,
        calibration_text=ctx.calibration_text,
    )


def build_personalization_prompt_section_from_meta(
    meta: ChallengeStreamPersonalizationMeta,
) -> str:
    """Reconstruit le bloc prompt à partir du DTO boundary (après sérialisation)."""
    tier_line = (
        f"- Niveau F42 (tier effectif) : {meta.resolved_target_tier}\n"
        if meta.resolved_target_tier is not None
        else ""
    )
    cal = (meta.calibration_text or "").strip()
    return (
        "CALIBRAGE APPRENANT (F42) — respecter pour la difficulté réelle du défi :\n"
        f"- Bande pédagogique (profil) : {meta.target_pedagogical_band}\n"
        f"{tier_line}"
        f"- Consigne de calibrage : {cal}"
    )


def build_challenge_generation_user_context(
    *,
    db,
    user,
    explicit_age_group_raw: Optional[str],
) -> ChallengeGenerationUserContext:
    """
    Résout l'âge affiché / persisté et la calibration F42.

    - Âge explicite API > âge profil pour l'enveloppe (``resolved_age_group``).
    - Bande pédagogique toujours issue du profil reco quand disponible.
    - Tier recalculé sur l'âge effectif × bande profil si âge explicite.
    """
    reco = None
    derived_fb = "PADAWAN"
    if user is not None and db is not None:
        reco = build_recommendation_user_context(user, db)
        derived_fb = reco.global_default_difficulty

    if reco is not None:
        user_ctx_age = reco.age_group
        band_label = _band_label_from_difficulty(reco.global_default_difficulty)
        user_tier = reco.target_difficulty_tier
    else:
        user_ctx_age = AgeGroups.ALL_AGES
        band_label = "learning"
        user_tier = None

    explicit_norm: Optional[str] = None
    if explicit_age_group_raw and str(explicit_age_group_raw).strip():
        explicit_norm = age_group_exercise_from_api(str(explicit_age_group_raw).strip())

    if explicit_norm:
        resolved_age = normalize_age_group(explicit_norm)
        resolved_tier, cal_text = _tier_and_calibration(
            resolved_age, band_label, derived_fb
        )
        rating_hint = tier_to_difficulty_rating_hint(resolved_tier)
        return ChallengeGenerationUserContext(
            explicit_age_group=resolved_age,
            resolved_age_group=resolved_age,
            age_group_source="explicit",
            user_context_age_group=user_ctx_age,
            user_target_difficulty_tier=user_tier,
            resolved_target_tier=resolved_tier,
            target_pedagogical_band=band_label,
            target_difficulty_rating_hint=rating_hint,
            calibration_text=cal_text,
        )

    if reco is not None and user_ctx_age != AgeGroups.ALL_AGES:
        resolved_age = normalize_age_group(user_ctx_age)
        age_group_source: Literal["explicit", "profile", "fallback"] = "profile"
        resolved_tier, cal_text = _tier_and_calibration(
            resolved_age, band_label, derived_fb
        )
    else:
        resolved_age = normalize_age_group(AgeGroups.GROUP_9_11)
        age_group_source = "fallback"
        resolved_tier, cal_text = _tier_and_calibration(
            resolved_age, band_label, derived_fb
        )

    rating_hint = tier_to_difficulty_rating_hint(resolved_tier)
    return ChallengeGenerationUserContext(
        explicit_age_group=None,
        resolved_age_group=resolved_age,
        age_group_source=age_group_source,
        user_context_age_group=user_ctx_age,
        user_target_difficulty_tier=user_tier,
        resolved_target_tier=resolved_tier,
        target_pedagogical_band=band_label,
        target_difficulty_rating_hint=rating_hint,
        calibration_text=cal_text,
    )
