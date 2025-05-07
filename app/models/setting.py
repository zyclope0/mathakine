from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Setting(Base):
    """Modèle pour la configuration de l'application (Configuration du Temple)"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=True)
    value_json = Column(JSON, nullable=True)  # Pour les valeurs complexes
    
    # Métadonnées
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)  # Catégorie: système, interface, exercice, etc.
    is_system = Column(Boolean, default=False)  # Si c'est un paramètre système (non modifiable par l'utilisateur)
    is_public = Column(Boolean, default=True)   # Si visible dans l'interface
    
    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Paramètre: {self.key}>" 