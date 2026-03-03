"""
Service pour la gestion des exercices mathématiques.
Implémente les opérations métier liées aux exercices et utilise le transaction manager.
"""

import random
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import String, cast
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.exceptions import ExerciseNotFoundError, ExerciseSubmitError
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.schemas.exercise import (
    ExerciseListItem,
    ExerciseListResponse,
    SubmitAnswerResponse,
)
from app.utils.json_utils import safe_parse_json
from app.utils.response_formatters import format_paginated_response

logger = get_logger(__name__)


def _exercise_row_to_dict(
    row: Any,
    *,
    include_correct_answer: bool = False,
    include_title: bool = False,
    include_age_group: bool = False,
    include_hint: bool = False,
    include_tags: bool = False,
    include_ai_generated: bool = False,
) -> Dict[str, Any]:
    """
    Mapper row → dict (DRY). Centralise la normalisation enum et safe_parse_json.
    Chaque caller spécifie les champs optionnels à inclure.
    """
    result: Dict[str, Any] = {
        "id": row.id,
        "exercise_type": (
            (row.exercise_type_str or "ADDITION").upper()
            if getattr(row, "exercise_type_str", None)
            else "ADDITION"
        ),
        "difficulty": (
            (row.difficulty_str or "PADAWAN").upper()
            if getattr(row, "difficulty_str", None)
            else "PADAWAN"
        ),
        "choices": safe_parse_json(getattr(row, "choices", None), []),
        "question": getattr(row, "question", ""),
        "explanation": getattr(row, "explanation") or "",
    }
    if include_correct_answer:
        result["correct_answer"] = getattr(row, "correct_answer", "")
    if include_title:
        result["title"] = getattr(row, "title", "")
    if include_age_group:
        result["age_group"] = getattr(row, "age_group", None)
    if include_hint:
        result["hint"] = getattr(row, "hint", None)
    if include_tags:
        result["tags"] = safe_parse_json(getattr(row, "tags", None), [])
    if include_ai_generated:
        result["ai_generated"] = getattr(row, "ai_generated", False) or False
    return result


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
        except SQLAlchemyError as get_exercise_error:
            logger.error(
                f"Erreur lors de la récupération de l'exercice {exercise_id}: {get_exercise_error}"
            )
            # Fallback vers la méthode originale en cas d'erreur
            try:
                return DatabaseAdapter.get_by_id(db, Exercise, exercise_id)
            except SQLAlchemyError:
                return None

    @staticmethod
    def get_exercise_for_api(db: Session, exercise_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un exercice formaté pour l'API publique (sans correct_answer).

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice

        Returns:
            Dictionnaire prêt pour JSONResponse ou None si non trouvé
        """
        try:
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
                    Exercise.age_group,
                    cast(Exercise.exercise_type, String).label("exercise_type_str"),
                    cast(Exercise.difficulty, String).label("difficulty_str"),
                )
                .filter(Exercise.id == exercise_id)
                .first()
            )

            if not exercise_row:
                raise ExerciseNotFoundError()

            return _exercise_row_to_dict(
                exercise_row,
                include_title=True,
                include_age_group=True,
                include_hint=True,
                include_tags=True,
                include_ai_generated=True,
            )
        except ExerciseNotFoundError:
            raise
        except SQLAlchemyError as err:
            logger.error(f"Erreur get_exercise_for_api {exercise_id}: {err}")
            return None

    @staticmethod
    def get_exercise_for_submit_validation(
        db: Session, exercise_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère un exercice pour validation de réponse (submit_answer).
        Inclut correct_answer. Utilise cast() pour éviter les erreurs enum.

        Returns:
            Dict avec id, exercise_type, difficulty, correct_answer, choices, question, explanation
            ou None si non trouvé.
        """
        try:
            exercise_row = (
                db.query(
                    Exercise.id,
                    Exercise.question,
                    Exercise.correct_answer,
                    Exercise.choices,
                    Exercise.explanation,
                    cast(Exercise.exercise_type, String).label("exercise_type_str"),
                    cast(Exercise.difficulty, String).label("difficulty_str"),
                )
                .filter(Exercise.id == exercise_id)
                .first()
            )

            if not exercise_row:
                return None

            return _exercise_row_to_dict(
                exercise_row,
                include_correct_answer=True,
            )
        except SQLAlchemyError as err:
            logger.error(
                f"Erreur get_exercise_for_submit_validation {exercise_id}: {err}"
            )
            return None

    @staticmethod
    def _check_answer_correct(exercise: Dict[str, Any], selected_answer: Any) -> bool:
        """
        Détermine si la réponse est correcte selon le type d'exercice.
        TEXTE/MIXTE : comparaison insensible à la casse ; autres : stricte.
        """
        correct_answer = exercise.get("correct_answer")
        if not correct_answer:
            return False
        text_based = [ExerciseType.TEXTE.value, ExerciseType.MIXTE.value]
        exercise_type = exercise.get("exercise_type", "")
        if exercise_type in text_based:
            return (
                str(selected_answer).lower().strip()
                == str(correct_answer).lower().strip()
            )
        return str(selected_answer).strip() == str(correct_answer).strip()

    @staticmethod
    def submit_answer_result(
        db: Session,
        exercise_id: int,
        user_id: int,
        selected_answer: Any,
        time_spent: float = 0,
    ) -> SubmitAnswerResponse:
        """
        Traite la soumission d'une réponse : validation, enregistrement, badges, streak.
        Retourne SubmitAnswerResponse pour la réponse HTTP.
        Lève ExerciseNotFoundError (404) ou ExerciseSubmitError (500) en cas d'erreur métier.
        """
        from app.services.badge_service import BadgeService
        from app.utils.json_utils import make_json_serializable

        exercise = ExerciseService.get_exercise_for_submit_validation(db, exercise_id)
        if not exercise:
            raise ExerciseNotFoundError()

        correct_answer = exercise.get("correct_answer")
        if not correct_answer:
            logger.error(f"ERREUR: L'exercice {exercise_id} n'a pas de correct_answer")
            raise ExerciseSubmitError(
                500, "L'exercice n'a pas de réponse correcte définie."
            )

        is_correct = ExerciseService._check_answer_correct(exercise, selected_answer)
        logger.debug(
            f"Réponse correcte? {is_correct} "
            f"(selected: '{selected_answer}', correct: '{correct_answer}')"
        )

        attempt_data = {
            "user_id": user_id,
            "exercise_id": exercise_id,
            "user_answer": selected_answer,
            "is_correct": is_correct,
            "time_spent": time_spent,
        }
        attempt_obj = ExerciseService.record_attempt(db, attempt_data)
        if not attempt_obj:
            logger.error("ERREUR: La tentative n'a pas été enregistrée correctement")
            raise ExerciseSubmitError(
                500, "Erreur lors de l'enregistrement de la tentative"
            )

        logger.info("Tentative enregistrée avec succès")

        new_badges = []
        try:
            badge_service = BadgeService(db)
            attempt_for_badges = {
                "exercise_type": exercise.get("exercise_type"),
                "is_correct": is_correct,
                "time_spent": time_spent,
                "exercise_id": exercise_id,
                "created_at": (
                    attempt_obj.created_at.isoformat()
                    if attempt_obj.created_at
                    else None
                ),
            }
            new_badges = badge_service.check_and_award_badges(
                user_id, attempt_for_badges
            )
            if new_badges:
                logger.info(
                    f"🎖️ {len(new_badges)} nouveaux badges attribués "
                    f"à l'utilisateur {user_id}"
                )
        except SQLAlchemyError as e:
            logger.warning(
                "⚠️ Erreur DB lors de la vérification des badges",
                exc_info=True,
            )
        except (TypeError, ValueError) as e:
            logger.warning(
                "⚠️ Erreur de données lors de la vérification des badges",
                exc_info=True,
            )

        try:
            from app.services.streak_service import update_user_streak
        except ImportError:
            logger.warning("Streak service indisponible (ImportError)", exc_info=True)
        else:
            try:
                update_user_streak(db, user_id)
            except SQLAlchemyError:
                logger.debug("Streak update skipped (DB error)", exc_info=True)
            except (TypeError, ValueError):
                logger.debug("Streak update skipped (data/type error)", exc_info=True)

        progress_notif = None
        if not new_badges:
            try:
                progress_notif = badge_service.get_closest_progress_notification(
                    user_id
                )
            except (SQLAlchemyError, TypeError, ValueError):
                logger.debug("Badge progress notification skipped", exc_info=True)
        return SubmitAnswerResponse(
            is_correct=is_correct,
            correct_answer=correct_answer,
            explanation=exercise.get("explanation") or "",
            attempt_id=attempt_obj.id,
            new_badges=make_json_serializable(new_badges) if new_badges else None,
            badges_earned=len(new_badges) if new_badges else None,
            progress_notification=progress_notif,
        )

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

            if exercise_type:
                query = query.filter(Exercise.exercise_type == exercise_type)

            if difficulty:
                query = query.filter(Exercise.difficulty == difficulty)

            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as exercises_fetch_error:
            logger.error(
                f"Erreur lors de la récupération des exercices: {exercises_fetch_error}"
            )
            return []

    @staticmethod
    def _apply_exercise_list_filters(
        query,
        exercise_type: Optional[str],
        age_group: Optional[str],
        search: Optional[str],
        completed_ids_to_exclude: List[int],
    ):
        """
        Applique les filtres communs pour count et select.
        Évite la duplication de logique dans get_exercises_list_for_api.
        """
        from sqlalchemy import or_

        if exercise_type:
            query = query.filter(Exercise.exercise_type == exercise_type)
        if age_group:
            query = query.filter(Exercise.age_group == age_group)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Exercise.title.ilike(search_pattern),
                    Exercise.question.ilike(search_pattern),
                )
            )
        if completed_ids_to_exclude:
            query = query.filter(Exercise.id.notin_(completed_ids_to_exclude))
        return query

    @staticmethod
    def get_exercises_list_for_api(
        db: Session,
        limit: int = 20,
        skip: int = 0,
        exercise_type: Optional[str] = None,
        age_group: Optional[str] = None,
        search: Optional[str] = None,
        order: str = "random",
        hide_completed: bool = False,
        user_id: Optional[int] = None,
    ) -> ExerciseListResponse:
        """
        Liste des exercices pour l'API avec pagination et filtres.

        Returns:
            ExerciseListResponse (DTO) avec items, total, page, limit, hasMore
        """
        from sqlalchemy import String, cast

        from app.models.attempt import Attempt
        from app.utils.json_utils import safe_parse_json

        # IDs à exclure si hide_completed et utilisateur connecté
        completed_ids_to_exclude: List[int] = []
        if hide_completed and user_id:
            subq = (
                db.query(Attempt.exercise_id)
                .filter(
                    Attempt.user_id == user_id,
                    Attempt.is_correct == True,
                )
                .distinct()
                .all()
            )
            completed_ids_to_exclude = [r[0] for r in subq if r[0] is not None]

        # Requête de base pour le count
        count_query = db.query(Exercise).filter(Exercise.is_archived == False)
        count_query = ExerciseService._apply_exercise_list_filters(
            count_query,
            exercise_type,
            age_group,
            search,
            completed_ids_to_exclude,
        )
        total = count_query.count()

        # Requête select avec les mêmes filtres
        exercises_query = db.query(
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
            Exercise.view_count,
            Exercise.created_at,
            cast(Exercise.exercise_type, String).label("exercise_type_str"),
            cast(Exercise.difficulty, String).label("difficulty_str"),
            Exercise.age_group,
        ).filter(Exercise.is_archived == False)
        exercises_query = ExerciseService._apply_exercise_list_filters(
            exercises_query,
            exercise_type,
            age_group,
            search,
            completed_ids_to_exclude,
        )

        if order == "recent":
            exercises_query = (
                exercises_query.order_by(Exercise.created_at.desc())
                .limit(limit)
                .offset(skip)
            )
        else:
            # Optimisation: random_offset au lieu de ORDER BY RANDOM() (O(1) vs O(n))
            max_offset = max(0, total - limit - skip)
            random_offset_val = random.randint(0, max_offset) if max_offset > 0 else 0
            exercises_query = (
                exercises_query.order_by(Exercise.id)
                .offset(skip + random_offset_val)
                .limit(limit)
            )

        rows = exercises_query.all()

        items = [
            ExerciseListItem(
                id=row.id,
                title=row.title,
                exercise_type=(
                    row.exercise_type_str.upper()
                    if row.exercise_type_str
                    else "ADDITION"
                ),
                difficulty=(
                    row.difficulty_str.upper() if row.difficulty_str else "PADAWAN"
                ),
                age_group=row.age_group,
                question=row.question,
                correct_answer=row.correct_answer,
                choices=safe_parse_json(row.choices, []),
                explanation=row.explanation,
                hint=row.hint,
                tags=safe_parse_json(row.tags, []),
                ai_generated=row.ai_generated or False,
                is_active=row.is_active if row.is_active is not None else True,
                view_count=row.view_count or 0,
            )
            for row in rows
        ]

        return ExerciseListResponse(**format_paginated_response(items, total, skip, limit))

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
    def get_user_completed_exercise_ids(db: Session, user_id: int) -> List[int]:
        """
        Récupère les IDs des exercices complétés par un utilisateur (distincts).

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur

        Returns:
            Liste des IDs d'exercices complétés (sans doublons)
        """
        rows = (
            db.query(Attempt.exercise_id)
            .filter(
                Attempt.user_id == user_id,
                Attempt.is_correct == True,
            )
            .distinct()
            .all()
        )
        return [r[0] for r in rows if r[0] is not None]

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

                if not exercise:
                    logger.error(
                        f"Exercice {exercise_id} introuvable — tentative non enregistrée"
                    )
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
                except SQLAlchemyError as stats_error:
                    logger.error(
                        f"Erreur DB lors de la mise à jour des statistiques: {stats_error}"
                    )
                    # Ne pas faire échouer la tentative pour une erreur de stats
                except (TypeError, ValueError) as stats_error:
                    logger.error(
                        f"Erreur de données lors de la mise à jour des statistiques: {stats_error}"
                    )
                    # Ne pas faire échouer la tentative pour une erreur de stats

                return attempt
            except SQLAlchemyError as attempt_record_error:
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

        session.flush()
