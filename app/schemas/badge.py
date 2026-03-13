"""
Schémas pour les endpoints badges utilisateur/public.
"""

from typing import List

from pydantic import BaseModel, Field


class PinBadgesResult(BaseModel):
    """Résultat PATCH /api/badges/pin — IDs des badges épinglés."""

    pinned_badge_ids: List[int] = Field(
        default_factory=list,
        description="IDs des badges épinglés (max 3)",
    )


class PinnedBadgesRequest(BaseModel):
    """Payload PATCH /api/badges/pin — liste des IDs de badges à épingler (max 3 utilisés)."""

    badge_ids: List[int] = Field(
        default_factory=list,
        description="IDs des badges à épingler (max 3, parmi les badges obtenus)",
    )
