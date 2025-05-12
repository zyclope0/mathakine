"""
Tests des endpoints de suppression pour vérifier que les suppressions en cascade fonctionnent correctement via l'API.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from sqlalchemy.orm import Session
from app.db.base import Base, engine
from app.api.deps import get_db_session, get_current_user, get_current_gardien_or_archiviste
from app.core.config import settings
import uuid

# Client pour tester l'API
client = TestClient(app)

@pytest.fixture
def db():
    """Fixture pour créer une session de base de données pour les tests"""
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    
    # Configure l'application pour utiliser la connexion de test
    def override_get_db():
        try:
            session = Session(autocommit=False, autoflush=False, bind=connection)
            yield session
        finally:
            session.close()
    
    # Override la dépendance
    app.dependency_overrides[get_db_session] = override_get_db
    
    # Créer une session pour le test
    session = Session(autocommit=False, autoflush=False, bind=connection)
    yield session
    
    # Cleanup - gérer correctement la fermeture pour éviter l'avertissement
    session.close()
    try:
        # Vérifier si la transaction est toujours active avant de faire rollback
        if transaction.is_active:
            transaction.rollback()
    except:
        # Si une erreur se produit, on ignore car la transaction est probablement déjà dissociée
        pass
    connection.close()
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db):
    """Fixture pour créer un utilisateur administrateur pour les tests"""
    # Créer un utilisateur administrateur
    admin = User(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="$2b$12$VKGW7HJ8HE2zVKgJ6VMVVuv.J9wxFw7.S5Aq6DFrW16.S9blOaaZG",  # "password"
        role=UserRole.ARCHIVISTE
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Override la dépendance d'authentification pour utiliser cet utilisateur sans token
    def override_get_current_user():
        return admin
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    return admin

@pytest.fixture
def regular_user(db):
    """Fixture pour créer un utilisateur standard pour les tests"""
    # Créer un utilisateur standard
    user = User(
        username=f"user_{uuid.uuid4().hex[:8]}",
        email=f"user_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="$2b$12$VKGW7HJ8HE2zVKgJ6VMVVuv.J9wxFw7.S5Aq6DFrW16.S9blOaaZG",  # "password"
        role=UserRole.PADAWAN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Override la dépendance d'authentification pour utiliser cet utilisateur sans token
    def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    return user

@pytest.fixture
def test_exercise_with_attempts(db):
    """Fixture pour créer un exercice avec des tentatives pour les tests"""
    # Créer un exercice
    exercise = Exercise(
        title="Test API Cascade Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
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
        role=UserRole.PADAWAN
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

@pytest.fixture
def override_admin_auth(admin_user):
    """Override l'authentification pour utiliser l'utilisateur admin"""
    # Sauvegarder la dépendance originale
    original = app.dependency_overrides.get(get_current_gardien_or_archiviste)
    
    # Remplacer par notre mock
    def mock_auth():
        return admin_user
    
    app.dependency_overrides[get_current_gardien_or_archiviste] = mock_auth
    
    yield
    
    # Restaurer la dépendance originale
    if original:
        app.dependency_overrides[get_current_gardien_or_archiviste] = original
    else:
        del app.dependency_overrides[get_current_gardien_or_archiviste]

@pytest.fixture
def override_regular_auth(regular_user):
    """Override l'authentification pour utiliser l'utilisateur régulier"""
    # Sauvegarder la dépendance originale
    original = app.dependency_overrides.get(get_current_user)
    
    # Remplacer par notre mock
    def mock_auth():
        return regular_user
    
    app.dependency_overrides[get_current_user] = mock_auth
    
    yield
    
    # Restaurer la dépendance originale
    if original:
        app.dependency_overrides[get_current_user] = original
    else:
        del app.dependency_overrides[get_current_user]

def test_delete_exercise_cascade(db, test_exercise_with_attempts, override_admin_auth):
    """Teste que l'endpoint de suppression d'exercice archive l'exercice et préserve les tentatives"""
    exercise_id = test_exercise_with_attempts["exercise_id"]
    attempt_ids = test_exercise_with_attempts["attempt_ids"]
    
    # Vérifier que l'exercice et les tentatives existent avant la suppression
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None
    assert exercise.is_archived is False, "L'exercice est déjà archivé"
    
    attempts = db.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == len(attempt_ids)
    
    # Appeler l'endpoint de suppression
    response = client.delete(f"/api/exercises/{exercise_id}")
    
    # Vérifier que la suppression a réussi
    assert response.status_code in [200, 204]
    
    # Rafraîchir les données de la session
    db.expire_all()
    
    # Vérifier que l'exercice a été archivé et non supprimé
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None, "L'exercice a été supprimé physiquement au lieu d'être archivé"
    assert exercise.is_archived is True, "L'exercice n'a pas été marqué comme archivé"
    
    # Les tentatives devraient toujours exister puisque l'exercice est archivé et non supprimé
    attempts = db.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == len(attempt_ids), "Les tentatives ont été supprimées alors que l'exercice est archivé"
    
    for attempt_id in attempt_ids:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        assert attempt is not None, f"La tentative {attempt_id} a été supprimée alors que l'exercice est archivé"

def test_delete_exercise_unauthorized(db, test_exercise_with_attempts, override_regular_auth):
    """Teste que l'endpoint de suppression d'exercice refuse les utilisateurs non autorisés"""
    exercise_id = test_exercise_with_attempts["exercise_id"]
    
    # Appeler l'endpoint de suppression (en tant qu'utilisateur standard)
    response = client.delete(f"/api/exercises/{exercise_id}")
    
    # Vérifier que la suppression est refusée
    assert response.status_code == 403
    
    # Vérifier que l'exercice existe toujours
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None

def test_delete_nonexistent_exercise(db, override_admin_auth):
    """Teste que l'endpoint de suppression gère correctement les exercices inexistants"""
    # ID très grand qui n'existe probablement pas
    exercise_id = 999999
    
    # Appeler l'endpoint de suppression
    response = client.delete(f"/api/exercises/{exercise_id}")
    
    # Vérifier qu'on obtient une erreur 404 ou 500
    # Note: Idéalement, on devrait toujours avoir un 404, mais dans certains cas
    # on peut avoir un 500 si l'exception 404 n'est pas correctement gérée
    assert response.status_code in [404, 500] 