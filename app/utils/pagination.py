"""
Utilitaires de pagination pour les handlers API.
Factorise le parsing des paramètres skip/limit.
"""

from typing import Any, Tuple


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
        default_limit: Valeur par défaut si limit absent.
        max_limit: Plafond pour limit.

    Returns:
        (skip, limit) avec skip >= 0 et 1 <= limit <= max_limit.
    """
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

    try:
        limit = int(limit_raw) if limit_raw not in (None, "") else default_limit
        limit = min(max_limit, max(1, limit))
    except (TypeError, ValueError):
        limit = default_limit

    return skip, limit
