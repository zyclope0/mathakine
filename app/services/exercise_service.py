"""
Service pour la gestion des exercices mathématiques.
Implémente les opérations métier liées aux exercices et utilise le transaction manager.
"""

from typing import Any, Dict, List, Optional, Union

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType


class ExerciseService:
    """
    Service pour la gestion des exercices mathématiques.
    Fournit des méthodes pour récupérer, créer, modifier et supprimer des exercices.
    """

    @staticmethod
    def get_exercise(db: Session, exercise_id: int) -> Optional[Exercise]:
        """
        Récupère un exercice par son ID.

        IMPORTANT: Utilise cast() pour charger les enums en tant que strings
        pour éviter les erreurs LookupError avec les valeurs en minuscules dans la DB.

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à récupérer

        Returns:
            L'exercice correspondant à l'ID ou None s'il n'existe pas
        """
        try:
            from sqlalchemy import String, cast

            # Charger les enums en tant que strings pour éviter les erreurs de conversion
            exercise_row = (
                db.query(
                    Exercise.id,
                    Exercise.title,
                    Exercise.question,
                    Exercise.correct_answer,
                    Exercise.choices,
                    Exercise.explanation,
                    Exercise.hint,
                    Exercise.tags,
                    Exercise.ai_generated,
                    Exercise.is_active,
                    Exercise.is_archived,
                    Exercise.view_count,
                    Exercise.created_at,
                    Exercise.updated_at,
                    cast(Exercise.exercise_type, String).label("exercise_type_str"),
                    cast(Exercise.difficulty, String).label("difficulty_str"),
                )
                .filter(Exercise.id == exercise_id)
                .first()
            )

            if not exercise_row:
                return None

            # Créer un objet Exercise avec les valeurs normalisées
            exercise = Exercise()
            exercise.id = exercise_row.id
            exercise.title = exercise_row.title
            exercise.question = exercise_row.question
            exercise.correct_answer = exercise_row.correct_answer
            exercise.choices = exercise_row.choices
            exercise.explanation = exercise_row.explanation
            exercise.hint = exercise_row.hint
            exercise.tags = exercise_row.tags
            exercise.ai_generated = exercise_row.ai_generated
            exercise.is_active = exercise_row.is_active
            exercise.is_archived = exercise_row.is_archived
            exercise.view_count = exercise_row.view_count
            exercise.created_at = exercise_row.created_at
            exercise.updated_at = exercise_row.updated_at

            # Convertir les strings normalisées en enums (en majuscules)
            from app.models.exercise import DifficultyLevel, ExerciseType

            exercise_type_normalized = (
                exercise_row.exercise_type_str.upper()
                if exercise_row.exercise_type_str
                else "ADDITION"
            )
            difficulty_normalized = (
                exercise_row.difficulty_str.upper()
                if exercise_row.difficulty_str
                else "PADAWAN"
            )

            try:
                exercise.exercise_type = ExerciseType(exercise_type_normalized)
            except ValueError:
                logger.warning(
                    f"Type d'exercice invalide: {exercise_type_normalized}, utilisation de ADDITION par défaut"
                )
                exercise.exercise_type = ExerciseType.ADDITION

            try:
                exercise.difficulty = DifficultyLevel(difficulty_normalized)
            except ValueError:
                logger.warning(
                    f"Difficulté invalide: {difficulty_normalized}, utilisation de PADAWAN par défaut"
                )
                exercise.difficulty = DifficultyLevel.PADAWAN

            return exercise
        except Exception as get_exercise_error:
            logger.error(
                f"Erreur lors de la récupération de l'exercice {exercise_id}: {get_exercise_error}"
            )
            # Fallback vers la méthode originale en cas d'erreur
            try:
                return DatabaseAdapter.get_by_id(db, Exercise, exercise_id)
            except Exception:
                return None

    @staticmethod
    def list_exercises(
        db: Session,
        exercise_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
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
                Exercise.is_archived == False, Exercise.is_active == True
            )

            # FILTRE CRITIQUE : Accepter les valeurs en majuscules ET minuscules
            # pour compatibilité avec les données existantes
            valid_types = [t.value for t in ExerciseType]
            valid_difficulties = [d.value for d in DifficultyLevel]

            # Ajouter les valeurs en minuscules pour compatibilité
            valid_types.extend(
                ["addition", "subtraction", "multiplication", "division", "mixed"]
            )
            valid_difficulties.extend(["initie", "padawan", "chevalier", "maitre"])

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
        except Exception as exercises_fetch_error:
            logger.error(
                f"Erreur lors de la récupération des exercices: {exercises_fetch_error}"
            )
            return []

    @staticmethod
    def create_exercise(
        db: Session, exercise_data: Dict[str, Any]
    ) -> Optional[Exercise]:
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
    def update_exercise(
        db: Session, exercise_id: int, exercise_data: Dict[str, Any]
    ) -> bool:
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
                logger.info(f"Tentative d'enregistrement pour l'exercice {exercise_id}")

                exercise = ExerciseService.get_exercise(session, exercise_id)

                # Si SQLAlchemy ne trouve pas l'exercice, essayer avec PostgreSQL direct
                if not exercise:
                    logger.warning(
                        f"SQLAlchemy n'a pas trouvé l'exercice {exercise_id}, tentative avec PostgreSQL direct"
                    )
                    try:
                        # NOTE: exercise_service_translations archivé - fallback désactivé
                        logger.error(f"Exercice {exercise_id} introuvable en base")
                        exercise_dict = None
                        if exercise_dict:
                            logger.info(
                                f"Exercice {exercise_id} trouvé via PostgreSQL direct"
                            )
                            # Utiliser get_exercise qui gère correctement les enums
                            exercise = ExerciseService.get_exercise(
                                session, exercise_id
                            )
                    except Exception as pg_error:
                        logger.error(
                            f"Erreur lors de la récupération PostgreSQL directe: {pg_error}"
                        )

                if not exercise:
                    logger.error(
                        f"Tentative d'enregistrement d'une tentative pour un exercice inexistant (ID {exercise_id})"
                    )
                    # Essayer de vérifier si l'exercice existe vraiment en BDD avec une requête directe
                    from server.database import get_db_connection

                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            "SELECT id FROM exercises WHERE id = %s", (exercise_id,)
                        )
                        exists = cursor.fetchone()
                        if exists:
                            logger.warning(
                                f"L'exercice {exercise_id} existe en BDD mais n'est pas trouvé par SQLAlchemy ORM"
                            )
                            # Forcer le refresh de la session SQLAlchemy et utiliser get_exercise qui gère les enums
                            session.expire_all()
                            exercise = ExerciseService.get_exercise(
                                session, exercise_id
                            )
                            if not exercise:
                                logger.error(
                                    f"Impossible de charger l'exercice {exercise_id} même après refresh"
                                )
                                return None
                        else:
                            logger.error(
                                f"L'exercice {exercise_id} n'existe vraiment pas en BDD"
                            )
                            return None
                    finally:
                        cursor.close()
                        conn.close()

                if not exercise:
                    return None

                logger.info(f"Exercice {exercise_id} trouvé: {exercise.title}")

                # Créer la tentative
                logger.info(
                    f"Création de la tentative avec attempt_data: {attempt_data}"
                )
                attempt = Attempt(**attempt_data)
                session.add(attempt)
                session.flush()
                logger.info(f"Tentative créée avec ID: {attempt.id}")

                # Log de l'action
                is_correct = attempt_data.get("is_correct", False)
                logger.info(
                    f"Tentative enregistrée pour l'exercice {exercise_id}: {'Correcte' if is_correct else 'Incorrecte'}"
                )

                # 🔥 CORRECTION CRITIQUE : Mettre à jour les statistiques utilisateur
                try:
                    ExerciseService._update_user_statistics(
                        session, attempt_data, exercise
                    )
                    logger.info(
                        f"Statistiques mises à jour pour l'utilisateur {attempt_data.get('user_id')}"
                    )
                except Exception as stats_error:
                    logger.error(
                        f"Erreur lors de la mise à jour des statistiques: {stats_error}"
                    )
                    # Ne pas faire échouer la tentative pour une erreur de stats

                return attempt
            except Exception as attempt_record_error:
                error_type = type(attempt_record_error).__name__
                error_msg = str(attempt_record_error)
                import traceback

                logger.error(
                    f"❌ ERREUR lors de l'enregistrement de la tentative: {error_type}: {error_msg}"
                )
                logger.error(f"Traceback complet:\n{traceback.format_exc()}")
                return None

    @staticmethod
    def _update_user_statistics(
        session: Session,
        attempt_data: Dict[str, Any],
        exercise: Union[Exercise, Dict[str, Any], None],
    ) -> None:
        """
        Met à jour les statistiques utilisateur après une tentative.

        Args:
            session: Session de base de données
            attempt_data: Données de la tentative
            exercise: Exercice concerné (objet Exercise, dict, ou None)
        """
        from datetime import datetime

        from app.models.legacy_tables import UserStats
        from app.models.progress import Progress

        user_id = attempt_data.get("user_id")
        is_correct = attempt_data.get("is_correct", False)
        time_spent = attempt_data.get("time_spent", 0)

        # Extraire exercise_type et difficulty depuis exercise (objet ou dict)
        if exercise is None:
            logger.warning("Aucun exercice fourni pour mettre à jour les statistiques")
            return

        if isinstance(exercise, dict):
            exercise_type = exercise.get("exercise_type")
            difficulty = exercise.get("difficulty")
        else:
            exercise_type = exercise.exercise_type
            difficulty = exercise.difficulty

        if not exercise_type:
            logger.warning(
                f"Impossible de déterminer le type d'exercice pour les statistiques"
            )
            return

        # 1. Mettre à jour ou créer Progress
        progress = (
            session.query(Progress)
            .filter(
                Progress.user_id == user_id, Progress.exercise_type == exercise_type
            )
            .first()
        )

        if progress:
            progress.total_attempts += 1
            if is_correct:
                progress.correct_attempts += 1
                progress.streak += 1
                if progress.streak > progress.highest_streak:
                    progress.highest_streak = progress.streak
            else:
                progress.streak = 0

            # Mettre à jour le temps moyen
            if progress.average_time is None:
                progress.average_time = time_spent
            else:
                total_time = (
                    progress.average_time * (progress.total_attempts - 1) + time_spent
                )
                progress.average_time = total_time / progress.total_attempts

            progress.completion_rate = progress.calculate_completion_rate()
            progress.update_mastery_level()
        else:
            new_progress = Progress(
                user_id=user_id,
                exercise_type=exercise_type,
                difficulty=difficulty if difficulty else "initie",
                total_attempts=1,
                correct_attempts=1 if is_correct else 0,
                average_time=time_spent,
                streak=1 if is_correct else 0,
                highest_streak=1 if is_correct else 0,
            )
            session.add(new_progress)

        # 2. Mettre à jour ou créer UserStats dans une session SÉPARÉE pour éviter
        #    de contaminer la transaction principale (table legacy, peut être absente)
        try:
            from sqlalchemy.orm import sessionmaker

            aux_factory = sessionmaker(autocommit=False, autoflush=False)
            aux_session = aux_factory(bind=session.get_bind())
            try:
                result = aux_session.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name='user_stats'"
                    )
                )
                if not result.scalar():
                    logger.debug("Table user_stats absente, ignorée")
                else:
                    ex_type_val = (
                        exercise_type.value
                        if hasattr(exercise_type, "value")
                        else str(exercise_type)
                    )
                    diff_val = (
                        difficulty.value
                        if hasattr(difficulty, "value")
                        else str(difficulty) or "initie"
                    )
                    user_stat = (
                        aux_session.query(UserStats)
                        .filter(
                            UserStats.exercise_type == ex_type_val,
                            UserStats.difficulty == diff_val,
                        )
                        .first()
                    )
                    if user_stat:
                        user_stat.total_attempts += 1
                        if is_correct:
                            user_stat.correct_attempts += 1
                        user_stat.last_updated = datetime.now()
                    else:
                        aux_session.add(
                            UserStats(
                                exercise_type=ex_type_val,
                                difficulty=diff_val,
                                total_attempts=1,
                                correct_attempts=1 if is_correct else 0,
                            )
                        )
                    aux_session.commit()
            finally:
                aux_session.close()
        except Exception as user_stats_err:
            logger.debug("UserStats ignoré: %s", user_stats_err)

        session.flush()
