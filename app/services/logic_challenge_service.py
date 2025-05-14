"""
Service pour la gestion des défis de logique mathématique (Épreuves du Conseil Jedi).
Implémente les opérations métier liées aux défis logiques et utilise le transaction manager.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt


class LogicChallengeService:
    """
    Service pour la gestion des défis de logique mathématique.
    Fournit des méthodes pour récupérer, créer, modifier et supprimer des défis.
    """
    
    @staticmethod
    def get_challenge(db: Session, challenge_id: int) -> Optional[LogicChallenge]:
        """
        Récupère un défi par son ID.
        
        Args:
            db: Session de base de données
            challenge_id: ID du défi à récupérer
            
        Returns:
            Le défi correspondant à l'ID ou None s'il n'existe pas
        """
        return DatabaseAdapter.get_by_id(db, LogicChallenge, challenge_id)
    
    @staticmethod
    def list_challenges(
        db: Session, 
        challenge_type: Optional[str] = None,
        age_group: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[LogicChallenge]:
        """
        Liste les défis actifs avec filtrage optionnel.
        
        Args:
            db: Session de base de données
            challenge_type: Type de défi à filtrer (optionnel)
            age_group: Groupe d'âge à filtrer (optionnel)
            limit: Nombre maximum de défis à retourner
            offset: Décalage pour la pagination
            
        Returns:
            Liste des défis correspondants aux critères
        """
        try:
            query = db.query(LogicChallenge).filter(LogicChallenge.is_archived == False)
            
            if challenge_type:
                query = query.filter(LogicChallenge.challenge_type == challenge_type)
            
            if age_group:
                query = query.filter(LogicChallenge.age_group == age_group)
            
            if offset is not None:
                query = query.offset(offset)
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des défis: {e}")
            return []
    
    @staticmethod
    def create_challenge(db: Session, challenge_data: Dict[str, Any]) -> Optional[LogicChallenge]:
        """
        Crée un nouveau défi.
        
        Args:
            db: Session de base de données
            challenge_data: Dictionnaire contenant les données du défi
            
        Returns:
            Le défi créé ou None en cas d'erreur
        """
        return DatabaseAdapter.create(db, LogicChallenge, challenge_data)
    
    @staticmethod
    def update_challenge(db: Session, challenge_id: int, challenge_data: Dict[str, Any]) -> bool:
        """
        Met à jour un défi existant.
        
        Args:
            db: Session de base de données
            challenge_id: ID du défi à mettre à jour
            challenge_data: Dictionnaire contenant les nouvelles valeurs
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        challenge = LogicChallengeService.get_challenge(db, challenge_id)
        if not challenge:
            logger.error(f"Défi avec ID {challenge_id} non trouvé pour mise à jour")
            return False
        
        return DatabaseAdapter.update(db, challenge, challenge_data)
    
    @staticmethod
    def archive_challenge(db: Session, challenge_id: int) -> bool:
        """
        Archive un défi (marque comme supprimé sans suppression physique).
        
        Args:
            db: Session de base de données
            challenge_id: ID du défi à archiver
            
        Returns:
            True si l'archivage a réussi, False sinon
        """
        challenge = LogicChallengeService.get_challenge(db, challenge_id)
        if not challenge:
            logger.error(f"Défi avec ID {challenge_id} non trouvé pour archivage")
            return False
        
        return DatabaseAdapter.archive(db, challenge)
    
    @staticmethod
    def delete_challenge(db: Session, challenge_id: int) -> bool:
        """
        Supprime physiquement un défi de la base de données.
        Les tentatives associées sont supprimées en cascade.
        
        Args:
            db: Session de base de données
            challenge_id: ID du défi à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        challenge = LogicChallengeService.get_challenge(db, challenge_id)
        if not challenge:
            logger.error(f"Défi avec ID {challenge_id} non trouvé pour suppression")
            return False
        
        return DatabaseAdapter.delete(db, challenge)
    
    @staticmethod
    def get_challenge_attempts(db: Session, challenge_id: int) -> List[LogicChallengeAttempt]:
        """
        Récupère toutes les tentatives associées à un défi.
        
        Args:
            db: Session de base de données
            challenge_id: ID du défi
            
        Returns:
            Liste des tentatives pour ce défi
        """
        return DatabaseAdapter.get_by_field(db, LogicChallengeAttempt, "challenge_id", challenge_id)
    
    @staticmethod
    def record_attempt(db: Session, attempt_data: Dict[str, Any]) -> Optional[LogicChallengeAttempt]:
        """
        Enregistre une nouvelle tentative pour un défi.
        
        Args:
            db: Session de base de données
            attempt_data: Dictionnaire contenant les données de la tentative
            
        Returns:
            La tentative créée ou None en cas d'erreur
        """
        with TransactionManager.transaction(db) as session:
            try:
                # Vérifier que le défi existe
                challenge_id = attempt_data.get("challenge_id")
                challenge = LogicChallengeService.get_challenge(session, challenge_id)
                
                if not challenge:
                    logger.error(f"Tentative d'enregistrement d'une tentative pour un défi inexistant (ID {challenge_id})")
                    return None
                
                # Créer la tentative
                attempt = LogicChallengeAttempt(**attempt_data)
                session.add(attempt)
                session.flush()
                
                # Log de l'action
                is_correct = attempt_data.get("is_correct", False)
                logger.info(f"Tentative enregistrée pour le défi {challenge_id}: {'Correcte' if is_correct else 'Incorrecte'}")
                
                return attempt
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement de la tentative: {e}")
                return None 