"""
Service de lecture/query pour les exercices (Lot 3).

Responsabilité : regrouper les accès DB pour get_exercise, liste, interleaved,
completed_ids, stats. Le handler ne fait plus d'accès DB direct.
"""

from typing import Any, Dict, List, Optional

from app.exceptions import ExerciseNotFoundError
from app.schemas.exercise import (
    ExerciseListQuery,
    ExerciseListResponse,
    InterleavedPlanQuery,
)
from app.services.exercise_service import ExerciseService
from app.services.exercise_stats_service import ExerciseStatsService
from app.services.interleaved_practice_service import get_interleaved_plan
from app.utils.db_utils import db_session


async def get_exercise_for_api(exercise_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère un exercice formaté pour l'API (sans correct_answer exposé).
    Ouvre la session DB en interne.
    """
    async with db_session() as db:
        return ExerciseService.get_exercise_for_api(db, exercise_id)


async def get_exercises_list_for_api(
    query: ExerciseListQuery,
    user_id: Optional[int] = None,
) -> ExerciseListResponse:
    """
    Liste des exercices pour l'API avec pagination et filtres.
    Ouvre la session DB en interne.
    """
    async with db_session() as db:
        return ExerciseService.get_exercises_list_for_api(
            db,
            limit=query.limit,
            skip=query.skip,
            exercise_type=query.exercise_type,
            age_group=query.age_group,
            search=query.search,
            order=query.order,
            hide_completed=query.hide_completed,
            user_id=user_id,
        )


async def get_interleaved_plan_for_api(
    user_id: int,
    query: InterleavedPlanQuery,
) -> Dict[str, Any]:
    """
    Retourne le plan entrelacé pour l'utilisateur.
    Ouvre la session DB en interne.
    """
    async with db_session() as db:
        return get_interleaved_plan(db, user_id, length=query.length)


async def get_completed_exercise_ids(user_id: int) -> List[int]:
    """
    Récupère les IDs des exercices complétés par l'utilisateur.
    Ouvre la session DB en interne.
    """
    async with db_session() as db:
        return ExerciseService.get_user_completed_exercise_ids(db, user_id)


async def get_exercises_stats_for_api() -> Dict[str, Any]:
    """
    Statistiques globales des exercices pour l'API.
    Ouvre la session DB en interne.
    """
    async with db_session() as db:
        return ExerciseStatsService.get_exercises_stats_for_api(db)
