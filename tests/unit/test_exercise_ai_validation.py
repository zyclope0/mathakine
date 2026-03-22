"""Validation post-generation flux exercices IA (metier, sans LLM)."""

from app.services.exercises.exercise_ai_validation import (
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
