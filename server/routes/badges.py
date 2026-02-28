"""Routes API badges."""

from starlette.routing import Route

from server.handlers.badge_handlers import (
    check_user_badges,
    get_available_badges,
    get_badges_rarity,
    get_user_badges,
    get_user_badges_progress,
    get_user_gamification_stats,
    patch_pinned_badges,
)


def get_badges_routes():
    return [
        Route("/api/badges/user", endpoint=get_user_badges, methods=["GET"]),
        Route(
            "/api/badges/available",
            endpoint=get_available_badges,
            methods=["GET"],
        ),
        Route(
            "/api/badges/check",
            endpoint=check_user_badges,
            methods=["POST"],
        ),
        Route(
            "/api/badges/stats",
            endpoint=get_user_gamification_stats,
            methods=["GET"],
        ),
        Route(
            "/api/badges/rarity",
            endpoint=get_badges_rarity,
            methods=["GET"],
        ),
        Route(
            "/api/badges/pin",
            endpoint=patch_pinned_badges,
            methods=["PATCH"],
        ),
        Route(
            "/api/challenges/badges/progress",
            endpoint=get_user_badges_progress,
            methods=["GET"],
        ),
    ]
