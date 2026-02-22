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
from server.auth import require_auth


@require_auth
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

            # Sérialiser les recommandations
            recommendations_data = []
            for rec in recommendations:
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

                # Ajouter les informations de l'exercice si disponible
                if rec.exercise_id:
                    rec_data["exercise_id"] = rec.exercise_id
                    # Optionnel: récupérer le titre et la question de l'exercice
                    try:
                        from app.services.exercise_service import ExerciseService

                        exercise = ExerciseService.get_exercise(db, rec.exercise_id)
                        if exercise:
                            rec_data["exercise_title"] = exercise.title
                            rec_data["exercise_question"] = exercise.question
                    except Exception:
                        pass  # Ignorer si l'exercice n'existe plus

                # Ajouter les informations du défi si disponible (recommandation challenge)
                if getattr(rec, "challenge_id", None):
                    rec_data["challenge_id"] = rec.challenge_id
                    try:
                        from app.services.logic_challenge_service import (
                            LogicChallengeService,
                        )

                        challenge = LogicChallengeService.get_challenge(
                            db, rec.challenge_id
                        )
                        if challenge:
                            rec_data["challenge_title"] = getattr(
                                challenge, "title", None
                            )
                            rec_data["exercise_title"] = (
                                rec_data.get("exercise_title") or challenge.title
                            )
                    except Exception:
                        pass

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
