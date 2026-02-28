"""
Tests pour app.utils.pagination (parse_pagination_params).
Vérifie le parsing de skip/limit avec valeurs par défaut et plafonds.
"""

import pytest

from app.utils.pagination import parse_pagination_params


def test_parse_pagination_params_defaults():
    """Sans paramètres → skip=0, limit=default_limit."""
    skip, limit = parse_pagination_params({})
    assert skip == 0
    assert limit == 20


def test_parse_pagination_params_custom_defaults():
    """default_limit et max_limit personnalisés."""
    skip, limit = parse_pagination_params({}, default_limit=50, max_limit=200)
    assert skip == 0
    assert limit == 50


def test_parse_pagination_params_valid_values():
    """Valeurs valides → retournées correctement."""
    params = {"skip": "10", "limit": "25"}
    skip, limit = parse_pagination_params(params)
    assert skip == 10
    assert limit == 25


def test_parse_pagination_params_limit_clamped_to_max():
    """limit > max_limit → clampé à max_limit."""
    params = {"limit": "999"}
    skip, limit = parse_pagination_params(params, max_limit=100)
    assert limit == 100


def test_parse_pagination_params_skip_negative_clamped():
    """skip négatif → clampé à 0."""
    params = {"skip": "-5"}
    skip, limit = parse_pagination_params(params)
    assert skip == 0


def test_parse_pagination_params_invalid_skip_fallback():
    """skip invalide (non-numérique) → 0."""
    params = {"skip": "abc", "limit": "20"}
    skip, limit = parse_pagination_params(params)
    assert skip == 0
    assert limit == 20


def test_parse_pagination_params_invalid_limit_fallback():
    """limit invalide → default_limit."""
    params = {"limit": "x"}
    skip, limit = parse_pagination_params(params)
    assert limit == 20


def test_parse_pagination_params_dict_like():
    """Fonctionne avec un objet dict-like (ex: request.query_params)."""

    class QueryParams:
        def get(self, key, default=None):
            d = {"skip": "5", "limit": "30"}
            return d.get(key, default)

    params = QueryParams()
    skip, limit = parse_pagination_params(params)
    assert skip == 5
    assert limit == 30
