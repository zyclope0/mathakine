"""
Calcul unique niveau / XP dans palier / rang de progression à partir du total persisté.

La clé technique persistée reste ``jedi_rank`` (historique) ; les libellés publics sont neutralisés en UI.
Toute évolution de la formule doit rester centralisée ici.
"""

from app.services.gamification.constants import POINTS_PER_LEVEL

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


def jedi_rank_for_level(level: int) -> str:
    """
    Identifiant de bucket de progression (8 paliers, F42-C3C) dérivé de ``current_level``.

    Seuils (niveau compte = total_points // POINTS_PER_LEVEL + 1) :
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
