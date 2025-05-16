from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base



class Recommendation(Base):
    """Modèle pour les recommandations personnalisées d'exercices (Conseils de Maître Jedi)"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relations
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="recommendations")
    
    # Exercice recommandé (optionnel - peut être une recommandation par type)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="SET NULL"), nullable=True)
    exercise = relationship("Exercise", backref="recommendations")
    
    # Catégorisation (toujours présent même si exercise_id est NULL)
    exercise_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    
    # Méta-données de recommandation
    priority = Column(Integer, default=5)  # 1-10 (plus c'est élevé, plus c'est prioritaire)
    reason = Column(Text, nullable=True)   # Raison de la recommandation en langage naturel
    is_completed = Column(Boolean, default=False)  # L'utilisateur a-t-il complété cette recommandation
    
    # Statistiques d'utilisation
    shown_count = Column(Integer, default=0)  # Nombre de fois que cette recommandation a été affichée
    clicked_count = Column(Integer, default=0)  # Nombre de fois que l'utilisateur a cliqué dessus
    
    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    
    
    def __repr__(self):
        exercise_info = f", Exercice {self.exercise_id}" if self.exercise_id else ""
        return f"<Recommandation: Utilisateur {self.user_id}{exercise_info}, Priorité {self.priority}>" 