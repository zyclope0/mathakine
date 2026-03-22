"""
IA3 — générateur simple local : invariants métier, politique de titres, choix distincts.

Couvre la non-régression du lot qualité (hors flux OpenAI).
"""

import random
import re

import pytest

from app.core.constants import DIFFICULTY_LIMITS, DifficultyLevels, ExerciseTypes
from app.generators.exercise_generation_policy import (
    SIMPLE_TITLE_ADDITION,
    pick_title_variant,
)
from app.generators.exercise_generator import generate_simple_exercise
from app.utils.exercise_generator_helpers import (
    ensure_four_distinct_str_choices,
    generate_smart_choices,
)


def test_pick_title_variant_deterministic_and_bounded() -> None:
    assert pick_title_variant(SIMPLE_TITLE_ADDITION, salt=0) in SIMPLE_TITLE_ADDITION
    assert pick_title_variant(SIMPLE_TITLE_ADDITION, salt=0) == pick_title_variant(
        SIMPLE_TITLE_ADDITION, salt=0
    )
    assert len(SIMPLE_TITLE_ADDITION) >= 4


def test_ensure_four_distinct_str_choices_no_duplicates() -> None:
    out = ensure_four_distinct_str_choices("5", ["5", "5", "6", "7"])
    assert len(out) == 4
    assert len(set(out)) == 4
    assert "5" in out


@pytest.mark.parametrize(
    "op", ("ADDITION", "SOUSTRACTION", "MULTIPLICATION", "DIVISION")
)
def test_generate_smart_choices_four_distinct_with_explicit_difficulty(
    op: str,
) -> None:
    random.seed(123)
    if op == "ADDITION":
        n1, n2, r = 12, 15, 27
    elif op == "SOUSTRACTION":
        n1, n2, r = 20, 7, 13
    elif op == "MULTIPLICATION":
        n1, n2, r = 4, 6, 24
    else:
        n1, n2, r = 24, 4, 6
    ch = generate_smart_choices(
        op, n1, n2, r, "9-11", derived_difficulty=DifficultyLevels.PADAWAN
    )
    assert len(ch) == 4
    assert len(set(ch)) == 4
    assert str(r) in ch


def test_simple_addition_initie_respects_difficulty_limits() -> None:
    """Plages issues de DIFFICULTY_LIMITS[INITIE][ADDITION] (âge 6-8 → INITIE)."""
    lim = DIFFICULTY_LIMITS[DifficultyLevels.INITIE][ExerciseTypes.ADDITION]
    lo, hi = lim["min"], lim["max"]
    random.seed(99)
    for _ in range(40):
        ex = generate_simple_exercise("ADDITION", "6-8")
        assert ex["exercise_type"] == "ADDITION"
        assert ex["difficulty"] == "INITIE"
        n1, n2 = ex["num1"], ex["num2"]
        assert lo <= n1 <= hi
        assert lo <= n2 <= hi
        assert int(ex["correct_answer"]) == n1 + n2


def test_simple_exercise_qcm_invariants_many_seeds() -> None:
    random.seed(7)
    for _ in range(25):
        ex = generate_simple_exercise("MULTIPLICATION", "9-11")
        ch = [str(c) for c in ex["choices"]]
        assert len(ch) == 4
        assert len(set(ch)) == 4
        assert ex["correct_answer"] in ch
        assert (
            int(ex["correct_answer"]) == ex["num1"] * ex["num2"]
        ), "Cohérence question / réponse"


def test_division_quotient_one_no_duplicate_choices() -> None:
    """Cas limite quotient 1 : anciennement « 1 » et « max(1,0) » pouvaient coïncider."""
    for seed in range(500):
        random.seed(seed)
        ex = generate_simple_exercise("DIVISION", "6-8")
        if ex["correct_answer"] == "1":
            ch = [str(c) for c in ex["choices"]]
            assert len(set(ch)) == 4
            assert "1" in ch
            return
    pytest.fail("Aucun tirage quotient=1 en 500 graines — affaiblir le test si besoin")


def test_simple_subtraction_result_non_negative() -> None:
    random.seed(11)
    for _ in range(30):
        ex = generate_simple_exercise("SOUSTRACTION", "9-11")
        assert int(ex["correct_answer"]) >= 0
        assert ex["num1"] > ex["num2"]


def test_divers_moyenne_exact_integer_mean_no_truncation() -> None:
    """
    Branche DIVERS / moyenne : la somme doit être divisible par le nombre de termes ;
    correct_answer et explication alignés sur la vraie moyenne (plus de // sur quotient faux).
    """
    pat = re.compile(
        r"moyenne de ces nombres\s*:\s*([0-9,\s]+)\s*\?",
        re.IGNORECASE,
    )
    hits = 0
    for seed in range(5000):
        random.seed(seed)
        ex = generate_simple_exercise("DIVERS", "15-17")
        m = pat.search(ex["question"])
        if not m:
            continue
        hits += 1
        nums = [int(x.strip()) for x in m.group(1).split(",")]
        n = len(nums)
        total = sum(nums)
        assert (
            total % n == 0
        ), f"somme non divisible par le cardinal — moyenne tronquée possible: {nums}"
        true_mean = total // n
        assert int(ex["correct_answer"]) == true_mean
        assert str(total) in ex["explanation"]
        assert str(n) in ex["explanation"]
        assert str(true_mean) in ex["explanation"]
    assert (
        hits >= 20
    ), "la branche moyenne doit être exercée (augmenter les graines si besoin)"
