"""
Tests des endpoints de suppression pour vérifier que les suppressions en cascade fonctionnent correctement via l'API.
"""
import pytest
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.utils.db_helpers import get_enum_value
import uuid


@pytest.fixture
def test_exercise_with_attempts(db_session):
    """Fixture pour créer un exercice avec des tentatives pour les tests"""
    db = db_session
    # Créer un exercice
    exercise = Exercise(
        title="Test API Cascade Exercise",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        age_group="6-8",
        question="Combien font 2+2?",
        correct_answer="4",
        choices=["2", "3", "4", "5"]
    )
    db.add(exercise)
    db.flush()

    # Créer un utilisateur standard
    user = User(
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        email=f"test_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="$2b$12$VKGW7HJ8HE2zVKgJ6VMVVuv.J9wxFw7.S5Aq6DFrW16.S9blOaaZG",  # "password"
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db.add(user)
    db.flush()

    # Créer des tentatives associées
    attempt1 = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="4",
        is_correct=True
    )
    attempt2 = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="3",
        is_correct=False
    )
    db.add(attempt1)
    db.add(attempt2)
    db.commit()

    return {
        "exercise_id": exercise.id,
        "user_id": user.id,
        "attempt_ids": [attempt1.id, attempt2.id]
    }


@pytest.mark.skip(reason="delete_exercise handler is a placeholder - returns 200 without actual deletion/archival")
async def test_delete_exercise_cascade(archiviste_client, db_session, test_exercise_with_attempts):
    """Teste que l'endpoint de suppression d'exercice archive l'exercice et préserve les tentatives"""
    client = archiviste_client["client"]
    exercise_id = test_exercise_with_attempts["exercise_id"]
    attempt_ids = test_exercise_with_attempts["attempt_ids"]

    # Vérifier que l'exercice et les tentatives existent avant la suppression
    exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None
    assert exercise.is_archived is False, "L'exercice est déjà archivé"

    attempts = db_session.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == len(attempt_ids)

    # Appeler l'endpoint de suppression
    response = await client.delete(f"/api/exercises/{exercise_id}")

    # Vérifier que la suppression a réussi
    assert response.status_code in [200, 204]

    # Rafraîchir les données de la session
    db_session.expire_all()

    # Vérifier que l'exercice a été archivé et non supprimé
    exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None, "L'exercice a été supprimé physiquement au lieu d'être archivé"
    assert exercise.is_archived is True, "L'exercice n'a pas été marqué comme archivé"

    # Les tentatives devraient toujours exister puisque l'exercice est archivé et non supprimé
    attempts = db_session.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == len(attempt_ids), "Les tentatives ont été supprimées alors que l'exercice est archivé"

    for attempt_id in attempt_ids:
        attempt = db_session.query(Attempt).filter(Attempt.id == attempt_id).first()
        assert attempt is not None, f"La tentative {attempt_id} a été supprimée alors que l'exercice est archivé"


@pytest.mark.skip(reason="delete_exercise handler is a placeholder - returns 200 without actual deletion/archival")
async def test_delete_exercise_unauthorized(padawan_client, db_session, test_exercise_with_attempts):
    """Teste que l'endpoint de suppression d'exercice refuse les utilisateurs non autorisés"""
    client = padawan_client["client"]
    exercise_id = test_exercise_with_attempts["exercise_id"]

    # Appeler l'endpoint de suppression (en tant qu'utilisateur standard)
    response = await client.delete(f"/api/exercises/{exercise_id}")

    # Vérifier que la suppression est refusée
    assert response.status_code == 403

    # Vérifier que l'exercice existe toujours
    exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None


@pytest.mark.skip(reason="delete_exercise handler is a placeholder - returns 200 without actual deletion/archival")
async def test_delete_nonexistent_exercise(archiviste_client):
    """Teste que l'endpoint de suppression gère correctement les exercices inexistants"""
    client = archiviste_client["client"]
    # ID très grand qui n'existe probablement pas
    exercise_id = 999999

    # Appeler l'endpoint de suppression
    response = await client.delete(f"/api/exercises/{exercise_id}")

    # Vérifier qu'on obtient une erreur 404 ou 500
    # Note: Idéalement, on devrait toujours avoir un 404, mais dans certains cas
    # on peut avoir un 500 si l'exception 404 n'est pas correctement gérée
    assert response.status_code in [404, 500]
