"""F42-C3C — échelle publique 8 buckets (``jedi_rank`` technique canonique)."""

import pytest

from app.services.gamification.compute import (
    canonicalize_progression_rank_bucket,
    compute_state_from_total_points,
    jedi_rank_for_level,
)
from app.services.gamification.constants import POINTS_PER_LEVEL


@pytest.mark.parametrize(
    "level,expected",
    [
        (1, "cadet"),
        (2, "cadet"),
        (3, "scout"),
        (5, "scout"),
        (6, "explorer"),
        (9, "explorer"),
        (10, "navigator"),
        (14, "navigator"),
        (15, "cartographer"),
        (21, "cartographer"),
        (22, "commander"),
        (29, "commander"),
        (30, "stellar_archivist"),
        (41, "stellar_archivist"),
        (42, "cosmic_legend"),
        (99, "cosmic_legend"),
    ],
)
def test_jedi_rank_for_level_boundaries(level: int, expected: str) -> None:
    assert jedi_rank_for_level(level) == expected


def test_compute_state_rank_aligns_with_level() -> None:
    """Même formule que le runtime : niveau dérivé des points puis bucket."""
    samples = [
        (0, 1, "cadet"),
        (POINTS_PER_LEVEL * 2, 3, "scout"),
        (POINTS_PER_LEVEL * 9, 10, "navigator"),
        (POINTS_PER_LEVEL * 21, 22, "commander"),
        (POINTS_PER_LEVEL * 41, 42, "cosmic_legend"),
    ]
    for total, exp_level, exp_rank in samples:
        _t, level, _xp, rank = compute_state_from_total_points(total)
        assert level == exp_level
        assert rank == exp_rank


@pytest.mark.parametrize(
    ("raw_rank", "level", "expected"),
    [
        ("youngling", 1, "cadet"),
        ("padawan", 3, "scout"),
        ("knight", 10, "navigator"),
        ("master", 22, "commander"),
        ("grand_master", 42, "cosmic_legend"),
        ("explorer", 7, "explorer"),
        (None, 6, "explorer"),
    ],
)
def test_canonicalize_progression_rank_bucket(
    raw_rank, level: int, expected: str
) -> None:
    assert canonicalize_progression_rank_bucket(raw_rank, level) == expected
