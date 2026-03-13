"""
Service audit log admin (B3.4).

Journal des actions admin : qui a fait quoi, quand.
"""

from typing import List, Optional, cast

from sqlalchemy.orm import Session, joinedload

from app.core.types import AuditLogItemDict, AuditLogPageDict
from app.models.admin_audit_log import AdminAuditLog
from app.services.admin_helpers import parse_json_safe


def get_audit_log_for_api(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    action_filter: Optional[str] = None,
    resource_filter: Optional[str] = None,
) -> AuditLogPageDict:
    """Journal des actions admin : pagination, filtres action/resource_type."""
    q = (
        db.query(AdminAuditLog)
        .options(joinedload(AdminAuditLog.admin_user))
        .order_by(AdminAuditLog.created_at.desc())
    )
    if action_filter:
        q = q.filter(AdminAuditLog.action == action_filter)
    if resource_filter:
        q = q.filter(AdminAuditLog.resource_type == resource_filter)
    total = q.count()
    logs = q.offset(skip).limit(limit).all()
    items: List[AuditLogItemDict] = []
    for log in logs:
        admin_username = log.admin_user.username if log.admin_user else None
        items.append(
            {
                "id": cast(int, log.id),
                "admin_user_id": cast(Optional[int], log.admin_user_id),
                "admin_username": admin_username,
                "action": cast(str, log.action),
                "resource_type": cast(str, log.resource_type),
                "resource_id": cast(Optional[int], log.resource_id),
                "details": parse_json_safe(log.details),
                "created_at": (log.created_at.isoformat() if log.created_at else None),
            }
        )
    return cast(AuditLogPageDict, {"items": items, "total": total})
