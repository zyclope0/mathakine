from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SpacedRepetitionItem(Base):
    """
    One SM-2 scheduling row per (user, exercise) — F04 backend foundation.

    Deleting the exercise removes its SR rows (ON DELETE CASCADE).
    """

    __tablename__ = "spaced_repetition_items"

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", name="uq_sri_user_exercise"),
        Index("ix_sri_user_next_review", "user_id", "next_review_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id = Column(
        Integer,
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ease_factor = Column(Float, nullable=False)
    interval_days = Column(Integer, nullable=False)
    next_review_date = Column(Date, nullable=False, index=True)
    repetition_count = Column(Integer, nullable=False)
    last_quality = Column(Integer, nullable=True)
    # Correlation idempotence (pas de FK : évite contrainte flush vs ordre transaction / tests unitaires)
    last_attempt_id = Column(Integer, nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="spaced_repetition_items")
    exercise = relationship("Exercise", back_populates="spaced_repetition_items")
