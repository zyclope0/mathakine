"""
Service de préparation du flux SSE IA pour défis (LOT 3 boundary).
LOT B1 : résultat typé PrepareStreamContextResult au lieu de tuple.
F42-C3A : ``age_group`` optionnel ; résolution profil via ``challenge_generation_context``.
"""

from __future__ import annotations

from typing import Optional

from app.core.config import settings
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.models.user import User
from app.schemas.logic_challenge import (
    GenerateChallengeStreamQuery,
    PrepareStreamContextResult,
)
from app.services.challenges.challenge_generation_context import (
    build_challenge_generation_user_context,
    personalization_meta_from_context,
)
from app.utils.enum_mapping import age_group_exercise_from_api
from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety
from app.utils.rate_limit import check_ai_generation_rate_limit

logger = get_logger(__name__)


def _is_profile_age_omission_marker(raw: Optional[str]) -> bool:
    """Aligné sur le frontend : valeur sentinelle = omission (résolution profil)."""
    if raw is None or not str(raw).strip():
        return False
    return str(raw).strip().lower() == "__profile__"


VALID_CHALLENGE_TYPES = [
    "sequence",
    "pattern",
    "visual",
    "puzzle",
    "graph",
    "riddle",
    "deduction",
    "chess",
    "coding",
    "probability",
]


def prepare_stream_context(
    *,
    challenge_type_raw: str = "sequence",
    age_group_raw: Optional[str] = None,
    prompt_raw: str = "",
    user_id: int | None = None,
    accept_language: str = "fr",
) -> PrepareStreamContextResult:
    """
    Prépare le contexte métier pour la génération IA streaming.

    Returns:
        PrepareStreamContextResult avec query ou error_message selon le cas.
    """
    # Validation et sanitization du prompt
    is_safe, safety_reason = validate_prompt_safety(prompt_raw)
    if not is_safe:
        logger.warning("Prompt utilisateur rejeté pour sécurité: %s", safety_reason)
        return PrepareStreamContextResult(
            query=None, error_message=f"Prompt invalide: {safety_reason}"
        )

    prompt = sanitize_user_prompt(prompt_raw)

    # Normalisation challenge_type
    challenge_type = challenge_type_raw.lower()
    if challenge_type not in VALID_CHALLENGE_TYPES:
        logger.warning(
            "Type de challenge invalide: %s, utilisation de 'sequence' par défaut",
            challenge_type_raw,
        )
        challenge_type = "sequence"

    explicit_requested = bool(age_group_raw and str(age_group_raw).strip()) and not (
        _is_profile_age_omission_marker(age_group_raw)
    )
    if explicit_requested:
        resolved_explicit = age_group_exercise_from_api(str(age_group_raw).strip())
        if not resolved_explicit:
            logger.warning("Groupe d'âge challenge invalide: %s", age_group_raw)
            return PrepareStreamContextResult(
                query=None,
                error_message="Groupe d'âge invalide",
            )
    elif not user_id:
        return PrepareStreamContextResult(
            query=None,
            error_message=(
                "Authentification requise pour omettre le groupe d'âge "
                "(utilisez le mode profil ou précisez un âge)."
            ),
        )

    if user_id:
        allowed, rate_limit_reason = check_ai_generation_rate_limit(user_id)
        if not allowed:
            logger.warning(
                "Rate limit atteint pour utilisateur %s: %s",
                user_id,
                rate_limit_reason,
            )
            return PrepareStreamContextResult(
                query=None,
                error_message=f"Limite de génération atteinte: {rate_limit_reason}",
            )

    with sync_db_session() as db:
        user = None
        if user_id is not None:
            user = db.query(User).filter(User.id == user_id).first()
        if explicit_requested:
            gen_ctx = build_challenge_generation_user_context(
                db=db,
                user=user,
                explicit_age_group_raw=str(age_group_raw).strip(),
            )
        else:
            if user is None:
                return PrepareStreamContextResult(
                    query=None,
                    error_message="Profil utilisateur introuvable pour la génération.",
                )
            gen_ctx = build_challenge_generation_user_context(
                db=db,
                user=user,
                explicit_age_group_raw=None,
            )

    age_group = gen_ctx.resolved_age_group
    personalization = personalization_meta_from_context(gen_ctx)

    # Vérification clé OpenAI
    if not settings.OPENAI_API_KEY:
        return PrepareStreamContextResult(
            query=None, error_message="OpenAI API key non configurée"
        )

    # Résolution locale
    from app.utils.translation import parse_accept_language

    locale = parse_accept_language(accept_language) or "fr"

    return PrepareStreamContextResult(
        query=GenerateChallengeStreamQuery(
            challenge_type=challenge_type,
            age_group=age_group,
            prompt=prompt,
            user_id=user_id,
            locale=locale,
            personalization=personalization,
        ),
        error_message=None,
    )
