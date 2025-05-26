"""
Service pour la gestion des utilisateurs.
Implémente les opérations métier liées aux utilisateurs et utilise le transaction manager.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.models.user import User, UserRole
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db


class UserService:
    """
    Service pour la gestion des utilisateurs.
    Fournit des méthodes pour récupérer, créer, modifier et supprimer des utilisateurs,
    ainsi que pour consulter leurs activités et statistiques.
    """
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à récupérer
            
        Returns:
            L'utilisateur correspondant à l'ID ou None s'il n'existe pas
        """
        return DatabaseAdapter.get_by_id(db, User, user_id)
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            db: Session de base de données
            username: Nom d'utilisateur à rechercher
            
        Returns:
            L'utilisateur correspondant au nom d'utilisateur ou None s'il n'existe pas
        """
        users = DatabaseAdapter.get_by_field(db, User, "username", username)
        return users[0] if users else None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son adresse email.
        
        Args:
            db: Session de base de données
            email: Adresse email à rechercher
            
        Returns:
            L'utilisateur correspondant à l'adresse email ou None s'il n'existe pas
        """
        users = DatabaseAdapter.get_by_field(db, User, "email", email)
        return users[0] if users else None
    
    @staticmethod
    def list_users(db: Session, limit: Optional[int] = None, offset: Optional[int] = None) -> List[User]:
        """
        Liste tous les utilisateurs actifs.
        
        Args:
            db: Session de base de données
            limit: Nombre maximum d'utilisateurs à retourner
            offset: Décalage pour la pagination
            
        Returns:
            Liste des utilisateurs actifs
        """
        try:
            query = db.query(User).filter(User.is_active == True)
            
            if offset is not None:
                query = query.offset(offset)
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []
    
    @staticmethod
    def create_user(db: Session, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Crée un nouvel utilisateur.
        
        Args:
            db: Session de base de données
            user_data: Dictionnaire contenant les données de l'utilisateur
            
        Returns:
            L'utilisateur créé ou None en cas d'erreur
        """
        # Vérifier si l'utilisateur existe déjà (par email ou username)
        username = user_data.get("username")
        email = user_data.get("email")
        
        with TransactionManager.transaction(db, auto_commit=False) as session:
            if username and UserService.get_user_by_username(session, username):
                logger.error(f"Un utilisateur avec le nom '{username}' existe déjà")
                return None
            
            if email and UserService.get_user_by_email(session, email):
                logger.error(f"Un utilisateur avec l'email '{email}' existe déjà")
                return None
            
            # Adapter le rôle utilisateur pour le moteur de base de données actuel
            role = user_data.get("role")
            if role:
                user_data["role"] = adapt_enum_for_db("UserRole", role, session)
                logger.debug(f"Rôle adapté: de '{role}' à '{user_data['role']}'")
            
            return DatabaseAdapter.create(session, User, user_data)
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> bool:
        """
        Met à jour un utilisateur existant.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à mettre à jour
            user_data: Dictionnaire contenant les nouvelles valeurs
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour mise à jour")
            return False
        
        # Adapter le rôle utilisateur si présent dans les données de mise à jour
        if "role" in user_data:
            role = user_data["role"]
            user_data["role"] = adapt_enum_for_db("UserRole", role, db)
            logger.debug(f"Rôle adapté pour mise à jour: de '{role}' à '{user_data['role']}'")
        
        return DatabaseAdapter.update(db, user, user_data)
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Supprime physiquement un utilisateur de la base de données.
        Les entités associées sont supprimées en cascade.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour suppression")
            return False
        
        return DatabaseAdapter.delete(db, user)
    
    @staticmethod
    def disable_user(db: Session, user_id: int) -> bool:
        """
        Désactive un utilisateur (préférable à la suppression).
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à désactiver
            
        Returns:
            True si la désactivation a réussi, False sinon
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour désactivation")
            return False
        
        return DatabaseAdapter.update(db, user, {"is_active": False})
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire contenant les statistiques de l'utilisateur
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour récupération des statistiques")
            return {}
        
        try:
            # Statistiques de base
            attempts_query = db.query(Attempt).filter(Attempt.user_id == user_id)
            total_attempts = attempts_query.count()
            correct_attempts = attempts_query.filter(Attempt.is_correct == True).count()
            
            # Calculer le taux de réussite (éviter la division par zéro)
            success_rate = round((correct_attempts / total_attempts) * 100) if total_attempts > 0 else 0
            
            # Statistiques par type d'exercice
            exercise_types_stats = {}
            
            # Récupérer tous les types d'exercices disponibles
            exercise_types_query = db.query(Exercise.exercise_type).distinct()
            exercise_types = [et[0] for et in exercise_types_query.all()]
            
            # Pour chaque type, calculer les statistiques
            for ex_type in exercise_types:
                # Récupérer les tentatives de ce type
                type_attempts = (
                    db.query(Attempt)
                    .join(Exercise, Exercise.id == Attempt.exercise_id)
                    .filter(Attempt.user_id == user_id)
                    .filter(Exercise.exercise_type == ex_type)
                    .all()
                )
                
                total_type = len(type_attempts)
                correct_type = sum(1 for a in type_attempts if a.is_correct)
                success_rate_type = round((correct_type / total_type) * 100) if total_type > 0 else 0
                
                exercise_types_stats[ex_type] = {
                    "total": total_type,
                    "correct": correct_type,
                    "success_rate": success_rate_type
                }
            
            # Récupérer les données de progression si disponibles
            progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
            progress_data = {}
            
            for record in progress_records:
                ex_type = record.exercise_type
                difficulty = record.difficulty
                
                if ex_type not in progress_data:
                    progress_data[ex_type] = {}
                
                progress_data[ex_type][difficulty] = {
                    "mastery_level": record.mastery_level,
                    "streak": record.streak,
                    "highest_streak": record.highest_streak,
                    "total_attempts": record.total_attempts,
                    "correct_attempts": record.correct_attempts
                }
            
            # Assembler toutes les statistiques
            stats = {
                "user_id": user.id,
                "username": user.username,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "grade_level": user.grade_level
                },
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "success_rate": success_rate,
                "by_exercise_type": exercise_types_stats
            }
            
            # Ajouter les données de progression si disponibles
            if progress_data:
                stats["progress"] = progress_data
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {"stats_error": "Erreur lors de la récupération des statistiques"} 