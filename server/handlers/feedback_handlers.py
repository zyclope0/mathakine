"""
Handlers pour les retours utilisateur (signalements).
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.admin_read_service import list_feedback_for_admin
from app.services.feedback_service import create_feedback_report_sync
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.request_utils import parse_json_body_any
from server.auth import require_admin, require_auth

logger = get_logger(__name__)


@require_auth
async def submit_feedback(request: Request) -> JSONResponse:
    """
    Soumettre un retour (signalement).
    Route: POST /api/feedback
    Body: { "feedback_type": "exercise"|"challenge"|"ui"|"other", "description": "...", "page_url": "...", "exercise_id": int?, "challenge_id": int? }
    """
    body_or_err = await parse_json_body_any(request)
    if isinstance(body_or_err, JSONResponse):
        return body_or_err
    try:
        feedback_type = (body_or_err.get("feedback_type") or "").strip()

        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("id")

        page_url = body_or_err.get("page_url") or ""
        exercise_id = body_or_err.get("exercise_id")
        challenge_id = body_or_err.get("challenge_id")
        description = (body_or_err.get("description") or "").strip()

        if exercise_id is not None:
            try:
                exercise_id = int(exercise_id)
            except (TypeError, ValueError):
                exercise_id = None
        if challenge_id is not None:
            try:
                challenge_id = int(challenge_id)
            except (TypeError, ValueError):
                challenge_id = None

        report, err = await run_db_bound(
            create_feedback_report_sync,
            feedback_type=feedback_type,
            description=description or None,
            page_url=page_url or None,
            exercise_id=exercise_id,
            challenge_id=challenge_id,
            user_id=user_id,
        )
        if err:
            return api_error_response(
                400, "feedback_type invalide (exercise, challenge, ui, other)"
            )

        logger.info(
            f"Feedback enregistre: type={feedback_type}, user_id={user_id}, id={report.id}"
        )
        return JSONResponse(
            {"success": True, "id": report.id, "message": "Merci pour votre retour !"},
            status_code=201,
        )
    except Exception as e:
        logger.error(f"Erreur submit_feedback: {e}", exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_admin
async def admin_list_feedback(request: Request) -> JSONResponse:
    """
    Liste des retours pour l'admin.
    Route: GET /api/admin/feedback
    """
    try:
        items = await run_db_bound(list_feedback_for_admin, limit=500)
        return JSONResponse({"feedback": items})
    except Exception as e:
        logger.error(f"Erreur admin_list_feedback: {e}", exc_info=True)
        return api_error_response(500, get_safe_error_message(e))
