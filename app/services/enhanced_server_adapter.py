"""
Service d'adaptation pour enhanced_server.py.
Permet d'utiliser le système de transaction et les services avec enhanced_server.py
sans modifier massivement le serveur existant.
"""

import json
from typing import Any, Dict, List, Optional, Union

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy.orm import Session

from app.db.adapter import DatabaseAdapter
from app.db.base import SessionLocal
from app.db.transaction import TransactionManager
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge
from app.models.user import User
from app.services import ExerciseService, LogicChallengeService, UserService


def _serialize_exercise(exercise: Exercise) -> Dict[str, Any]:
    """
    Helper pour sérialiser un objet Exercise en dictionnaire JSON-sérialisable.

    Args:
        exercise: Objet Exercise SQLAlchemy

    Returns:
        Dictionnaire sérialisable en JSON
    """
    # Convertir les énumérations en strings
    exercise_type_value = (
        exercise.exercise_type.value
        if hasattr(exercise.exercise_type, "value")
        else str(exercise.exercise_type)
    )
    difficulty_value = (
        exercise.difficulty.value
        if hasattr(exercise.difficulty, "value")
        else str(exercise.difficulty)
    )

    # Convertir les dates en ISO format strings
    created_at_str = exercise.created_at.isoformat() if exercise.created_at else None
    updated_at_str = exercise.updated_at.isoformat() if exercise.updated_at else None

    # Gérer les choices (peut être JSON string ou list)
    choices_value = exercise.choices
    if isinstance(choices_value, str):
        try:
            choices_value = json.loads(choices_value)
        except (json.JSONDecodeError, TypeError):
            choices_value = []
    elif choices_value is None:
        choices_value = []

    return {
        "id": exercise.id,
        "title": exercise.title,
        "creator_id": exercise.creator_id,
        "exercise_type": exercise_type_value,
        "difficulty": difficulty_value,
        "tags": exercise.tags,
        "question": exercise.question,
        "correct_answer": exercise.correct_answer,
        "choices": choices_value,
        "explanation": exercise.explanation,
        "hint": exercise.hint,
        "image_url": exercise.image_url,
        "audio_url": exercise.audio_url,
        "is_active": exercise.is_active,
        "is_archived": exercise.is_archived,
        "ai_generated": getattr(exercise, "ai_generated", False),
        "view_count": exercise.view_count or 0,
        "created_at": created_at_str,
        "updated_at": updated_at_str,
    }


class EnhancedServerAdapter:
    """
    Adaptateur pour enhanced_server.py.
    Fournit des méthodes qui correspondent aux opérations SQL directes
    dans enhanced_server.py, mais utilise notre système de transaction.
    """

    @staticmethod
    def get_db_session() -> Session:
        """
        Obtient une session de base de données.
        Remplace la fonction get_db_connection() de enhanced_server.py.

        Returns:
            Session: Une session SQLAlchemy
        """
        return SessionLocal()

    @staticmethod
    def close_db_session(db: Session) -> None:
        """
        Ferme une session de base de données.

        Args:
            db: Session à fermer
        """
        db.close()

    @staticmethod
    def get_exercise_by_id(db: Session, exercise_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un exercice par son ID.

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice

        Returns:
            Un dictionnaire contenant les données de l'exercice ou None
        """
        exercise = ExerciseService.get_exercise(db, exercise_id)
        if exercise:
            return _serialize_exercise(exercise)
        return None

    @staticmethod
    def list_exercises(
        db: Session,
        exercise_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Liste les exercices actifs avec filtrage optionnel.

        Args:
            db: Session de base de données
            exercise_type: Type d'exercice à filtrer
            difficulty: Niveau de difficulté à filtrer
            limit: Nombre maximum d'exercices à retourner

        Returns:
            Liste de dictionnaires contenant les données des exercices
        """
        exercises = ExerciseService.list_exercises(
            db, exercise_type=exercise_type, difficulty=difficulty, limit=limit
        )

        # Convertir les objets SQLAlchemy en dictionnaires avec sérialisation des dates
        return [_serialize_exercise(ex) for ex in exercises]

    @staticmethod
    def create_exercise(
        db: Session, exercise_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Crée un nouvel exercice.

        Args:
            db: Session de base de données
            exercise_data: Données de l'exercice

        Returns:
            Un dictionnaire contenant les données de l'exercice créé ou None
        """
        exercise = ExerciseService.create_exercise(db, exercise_data)
        if exercise:
            return _serialize_exercise(exercise)
        return None

    @staticmethod
    def create_generated_exercise(
        db: Session,
        exercise_type: str,
        age_group: str,  # Ajout du paramètre manquant
        difficulty: str,
        title: str,
        question: str,
        correct_answer: str,
        choices: List[str],
        explanation: str,
        hint: Optional[str] = None,
        tags: Optional[str] = None,
        ai_generated: bool = False,
        locale: str = "fr",
    ) -> Optional[Dict[str, Any]]:
        """
        Crée un nouvel exercice généré avec support des traductions.
        Cette méthode est spécifiquement conçue pour les fonctions de génération d'exercices
        dans enhanced_server.py.

        Args:
            db: Session de base de données (utilisée pour cohérence transactionnelle)
            exercise_type: Type d'exercice
            age_group: Groupe d'âge de l'exercice
            difficulty: Niveau de difficulté
            title: Titre de l'exercice
            question: Question de l'exercice
            correct_answer: Réponse correcte
            choices: Liste des choix de réponses
            explanation: Explication de la réponse
            hint: Indice (optionnel)
            tags: Tags (optionnel)
            ai_generated: Si l'exercice a été généré par IA
            locale: Locale pour la création des traductions (défaut: "fr")

        Returns:
            Un dictionnaire contenant les données de l'exercice créé ou None
        """
        # NOTE: exercise_service_translations archivé - utiliser ExerciseService ORM
        from app.services import ExerciseService

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
            f"Création d'un exercice généré de type {exercise_type}, groupe d'âge {age_group}, difficulté {difficulty}"
        )
        exercise = ExerciseService.create_exercise(db, exercise_data)
        return _serialize_exercise(exercise) if exercise else None

    @staticmethod
    def update_exercise(
        db: Session, exercise_id: int, exercise_data: Dict[str, Any]
    ) -> bool:
        """
        Met à jour un exercice existant.

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à mettre à jour
            exercise_data: Nouvelles données de l'exercice

        Returns:
            True si la mise à jour a réussi, False sinon
        """
        return ExerciseService.update_exercise(db, exercise_id, exercise_data)

    @staticmethod
    def archive_exercise(db: Session, exercise_id: int) -> bool:
        """
        Archive un exercice (marque comme supprimé sans suppression physique).

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à archiver

        Returns:
            True si l'archivage a réussi, False sinon
        """
        return ExerciseService.archive_exercise(db, exercise_id)

    @staticmethod
    def record_attempt(
        db: Session, attempt_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Enregistre une tentative de résolution d'exercice avec PostgreSQL direct.

        Args:
            db: Session de base de données (non utilisée, conservée pour compatibilité)
            attempt_data: Données de la tentative

        Returns:
            Un dictionnaire contenant les données de la tentative créée ou None
        """
        # NOTE: attempt_service_translations archivé - utiliser Attempt ORM
        from app.models.attempt import Attempt

        attempt = Attempt(**attempt_data)
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def get_user_stats(
        db: Session, user_id: int, time_range: str = "30"
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un utilisateur (base).

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            time_range: Période de temps ("7", "30", "90", "all")

        Returns:
            Un dictionnaire contenant les statistiques de l'utilisateur
        """
        return UserService.get_user_stats(db, user_id, time_range=time_range)

    @staticmethod
    def get_user_stats_for_dashboard(
        db: Session, user_id: int, time_range: str = "30"
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques complètes pour le tableau de bord (XP, niveau, activité).
        """
        return UserService.get_user_stats_for_dashboard(
            db, user_id, time_range=time_range
        )

    @staticmethod
    def execute_raw_query(
        db: Session, query: str, params: dict = None
    ) -> List[Dict[str, Any]]:
        """
        Exécute une requête SQL brute (paramètres nommés uniquement).
        À utiliser uniquement pour la compatibilité avec le code existant.
        Privilégier les méthodes du service (audit 3.1).

        Args:
            db: Session de base de données
            query: Requête SQL avec paramètres nommés (:param_name)
            params: Dictionnaire de paramètres nommés

        Returns:
            Liste de dictionnaires contenant les résultats
        """
        logger.warning(
            "Utilisation de execute_raw_query - À remplacer par les méthodes du service"
        )
        return DatabaseAdapter.execute_query(db, query, params or {})

    # === MÉTHODES POUR LOGIC CHALLENGES (NOUVEAU !) ===

    @staticmethod
    def get_logic_challenges(limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des logic challenges actifs.

        Args:
            limit: Nombre maximum de challenges à retourner

        Returns:
            Liste de dictionnaires contenant les données des logic challenges
        """
        db = EnhancedServerAdapter.get_db_session()
        try:
            challenges = LogicChallengeService.list_challenges(db, limit=limit)

            # Convertir en dictionnaires - utiliser to_dict() pour éviter les erreurs d'attributs
            return [ch.to_dict() for ch in challenges]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des logic challenges: {e}")
            return []
        finally:
            EnhancedServerAdapter.close_db_session(db)

    @staticmethod
    def get_logic_challenge(challenge_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un logic challenge par son ID.

        Args:
            challenge_id: ID du challenge

        Returns:
            Un dictionnaire contenant les données du challenge ou None
        """
        db = EnhancedServerAdapter.get_db_session()
        try:
            challenge = LogicChallengeService.get_challenge(db, challenge_id)
            if challenge:
                return challenge.to_dict()
            return None
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération du logic challenge {challenge_id}: {e}"
            )
            return None
        finally:
            EnhancedServerAdapter.close_db_session(db)
