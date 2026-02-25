"""
Modèle pour les événements analytiques EdTech (CTR Quick Start, temps vers 1er attempt, conversion).
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class EdTechEvent(Base):
    """Événements analytiques EdTech — quick_start_click, first_attempt."""

    __tablename__ = "edtech_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event = Column(
        String(50), nullable=False, index=True
    )  # quick_start_click, first_attempt
    payload = Column(
        JSONB, nullable=True
    )  # type, guided, targetId, timeToFirstAttemptMs
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
