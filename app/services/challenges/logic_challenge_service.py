"""
Service pour la gestion des défis de logique mathématique (Épreuves du Conseil Jedi).
Implémente les opérations métier liées aux défis logiques et utilise le transaction manager.
"""

from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.difficulty_tier import compute_difficulty_tier_for_logic_challenge
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
            query = db.query(LogicChallenge).filter(LogicChallenge.is_archived.is_(False))

            if challenge_type:
                # Adapter le type de défi pour le moteur de base de données actuel
                adapted_type = adapt_enum_for_db(
                    "LogicChallengeType", challenge_type, db
                )
                logger.debug(
                    "Type de défi adapté: de '%s' à '%s'", challenge_type, adapted_type
                )
                query = query.filter(LogicChallenge.challenge_type == adapted_type)

            if age_group:
                # Adapter le groupe d'âge pour le moteur de base de données actuel
                adapted_age = adapt_enum_for_db("AgeGroup", age_group, db)
                logger.debug(
                    "Groupe d'âge adapté: de '%s' à '%s'", age_group, adapted_age
                )
                query = query.filter(LogicChallenge.age_group == adapted_age)

            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as challenges_fetch_error:
            logger.error(
                "Erreur lors de la récupération des défis: %s", challenges_fetch_error
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
                "Type de défi adapté: de '%s' à '%s'",
                challenge_type,
                challenge_data["challenge_type"],
            )

        if "age_group" in challenge_data:
            age_group = challenge_data["age_group"]
            challenge_data["age_group"] = adapt_enum_for_db("AgeGroup", age_group, db)
            logger.debug(
                "Groupe d'âge adapté: de '%s' à '%s'",
                age_group,
                challenge_data["age_group"],
            )

        # Définir explicitement created_at si non présent pour éviter les valeurs NULL
        from datetime import datetime, timezone

        if (
            "created_at" not in challenge_data
            or challenge_data.get("created_at") is None
        ):
            challenge_data["created_at"] = datetime.now(timezone.utc)

        from app.core.difficulty_tier import compute_difficulty_tier_for_logic_challenge

        data = dict(challenge_data)
        if data.get("difficulty_tier") is None:
            data["difficulty_tier"] = compute_difficulty_tier_for_logic_challenge(
                data.get("age_group"),
                data.get("difficulty"),
                data.get("difficulty_rating"),
            )
        return DatabaseAdapter.create(db, LogicChallenge, data)

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
            logger.error("Défi avec ID %s non trouvé pour mise à jour", challenge_id)
            return False

        # Adapter les valeurs d'enum pour le moteur de base de données actuel
        if "challenge_type" in challenge_data:
            challenge_type = challenge_data["challenge_type"]
            challenge_data["challenge_type"] = adapt_enum_for_db(
                "LogicChallengeType", challenge_type, db
            )
            logger.debug(
                "Type de défi adapté pour mise à jour: de '%s' à '%s'",
                challenge_type,
                challenge_data["challenge_type"],
            )

        if "age_group" in challenge_data:
            age_group = challenge_data["age_group"]
            challenge_data["age_group"] = adapt_enum_for_db("AgeGroup", age_group, db)
            logger.debug(
                "Groupe d'âge adapté pour mise à jour: de '%s' à '%s'",
                age_group,
                challenge_data["age_group"],
            )

        edata = dict(challenge_data)
        if "difficulty_tier" not in edata and any(
            k in edata for k in ("difficulty", "age_group", "difficulty_rating")
        ):
            next_age = edata.get("age_group", challenge.age_group)
            next_diff = edata.get("difficulty", challenge.difficulty)
            next_rating = edata.get("difficulty_rating", challenge.difficulty_rating)
            edata["difficulty_tier"] = compute_difficulty_tier_for_logic_challenge(
                next_age, next_diff, next_rating
            )
        return DatabaseAdapter.update(db, challenge, edata)

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
            logger.error("Défi avec ID %s non trouvé pour archivage", challenge_id)
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
            logger.error("Défi avec ID %s non trouvé pour suppression", challenge_id)
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
                    "Tentative d'enregistrement d'une tentative pour un défi inexistant (ID %s)",
                    challenge_id,
                )
                return None

            # Créer la tentative
            attempt = LogicChallengeAttempt(**attempt_data)
            db.add(attempt)
            db.flush()

            # Log de l'action
            is_correct = attempt_data.get("is_correct", False)
            logger.info(
                "Tentative enregistrée pour le défi %s: %s",
                challenge_id,
                "Correcte" if is_correct else "Incorrecte",
            )

            if auto_commit:
                db.commit()
                db.refresh(attempt)
            return attempt
        except SQLAlchemyError as attempt_save_error:
            if auto_commit:
                db.rollback()
            logger.error(
                "Erreur lors de l'enregistrement de la tentative: %s",
                attempt_save_error,
            )
            return None
        except (TypeError, ValueError) as attempt_save_error:
            if auto_commit:
                db.rollback()
            logger.error(
                "Erreur de données lors de l'enregistrement de la tentative: %s",
                attempt_save_error,
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
    ):
        """
        Délègue à challenge_attempt_service (LOT 2.1).
        Retourne SubmitChallengeAttemptResult (LOT B1).
        Conservé pour compatibilité avec appelants synchrones (tests, etc.).
        """
        from app.services.challenges.challenge_attempt_service import (
            submit_challenge_attempt_sync,
        )

        return submit_challenge_attempt_sync(
            db, challenge_id, user_id, user_solution, time_spent, hints_used_count
        )
