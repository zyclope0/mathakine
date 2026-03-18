"""
Tests unitaires pour le flux de création exercice admin (Lot G3).
"""

from app.services.admin.admin_exercise_create_flow import (
    persist_exercise_create,
    prepare_exercise_create_data,
    validate_exercise_create_pre_persist,
)


class TestPrepareExerciseCreateData:
    """Étape 1 : préparation / normalisation."""

    def test_normalizes_title(self):
        prepared = prepare_exercise_create_data(
            {"title": "  Trimmed  ", "question": "Q", "correct_answer": "A"}
        )
        assert prepared["title"] == "Trimmed"

    def test_normalizes_exercise_type_uppercase(self):
        prepared = prepare_exercise_create_data(
            {
                "title": "T",
                "question": "Q",
                "correct_answer": "A",
                "exercise_type": "addition",
            }
        )
        assert prepared["exercise_type"] == "ADDITION"

    def test_defaults_exercise_type(self):
        prepared = prepare_exercise_create_data(
            {"title": "T", "question": "Q", "correct_answer": "A"}
        )
        assert prepared["exercise_type"] == "DIVERS"
        assert prepared["difficulty"] == "PADAWAN"
        assert prepared["age_group"] == "9-11"

    def test_extracts_choices_explanation_hint(self):
        prepared = prepare_exercise_create_data(
            {
                "title": "T",
                "question": "Q",
                "correct_answer": "A",
                "choices": [1, 2, 3],
                "explanation": "Ex",
                "hint": "H",
            }
        )
        assert prepared["choices"] == [1, 2, 3]
        assert prepared["explanation"] == "Ex"
        assert prepared["hint"] == "H"


class TestValidateExerciseCreatePrePersist:
    """Étape 2 : validation métier."""

    def test_rejects_empty_title(self, db_session):
        prepared = {"title": "", "question": "Q", "correct_answer": "A"}
        err, status = validate_exercise_create_pre_persist(prepared, db_session)
        assert err == "Le titre est obligatoire."
        assert status == 400

    def test_rejects_empty_question(self, db_session):
        prepared = {"title": "T", "question": "", "correct_answer": "A"}
        err, status = validate_exercise_create_pre_persist(prepared, db_session)
        assert err == "La question est obligatoire."
        assert status == 400

    def test_rejects_empty_correct_answer(self, db_session):
        prepared = {"title": "T", "question": "Q", "correct_answer": ""}
        err, status = validate_exercise_create_pre_persist(prepared, db_session)
        assert err == "La réponse correcte est obligatoire."
        assert status == 400

    def test_accepts_valid_prepared(self, db_session):
        prepared = {
            "title": "Valid",
            "question": "Q?",
            "correct_answer": "A",
            "exercise_type": "ADDITION",
            "difficulty": "PADAWAN",
            "age_group": "9-11",
        }
        err, status = validate_exercise_create_pre_persist(prepared, db_session)
        assert err is None
        assert status == 0


class TestPersistExerciseCreate:
    """Étape 3 : mutation / persistance."""

    def test_creates_exercise(self, db_session):
        prepared = {
            "title": "Persist Test G3",
            "question": "1+1?",
            "correct_answer": "2",
            "exercise_type": "ADDITION",
            "difficulty": "PADAWAN",
            "age_group": "9-11",
            "explanation": "Simple addition",
        }
        ex = persist_exercise_create(db_session, prepared, admin_user_id=None)
        assert ex.id is not None
        assert ex.title == "Persist Test G3"
        assert ex.question == "1+1?"
        assert ex.correct_answer == "2"
        assert ex.exercise_type == "ADDITION"
        assert ex.ai_generated is False
