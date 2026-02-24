"""
Gestion de l'accès limité pour utilisateurs non vérifiés (First Exercise < 90s).

Règles :
- 0 à UNVERIFIED_GRACE_PERIOD_MINUTES : accès complet (full)
- Au-delà : exercices uniquement (exercises_only)
- Utilisateur vérifié : accès complet (full)
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal

from app.core.config import settings

if TYPE_CHECKING:
    from app.models.user import User

AccessScope = Literal["full", "exercises_only"]


def get_unverified_access_scope(user: "User") -> AccessScope:
    """
    Détermine le scope d'accès pour un utilisateur non vérifié.

    - Utilisateur vérifié : toujours "full"
    - 0 à grace_period min après création : "full" (accès complet)
    - Au-delà : "exercises_only" (exercices uniquement)

    Returns:
        "full" ou "exercises_only"
    """
    if getattr(user, "is_email_verified", True):
        return "full"

    created_at = getattr(user, "created_at", None)
    if not created_at:
        return "full"  # Par défaut si created_at manquant

    # Support des objets naïfs (sans timezone)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - created_at).total_seconds()
    grace_seconds = settings.UNVERIFIED_GRACE_PERIOD_MINUTES * 60

    if elapsed_seconds < grace_seconds:
        return "full"
    return "exercises_only"
