"""
Schémas pour les endpoints badges utilisateur/public.
"""

from typing import List

from pydantic import BaseModel, Field


class PinnedBadgesRequest(BaseModel):
    """Payload PATCH /api/badges/pin — liste des IDs de badges à épingler (max 3 utilisés)."""

    badge_ids: List[int] = Field(
        default_factory=list,
        description="IDs des badges à épingler (max 3, parmi les badges obtenus)",
    )
