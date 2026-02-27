"""
Service pour la gestion des exercices mathématiques.
Implémente les opérations métier liées aux exercices et utilise le transaction manager.
"""

from typing import Any, Dict, List, Optional, Union

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ExerciseSubmitError(Exception):
    """Erreur lors de la soumission d'une réponse (submit_answer)."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


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
            from sqlalchemy import String, cast

            from app.utils.json_utils import safe_parse_json

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
                return None

            return {
                "id": exercise_row.id,
                "title": exercise_row.title,
                "exercise_type": (
                    exercise_row.exercise_type_str.upper()
                    if exercise_row.exercise_type_str
                    else "ADDITION"
                ),
                "difficulty": (
                    exercise_row.difficulty_str.upper()
                    if exercise_row.difficulty_str
                    else "PADAWAN"
                ),
                "age_group": exercise_row.age_group,
                "question": exercise_row.question,
                "choices": safe_parse_json(exercise_row.choices, []),
                "explanation": exercise_row.explanation,
                "hint": exercise_row.hint,
                "tags": safe_parse_json(exercise_row.tags, []),
                "ai_generated": exercise_row.ai_generated or False,
            }
        except Exception as err:
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
            from sqlalchemy import String, cast

            from app.utils.json_utils import safe_parse_json

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

            return {
                "id": exercise_row.id,
                "exercise_type": (
                    exercise_row.exercise_type_str.upper()
                    if exercise_row.exercise_type_str
                    else "ADDITION"
                ),
                "difficulty": (
                    exercise_row.difficulty_str.upper()
                    if exercise_row.difficulty_str
                    else "PADAWAN"
                ),
                "correct_answer": exercise_row.correct_answer,
                "choices": safe_parse_json(exercise_row.choices, []),
                "question": exercise_row.question,
                "explanation": exercise_row.explanation,
            }
        except Exception as err:
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
    ) -> Dict[str, Any]:
        """
        Traite la soumission d'une réponse : validation, enregistrement, badges, streak.
        Retourne le dict response_data pour JSONResponse.
        Lève ExerciseSubmitError en cas d'erreur métier.
        """
        from app.services.badge_service import BadgeService
        from app.utils.json_utils import make_json_serializable

        exercise = ExerciseService.get_exercise_for_submit_validation(db, exercise_id)
        if not exercise:
            raise ExerciseSubmitError(404, "Exercice non trouvé")

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
        except Exception as badge_error:
            logger.warning(
                f"⚠️ Erreur lors de la vérification des badges: {badge_error}"
            )

        try:
            from app.services.streak_service import update_user_streak

            update_user_streak(db, user_id)
        except Exception as streak_err:
            logger.debug(f"Streak update skipped: {streak_err}")

        badge_service = BadgeService(db)
        response_data = {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": exercise.get("explanation", ""),
            "attempt_id": attempt_obj.id,
        }
        if new_badges:
            response_data["new_badges"] = make_json_serializable(new_badges)
            response_data["badges_earned"] = len(new_badges)
        else:
            progress_notif = badge_service.get_closest_progress_notification(user_id)
            if progress_notif:
                response_data["progress_notification"] = progress_notif

        return make_json_serializable(response_data)

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
    ) -> Dict[str, Any]:
        """
        Liste des exercices pour l'API avec pagination et filtres.

        Returns:
            Dict avec items, total, page, limit, hasMore
        """
        from sqlalchemy import String, cast, func, or_

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

        # Requête de base
        query = db.query(Exercise).filter(Exercise.is_archived == False)

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

        total = query.count()

        # Récupérer les exercices avec les mêmes filtres
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

        if exercise_type:
            exercises_query = exercises_query.filter(
                Exercise.exercise_type == exercise_type
            )
        if age_group:
            exercises_query = exercises_query.filter(Exercise.age_group == age_group)
        if search:
            search_pattern = f"%{search}%"
            exercises_query = exercises_query.filter(
                or_(
                    Exercise.title.ilike(search_pattern),
                    Exercise.question.ilike(search_pattern),
                )
            )
        if completed_ids_to_exclude:
            exercises_query = exercises_query.filter(
                Exercise.id.notin_(completed_ids_to_exclude)
            )

        if order == "recent":
            exercises_query = (
                exercises_query.order_by(Exercise.created_at.desc())
                .limit(limit)
                .offset(skip)
            )
        else:
            exercises_query = (
                exercises_query.order_by(func.random()).limit(limit).offset(skip)
            )

        rows = exercises_query.all()

        exercises = []
        for row in rows:
            exercises.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "exercise_type": (
                        row.exercise_type_str.upper()
                        if row.exercise_type_str
                        else "ADDITION"
                    ),
                    "difficulty": (
                        row.difficulty_str.upper() if row.difficulty_str else "PADAWAN"
                    ),
                    "age_group": row.age_group,
                    "question": row.question,
                    "correct_answer": row.correct_answer,
                    "choices": safe_parse_json(row.choices, []),
                    "explanation": row.explanation,
                    "hint": row.hint,
                    "tags": safe_parse_json(row.tags, []),
                    "ai_generated": row.ai_generated,
                    "is_active": row.is_active,
                    "view_count": row.view_count,
                }
            )

        page = (skip // limit) + 1 if limit > 0 else 1
        has_more = (skip + len(exercises)) < total

        return {
            "items": exercises,
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": has_more,
        }

    @staticmethod
    def get_exercises_stats_for_api(db: Session) -> Dict[str, Any]:
        """
        Statistiques globales des exercices et défis pour l'API.
        Thème Académie des Sages.
        """
        import random

        from sqlalchemy import func

        from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt

        # 1. Stats générales
        total_exercises = (
            db.query(func.count(Exercise.id))
            .filter(Exercise.is_active == True)
            .scalar()
            or 0
        )
        total_archived = (
            db.query(func.count(Exercise.id))
            .filter(Exercise.is_archived == True)
            .scalar()
            or 0
        )
        ai_generated_count = (
            db.query(func.count(Exercise.id))
            .filter(Exercise.ai_generated == True, Exercise.is_active == True)
            .scalar()
            or 0
        )

        # 2. Par discipline
        discipline_names = {
            "ADDITION": "Art de l'Addition",
            "SOUSTRACTION": "Maîtrise de la Soustraction",
            "MULTIPLICATION": "Puissance Multiplicative",
            "DIVISION": "Science de la Division",
            "FRACTIONS": "Sagesse des Fractions",
            "GEOMETRIE": "Vision Spatiale",
            "TEXTE": "Énigmes Logiques",
            "MIXTE": "Épreuves Combinées",
            "DIVERS": "Défis Variés",
        }
        by_type_query = (
            db.query(Exercise.exercise_type, func.count(Exercise.id).label("count"))
            .filter(Exercise.is_active == True)
            .group_by(Exercise.exercise_type)
            .all()
        )
        by_discipline = {}
        for ex_type, count in by_type_query:
            type_upper = str(ex_type).upper() if ex_type else "DIVERS"
            by_discipline[type_upper] = {
                "count": count,
                "discipline_name": discipline_names.get(type_upper, type_upper),
                "percentage": (
                    round((count / total_exercises * 100), 1)
                    if total_exercises > 0
                    else 0
                ),
            }

        # 3. Par rang (difficulté)
        academy_ranks = {
            "INITIE": {
                "name": "Initié",
                "description": "Premier pas vers la sagesse",
                "min_age": 6,
            },
            "PADAWAN": {
                "name": "Apprenti",
                "description": "En cours de formation",
                "min_age": 9,
            },
            "CHEVALIER": {
                "name": "Chevalier",
                "description": "Maîtrise confirmée",
                "min_age": 12,
            },
            "MAITRE": {
                "name": "Maître",
                "description": "Sagesse avancée",
                "min_age": 15,
            },
            "GRAND_MAITRE": {
                "name": "Grand Maître",
                "description": "Sommité de l'Académie",
                "min_age": 17,
            },
        }
        by_difficulty_query = (
            db.query(Exercise.difficulty, func.count(Exercise.id).label("count"))
            .filter(Exercise.is_active == True)
            .group_by(Exercise.difficulty)
            .all()
        )
        by_rank = {}
        for diff, count in by_difficulty_query:
            diff_upper = str(diff).upper() if diff else "PADAWAN"
            rank_info = academy_ranks.get(
                diff_upper,
                {"name": diff_upper, "description": "Rang spécial", "min_age": 10},
            )
            by_rank[diff_upper] = {
                "count": count,
                "rank_name": rank_info["name"],
                "description": rank_info["description"],
                "min_age": rank_info["min_age"],
                "percentage": (
                    round((count / total_exercises * 100), 1)
                    if total_exercises > 0
                    else 0
                ),
            }

        # 4. Par groupe d'apprentis (âge)
        apprentice_groups = {
            "6-8": {"name": "Novices", "description": "Futurs espoirs de l'Académie"},
            "8-10": {
                "name": "Apprentis Débutants",
                "description": "En début de formation",
            },
            "9-11": {
                "name": "Apprentis Juniors",
                "description": "Formation intermédiaire",
            },
            "10-12": {
                "name": "Apprentis Confirmés",
                "description": "Prêts pour les épreuves",
            },
            "11-13": {
                "name": "Aspirants Chevaliers",
                "description": "Sur le chemin de la maîtrise",
            },
            "12-14": {"name": "Chevaliers en Devenir", "description": "Défis avancés"},
            "14-16": {
                "name": "Élite de l'Académie",
                "description": "Formation d'excellence",
            },
            "15-17": {"name": "Candidats Maîtres", "description": "Ultimes épreuves"},
            "17+": {"name": "Conseil des Sages", "description": "Niveau Grand Maître"},
        }
        by_age_query = (
            db.query(Exercise.age_group, func.count(Exercise.id).label("count"))
            .filter(Exercise.is_active == True)
            .group_by(Exercise.age_group)
            .all()
        )
        by_apprentice_group = {}
        for age_grp, count in by_age_query:
            group_key = str(age_grp) if age_grp else "10-12"
            group_info = apprentice_groups.get(
                group_key,
                {"name": f"Groupe {group_key}", "description": "Formation spéciale"},
            )
            by_apprentice_group[group_key] = {
                "count": count,
                "group_name": group_info["name"],
                "description": group_info["description"],
                "percentage": (
                    round((count / total_exercises * 100), 1)
                    if total_exercises > 0
                    else 0
                ),
            }

        # 5. Complétion globale
        total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
        correct_attempts = (
            db.query(func.count(Attempt.id)).filter(Attempt.is_correct == True).scalar()
            or 0
        )
        global_success_rate = (
            round((correct_attempts / total_attempts * 100), 1)
            if total_attempts > 0
            else 0
        )

        popular_query = (
            db.query(
                Exercise.id,
                Exercise.title,
                Exercise.exercise_type,
                Exercise.difficulty,
                func.count(Attempt.id).label("attempt_count"),
            )
            .join(Attempt, Attempt.exercise_id == Exercise.id)
            .filter(Exercise.is_active == True)
            .group_by(
                Exercise.id, Exercise.title, Exercise.exercise_type, Exercise.difficulty
            )
            .order_by(func.count(Attempt.id).desc())
            .limit(5)
            .all()
        )
        popular_challenges = []
        for ex_id, title, ex_type, diff, attempt_count in popular_query:
            type_upper = str(ex_type).upper() if ex_type else "DIVERS"
            popular_challenges.append(
                {
                    "id": ex_id,
                    "title": title,
                    "discipline": discipline_names.get(type_upper, type_upper),
                    "rank": academy_ranks.get(str(diff).upper(), {}).get("name", diff),
                    "apprentices_trained": attempt_count,
                }
            )

        # 6. Stats défis logiques
        total_logic_challenges = (
            db.query(func.count(LogicChallenge.id))
            .filter(LogicChallenge.is_archived == False)
            .scalar()
            or 0
        )
        total_challenge_attempts = (
            db.query(func.count(LogicChallengeAttempt.id)).scalar() or 0
        )
        correct_challenge_attempts = (
            db.query(func.count(LogicChallengeAttempt.id))
            .filter(LogicChallengeAttempt.is_correct == True)
            .scalar()
            or 0
        )
        challenge_success_rate = (
            round((correct_challenge_attempts / total_challenge_attempts * 100), 1)
            if total_challenge_attempts > 0
            else 0
        )

        # 7. Construire la réponse
        total_ai_generated = ai_generated_count + total_logic_challenges
        total_content = total_exercises + total_logic_challenges

        def _mastery_msg(rate):
            if rate >= 90:
                return "L'Académie forme d'excellents mathématiciens ! La sagesse règne ici."
            if rate >= 75:
                return "Belle progression des apprentis. Le Conseil est satisfait."
            if rate >= 60:
                return "Les apprentis progressent. La patience est une vertu des sages."
            if rate >= 40:
                return "L'entraînement doit s'intensifier. La voie de la maîtrise est exigeante."
            return (
                "Beaucoup reste à apprendre. Persévérance et courage sont essentiels."
            )

        wisdoms = [
            "La connaissance est le premier pas vers la sagesse. — Les Anciens",
            "Fais-le, ou ne le fais pas. L'hésitation est l'ennemi du progrès. — Proverbe des Maîtres",
            "L'erreur est le chemin de l'apprentissage. — Sagesse ancestrale",
            "Celui qui pose des questions ne s'égare jamais. — Dicton des Sages",
            "L'apprentissage est une voie sans fin. — Chroniques de l'Académie",
            "La patience transforme l'apprenti en maître. — Conseil des Sages",
            "Chaque problème résolu ouvre la porte à de nouveaux défis. — Tradition mathématique",
            "La persévérance est l'arme secrète du mathématicien. — Archives de l'Académie",
        ]

        return {
            "archive_status": "Chroniques accessibles",
            "academy_statistics": {
                "total_exercises": total_exercises,
                "total_challenges": total_logic_challenges,
                "total_content": total_content,
                "archived_exercises": total_archived,
                "ai_generated": total_ai_generated,
                "ai_generated_exercises": ai_generated_count,
                "ai_generated_challenges": total_logic_challenges,
                "ai_generated_percentage": (
                    round((total_ai_generated / total_content * 100), 1)
                    if total_content > 0
                    else 0
                ),
            },
            "by_discipline": by_discipline,
            "by_rank": by_rank,
            "by_apprentice_group": by_apprentice_group,
            "global_performance": {
                "total_attempts": total_attempts + total_challenge_attempts,
                "exercise_attempts": total_attempts,
                "challenge_attempts": total_challenge_attempts,
                "successful_attempts": correct_attempts + correct_challenge_attempts,
                "mastery_rate": global_success_rate,
                "challenge_mastery_rate": challenge_success_rate,
                "message": _mastery_msg(global_success_rate),
            },
            "legendary_challenges": popular_challenges,
            "sage_wisdom": random.choice(wisdoms),
        }

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
