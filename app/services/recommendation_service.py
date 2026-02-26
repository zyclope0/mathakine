from datetime import datetime, timedelta, timezone
from typing import Tuple

from sqlalchemy import and_, exists, or_
from sqlalchemy.sql import func

from app.core.constants import AgeGroups, get_difficulty_from_age_group
from app.core.logging_config import get_logger
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeAttempt
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.user import User

logger = get_logger(__name__)

# Mapping grade_level → age_group (quand preferred_difficulty vide)
# Approximation : suisse 1H-11H, unifié 1-12
_GRADE_TO_AGE_GROUP = {
    (1, 3): AgeGroups.GROUP_6_8,  # CP-CE2
    (4, 6): AgeGroups.GROUP_9_11,  # CM1-6e
    (7, 9): AgeGroups.GROUP_12_14,  # 5e-3e
    (10, 12): AgeGroups.GROUP_15_17,  # Lycée
}


class RecommendationService:
    """Service analysant les performances et générant des recommandations personnalisées"""

    @staticmethod
    def _get_user_context(user) -> Tuple[str, str, str, str]:
        """
        Extrait le contexte utilisateur (onboarding + profil) pour les recommandations.

        Returns:
            (age_group, default_difficulty, learning_goal, practice_rhythm)
        """
        # preferred_difficulty stocke le groupe d'âge (6-8, 9-11, etc.) depuis l'onboarding
        age_group = None
        if getattr(user, "preferred_difficulty", None):
            val = str(user.preferred_difficulty).lower().strip()
            if val in (
                AgeGroups.GROUP_6_8,
                AgeGroups.GROUP_9_11,
                AgeGroups.GROUP_12_14,
                AgeGroups.GROUP_15_17,
                AgeGroups.ADULT,
                AgeGroups.ALL_AGES,
            ):
                age_group = val
            elif val in ("6-8", "9-11", "12-14", "15-17", "adulte", "tous-ages"):
                age_group = val

        # Fallback : dériver du grade_level
        if not age_group and getattr(user, "grade_level", None) is not None:
            try:
                gl = int(user.grade_level)
                for (lo, hi), ag in _GRADE_TO_AGE_GROUP.items():
                    if lo <= gl <= hi:
                        age_group = ag
                        break
            except (TypeError, ValueError):
                pass

        # Sans onboarding/profil : ne pas filtrer par âge (tous-ages = large)
        age_group = age_group or AgeGroups.ALL_AGES
        default_difficulty = get_difficulty_from_age_group(age_group)
        learning_goal = getattr(user, "learning_goal", None) or ""
        practice_rhythm = getattr(user, "practice_rhythm", None) or ""
        return age_group, default_difficulty, learning_goal, practice_rhythm

    @staticmethod
    def generate_recommendations(db, user_id):
        """Génère des recommandations pour un utilisateur basé sur ses performances

        Args:
            db: Session SQLAlchemy
            user_id: ID de l'utilisateur

        Returns:
            list: Liste des recommandations générées
        """
        try:
            # Récupérer les données utilisateur
            user_exists = db.query(exists().where(User.id == user_id)).scalar()
            if not user_exists:
                logger.warning(
                    f"Tentative de génération de recommandations pour un utilisateur inexistant: {user_id}"
                )
                return []

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"Utilisateur {user_id} non trouvé")
                return []

            # Contexte onboarding/profil pour personnalisation
            user_age_group, user_default_difficulty, learning_goal, practice_rhythm = (
                RecommendationService._get_user_context(user)
            )
            logger.debug(
                f"Recommandations user {user_id}: age_group={user_age_group}, "
                f"default_difficulty={user_default_difficulty}, goal={learning_goal}"
            )

            # Récupérer les stats récentes (30 derniers jours) pour mieux cibler
            from app.services.user_service import UserService

            recent_stats = UserService.get_user_stats(db, user_id, time_range="30")
            performance_by_type = recent_stats.get("by_exercise_type", {})

            # Analyser les performances récentes
            progress_records = (
                db.query(Progress).filter(Progress.user_id == user_id).all()
            )
            recent_attempts = (
                db.query(Attempt)
                .filter(
                    Attempt.user_id == user_id,
                    Attempt.created_at
                    > datetime.now(timezone.utc) - timedelta(days=30),
                )
                .order_by(Attempt.created_at.desc())
                .limit(50)
                .all()
            )

            # Exercices déjà réussis (toutes périodes) — ne pas recommander
            all_completed_exercise_ids = {
                a.exercise_id
                for a in db.query(Attempt)
                .filter(
                    Attempt.user_id == user_id,
                    Attempt.is_correct == True,
                    Attempt.exercise_id.isnot(None),
                )
                .all()
                if a.exercise_id
            }

            # Supprimer les anciennes recommandations non complétées
            db.query(Recommendation).filter(
                Recommendation.user_id == user_id, Recommendation.is_completed == False
            ).delete()

            # Générer de nouvelles recommandations
            recommendations = []

            # 1. Recommandations basées sur les domaines à améliorer (utilisant les stats récentes)
            # Prioriser les types avec faible taux de réussite récent
            for ex_type_key, type_stats in performance_by_type.items():
                # Normaliser le type d'exercice (peut être en minuscules depuis SQL)
                ex_type = str(ex_type_key).lower()
                success_rate = type_stats.get("success_rate", 0)
                total = type_stats.get("total", 0)

                # Seulement recommander si au moins 3 tentatives récentes pour avoir des données fiables
                if total >= 3 and success_rate < 70:
                    # Déterminer la priorité selon le taux de réussite + objectif (learning_goal)
                    if success_rate < 50:
                        priority = 9  # Urgent
                        reason = f"Votre taux de réussite en {ex_type} est de {success_rate}%. Continuons à progresser !"
                    else:
                        priority = 8  # Important
                        reason = f"Pour améliorer votre taux de réussite en {ex_type} ({success_rate}%)"
                    if learning_goal == "preparer_exam":
                        priority = min(10, priority + 1)  # Prioriser en vue d'un examen

                    # Trouver le niveau de difficulté le plus approprié
                    # Utiliser le niveau le plus pratiqué récemment ou le niveau actuel du Progress
                    target_difficulty = None
                    for progress in progress_records:
                        if str(progress.exercise_type).lower() == ex_type:
                            target_difficulty = progress.difficulty
                            break

                    if not target_difficulty:
                        target_difficulty = user_default_difficulty

                    # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                    valid_types = [t.value for t in ExerciseType]
                    valid_difficulties = [d.value for d in DifficultyLevel]

                    # Trouver des exercices appropriés (filtrer par age_group si dispo)
                    exercise_query = db.query(Exercise).filter(
                        func.lower(Exercise.exercise_type) == ex_type,
                        Exercise.difficulty == target_difficulty,
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties),
                        Exercise.is_archived == False,
                        Exercise.is_active == True,
                    )
                    # Cibler le groupe d'âge utilisateur (sauf tous-ages = pas de filtre)
                    if user_age_group != AgeGroups.ALL_AGES:
                        age_values = list(
                            AgeGroups.AGE_ALIASES.get(user_age_group, [user_age_group])
                        )
                        age_values = [str(v).lower() for v in age_values]
                        age_values.extend(["tous-ages", "tous ages", "all_ages"])
                        exercise_query = exercise_query.filter(
                            func.lower(Exercise.age_group).in_(age_values)
                        )

                    # Exclure les exercices déjà réussis
                    if all_completed_exercise_ids:
                        exercise_query = exercise_query.filter(
                            ~Exercise.id.in_(list(all_completed_exercise_ids))
                        )

                    exercises = exercise_query.order_by(func.random()).limit(2).all()

                    for ex in exercises:
                        # Exclure si l'utilisateur a déjà réussi cet exercice
                        if ex.id not in all_completed_exercise_ids:
                            recommendations.append(
                                Recommendation(
                                    user_id=user_id,
                                    exercise_type=ex.exercise_type,
                                    difficulty=ex.difficulty,
                                    exercise_id=ex.id,
                                    priority=priority,
                                    reason=reason,
                                )
                            )

            # 2. Recommandations pour monter en niveau (progression) - basé sur stats récentes
            for ex_type_key, type_stats in performance_by_type.items():
                # Normaliser le type d'exercice
                ex_type = str(ex_type_key).lower()
                success_rate = type_stats.get("success_rate", 0)
                total = type_stats.get("total", 0)

                # Si taux de réussite > 85% avec au moins 5 tentatives récentes, proposer niveau supérieur
                if total >= 5 and success_rate > 85:
                    # Trouver le niveau actuel depuis Progress
                    current_difficulty = None
                    for progress in progress_records:
                        if str(progress.exercise_type).lower() == ex_type:
                            current_difficulty = progress.difficulty
                            break

                    if not current_difficulty:
                        continue  # Pas de niveau trouvé, passer au suivant

                    # Proposer des exercices du niveau supérieur
                    next_difficulty = RecommendationService._get_next_difficulty(
                        current_difficulty
                    )
                    if next_difficulty:
                        # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                        valid_types = [t.value for t in ExerciseType]
                        valid_difficulties = [d.value for d in DifficultyLevel]

                        # Normaliser ex_type pour la comparaison
                        exercise_type_filter = ex_type
                        for enum_type in ExerciseType:
                            if enum_type.value.lower() == ex_type:
                                exercise_type_filter = enum_type.value
                                break

                        exercise_query = db.query(Exercise).filter(
                            func.lower(Exercise.exercise_type) == ex_type,
                            Exercise.difficulty == next_difficulty,
                            Exercise.exercise_type.in_(valid_types),
                            Exercise.difficulty.in_(valid_difficulties),
                            Exercise.is_archived == False,
                            Exercise.is_active == True,
                        )

                        # Exclure les exercices déjà réussis
                        if all_completed_exercise_ids:
                            exercise_query = exercise_query.filter(
                                ~Exercise.id.in_(list(all_completed_exercise_ids))
                            )

                        exercises = (
                            exercise_query.order_by(func.random()).limit(1).all()
                        )

                        for ex in exercises:
                            if ex.id not in all_completed_exercise_ids:
                                recommendations.append(
                                    Recommendation(
                                        user_id=user_id,
                                        exercise_type=ex.exercise_type,
                                        difficulty=ex.difficulty,
                                        exercise_id=ex.id,
                                        priority=7,
                                        reason=f"Excellent ! Vous avez {success_rate}% de réussite en {ex.exercise_type}. Essayons le niveau {next_difficulty} !",
                                    )
                                )

            # 3. Recommandations pour maintenir les compétences (réactivation)
            # Trouver les compétences non pratiquées récemment
            # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides dès le départ
            valid_types = [t.value for t in ExerciseType]
            valid_difficulties = [d.value for d in DifficultyLevel]

            all_exercise_types = (
                db.query(Exercise.exercise_type)
                .filter(
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                )
                .distinct()
                .all()
            )

            for ex_type in all_exercise_types:
                ex_type = ex_type[0]  # Extraction du tuple
                # Vérifier si ce type d'exercice a été pratiqué récemment
                # Utiliser une requête filtrée pour éviter les erreurs d'énumération
                recent_type_attempts = []
                for a in recent_attempts:
                    exercise = (
                        db.query(Exercise)
                        .filter(
                            Exercise.id == a.exercise_id,
                            Exercise.exercise_type.in_(valid_types),
                            Exercise.difficulty.in_(valid_difficulties),
                        )
                        .first()
                    )
                    if exercise and exercise.exercise_type == ex_type:
                        recent_type_attempts.append(a)

                if not recent_type_attempts:
                    # Trouver le niveau le plus élevé maîtrisé par l'utilisateur pour ce type
                    user_level = None
                    for p in progress_records:
                        if (
                            p.exercise_type == ex_type
                            and p.calculate_completion_rate() > 70
                        ):
                            user_level = p.difficulty

                    # Si aucun niveau trouvé, utiliser le niveau du profil/onboarding
                    if not user_level:
                        user_level = user_default_difficulty

                    # Proposer un exercice pour maintenir cette compétence
                    ex_filter = [
                        Exercise.exercise_type == ex_type,
                        Exercise.difficulty == user_level,
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties),
                        Exercise.is_archived == False,
                        Exercise.is_active == True,
                    ]
                    if user_age_group != AgeGroups.ALL_AGES:
                        age_values = list(
                            AgeGroups.AGE_ALIASES.get(user_age_group, [user_age_group])
                        )
                        age_values = [str(v).lower() for v in age_values]
                        age_values.extend(["tous-ages", "tous ages", "all_ages"])
                        ex_filter.append(func.lower(Exercise.age_group).in_(age_values))
                    exercises = (
                        db.query(Exercise)
                        .filter(*ex_filter)
                        .order_by(func.random())
                        .limit(1)
                        .all()
                    )

                    for ex in exercises:
                        # Exclure les exercices déjà réussis
                        if ex.id not in all_completed_exercise_ids:
                            recommendations.append(
                                Recommendation(
                                    user_id=user_id,
                                    exercise_type=ex.exercise_type,
                                    difficulty=ex.difficulty,
                                    exercise_id=ex.id,
                                    priority=5,
                                    reason=f"Pour maintenir vos compétences en {ex.exercise_type}",
                                )
                            )

            # 4. Recommandations de découverte (nouveaux types d'exercices)
            practised_types = set([p.exercise_type for p in progress_records])
            all_types = set([ex_type[0] for ex_type in all_exercise_types])
            new_types = all_types - practised_types

            for new_type in new_types:
                # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                valid_types = [t.value for t in ExerciseType]
                valid_difficulties = [d.value for d in DifficultyLevel]

                ex_filter = [
                    Exercise.exercise_type == new_type,
                    Exercise.difficulty == user_default_difficulty,
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True,
                ]
                if user_age_group != AgeGroups.ALL_AGES:
                    age_values = list(
                        AgeGroups.AGE_ALIASES.get(user_age_group, [user_age_group])
                    )
                    age_values = [str(v).lower() for v in age_values]
                    age_values.extend(["tous-ages", "tous ages", "all_ages"])
                    ex_filter.append(func.lower(Exercise.age_group).in_(age_values))
                exercises = (
                    db.query(Exercise)
                    .filter(*ex_filter)
                    .order_by(func.random())
                    .limit(1)
                    .all()
                )

                for ex in exercises:
                    # Exclure les exercices déjà réussis
                    if ex.id not in all_completed_exercise_ids:
                        recommendations.append(
                            Recommendation(
                                user_id=user_id,
                                exercise_type=ex.exercise_type,
                                difficulty=ex.difficulty,
                                exercise_id=ex.id,
                                priority=4,
                                reason=f"Découvrez un nouveau type d'exercice: {ex.exercise_type}",
                            )
                        )

            # 5. Recommandations de défis logiques (challenges) — ciblés par age_group
            from app.services.challenge_service import normalize_age_group_for_db

            completed_challenge_ids = {
                a.challenge_id
                for a in db.query(LogicChallengeAttempt)
                .filter(
                    LogicChallengeAttempt.user_id == user_id,
                    LogicChallengeAttempt.is_correct == True,
                )
                .all()
            }
            challenge_query = db.query(LogicChallenge).filter(
                LogicChallenge.is_archived == False
            )
            # Filtrer par groupe d'âge utilisateur (sauf tous-ages)
            if user_age_group != AgeGroups.ALL_AGES:
                try:
                    db_age_group = normalize_age_group_for_db(user_age_group)
                    challenge_query = challenge_query.filter(
                        or_(
                            LogicChallenge.age_group == db_age_group,
                            LogicChallenge.age_group == AgeGroup.ALL_AGES,
                        )
                    )
                except Exception:
                    pass  # Garder tous les défis si erreur de conversion
            if completed_challenge_ids:
                challenge_query = challenge_query.filter(
                    ~LogicChallenge.id.in_(list(completed_challenge_ids))
                )
            suggested_challenges = (
                challenge_query.order_by(func.random()).limit(4).all()
            )
            # Priorité selon défis complétés + objectif (samuser → plus de défis)
            num_completed = len(completed_challenge_ids)
            challenge_priority = (
                8 if num_completed == 0 else 7 if num_completed < 3 else 6
            )
            if learning_goal == "samuser":
                challenge_priority = min(9, challenge_priority + 1)
            for ch in suggested_challenges:
                challenge_type_str = (
                    str(ch.challenge_type).lower() if ch.challenge_type else "logique"
                )
                if num_completed == 0:
                    reason = "Découvrez les défis logiques pour aiguiser votre raisonnement !"
                elif num_completed < 3:
                    reason = (
                        f"Variez votre entraînement avec un défi {challenge_type_str} !"
                    )
                else:
                    reason = f"Testez vos compétences logiques avec un défi {challenge_type_str} !"
                recommendations.append(
                    Recommendation(
                        user_id=user_id,
                        exercise_id=None,
                        challenge_id=ch.id,
                        recommendation_type="challenge",
                        exercise_type="challenge",
                        difficulty=ch.difficulty or "PADAWAN",
                        priority=challenge_priority,
                        reason=reason,
                    )
                )

            # Si aucune recommandation n'a été générée, proposer quelques exercices aléatoires
            if not recommendations:
                # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                valid_types = [t.value for t in ExerciseType]
                valid_difficulties = [d.value for d in DifficultyLevel]

                logger.debug(
                    f"Aucune recommandation générée, recherche d'exercices aléatoires..."
                )
                logger.debug(f"Types valides: {valid_types}")
                logger.debug(f"Difficultés valides: {valid_difficulties}")

                ex_filter = [
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True,
                ]
                if user_age_group != AgeGroups.ALL_AGES:
                    age_values = list(
                        AgeGroups.AGE_ALIASES.get(user_age_group, [user_age_group])
                    )
                    age_values = [str(v).lower() for v in age_values]
                    age_values.extend(["tous-ages", "tous ages", "all_ages"])
                    ex_filter.append(func.lower(Exercise.age_group).in_(age_values))
                exercise_query = db.query(Exercise).filter(*ex_filter)

                # Exclure les exercices déjà réussis
                if all_completed_exercise_ids:
                    exercise_query = exercise_query.filter(
                        ~Exercise.id.in_(list(all_completed_exercise_ids))
                    )

                random_exercises = exercise_query.order_by(func.random()).limit(3).all()

                logger.debug(f"Exercices trouvés: {len(random_exercises)}")
                for ex in random_exercises:
                    logger.debug(f"  - {ex.title} ({ex.exercise_type}/{ex.difficulty})")

                for ex in random_exercises:
                    if ex.id in all_completed_exercise_ids:
                        continue
                    recommendations.append(
                        Recommendation(
                            user_id=user_id,
                            exercise_type=ex.exercise_type,
                            difficulty=ex.difficulty,
                            exercise_id=ex.id,
                            priority=3,
                            reason="Pour continuer votre apprentissage",
                        )
                    )

                logger.debug(f"Recommandations fallback créées: {len(recommendations)}")

            # Ajouter toutes les recommandations
            db.add_all(recommendations)
            db.commit()

            return recommendations

        except Exception as recommendations_generation_error:
            logger.error(
                f"Erreur dans la génération des recommandations: {str(recommendations_generation_error)}"
            )
            db.rollback()
            return []

    @staticmethod
    def mark_recommendation_as_shown(db, recommendation_id):
        """Marque une recommandation comme ayant été montrée à l'utilisateur"""
        try:
            recommendation = (
                db.query(Recommendation)
                .filter(Recommendation.id == recommendation_id)
                .first()
            )
            if recommendation:
                recommendation.shown_count += 1
                db.commit()
        except Exception as mark_shown_error:
            logger.error(
                f"Erreur lors du marquage de la recommandation comme montrée: {str(mark_shown_error)}"
            )
            db.rollback()

    @staticmethod
    def mark_recommendation_as_clicked(db, recommendation_id):
        """Marque une recommandation comme ayant été cliquée par l'utilisateur"""
        try:
            recommendation = (
                db.query(Recommendation)
                .filter(Recommendation.id == recommendation_id)
                .first()
            )
            if recommendation:
                recommendation.clicked_count += 1
                recommendation.last_clicked_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as mark_clicked_error:
            logger.error(
                f"Erreur lors du marquage de la recommandation comme cliquée: {str(mark_clicked_error)}"
            )
            db.rollback()

    @staticmethod
    def mark_recommendation_as_completed(db, recommendation_id, user_id=None):
        """
        Marque une recommandation comme complétée.
        Si user_id fourni, vérifie que la recommandation appartient à l'utilisateur.

        Returns:
            (success: bool, recommendation: Recommendation | None)
        """
        try:
            q = db.query(Recommendation).filter(Recommendation.id == recommendation_id)
            if user_id is not None:
                q = q.filter(Recommendation.user_id == user_id)
            recommendation = q.first()
            if recommendation:
                recommendation.is_completed = True
                recommendation.completed_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(recommendation)
                return True, recommendation
            return False, None
        except Exception as mark_completed_error:
            logger.error(
                f"Erreur lors du marquage de la recommandation comme complétée: {str(mark_completed_error)}"
            )
            db.rollback()
            return False, None

    @staticmethod
    def get_recommendations_for_api(db, user_id, limit=7):
        """
        Récupère les recommandations formatées pour l'API (filtrage archivés, enrichissement).

        Returns:
            Liste de dicts prêts pour JSONResponse
        """
        recommendations = RecommendationService.get_user_recommendations(
            db, user_id, limit=limit
        )
        if not recommendations:
            try:
                RecommendationService.generate_recommendations(db, user_id)
                db.commit()
                recommendations = RecommendationService.get_user_recommendations(
                    db, user_id, limit=limit
                )
            except Exception as gen_error:
                logger.error(f"Erreur génération recommandations: {gen_error}")
                return []

        completed_exercise_ids = {
            a.exercise_id
            for a in db.query(Attempt)
            .filter(
                Attempt.user_id == user_id,
                Attempt.is_correct == True,
                Attempt.exercise_id.isnot(None),
            )
            .all()
            if a.exercise_id
        }
        completed_challenge_ids = {
            a.challenge_id
            for a in db.query(LogicChallengeAttempt)
            .filter(
                LogicChallengeAttempt.user_id == user_id,
                LogicChallengeAttempt.is_correct == True,
                LogicChallengeAttempt.challenge_id.isnot(None),
            )
            .all()
            if a.challenge_id
        }

        difficulty_to_age_group = {
            "INITIE": "6-8",
            "PADAWAN": "9-11",
            "CHEVALIER": "12-14",
            "MAITRE": "15-17",
            "GRAND_MAITRE": "adulte",
        }

        result = []
        for rec in recommendations:
            if rec.exercise_id and rec.exercise_id in completed_exercise_ids:
                continue
            if getattr(rec, "challenge_id", None) and rec.challenge_id in completed_challenge_ids:
                continue

            exercise = None
            challenge = None
            if rec.exercise_id:
                exercise = db.query(Exercise).filter(Exercise.id == rec.exercise_id).first()
                if not exercise or exercise.is_archived or not getattr(exercise, "is_active", True):
                    continue
            if getattr(rec, "challenge_id", None):
                challenge = db.query(LogicChallenge).filter(LogicChallenge.id == rec.challenge_id).first()
                if not challenge or getattr(challenge, "is_archived", False):
                    continue

            difficulty_str = str(rec.difficulty).upper() if rec.difficulty else "PADAWAN"
            age_group = difficulty_to_age_group.get(difficulty_str, "9-11")

            rec_data = {
                "id": rec.id,
                "exercise_type": str(rec.exercise_type),
                "difficulty": difficulty_str,
                "age_group": age_group,
                "reason": rec.reason or "",
                "priority": rec.priority,
                "recommendation_type": getattr(rec, "recommendation_type", None) or "exercise",
            }
            if rec.exercise_id and exercise:
                rec_data["exercise_id"] = rec.exercise_id
                rec_data["exercise_title"] = exercise.title
                rec_data["exercise_question"] = getattr(exercise, "question", None)
            if getattr(rec, "challenge_id", None) and challenge:
                rec_data["challenge_id"] = rec.challenge_id
                rec_data["challenge_title"] = getattr(challenge, "title", None)
                rec_data["exercise_title"] = rec_data.get("exercise_title") or challenge.title

            result.append(rec_data)

        return result

    @staticmethod
    def get_user_recommendations(db, user_id, limit=7):
        """Récupère les recommandations actives (mix exercices + défis)"""
        all_recs = (
            db.query(Recommendation)
            .filter(
                Recommendation.user_id == user_id, Recommendation.is_completed == False
            )
            .order_by(Recommendation.priority.desc())
            .limit(limit + 10)
            .all()
        )
        result = list(all_recs[:limit])
        challenges = [r for r in all_recs if getattr(r, "challenge_id", None)]
        # Si aucun défi dans le top limit mais qu'il en existe, en insérer un
        if challenges and not any(getattr(r, "challenge_id", None) for r in result):
            exercises_only = [r for r in result if not getattr(r, "challenge_id", None)]
            if len(exercises_only) >= limit - 1:
                result = exercises_only[: limit - 1] + [challenges[0]]
        return result[:limit]

    @staticmethod
    def _get_next_difficulty(current_difficulty):
        """Retourne le niveau de difficulté suivant"""
        # Utiliser les mêmes valeurs que les énumérations DifficultyLevel (en majuscules)
        difficulty_levels = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE"]
        try:
            current_index = difficulty_levels.index(current_difficulty.upper())
            if current_index < len(difficulty_levels) - 1:
                return difficulty_levels[current_index + 1]
        except ValueError:
            pass
        return None
