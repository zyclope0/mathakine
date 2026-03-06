"""
Modèle SQLAlchemy pour les défis quotidiens (F02).

Un DailyChallenge représente un objectif quotidien pour un utilisateur.
Types : volume_exercises (N exercices quelconques), specific_type (N exercices
d'un type donné), logic_challenge (N défis logiques).
"""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class DailyChallenge(Base):
    """Défi quotidien pour un utilisateur."""

    __tablename__ = "daily_challenges"

    __table_args__ = (Index("ix_daily_challenges_user_date", "user_id", "date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user = relationship("User", back_populates="daily_challenges")

    date = Column(Date, nullable=False, index=True)

    # volume_exercises | specific_type | logic_challenge
    challenge_type = Column(String(50), nullable=False)

    # Pour specific_type : {"exercise_type": "addition"}
    metadata_ = Column("metadata", JSONB, nullable=True)

    target_count = Column(Integer, nullable=False, default=1)
    completed_count = Column(Integer, nullable=False, default=0)

    # pending | completed | expired
    status = Column(String(20), nullable=False, default="pending")

    bonus_points = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<DailyChallenge id={self.id} user={self.user_id} "
            f"date={self.date} type={self.challenge_type} "
            f"{self.completed_count}/{self.target_count} status={self.status}>"
        )
