"""
Handler pour les événements analytiques EdTech (CTR Quick Start, temps vers 1er attempt, conversion).
Persistance en BDD + log structuré. Consultation via admin /api/admin/analytics/edtech.
"""

import json

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.services.analytics_service import AnalyticsService
from app.utils.db_utils import db_session
from app.utils.error_handler import api_error_response
from app.utils.pagination import parse_pagination_params
from server.auth import require_auth

logger = get_logger(__name__)


@require_auth
async def analytics_event(request: Request):
    """
    Enregistrer un événement analytics EdTech.
    Route: POST /api/analytics/event
    Body: { "event": "quick_start_click"|"first_attempt", "payload": {...} }
    """
    try:
        body = await request.json()
        event = (body.get("event") or "").strip()
        payload = body.get("payload") or {}

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

        async with db_session() as db:
            ok = AnalyticsService.record_edtech_event(
                db,
                event=event,
                payload=payload_dict,
                user_id=user_id,
            )
            if not ok:
                return api_error_response(
                    400, "event invalide (attendu: first_attempt, quick_start_click)"
                )

        return JSONResponse({"ok": True}, status_code=200)
    except json.JSONDecodeError as e:
        logger.warning("analytics_event: body JSON invalide: %s", e)
        return api_error_response(400, "body JSON invalide")
    except Exception as e:
        logger.exception("analytics_event: %s", e)
        return api_error_response(500, "Erreur serveur")


# --- Admin : consultation des analytics EdTech ---

from datetime import datetime, timedelta, timezone

from server.auth import require_admin


@require_auth
@require_admin
async def admin_analytics_edtech(request: Request):
    """
    GET /api/admin/analytics/edtech
    Agrégats et liste des événements EdTech (period=7d|30d, event=optional).
    """
    try:
        period = request.query_params.get("period", "7d")
        event_filter = request.query_params.get("event", "").strip()
        _, limit = parse_pagination_params(
            request.query_params, default_limit=200, max_limit=500
        )

        since = datetime.now(timezone.utc)
        if period == "30d":
            since -= timedelta(days=30)
        else:
            since -= timedelta(days=7)

        async with db_session() as db:
            result = AnalyticsService.get_edtech_analytics_for_admin(
                db,
                since=since,
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
        return api_error_response(500, "Erreur serveur")
