"""Sources d'attribution de points — valeurs stables en base (ledger)."""

from enum import StrEnum


class PointEventSourceType(StrEnum):
    """Type de source pour un événement du ledger (colonne point_events.source_type)."""

    BADGE_AWARDED = "badge_awarded"
    EXERCISE_COMPLETED = "exercise_completed"
    DAILY_CHALLENGE_COMPLETED = "daily_challenge_completed"
