"""
Handlers pour les defis quotidiens (F02).

Route: GET /api/daily-challenges - recupere les defis du jour (cree si absent).
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.progress.daily_challenge_service import (
    get_or_create_today_for_user_sync,
)
from app.utils.error_handler import api_error_response, capture_internal_error_response
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)


@require_auth
@require_full_access
async def get_daily_challenges(request: Request) -> JSONResponse:
    """
    Recupere les defis quotidiens du jour pour l'utilisateur connecte.
    Les cree automatiquement s'ils n'existent pas.
    Route: GET /api/daily-challenges
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return api_error_response(400, "ID utilisateur manquant")

        data = await run_db_bound(get_or_create_today_for_user_sync, user_id)
        return JSONResponse({"challenges": data})

    except Exception as e:
        logger.error(f"Erreur GET /api/daily-challenges: {e}", exc_info=True)
        return capture_internal_error_response(
            e,
            "Erreur lors de la recuperation des defis",
            tags={"handler": "daily_challenges.get_daily_challenges"},
        )
