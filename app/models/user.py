from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base import Base

class UserRole(str, enum.Enum):
    """Les rangs de l'Ordre Jedi des Mathématiques"""
    PADAWAN = "padawan"     # Apprenti, niveau standard
    MAITRE = "maitre"       # Enseignant, créateur d'exercices
    GARDIEN = "gardien"     # Modérateur, gestion des utilisateurs
    ARCHIVISTE = "archiviste"  # Administrateur, accès complet

class User(Base):
    """Modèle de données pour les utilisateurs de Mathakine"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.PADAWAN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Informations pédagogiques
    grade_level = Column(Integer, nullable=True)  # Niveau scolaire
    learning_style = Column(String, nullable=True)  # Style d'apprentissage préféré
    preferred_difficulty = Column(String, nullable=True)  # Difficulté préférée
    
    # Préférences d'interface
    preferred_theme = Column(String, default="light")  # "light" ou "dark" (Côté Lumineux ou Côté Obscur)
    accessibility_settings = Column(String, nullable=True)  # JSON des paramètres d'accessibilité
    
    # Relations
    created_exercises = relationship("Exercise", back_populates="creator")
    attempts = relationship("Attempt", back_populates="user")
    progress_records = relationship("Progress", back_populates="user")
    
    # Relations avec les défis logiques
    created_logic_challenges = relationship("LogicChallenge", back_populates="creator")
    logic_challenge_attempts = relationship("LogicChallengeAttempt", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}>" 