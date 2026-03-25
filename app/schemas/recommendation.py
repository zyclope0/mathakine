from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class RecommendationBase(BaseModel):
    """Schéma de base pour les recommandations (exercices et défis logiques)."""

    exercise_type: str = Field(
        ...,
        description="Type disciplinaire / catalogue (exercice ou piste pour reco défi)",
    )
    difficulty: str = Field(
        ...,
        description="Niveau de difficulté cible (exercice ou défi)",
    )
    priority: int = Field(
        5, ge=1, le=10, description="Priorité de la recommandation (1-10)"
    )
    reason: Optional[str] = Field(None, description="Raison de la recommandation")
    reason_code: Optional[str] = Field(
        None, description="Clé stable pour i18n (R5, optionnel)"
    )
    reason_params: Optional[Dict[str, Any]] = Field(
        None, description="Paramètres interpolables pour la raison (R5)"
    )


class RecommendationCreate(RecommendationBase):
    """Schéma pour la création de recommandations"""

    user_id: int = Field(..., description="ID de l'utilisateur")
    exercise_id: Optional[int] = Field(
        None, description="ID de l'exercice recommandé (optionnel)"
    )
    challenge_id: Optional[int] = Field(
        None, description="ID du défi logique recommandé (optionnel)"
    )
    recommendation_type: Optional[str] = Field(
        None,
        description='Type de recommandation : "exercise" ou "challenge" (optionnel)',
    )


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
    challenge_id: Optional[int] = None
    recommendation_type: Optional[str] = None
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
    challenge_id: Optional[int] = None
    challenge_title: Optional[str] = None
    recommendation_type: Optional[str] = None
