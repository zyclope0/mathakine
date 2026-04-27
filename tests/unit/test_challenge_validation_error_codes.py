"""Tests for stable validation error code classification (Phase 1B)."""

from __future__ import annotations

from pathlib import Path

from app.services.challenges import challenge_validation_error_codes as cvec


def test_mapper_examples_by_family() -> None:
    assert (
        cvec.classify_challenge_validation_error("CHESS: pièce invalide '9' en [0,0]")
        == "chess_invalid_piece"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "CHESS: roi noir déjà en échec alors que c'est aux Blancs de jouer"
        )
        == "chess_king_in_check"
    )
    mojib = (
        "CHESS: roi noir d\u00c3\u00a9j\u00c3\u00a0 en \u00c3\u00a9chec "
        "alors que c'est aux Blancs de jouer"
    )
    assert cvec.classify_challenge_validation_error(mojib) == "chess_king_in_check"
    assert (
        cvec.classify_challenge_validation_error("RIDDLE: visual_data manquant")
        == "missing_visual_data"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "PUZZLE incomplet: aucun indice (hints/rules/clues) ni description fourni. "
        )
        == "puzzle_missing_clues"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "DEDUCTION: les indices reconnus ne mènent pas à une solution unique "
            "(plusieurs plannings restent possibles). Ajouter un indice discriminant."
        )
        == "deduction_no_unique_solution"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "PROBABILITY: correct_answer incohérent avec visual_data. "
            "Attendu environ 50.00%, reçu 0.1."
        )
        == "probability_answer_inconsistent"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "PROBABILITY: le total des poids d'urne doit sommer a 1.0 "
            "pour une distribution valide (urns)."
        )
        == "probability_sum_not_one"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "QCM PROBABILITY : des options sont mathematiquement equivalentes (x).",
            challenge_type="PROBABILITY",
        )
        == "probability_equivalent_choices"
    )
    assert (
        cvec.classify_challenge_validation_error(
            "Pattern multi-cellules non verifiable: "
            "correct_answer doit contenir 2 valeurs separees par des virgules"
        )
        == "pattern_unverifiable"
    )


def test_dedup_and_order() -> None:
    out = cvec.classify_challenge_validation_errors(
        [
            "CHESS: pièce invalide 'x' en [1,1]",
            "CHESS: pièce invalide 'y' en [2,2]",
            "QCM: des options sont en doublon (ou quasi-identiques apres normalisation) -",
        ],
        challenge_type="chess",
    )
    assert out == ["chess_invalid_piece", "duplicate_choices"]


def test_validation_unknown() -> None:
    assert cvec.classify_challenge_validation_error("Xyzzy total nonsense") == (
        "validation_unknown"
    )


def test_deduction_duplicate_first_segment_classified() -> None:
    """Message structurel `same first-category entity x N` doit être distinct de no_unique_solution."""
    msg = "DEDUCTION: une même entité (première catégorie) apparaît plusieurs fois"
    assert (
        cvec.classify_challenge_validation_error(msg)
        == "deduction_duplicate_first_segment"
    )


def test_deduction_bijection_violated_classified() -> None:
    """Message structurel `one-to-one violated` doit être distinct de no_unique_solution."""
    msg = (
        "DEDUCTION: la catégorie « Maison » impose une assignation one-to-one : "
        "une même valeur apparaît pour plusieurs lignes "
        "(ex. deux personnes avec la même valeur)."
    )
    assert (
        cvec.classify_challenge_validation_error(msg) == "deduction_bijection_violated"
    )


def test_deduction_no_unique_solution_still_classified() -> None:
    """Régression-guard : les nouvelles règles ne doivent pas voler le code existant."""
    msg = (
        "DEDUCTION: les indices reconnus ne mènent pas à une solution unique "
        "(plusieurs plannings restent possibles). Ajouter un indice discriminant."
    )
    assert (
        cvec.classify_challenge_validation_error(msg) == "deduction_no_unique_solution"
    )


def test_deduction_answer_entities_missing_positive() -> None:
    """Message validateur : entités manquantes dans correct_answer (première catégorie)."""
    msg = (
        "DEDUCTION: entités manquantes dans correct_answer (première catégorie): "
        "['Alice', 'Bob']"
    )
    assert (
        cvec.classify_challenge_validation_error(msg)
        == "deduction_answer_entities_missing"
    )


def test_deduction_answer_entities_missing_negative_does_not_match_other() -> None:
    """Garde-fou : un message d'entité non-DEDUCTION ne doit pas matcher cette règle."""
    msg = "GRAPH: entités manquantes dans correct_answer"
    assert (
        cvec.classify_challenge_validation_error(msg)
        != "deduction_answer_entities_missing"
    )

    msg2 = "DEDUCTION: contradiction détectée, aucune solution"
    assert (
        cvec.classify_challenge_validation_error(msg2)
        != "deduction_answer_entities_missing"
    )


def test_challenge_pipeline_resolved_log_uses_loguru_braces() -> None:
    p = (
        Path(__file__).resolve().parent.parent.parent
        / "app"
        / "services"
        / "challenges"
        / "challenge_ai_service.py"
    )
    text = p.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Challenge pipeline resolved:" in line:
            assert "%s" not in line, line
