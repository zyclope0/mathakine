from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base



class Attempt(Base):
    """Modèle pour les tentatives de résolution d'exercices (Tentatives d'Accomplissement)"""
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)

    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="attempts")
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    exercise = relationship("Exercise", back_populates="attempts")

    # Données de tentative
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Float, nullable=True)  # Temps passé en secondes

    # Métadonnées
    attempt_number = Column(Integer, default=1)  # Numéro de tentative pour cet exercice et cet utilisateur
    hints_used = Column(Integer, default=0)  # Nombre d'indices utilisés
    device_info = Column(String, nullable=True)  # Information sur l'appareil utilisé

    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())



    def __repr__(self):
        status = "réussie" if self.is_correct else "échouée"
        return f"<Tentative {self.id}: Utilisateur {self.user_id}, Exercice {self.exercise_id}\
            , {status}>"
