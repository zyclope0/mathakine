"""Routes API utilisateurs."""

from starlette.routing import Route

from server.handlers.auth_handlers import api_get_current_user
from server.handlers.user_handlers import (
    create_user_account,
    delete_user,
    delete_user_me,
    export_user_data,
    get_all_user_progress,
    get_all_users,
    get_challenges_progress,
    get_user_sessions,
    get_user_stats,
    get_users_leaderboard,
    revoke_user_session,
    update_user_me,
    update_user_password_me,
)


def get_users_routes():
    return [
        Route("/api/users/", endpoint=get_all_users, methods=["GET"]),
        Route("/api/users/", endpoint=create_user_account, methods=["POST"]),
        Route("/api/users/me", endpoint=api_get_current_user, methods=["GET"]),
        Route("/api/users/me", endpoint=update_user_me, methods=["PUT"]),
        Route(
            "/api/users/me/password",
            endpoint=update_user_password_me,
            methods=["PUT"],
        ),
        Route("/api/users/me", endpoint=delete_user_me, methods=["DELETE"]),
        Route("/api/users/me/export", endpoint=export_user_data, methods=["GET"]),
        Route(
            "/api/users/me/sessions",
            endpoint=get_user_sessions,
            methods=["GET"],
        ),
        Route(
            "/api/users/me/sessions/{session_id:int}",
            endpoint=revoke_user_session,
            methods=["DELETE"],
        ),
        Route(
            "/api/users/me/progress",
            endpoint=get_all_user_progress,
            methods=["GET"],
        ),
        Route(
            "/api/users/me/challenges/progress",
            endpoint=get_challenges_progress,
            methods=["GET"],
        ),
        Route("/api/users/stats", endpoint=get_user_stats, methods=["GET"]),
        Route(
            "/api/users/leaderboard",
            endpoint=get_users_leaderboard,
            methods=["GET"],
        ),
        Route(
            "/api/users/{user_id:int}",
            endpoint=delete_user,
            methods=["DELETE"],
        ),
    ]
