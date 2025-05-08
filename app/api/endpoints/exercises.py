"""
Endpoints API pour la gestion des exercices
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app.api.deps import get_db_session
from app.schemas.exercise import Exercise, ExerciseCreate, ExerciseUpdate
from app.schemas.common import PaginationParams
from app.models.exercise import DifficultyLevel, ExerciseType

router = APIRouter()


@router.get("/", response_model=List[Exercise])
def get_exercises(
    db: Session = Depends(get_db_session),
    params: PaginationParams = Depends(),
    exercise_type: Optional[ExerciseType] = None,
    difficulty: Optional[DifficultyLevel] = None,
) -> Any:
    """
    Récupérer tous les exercices avec filtre optionnel par type et difficulté.
    """
    # Données de test pour les exercices
    test_exercises = [
        {
            "id": 1,
            "title": "Addition simple",
            "exercise_type": ExerciseType.ADDITION.value,
            "difficulty": DifficultyLevel.INITIE.value,
            "question": "Combien font 2+2?",
            "correct_answer": "4",
            "choices": ["2", "3", "4", "5"],
            "explanation": "2 + 2 = 4, c'est une addition élémentaire.",
            "hint": "Ajoutez le premier nombre au second",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": 10,
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        },
        {
            "id": 2,
            "title": "Multiplication simple",
            "exercise_type": ExerciseType.MULTIPLICATION.value,
            "difficulty": DifficultyLevel.PADAWAN.value,
            "question": "Combien font 3×5?",
            "correct_answer": "15",
            "choices": ["10", "12", "15", "18"],
            "explanation": "3 × 5 = 15, c'est une multiplication élémentaire.",
            "hint": "Additionnez 5 trois fois",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": 8,
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    ]
    
    # Filtrer si nécessaire
    if exercise_type:
        test_exercises = [ex for ex in test_exercises if ex["exercise_type"] == exercise_type.value]
    if difficulty:
        test_exercises = [ex for ex in test_exercises if ex["difficulty"] == difficulty.value]
    
    return test_exercises


@router.get("/types", response_model=List[str])
def get_exercise_types() -> Any:
    """
    Récupérer tous les types d'exercices disponibles.
    """
    return [t.value for t in ExerciseType]


@router.get("/difficulties", response_model=List[str])
def get_difficulty_levels() -> Any:
    """
    Récupérer tous les niveaux de difficulté disponibles.
    """
    return [d.value for d in DifficultyLevel]


@router.post("/", response_model=Exercise)
def create_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_in: ExerciseCreate,
) -> Any:
    """
    Créer un nouvel exercice.
    """
    # Placeholder function - implement actual exercise creation
    return {
        "id": 0,
        "title": exercise_in.title,
        "exercise_type": exercise_in.exercise_type,
        "difficulty": exercise_in.difficulty,
        "question": exercise_in.question,
        "correct_answer": exercise_in.correct_answer,
        "choices": exercise_in.choices,
        "is_active": True
    }


@router.get("/random", response_model=Exercise)
def get_random_exercise(
    db: Session = Depends(get_db_session),
    exercise_type: Optional[ExerciseType] = None,
    difficulty: Optional[DifficultyLevel] = None,
) -> Any:
    """
    Récupérer un exercice aléatoire avec filtre optionnel par type et difficulté.
    """
    # Placeholder function - implement actual random exercise retrieval
    return {
        "id": 1,
        "title": "Exercice aléatoire",
        "exercise_type": ExerciseType.ADDITION.value,
        "difficulty": DifficultyLevel.INITIE.value,
        "question": "Combien font 2+2?",
        "correct_answer": "4",
        "choices": ["2", "3", "4", "5"],
        "is_active": True
    }


@router.get("/{exercise_id}", response_model=Exercise)
def get_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_id: int,
) -> Any:
    """
    Récupérer un exercice par ID.
    """
    # Placeholder function - implement actual exercise retrieval
    if exercise_id == 1:
        return {
            "id": 1,
            "title": "Addition simple",
            "exercise_type": ExerciseType.ADDITION.value,
            "difficulty": DifficultyLevel.INITIE.value,
            "question": "Combien font 2+2?",
            "correct_answer": "4",
            "choices": ["2", "3", "4", "5"],
            "explanation": "2 + 2 = 4, c'est une addition élémentaire.",
            "hint": "Ajoutez le premier nombre au second",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": 10,
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    elif exercise_id == 2:
        return {
            "id": 2,
            "title": "Multiplication simple",
            "exercise_type": ExerciseType.MULTIPLICATION.value,
            "difficulty": DifficultyLevel.PADAWAN.value,
            "question": "Combien font 3×5?",
            "correct_answer": "15",
            "choices": ["10", "12", "15", "18"],
            "explanation": "3 × 5 = 15, c'est une multiplication élémentaire.",
            "hint": "Additionnez 5 trois fois",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": 8,
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Exercice non trouvé"
    )


@router.post("/{exercise_id}/attempt", response_model=dict)
def attempt_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_id: int,
    attempt_data: dict,
) -> Any:
    """
    Soumettre une tentative pour un exercice.
    """
    # Récupérer l'exercice
    exercise = None
    try:
        exercise = get_exercise(db=db, exercise_id=exercise_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercice non trouvé"
        )
    
    # Vérifier la réponse
    user_answer = attempt_data.get("user_answer", "")
    is_correct = user_answer == exercise["correct_answer"]
    
    return {
        "is_correct": is_correct,
        "feedback": "Bravo, c'est correct!" if is_correct else "Ce n'est pas la bonne réponse.",
        "correct_answer": exercise["correct_answer"] if not is_correct else None,
        "explanation": exercise["explanation"]
    } 