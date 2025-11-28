from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RecommendationBase(BaseModel):
    """Schéma de base pour les recommandations d'exercices"""
    exercise_type: str = Field(..., description="Type d'exercice recommandé")
    difficulty: str = Field(..., description="Niveau de difficulté recommandé")
    priority: int = Field(5, ge=1, le=10, description="Priorité de la recommandation (1-10)")
    reason: Optional[str] = Field(None, description="Raison de la recommandation")

class RecommendationCreate(RecommendationBase):
    """Schéma pour la création de recommandations"""
    user_id: int = Field(..., description="ID de l'utilisateur")
    exercise_id: Optional[int] = Field(None, description="ID de l'exercice recommandé (optionnel)")
    
class RecommendationUpdate(BaseModel):
    """Schéma pour la mise à jour de recommandations"""
    is_completed: Optional[bool] = Field(None, description="Marqué comme complété")
    shown_count: Optional[int] = Field(None, description="Nombre d'affichages")
    clicked_count: Optional[int] = Field(None, description="Nombre de clics")

class RecommendationInDB(RecommendationBase):
    """Schéma pour les recommandations stockées en base de données"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    exercise_id: Optional[int] = None
    is_completed: bool
    shown_count: int
    clicked_count: int
    created_at: datetime
    updated_at: datetime

class RecommendationResponse(RecommendationBase):
    """Schéma pour la réponse API de recommandations"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    exercise_id: Optional[int] = None
    exercise_title: Optional[str] = None
    exercise_question: Optional[str] = None 