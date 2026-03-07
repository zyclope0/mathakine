"""
Facade AdminService — délègue aux sous-services spécialisés.

Préserve la compatibilité avec admin_handlers.py qui importe
``from app.services.admin_service import AdminService``.

Phase 3, item 3.3 — audit architecture 03/2026.
"""

from app.services.admin_config_service import AdminConfigService  # noqa: F401
from app.services.admin_content_service import AdminContentService  # noqa: F401
from app.services.admin_helpers import CONFIG_SCHEMA  # noqa: F401
from app.services.admin_stats_service import AdminStatsService  # noqa: F401
from app.services.admin_user_service import AdminUserService  # noqa: F401


class AdminService:
    """Facade réexportant toutes les opérations admin."""

    # ── Config ────────────────────────────────────────────────────────────
    get_config_for_api = AdminConfigService.get_config_for_api
    update_config = AdminConfigService.update_config

    # ── Stats ─────────────────────────────────────────────────────────────
    get_overview_for_api = AdminStatsService.get_overview_for_api
    get_audit_log_for_api = AdminStatsService.get_audit_log_for_api
    get_moderation_for_api = AdminStatsService.get_moderation_for_api
    get_reports_for_api = AdminStatsService.get_reports_for_api

    # ── Users ─────────────────────────────────────────────────────────────
    ROLE_MAP = AdminUserService.ROLE_MAP
    list_users_for_admin = AdminUserService.list_users_for_admin
    validate_and_patch_user = AdminUserService.validate_and_patch_user
    patch_user_for_admin = AdminUserService.patch_user_for_admin
    send_reset_password_for_admin = AdminUserService.send_reset_password_for_admin
    resend_verification_for_admin = AdminUserService.resend_verification_for_admin
    delete_user_for_admin = AdminUserService.delete_user_for_admin

    # ── Content (badges, exercises, challenges, export) ───────────────────
    _achievement_to_detail = AdminContentService._achievement_to_detail
    _validate_badge_requirements = AdminContentService._validate_badge_requirements
    list_badges_for_admin = AdminContentService.list_badges_for_admin
    create_badge_for_admin = AdminContentService.create_badge_for_admin
    get_badge_for_admin = AdminContentService.get_badge_for_admin
    put_badge_for_admin = AdminContentService.put_badge_for_admin
    delete_badge_for_admin = AdminContentService.delete_badge_for_admin

    _exercise_to_detail = AdminContentService._exercise_to_detail
    list_exercises_for_admin = AdminContentService.list_exercises_for_admin
    create_exercise_for_admin = AdminContentService.create_exercise_for_admin
    get_exercise_for_admin = AdminContentService.get_exercise_for_admin
    put_exercise_for_admin = AdminContentService.put_exercise_for_admin
    duplicate_exercise_for_admin = AdminContentService.duplicate_exercise_for_admin
    patch_exercise_for_admin = AdminContentService.patch_exercise_for_admin

    _challenge_to_detail = AdminContentService._challenge_to_detail
    list_challenges_for_admin = AdminContentService.list_challenges_for_admin
    create_challenge_for_admin = AdminContentService.create_challenge_for_admin
    get_challenge_for_admin = AdminContentService.get_challenge_for_admin
    put_challenge_for_admin = AdminContentService.put_challenge_for_admin
    duplicate_challenge_for_admin = AdminContentService.duplicate_challenge_for_admin
    patch_challenge_for_admin = AdminContentService.patch_challenge_for_admin

    export_csv_data_for_admin = AdminContentService.export_csv_data_for_admin
