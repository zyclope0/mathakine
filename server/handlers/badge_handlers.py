"""
Handlers pour la gestion des badges et achievements (API)
LOT A6 : appels via run_db_bound() vers facades sync.
"""

import traceback

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.schemas.badge import PinnedBadgesRequest
from app.services.badges.badge_application_service import BadgeApplicationService
from app.services.badges.badge_user_view_service import (
    AVAILABLE_BADGES_DEFAULT_LIMIT,
    AVAILABLE_BADGES_MAX_LIMIT,
)
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.pagination import parse_pagination_params
from app.utils.request_utils import parse_json_body_any
from app.utils.simple_ttl_cache import get_or_set
from app.utils.translation import parse_accept_language
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)


@require_auth
async def get_user_badges(request: Request) -> JSONResponse:
    """Récupérer tous les badges d'un utilisateur"""
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        data = await run_db_bound(BadgeApplicationService.get_user_badges, user_id)
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération des badges utilisateur: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


async def get_available_badges(request: Request) -> JSONResponse:
    """Récupérer les badges disponibles (borné, D5). GET ?limit=N (défaut 100, max 200)."""
    try:
        accept_language = request.headers.get("Accept-Language", "fr")
        parse_accept_language(accept_language)

        _, limit = parse_pagination_params(
            request.query_params,
            default_limit=AVAILABLE_BADGES_DEFAULT_LIMIT,
            max_limit=AVAILABLE_BADGES_MAX_LIMIT,
        )
        available_badges = await run_db_bound(
            BadgeApplicationService.get_available_badges, limit=limit
        )
        return JSONResponse({"success": True, "data": available_badges})
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des badges disponibles: {e}")
        logger.debug(traceback.format_exc())
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def check_user_badges(request: Request) -> JSONResponse:
    """Forcer la vérification des badges pour un utilisateur (utile pour les tests)"""
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        new_badges = await run_db_bound(
            BadgeApplicationService.check_and_award_badges, user_id
        )
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
    except Exception as e:
        logger.error(
            f"Erreur lors de la vérification forcée des badges: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def get_user_gamification_stats(request: Request) -> JSONResponse:
    """Récupérer les statistiques de gamification d'un utilisateur (cache TTL 60s)."""
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        async def _fetch():
            return await run_db_bound(
                BadgeApplicationService.get_user_gamification_stats, user_id
            )

        response_data = await get_or_set(f"gamification_stats:{user_id}", 60.0, _fetch)
        return JSONResponse({"success": True, "data": response_data})
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération des statistiques de gamification: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def patch_pinned_badges(request: Request) -> JSONResponse:
    """A-4 : Épingler 1-3 badges. Body: { "badge_ids": [1, 2, 3] }"""
    body_or_err = await parse_json_body_any(request)
    if isinstance(body_or_err, JSONResponse):
        return body_or_err

    try:
        payload = PinnedBadgesRequest.model_validate(body_or_err)
    except ValidationError as ve:
        err_msg = (
            ve.errors()[0].get("msg", str(ve))
            if ve.errors()
            else "badge_ids doit être une liste d'entiers"
        )
        return api_error_response(400, err_msg)

    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return api_error_response(401, "Non authentifié")

        result = await run_db_bound(
            BadgeApplicationService.set_pinned_badges,
            user_id,
            payload.badge_ids,
        )
        return JSONResponse(
            {"success": True, "data": {"pinned_badge_ids": result.pinned_badge_ids}}
        )
    except Exception as e:
        logger.error(f"Erreur patch_pinned_badges: {e}", exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


async def get_badges_rarity(request: Request) -> JSONResponse:
    """
    Stats rareté par badge (unlock_percent, rarity).
    GET /api/badges/rarity — public (pas de données sensibles). Cache TTL 90s.
    """
    try:

        async def _fetch():
            return await run_db_bound(BadgeApplicationService.get_badges_rarity_stats)

        data = await get_or_set("badges_rarity", 90.0, _fetch)
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erreur get_badges_rarity: {e}", exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_user_badges_progress(request: Request) -> JSONResponse:
    """
    Progression vers les badges (débloqués + en cours).
    Route: GET /api/challenges/badges/progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return api_error_response(400, "ID utilisateur manquant")

        data = await run_db_bound(BadgeApplicationService.get_badges_progress, user_id)
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de la progression des badges: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))
