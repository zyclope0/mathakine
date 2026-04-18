"""Validation post-generation flux exercices IA (metier, sans LLM)."""

import pytest

from app.services.exercises.exercise_ai_validation import (
    _parse_float_strict,
    _try_verify_arithmetic,
    format_validation_error_message,
    validate_exercise_ai_output,
)


def _valid_base(**overrides):
    base = dict(
        exercise_type="addition",
        title="Somme simple",
        question="Calcule $1+1$ pour un enfant.",
        correct_answer="2",
        choices=["2", "3", "4", "5"],
        explanation="On additionne les deux termes : $1+1=2$. La reponse est donc 2.",
        hint="Pense a loperation qui assemble deux quantites.",
    )
    base.update(overrides)
    return base


def test_validate_ok_addition_minimal() -> None:
    ok, reasons = validate_exercise_ai_output(**_valid_base())
    assert ok is True
    assert reasons == []


def test_validate_rejects_correct_answer_not_in_choices() -> None:
    ok, reasons = validate_exercise_ai_output(
        **_valid_base(correct_answer="99", choices=["1", "2", "3", "4"])
    )
    assert ok is False
    assert "correct_answer_absente_des_choix" in reasons


def test_validate_numeric_equivalence_7_vs_7_0() -> None:
    ok, reasons = validate_exercise_ai_output(
        **_valid_base(correct_answer="7", choices=["7.0", "8", "9", "10"])
    )
    assert ok is True
    assert reasons == []


def test_validate_rejects_duplicate_numeric_choices() -> None:
    ok, reasons = validate_exercise_ai_output(
        **_valid_base(choices=["5", "5.0", "6", "7"])
    )
    assert ok is False
    assert "choices_non_distincts" in reasons


def test_validate_rejects_wrong_choice_count() -> None:
    ok, reasons = validate_exercise_ai_output(**_valid_base(choices=["1", "2", "3"]))
    assert ok is False
    assert "choices_doit_contenir_4_elements" in reasons


def test_validate_rejects_non_numeric_for_addition() -> None:
    ok, reasons = validate_exercise_ai_output(
        **_valid_base(correct_answer="deux", choices=["deux", "un", "trois", "quatre"])
    )
    assert ok is False
    assert "correct_answer_non_numerique_attendu" in reasons


def test_validate_fractions_allows_non_numeric_strings() -> None:
    ok, reasons = validate_exercise_ai_output(
        **_valid_base(
            exercise_type="fractions",
            question="Simplifie une fraction pour un eleve.",
            correct_answer="3/4",
            choices=["3/4", "1/2", "2/3", "5/6"],
            explanation="On simplifie le numerateur et le denominateur par leur pgcd, "
            "etape par etape, jusqu a obtenir une fraction irreductible claire.",
            hint="Cherche un diviseur commun au numerateur et au denominateur.",
        )
    )
    assert ok is True


def test_format_validation_error_message_fallback() -> None:
    msg = format_validation_error_message(["title_trop_court"])
    assert "respecte" in msg.lower() or "réessayez" in msg.lower()


# ---------------------------------------------------------------------------
# GAP-4 — _parse_float_strict
# ---------------------------------------------------------------------------


class TestParseFloatStrict:
    """Vérifie que le parser de nombres est bien borné."""

    def test_integer(self) -> None:
        assert _parse_float_strict("42") == pytest.approx(42.0)

    def test_decimal_dot(self) -> None:
        assert _parse_float_strict("3.5") == pytest.approx(3.5)

    def test_decimal_comma(self) -> None:
        assert _parse_float_strict("3,5") == pytest.approx(3.5)

    def test_thousands_space(self) -> None:
        assert _parse_float_strict("1 234") == pytest.approx(1234.0)

    def test_thousands_space_with_decimal(self) -> None:
        assert _parse_float_strict("1 234,5") == pytest.approx(1234.5)

    def test_rejects_letters(self) -> None:
        assert _parse_float_strict("12a") is None

    def test_rejects_empty(self) -> None:
        assert _parse_float_strict("") is None

    def test_rejects_text(self) -> None:
        assert _parse_float_strict("deux") is None

    def test_rejects_fraction_string(self) -> None:
        # "3/4" n'est pas un float strict — pas dans les types numériques purs
        assert _parse_float_strict("3/4") is None


# ---------------------------------------------------------------------------
# GAP-4 — _try_verify_arithmetic (unité sur la fonction de vérification)
# ---------------------------------------------------------------------------


class TestTryVerifyArithmetic:
    """Tests de la vérification arithmétique conservative — fail-open si ambigu."""

    # --- Cas PASS : expression trouvée et correcte → None ---

    def test_multiplication_correct(self) -> None:
        assert _try_verify_arithmetic("Calcule 12 × 14", "168") is None

    def test_addition_correct(self) -> None:
        assert _try_verify_arithmetic("3 + 4", "7") is None

    def test_subtraction_correct(self) -> None:
        assert _try_verify_arithmetic("100 − 37", "63") is None

    def test_division_correct(self) -> None:
        assert _try_verify_arithmetic("45 / 9", "5") is None

    def test_decimal_comma_correct(self) -> None:
        assert _try_verify_arithmetic("3,5 + 1,5", "5") is None

    def test_thousands_separator_correct(self) -> None:
        assert _try_verify_arithmetic("1 234 + 5 678", "6912") is None

    # --- Cas FAIL : expression trouvée et incorrecte → message non-None ---

    def test_multiplication_wrong(self) -> None:
        assert _try_verify_arithmetic("Calcule 12 × 14", "196") is not None

    def test_subtraction_wrong(self) -> None:
        # BUG CORRIGÉ : 100−37=63, donc "53" est faux
        assert _try_verify_arithmetic("100 − 37", "53") is not None

    def test_addition_wrong(self) -> None:
        assert _try_verify_arithmetic("5 + 3", "9") is not None

    # --- Cas SKIP fail-open : 0 match ou ambiguïté → None ---

    def test_narrative_no_operator(self) -> None:
        # Pas de symbole opérateur → 0 match
        assert _try_verify_arithmetic("Pierre a 45 billes et en perd 12", "33") is None

    def test_multiple_expressions_ambiguous(self) -> None:
        # 2 expressions dans la phrase → ambiguïté → skip
        assert _try_verify_arithmetic("Il a 3 + 4 et donne 2 + 1", "5") is None

    def test_multi_step_expression_no_match(self) -> None:
        # "(3+4)×2" → le regex ne matche pas les parenthèses → 0 match
        assert _try_verify_arithmetic("(3+4)×2", "14") is None

    def test_division_by_zero_skip(self) -> None:
        assert _try_verify_arithmetic("10 / 0", "0") is None

    def test_empty_question_skip(self) -> None:
        assert _try_verify_arithmetic("", "5") is None

    def test_non_parseable_answer_skip(self) -> None:
        assert _try_verify_arithmetic("3 + 4", "sept") is None

    # --- Cas LaTeX : opérateurs \times / \div + délimiteurs $ → chemin nominal générateur ---

    def test_latex_times_correct(self) -> None:
        # Calcule $3 \times 4$ → 12 : chemin nominal du générateur IA
        assert _try_verify_arithmetic(r"Calcule $3 \times 4$", "12") is None

    def test_latex_times_wrong(self) -> None:
        assert _try_verify_arithmetic(r"Calcule $3 \times 4$", "11") is not None

    def test_latex_div_correct(self) -> None:
        assert _try_verify_arithmetic(r"Calcule $12 \div 3$", "4") is None

    def test_latex_div_wrong(self) -> None:
        assert _try_verify_arithmetic(r"Calcule $12 \div 3$", "5") is not None

    def test_latex_times_large_correct(self) -> None:
        assert _try_verify_arithmetic(r"Calcule $12 \times 14$", "168") is None

    def test_latex_times_large_wrong(self) -> None:
        assert _try_verify_arithmetic(r"Calcule $12 \times 14$", "196") is not None


# ---------------------------------------------------------------------------
# GAP-4 — intégration dans validate_exercise_ai_output
# ---------------------------------------------------------------------------


class TestValidateExerciseArithmeticIntegration:
    """Vérifie que le check arithmétique est correctement câblé dans la validation globale."""

    def test_rejects_wrong_arithmetic(self) -> None:
        ok, reasons = validate_exercise_ai_output(
            **_valid_base(
                question="Calcule 12 × 14",
                correct_answer="196",
                choices=["168", "196", "170", "200"],
            )
        )
        assert ok is False
        assert "correct_answer_arithmetiquement_fausse" in reasons

    def test_accepts_correct_arithmetic(self) -> None:
        ok, reasons = validate_exercise_ai_output(
            **_valid_base(
                question="Calcule 12 × 14",
                correct_answer="168",
                choices=["168", "196", "170", "200"],
            )
        )
        assert ok is True
        assert reasons == []

    def test_skips_arithmetic_check_for_narrative_question(self) -> None:
        # Problème texte sans opérateur explicite → pas de vérification arithmétique
        ok, reasons = validate_exercise_ai_output(
            **_valid_base(
                exercise_type="addition",
                question="Marie a 12 bonbons et en reçoit encore 7. Combien en a-t-elle ?",
                correct_answer="19",
                choices=["19", "17", "21", "20"],
            )
        )
        assert ok is True
        assert "correct_answer_arithmetiquement_fausse" not in reasons

    def test_skips_arithmetic_check_for_fractions_type(self) -> None:
        # Le type fractions n'est pas dans _NUMERIC_EXERCISE_TYPES
        ok, reasons = validate_exercise_ai_output(
            **_valid_base(
                exercise_type="fractions",
                question="Simplifie 6/8.",
                correct_answer="3/4",
                choices=["3/4", "1/2", "2/3", "5/6"],
                hint="Cherche un diviseur commun.",
                explanation="On simplifie le numerateur et le denominateur par leur pgcd etape par etape.",
            )
        )
        assert "correct_answer_arithmetiquement_fausse" not in reasons

    def test_format_message_arithmetic_error(self) -> None:
        msg = format_validation_error_message(["correct_answer_arithmetiquement_fausse"])
        assert "exactitude" in msg.lower() or "calcul" in msg.lower()
