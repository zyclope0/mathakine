"""
Modèles SQLAlchemy pour le système de badges
"""
from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Achievement(Base):
    """Modèle pour les badges/achievements"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    difficulty = Column(String(50), nullable=True)  # bronze, silver, gold, legendary
    points_reward = Column(Integer, default=0)
    is_secret = Column(Boolean, default=False)
    requirements = Column(JSON, nullable=True)
    star_wars_title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relations
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement {self.code}: {self.name} ({self.difficulty})>"


class UserAchievement(Base):
    """Modèle pour les badges obtenus par les utilisateurs"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    progress_data = Column(JSON, nullable=True)
    is_displayed = Column(Boolean, default=True)

    # Relations
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self):
        return f"<UserAchievement: User {self.user_id}, Achievement {self.achievement_id}>"
