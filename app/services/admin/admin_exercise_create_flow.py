"""
Flux de création exercice admin — Lot G3.

Sépare explicitement (calqué sur admin_badge_create_flow) :
1. préparation / normalisation d'entrée
2. validation métier
3. mutation / persistance
4. mapping (délégué à admin_content_service._exercise_to_detail)
"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.types import ExerciseCreatePrepared, ValidationResult
from app.models.exercise import Exercise
from app.services.admin.admin_helpers import log_admin_action


def prepare_exercise_create_data(data: Dict[str, Any]) -> ExerciseCreatePrepared:
    """
    Étape 1 : préparation / normalisation d'entrée.
    Extrait et normalise les champs pour la création d'un exercice.
    """
    return {
        "title": (data.get("title") or "").strip(),
        "question": (data.get("question") or "").strip(),
        "correct_answer": (data.get("correct_answer") or "").strip(),
        "exercise_type": (data.get("exercise_type") or "DIVERS").strip().upper(),
        "difficulty": (data.get("difficulty") or "PADAWAN").strip(),
        "age_group": (data.get("age_group") or "9-11").strip(),
        "choices": data.get("choices"),
        "explanation": (data.get("explanation") or "").strip() or None,
        "hint": (data.get("hint") or "").strip() or None,
        "tags": (data.get("tags") or "").strip() or None,
    }


def validate_exercise_create_pre_persist(
    prepared: ExerciseCreatePrepared, db: Session
) -> ValidationResult:
    """
    Étape 2 : validation métier.
    Retourne (error_message, status_code) ou (None, 0) si valide.
    """
    if not prepared.get("title"):
        return "Le titre est obligatoire.", 400
    if not prepared.get("question"):
        return "La question est obligatoire.", 400
    if not prepared.get("correct_answer"):
        return "La réponse correcte est obligatoire.", 400
    return None, 0


def persist_exercise_create(
    db: Session,
    prepared: ExerciseCreatePrepared,
    admin_user_id: Optional[int] = None,
) -> Exercise:
    """
    Étape 3 : mutation / persistance.
    Crée l'Exercise, log l'action admin, commit.
    """
    ex = Exercise(
        title=prepared["title"],
        exercise_type=prepared["exercise_type"],
        difficulty=prepared["difficulty"],
        age_group=prepared["age_group"],
        question=prepared["question"],
        correct_answer=prepared["correct_answer"],
        choices=prepared.get("choices"),
        explanation=prepared.get("explanation"),
        hint=prepared.get("hint"),
        tags=prepared.get("tags"),
        ai_generated=False,
    )
    db.add(ex)
    db.flush()
    log_admin_action(
        db, admin_user_id, "exercise_create", "exercise", ex.id, {"title": ex.title}
    )
    db.commit()
    db.refresh(ex)
    return ex
