from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Index, Integer,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Attempt(Base):
    """Modèle pour les tentatives de résolution d'exercices (Tentatives d'Accomplissement)"""
    __tablename__ = "attempts"
    
    # Index composites pour les requêtes fréquentes
    __table_args__ = (
        Index('ix_attempts_user_exercise', 'user_id', 'exercise_id'),
        Index('ix_attempts_user_correct', 'user_id', 'is_correct'),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Relations (avec index sur les FK pour les JOINs)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="attempts")
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    exercise = relationship("Exercise", back_populates="attempts")

    # Données de tentative
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, index=True)  # Filtrage fréquent
    time_spent = Column(Float, nullable=True)  # Temps passé en secondes

    # Métadonnées
    attempt_number = Column(Integer, default=1)  # Numéro de tentative pour cet exercice et cet utilisateur
    hints_used = Column(Integer, default=0)  # Nombre d'indices utilisés
    device_info = Column(String, nullable=True)  # Information sur l'appareil utilisé

    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)  # Tri chronologique



    def __repr__(self):
        status = "réussie" if self.is_correct else "échouée"
        return f"<Tentative {self.id}: Utilisateur {self.user_id}, Exercice {self.exercise_id}\
            , {status}>"
