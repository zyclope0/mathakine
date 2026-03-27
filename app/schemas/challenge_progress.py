"""Schémas Pydantic — progression par type de défi (challenge_progress)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgressF42Snapshot(BaseModel):
    """Projection F42 additive (``mastery_tier_bridge``), exercices ou défis."""

    model_config = ConfigDict(extra="ignore")

    canonical_age_group: str
    pedagogical_band: str
    difficulty_tier: Optional[int] = None
    mastery_level: Optional[int] = None
    progress_difficulty_legacy: Optional[str] = None
    mastery_level_challenge: Optional[str] = None


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
    f42: Optional[ProgressF42Snapshot] = None


class ChallengeProgressDetailedResponse(BaseModel):
    """Réponse GET detailed-progress — liste par type."""

    items: List[ChallengeProgressRow]
