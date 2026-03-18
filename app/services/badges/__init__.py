"""
Domaine Badges — services badges et achievements (Lot B3).
"""

from app.services.badges.badge_application_service import BadgeApplicationService
from app.services.badges.badge_requirement_validation import validate_badge_requirements
from app.services.badges.badge_service import BadgeService
from app.services.badges.badge_user_view_service import (
    AVAILABLE_BADGES_DEFAULT_LIMIT,
    AVAILABLE_BADGES_MAX_LIMIT,
)

__all__ = [
    "BadgeApplicationService",
    "BadgeService",
    "AVAILABLE_BADGES_DEFAULT_LIMIT",
    "AVAILABLE_BADGES_MAX_LIMIT",
    "validate_badge_requirements",
]
