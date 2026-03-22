"""Exceptions métier — gamification persistante."""


class GamificationError(Exception):
    """Erreur de domaine gamification (compte)."""


class GamificationUserNotFoundError(GamificationError):
    """Utilisateur introuvable pour une opération de points."""


class InvalidGamificationPointsDeltaError(GamificationError):
    """Delta de points invalide (ex. négatif ou nul quand une attribution est requise)."""
