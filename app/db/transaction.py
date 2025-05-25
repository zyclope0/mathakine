"""
Transaction management utilities for database operations in Mathakine.
This module provides consistent transaction management across the application.
"""
from contextlib import contextmanager
from sqlalchemy.orm import Session
from loguru import logger
from sqlalchemy import text


class TransactionManager:
    """
    Gère les transactions de base de données de manière unifiée.
    Fournit des méthodes pour démarrer, valider et annuler des transactions,
    ainsi qu'un gestionnaire de contexte pour une utilisation simplifiée.
    """
    
    @staticmethod
    @contextmanager
    def transaction(db_session: Session, *, auto_commit=True, log_prefix="DB"):
        """
        Gestionnaire de contexte pour les transactions de base de données.
        
        Args:
            db_session: Session SQLAlchemy à utiliser
            auto_commit: Si True, commit automatiquement à la fin du bloc
            log_prefix: Préfixe pour les messages de journalisation
            
        Yields:
            Session: La session de base de données
            
        Usage:
            with TransactionManager.transaction(db) as session:
                # Effectuer des opérations
                session.add(model)
                # Pas besoin de faire session.commit() - c'est géré automatiquement
        """
        # Créer un point de sauvegarde pour permettre un rollback partiel
        # même si nous sommes dans une transaction externe
        try:
            savepoint = db_session.begin_nested()
            logger.debug(f"{log_prefix}: Début de la transaction (avec savepoint)")
            
            yield db_session
            
            if auto_commit:
                # Commit du savepoint
                savepoint.commit()
                # Commit de la transaction principale si nous ne sommes pas dans une transaction de test
                if not savepoint.is_active:
                    db_session.commit()
                logger.debug(f"{log_prefix}: Transaction validée (commit)")
        except Exception as e:
            # Rollback au savepoint
            if 'savepoint' in locals() and savepoint.is_active:
                savepoint.rollback()
            # Également rollback de la transaction principale
            db_session.rollback()
            logger.error(f"{log_prefix}: Transaction annulée (rollback) suite à l'erreur: {e}")
            raise
    
    @staticmethod
    def commit(db_session: Session, log_prefix="DB"):
        """Valide les modifications de la session en cours"""
        try:
            db_session.commit()
            logger.debug(f"{log_prefix}: Transaction validée (commit)")
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"{log_prefix}: Échec de commit, transaction annulée: {e}")
            return False
    
    @staticmethod
    def rollback(db_session: Session, log_prefix="DB"):
        """Annule les modifications de la session en cours"""
        try:
            db_session.rollback()
            logger.debug(f"{log_prefix}: Transaction annulée (rollback)")
            return True
        except Exception as e:
            logger.error(f"{log_prefix}: Échec de rollback: {e}")
            return False
    
    @staticmethod
    def safe_delete(db_session: Session, obj, *, auto_commit=True, log_prefix="DB"):
        """
        Supprime un objet de la base de données en toute sécurité.
        Les suppressions en cascade sont gérées automatiquement grâce aux relations SQLAlchemy.
        
        Args:
            db_session: Session SQLAlchemy
            obj: L'objet à supprimer
            auto_commit: Si True, commit après la suppression
            log_prefix: Préfixe pour les messages de journalisation
        
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            # Supprimer directement l'objet
            db_session.delete(obj)
            logger.debug(f"{log_prefix}: Objet {obj.__class__.__name__}(id={getattr(obj, 'id', 'N/A')}) marqué pour suppression")
            
            if auto_commit:
                # Utiliser un savepoint pour pouvoir faire un rollback partiel en cas d'erreur
                try:
                    db_session.commit()
                    logger.debug(f"{log_prefix}: Suppression confirmée avec succès")
                    return True
                except Exception as e:
                    db_session.rollback()
                    logger.error(f"{log_prefix}: Échec de la suppression lors du commit: {e}")
                    
                    # Alternative: tenter une suppression sans cascade si la première méthode échoue
                    try:
                        # Suppression directe par ID pour éviter de charger les relations
                        stmt = f"DELETE FROM {obj.__tablename__} WHERE id = :id"
                        db_session.execute(text(stmt), {"id": obj.id})
                        db_session.commit()
                        logger.info(f"{log_prefix}: Suppression alternative réussie pour {obj.__class__.__name__}(id={obj.id})")
                        return True
                    except Exception as e2:
                        db_session.rollback()
                        logger.error(f"{log_prefix}: Échec de la suppression alternative: {e2}")
                        return False
            
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"{log_prefix}: Échec de la suppression: {e}")
            return False
    
    @staticmethod
    def safe_archive(db_session: Session, obj, *, auto_commit=True, log_prefix="DB"):
        """
        Archive un objet au lieu de le supprimer physiquement.
        
        Args:
            db_session: Session SQLAlchemy
            obj: L'objet à archiver (doit avoir un attribut is_archived)
            auto_commit: Si True, commit après l'archivage
            log_prefix: Préfixe pour les messages de journalisation
            
        Returns:
            bool: True si l'archivage a réussi, False sinon
        """
        try:
            if not hasattr(obj, 'is_archived'):
                logger.error(f"{log_prefix}: L'objet {obj.__class__.__name__} n'a pas d'attribut is_archived")
                return False
                
            obj.is_archived = True
            logger.debug(f"{log_prefix}: Objet {obj.__class__.__name__}(id={getattr(obj, 'id', 'N/A')}) marqué comme archivé")
            
            if auto_commit:
                db_session.commit()
                logger.debug(f"{log_prefix}: Archivage confirmé avec succès")
            
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"{log_prefix}: Échec de l'archivage: {e}")
            return False 