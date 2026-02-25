"""
Handlers pour les recommandations personnalisées.
"""

import traceback
from datetime import datetime, timezone

from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.models.recommendation import Recommendation
from app.utils.db_utils import db_session
from app.utils.error_handler import get_safe_error_message

logger = get_logger(__name__)
from app.services.recommendation_service import RecommendationService
from server.auth import require_auth, require_full_access


@require_auth
@require_full_access
async def get_recommendations(request):
    """
    Récupère les recommandations personnalisées pour l'utilisateur connecté.
    Route: GET /api/recommendations
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)

        async with db_session() as db:
            recommendations = RecommendationService.get_user_recommendations(
                db, user_id, limit=7
            )

            # Si aucune recommandation n'existe, générer de nouvelles
            if not recommendations:
                try:
                    RecommendationService.generate_recommendations(db, user_id)
                    db.commit()
                    recommendations = RecommendationService.get_user_recommendations(
                        db, user_id, limit=7
                    )
                except Exception as gen_error:
                    logger.error(
                        f"Erreur lors de la génération des recommandations: {str(gen_error)}"
                    )
                    traceback.print_exc()
                    recommendations = []

            # Mapping difficulté → groupe d'âge (inverse du mapping age_group → difficulty)
            difficulty_to_age_group = {
                "INITIE": "6-8",
                "PADAWAN": "9-11",
                "CHEVALIER": "12-14",
                "MAITRE": "15-17",
                "GRAND_MAITRE": "adulte",
            }

            # Sérialiser les recommandations (exclure exercices/défis archivés ou déjà réussis)
            from app.models.attempt import Attempt
            from app.models.exercise import Exercise
            from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt

            # Exercices déjà réussis
            completed_exercise_ids = {
                a.exercise_id
                for a in db.query(Attempt)
                .filter(
                    Attempt.user_id == user_id,
                    Attempt.is_correct == True,
                    Attempt.exercise_id.isnot(None),
                )
                .all()
                if a.exercise_id
            }

            # Défis déjà réussis par l'utilisateur — ne pas les proposer
            completed_challenge_ids = {
                a.challenge_id
                for a in db.query(LogicChallengeAttempt)
                .filter(
                    LogicChallengeAttempt.user_id == user_id,
                    LogicChallengeAttempt.is_correct == True,
                    LogicChallengeAttempt.challenge_id.isnot(None),
                )
                .all()
                if a.challenge_id
            }

            recommendations_data = []
            for rec in recommendations:
                exercise = None
                challenge = None

                # Exclure si l'exercice lié est archivé, inactif ou déjà réussi
                if rec.exercise_id:
                    if rec.exercise_id in completed_exercise_ids:
                        continue  # Ne pas proposer un exercice déjà réussi
                    exercise = (
                        db.query(Exercise)
                        .filter(Exercise.id == rec.exercise_id)
                        .first()
                    )
                    if (
                        not exercise
                        or exercise.is_archived
                        or not getattr(exercise, "is_active", True)
                    ):
                        continue  # Ne pas proposer un exercice archivé/inactif

                # Exclure si le défi lié est archivé ou déjà réussi
                if getattr(rec, "challenge_id", None):
                    if rec.challenge_id in completed_challenge_ids:
                        continue  # Ne pas proposer un défi déjà réussi
                    challenge = (
                        db.query(LogicChallenge)
                        .filter(LogicChallenge.id == rec.challenge_id)
                        .first()
                    )
                    if not challenge or getattr(challenge, "is_archived", False):
                        continue  # Ne pas proposer un défi archivé

                difficulty_str = (
                    str(rec.difficulty).upper() if rec.difficulty else "PADAWAN"
                )
                age_group = difficulty_to_age_group.get(difficulty_str, "9-11")

                rec_data = {
                    "id": rec.id,
                    "exercise_type": str(rec.exercise_type),
                    "difficulty": difficulty_str,
                    "age_group": age_group,
                    "reason": rec.reason or "",
                    "priority": rec.priority,
                    "recommendation_type": getattr(rec, "recommendation_type", None)
                    or "exercise",
                }

                # Ajouter les informations de l'exercice si disponible (exercise déjà chargé)
                if rec.exercise_id and exercise:
                    rec_data["exercise_id"] = rec.exercise_id
                    rec_data["exercise_title"] = exercise.title
                    rec_data["exercise_question"] = getattr(exercise, "question", None)

                # Ajouter les informations du défi si disponible (challenge déjà chargé)
                if getattr(rec, "challenge_id", None) and challenge:
                    rec_data["challenge_id"] = rec.challenge_id
                    rec_data["challenge_title"] = getattr(challenge, "title", None)
                    rec_data["exercise_title"] = (
                        rec_data.get("exercise_title") or challenge.title
                    )

                recommendations_data.append(rec_data)

            return JSONResponse(recommendations_data)
    except Exception as recommendations_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des recommandations: {recommendations_retrieval_error}"
        )
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(recommendations_retrieval_error)},
            status_code=500,
        )


@require_auth
@require_full_access
async def generate_recommendations(request):
    """
    Génère de nouvelles recommandations pour l'utilisateur connecté.
    Route: POST /api/recommendations/generate
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)

        async with db_session() as db:
            recommendations = RecommendationService.generate_recommendations(
                db, user_id
            )
            db.commit()
            return JSONResponse(
                {
                    "message": "Recommandations générées avec succès",
                    "count": len(recommendations) if recommendations else 0,
                }
            )
    except Exception as recommendations_generation_error:
        logger.error(
            f"Erreur lors de la génération des recommandations: {recommendations_generation_error}"
        )
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(recommendations_generation_error)},
            status_code=500,
        )


@require_auth
@require_full_access
async def handle_recommendation_complete(request):
    """
    Marquer une recommandation comme complétée.
    Route: POST /api/recommendations/complete
    Body: { "recommendation_id": int }
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)

        data = await request.json()
        recommendation_id = data.get("recommendation_id")
        if recommendation_id is None:
            return JSONResponse(
                {"error": "recommendation_id manquant"}, status_code=400
            )
        try:
            recommendation_id = int(recommendation_id)
        except (TypeError, ValueError):
            return JSONResponse(
                {"error": "recommendation_id invalide"}, status_code=400
            )

        async with db_session() as db:
            rec = (
                db.query(Recommendation)
                .filter(
                    Recommendation.id == recommendation_id,
                    Recommendation.user_id == user_id,
                )
                .first()
            )
            if not rec:
                return JSONResponse(
                    {"error": "Recommandation non trouvée"}, status_code=404
                )
            rec.is_completed = True
            rec.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(rec)

        return JSONResponse(
            {"message": "Recommandation marquée comme complétée", "id": rec.id},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la recommandation complétée: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)
