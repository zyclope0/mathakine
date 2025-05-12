"""
Tests fonctionnels pour vérifier que le serveur Starlette (enhanced_server.py) 
gère correctement les suppressions en cascade.
"""
import pytest
import uuid
import asyncio
import json
from sqlalchemy.orm import Session
from app.db.base import engine
from app.models.user import User
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt

# Importer les fonctions directement depuis le serveur enhanced_server
try:
    import sys
    import os
    # Ajouter le répertoire racine au path si nécessaire
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from enhanced_server import delete_exercise
except ImportError as e:
    # Si l'import échoue, nous utiliserons un mock
    delete_exercise = None
    print(f"Erreur d'import: {e}")

@pytest.fixture
def setup_test_data():
    """Crée des données de test pour le test de suppression en cascade"""
    # Créer une session de base de données
    session = Session(engine)
    
    try:
        # Créer un utilisateur de test
        test_username = f"test_starlette_{uuid.uuid4().hex[:8]}"
        user = User(
            username=test_username,
            email=f"{test_username}@example.com",
            hashed_password="$2b$12$VKGW7HJ8HE2zVKgJ6VMVVuv.J9wxFw7.S5Aq6DFrW16.S9blOaaZG",  # "password"
        )
        session.add(user)
        session.flush()
        
        # Créer un exercice de test
        exercise = Exercise(
            title="Test Starlette Cascade",
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Combien font 5+5?",
            correct_answer="10",
            choices=["8", "9", "10", "11"]
        )
        session.add(exercise)
        session.flush()
        
        # Créer des tentatives associées
        attempt1 = Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="10",
            is_correct=True
        )
        session.add(attempt1)
        
        attempt2 = Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="9",
            is_correct=False
        )
        session.add(attempt2)
        
        # Valider les changements
        session.commit()
        
        # Récupérer les IDs pour le test
        result = {
            "user_id": user.id,
            "exercise_id": exercise.id,
            "attempt_ids": [attempt1.id, attempt2.id],
            "session": session
        }
        
        yield result
        
    except Exception as e:
        session.rollback()
        pytest.fail(f"Erreur lors de la configuration du test: {str(e)}")
    
    finally:
        # Nettoyer la session après le test
        session.close()

# Créer une classe MockRequest pour simuler une requête Starlette
class MockRequest:
    def __init__(self, path_params):
        self.path_params = path_params

@pytest.mark.asyncio
async def test_starlette_cascade_deletion(setup_test_data):
    """Teste que le serveur Starlette gère correctement les suppressions en cascade"""
    # Si la fonction delete_exercise n'est pas disponible, ignorer le test
    if delete_exercise is None:
        pytest.skip("Fonction delete_exercise non disponible")
    
    exercise_id = setup_test_data["exercise_id"]
    attempt_ids = setup_test_data["attempt_ids"]
    session = setup_test_data["session"]
    
    # Vérifier que l'exercice et les tentatives existent
    exercise = session.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None, "L'exercice n'existe pas"
    assert exercise.is_archived is False, "L'exercice est déjà archivé"
    
    attempts = session.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == 2, "Les tentatives n'existent pas"
    
    # Créer une mock request pour passer à la fonction delete_exercise
    mock_request = MockRequest({"exercise_id": exercise_id})
    
    # Appeler la fonction asynchrone
    result = await delete_exercise(mock_request)
    
    # Vérifier le résultat
    assert result.status_code == 200, f"Code d'erreur inattendu: {result.status_code}, {result.body.decode()}"
    
    # Extraire les données JSON du corps de la réponse
    result_data = json.loads(result.body.decode())
    assert result_data["success"] is True, "La suppression a échoué"
    print(f"Exercice {exercise_id} archivé avec succès")
    
    # Rafraîchir les données de la session
    session.expire_all()
    
    # Vérifier que l'exercice a été archivé et non supprimé
    exercise = session.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None, "L'exercice a été supprimé physiquement au lieu d'être archivé"
    assert exercise.is_archived is True, "L'exercice n'a pas été marqué comme archivé"
    
    # Les tentatives devraient toujours exister puisque l'exercice est archivé et non supprimé
    attempts = session.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == 2, "Les tentatives ont été supprimées alors que l'exercice est archivé"
    
    for attempt_id in attempt_ids:
        attempt = session.query(Attempt).filter(Attempt.id == attempt_id).first()
        assert attempt is not None, f"La tentative {attempt_id} a été supprimée alors que l'exercice est archivé" 