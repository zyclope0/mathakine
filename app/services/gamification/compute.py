"""
Calcul unique niveau / XP dans palier / rang Jedi à partir du total persisté.

Toute évolution de la formule doit rester centralisée ici.
"""

from app.services.gamification.constants import POINTS_PER_LEVEL


def jedi_rank_for_level(level: int) -> str:
    """Rang Jedi dérivé du niveau gamification (compte)."""
    if level < 5:
        return "youngling"
    if level < 15:
        return "padawan"
    if level < 30:
        return "knight"
    if level < 50:
        return "master"
    return "grand_master"


def compute_state_from_total_points(total_points: int) -> tuple[int, int, int, str]:
    """
    Retourne (total_points_clamped, current_level, experience_points, jedi_rank).

    - current_level : max(1, total // POINTS_PER_LEVEL + 1)
    - experience_points : total % POINTS_PER_LEVEL
    """
    total = max(0, int(total_points))
    if POINTS_PER_LEVEL <= 0:
        raise ValueError("POINTS_PER_LEVEL doit être > 0")
    level = max(1, total // POINTS_PER_LEVEL + 1)
    xp_in_bracket = total % POINTS_PER_LEVEL
    rank = jedi_rank_for_level(level)
    return total, level, xp_in_bracket, rank
