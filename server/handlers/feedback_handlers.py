"""
Handlers pour les retours utilisateur (signalements).
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.core.user_roles import serialize_user_role
from app.services.admin.admin_read_service import list_feedback_for_admin
from app.services.feedback.feedback_service import (
    create_feedback_report_sync,
    delete_feedback_sync,
    update_feedback_status_sync,
)
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.rate_limit import rate_limit_feedback
from app.utils.request_utils import parse_json_body_any
from server.auth import require_admin, require_auth

logger = get_logger(__name__)


@require_auth
@rate_limit_feedback
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

        active_theme = (body_or_err.get("active_theme") or "").strip() or None
        ni_raw = (body_or_err.get("ni_state") or "").strip().lower() or None
        ni_state = ni_raw if ni_raw in ("on", "off") else None
        component_id = (body_or_err.get("component_id") or "").strip() or None

        user_role = None
        if hasattr(request.state, "user") and request.state.user:
            user_role = serialize_user_role(request.state.user.get("role"))

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
            user_role=user_role,
            active_theme=active_theme,
            ni_state=ni_state,
            component_id=component_id,
        )
        if err:
            return api_error_response(
                400, "feedback_type invalide (exercise, challenge, ui, other)"
            )

        logger.info(
            "Feedback enregistre: type=%s, user_id=%s, id=%s",
            feedback_type,
            user_id,
            report.id,
        )
        return JSONResponse(
            {"success": True, "id": report.id, "message": "Merci pour votre retour !"},
            status_code=201,
        )
    except Exception as e:
        logger.error("Erreur submit_feedback: %s", e, exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_admin
async def admin_patch_feedback_status(request: Request) -> JSONResponse:
    """
    Met a jour le statut d'un retour (admin).
    Route: PATCH /api/admin/feedback/{feedback_id}
    Body: { "status": "new" | "read" | "resolved" }
    """
    try:
        feedback_id_raw = request.path_params.get("feedback_id")
        if feedback_id_raw is None:
            return api_error_response(400, "Identifiant feedback manquant")
        try:
            feedback_id = int(feedback_id_raw)
        except (TypeError, ValueError):
            return api_error_response(400, "Identifiant feedback invalide")

        body_or_err = await parse_json_body_any(request)
        if isinstance(body_or_err, JSONResponse):
            return body_or_err

        status_raw = body_or_err.get("status")
        if not isinstance(status_raw, str) or not status_raw.strip():
            return api_error_response(400, "Champ status requis (new, read, resolved)")

        payload, err = await run_db_bound(
            update_feedback_status_sync,
            feedback_id=feedback_id,
            status=status_raw,
        )
        if err == "not_found":
            return api_error_response(404, "Retour introuvable")
        if err == "invalid_status":
            return api_error_response(400, "Statut invalide (new, read, resolved)")
        if err or payload is None:
            logger.error(
                "admin_patch_feedback_status: unexpected err=%s payload=%s", err, payload
            )
            return api_error_response(500, "Erreur lors de la mise à jour du statut")

        return JSONResponse(payload)
    except Exception as e:
        logger.error("Erreur admin_patch_feedback_status: %s", e, exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_admin
async def admin_delete_feedback(request: Request) -> JSONResponse:
    """
    Supprime un retour (admin, hard delete).
    Route: DELETE /api/admin/feedback/{feedback_id}
    """
    try:
        feedback_id_raw = request.path_params.get("feedback_id")
        if feedback_id_raw is None:
            return api_error_response(400, "Identifiant feedback manquant")
        try:
            feedback_id = int(feedback_id_raw)
        except (TypeError, ValueError):
            return api_error_response(400, "Identifiant feedback invalide")

        ok, err = await run_db_bound(delete_feedback_sync, feedback_id=feedback_id)
        if err == "not_found":
            return api_error_response(404, "Retour introuvable")
        if not ok:
            logger.error("admin_delete_feedback: unexpected err=%s ok=%s", err, ok)
            return api_error_response(500, "Erreur lors de la suppression")

        return JSONResponse({"success": True, "id": feedback_id})
    except Exception as e:
        logger.error("Erreur admin_delete_feedback: %s", e, exc_info=True)
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
        logger.error("Erreur admin_list_feedback: %s", e, exc_info=True)
        return api_error_response(500, get_safe_error_message(e))
