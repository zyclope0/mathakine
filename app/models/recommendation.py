from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Recommendation(Base):
    """Modèle pour les recommandations personnalisées d'exercices (Conseils de Maître Jedi)"""
    __tablename__ = "recommendations"
    
    # Index composites pour les requêtes fréquentes
    __table_args__ = (
        Index('ix_recommendations_user_completed', 'user_id', 'is_completed'),
        Index('ix_recommendations_user_priority', 'user_id', 'priority'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relations (avec index sur les FK pour les JOINs)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="recommendations")
    
    # Exercice recommandé (optionnel - peut être une recommandation par type)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="SET NULL"), nullable=True, index=True)
    exercise = relationship("Exercise", backref="recommendations")
    
    # Catégorisation (toujours présent même si exercise_id est NULL)
    exercise_type = Column(String, nullable=False, index=True)
    difficulty = Column(String, nullable=False)
    
    # Méta-données de recommandation
    priority = Column(Integer, default=5, index=True)  # 1-10 (plus c'est élevé, plus c'est prioritaire)
    reason = Column(Text, nullable=True)   # Raison de la recommandation en langage naturel
    is_completed = Column(Boolean, default=False, index=True)  # L'utilisateur a-t-il complété cette recommandation
    
    # Statistiques d'utilisation
    shown_count = Column(Integer, default=0)  # Nombre de fois que cette recommandation a été affichée
    clicked_count = Column(Integer, default=0)  # Nombre de fois que l'utilisateur a cliqué dessus
    last_clicked_at = Column(DateTime(timezone=True), nullable=True)  # Date du dernier clic
    completed_at = Column(DateTime(timezone=True), nullable=True)  # Date de complétion
    
    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    
    
    def __repr__(self):
        exercise_info = f", Exercice {self.exercise_id}" if self.exercise_id else ""
        return f"<Recommandation: Utilisateur {self.user_id}{exercise_info}, Priorité {self.priority}>" 