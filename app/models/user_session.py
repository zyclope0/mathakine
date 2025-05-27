"""
Modèle SQLAlchemy pour les sessions utilisateur
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET
from app.db.base import Base


class UserSession(Base):
    """Modèle pour les sessions utilisateur"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(JSON, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    location_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    last_activity = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relations
    user = relationship("User", back_populates="user_sessions")

    def __repr__(self):
        return f"<UserSession {self.id}: User {self.user_id}, Active: {self.is_active}>"

    def is_expired(self) -> bool:
        """Vérifier si la session a expiré"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at

    def extend_session(self, hours: int = 24):
        """Prolonger la session"""
        from datetime import datetime, timezone, timedelta
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        self.last_activity = datetime.now(timezone.utc)
