"""
Service d'adaptation pour enhanced_server.py.
Permet d'utiliser le système de transaction et les services avec enhanced_server.py
sans modifier massivement le serveur existant.
"""
from typing import Dict, List, Any, Optional, Union
from sqlalchemy.orm import Session

from app.db.transaction import TransactionManager
from app.db.adapter import DatabaseAdapter
from app.services import ExerciseService, UserService, LogicChallengeService
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from app.models.user import User
from app.models.logic_challenge import LogicChallenge
from app.db.base import SessionLocal

from loguru import logger


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
            # Convertir l'objet SQLAlchemy en dictionnaire
            return {
                'id': exercise.id,
                'title': exercise.title,
                'creator_id': exercise.creator_id,
                'exercise_type': exercise.exercise_type,
                'difficulty': exercise.difficulty,
                'tags': exercise.tags,
                'question': exercise.question,
                'correct_answer': exercise.correct_answer,
                'choices': exercise.choices,
                'explanation': exercise.explanation,
                'hint': exercise.hint,
                'image_url': exercise.image_url,
                'audio_url': exercise.audio_url,
                'is_active': exercise.is_active,
                'is_archived': exercise.is_archived,
                'view_count': exercise.view_count,
                'created_at': exercise.created_at,
                'updated_at': exercise.updated_at
            }
        return None
    
    @staticmethod
    def list_exercises(
        db: Session, 
        exercise_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None
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
            db,
            exercise_type=exercise_type,
            difficulty=difficulty,
            limit=limit
        )
        
        # Convertir les objets SQLAlchemy en dictionnaires
        return [
            {
                'id': ex.id,
                'title': ex.title,
                'creator_id': ex.creator_id,
                'exercise_type': ex.exercise_type,
                'difficulty': ex.difficulty,
                'tags': ex.tags,
                'question': ex.question,
                'correct_answer': ex.correct_answer,
                'choices': ex.choices,
                'explanation': ex.explanation,
                'hint': ex.hint,
                'image_url': ex.image_url,
                'audio_url': ex.audio_url,
                'is_active': ex.is_active,
                'is_archived': ex.is_archived,
                'view_count': ex.view_count,
                'created_at': ex.created_at,
                'updated_at': ex.updated_at
            }
            for ex in exercises
        ]
    
    @staticmethod
    def create_exercise(db: Session, exercise_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
            return {
                'id': exercise.id,
                'title': exercise.title,
                'creator_id': exercise.creator_id,
                'exercise_type': exercise.exercise_type,
                'difficulty': exercise.difficulty,
                'tags': exercise.tags,
                'question': exercise.question,
                'correct_answer': exercise.correct_answer,
                'choices': exercise.choices,
                'explanation': exercise.explanation,
                'hint': exercise.hint,
                'image_url': exercise.image_url,
                'audio_url': exercise.audio_url,
                'is_active': exercise.is_active,
                'is_archived': exercise.is_archived,
                'view_count': exercise.view_count,
                'created_at': exercise.created_at,
                'updated_at': exercise.updated_at
            }
        return None
    
    @staticmethod
    def update_exercise(db: Session, exercise_id: int, exercise_data: Dict[str, Any]) -> bool:
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
    def record_attempt(db: Session, attempt_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enregistre une tentative de résolution d'exercice.
        
        Args:
            db: Session de base de données
            attempt_data: Données de la tentative
            
        Returns:
            Un dictionnaire contenant les données de la tentative créée ou None
        """
        attempt = ExerciseService.record_attempt(db, attempt_data)
        if attempt:
            return {
                'id': attempt.id,
                'user_id': attempt.user_id,
                'exercise_id': attempt.exercise_id,
                'user_answer': attempt.user_answer,
                'is_correct': attempt.is_correct,
                'time_spent': attempt.time_spent,
                'attempt_number': attempt.attempt_number,
                'hints_used': attempt.hints_used,
                'device_info': attempt.device_info,
                'created_at': attempt.created_at
            }
        return None
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            Un dictionnaire contenant les statistiques de l'utilisateur
        """
        return UserService.get_user_stats(db, user_id)
    
    @staticmethod
    def execute_raw_query(db: Session, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Exécute une requête SQL brute.
        À utiliser uniquement pour la compatibilité avec le code existant.
        
        Args:
            db: Session de base de données
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Liste de dictionnaires contenant les résultats
        """
        logger.warning("Utilisation de execute_raw_query - À remplacer par les méthodes du service")
        return DatabaseAdapter.execute_query(db, query, params or ()) 