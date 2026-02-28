"""
Parsing des paramètres pour GET /api/challenges.
Extrait et normalise les query params hors du handler.
"""

from dataclasses import dataclass
from typing import Optional

from starlette.requests import Request

import app.core.constants as constants
from app.utils.pagination import parse_pagination_params

# Import différé pour éviter cycles
# from app.services.challenge_service import normalize_age_group_for_db


@dataclass
class ListChallengesQuery:
    """Paramètres parsés pour la liste des challenges (GET /api/challenges)."""

    challenge_type: Optional[str]
    age_group_db: Optional[object]  # AgeGroup enum
    search: Optional[str]
    skip: int
    limit: int
    active_only: bool
    order: str
    hide_completed: bool


# Alias rétrocompatibilité
ChallengeListParams = ListChallengesQuery


def parse_challenge_list_params(request: Request) -> ListChallengesQuery:
    """
    Parse et normalise les paramètres de GET /api/challenges.

    Returns:
        ChallengeListParams avec valeurs prêtes pour challenge_service.
    """
    params = request.query_params
    challenge_type_raw = params.get("challenge_type")
    age_group_raw = params.get("age_group")
    search = params.get("search") or params.get("q")
    search = (search or "").strip() or None

    skip, limit = parse_pagination_params(params, default_limit=20, max_limit=100)
    active_only = (params.get("active_only", "true") or "").lower() == "true"
    order = (params.get("order") or "random").strip().lower()
    hide_completed = (params.get("hide_completed") or "false").lower() == "true"

    challenge_type = (
        constants.normalize_challenge_type(challenge_type_raw)
        if challenge_type_raw
        else None
    )

    from app.services.challenge_service import normalize_age_group_for_db

    age_group_db = normalize_age_group_for_db(age_group_raw) if age_group_raw else None

    return ListChallengesQuery(
        challenge_type=challenge_type,
        age_group_db=age_group_db,
        search=search,
        skip=skip,
        limit=limit,
        active_only=active_only,
        order=order,
        hide_completed=hide_completed,
    )
