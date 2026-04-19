"""Unit tests for exercise_ai_service — pure data contracts.

Couvre les invariants structurels de ``DIFFICULTY_RANGES`` (Lot A — calibration
de difficulté à la génération). Les plages numériques injectées dans le prompt
LLM doivent respecter une monotonie stricte pour éviter l'ancrage bas observé
sur les plages chevauchantes précédentes.
"""

from __future__ import annotations

from app.services.exercises.exercise_ai_service import (
    DIFFICULTY_RANGES,
    _HIGH_DIFFICULTY_DIRECTIVE_ATOMIC,
    _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP,
    _non_triviality_hint,
    build_exercise_system_prompt,
)

_ORDERED_LEVELS = ("INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GRAND_MAITRE")

_EXERCISE_TYPES = (
    "addition",
    "soustraction",
    "multiplication",
    "division",
    "fractions",
    "geometrie",
    "texte",
    "mixte",
    "divers",
)


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


# ---------------------------------------------------------------------------
# Lot C — guidance non-trivialité conditionnelle au type
# ---------------------------------------------------------------------------


def test_non_triviality_empty_for_initie_and_padawan() -> None:
    for et in _EXERCISE_TYPES:
        for diff in ("INITIE", "PADAWAN", "initie", " padawan "):
            assert _non_triviality_hint(et, diff) == ""


def test_non_triviality_atomic_addition_grand_maitre() -> None:
    assert (
        _non_triviality_hint("addition", "GRAND_MAITRE")
        == _HIGH_DIFFICULTY_DIRECTIVE_ATOMIC
    )


def test_non_triviality_narrative_texte_chevalier() -> None:
    assert (
        _non_triviality_hint("texte", "CHEVALIER")
        == _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["CHEVALIER"]
    )


def test_non_triviality_narrative_mixte_maitre() -> None:
    assert (
        _non_triviality_hint("mixte", "MAITRE")
        == _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["MAITRE"]
    )


def test_system_prompt_includes_directive_when_chevalier_texte() -> None:
    prompt = build_exercise_system_prompt(
        "texte",
        "CHEVALIER",
        "9-11",
        {"desc": "test desc"},
        "",
        calibration_desc="calibration test",
    )
    assert "- Exigence de difficulté :" in prompt
    assert _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["CHEVALIER"] in prompt


def test_system_prompt_has_no_directive_for_initie() -> None:
    prompt = build_exercise_system_prompt(
        "texte",
        "INITIE",
        "9-11",
        {"desc": "test desc"},
        "",
        calibration_desc="calibration test",
    )
    assert "Exigence de difficulté" not in prompt
