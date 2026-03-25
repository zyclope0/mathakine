"""
Périodes du classement par points (agrégation sur ``point_events``).

``month`` = fenêtre glissante de 30 jours (pas mois calendaire).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Optional


class LeaderboardPeriod(StrEnum):
    """Valeurs acceptées pour le paramètre de requête ``period``."""

    ALL = "all"
    WEEK = "week"
    MONTH = "month"


LEADERBOARD_PERIOD_WEEK_DAYS = 7
LEADERBOARD_PERIOD_MONTH_ROLLING_DAYS = 30


def parse_leaderboard_period(raw: Optional[str]) -> LeaderboardPeriod:
    """
    Parse le paramètre ``period`` (query string).

    Raises:
        ValueError: si la valeur n'est pas reconnue.
    """
    if raw is None or raw == "":
        return LeaderboardPeriod.ALL
    key = raw.strip().lower()
    try:
        return LeaderboardPeriod(key)
    except ValueError as exc:
        raise ValueError(f"Invalid leaderboard period: {raw!r}") from exc


def leaderboard_period_cutoff_utc(period: LeaderboardPeriod) -> Optional[datetime]:
    """
    Retourne le seuil ``created_at >= cutoff`` pour filtrer ``point_events``.

    ``None`` signifie : pas de filtre temporel (tout l'historique).
    """
    if period is LeaderboardPeriod.ALL:
        return None
    now = datetime.now(timezone.utc)
    if period is LeaderboardPeriod.WEEK:
        return now - timedelta(days=LEADERBOARD_PERIOD_WEEK_DAYS)
    if period is LeaderboardPeriod.MONTH:
        return now - timedelta(days=LEADERBOARD_PERIOD_MONTH_ROLLING_DAYS)
    raise AssertionError(f"Unhandled period: {period!r}")
