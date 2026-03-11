"""
Service de lecture admin (LOT 4 boundary).

Centralise l'accès DB et l'appel aux sous-services pour les routes GET admin.
Les handlers restent minces : parse → call → JSONResponse.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.services.admin_service import AdminService
from app.services.analytics_service import AnalyticsService
from app.services.feedback_service import FeedbackService
from app.utils.db_utils import db_session


async def get_config_for_api() -> List[Dict[str, Any]]:
    """GET /api/admin/config — paramètres globaux."""
    async with db_session() as db:
        return AdminService.get_config_for_api(db)


async def get_overview_for_api() -> Dict[str, int]:
    """GET /api/admin/overview — KPIs globaux."""
    async with db_session() as db:
        return AdminService.get_overview_for_api(db)


async def list_users_for_admin(
    *,
    search: str = "",
    role: str = "",
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """GET /api/admin/users — liste paginée avec filtres."""
    async with db_session() as db:
        return AdminService.list_users_for_admin(
            db,
            search=search,
            role=role,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )


async def list_exercises_for_admin(
    *,
    archived: Optional[bool] = None,
    exercise_type: Optional[str] = None,
    search: str = "",
    sort: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """GET /api/admin/exercises — liste paginée."""
    async with db_session() as db:
        return AdminService.list_exercises_for_admin(
            db,
            archived=archived,
            exercise_type=exercise_type,
            search=search,
            sort=sort,
            order=order,
            skip=skip,
            limit=limit,
        )


async def get_exercise_for_admin(
    exercise_id: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """GET /api/admin/exercises/{id} — détail pour édition."""
    async with db_session() as db:
        return AdminService.get_exercise_for_admin(db, exercise_id)


async def list_badges_for_admin() -> Dict[str, Any]:
    """GET /api/admin/badges — liste tous les badges."""
    async with db_session() as db:
        return AdminService.list_badges_for_admin(db)


async def get_badge_for_admin(
    badge_id: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """GET /api/admin/badges/{id} — détail pour édition."""
    async with db_session() as db:
        return AdminService.get_badge_for_admin(db, badge_id=badge_id)


async def list_challenges_for_admin(
    *,
    archived: Optional[bool] = None,
    challenge_type: Optional[str] = None,
    search: str = "",
    sort: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """GET /api/admin/challenges — liste paginée."""
    async with db_session() as db:
        return AdminService.list_challenges_for_admin(
            db,
            archived=archived,
            challenge_type=challenge_type,
            search=search,
            sort=sort,
            order=order,
            skip=skip,
            limit=limit,
        )


async def get_challenge_for_admin(
    challenge_id: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """GET /api/admin/challenges/{id} — détail pour édition."""
    async with db_session() as db:
        return AdminService.get_challenge_for_admin(db, challenge_id)


async def get_audit_log_for_api(
    *,
    skip: int = 0,
    limit: int = 50,
    action_filter: Optional[str] = None,
    resource_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """GET /api/admin/audit-log — journal des actions admin."""
    async with db_session() as db:
        return AdminService.get_audit_log_for_api(
            db,
            skip=skip,
            limit=limit,
            action_filter=action_filter,
            resource_filter=resource_filter,
        )


async def get_moderation_for_api(
    *,
    mod_type: str = "all",
    skip: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """GET /api/admin/moderation — contenu IA pour modération."""
    async with db_session() as db:
        return AdminService.get_moderation_for_api(
            db, mod_type=mod_type, skip=skip, limit=limit
        )


async def get_reports_for_api(*, period: str = "7d") -> Dict[str, Any]:
    """GET /api/admin/reports — rapports par période."""
    async with db_session() as db:
        return AdminService.get_reports_for_api(db, period=period)


async def export_csv_data_for_admin(
    *,
    export_type: str,
    period: str,
    admin_user_id: Optional[int] = None,
) -> Tuple[List[str], List[List[Any]]]:
    """GET /api/admin/export — headers + rows pour stream CSV."""
    async with db_session() as db:
        return AdminService.export_csv_data_for_admin(
            db,
            export_type=export_type,
            period=period,
            admin_user_id=admin_user_id,
        )


async def get_edtech_analytics_for_admin(
    *,
    period: str = "7d",
    event_filter: str = "",
    limit: int = 200,
) -> Dict[str, Any]:
    """GET /api/admin/analytics/edtech — agrégats et événements EdTech."""
    since = datetime.now(timezone.utc)
    if period == "30d":
        since -= timedelta(days=30)
    else:
        since -= timedelta(days=7)
    async with db_session() as db:
        return AnalyticsService.get_edtech_analytics_for_admin(
            db,
            since=since,
            event_filter=event_filter,
            limit=limit,
        )


async def list_feedback_for_admin(limit: int = 500) -> List[Dict[str, Any]]:
    """GET /api/admin/feedback — liste des retours pour l'admin."""
    async with db_session() as db:
        return FeedbackService.list_feedback_for_admin(db, limit=limit)
