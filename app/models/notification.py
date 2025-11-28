"""
Modèle SQLAlchemy pour les notifications
"""
from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Notification(Base):
    """Modèle pour les notifications utilisateur"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)
    action_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    is_email_sent = Column(Boolean, default=False)
    priority = Column(Integer, default=5)  # 1-10
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)

    # Relations
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id}: {self.type} for User {self.user_id}>"

    def mark_as_read(self):
        """Marquer la notification comme lue"""
        self.is_read = True

    def is_expired(self) -> bool:
        """Vérifier si la notification a expiré"""
        if self.expires_at is None:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
