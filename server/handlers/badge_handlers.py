"""
Handlers pour la gestion des badges et achievements (API)
"""

import json
import traceback

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.services.badge_service import BadgeService
from app.utils.db_utils import db_session
from app.utils.error_handler import get_safe_error_message

logger = get_logger(__name__)
# NOTE: badge_service_translations archivé - utiliser BadgeService ORM uniquement
from app.utils.translation import parse_accept_language
from server.auth import require_auth


@require_auth
async def get_user_badges(request):
    """Récupérer tous les badges d'un utilisateur"""
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        async with db_session() as db:
            badge_service = BadgeService(db)
            user_badges_data = badge_service.get_user_badges(user_id)
            return JSONResponse({"success": True, "data": user_badges_data})

    except Exception as user_badges_error:
        logger.error(
            f"Erreur lors de la récupération des badges utilisateur: {user_badges_error}"
        )
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(user_badges_error)}, status_code=500
        )


async def get_available_badges(request: Request):
    """Récupérer tous les badges disponibles avec traductions"""
    try:
        accept_language = request.headers.get("Accept-Language", "fr")
        parse_accept_language(accept_language)

        async with db_session() as db:
            badge_service = BadgeService(db)
            available_badges = badge_service.get_available_badges()

        return JSONResponse({"success": True, "data": available_badges})

    except Exception as available_badges_error:
        logger.error(
            f"Erreur lors de la récupération des badges disponibles: {available_badges_error}"
        )
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": get_safe_error_message(available_badges_error)}, status_code=500
        )


@require_auth
async def check_user_badges(request):
    """Forcer la vérification des badges pour un utilisateur (utile pour les tests)"""
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        async with db_session() as db:
            badge_service = BadgeService(db)
            new_badges = badge_service.check_and_award_badges(user_id)
            return JSONResponse(
                {
                    "success": True,
                    "new_badges": new_badges,
                    "badges_earned": len(new_badges),
                    "message": (
                        f"{len(new_badges)} nouveaux badges obtenus"
                        if new_badges
                        else "Aucun nouveau badge"
                    ),
                }
            )

    except Exception as badge_verification_error:
        logger.error(
            f"Erreur lors de la vérification forcée des badges: {badge_verification_error}"
        )
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(badge_verification_error)}, status_code=500
        )


@require_auth
async def get_user_gamification_stats(request):
    """Récupérer les statistiques de gamification d'un utilisateur"""
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        async with db_session() as db:
            from sqlalchemy import text

            badge_service = BadgeService(db)
            user_data = badge_service.get_user_badges(user_id)

            stats = db.execute(
                text("""
                SELECT
                    COUNT(*) as total_attempts,
                    COUNT(CASE WHEN is_correct THEN 1 END) as correct_attempts,
                    AVG(time_spent) as avg_time_spent
                FROM attempts
                WHERE user_id = :user_id
            """),
                {"user_id": user_id},
            ).fetchone()

            badge_stats = db.execute(
                text("""
                SELECT a.category, COUNT(*) as count
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = :user_id
                GROUP BY a.category
            """),
                {"user_id": user_id},
            ).fetchall()

            response_data = {
                "user_stats": user_data.get("user_stats", {}),
                "badges_summary": {
                    "total_badges": len(user_data.get("earned_badges", [])),
                    "by_category": {row[0]: row[1] for row in badge_stats},
                },
                "performance": {
                    "total_attempts": stats[0] if stats else 0,
                    "correct_attempts": stats[1] if stats else 0,
                    "success_rate": round(
                        (stats[1] / stats[0] * 100) if stats and stats[0] > 0 else 0, 1
                    ),
                    "avg_time_spent": round(stats[2], 2) if stats and stats[2] else 0,
                },
            }
            return JSONResponse({"success": True, "data": response_data})

    except Exception as gamification_stats_error:
        logger.error(
            f"Erreur lors de la récupération des statistiques de gamification: {gamification_stats_error}"
        )
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(gamification_stats_error)}, status_code=500
        )


@require_auth
async def patch_pinned_badges(request: Request):
    """A-4 : Épingler 1-3 badges. Body: { "badge_ids": [1, 2, 3] }"""
    try:
        body = await request.json()
        badge_ids = body.get("badge_ids", [])
        if not isinstance(badge_ids, list):
            return JSONResponse(
                {"error": "badge_ids doit être une liste"}, status_code=400
            )
        badge_ids = [int(x) for x in badge_ids if isinstance(x, (int, float))]
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        async with db_session() as db:
            badge_service = BadgeService(db)
            pinned = badge_service.set_pinned_badges(user_id, badge_ids)
        return JSONResponse({"success": True, "data": {"pinned_badge_ids": pinned}})
    except json.JSONDecodeError:
        return JSONResponse({"error": "JSON invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur patch_pinned_badges: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


async def get_badges_rarity(request: Request):
    """
    Stats rareté par badge (unlock_percent, rarity).
    GET /api/badges/rarity — public (pas de données sensibles).
    """
    try:
        async with db_session() as db:
            badge_service = BadgeService(db)
            data = badge_service.get_badges_rarity_stats()
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erreur get_badges_rarity: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def get_user_badges_progress(request: Request):
    """
    Progression vers les badges (débloqués + en cours).
    Route: GET /api/challenges/badges/progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)

        async with db_session() as db:
            badge_service = BadgeService(db)
            data = badge_service.get_badges_progress(user_id)

        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de la progression des badges: {e}"
        )
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)
