"""
Service pour la gestion des défis de logique mathématique (Épreuves du Conseil Jedi).
Implémente les opérations métier liées aux défis logiques et utilise le transaction manager.
"""

from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.exceptions import ChallengeNotFoundError
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.utils.db_helpers import adapt_enum_for_db, get_enum_value


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
    def get_challenge_or_raise(db: Session, challenge_id: int) -> LogicChallenge:
        """
        Récupère un défi par son ID.
        Lève ChallengeNotFoundError si le défi n'existe pas.
        """
        challenge = DatabaseAdapter.get_by_id(db, LogicChallenge, challenge_id)
        if not challenge:
            raise ChallengeNotFoundError()
        return challenge

    @staticmethod
    def list_challenges(
        db: Session,
        challenge_type: Optional[str] = None,
        age_group: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
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
                adapted_type = adapt_enum_for_db(
                    "LogicChallengeType", challenge_type, db
                )
                logger.debug(
                    f"Type de défi adapté: de '{challenge_type}' à '{adapted_type}'"
                )
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
        except SQLAlchemyError as challenges_fetch_error:
            logger.error(
                f"Erreur lors de la récupération des défis: {challenges_fetch_error}"
            )
            return []

    @staticmethod
    def create_challenge(
        db: Session, challenge_data: Dict[str, Any]
    ) -> Optional[LogicChallenge]:
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
            challenge_data["challenge_type"] = adapt_enum_for_db(
                "LogicChallengeType", challenge_type, db
            )
            logger.debug(
                f"Type de défi adapté: de '{challenge_type}' à '{challenge_data['challenge_type']}'"
            )

        if "age_group" in challenge_data:
            age_group = challenge_data["age_group"]
            challenge_data["age_group"] = adapt_enum_for_db("AgeGroup", age_group, db)
            logger.debug(
                f"Groupe d'âge adapté: de '{age_group}' à '{challenge_data['age_group']}'"
            )

        # Définir explicitement created_at si non présent pour éviter les valeurs NULL
        from datetime import datetime, timezone

        if (
            "created_at" not in challenge_data
            or challenge_data.get("created_at") is None
        ):
            challenge_data["created_at"] = datetime.now(timezone.utc)

        return DatabaseAdapter.create(db, LogicChallenge, challenge_data)

    @staticmethod
    def update_challenge(
        db: Session, challenge_id: int, challenge_data: Dict[str, Any]
    ) -> bool:
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
            challenge_data["challenge_type"] = adapt_enum_for_db(
                "LogicChallengeType", challenge_type, db
            )
            logger.debug(
                f"Type de défi adapté pour mise à jour: de '{challenge_type}' à '{challenge_data['challenge_type']}'"
            )

        if "age_group" in challenge_data:
            age_group = challenge_data["age_group"]
            challenge_data["age_group"] = adapt_enum_for_db("AgeGroup", age_group, db)
            logger.debug(
                f"Groupe d'âge adapté pour mise à jour: de '{age_group}' à '{challenge_data['age_group']}'"
            )

        return DatabaseAdapter.update(db, challenge, challenge_data)

    @staticmethod
    def archive_challenge(db: Session, challenge_id: int) -> None:
        """
        Archive un défi (marque comme supprimé sans suppression physique).

        Args:
            db: Session de base de données
            challenge_id: ID du défi à archiver

        Raises:
            ChallengeNotFoundError: Si le défi n'existe pas
            DatabaseOperationError: Si l'archivage échoue en base de données
        """
        challenge = LogicChallengeService.get_challenge(db, challenge_id)
        if not challenge:
            logger.error(f"Défi avec ID {challenge_id} non trouvé pour archivage")
            raise ChallengeNotFoundError(f"Défi avec ID {challenge_id} non trouvé")

        DatabaseAdapter.archive(db, challenge)

    @staticmethod
    def delete_challenge(db: Session, challenge_id: int) -> None:
        """
        Supprime physiquement un défi de la base de données.
        Les tentatives associées sont supprimées en cascade.

        Args:
            db: Session de base de données
            challenge_id: ID du défi à supprimer

        Raises:
            ChallengeNotFoundError: Si le défi n'existe pas
            DatabaseOperationError: Si la suppression échoue en base de données
        """
        challenge = LogicChallengeService.get_challenge(db, challenge_id)
        if not challenge:
            logger.error(f"Défi avec ID {challenge_id} non trouvé pour suppression")
            raise ChallengeNotFoundError(f"Défi avec ID {challenge_id} non trouvé")

        DatabaseAdapter.delete(db, challenge)

    @staticmethod
    def get_challenge_attempts(
        db: Session, challenge_id: int
    ) -> List[LogicChallengeAttempt]:
        """
        Récupère toutes les tentatives associées à un défi.

        Args:
            db: Session de base de données
            challenge_id: ID du défi

        Returns:
            Liste des tentatives pour ce défi
        """
        return DatabaseAdapter.get_by_field(
            db, LogicChallengeAttempt, "challenge_id", challenge_id
        )

    @staticmethod
    def record_attempt(
        db: Session, attempt_data: Dict[str, Any], *, auto_commit: bool = True
    ) -> Optional[LogicChallengeAttempt]:
        """
        Enregistre une nouvelle tentative pour un défi.

        Args:
            db: Session de base de données
            attempt_data: Dictionnaire contenant les données de la tentative

        Returns:
            La tentative créée ou None en cas d'erreur
        """
        try:
            # Vérifier que le défi existe
            challenge_id = attempt_data.get("challenge_id")
            challenge = LogicChallengeService.get_challenge(db, challenge_id)

            if not challenge:
                logger.error(
                    f"Tentative d'enregistrement d'une tentative pour un défi inexistant (ID {challenge_id})"
                )
                return None

            # Créer la tentative
            attempt = LogicChallengeAttempt(**attempt_data)
            db.add(attempt)
            db.flush()

            # Log de l'action
            is_correct = attempt_data.get("is_correct", False)
            logger.info(
                f"Tentative enregistrée pour le défi {challenge_id}: {'Correcte' if is_correct else 'Incorrecte'}"
            )

            if auto_commit:
                db.commit()
                db.refresh(attempt)
            return attempt
        except SQLAlchemyError as attempt_save_error:
            if auto_commit:
                db.rollback()
            logger.error(
                f"Erreur lors de l'enregistrement de la tentative: {attempt_save_error}"
            )
            return None
        except (TypeError, ValueError) as attempt_save_error:
            if auto_commit:
                db.rollback()
            logger.error(
                f"Erreur de données lors de l'enregistrement de la tentative: {attempt_save_error}"
            )
            return None

    @staticmethod
    def submit_answer_result(
        db: Session,
        challenge_id: int,
        user_id: int,
        user_solution: Any,
        time_spent: Any = None,
        hints_used_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Orchestrateur transactionnel pour une tentative de défi logique.
        """
        from app.services.badge_service import BadgeService
        from app.services.challenge_answer_service import check_answer

        challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)
        challenge_type = (
            str(challenge.challenge_type).lower() if challenge.challenge_type else ""
        )
        is_correct = check_answer(
            challenge_type=challenge_type,
            user_answer=user_solution,
            correct_answer=challenge.correct_answer or "",
            visual_data=getattr(challenge, "visual_data", None),
        )

        attempt_data = {
            "user_id": user_id,
            "challenge_id": challenge_id,
            "user_solution": user_solution,
            "is_correct": is_correct,
            "time_spent": time_spent,
            "hints_used": hints_used_count,
        }
        attempt = LogicChallengeService.record_attempt(
            db, attempt_data, auto_commit=False
        )
        if not attempt:
            raise ValueError("Impossible d'enregistrer la tentative.")

        new_badges = []
        if is_correct:
            try:
                badge_service = BadgeService(db, auto_commit=False)
                new_badges = badge_service.check_and_award_badges(user_id)
            except (SQLAlchemyError, TypeError, ValueError) as badge_err:
                logger.warning(
                    "Badge check après défi (best effort): %s",
                    badge_err,
                    exc_info=True,
                )

        try:
            from app.services.streak_service import update_user_streak

            streak_savepoint = db.begin_nested()
            update_user_streak(db, user_id, auto_commit=False)
            streak_savepoint.commit()
        except ImportError:
            logger.warning("Streak service indisponible (ImportError)", exc_info=True)
        except (SQLAlchemyError, TypeError, ValueError):
            if "streak_savepoint" in locals() and streak_savepoint.is_active:
                streak_savepoint.rollback()
            logger.debug("Streak update skipped", exc_info=True)

        if is_correct:
            try:
                from app.services.daily_challenge_service import (
                    record_logic_challenge_completed,
                )

                daily_savepoint = db.begin_nested()
                record_logic_challenge_completed(db, user_id, is_correct)
                daily_savepoint.commit()
            except Exception:
                if "daily_savepoint" in locals() and daily_savepoint.is_active:
                    daily_savepoint.rollback()
                logger.debug("Daily challenge update skipped (logic)", exc_info=True)

        progress_notif = None
        if not new_badges:
            try:
                svc = BadgeService(db, auto_commit=False)
                progress_notif = svc.get_closest_progress_notification(user_id)
            except (SQLAlchemyError, TypeError, ValueError):
                logger.debug(
                    "Progress notification skipped (best effort)",
                    exc_info=True,
                )

        db.commit()
        db.refresh(attempt)

        response_data = {
            "is_correct": is_correct,
            "explanation": challenge.solution_explanation if is_correct else None,
            "new_badges": new_badges,
        }
        if progress_notif:
            response_data["progress_notification"] = progress_notif

        if not is_correct:
            hints_list = challenge.hints if isinstance(challenge.hints, list) else []
            response_data["hints_remaining"] = len(hints_list) - hints_used_count

        return response_data
