"""
Helpers partagés entre les sous-services admin.

Phase 3, item 3.3 — audit architecture 03/2026.
"""

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.admin_audit_log import AdminAuditLog

CONFIG_SCHEMA: Dict[str, Dict[str, Any]] = {
    "maintenance_mode": {
        "type": "bool",
        "default": False,
        "category": "système",
        "label": "Mode maintenance",
    },
    "registration_enabled": {
        "type": "bool",
        "default": True,
        "category": "système",
        "label": "Inscriptions ouvertes",
    },
    "feature_ai_challenges_enabled": {
        "type": "bool",
        "default": True,
        "category": "features",
        "label": "Défis IA activés",
    },
    "feature_chat_enabled": {
        "type": "bool",
        "default": True,
        "category": "features",
        "label": "Chat IA activé",
    },
    "max_generations_per_user_per_hour": {
        "type": "int",
        "default": 20,
        "min": 1,
        "max": 100,
        "category": "limites",
        "label": "Générations max/user/heure",
    },
    "max_export_rows": {
        "type": "int",
        "default": 10000,
        "min": 100,
        "max": 100000,
        "category": "limites",
        "label": "Lignes max export CSV",
    },
}


def parse_setting_value(value: Optional[str], schema: dict) -> Any:
    if value is None:
        return schema.get("default", "")
    stype = schema.get("type", "str")
    if stype == "bool":
        return value.lower() in ("true", "1", "yes", "on")
    if stype == "int":
        try:
            v = int(value)
            if "min" in schema and v < schema["min"]:
                return schema.get("default", 0)
            if "max" in schema and v > schema["max"]:
                return schema["max"]
            return v
        except ValueError:
            return schema.get("default", 0)
    return value


def serialize_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def log_admin_action(
    db: Session,
    admin_user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
) -> None:
    try:
        log = AdminAuditLog(
            admin_user_id=admin_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
        )
        db.add(log)
    except Exception:
        pass


def parse_json_safe(s: Optional[str]) -> Optional[Any]:
    if not s:
        return None
    try:
        return json.loads(s)
    except (TypeError, ValueError):
        return None
