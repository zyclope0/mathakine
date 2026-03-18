"""
Service de requête pour la boundary challenge (LOT 1).
LOT B1 : retours typés (ChallengeListResponse, ChallengeHintResponse).
"""

import json
from typing import Any, List, Optional

from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.exceptions import ChallengeNotFoundError
from app.schemas.logic_challenge import (
    ChallengeHintResponse,
    ChallengeListItem,
    ChallengeListResponse,
)
from app.services import challenge_service
from app.services.logic_challenge_service import LogicChallengeService
from app.utils.response_formatters import format_paginated_response

logger = get_logger(__name__)


def _parse_hints(hints) -> List[str]:
    """Parse hints depuis challenge (str JSON ou list)."""
    if isinstance(hints, str):
        try:
            parsed = json.loads(hints)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
    if isinstance(hints, list):
        return hints
    return []


def list_challenges_for_api(
    *,
    challenge_type: Optional[str] = None,
    age_group_db: Optional[object] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
    order: str = "random",
    hide_completed: bool = False,
    user_id: Optional[int] = None,
) -> ChallengeListResponse:
    """
    Liste des défis formatés pour l'API (GET /api/challenges).

    Returns:
        ChallengeListResponse typé
    """
    exclude_ids: List[int] = []
    with sync_db_session() as db:
        if hide_completed and user_id:
            exclude_ids = challenge_service.get_user_completed_challenges(db, user_id)

        total = challenge_service.count_challenges(
            db=db,
            challenge_type=challenge_type,
            age_group=age_group_db,
            search=search,
            exclude_ids=exclude_ids if exclude_ids else None,
            active_only=active_only,
        )
        challenges = challenge_service.list_challenges(
            db=db,
            challenge_type=challenge_type,
            age_group=age_group_db,
            search=search,
            limit=limit,
            offset=skip,
            order=order,
            exclude_ids=exclude_ids if exclude_ids else None,
            total=total if order == "random" else None,
            active_only=active_only,
        )
        challenges_list = [
            ChallengeListItem.model_validate(challenge_service.challenge_to_api_dict(c))
            for c in challenges
        ]

    data = format_paginated_response(challenges_list, total, skip, limit)
    return ChallengeListResponse.model_validate(data)


def get_challenge_detail_for_api(challenge_id: int) -> dict[str, Any]:
    """
    Récupère un défi formaté pour l'API (GET /api/challenges/{id}).
    Lève ChallengeNotFoundError si introuvable.
    Note: dict conservé (challenge_service non refactoré B1).
    """
    with sync_db_session() as db:
        return challenge_service.get_challenge_for_api(db, challenge_id)


def get_challenge_hint_for_api(challenge_id: int, level: int) -> ChallengeHintResponse:
    """
    Récupère un indice pour l'API (GET /api/challenges/{id}/hint?level=N).
    Lève ChallengeNotFoundError si défi introuvable.
    Lève ValueError si level invalide (hors plage).
    """
    with sync_db_session() as db:
        challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)
        hints = _parse_hints(challenge.hints)

        if level < 1 or level > len(hints):
            raise ValueError(f"Indice de niveau {level} non disponible")

        hint_text = hints[level - 1] if level <= len(hints) else ""
        return ChallengeHintResponse(hint=hint_text)


def get_completed_challenges_ids(user_id: int) -> List[int]:
    """
    Récupère les IDs des challenges complétés par l'utilisateur.
    """
    with sync_db_session() as db:
        return challenge_service.get_user_completed_challenges(db, user_id)
