"""Schémas Pydantic — progression par type de défi (challenge_progress)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChallengeProgressRow(BaseModel):
    """Une ligne agrégée (user + challenge_type)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    challenge_type: str = Field(
        ..., description="Valeur enum type de défi (ex. sequence)"
    )
    total_attempts: int
    correct_attempts: int
    completion_rate: float = Field(
        ..., description="Pourcentage de réussite 0–100 sur les tentatives enregistrées"
    )
    mastery_level: str
    last_attempted_at: Optional[datetime] = None


class ChallengeProgressDetailedResponse(BaseModel):
    """Réponse GET detailed-progress — liste par type."""

    items: List[ChallengeProgressRow]
