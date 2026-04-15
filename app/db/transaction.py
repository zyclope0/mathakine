"""
Transaction management utilities for database operations in Mathakine.
This module provides consistent transaction management across the application.
"""

from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.exceptions import DatabaseOperationError

logger = get_logger(__name__)


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
            logger.debug("%s: Début de la transaction (avec savepoint)", log_prefix)

            yield db_session

            if auto_commit:
                # Commit du savepoint (libère le SAVEPOINT côté DB)
                savepoint.commit()
                # Commit de la transaction principale pour persister les données
                db_session.commit()
                logger.debug("%s: Transaction validée (commit)", log_prefix)
        except Exception as savepoint_error:
            # Rollback au savepoint
            if "savepoint" in locals() and savepoint.is_active:
                savepoint.rollback()
            # Également rollback de la transaction principale
            db_session.rollback()
            logger.error(
                "%s: Transaction annulée (rollback) suite à l'erreur: %s",
                log_prefix,
                savepoint_error,
            )
            raise

    @staticmethod
    def commit(db_session: Session, log_prefix="DB"):
        """Valide les modifications de la session en cours"""
        try:
            db_session.commit()
            logger.debug("%s: Transaction validée (commit)", log_prefix)
            return True
        except Exception as commit_error:
            db_session.rollback()
            logger.error(
                "%s: Échec de commit, transaction annulée: %s", log_prefix, commit_error
            )
            return False

    @staticmethod
    def rollback(db_session: Session, log_prefix="DB"):
        """Annule les modifications de la session en cours"""
        try:
            db_session.rollback()
            logger.debug("%s: Transaction annulée (rollback)", log_prefix)
            return True
        except Exception as rollback_error:
            logger.error("%s: Échec de rollback: %s", log_prefix, rollback_error)
            return False

    @staticmethod
    def safe_delete(
        db_session: Session, obj, *, auto_commit=True, log_prefix="DB"
    ) -> None:
        """
        Supprime un objet de la base de données en toute sécurité.
        Les suppressions en cascade sont gérées automatiquement grâce aux relations SQLAlchemy.

        Args:
            db_session: Session SQLAlchemy
            obj: L'objet à supprimer
            auto_commit: Si True, commit après la suppression
            log_prefix: Préfixe pour les messages de journalisation

        Raises:
            DatabaseOperationError: Si la suppression échoue (objet introuvable ou erreur DB)
        """
        try:
            obj_id = getattr(obj, "id", None)
            if obj not in db_session:
                if obj_id:
                    obj_from_db = (
                        db_session.query(obj.__class__)
                        .filter(obj.__class__.id == obj_id)
                        .first()
                    )
                    if not obj_from_db:
                        msg = (
                            f"{log_prefix}: Objet {obj.__class__.__name__}"
                            f"(id={obj_id}) non trouvé dans la base de données"
                        )
                        logger.error(msg)
                        raise DatabaseOperationError(msg)
                    obj = obj_from_db
                else:
                    msg = f"{log_prefix}: L'objet {obj.__class__.__name__} n'a pas d'attribut id"
                    logger.error(msg)
                    raise DatabaseOperationError(msg)

            db_session.delete(obj)
            logger.debug(
                "%s: Objet %s(id=%s) marqué pour suppression",
                log_prefix,
                obj.__class__.__name__,
                getattr(obj, "id", "N/A"),
            )

            if auto_commit:
                try:
                    db_session.commit()
                    logger.debug("%s: Suppression confirmée avec succès", log_prefix)
                except Exception as delete_commit_error:
                    db_session.rollback()
                    logger.error(
                        "%s: Échec de la suppression lors du commit: %s",
                        log_prefix,
                        delete_commit_error,
                    )
                    # Pas de fallback SQL brut (A44-S1) : évite DELETE ad hoc hors ORM
                    # et comportements imprevisibles (FK, cascades, audit).
                    raise DatabaseOperationError(
                        f"{log_prefix}: Échec de la suppression lors du commit"
                    ) from delete_commit_error

        except DatabaseOperationError:
            raise
        except Exception as delete_error:
            db_session.rollback()
            msg = f"{log_prefix}: Échec de la suppression: {delete_error}"
            logger.error(msg)
            raise DatabaseOperationError(msg) from delete_error

    @staticmethod
    def safe_archive(
        db_session: Session, obj, *, auto_commit=True, log_prefix="DB"
    ) -> None:
        """
        Archive un objet au lieu de le supprimer physiquement.

        Args:
            db_session: Session SQLAlchemy
            obj: L'objet à archiver (doit avoir un attribut is_archived)
            auto_commit: Si True, commit après l'archivage
            log_prefix: Préfixe pour les messages de journalisation

        Raises:
            DatabaseOperationError: Si l'archivage échoue (attribut manquant,
                objet introuvable ou erreur DB)
        """
        try:
            if not hasattr(obj, "is_archived"):
                msg = (
                    f"{log_prefix}: L'objet {obj.__class__.__name__}"
                    " n'a pas d'attribut is_archived"
                )
                logger.error(msg)
                raise DatabaseOperationError(msg)

            obj_id = getattr(obj, "id", None)
            if obj not in db_session:
                if obj_id:
                    obj_from_db = (
                        db_session.query(obj.__class__)
                        .filter(obj.__class__.id == obj_id)
                        .first()
                    )
                    if not obj_from_db:
                        msg = (
                            f"{log_prefix}: Objet {obj.__class__.__name__}"
                            f"(id={obj_id}) non trouvé dans la base de données"
                        )
                        logger.error(msg)
                        raise DatabaseOperationError(msg)
                    obj = obj_from_db
                else:
                    obj = db_session.merge(obj)

            obj.is_archived = True
            logger.debug(
                "%s: Objet %s(id=%s) marqué comme archivé",
                log_prefix,
                obj.__class__.__name__,
                getattr(obj, "id", "N/A"),
            )

            if auto_commit:
                db_session.commit()
                logger.debug("%s: Archivage confirmé avec succès", log_prefix)

        except DatabaseOperationError:
            raise
        except Exception as e:
            db_session.rollback()
            msg = f"{log_prefix}: Échec de l'archivage: {e}"
            logger.error(msg)
            raise DatabaseOperationError(msg) from e
