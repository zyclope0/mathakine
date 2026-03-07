"""Tests pour app.utils.latex_utils — correction bug LaTeX fractions collées."""

import pytest

from app.utils.latex_utils import sanitize_exercise_text_fields, sanitize_latex_fractions


class TestSanitizeLatexFractions:
    def test_fraction_followed_by_digits_adds_space(self):
        """\\frac{1}{8}81 → \\frac{1}{8} 81"""
        assert (
            sanitize_latex_fractions(r"on a prélevé $\frac{1}{8}81$ du total")
            == r"on a prélevé $\frac{1}{8} 81$ du total"
        )

    def test_fraction_27_followed_by_72(self):
        assert (
            sanitize_latex_fractions(r"soutiré $\frac{2}{7}72$")
            == r"soutiré $\frac{2}{7} 72$"
        )

    def test_fraction_15_followed_by_51(self):
        assert (
            sanitize_latex_fractions(r"retiré $\frac{1}{5}51$")
            == r"retiré $\frac{1}{5} 51$"
        )

    def test_fraction_with_space_unchanged(self):
        """Déjà correct : pas de modification"""
        text = r"$\frac{1}{8}$ du total"
        assert sanitize_latex_fractions(text) == text

    def test_empty_string(self):
        assert sanitize_latex_fractions("") == ""

    def test_none_returns_none(self):
        assert sanitize_latex_fractions(None) is None


class TestSanitizeExerciseTextFields:
    def test_all_fields_sanitized(self):
        q, expl, hint = sanitize_exercise_text_fields(
            r"$\frac{1}{8}81$ kg",
            r"Étape 1: $\frac{2}{7}72$",
            r"Pense à $\frac{1}{5}51$",
        )
        assert q == r"$\frac{1}{8} 81$ kg"
        assert expl == r"Étape 1: $\frac{2}{7} 72$"
        assert hint == r"Pense à $\frac{1}{5} 51$"
