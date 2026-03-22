"""
Utilitaires de pagination pour les handlers API.
Factorise le parsing des paramètres skip/limit.
"""

from typing import Any, Tuple


def _coerce_int(n: Any, *, fallback: int) -> int:
    """Convertit en int ; en échec retourne ``fallback``."""
    try:
        return int(n)
    except (TypeError, ValueError):
        return fallback


def _effective_max_limit(max_limit: Any) -> int:
    """
    Plafond effectif pour ``limit``, toujours >= 1.

    Si ``max_limit`` est invalide ou <= 0, borne minimale 1 pour que
    ``1 <= limit <= max`` soit satisfaisable.
    """
    m = _coerce_int(max_limit, fallback=100)
    return max(1, m)


def _clamp_limit(candidate: int, effective_max: int) -> int:
    """
    Normalise ``candidate`` pour respecter ``1 <= limit <= effective_max``.

    Précondition : ``effective_max >= 1``.
    """
    return min(effective_max, max(1, candidate))


def _parse_limit_raw(raw: Any, *, numeric_fallback: int) -> int:
    """
    Interprète une valeur brute de ``limit`` (paramètre query).

    Retourne un entier (éventuellement hors bornes) ; ``numeric_fallback`` si
    valeur absente, vide ou non numérique.
    """
    try:
        if raw in (None, ""):
            return numeric_fallback
        return int(raw)
    except (TypeError, ValueError):
        return numeric_fallback


def parse_pagination_params(
    params: Any,
    *,
    default_limit: int = 20,
    max_limit: int = 100,
) -> Tuple[int, int]:
    """
    Parse skip et limit depuis les paramètres de requête.

    Args:
        params: Dict-like (request.query_params) ou dict.
        default_limit: Valeur par défaut si limit absent ou invalide (normalisée).
        max_limit: Plafond pour limit (si <= 0 ou invalide, un plafond effectif >= 1 est appliqué).

    Returns:
        (skip, limit) avec skip >= 0 et 1 <= limit <= plafond effectif
        (toujours cohérent avec le clamp appliqué).
    """
    effective_max = _effective_max_limit(max_limit)
    default_coerced = _coerce_int(default_limit, fallback=20)
    norm_default = _clamp_limit(default_coerced, effective_max)

    if hasattr(params, "get"):
        skip_raw = params.get("skip", 0)
        limit_raw = params.get("limit", default_limit)
    else:
        skip_raw = 0
        limit_raw = default_limit

    try:
        skip = max(0, int(skip_raw))
    except (TypeError, ValueError):
        skip = 0

    candidate = _parse_limit_raw(limit_raw, numeric_fallback=norm_default)
    limit = _clamp_limit(candidate, effective_max)

    return skip, limit
