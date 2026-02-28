"""Tests pour app.utils.response_formatters."""

import pytest

from app.utils.response_formatters import format_paginated_response


def test_format_paginated_response_basic():
    """Format standard avec items, total, skip, limit."""
    items = [{"id": 1}, {"id": 2}]
    out = format_paginated_response(items, total=10, skip=0, limit=2)
    assert out["items"] == items
    assert out["total"] == 10
    assert out["page"] == 1
    assert out["limit"] == 2
    assert out["hasMore"] is True


def test_format_paginated_response_last_page():
    """Dernière page → hasMore=False."""
    items = [{"id": 9}]
    out = format_paginated_response(items, total=10, skip=9, limit=5)
    assert out["hasMore"] is False
    assert out["page"] == 2


def test_format_paginated_response_empty():
    """Liste vide."""
    out = format_paginated_response([], total=0, skip=0, limit=20)
    assert out["items"] == []
    assert out["total"] == 0
    assert out["page"] == 1
    assert out["hasMore"] is False
