"""
Service pour les événements analytiques EdTech.
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.edtech_event import EdTechEvent

logger = get_logger(__name__)

VALID_EVENTS = frozenset({"quick_start_click", "first_attempt"})


class AnalyticsService:
    """Service pour les analytics EdTech."""

    @staticmethod
    def record_edtech_event(
        db: Session,
        *,
        event: str,
        payload: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Enregistre un événement EdTech.

        Returns:
            True si enregistré, False si event invalide (non persisted)
        """
        event = (event or "").strip().lower()
        if event not in VALID_EVENTS:
            return False

        record = EdTechEvent(
            user_id=user_id,
            event=event,
            payload=payload if isinstance(payload, dict) else {},
        )
        db.add(record)
        db.commit()
        return True

    @staticmethod
    def get_edtech_analytics_for_admin(
        db: Session,
        *,
        since: datetime,
        event_filter: str = "",
        limit: int = 200,
    ) -> Dict[str, Any]:
        """
        Récupère les agrégats et la liste des événements EdTech pour l'admin.
        """
        limit = min(limit, 500)
        event_filter = (event_filter or "").strip().lower()

        q = db.query(EdTechEvent).filter(EdTechEvent.created_at >= since)
        if event_filter and event_filter in VALID_EVENTS:
            q = q.filter(EdTechEvent.event == event_filter)
        events = q.order_by(EdTechEvent.created_at.desc()).limit(limit).all()

        q_all = db.query(EdTechEvent).filter(EdTechEvent.created_at >= since)
        if event_filter and event_filter in VALID_EVENTS:
            q_all = q_all.filter(EdTechEvent.event == event_filter)
        events_all = q_all.all()

        aggregates = defaultdict(lambda: {"count": 0, "time_to_first_attempt_ms": []})
        ctr_guided = 0
        ctr_total = 0
        unique_user_ids = set()
        clicks_by_type = {"exercise": 0, "challenge": 0}
        attempts_by_type = {"exercise": 0, "challenge": 0}

        for e in events_all:
            if e.user_id:
                unique_user_ids.add(e.user_id)
            aggregates[e.event]["count"] += 1
            if e.event == "first_attempt" and e.payload:
                t = e.payload.get("timeToFirstAttemptMs")
                if t is not None:
                    try:
                        aggregates[e.event]["time_to_first_attempt_ms"].append(float(t))
                    except (TypeError, ValueError):
                        pass
                typ = (e.payload.get("type") or "").lower()
                if typ in attempts_by_type:
                    attempts_by_type[typ] += 1
            if e.event == "quick_start_click":
                ctr_total += 1
                if e.payload and e.payload.get("guided"):
                    ctr_guided += 1
                typ = (e.payload.get("type") or "").lower()
                if typ in clicks_by_type:
                    clicks_by_type[typ] += 1

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
                "by_type": dict(clicks_by_type),
            }

        if aggregates.get("first_attempt"):
            agg_result["first_attempt"]["by_type"] = dict(attempts_by_type)

        events_data: List[Dict[str, Any]] = [
            {
                "id": e.id,
                "user_id": e.user_id,
                "event": e.event,
                "payload": e.payload,
                "created_at": (e.created_at.isoformat() if e.created_at else None),
            }
            for e in events
        ]

        return {
            "since": since.isoformat(),
            "aggregates": dict(agg_result),
            "ctr_summary": ctr_summary,
            "unique_users": len(unique_user_ids),
            "events": events_data,
        }
