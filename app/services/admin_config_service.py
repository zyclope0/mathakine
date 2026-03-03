"""
Service admin pour la gestion de la configuration.

Extrait de AdminService.
Phase 3, item 3.3d — audit architecture 03/2026.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.setting import Setting
from app.services.admin_helpers import (
    CONFIG_SCHEMA,
    log_admin_action,
    parse_setting_value,
    serialize_value,
)


class AdminConfigService:
    """Gestion des paramètres globaux de la plateforme."""

    @staticmethod
    def get_config_for_api(db: Session) -> List[Dict[str, Any]]:
        rows = db.query(Setting).filter(Setting.key.in_(CONFIG_SCHEMA)).all()
        by_key = {r.key: r for r in rows}
        result = []
        for key, schema in CONFIG_SCHEMA.items():
            row = by_key.get(key)
            raw = row.value if row else None
            value = parse_setting_value(raw, schema)
            result.append(
                {
                    "key": key,
                    "value": value,
                    "type": schema["type"],
                    "category": schema.get("category", ""),
                    "label": schema.get("label", key),
                    "min": schema.get("min"),
                    "max": schema.get("max"),
                }
            )
        return result

    @staticmethod
    def update_config(
        db: Session,
        settings_in: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> None:
        for key, value in settings_in.items():
            if key not in CONFIG_SCHEMA:
                continue
            schema = CONFIG_SCHEMA[key]
            str_val = serialize_value(value)
            if schema["type"] == "int":
                try:
                    v = (
                        int(value)
                        if not isinstance(value, (bool, type(None)))
                        else schema["default"]
                    )
                    if "min" in schema and v < schema["min"]:
                        v = schema["min"]
                    if "max" in schema and v > schema["max"]:
                        v = schema["max"]
                    str_val = str(v)
                except (ValueError, TypeError):
                    str_val = str(schema.get("default", 0))
            elif schema["type"] == "bool":
                str_val = "true" if value in (True, "true", "1", 1) else "false"

            row = db.query(Setting).filter(Setting.key == key).first()
            if row:
                row.value = str_val
                row.updated_at = datetime.now(timezone.utc)
            else:
                db.add(
                    Setting(
                        key=key,
                        value=str_val,
                        category=schema.get("category"),
                        description=schema.get("label"),
                        is_system=True,
                        is_public=False,
                    )
                )
        log_admin_action(
            db,
            admin_user_id,
            "config_update",
            "settings",
            None,
            {"updated_keys": list(settings_in.keys())},
        )
        db.commit()
