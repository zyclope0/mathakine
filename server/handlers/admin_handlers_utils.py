"""
Utilitaires partagés pour les handlers admin (audit, config, sérialisation).

Extrait de admin_handlers.py (PR découpage admin) — fonctions pures sans dépendance Request.
"""
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.admin_audit_log import AdminAuditLog


# Schéma des paramètres globaux (connus et modifiables par l'admin)
CONFIG_SCHEMA = {
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


def _log_admin_action(
    db: Session,
    admin_user_id: int | None,
    action: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    details: dict | None = None,
) -> None:
    """Enregistre une action admin dans le journal d'audit."""
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
        pass  # Ne pas faire échouer l'action principale


def _parse_setting_value(
    value: str | None, schema: dict
) -> bool | int | str:
    """Parse une valeur de paramètre selon le schéma."""
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


def _serialize_value(v: Any) -> str:
    """Sérialise une valeur pour stockage en DB."""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)
