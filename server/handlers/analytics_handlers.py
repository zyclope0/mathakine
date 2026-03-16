"""
Handler pour les evenements analytiques EdTech (CTR Quick Start, temps vers 1er attempt, conversion).
Persistance en BDD + log structure. Consultation via admin /api/admin/analytics/edtech.
"""

import json

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.analytics_service import record_edtech_event_sync
from app.utils.error_handler import api_error_response, capture_internal_error_response
from app.utils.pagination import parse_pagination_params
from app.utils.request_utils import parse_json_body_any
from server.auth import require_auth

logger = get_logger(__name__)


@require_auth
async def analytics_event(request: Request) -> JSONResponse:
    """
    Enregistrer un evenement analytics EdTech.
    Route: POST /api/analytics/event
    Body: { "event": "quick_start_click"|"first_attempt", "payload": {...} }
    """
    body_or_err = await parse_json_body_any(request)
    if isinstance(body_or_err, JSONResponse):
        return body_or_err
    try:
        event = (body_or_err.get("event") or "").strip()
        payload = body_or_err.get("payload") or {}

        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("id")

        payload_dict = payload if isinstance(payload, dict) else {}
        log_payload = {
            "event": event,
            "user_id": user_id,
            **payload_dict,
        }
        logger.info("[EDTECH] %s", json.dumps(log_payload, default=str))

        ok = await run_db_bound(
            record_edtech_event_sync,
            event=event,
            payload=payload_dict,
            user_id=user_id,
        )
        if not ok:
            return api_error_response(
                400, "event invalide (attendu: first_attempt, quick_start_click)"
            )

        return JSONResponse({"ok": True}, status_code=200)
    except Exception as e:
        logger.exception("analytics_event: %s", e)
        return capture_internal_error_response(
            e,
            "Erreur serveur",
            tags={"handler": "analytics.analytics_event"},
        )


# --- Admin : consultation des analytics EdTech ---

from app.services.admin_read_service import get_edtech_analytics_for_admin
from server.auth import require_admin


@require_auth
@require_admin
async def admin_analytics_edtech(request: Request) -> JSONResponse:
    """
    GET /api/admin/analytics/edtech
    Agregats et liste des evenements EdTech (period=7d|30d, event=optional).
    """
    try:
        period = request.query_params.get("period", "7d")
        event_filter = request.query_params.get("event", "").strip()
        _, limit = parse_pagination_params(
            request.query_params, default_limit=200, max_limit=500
        )

        result = await run_db_bound(
            get_edtech_analytics_for_admin,
            period=period,
            event_filter=event_filter,
            limit=limit,
        )

        return JSONResponse(
            {
                "period": period,
                "since": result["since"],
                "aggregates": result["aggregates"],
                "ctr_summary": result["ctr_summary"],
                "unique_users": result["unique_users"],
                "events": result["events"],
            }
        )
    except Exception as e:
        logger.exception("admin_analytics_edtech: %s", e)
        return capture_internal_error_response(
            e,
            "Erreur serveur",
            tags={"handler": "analytics.admin_analytics_edtech"},
        )
