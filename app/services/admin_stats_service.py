"""
Facade admin stats (B3.4).

Délègue aux sous-services par responsabilité :
- admin_overview_service : KPIs globaux
- admin_audit_service : audit log
- admin_moderation_service : modération contenu IA
- admin_reporting_service : rapports périodiques
"""

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.core.types import AdminReportDict, AuditLogPageDict, ModerationDict
from app.services.admin_audit_service import get_audit_log_for_api as _get_audit
from app.services.admin_moderation_service import (
    get_moderation_for_api as _get_moderation,
)
from app.services.admin_overview_service import get_overview_for_api as _get_overview
from app.services.admin_reporting_service import get_reports_for_api as _get_reports


class AdminStatsService:
    """Facade : statistiques, rapports, audit log et modération admin."""

    @staticmethod
    def get_overview_for_api(db: Session) -> Dict[str, int]:
        """KPIs globaux : total_users, total_exercises, total_challenges, total_attempts."""
        return _get_overview(db)

    @staticmethod
    def get_audit_log_for_api(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        action_filter: Optional[str] = None,
        resource_filter: Optional[str] = None,
    ) -> AuditLogPageDict:
        """Journal des actions admin."""
        return _get_audit(
            db,
            skip=skip,
            limit=limit,
            action_filter=action_filter,
            resource_filter=resource_filter,
        )

    @staticmethod
    def get_moderation_for_api(
        db: Session,
        *,
        mod_type: str = "all",
        skip: int = 0,
        limit: int = 50,
    ) -> ModerationDict:
        """Contenu IA pour modération."""
        return _get_moderation(db, mod_type=mod_type, skip=skip, limit=limit)

    @staticmethod
    def get_reports_for_api(
        db: Session,
        *,
        period: str = "7d",
    ) -> AdminReportDict:
        """Rapports par période : inscriptions, activité, taux succès."""
        return _get_reports(db, period=period)
