"""
Endpoints API pour la gestion des badges et achievements
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.api.deps import get_db_session, get_current_active_user
from app.services.badge_service import BadgeService
from app.models.user import User
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/user", response_model=Dict[str, Any])
async def get_current_user_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    Récupérer tous les badges de l'utilisateur connecté
    """
    try:
        badge_service = BadgeService(db)
        user_badges_data = badge_service.get_user_badges(current_user.id)
        
        return {
            "success": True,
            "data": user_badges_data
        }
    except Exception as user_badges_fetch_error:
        logger.error(f"Erreur récupération badges utilisateur {current_user.id}: {user_badges_fetch_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des badges"
        )

@router.get("/available", response_model=Dict[str, Any])
async def get_available_badges(
    db: Session = Depends(get_db_session)
):
    """
    Récupérer tous les badges disponibles dans le système
    """
    try:
        badge_service = BadgeService(db)
        available_badges = badge_service.get_available_badges()
        
        return {
            "success": True,
            "data": available_badges
        }
    except Exception as available_badges_fetch_error:
        logger.error(f"Erreur récupération badges disponibles: {available_badges_fetch_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des badges disponibles"
        )

@router.post("/check", response_model=Dict[str, Any])
async def check_user_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    Forcer la vérification des badges pour l'utilisateur connecté
    Utile pour les tests ou la synchronisation manuelle
    """
    try:
        badge_service = BadgeService(db)
        new_badges = badge_service.check_and_award_badges(current_user.id)
        
        return {
            "success": True,
            "new_badges": new_badges,
            "badges_earned": len(new_badges),
            "message": f"{len(new_badges)} nouveaux badges obtenus" if new_badges else "Aucun nouveau badge"
        }
    except Exception as badge_verification_error:
        logger.error(f"Erreur vérification badges utilisateur {current_user.id}: {badge_verification_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification des badges"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_user_gamification_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    Récupérer les statistiques de gamification complètes de l'utilisateur
    """
    try:
        badge_service = BadgeService(db)
        user_data = badge_service.get_user_badges(current_user.id)
        
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
        """), {"user_id": current_user.id}).fetchone()
        
        # Compter les badges par catégorie
        badge_stats = db.execute(text("""
            SELECT a.category, COUNT(*) as count
            FROM achievements a
            JOIN user_achievements ua ON a.id = ua.achievement_id
            WHERE ua.user_id = :user_id
            GROUP BY a.category
        """), {"user_id": current_user.id}).fetchall()
        
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
        
        return {
            "success": True,
            "data": response_data
        }
        
    except Exception as gamification_stats_error:
        logger.error(f"Erreur récupération stats gamification utilisateur {current_user.id}: {gamification_stats_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques"
        ) 