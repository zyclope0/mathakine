"""
Service pour la gestion des exercices mathématiques.
Implémente les opérations métier liées aux exercices et utilise le transaction manager.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt


class ExerciseService:
    """
    Service pour la gestion des exercices mathématiques.
    Fournit des méthodes pour récupérer, créer, modifier et supprimer des exercices.
    """
    
    @staticmethod
    def get_exercise(db: Session, exercise_id: int) -> Optional[Exercise]:
        """
        Récupère un exercice par son ID.
        
        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à récupérer
            
        Returns:
            L'exercice correspondant à l'ID ou None s'il n'existe pas
        """
        return DatabaseAdapter.get_by_id(db, Exercise, exercise_id)
    
    @staticmethod
    def list_exercises(
        db: Session, 
        exercise_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Exercise]:
        """
        Liste les exercices actifs avec filtrage optionnel.
        
        Args:
            db: Session de base de données
            exercise_type: Type d'exercice à filtrer (optionnel)
            difficulty: Niveau de difficulté à filtrer (optionnel)
            limit: Nombre maximum d'exercices à retourner
            offset: Décalage pour la pagination
            
        Returns:
            Liste des exercices correspondants aux critères
        """
        try:
            query = db.query(Exercise).filter(
                Exercise.is_archived == False,
                Exercise.is_active == True
            )
            
            # FILTRE CRITIQUE : Accepter les valeurs en majuscules ET minuscules
            # pour compatibilité avec les données existantes
            valid_types = [t.value for t in ExerciseType]
            valid_difficulties = [d.value for d in DifficultyLevel]
            
            # Ajouter les valeurs en minuscules pour compatibilité
            valid_types.extend(['addition', 'subtraction', 'multiplication', 'division', 'mixed'])
            valid_difficulties.extend(['initie', 'padawan', 'chevalier', 'maitre'])
            
            # Ne pas filtrer par énumération pour éviter les problèmes
            # query = query.filter(Exercise.exercise_type.in_(valid_types))
            # query = query.filter(Exercise.difficulty.in_(valid_difficulties))
            
            if exercise_type:
                query = query.filter(Exercise.exercise_type == exercise_type)
            
            if difficulty:
                query = query.filter(Exercise.difficulty == difficulty)
            
            if offset is not None:
                query = query.offset(offset)
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des exercices: {e}")
            return []
    
    @staticmethod
    def create_exercise(db: Session, exercise_data: Dict[str, Any]) -> Optional[Exercise]:
        """
        Crée un nouvel exercice.
        
        Args:
            db: Session de base de données
            exercise_data: Dictionnaire contenant les données de l'exercice
            
        Returns:
            L'exercice créé ou None en cas d'erreur
        """
        return DatabaseAdapter.create(db, Exercise, exercise_data)
    
    @staticmethod
    def update_exercise(db: Session, exercise_id: int, exercise_data: Dict[str, Any]) -> bool:
        """
        Met à jour un exercice existant.
        
        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à mettre à jour
            exercise_data: Dictionnaire contenant les nouvelles valeurs
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        exercise = ExerciseService.get_exercise(db, exercise_id)
        if not exercise:
            logger.error(f"Exercice avec ID {exercise_id} non trouvé pour mise à jour")
            return False
        
        return DatabaseAdapter.update(db, exercise, exercise_data)
    
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
        exercise = ExerciseService.get_exercise(db, exercise_id)
        if not exercise:
            logger.error(f"Exercice avec ID {exercise_id} non trouvé pour archivage")
            return False
        
        return DatabaseAdapter.archive(db, exercise)
    
    @staticmethod
    def delete_exercise(db: Session, exercise_id: int) -> bool:
        """
        Supprime physiquement un exercice de la base de données.
        Les tentatives associées sont supprimées en cascade.
        
        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        exercise = ExerciseService.get_exercise(db, exercise_id)
        if not exercise:
            logger.error(f"Exercice avec ID {exercise_id} non trouvé pour suppression")
            return False
        
        return DatabaseAdapter.delete(db, exercise)
    
    @staticmethod
    def get_exercise_attempts(db: Session, exercise_id: int) -> List[Attempt]:
        """
        Récupère toutes les tentatives associées à un exercice.
        
        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice
            
        Returns:
            Liste des tentatives pour cet exercice
        """
        return DatabaseAdapter.get_by_field(db, Attempt, "exercise_id", exercise_id)
    
    @staticmethod
    def record_attempt(db: Session, attempt_data: Dict[str, Any]) -> Optional[Attempt]:
        """
        Enregistre une nouvelle tentative pour un exercice.
        
        Args:
            db: Session de base de données
            attempt_data: Dictionnaire contenant les données de la tentative
            
        Returns:
            La tentative créée ou None en cas d'erreur
        """
        with TransactionManager.transaction(db) as session:
            try:
                # Vérifier que l'exercice existe
                exercise_id = attempt_data.get("exercise_id")
                exercise = ExerciseService.get_exercise(session, exercise_id)
                
                if not exercise:
                    logger.error(f"Tentative d'enregistrement d'une tentative pour un exercice inexistant (ID {exercise_id})")
                    return None
                
                # Créer la tentative
                attempt = Attempt(**attempt_data)
                session.add(attempt)
                session.flush()
                
                # Log de l'action
                is_correct = attempt_data.get("is_correct", False)
                logger.info(f"Tentative enregistrée pour l'exercice {exercise_id}: {'Correcte' if is_correct else 'Incorrecte'}")
                
                return attempt
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement de la tentative: {e}")
                return None 