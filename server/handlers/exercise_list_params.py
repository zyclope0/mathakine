"""
Parsing des paramètres pour GET /api/exercises.
Extrait et normalise les query params hors du handler.
Lot 3 : retourne ExerciseListQuery (Pydantic).
"""

from typing import Optional

from starlette.requests import Request

from app.schemas.exercise import ExerciseListQuery
from app.utils.pagination import parse_pagination_params


def parse_exercise_list_params(request: Request) -> ExerciseListQuery:
    """
    Parse et normalise les paramètres de GET /api/exercises.

    Returns:
        ExerciseListQuery avec valeurs prêtes pour exercise_query_service.
    """
    params = request.query_params
    skip, limit = parse_pagination_params(params, default_limit=20, max_limit=100)

    exercise_type_raw = params.get("exercise_type")
    age_group_raw = params.get("age_group")
    search = params.get("search") or params.get("q")
    search = (search or "").strip() or None
    order = (params.get("order") or "random").strip().lower()
    hide_completed = (params.get("hide_completed") or "false").lower() == "true"

    # Normaliser exercise_type et age_group uniquement si fournis
    exercise_type: Optional[str] = None
    age_group: Optional[str] = None
    if exercise_type_raw or age_group_raw:
        from server.exercise_generator import normalize_and_validate_exercise_params

        norm_type, norm_age, _ = normalize_and_validate_exercise_params(
            exercise_type_raw, age_group_raw
        )
        exercise_type = norm_type if exercise_type_raw else None
        age_group = norm_age if age_group_raw else None

    return ExerciseListQuery(
        skip=skip,
        limit=limit,
        exercise_type=exercise_type,
        age_group=age_group,
        search=search,
        order=order,
        hide_completed=hide_completed,
    )
