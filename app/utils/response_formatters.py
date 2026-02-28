"""
Utilitaires de formatage des réponses API.
Factorise le format paginé standardisé (items, total, page, limit, hasMore).
"""

from typing import Any, Dict, List


def format_paginated_response(
    items: List[Any],
    total: int,
    skip: int,
    limit: int,
) -> Dict[str, Any]:
    """
    Construit une réponse paginée standardisée.

    Args:
        items: Liste des éléments de la page courante.
        total: Nombre total d'éléments (sans pagination).
        skip: Décalage appliqué.
        limit: Nombre d'éléments par page.

    Returns:
        Dict avec keys: items, total, page, limit, hasMore
    """
    page = (skip // limit) + 1 if limit > 0 else 1
    has_more = (skip + len(items)) < total
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "hasMore": has_more,
    }
