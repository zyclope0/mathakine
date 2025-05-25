"""
Modèle SQLAlchemy pour les utilisateurs
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
import json
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.db.base import Base



class UserRole(PyEnum):
    """Énumération des rôles d'utilisateur"""
    PADAWAN = "padawan"     # Apprenti, niveau standard
    MAITRE = "maitre"       # Enseignant, créateur d'exercices
    GARDIEN = "gardien"     # Modérateur, gestion des utilisateurs
    ARCHIVISTE = "archiviste"  # Administrateur, accès complet
    ADMIN = "admin"



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

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole, name="userrole", create_type=False), default=UserRole.PADAWAN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Informations pédagogiques
    grade_level = Column(Integer)
    learning_style = Column(String(50))
    preferred_difficulty = Column(String(50))

    # Préférences d'interface
    preferred_theme = Column(String(50))
    accessibility_settings = Column(JSONEncodedDict)

    # Relations
    created_exercises = relationship("Exercise", back_populates="creator", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

    # Relations avec les défis logiques
    created_logic_challenges = relationship("LogicChallenge", back_populates="creator", cascade="all, delete-orphan")
    logic_challenge_attempts = relationship("LogicChallengeAttempt", back_populates="user", cascade="all, delete-orphan")



    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}>"
