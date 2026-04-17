"""
Service pour la gestion des retours utilisateur (signalements).
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.models.feedback_report import FeedbackReport

logger = get_logger(__name__)

VALID_TYPES = frozenset({"exercise", "challenge", "ui", "other"})

VALID_STATUSES = frozenset({"new", "read", "resolved"})


def delete_feedback_sync(*, feedback_id: int) -> Tuple[bool, Optional[str]]:
    """
    Use case sync: supprime un rapport de feedback (hard delete).
    Execute via run_db_bound() depuis les handlers async.

    Returns:
        (True, None) en cas de succes
        (False, "not_found") si le rapport n'existe pas
    """
    with sync_db_session() as db:
        return FeedbackService.delete_feedback(db, feedback_id=feedback_id)


def update_feedback_status_sync(
    *, feedback_id: int, status: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Use case sync: met a jour le statut d'un rapport de feedback.
    Execute via run_db_bound() depuis les handlers async.

    Returns:
        ({ "id", "status" }, None) en cas de succes
        (None, "not_found" | "invalid_status") sinon
    """
    with sync_db_session() as db:
        return FeedbackService.update_feedback_status(
            db, feedback_id=feedback_id, status=status
        )


def create_feedback_report_sync(
    *,
    feedback_type: str,
    description: Optional[str] = None,
    page_url: Optional[str] = None,
    exercise_id: Optional[int] = None,
    challenge_id: Optional[int] = None,
    user_id: Optional[int] = None,
    user_role: Optional[str] = None,
    active_theme: Optional[str] = None,
    ni_state: Optional[str] = None,
    component_id: Optional[str] = None,
) -> Tuple[Optional[FeedbackReport], Optional[str]]:
    """
    Use case sync: cree un rapport de feedback.
    Execute via run_db_bound() depuis les handlers async.
    """
    with sync_db_session() as db:
        return FeedbackService.create_feedback_report(
            db,
            feedback_type=feedback_type,
            description=description,
            page_url=page_url,
            exercise_id=exercise_id,
            challenge_id=challenge_id,
            user_id=user_id,
            user_role=user_role,
            active_theme=active_theme,
            ni_state=ni_state,
            component_id=component_id,
        )


class FeedbackService:
    """Service pour les retours et signalements."""

    @staticmethod
    def create_feedback_report(
        db: Session,
        *,
        feedback_type: str,
        description: Optional[str] = None,
        page_url: Optional[str] = None,
        exercise_id: Optional[int] = None,
        challenge_id: Optional[int] = None,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
        active_theme: Optional[str] = None,
        ni_state: Optional[str] = None,
        component_id: Optional[str] = None,
    ) -> Tuple[Optional[FeedbackReport], Optional[str]]:
        """
        Cree un rapport de feedback.

        Returns:
            (FeedbackReport, None) en cas de succes
            (None, "message_erreur") sinon (ex: feedback_type invalide)
        """
        feedback_type = (feedback_type or "").strip().lower()
        if feedback_type not in VALID_TYPES:
            return None, f"feedback_type invalide (attendus: {', '.join(VALID_TYPES)})"

        report = FeedbackReport(
            user_id=user_id,
            feedback_type=feedback_type,
            page_url=page_url or None,
            exercise_id=exercise_id,
            challenge_id=challenge_id,
            description=description or None,
            user_role=user_role or None,
            active_theme=active_theme or None,
            ni_state=ni_state or None,
            component_id=component_id or None,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report, None

    @staticmethod
    def list_feedback_for_admin(db: Session, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Liste les retours pour l'admin, tries par date decroissante.
        """
        reports = (
            db.query(FeedbackReport)
            .order_by(FeedbackReport.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.user.username if r.user else None,
                "feedback_type": r.feedback_type,
                "page_url": r.page_url,
                "exercise_id": r.exercise_id,
                "challenge_id": r.challenge_id,
                "description": r.description,
                "user_role": r.user_role,
                "active_theme": r.active_theme,
                "ni_state": r.ni_state,
                "component_id": r.component_id,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ]

    @staticmethod
    def delete_feedback(db: Session, *, feedback_id: int) -> Tuple[bool, Optional[str]]:
        """
        Supprime un rapport par identifiant.

        Returns:
            (True, None) en cas de succes
            (False, "not_found") sinon
        """
        report = (
            db.query(FeedbackReport).filter(FeedbackReport.id == feedback_id).first()
        )
        if report is None:
            return False, "not_found"

        db.delete(report)
        db.commit()
        return True, None

    @staticmethod
    def update_feedback_status(
        db: Session,
        *,
        feedback_id: int,
        status: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Met a jour le statut d'un rapport (new | read | resolved).

        Returns:
            ({"id", "status"}, None) en cas de succes
            (None, "not_found" | "invalid_status") sinon
        """
        normalized = (status or "").strip().lower()
        if normalized not in VALID_STATUSES:
            return None, "invalid_status"

        report = (
            db.query(FeedbackReport).filter(FeedbackReport.id == feedback_id).first()
        )
        if report is None:
            return None, "not_found"

        report.status = normalized
        db.commit()
        db.refresh(report)
        return {"id": report.id, "status": normalized}, None
