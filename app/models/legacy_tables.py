"""
Modèles SQLAlchemy pour les tables héritées de l'ancienne base de données.
Ces modèles sont inclus pour la compatibilité avec la base de données existante.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Results(Base):
    """Modèle pour la table results (résultats d'exercices)."""
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempt_count = Column(Integer, server_default=text('1'))
    time_spent = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    def __repr__(self):
        return f"<Result(id={self.id}, exercise_id={self.exercise_id}, correct={self.is_correct})>"


class Statistics(Base):
    """Modèle pour la table statistics (statistiques par session)."""
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(255), nullable=False)
    exercise_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    total_attempts = Column(Integer, server_default=text('0'), nullable=False)
    correct_attempts = Column(Integer, server_default=text('0'), nullable=False)
    avg_time = Column(Float, server_default=text('0'), nullable=False)
    last_updated = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    def __repr__(self):
        return f"<Statistics(id={self.id}, session_id={self.session_id}, exercise_type={self.exercise_type})>"


class UserStats(Base):
    """Modèle pour la table user_stats (statistiques utilisateur)."""
    __tablename__ = 'user_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    total_attempts = Column(Integer, server_default=text('0'))
    correct_attempts = Column(Integer, server_default=text('0'))
    last_updated = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    def __repr__(self):
        return f"<UserStats(id={self.id}, exercise_type={self.exercise_type}, difficulty={self.difficulty})>"


class SchemaVersion(Base):
    """Modèle pour la table schema_version (version du schéma)."""
    __tablename__ = 'schema_version'
    
    version = Column(Integer, primary_key=True)
    
    def __repr__(self):
        return f"<SchemaVersion(version={self.version})>" 