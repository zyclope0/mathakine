"""
Ledger des attributions de points (gamification compte).

Écrit uniquement via GamificationService.apply_points.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PointEvent(Base):
    """Événement d'attribution de points sur le compte utilisateur."""

    __tablename__ = "point_events"

    __table_args__ = (Index("ix_point_events_user_created", "user_id", "created_at"),)

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user = relationship("User", back_populates="point_events")

    # Valeurs PointEventSourceType (StrEnum) sérialisées en string stable
    source_type = Column(String(50), nullable=False, index=True)
    source_id = Column(Integer, nullable=True, index=True)

    points_delta = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)

    details = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
