"""
Service de lecture/query pour les exercices (Lot 3/A4).

Responsabilité : regrouper les accès DB pour get_exercise, liste, interleaved,
completed_ids, stats. Le handler ne fait plus d'accès DB direct.

Modèle A4 : fonctions sync exécutées via run_db_bound() depuis les handlers.
"""

from typing import Any, Dict, List, Optional

from app.core.db_boundary import sync_db_session
from app.schemas.exercise import (
    ExerciseListQuery,
    ExerciseListResponse,
    InterleavedPlanQuery,
)
from app.services.exercises.exercise_service import ExerciseService
from app.services.exercises.exercise_stats_service import ExerciseStatsService
from app.services.exercises.interleaved_practice_service import get_interleaved_plan


def get_exercise_for_api_sync(exercise_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère un exercice formaté pour l'API (sans correct_answer exposé).
    Sync, exécuté via run_db_bound().
    """
    with sync_db_session() as db:
        return ExerciseService.get_exercise_for_api(db, exercise_id)


def get_exercises_list_for_api_sync(
    query: ExerciseListQuery,
    user_id: Optional[int] = None,
) -> ExerciseListResponse:
    """
    Liste des exercices pour l'API avec pagination et filtres.
    Sync, exécuté via run_db_bound().
    """
    with sync_db_session() as db:
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


def get_interleaved_plan_for_api_sync(
    user_id: int,
    query: InterleavedPlanQuery,
) -> Dict[str, Any]:
    """
    Retourne le plan entrelacé pour l'utilisateur.
    Sync, exécuté via run_db_bound().
    """
    with sync_db_session() as db:
        return get_interleaved_plan(db, user_id, length=query.length)


def get_completed_exercise_ids_sync(user_id: int) -> List[int]:
    """
    Récupère les IDs des exercices complétés par l'utilisateur.
    Sync, exécuté via run_db_bound().
    """
    with sync_db_session() as db:
        return ExerciseService.get_user_completed_exercise_ids(db, user_id)


def get_exercises_stats_for_api_sync() -> Dict[str, Any]:
    """
    Statistiques globales des exercices pour l'API.
    Sync, exécuté via run_db_bound().
    """
    with sync_db_session() as db:
        return ExerciseStatsService.get_exercises_stats_for_api(db)
