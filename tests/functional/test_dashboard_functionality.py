"""
Tests fonctionnels pour le tableau de bord après correction critique (Mai 2025)
"""
import pytest
from starlette.testclient import TestClient
from enhanced_server import app
from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.services.auth_service import get_user_by_username, create_user
from app.schemas.user import UserCreate
from app.utils.db_helpers import get_enum_value
from app.core.security import create_access_token
from datetime import datetime, timezone, timedelta
import json
import uuid

@pytest.fixture
def test_client():
    """Client de test pour l'application Starlette"""
    return TestClient(app)

@pytest.fixture
def authenticated_user_with_data(test_client):
    """
    Crée un utilisateur authentifié avec des données de test pour le tableau de bord
    """
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Créer un utilisateur unique pour ce test
        unique_id = str(uuid.uuid4())[:8]
        username = f"dashboard_test_{unique_id}"
        email = f"dashboard_test_{unique_id}@example.com"
        
        user_data = UserCreate(
            username=username,
            email=email,
            password="TestPassword123",
            full_name="Dashboard Test User",
            role="padawan"
        )
        
        # Créer l'utilisateur
        user = create_user(db, user_data)
        
        # Créer des exercices de test
        exercises = []
        exercise_types = [
            (ExerciseType.ADDITION, "Addition simple"),
            (ExerciseType.SOUSTRACTION, "Soustraction simple"),
            (ExerciseType.MULTIPLICATION, "Multiplication simple"),
            (ExerciseType.DIVISION, "Division simple")
        ]
        
        for ex_type, title in exercise_types:
            exercise = Exercise(
                title=f"{title} - Test {unique_id}",
                exercise_type=get_enum_value(ExerciseType, ex_type.value, db),
                difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db),
                question=f"Question de test pour {title}",
                correct_answer="42",
                choices=json.dumps(["40", "41", "42", "43"]),
                explanation="Explication de test",
                hint="Indice de test",
                is_active=True,
                is_archived=False,
                creator_id=user.id
            )
            db.add(exercise)
            db.flush()
            exercises.append(exercise)
        
        # Créer des tentatives de test
        base_time = datetime.now(timezone.utc) - timedelta(days=3)
        attempts = []
        
        for i, exercise in enumerate(exercises):
            # Créer 3-5 tentatives par exercice
            for j in range(3 + i):  # 3, 4, 5, 6 tentatives
                is_correct = j < 2 or (j == 2 and i % 2 == 0)  # ~70% de réussite
                attempt = Attempt(
                    user_id=user.id,
                    exercise_id=exercise.id,
                    user_answer="42" if is_correct else "wrong",
                    is_correct=is_correct,
                    time_spent=60.0 + (j * 10),
                    attempt_number=j + 1,
                    hints_used=j % 3,
                    device_info="Test Device",
                    created_at=base_time + timedelta(hours=i*6 + j)
                )
                db.add(attempt)
                attempts.append(attempt)
        
        db.commit()
        
        # Créer un token d'authentification
        access_token = create_access_token(data={"sub": user.username})
        
        # Configurer les cookies d'authentification
        test_client.cookies.set("access_token", access_token)
        
        yield {
            "user": user,
            "exercises": exercises,
            "attempts": attempts,
            "client": test_client,
            "token": access_token
        }
        
    finally:
        # Nettoyage
        try:
            # Supprimer les tentatives
            db.query(Attempt).filter(Attempt.user_id == user.id).delete()
            # Supprimer les exercices
            for exercise in exercises:
                db.query(Exercise).filter(Exercise.id == exercise.id).delete()
            # Supprimer l'utilisateur
            db.query(User).filter(User.id == user.id).delete()
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()

def test_dashboard_page_loads(authenticated_user_with_data):
    """Test que la page du tableau de bord se charge correctement"""
    client = authenticated_user_with_data["client"]
    user = authenticated_user_with_data["user"]
    
    response = client.get("/dashboard")
    
    assert response.status_code == 200
    assert "Tableau de Bord" in response.text
    assert "Mathakine" in response.text

def test_dashboard_api_returns_user_stats(authenticated_user_with_data):
    """Test que l'API du tableau de bord retourne les bonnes statistiques utilisateur"""
    client = authenticated_user_with_data["client"]
    user = authenticated_user_with_data["user"]
    attempts = authenticated_user_with_data["attempts"]
    
    response = client.get("/api/users/stats")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Vérifier la structure de base
    assert "total_exercises" in data
    assert "correct_answers" in data
    assert "success_rate" in data
    assert "experience_points" in data
    assert "performance_by_type" in data
    assert "level" in data
    
    # Vérifier les valeurs
    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.is_correct)
    expected_success_rate = round((correct_attempts / total_attempts) * 100)
    
    assert data["total_exercises"] == total_attempts
    assert data["correct_answers"] == correct_attempts
    assert data["success_rate"] == expected_success_rate
    assert data["experience_points"] == total_attempts * 10
    
    # Vérifier les performances par type
    performance = data["performance_by_type"]
    assert isinstance(performance, dict)
    
    # Vérifier que les types d'exercices sont présents
    expected_types = ["addition", "soustraction", "multiplication", "division"]
    for ex_type in expected_types:
        if ex_type in performance:
            type_data = performance[ex_type]
            assert "completed" in type_data
            assert "correct" in type_data
            assert "success_rate" in type_data
            assert isinstance(type_data["completed"], int)
            assert isinstance(type_data["correct"], int)
            assert isinstance(type_data["success_rate"], (int, float))

def test_dashboard_api_requires_authentication(test_client):
    """Test que l'API du tableau de bord nécessite une authentification"""
    # Tester sans token
    response = test_client.get("/api/users/stats")
    
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert "Authentification requise" in data["error"]

def test_dashboard_api_with_no_data(test_client):
    """Test que l'API du tableau de bord gère correctement un utilisateur sans données"""
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Créer un utilisateur sans exercices ni tentatives
        unique_id = str(uuid.uuid4())[:8]
        username = f"empty_user_{unique_id}"
        email = f"empty_user_{unique_id}@example.com"
        
        user_data = UserCreate(
            username=username,
            email=email,
            password="TestPassword123",
            full_name="Empty Test User",
            role="padawan"
        )
        
        user = create_user(db, user_data)
        db.commit()
        
        # Créer un token et configurer l'authentification
        access_token = create_access_token(data={"sub": user.username})
        test_client.cookies.set("access_token", access_token)
        
        response = test_client.get("/api/users/stats")
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Vérifier que les valeurs par défaut sont retournées
        assert data["total_exercises"] == 0
        assert data["correct_answers"] == 0
        assert data["success_rate"] == 0
        assert data["experience_points"] == 0
        assert isinstance(data["performance_by_type"], dict)
        
    finally:
        # Nettoyage
        try:
            db.query(User).filter(User.id == user.id).delete()
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()

def test_dashboard_redirects_unauthenticated_users(test_client):
    """Test que la page du tableau de bord redirige les utilisateurs non authentifiés"""
    response = test_client.get("/dashboard", follow_redirects=False)
    
    assert response.status_code == 302
    assert response.headers["location"] == "/login"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 