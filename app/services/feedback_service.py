"""
Service pour la gestion des retours utilisateur (signalements).
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.feedback_report import FeedbackReport

logger = get_logger(__name__)

VALID_TYPES = frozenset({"exercise", "challenge", "ui", "other"})


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
    ) -> Tuple[Optional[FeedbackReport], Optional[str]]:
        """
        Crée un rapport de feedback.

        Returns:
            (FeedbackReport, None) en cas de succès
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
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report, None

    @staticmethod
    def list_feedback_for_admin(db: Session, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Liste les retours pour l'admin, triés par date décroissante.
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
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ]
