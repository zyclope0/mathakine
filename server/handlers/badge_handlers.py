"""
Handlers pour la gestion des badges et achievements (API)
"""
import traceback

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.services.badge_service import BadgeService

logger = get_logger(__name__)
from app.services.enhanced_server_adapter import EnhancedServerAdapter
# NOTE: badge_service_translations archivé - utiliser BadgeService ORM uniquement
from app.utils.translation import parse_accept_language
from server.auth import get_current_user

async def get_user_badges(request):
    """Récupérer tous les badges d'un utilisateur"""
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user:
            return JSONResponse(
                {"error": "Vous devez être authentifié pour voir vos badges."},
                status_code=401
            )
        
        user_id = current_user.get('id')
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            badge_service = BadgeService(db)
            user_badges_data = badge_service.get_user_badges(user_id)
            
            return JSONResponse({
                "success": True,
                "data": user_badges_data
            })
            
        finally:
            EnhancedServerAdapter.close_db_session(db)

    except Exception as user_badges_error:
        logger.error(f"Erreur lors de la récupération des badges utilisateur: {user_badges_error}")
        traceback.print_exc()
        return JSONResponse({"error": str(user_badges_error)}, status_code=500)

async def get_available_badges(request: Request):
    """Récupérer tous les badges disponibles avec traductions"""
    try:
        # Récupérer la locale depuis le header Accept-Language
        accept_language = request.headers.get('Accept-Language', 'fr')
        locale = parse_accept_language(accept_language)
        
        # Utiliser le service ORM BadgeService
        db = EnhancedServerAdapter.get_db_session()
        try:
            badge_service = BadgeService(db)
            available_badges = badge_service.get_available_badges()
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        return JSONResponse({
            "success": True,
            "data": available_badges
        })

    except Exception as available_badges_error:
        logger.error(f"Erreur lors de la récupération des badges disponibles: {available_badges_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse({"error": str(available_badges_error)}, status_code=500)

async def check_user_badges(request):
    """Forcer la vérification des badges pour un utilisateur (utile pour les tests)"""
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user:
            return JSONResponse(
                {"error": "Vous devez être authentifié pour vérifier vos badges."},
                status_code=401
            )
        
        user_id = current_user.get('id')
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            badge_service = BadgeService(db)
            new_badges = badge_service.check_and_award_badges(user_id)
            
            return JSONResponse({
                "success": True,
                "new_badges": new_badges,
                "badges_earned": len(new_badges),
                "message": f"{len(new_badges)} nouveaux badges obtenus" if new_badges else "Aucun nouveau badge"
            })
            
        finally:
            EnhancedServerAdapter.close_db_session(db)

    except Exception as badge_verification_error:
        logger.error(f"Erreur lors de la vérification forcée des badges: {badge_verification_error}")
        traceback.print_exc()
        return JSONResponse({"error": str(badge_verification_error)}, status_code=500)

async def get_user_gamification_stats(request):
    """Récupérer les statistiques de gamification d'un utilisateur"""
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user:
            return JSONResponse(
                {"error": "Vous devez être authentifié pour voir vos statistiques."},
                status_code=401
            )
        
        user_id = current_user.get('id')
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            badge_service = BadgeService(db)
            user_data = badge_service.get_user_badges(user_id)
            
            # Ajouter des statistiques supplémentaires
            from sqlalchemy import text

            # Compter les tentatives totales et réussies
            stats = db.execute(text("""
                SELECT 
                    COUNT(*) as total_attempts,
                    COUNT(CASE WHEN is_correct THEN 1 END) as correct_attempts,
                    AVG(time_spent) as avg_time_spent
                FROM attempts 
                WHERE user_id = :user_id
            """), {"user_id": user_id}).fetchone()
            
            # Compter les badges par catégorie
            badge_stats = db.execute(text("""
                SELECT a.category, COUNT(*) as count
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = :user_id
                GROUP BY a.category
            """), {"user_id": user_id}).fetchall()
            
            response_data = {
                "user_stats": user_data.get("user_stats", {}),
                "badges_summary": {
                    "total_badges": len(user_data.get("earned_badges", [])),
                    "by_category": {row[0]: row[1] for row in badge_stats}
                },
                "performance": {
                    "total_attempts": stats[0] if stats else 0,
                    "correct_attempts": stats[1] if stats else 0,
                    "success_rate": round((stats[1] / stats[0] * 100) if stats and stats[0] > 0 else 0, 1),
                    "avg_time_spent": round(stats[2], 2) if stats and stats[2] else 0
                }
            }
            
            return JSONResponse({
                "success": True,
                "data": response_data
            })
            
        finally:
            EnhancedServerAdapter.close_db_session(db)

    except Exception as gamification_stats_error:
        logger.error(f"Erreur lors de la récupération des statistiques de gamification: {gamification_stats_error}")
        traceback.print_exc()
        return JSONResponse({"error": str(gamification_stats_error)}, status_code=500)


async def get_user_badges_progress(request: Request):
    """
    Handler pour récupérer la progression des badges d'un utilisateur (placeholder).
    Route: GET /api/challenges/badges/progress
    """
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user:
            return JSONResponse(
                {"error": "Vous devez être authentifié pour voir la progression de vos badges."},
                status_code=401
            )
        
        user_id = current_user.get('id')
        logger.info(f"Accès à la progression des badges pour l'utilisateur {user_id}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": f"La fonctionnalité de progression des badges pour l'utilisateur {user_id} est en cours de développement."},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la progression des badges: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500) 