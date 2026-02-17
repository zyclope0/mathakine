"""
Routes API pour Mathakine (backend Starlette).

Ce module définit uniquement les routes API JSON utilisées par le frontend Next.js.
Toutes les routes HTML/templates ont été supprimées (frontend géré par Next.js).
"""
from typing import List

from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route

# Imports API handlers - Admin
from server.handlers.admin_handlers import (
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
    admin_exercise_get,
    admin_exercises,
    admin_exercises_duplicate,
    admin_exercises_patch,
    admin_exercises_post,
    admin_exercises_put,
    admin_audit_log,
    admin_config_get,
    admin_config_put,
    admin_export,
    admin_health,
    admin_moderation,
    admin_overview,
    admin_reports,
    admin_users,
    admin_users_patch,
    admin_users_resend_verification,
    admin_users_send_reset_password,
)
# Imports API handlers - Auth
from server.handlers.auth_handlers import (api_get_current_user, api_login,
                                           api_refresh_token, api_validate_token,
                                           api_get_csrf_token,
                                           api_logout, api_forgot_password,
                                           api_reset_password,
                                           resend_verification_email,
                                           verify_email)
# Imports API handlers - Badges
from server.handlers.badge_handlers import (check_user_badges,
                                            get_available_badges,
                                            get_badges_rarity,
                                            get_user_badges,
                                            get_user_gamification_stats,
                                            get_user_badges_progress,
                                            patch_pinned_badges)
# Imports API handlers - Challenges
from server.handlers.challenge_handlers import (generate_ai_challenge_stream,
                                                get_challenge,
                                                get_challenge_hint,
                                                get_challenges_list,
                                                get_completed_challenges_ids,
                                                submit_challenge_answer,
                                                start_challenge,
                                                get_challenge_progress,
                                                get_challenge_rewards)
# Imports API handlers - Chat
from server.handlers.chat_handlers import chat_api, chat_api_stream
# Imports API handlers - Exercises
from server.handlers.exercise_handlers import (generate_ai_exercise_stream,
                                               generate_exercise,
                                               generate_exercise_api,
                                               get_completed_exercises_ids,
                                               get_exercise, submit_answer,
                                               delete_exercise,
                                               get_exercises_list,
                                               get_exercises_stats)
# Imports API handlers - Recommendations
from server.handlers.recommendation_handlers import (generate_recommendations,
                                                     get_recommendations,
                                                     handle_recommendation_complete)
# Imports API handlers - Users
from server.handlers.user_handlers import (create_user_account, get_all_users,
                                           get_user_stats,
                                           get_users_leaderboard,
                                           get_all_user_progress,
                                           get_user_progress_by_exercise_type,
                                           get_challenges_progress,
                                           update_user_me,
                                           update_user_password_me,
                                           delete_user,
                                           delete_user_me,
                                           export_user_data,
                                           get_user_sessions,
                                           revoke_user_session)


async def health_handler(request):
    """GET /health - Health check pour Render et load balancers."""
    return PlainTextResponse("ok", status_code=200)


async def robots_txt(request):
    """robots.txt - évite les 404 des crawlers sur le backend."""
    return PlainTextResponse(
        "User-agent: *\nDisallow: /\n",
        media_type="text/plain"
    )


async def metrics_handler(request):
    """GET /metrics - métriques Prometheus (p50/p95/p99, taux d'erreur)."""
    from app.core.monitoring import metrics_endpoint
    return await metrics_endpoint(request)


def get_routes() -> List:
    """
    Retourne la liste des routes API JSON pour le backend Starlette.
    """
    return [
        Route("/health", endpoint=health_handler, methods=["GET"]),
        Route("/robots.txt", endpoint=robots_txt, methods=["GET"]),
        Route("/metrics", endpoint=metrics_handler, methods=["GET"]),
        # ========================================
        # AUTH API (7 routes)
        # ========================================
        Route("/api/auth/login", endpoint=api_login, methods=["POST"]),
        Route("/api/auth/csrf", endpoint=api_get_csrf_token, methods=["GET"]),
        Route("/api/auth/validate-token", endpoint=api_validate_token, methods=["POST"]),
        Route("/api/auth/refresh", endpoint=api_refresh_token, methods=["POST"]),
        Route("/api/auth/logout", endpoint=api_logout, methods=["POST"]),
        Route("/api/auth/forgot-password", endpoint=api_forgot_password, methods=["POST"]),
        Route("/api/auth/reset-password", endpoint=api_reset_password, methods=["POST"]),
        Route("/api/auth/verify-email", endpoint=verify_email, methods=["GET"]),
        Route("/api/auth/resend-verification", endpoint=resend_verification_email, methods=["POST"]),
        
        # ========================================
        # USERS API (13 routes)
        # ========================================
        Route("/api/users/", endpoint=get_all_users, methods=["GET"]),
        Route("/api/users/", endpoint=create_user_account, methods=["POST"]),
        Route("/api/users/me", endpoint=api_get_current_user, methods=["GET"]),
        Route("/api/users/me", endpoint=update_user_me, methods=["PUT"]),
        Route("/api/users/me/password", endpoint=update_user_password_me, methods=["PUT"]),
        Route("/api/users/me", endpoint=delete_user_me, methods=["DELETE"]),
        Route("/api/users/me/export", endpoint=export_user_data, methods=["GET"]),
        Route("/api/users/me/sessions", endpoint=get_user_sessions, methods=["GET"]),
        Route("/api/users/me/sessions/{session_id:int}", endpoint=revoke_user_session, methods=["DELETE"]),
        Route("/api/users/me/progress", endpoint=get_all_user_progress, methods=["GET"]),
        Route("/api/users/me/progress/{exercise_type}", endpoint=get_user_progress_by_exercise_type, methods=["GET"]),
        Route("/api/users/me/challenges/progress", endpoint=get_challenges_progress, methods=["GET"]),
        Route("/api/users/stats", endpoint=get_user_stats, methods=["GET"]),
        Route("/api/users/leaderboard", endpoint=get_users_leaderboard, methods=["GET"]),
        Route("/api/users/{user_id:int}", endpoint=delete_user, methods=["DELETE"]),
        
        # ========================================
        # EXERCISES API (9 routes)
        # ========================================
        Route("/api/exercises", endpoint=get_exercises_list, methods=["GET"]),
        Route("/api/exercises/stats", endpoint=get_exercises_stats, methods=["GET"]),  # Statistiques Holocron
        Route("/api/exercises/{exercise_id:int}", endpoint=get_exercise, methods=["GET"]),
        Route("/api/exercises/{exercise_id:int}", endpoint=delete_exercise, methods=["DELETE"]),
        Route("/api/exercises/generate", endpoint=generate_exercise, methods=["GET"]),
        Route("/api/exercises/generate", endpoint=generate_exercise_api, methods=["POST"]),
        Route("/api/exercises/generate-ai-stream", endpoint=generate_ai_exercise_stream, methods=["GET"]),
        Route("/api/exercises/completed-ids", endpoint=get_completed_exercises_ids, methods=["GET"]),
        Route("/api/exercises/{exercise_id:int}/attempt", endpoint=submit_answer, methods=["POST"]),
        
        # ========================================
        # BADGES API (5 routes)
        # ========================================
        Route("/api/badges/user", endpoint=get_user_badges, methods=["GET"]),
        Route("/api/badges/available", endpoint=get_available_badges, methods=["GET"]),
        Route("/api/badges/check", endpoint=check_user_badges, methods=["POST"]),
        Route("/api/badges/stats", endpoint=get_user_gamification_stats, methods=["GET"]),
        Route("/api/badges/rarity", endpoint=get_badges_rarity, methods=["GET"]),
        Route("/api/badges/pin", endpoint=patch_pinned_badges, methods=["PATCH"]),
        Route("/api/challenges/badges/progress", endpoint=get_user_badges_progress, methods=["GET"]),
        
        # ========================================
        # ADMIN API (rôle archiviste) — Mount pour éviter conflits de routage
        # ========================================
        Mount(
            "/api/admin",
            routes=[
                Route("/health", endpoint=admin_health, methods=["GET"]),
                Route("/overview", endpoint=admin_overview, methods=["GET"]),
                Route("/users", endpoint=admin_users, methods=["GET"]),
                Route("/users/{user_id:int}", endpoint=admin_users_patch, methods=["PATCH"]),
                Route("/users/{user_id:int}/send-reset-password", endpoint=admin_users_send_reset_password, methods=["POST"]),
                Route("/users/{user_id:int}/resend-verification", endpoint=admin_users_resend_verification, methods=["POST"]),
                Route("/exercises", endpoint=admin_exercises, methods=["GET"]),
                Route("/exercises", endpoint=admin_exercises_post, methods=["POST"]),
                Route("/exercises/{exercise_id:int}/duplicate", endpoint=admin_exercises_duplicate, methods=["POST"]),
                Route("/exercises/{exercise_id:int}", endpoint=admin_exercise_get, methods=["GET"]),
                Route("/exercises/{exercise_id:int}", endpoint=admin_exercises_put, methods=["PUT"]),
                Route("/exercises/{exercise_id:int}", endpoint=admin_exercises_patch, methods=["PATCH"]),
                Route("/challenges", endpoint=admin_challenges, methods=["GET"]),
                Route("/challenges", endpoint=admin_challenges_post, methods=["POST"]),
                Route("/challenges/{challenge_id:int}/duplicate", endpoint=admin_challenges_duplicate, methods=["POST"]),
                Route("/challenges/{challenge_id:int}", endpoint=admin_challenge_get, methods=["GET"]),
                Route("/challenges/{challenge_id:int}", endpoint=admin_challenges_put, methods=["PUT"]),
                Route("/challenges/{challenge_id:int}", endpoint=admin_challenges_patch, methods=["PATCH"]),
                Route("/reports", endpoint=admin_reports, methods=["GET"]),
                Route("/audit-log", endpoint=admin_audit_log, methods=["GET"]),
                Route("/moderation", endpoint=admin_moderation, methods=["GET"]),
                Route("/config", endpoint=admin_config_get, methods=["GET"]),
                Route("/config", endpoint=admin_config_put, methods=["PUT"]),
                Route("/export", endpoint=admin_export, methods=["GET"]),
                # Lot B-1 : CRUD badges
                Route("/badges", endpoint=admin_badges, methods=["GET"]),
                Route("/badges", endpoint=admin_badges_post, methods=["POST"]),
                Route("/badges/{badge_id:int}", endpoint=admin_badge_get, methods=["GET"]),
                Route("/badges/{badge_id:int}", endpoint=admin_badges_put, methods=["PUT"]),
                Route("/badges/{badge_id:int}", endpoint=admin_badges_delete, methods=["DELETE"]),
            ],
        ),
        
        # ========================================
        # RECOMMENDATIONS API (3 routes)
        # ========================================
        Route("/api/recommendations", endpoint=get_recommendations, methods=["GET"]),
        Route("/api/recommendations/generate", endpoint=generate_recommendations, methods=["POST"]),
        Route("/api/recommendations/complete", endpoint=handle_recommendation_complete, methods=["POST"]),
        
        # ========================================
        # CHAT API (2 routes)
        # ========================================
        Route("/api/chat", endpoint=chat_api, methods=["POST"]),
        Route("/api/chat/stream", endpoint=chat_api_stream, methods=["POST"]),
        
        # ========================================
        # CHALLENGES API (10 routes) ⚠️ CRITIQUE pour Next.js
        # ========================================
        Route("/api/challenges", endpoint=get_challenges_list, methods=["GET"]),
        Route("/api/challenges/{challenge_id:int}", endpoint=get_challenge, methods=["GET"]),
        Route("/api/challenges/{challenge_id:int}/attempt", endpoint=submit_challenge_answer, methods=["POST"]),
        Route("/api/challenges/{challenge_id:int}/hint", endpoint=get_challenge_hint, methods=["GET"]),
        Route("/api/challenges/completed-ids", endpoint=get_completed_challenges_ids, methods=["GET"]),
        Route("/api/challenges/start/{challenge_id:int}", endpoint=start_challenge, methods=["POST"]),
        Route("/api/challenges/progress/{challenge_id:int}", endpoint=get_challenge_progress, methods=["GET"]),
        Route("/api/challenges/rewards/{challenge_id:int}", endpoint=get_challenge_rewards, methods=["GET"]),
        Route("/api/challenges/generate-ai-stream", endpoint=generate_ai_challenge_stream, methods=["GET"]),
        Route("/api/challenges/badges/progress", endpoint=get_user_badges_progress, methods=["GET"]),
    ]
