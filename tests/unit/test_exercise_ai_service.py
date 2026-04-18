"""Unit tests for exercise_ai_service — pure data contracts.

Couvre les invariants structurels de ``DIFFICULTY_RANGES`` (Lot A — calibration
de difficulté à la génération). Les plages numériques injectées dans le prompt
LLM doivent respecter une monotonie stricte pour éviter l'ancrage bas observé
sur les plages chevauchantes précédentes.
"""

from __future__ import annotations

from app.services.exercises.exercise_ai_service import DIFFICULTY_RANGES

_ORDERED_LEVELS = ("INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GRAND_MAITRE")


def test_difficulty_ranges_five_levels_exact() -> None:
    assert set(DIFFICULTY_RANGES.keys()) == set(_ORDERED_LEVELS)
    assert len(DIFFICULTY_RANGES) == 5


def test_difficulty_ranges_strictly_monotonic_min() -> None:
    # Contrainte : min_{i+1} == max_i pour les 4 transitions consécutives.
    for prev, nxt in zip(_ORDERED_LEVELS, _ORDERED_LEVELS[1:]):
        prev_max = DIFFICULTY_RANGES[prev]["max"]
        nxt_min = DIFFICULTY_RANGES[nxt]["min"]
        assert nxt_min == prev_max, (
            f"transition {prev} -> {nxt} : min attendu == max précédent "
            f"({prev_max}) ; observé : {nxt_min}"
        )


def test_difficulty_ranges_strictly_monotonic_max() -> None:
    # max_{i+1} > max_i : les plafonds progressent strictement.
    for prev, nxt in zip(_ORDERED_LEVELS, _ORDERED_LEVELS[1:]):
        prev_max = DIFFICULTY_RANGES[prev]["max"]
        nxt_max = DIFFICULTY_RANGES[nxt]["max"]
        assert nxt_max > prev_max, (
            f"transition {prev} -> {nxt} : max attendu strictement supérieur "
            f"({prev_max}) ; observé : {nxt_max}"
        )


def test_difficulty_ranges_desc_non_empty_and_distinct() -> None:
    descs = [DIFFICULTY_RANGES[level]["desc"] for level in _ORDERED_LEVELS]
    for level, desc in zip(_ORDERED_LEVELS, descs):
        assert isinstance(desc, str)
        assert desc.strip(), f"desc vide pour {level}"
    assert len(set(descs)) == 5, "les 5 descriptions doivent être distinctes"


def test_difficulty_ranges_min_strictly_positive_for_all_levels() -> None:
    # Garde-fou additionnel : aucun niveau ne doit autoriser min <= 0
    # (plages numériques côté exercices, pas de signed).
    for level in _ORDERED_LEVELS:
        assert DIFFICULTY_RANGES[level]["min"] >= 1


def test_difficulty_ranges_max_strictly_greater_than_min_per_level() -> None:
    # Intra-niveau : max > min, évite un niveau dégénéré min == max.
    for level in _ORDERED_LEVELS:
        entry = DIFFICULTY_RANGES[level]
        assert (
            entry["max"] > entry["min"]
        ), f"{level} : max ({entry['max']}) doit être > min ({entry['min']})"
