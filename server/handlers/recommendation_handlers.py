"""
Handlers pour les recommandations personnalisées.
"""

import traceback

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.services.recommendation_service import RecommendationService
from app.utils.db_utils import db_session
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.request_utils import parse_json_body_any
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)


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
            return api_error_response(400, "ID utilisateur manquant")

        async with db_session() as db:
            recommendations_data = RecommendationService.get_recommendations_for_api(
                db, user_id, limit=7
            )
            return JSONResponse(recommendations_data)
    except Exception as recommendations_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des recommandations: {recommendations_retrieval_error}"
        )
        traceback.print_exc()
        return api_error_response(
            500, get_safe_error_message(recommendations_retrieval_error)
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
            return api_error_response(400, "ID utilisateur manquant")

        async with db_session() as db:
            recommendations = RecommendationService.generate_recommendations(
                db, user_id
            )
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
        return api_error_response(
            500, get_safe_error_message(recommendations_generation_error)
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
            return api_error_response(400, "ID utilisateur manquant")

        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        data = data_or_err
        recommendation_id = data.get("recommendation_id")
        if recommendation_id is None:
            return api_error_response(400, "recommendation_id manquant")
        try:
            recommendation_id = int(recommendation_id)
        except (TypeError, ValueError):
            return api_error_response(400, "recommendation_id invalide")

        async with db_session() as db:
            success, rec = RecommendationService.mark_recommendation_as_completed(
                db, recommendation_id, user_id=user_id
            )
            if not success or not rec:
                return api_error_response(404, "Recommandation non trouvée")

        return JSONResponse(
            {"message": "Recommandation marquée comme complétée", "id": rec.id},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la recommandation complétée: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))
