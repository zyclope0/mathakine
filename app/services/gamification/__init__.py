"""
Gamification persistante du compte (points, niveau, rang).

Ne couvre pas l'IRT / diagnostic ni la maîtrise par type d'exercice.
"""

from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType

__all__ = ["GamificationService", "PointEventSourceType"]
