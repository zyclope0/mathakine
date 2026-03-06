"""
Handlers pour les défis quotidiens (F02).

Route: GET /api/daily-challenges — récupère les défis du jour (crée si absent).
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.services.daily_challenge_service import get_or_create_today
from app.utils.db_utils import db_session
from app.utils.error_handler import api_error_response
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)


def _daily_challenge_to_dict(dc) -> dict:
    """Sérialise un DailyChallenge pour l'API."""
    return {
        "id": dc.id,
        "date": dc.date.isoformat() if dc.date else None,
        "challenge_type": dc.challenge_type,
        "metadata": dc.metadata_ or {},
        "target_count": dc.target_count,
        "completed_count": dc.completed_count,
        "status": dc.status,
        "bonus_points": dc.bonus_points,
    }


@require_auth
@require_full_access
async def get_daily_challenges(request: Request) -> JSONResponse:
    """
    Récupère les défis quotidiens du jour pour l'utilisateur connecté.
    Les crée automatiquement s'ils n'existent pas.
    Route: GET /api/daily-challenges
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        if not user_id:
            return api_error_response(400, "ID utilisateur manquant")

        async with db_session() as db:
            challenges = get_or_create_today(db, user_id)
            db.commit()
            data = [_daily_challenge_to_dict(c) for c in challenges]
            return JSONResponse({"challenges": data})

    except Exception as e:
        logger.error(f"Erreur GET /api/daily-challenges: {e}", exc_info=True)
        return api_error_response(500, "Erreur lors de la récupération des défis")
