"""
Tests de caractérisation pour ChallengeAnswerService.

Valident le comportement de chaque stratégie de comparaison de réponses
AVANT le refactoring du handler challenge.

Phase 3, item 3.1a — audit architecture 03/2026.
"""

import pytest

from app.services.challenges.challenge_answer_service import (
    check_answer,
    compare_chess,
    compare_deduction,
    compare_graph,
    compare_probability,
    compare_sequence_default,
    compare_visual_pattern,
    normalize_accents,
    normalize_shape_answer,
    parse_answer_to_list,
    parse_multi_visual_answer,
)

# ── Helpers ───────────────────────────────────────────────────────────────


class TestNormalizeAccents:
    def test_removes_accents(self):
        assert normalize_accents("carré") == "carre"
        assert normalize_accents("élève") == "eleve"

    def test_empty_string(self):
        assert normalize_accents("") == ""

    def test_no_accents(self):
        assert normalize_accents("hello") == "hello"


class TestNormalizeShapeAnswer:
    def test_synonym_square(self):
        assert normalize_shape_answer("square bleu") == "carre bleu"

    def test_accented_shape(self):
        assert normalize_shape_answer("carré rouge") == "carre rouge"

    def test_color_first(self):
        assert normalize_shape_answer("bleu carré") == "carre bleu"

    def test_extended_polygon_color_first(self):
        assert normalize_shape_answer("bleu heptagone") == "heptagone bleu"
        assert normalize_shape_answer("jaune octogone") == "octogone jaune"
        assert normalize_shape_answer("violet nonagone") == "nonagone violet"

    def test_empty(self):
        assert normalize_shape_answer("") == ""


class TestParseAnswerToList:
    def test_python_list(self):
        assert parse_answer_to_list("['Rouge', 'Vert']") == ["rouge", "vert"]

    def test_csv(self):
        assert parse_answer_to_list("O, O, X, O") == ["o", "o", "x", "o"]

    def test_space_separated(self):
        assert parse_answer_to_list("A B C") == ["a", "b", "c"]

    def test_single_value(self):
        assert parse_answer_to_list("42") == ["42"]

    def test_empty(self):
        assert parse_answer_to_list("") == []


class TestParseMultiVisualAnswer:
    def test_position_format(self):
        parts = parse_multi_visual_answer(
            "Position 6: carré bleu, Position 9: triangle vert"
        )
        assert len(parts) == 2
        assert parts[0][0] == 6
        assert parts[1][0] == 9

    def test_compact_format(self):
        parts = parse_multi_visual_answer("6:cercle rouge,9:étoile jaune")
        assert len(parts) == 2
        assert parts[0][0] == 6
        assert parts[1][0] == 9

    def test_empty(self):
        assert parse_multi_visual_answer("") == []


# ── SEQUENCE (default) ────────────────────────────────────────────────────


class TestSequenceDefault:
    def test_simple_equality(self):
        assert compare_sequence_default("42", "42") is True

    def test_case_insensitive(self):
        assert compare_sequence_default("Rouge", "rouge") is True

    def test_list_equality(self):
        assert compare_sequence_default("1, 2, 3", "1, 2, 3") is True

    def test_list_wrong_order(self):
        assert compare_sequence_default("1, 3, 2", "1, 2, 3") is False

    def test_mismatch(self):
        assert compare_sequence_default("42", "43") is False


# ── DEDUCTION ─────────────────────────────────────────────────────────────


class TestDeduction:
    def test_entity_value_format(self):
        user = "Emma:Chimie:700,Lucas:Info:600"
        correct = "Emma:Chimie:700,Lucas:Info:600"
        assert compare_deduction(user, correct) is True

    def test_different_order(self):
        user = "Lucas:Info:600,Emma:Chimie:700"
        correct = "Emma:Chimie:700,Lucas:Info:600"
        assert compare_deduction(user, correct) is True

    def test_ordinal_normalization(self):
        user = "Emma:1er,Lucas:2ème"
        correct = "Emma:1,Lucas:2"
        assert compare_deduction(user, correct) is True

    def test_wrong_answer(self):
        user = "Emma:Chimie:700,Lucas:Info:500"
        correct = "Emma:Chimie:700,Lucas:Info:600"
        assert compare_deduction(user, correct) is False


# ── PROBABILITY ───────────────────────────────────────────────────────────


class TestProbability:
    def test_fraction(self):
        assert compare_probability("3/5", "6/10") is True

    def test_percentage(self):
        assert compare_probability("60%", "3/5") is True

    def test_decimal(self):
        assert compare_probability("0.6", "3/5") is True

    def test_exact_string_match_fallback(self):
        assert compare_probability("abc", "abc") is True

    def test_wrong_fraction(self):
        assert compare_probability("2/5", "3/5") is False


# ── CHESS ─────────────────────────────────────────────────────────────────


class TestChess:
    def test_french_notation(self):
        assert compare_chess("Dg8+ Txg8 Cf7#", "Dg8+Txg8Cf7#") is True

    def test_english_to_french(self):
        assert compare_chess("Qg8+ Rxg8 Nf7#", "Dg8+Txg8Cf7#") is True

    def test_multi_solution_pipe(self):
        assert compare_chess("Dg8+", "Dg8+ | Cf7#") is True

    def test_wrong_move(self):
        assert compare_chess("De5", "Dg8+") is False


# ── GRAPH ─────────────────────────────────────────────────────────────────


class TestGraph:
    def test_node_set_any_order(self):
        assert compare_graph("A, B, C", "C, B, A") is True

    def test_node_set_wrong(self):
        assert compare_graph("A, B", "A, B, C") is False

    def test_single_path_ordered(self):
        assert compare_graph("A-B", "A-B") is True


# ── VISUAL / PATTERN ─────────────────────────────────────────────────────


class TestVisualPattern:
    def test_single_shape(self):
        assert compare_visual_pattern("cercle rouge", "cercle rouge", "visual") is True

    def test_synonym_tolerance(self):
        assert compare_visual_pattern("square bleu", "carré bleu", "visual") is True

    def test_pattern_multi_csv(self):
        assert compare_visual_pattern("O, O, X, O", "O, O, X, O", "pattern") is True

    def test_pattern_multi_csv_wrong(self):
        assert compare_visual_pattern("O, X, X, O", "O, O, X, O", "pattern") is False

    def test_pattern_prefers_persisted_correct_answer_over_runtime_heuristic(self):
        visual_data = {
            "grid": [
                ["3", "5", "8", "12", "17"],
                ["4", "7", "11", "16", "?"],
                ["6", "10", "15", "?", "?"],
                ["9", "14", "?", "27", "35"],
                ["?", "22", "29", "37", "46"],
            ]
        }
        assert (
            compare_visual_pattern(
                "22, 21, 28, 20, 16",
                "22, 21, 28, 20, 16",
                "pattern",
                visual_data,
            )
            is True
        )

    # ── check_answer (dispatch) ──────────────────────────────────────────────

    def test_visual_ordered_csv_requires_all_items_in_order(self):
        correct = "heptagone bleu, hexagone jaune, carré orange"

        assert (
            compare_visual_pattern(
                "heptagone bleu, hexagone jaune, carre orange",
                correct,
                "visual",
            )
            is True
        )
        assert compare_visual_pattern("heptagone bleu", correct, "visual") is False
        assert (
            compare_visual_pattern(
                "hexagone jaune, heptagone bleu, carre orange",
                correct,
                "visual",
            )
            is False
        )

    def test_visual_ordered_csv_accepts_color_first_and_semicolon_separator(self):
        correct = "heptagone bleu, hexagone jaune, carré orange"

        assert (
            compare_visual_pattern(
                "bleu heptagone; jaune hexagone; orange carre",
                correct,
                "visual",
            )
            is True
        )


class TestCheckAnswer:
    def test_dispatches_deduction(self):
        assert check_answer("DEDUCTION", "A:B:C", "A:B:C") is True

    def test_dispatches_probability(self):
        assert check_answer("PROBABILITY", "3/5", "6/10") is True

    def test_dispatches_chess(self):
        assert check_answer("CHESS", "Dg8+", "Dg8+") is True

    def test_dispatches_graph(self):
        assert check_answer("GRAPH", "A, B, C", "C, B, A") is True

    def test_dispatches_visual(self):
        assert check_answer("VISUAL", "cercle rouge", "cercle rouge") is True

    def test_dispatches_pattern(self):
        assert check_answer("PATTERN", "O, O, X", "O, O, X") is True

    def test_dispatches_sequence_default(self):
        assert check_answer("SEQUENCE", "42", "42") is True
        assert check_answer("", "42", "42") is True
