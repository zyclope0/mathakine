"""
Handlers pour les retours utilisateur (signalements).
"""

import traceback

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.models.feedback_report import FeedbackReport
from app.utils.db_utils import db_session
from app.utils.error_handler import get_safe_error_message
from server.auth import require_admin, require_auth

logger = get_logger(__name__)

VALID_TYPES = frozenset({"exercise", "challenge", "ui", "other"})


@require_auth
async def submit_feedback(request: Request):
    """
    Soumettre un retour (signalement).
    Route: POST /api/feedback
    Body: { "feedback_type": "exercise"|"challenge"|"ui"|"other", "description": "...", "page_url": "...", "exercise_id": int?, "challenge_id": int? }
    """
    try:
        body = await request.json()
        feedback_type = (body.get("feedback_type") or "").strip().lower()
        if feedback_type not in VALID_TYPES:
            return JSONResponse(
                {"error": "feedback_type invalide (exercise, challenge, ui, other)"},
                status_code=400,
            )

        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("id")

        page_url = body.get("page_url") or ""
        exercise_id = body.get("exercise_id")
        challenge_id = body.get("challenge_id")
        description = (body.get("description") or "").strip()

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

        async with db_session() as db:
            report = FeedbackReport(
                user_id=user_id,
                feedback_type=feedback_type,
                page_url=page_url or None,
                exercise_id=exercise_id,
                challenge_id=challenge_id,
                description=description or None,
            )
            db.add(report)
            db.commit()
            db.refresh(report)

        logger.info(
            f"Feedback enregistré: type={feedback_type}, user_id={user_id}, id={report.id}"
        )
        return JSONResponse(
            {"success": True, "id": report.id, "message": "Merci pour votre retour !"},
            status_code=201,
        )
    except Exception as e:
        logger.error(f"Erreur submit_feedback: {e}")
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(e)}, status_code=500
        )


@require_auth
@require_admin
async def admin_list_feedback(request: Request):
    """
    Liste des retours pour l'admin.
    Route: GET /api/admin/feedback
    """
    try:
        async with db_session() as db:
            reports = (
                db.query(FeedbackReport)
                .order_by(FeedbackReport.created_at.desc())
                .limit(500)
                .all()
            )
            items = []
            for r in reports:
                items.append(
                    {
                        "id": r.id,
                        "user_id": r.user_id,
                        "username": r.user.username if r.user else None,
                        "feedback_type": r.feedback_type,
                        "page_url": r.page_url,
                        "exercise_id": r.exercise_id,
                        "challenge_id": r.challenge_id,
                        "description": r.description,
                        "status": r.status,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                )
            return JSONResponse({"feedback": items})
    except Exception as e:
        logger.error(f"Erreur admin_list_feedback: {e}")
        traceback.print_exc()
        return JSONResponse(
            {"error": get_safe_error_message(e)}, status_code=500
        )
