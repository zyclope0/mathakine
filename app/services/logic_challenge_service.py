"""
Service pour la gestion des défis de logique mathématique (Épreuves du Conseil Jedi).
Implémente les opérations métier liées aux défis logiques et utilise le transaction manager.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt, LogicChallengeType, AgeGroup
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db


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
                # Adapter le type de défi pour le moteur de base de données actuel
                adapted_type = adapt_enum_for_db("LogicChallengeType", challenge_type, db)
                logger.debug(f"Type de défi adapté: de '{challenge_type}' à '{adapted_type}'")
                query = query.filter(LogicChallenge.challenge_type == adapted_type)
            
            if age_group:
                # Adapter le groupe d'âge pour le moteur de base de données actuel
                adapted_age = adapt_enum_for_db("AgeGroup", age_group, db)
                logger.debug(f"Groupe d'âge adapté: de '{age_group}' à '{adapted_age}'")
                query = query.filter(LogicChallenge.age_group == adapted_age)
            
            if offset is not None:
                query = query.offset(offset)
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
        except Exception as challenges_fetch_error:
            logger.error(f"Erreur lors de la récupération des défis: {challenges_fetch_error}")
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
        # Adapter les valeurs d'enum pour le moteur de base de données actuel
        if "challenge_type" in challenge_data:
            challenge_type = challenge_data["challenge_type"]
            challenge_data["challenge_type"] = adapt_enum_for_db("LogicChallengeType", challenge_type, db)
            logger.debug(f"Type de défi adapté: de '{challenge_type}' à '{challenge_data['challenge_type']}'")
        
        if "age_group" in challenge_data:
            age_group = challenge_data["age_group"]
            challenge_data["age_group"] = adapt_enum_for_db("AgeGroup", age_group, db)
            logger.debug(f"Groupe d'âge adapté: de '{age_group}' à '{challenge_data['age_group']}'")
        
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
        
        # Adapter les valeurs d'enum pour le moteur de base de données actuel
        if "challenge_type" in challenge_data:
            challenge_type = challenge_data["challenge_type"]
            challenge_data["challenge_type"] = adapt_enum_for_db("LogicChallengeType", challenge_type, db)
            logger.debug(f"Type de défi adapté pour mise à jour: de '{challenge_type}' à '{challenge_data['challenge_type']}'")
        
        if "age_group" in challenge_data:
            age_group = challenge_data["age_group"]
            challenge_data["age_group"] = adapt_enum_for_db("AgeGroup", age_group, db)
            logger.debug(f"Groupe d'âge adapté pour mise à jour: de '{age_group}' à '{challenge_data['age_group']}'")
        
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
            except Exception as attempt_save_error:
                logger.error(f"Erreur lors de l'enregistrement de la tentative: {attempt_save_error}")
                return None 