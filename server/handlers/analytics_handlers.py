"""
Handler pour les événements analytiques EdTech (CTR Quick Start, temps vers 1er attempt, conversion).
Persistance en BDD + log structuré. Consultation via admin /api/admin/analytics/edtech.
"""

import json

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.models.edtech_event import EdTechEvent
from app.utils.db_utils import db_session
from server.auth import require_auth

logger = get_logger(__name__)

VALID_EVENTS = frozenset({"quick_start_click", "first_attempt"})


@require_auth
async def analytics_event(request: Request):
    """
    Enregistrer un événement analytics EdTech.
    Route: POST /api/analytics/event
    Body: { "event": "quick_start_click"|"first_attempt", "payload": {...} }
    """
    try:
        body = await request.json()
        event = (body.get("event") or "").strip().lower()
        payload = body.get("payload") or {}

        if event not in VALID_EVENTS:
            return JSONResponse(
                {"error": f"event invalide (attendu: {sorted(VALID_EVENTS)})"},
                status_code=400,
            )

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
            record = EdTechEvent(
                user_id=user_id,
                event=event,
                payload=payload_dict,
            )
            db.add(record)
            db.commit()

        return JSONResponse({"ok": True}, status_code=200)
    except json.JSONDecodeError as e:
        logger.warning("analytics_event: body JSON invalide: %s", e)
        return JSONResponse({"error": "body JSON invalide"}, status_code=400)
    except Exception as e:
        logger.exception("analytics_event: %s", e)
        return JSONResponse({"error": "Erreur serveur"}, status_code=500)


# --- Admin : consultation des analytics EdTech ---

from collections import defaultdict
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
        event_filter = request.query_params.get("event", "").strip().lower()
        limit = min(int(request.query_params.get("limit", "200")), 500)

        since = datetime.now(timezone.utc)
        if period == "30d":
            since -= timedelta(days=30)
        else:
            since -= timedelta(days=7)

        async with db_session() as db:
            q = db.query(EdTechEvent).filter(EdTechEvent.created_at >= since)
            if event_filter and event_filter in VALID_EVENTS:
                q = q.filter(EdTechEvent.event == event_filter)
            events = q.order_by(EdTechEvent.created_at.desc()).limit(limit).all()

            # Agrégats sur TOUS les événements de la période (sans limit)
            q_all = db.query(EdTechEvent).filter(EdTechEvent.created_at >= since)
            if event_filter and event_filter in VALID_EVENTS:
                q_all = q_all.filter(EdTechEvent.event == event_filter)
            events_all = q_all.all()

        # Agrégats calculés en Python
        aggregates = defaultdict(lambda: {"count": 0, "time_to_first_attempt_ms": []})
        ctr_guided = 0
        ctr_total = 0

        for e in events_all:
            aggregates[e.event]["count"] += 1
            if e.event == "first_attempt" and e.payload:
                t = e.payload.get("timeToFirstAttemptMs")
                if t is not None:
                    try:
                        aggregates[e.event]["time_to_first_attempt_ms"].append(float(t))
                    except (TypeError, ValueError):
                        pass
            if e.event == "quick_start_click":
                ctr_total += 1
                if e.payload and e.payload.get("guided"):
                    ctr_guided += 1

        # Résumé agrégé
        agg_result = {}
        for evt, data in aggregates.items():
            times = data["time_to_first_attempt_ms"]
            avg_ms = round(sum(times) / len(times), 0) if times else None
            agg_result[evt] = {
                "count": data["count"],
                "avg_time_to_first_attempt_ms": avg_ms,
            }

        ctr_summary = {}
        if ctr_total > 0:
            ctr_summary = {
                "total_clicks": ctr_total,
                "guided_clicks": ctr_guided,
                "guided_rate_pct": round(100 * ctr_guided / ctr_total, 1),
            }

        events_data = [
            {
                "id": e.id,
                "user_id": e.user_id,
                "event": e.event,
                "payload": e.payload,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]

        return JSONResponse(
            {
                "period": period,
                "since": since.isoformat(),
                "aggregates": dict(agg_result),
                "ctr_summary": ctr_summary,
                "events": events_data,
            }
        )
    except Exception as e:
        logger.exception("admin_analytics_edtech: %s", e)
        return JSONResponse({"error": "Erreur serveur"}, status_code=500)
