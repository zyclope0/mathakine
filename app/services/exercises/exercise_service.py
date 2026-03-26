"""
Service pour la gestion des exercices mathématiques.
Implémente les opérations métier liées aux exercices et utilise le transaction manager.
"""

import random
from typing import Any, Dict, List, Optional

from sqlalchemy import String, cast
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.adapter import DatabaseAdapter
from app.exceptions import ExerciseNotFoundError, ExerciseSubmitError
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.schemas.exercise import (
    ExerciseListItem,
    ExerciseListResponse,
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
            Exercise.difficulty_tier,
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
                difficulty_tier=row.difficulty_tier,
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

        return ExerciseListResponse(
            **format_paginated_response(items, total, skip, limit)
        )

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
        from app.core.difficulty_tier import (
            compute_difficulty_tier_for_exercise_strings,
        )

        data = dict(exercise_data)
        if (
            data.get("difficulty_tier") is None
            and data.get("age_group")
            and data.get("difficulty")
        ):
            data["difficulty_tier"] = compute_difficulty_tier_for_exercise_strings(
                data["age_group"], data["difficulty"]
            )
        return DatabaseAdapter.create(db, Exercise, data)

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

        from app.core.difficulty_tier import (
            compute_difficulty_tier_for_exercise_strings,
        )

        edata = dict(exercise_data)
        if "difficulty_tier" not in edata and any(
            k in edata for k in ("difficulty", "age_group")
        ):
            next_age = edata.get("age_group", exercise.age_group)
            next_diff = edata.get("difficulty", exercise.difficulty)
            edata["difficulty_tier"] = compute_difficulty_tier_for_exercise_strings(
                next_age, next_diff
            )
        return DatabaseAdapter.update(db, exercise, edata)

    @staticmethod
    def archive_exercise(db: Session, exercise_id: int) -> None:
        """
        Archive un exercice (marque comme supprimé sans suppression physique).

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à archiver

        Raises:
            ExerciseNotFoundError: Si l'exercice n'existe pas
            DatabaseOperationError: Si l'archivage échoue en base de données
        """
        exercise = ExerciseService.get_exercise(db, exercise_id)
        if not exercise:
            logger.error(f"Exercice avec ID {exercise_id} non trouvé pour archivage")
            raise ExerciseNotFoundError(f"Exercice avec ID {exercise_id} non trouvé")

        DatabaseAdapter.archive(db, exercise)

    @staticmethod
    def delete_exercise(db: Session, exercise_id: int) -> None:
        """
        Supprime physiquement un exercice de la base de données.
        Les tentatives associées sont supprimées en cascade.

        Args:
            db: Session de base de données
            exercise_id: ID de l'exercice à supprimer

        Raises:
            ExerciseNotFoundError: Si l'exercice n'existe pas
            DatabaseOperationError: Si la suppression échoue en base de données
        """
        exercise = ExerciseService.get_exercise(db, exercise_id)
        if not exercise:
            logger.error(f"Exercice avec ID {exercise_id} non trouvé pour suppression")
            raise ExerciseNotFoundError(f"Exercice avec ID {exercise_id} non trouvé")

        DatabaseAdapter.delete(db, exercise)

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
    def record_attempt(
        db: Session, attempt_data: Dict[str, Any], *, auto_commit: bool = True
    ) -> Optional[Attempt]:
        """
        Enregistre une nouvelle tentative pour un exercice.

        Args:
            db: Session de base de données
            attempt_data: Dictionnaire contenant les données de la tentative

        Returns:
            La tentative créée ou None en cas d'erreur
        """
        try:
            # Vérifier que l'exercice existe
            exercise_id = attempt_data.get("exercise_id")
            logger.info(f"Tentative d'enregistrement pour l'exercice {exercise_id}")

            exercise = ExerciseService.get_exercise(db, exercise_id)

            if not exercise:
                logger.error(
                    f"Exercice {exercise_id} introuvable — tentative non enregistrée"
                )
                return None

            logger.info(f"Exercice {exercise_id} trouvé: {exercise.title}")

            # Créer la tentative
            logger.info(f"Création de la tentative avec attempt_data: {attempt_data}")
            attempt = Attempt(**attempt_data)
            db.add(attempt)
            db.flush()
            logger.info(f"Tentative créée avec ID: {attempt.id}")

            # Log de l'action
            is_correct = attempt_data.get("is_correct", False)
            logger.info(
                f"Tentative enregistrée pour l'exercice {exercise_id}: {'Correcte' if is_correct else 'Incorrecte'}"
            )

            if auto_commit:
                db.commit()
                db.refresh(attempt)
            return attempt
        except SQLAlchemyError as attempt_record_error:
            error_type = type(attempt_record_error).__name__
            error_msg = str(attempt_record_error)
            import traceback

            if auto_commit:
                db.rollback()
            logger.error(
                f"❌ ERREUR lors de l'enregistrement de la tentative: {error_type}: {error_msg}"
            )
            logger.error(f"Traceback complet:\n{traceback.format_exc()}")
            return None
