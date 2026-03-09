"""
Repository pour les exercices — accès données uniquement.
Responsabilités : lecture utilisateur (adaptive), persistance exercice généré.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.adapter import DatabaseAdapter
from app.models.exercise import Exercise
from app.models.user import User

logger = get_logger(__name__)


class ExerciseRepository:
    """Accès données pour le domaine exercice."""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par ID pour la résolution adaptative.

        Args:
            db: Session SQLAlchemy
            user_id: ID de l'utilisateur

        Returns:
            Objet User ou None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def persist_generated_exercise(
        db: Session,
        exercise_type: str,
        age_group: str,
        difficulty: str,
        title: str,
        question: str,
        correct_answer: str,
        choices: List[str],
        explanation: str,
        hint: Optional[str] = None,
        tags: Optional[str] = None,
        ai_generated: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Persiste un exercice généré en base.

        Args:
            db: Session SQLAlchemy
            exercise_type: Type d'exercice
            age_group: Groupe d'âge
            difficulty: Difficulté dérivée
            title: Titre
            question: Question
            correct_answer: Réponse correcte
            choices: Liste des choix
            explanation: Explication
            hint: Indice (optionnel)
            tags: Tags (optionnel)
            ai_generated: Généré par IA

        Returns:
            Dictionnaire avec id et données de l'exercice créé, ou None
        """
        exercise_data = {
            "title": title,
            "exercise_type": exercise_type,
            "age_group": age_group,
            "difficulty": difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "explanation": explanation,
            "hint": hint,
            "tags": tags or "generated",
            "ai_generated": ai_generated,
            "is_active": True,
            "is_archived": False,
            "view_count": 0,
        }
        logger.info(
            f"Création exercice généré: type={exercise_type}, age_group={age_group}, difficulty={difficulty}"
        )
        exercise = DatabaseAdapter.create(db, Exercise, exercise_data)
        if not exercise:
            return None
        return {"id": exercise.id}
