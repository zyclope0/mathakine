"""
Modèle SQLAlchemy pour les utilisateurs
"""
import json
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from sqlalchemy.types import TypeDecorator

from app.db.base import Base


class UserRole(PyEnum):
    """Énumération des rôles d'utilisateur"""
    PADAWAN = "padawan"     # Apprenti, niveau standard
    MAITRE = "maitre"       # Enseignant, créateur d'exercices
    GARDIEN = "gardien"     # Modérateur, gestion des utilisateurs
    ARCHIVISTE = "archiviste"  # Administrateur, accès complet



class JSONEncodedDict(TypeDecorator):
    """Représente un dictionnaire mappé vers une colonne TEXT"""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value



class User(Base):
    """Modèle de données pour les utilisateurs de Mathakine"""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_users_avatar_url', 'avatar_url'),
        Index('idx_users_jedi_rank', 'jedi_rank'),
        Index('idx_users_total_points', 'total_points'),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole, name="userrole", create_type=False), default=UserRole.PADAWAN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Vérification email
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True, index=True)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Réinitialisation mot de passe
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Informations pédagogiques
    grade_level = Column(Integer)
    learning_style = Column(String(50))
    preferred_difficulty = Column(String(50))

    # Préférences d'interface
    preferred_theme = Column(String(50))
    accessibility_settings = Column(JSONEncodedDict)

    # Colonnes de gamification (système de badges)
    pinned_badge_ids = Column(JSONB, nullable=True)  # A-4: max 3 badge IDs épinglés
    total_points = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    jedi_rank = Column(String(50), default='youngling')
    avatar_url = Column(String(255), nullable=True)

    # Relations
    created_exercises = relationship("Exercise", back_populates="creator", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

    # Relations avec les défis logiques
    created_logic_challenges = relationship("LogicChallenge", back_populates="creator", cascade="all, delete-orphan")
    logic_challenge_attempts = relationship("LogicChallengeAttempt", back_populates="user", cascade="all, delete-orphan")

    # Relations avec le système de badges
    user_achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

    # Relations avec les sessions et notifications
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")



    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}>"
