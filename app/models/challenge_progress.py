"""Progression agrégée par type de défi logique (distincte de progress exercices)."""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChallengeProgress(Base):
    """Une ligne par (utilisateur, type de défi) — stats cumulées."""

    __tablename__ = "challenge_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "challenge_type", name="uq_challenge_progress_user_type"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user = relationship("User", back_populates="challenge_progress_rows")

    challenge_type = Column(String(50), nullable=False)
    total_attempts = Column(Integer, nullable=False, default=0)
    correct_attempts = Column(Integer, nullable=False, default=0)
    completion_rate = Column(Float, nullable=False, default=0.0)
    mastery_level = Column(String(20), nullable=False, default="novice")
    last_attempted_at = Column(DateTime(timezone=True), nullable=True)
