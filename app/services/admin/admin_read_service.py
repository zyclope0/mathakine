"""
Service de lecture admin (LOT 4 boundary).

Centralise l'accès DB et l'appel aux sous-services pour les routes GET admin.
Les handlers restent minces : parse -> run_db_bound -> JSONResponse.

LOT A6 : sync + sync_db_session, exécuté via run_db_bound() depuis les handlers.
LOT B2 : contrats explicites (AdminError) à la place des tuples (result, err, code).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.db_boundary import sync_db_session
from app.schemas.admin import AdminError
from app.services.admin.admin_service import AdminService
from app.services.analytics.analytics_service import AnalyticsService
from app.services.feedback.feedback_service import FeedbackService
from app.services.users.user_service import UserService


def get_config_for_api() -> List[Dict[str, Any]]:
    """GET /api/admin/config — paramètres globaux."""
    with sync_db_session() as db:
        return AdminService.get_config_for_api(db)


def get_overview_for_api() -> Dict[str, int]:
    """GET /api/admin/overview — KPIs globaux."""
    with sync_db_session() as db:
        return AdminService.get_overview_for_api(db)


def get_f43_account_progression_observability() -> Dict[str, Any]:
    """
    GET /api/admin/observability/f43-account-progression — F43-A1 read-only.

    Distributions des utilisateurs actifs par ``current_level`` / ``jedi_rank``
    recalculés depuis ``total_points`` (même vérité que ``/me``).
    """
    with sync_db_session() as db:
        return UserService.get_f43_account_progression_distribution(db)


def list_users_for_admin(
    *,
    search: str = "",
    role: str = "",
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """GET /api/admin/users — liste paginée avec filtres."""
    with sync_db_session() as db:
        return AdminService.list_users_for_admin(
            db,
            search=search,
            role=role,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )


def list_exercises_for_admin(
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
    with sync_db_session() as db:
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


def get_exercise_for_admin(exercise_id: int) -> Dict[str, Any]:
    """GET /api/admin/exercises/{id} — détail pour édition. Lève AdminError si non trouvé."""
    with sync_db_session() as db:
        result, err, code = AdminService.get_exercise_for_admin(db, exercise_id)
        if err:
            raise AdminError(err, code)
        return result


def list_badges_for_admin() -> Dict[str, Any]:
    """GET /api/admin/badges — liste tous les badges."""
    with sync_db_session() as db:
        return AdminService.list_badges_for_admin(db)


def get_badge_for_admin(badge_id: int) -> Dict[str, Any]:
    """GET /api/admin/badges/{id} — détail pour édition. Lève AdminError si non trouvé."""
    with sync_db_session() as db:
        result, err, code = AdminService.get_badge_for_admin(db, badge_id=badge_id)
        if err:
            raise AdminError(err, code)
        return result


def list_challenges_for_admin(
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
    with sync_db_session() as db:
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


def get_challenge_for_admin(challenge_id: int) -> Dict[str, Any]:
    """GET /api/admin/challenges/{id} — détail pour édition. Lève AdminError si non trouvé."""
    with sync_db_session() as db:
        result, err, code = AdminService.get_challenge_for_admin(db, challenge_id)
        if err:
            raise AdminError(err, code)
        return result


def get_audit_log_for_api(
    *,
    skip: int = 0,
    limit: int = 50,
    action_filter: Optional[str] = None,
    resource_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """GET /api/admin/audit-log — journal des actions admin."""
    with sync_db_session() as db:
        return AdminService.get_audit_log_for_api(
            db,
            skip=skip,
            limit=limit,
            action_filter=action_filter,
            resource_filter=resource_filter,
        )


def get_moderation_for_api(
    *,
    mod_type: str = "all",
    skip: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """GET /api/admin/moderation — contenu IA pour modération."""
    with sync_db_session() as db:
        return AdminService.get_moderation_for_api(
            db, mod_type=mod_type, skip=skip, limit=limit
        )


def get_reports_for_api(*, period: str = "7d") -> Dict[str, Any]:
    """GET /api/admin/reports — rapports par période."""
    with sync_db_session() as db:
        return AdminService.get_reports_for_api(db, period=period)


def export_csv_data_for_admin(
    *,
    export_type: str,
    period: str,
    admin_user_id: Optional[int] = None,
):
    """GET /api/admin/export — headers + rows pour stream CSV. Déprécié: utiliser AdminApplicationService.export_csv_data_for_admin."""
    with sync_db_session() as db:
        return AdminService.export_csv_data_for_admin(
            db,
            export_type=export_type,
            period=period,
            admin_user_id=admin_user_id,
        )


def get_edtech_analytics_for_admin(
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
    with sync_db_session() as db:
        return AnalyticsService.get_edtech_analytics_for_admin(
            db,
            since=since,
            event_filter=event_filter,
            limit=limit,
        )


def list_feedback_for_admin(limit: int = 500) -> List[Dict[str, Any]]:
    """GET /api/admin/feedback — liste des retours pour l'admin."""
    with sync_db_session() as db:
        return FeedbackService.list_feedback_for_admin(db, limit=limit)


def list_ai_eval_harness_runs_for_admin(*, limit: int = 20) -> Dict[str, Any]:
    """
    GET /api/admin/ai-eval-harness-runs — derniers runs persistés (IA8), read-only.

    Les coûts/tokens par cas restent des estimations ; ce n'est pas de la compta.
    """
    from app.repositories.ai_eval_harness_repository import AiEvalHarnessRepository

    cap = max(1, min(limit, 100))
    with sync_db_session() as db:
        runs = AiEvalHarnessRepository.list_recent_runs(db, limit=cap)
        return {
            "runs": [AiEvalHarnessRepository.run_to_summary_dict(r) for r in runs],
            "limit": cap,
            "disclaimer_fr": (
                "Runs d'évaluation (harness) persistés : mode offline/live, corpus et compteurs figés "
                "au moment du run. Distinct des agrégats runtime in-memory."
            ),
        }
