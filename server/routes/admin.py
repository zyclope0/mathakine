"""Routes API admin (rôle admin canonique)."""

from starlette.routing import Mount, Route

from server.handlers.admin_handlers import (
    admin_ai_eval_harness_runs,
    admin_ai_stats,
    admin_audit_log,
    admin_badge_get,
    admin_badges,
    admin_badges_delete,
    admin_badges_post,
    admin_badges_put,
    admin_challenge_get,
    admin_challenges,
    admin_challenges_duplicate,
    admin_challenges_patch,
    admin_challenges_post,
    admin_challenges_put,
    admin_config_get,
    admin_config_put,
    admin_exercise_get,
    admin_exercises,
    admin_exercises_duplicate,
    admin_exercises_patch,
    admin_exercises_post,
    admin_exercises_put,
    admin_export,
    admin_f43_account_progression,
    admin_generation_metrics,
    admin_health,
    admin_moderation,
    admin_overview,
    admin_reports,
    admin_users,
    admin_users_delete,
    admin_users_patch,
    admin_users_resend_verification,
    admin_users_send_reset_password,
)
from server.handlers.analytics_handlers import admin_analytics_edtech
from server.handlers.feedback_handlers import (
    admin_delete_feedback,
    admin_list_feedback,
    admin_patch_feedback_status,
)


def get_admin_routes():
    """Mount /api/admin avec toutes les routes admin."""
    return [
        Mount(
            "/api/admin",
            routes=[
                Route("/health", endpoint=admin_health, methods=["GET"]),
                Route("/overview", endpoint=admin_overview, methods=["GET"]),
                Route(
                    "/observability/f43-account-progression",
                    endpoint=admin_f43_account_progression,
                    methods=["GET"],
                ),
                Route("/users", endpoint=admin_users, methods=["GET"]),
                Route(
                    "/users/{user_id:int}",
                    endpoint=admin_users_patch,
                    methods=["PATCH"],
                ),
                Route(
                    "/users/{user_id:int}/send-reset-password",
                    endpoint=admin_users_send_reset_password,
                    methods=["POST"],
                ),
                Route(
                    "/users/{user_id:int}/resend-verification",
                    endpoint=admin_users_resend_verification,
                    methods=["POST"],
                ),
                Route(
                    "/users/{user_id:int}",
                    endpoint=admin_users_delete,
                    methods=["DELETE"],
                ),
                Route("/exercises", endpoint=admin_exercises, methods=["GET"]),
                Route("/exercises", endpoint=admin_exercises_post, methods=["POST"]),
                Route(
                    "/exercises/{exercise_id:int}/duplicate",
                    endpoint=admin_exercises_duplicate,
                    methods=["POST"],
                ),
                Route(
                    "/exercises/{exercise_id:int}",
                    endpoint=admin_exercise_get,
                    methods=["GET"],
                ),
                Route(
                    "/exercises/{exercise_id:int}",
                    endpoint=admin_exercises_put,
                    methods=["PUT"],
                ),
                Route(
                    "/exercises/{exercise_id:int}",
                    endpoint=admin_exercises_patch,
                    methods=["PATCH"],
                ),
                Route("/challenges", endpoint=admin_challenges, methods=["GET"]),
                Route(
                    "/challenges",
                    endpoint=admin_challenges_post,
                    methods=["POST"],
                ),
                Route(
                    "/challenges/{challenge_id:int}/duplicate",
                    endpoint=admin_challenges_duplicate,
                    methods=["POST"],
                ),
                Route(
                    "/challenges/{challenge_id:int}",
                    endpoint=admin_challenge_get,
                    methods=["GET"],
                ),
                Route(
                    "/challenges/{challenge_id:int}",
                    endpoint=admin_challenges_put,
                    methods=["PUT"],
                ),
                Route(
                    "/challenges/{challenge_id:int}",
                    endpoint=admin_challenges_patch,
                    methods=["PATCH"],
                ),
                Route("/reports", endpoint=admin_reports, methods=["GET"]),
                Route("/feedback", endpoint=admin_list_feedback, methods=["GET"]),
                Route(
                    "/feedback/{feedback_id:int}",
                    endpoint=admin_patch_feedback_status,
                    methods=["PATCH"],
                ),
                Route(
                    "/feedback/{feedback_id:int}",
                    endpoint=admin_delete_feedback,
                    methods=["DELETE"],
                ),
                Route("/audit-log", endpoint=admin_audit_log, methods=["GET"]),
                Route("/moderation", endpoint=admin_moderation, methods=["GET"]),
                Route("/config", endpoint=admin_config_get, methods=["GET"]),
                Route("/config", endpoint=admin_config_put, methods=["PUT"]),
                Route("/export", endpoint=admin_export, methods=["GET"]),
                Route("/badges", endpoint=admin_badges, methods=["GET"]),
                Route("/badges", endpoint=admin_badges_post, methods=["POST"]),
                Route(
                    "/badges/{badge_id:int}",
                    endpoint=admin_badge_get,
                    methods=["GET"],
                ),
                Route(
                    "/badges/{badge_id:int}",
                    endpoint=admin_badges_put,
                    methods=["PUT"],
                ),
                Route(
                    "/badges/{badge_id:int}",
                    endpoint=admin_badges_delete,
                    methods=["DELETE"],
                ),
                Route(
                    "/analytics/edtech",
                    endpoint=admin_analytics_edtech,
                    methods=["GET"],
                ),
                Route("/ai-stats", endpoint=admin_ai_stats, methods=["GET"]),
                Route(
                    "/generation-metrics",
                    endpoint=admin_generation_metrics,
                    methods=["GET"],
                ),
                Route(
                    "/ai-eval-harness-runs",
                    endpoint=admin_ai_eval_harness_runs,
                    methods=["GET"],
                ),
            ],
        ),
    ]
