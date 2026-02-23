"""
Modèle pour les retours utilisateur (signalements exercices, défis, bugs).
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class FeedbackReport(Base):
    """Retours et signalements des utilisateurs (MVP alpha)."""

    __tablename__ = "feedback_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # exercise | challenge | ui | other
    feedback_type = Column(String(20), nullable=False, index=True)
    page_url = Column(Text, nullable=True)
    exercise_id = Column(Integer, nullable=True, index=True)
    challenge_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="new", nullable=False)  # new | read | resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
