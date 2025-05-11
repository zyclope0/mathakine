from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base



class DifficultyLevel(str, enum.Enum):
    """Niveaux de difficulté des épreuves mathématiques"""
    INITIE = "initie"       # Facile
    PADAWAN = "padawan"     # Moyen
    CHEVALIER = "chevalier" # Difficile
    MAITRE = "maitre"       # Très difficile



class ExerciseType(str, enum.Enum):
    """Types d'épreuves mathématiques"""
    ADDITION = "addition"           # Additions
    SOUSTRACTION = "soustraction"   # Soustractions
    MULTIPLICATION = "multiplication" # Multiplications
    DIVISION = "division"           # Divisions
    FRACTIONS = "fractions"         # Fractions
    GEOMETRIE = "geometrie"         # Géométrie
    DIVERS = "divers"               # Exercices variés



class Exercise(Base):
    """Modèle de données pour les exercices mathématiques (Épreuves Jedi)"""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)

    # Métadonnées
    title = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="created_exercises")
    exercise_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    tags = Column(String, nullable=True)  # Tags séparés par des virgules

    # Contenu de l'exercice
    question = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)
    choices = Column(JSON, nullable=True)  # Options pour les questions à choix multiples
    explanation = Column(Text, nullable=True)  # Explication de la solution
    hint = Column(Text, nullable=True)  # Indice pour aider l'élève

    # Métadonnées du contenu
    image_url = Column(String, nullable=True)  # URL de l'image associée
    audio_url = Column(String, nullable=True)  # URL audio pour accessibilité

    # États
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relations
    attempts = relationship("Attempt", back_populates="exercise", cascade="all, delete-orphan")



    def __repr__(self):
        return f"<Exercise {self.id}: {self.title} ({self.difficulty})>"
