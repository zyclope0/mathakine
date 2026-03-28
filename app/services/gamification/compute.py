"""
Calculs déterministes de progression compte (niveau / XP / rang).

F42-P4 : la progression n'est plus linéaire à 100 pts / niveau.
``total_points`` reste la source de vérité ; ``current_level`` et
``experience_points`` sont dérivés par une courbe à paliers de coût.

La clé technique persistée reste ``jedi_rank`` (historique) ; les buckets
publics canoniques (F42-C3C) sont dérivés du niveau synthétisé.
"""

from __future__ import annotations

from typing import Optional, Tuple

from app.services.gamification.constants import LEVEL_UP_COST_SEGMENTS

_CANONICAL_PROGRESS_RANKS = frozenset(
    {
        "cadet",
        "scout",
        "explorer",
        "navigator",
        "cartographer",
        "commander",
        "stellar_archivist",
        "cosmic_legend",
    }
)

_LEGACY_PROGRESS_RANKS = frozenset(
    {
        "youngling",
        "padawan",
        "knight",
        "master",
        "grand_master",
    }
)

_LEGACY_TO_CANONICAL_FALLBACK = {
    "youngling": "cadet",
    "padawan": "explorer",
    "knight": "navigator",
    "master": "commander",
    "grand_master": "cosmic_legend",
}


def cost_to_advance_from_level(level: int) -> int:
    """
    Coût en points pour passer du niveau ``level`` au niveau ``level + 1``.

    ``level`` est le niveau courant (>= 1).
    """
    if level < 1:
        level = 1
    for level_max, cost in LEVEL_UP_COST_SEGMENTS:
        if level <= level_max:
            return int(cost)
    return int(LEVEL_UP_COST_SEGMENTS[-1][1])


def cumulative_points_at_level_start(level: int) -> int:
    """
    Points cumulés minimum pour *être* au niveau ``level`` (plancher inclus).

    Niveau 1 : 0 point.
    """
    if level <= 1:
        return 0
    total = 0
    for L in range(1, level):
        total += cost_to_advance_from_level(L)
    return int(total)


def level_and_xp_from_total_points(total_points: int) -> Tuple[int, int]:
    """Déduit (niveau, xp_dans_le_niveau) à partir de ``total_points`` (>= 0)."""
    total = max(0, int(total_points))
    level = 1
    while cumulative_points_at_level_start(level + 1) <= total:
        level += 1
    xp = total - cumulative_points_at_level_start(level)
    return int(level), int(xp)


def experience_points_in_current_level(total_points: int) -> int:
    """Alias explicite : XP accumulée dans le niveau courant."""
    _, xp = level_and_xp_from_total_points(total_points)
    return int(xp)


def points_to_gain_next_level(current_level: int) -> int:
    """Points nécessaires pour passer du niveau courant au suivant."""
    return int(cost_to_advance_from_level(current_level))


def jedi_rank_for_level(level: int) -> str:
    """
    Identifiant de bucket de progression (8 paliers, F42-C3C) dérivé du niveau synthétisé.

    Seuils (``level`` issu de ``total_points`` via la courbe F42-P4) :
      cadet < 3 · scout < 6 · explorer < 10 · navigator < 15 ·
      cartographer < 22 · commander < 30 · stellar_archivist < 42 · cosmic_legend au-delà.
    """
    if level < 3:
        return "cadet"
    if level < 6:
        return "scout"
    if level < 10:
        return "explorer"
    if level < 15:
        return "navigator"
    if level < 22:
        return "cartographer"
    if level < 30:
        return "commander"
    if level < 42:
        return "stellar_archivist"
    return "cosmic_legend"


def canonicalize_progression_rank_bucket(
    raw_rank: object, level: int | None = None
) -> str:
    """
    Retourne le bucket canonique F42-C3C pour une valeur persistée historique.

    Priorité:
    - bucket canonique déjà valide -> inchangé
    - bucket legacy + niveau compte connu -> recalcul via `jedi_rank_for_level(level)`
    - bucket legacy sans niveau exploitable -> mapping de compatibilité approximatif
    - valeur vide/invalide -> bucket dérivé du niveau si possible, sinon `cadet`
    """
    rank = str(raw_rank or "").strip().lower()
    if rank in _CANONICAL_PROGRESS_RANKS:
        return rank

    safe_level = int(level) if level is not None else None
    if (
        safe_level is not None
        and safe_level > 0
        and (rank in _LEGACY_PROGRESS_RANKS or not rank)
    ):
        return jedi_rank_for_level(safe_level)

    if rank in _LEGACY_TO_CANONICAL_FALLBACK:
        return _LEGACY_TO_CANONICAL_FALLBACK[rank]

    if safe_level is not None and safe_level > 0:
        return jedi_rank_for_level(safe_level)
    return "cadet"


def compute_state_from_total_points(total_points: int) -> Tuple[int, int, int, str]:
    """
    Retourne (total_points_clamped, current_level, experience_points, jedi_rank).

    Niveau et XP dans le palier sont dérivés de ``total_points`` par la courbe
    à segments ``LEVEL_UP_COST_SEGMENTS``.
    """
    total = max(0, int(total_points))
    level, xp_in_bracket = level_and_xp_from_total_points(total)
    rank = jedi_rank_for_level(level)
    return total, level, xp_in_bracket, rank
