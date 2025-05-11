from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.exercise import ExerciseType



class Progress(Base):
    """Modèle pour suivre la progression des utilisateurs (Chemin vers la Maîtrise)"""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)

    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="progress_records")

    # Données de progression
    exercise_type = Column(String, nullable=False)  # Type d'exercice (addition, soustraction, etc.)
    difficulty = Column(String, nullable=False)     # Niveau de difficulté
    total_attempts = Column(Integer, default=0)     # Nombre total de tentatives
    correct_attempts = Column(Integer, default=0)   # Nombre de tentatives réussies

    # Métriques de performance
    average_time = Column(Float, nullable=True)        # Temps moyen pour résoudre
    completion_rate = Column(Float, nullable=True)     # Taux de complétion (%)
    streak = Column(Integer, default=0)                # Série actuelle d'exercices réussis
    highest_streak = Column(Integer, default=0)        # Meilleure série

    # Niveau de maîtrise (compatible avec le thème Star Wars)
    # 1: Novice, 2: Initié, 3: Padawan, 4: Chevalier, 5: Maître
    mastery_level = Column(Integer, default=1)

    # Médailles et récompenses (format JSON)
    awards = Column(JSON, nullable=True)

    # Données analytiques et conseils
    strengths = Column(String, nullable=True)        # Points forts identifiés
    areas_to_improve = Column(String, nullable=True) # Domaines à améliorer
    recommendations = Column(String, nullable=True)  # Exercices recommandés

    # Horodatage
    last_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())



    def __repr__(self):
        return f"<Progression: {self.user_id}, {self.exercise_type}, Niveau {self.mastery_level}>"



    def calculate_completion_rate(self):
        """Calcule le taux de complétion"""
        if self.total_attempts == 0:
            return 0
        return (self.correct_attempts / self.total_attempts) * 100



    def update_mastery_level(self):
        """Met à jour le niveau de maîtrise basé sur le taux de complétion"""
        rate = self.calculate_completion_rate()
        if rate >= 95:
            self.mastery_level = 5  # Maître
        elif rate >= 85:
            self.mastery_level = 4  # Chevalier
        elif rate >= 70:
            self.mastery_level = 3  # Padawan
        elif rate >= 50:
            self.mastery_level = 2  # Initié
        else:
            self.mastery_level = 1  # Novice
