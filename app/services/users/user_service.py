"""
Service pour la gestion des utilisateurs.
Implémente les opérations métier liées aux utilisateurs et utilise le transaction manager.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.core.logging_config import get_logger
from app.core.types import (
    ChallengesProgressDict,
    ChartData,
    DashboardStats,
    PerformanceByType,
    UserProgressDict,
)

logger = get_logger(__name__)
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.db.adapter import DatabaseAdapter
from app.db.transaction import TransactionManager
from app.exceptions import UserNotFoundError
from app.models.achievement import UserAchievement
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.user import User, UserRole
from app.models.user_session import UserSession
from app.services.gamification.gamification_service import GamificationService
from app.utils.db_helpers import adapt_enum_for_db, get_enum_value


class UserService:
    """
    Service pour la gestion des utilisateurs.
    Fournit des méthodes pour récupérer, créer, modifier et supprimer des utilisateurs,
    ainsi que pour consulter leurs activités et statistiques.
    """

    @staticmethod
    def _flush_or_commit(db: Session, *, auto_commit: bool) -> None:
        if auto_commit:
            db.commit()
        else:
            db.flush()

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à récupérer

        Returns:
            L'utilisateur correspondant à l'ID ou None s'il n'existe pas
        """
        return DatabaseAdapter.get_by_id(db, User, user_id)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.

        Args:
            db: Session de base de données
            username: Nom d'utilisateur à rechercher

        Returns:
            L'utilisateur correspondant au nom d'utilisateur ou None s'il n'existe pas
        """
        users = DatabaseAdapter.get_by_field(db, User, "username", username)
        return users[0] if users else None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son adresse email.

        Args:
            db: Session de base de données
            email: Adresse email à rechercher

        Returns:
            L'utilisateur correspondant à l'adresse email ou None s'il n'existe pas
        """
        users = DatabaseAdapter.get_by_field(db, User, "email", email)
        return users[0] if users else None

    @staticmethod
    def list_users(
        db: Session, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[User]:
        """
        Liste tous les utilisateurs actifs.

        Args:
            db: Session de base de données
            limit: Nombre maximum d'utilisateurs à retourner
            offset: Décalage pour la pagination

        Returns:
            Liste des utilisateurs actifs
        """
        try:
            query = db.query(User).filter(User.is_active == True)

            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as users_fetch_error:
            logger.error(
                f"Erreur lors de la récupération des utilisateurs: {users_fetch_error}"
            )
            return []

    @staticmethod
    def create_user(db: Session, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Crée un nouvel utilisateur.

        Args:
            db: Session de base de données
            user_data: Dictionnaire contenant les données de l'utilisateur

        Returns:
            L'utilisateur créé ou None en cas d'erreur
        """
        # Vérifier si l'utilisateur existe déjà (par email ou username)
        username = user_data.get("username")
        email = user_data.get("email")

        with TransactionManager.transaction(db, auto_commit=False) as session:
            if username and UserService.get_user_by_username(session, username):
                logger.error(f"Un utilisateur avec le nom '{username}' existe déjà")
                return None

            if email and UserService.get_user_by_email(session, email):
                logger.error(f"Un utilisateur avec l'email '{email}' existe déjà")
                return None

            # Adapter le rôle utilisateur pour le moteur de base de données actuel
            role = user_data.get("role")
            if role:
                user_data["role"] = adapt_enum_for_db("UserRole", role, session)
                logger.debug(f"Rôle adapté: de '{role}' à '{user_data['role']}'")

            return DatabaseAdapter.create(session, User, user_data)

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> bool:
        """
        Met à jour un utilisateur existant.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à mettre à jour
            user_data: Dictionnaire contenant les nouvelles valeurs

        Returns:
            True si la mise à jour a réussi, False sinon
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour mise à jour")
            return False

        # Adapter le rôle utilisateur si présent dans les données de mise à jour
        if "role" in user_data:
            role = user_data["role"]
            user_data["role"] = adapt_enum_for_db("UserRole", role, db)
            logger.debug(
                f"Rôle adapté pour mise à jour: de '{role}' à '{user_data['role']}'"
            )

        return DatabaseAdapter.update(db, user, user_data)

    @staticmethod
    def delete_user(db: Session, user_id: int, *, auto_commit: bool = True) -> None:
        """
        Supprime physiquement un utilisateur de la base de données.
        Les entités associées sont supprimées en cascade.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à supprimer

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas
            DatabaseOperationError: Si la suppression échoue en base de données
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour suppression")
            raise UserNotFoundError(f"Utilisateur avec ID {user_id} non trouvé")

        TransactionManager.safe_delete(db, user, auto_commit=auto_commit)

    @staticmethod
    def disable_user(db: Session, user_id: int) -> bool:
        """
        Désactive un utilisateur (préférable à la suppression).

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à désactiver

        Returns:
            True si la désactivation a réussi, False sinon
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(f"Utilisateur avec ID {user_id} non trouvé pour désactivation")
            return False

        return DatabaseAdapter.update(db, user, {"is_active": False})

    @staticmethod
    def get_user_stats(
        db: Session, user_id: int, time_range: str = "30"
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un utilisateur.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            time_range: Période de temps ("7", "30", "90", "all")

        Returns:
            Dictionnaire contenant les statistiques de l'utilisateur
        """
        user = UserService.get_user(db, user_id)
        if not user:
            logger.error(
                f"Utilisateur avec ID {user_id} non trouvé pour récupération des statistiques"
            )
            return {}

        try:
            from datetime import datetime, timedelta, timezone

            # Calculer la date de début selon time_range
            date_filter = None
            if time_range != "all":
                days = int(time_range)
                date_filter = datetime.now(timezone.utc) - timedelta(days=days)

            # Statistiques de base avec filtre temporel
            attempts_query = db.query(Attempt).filter(Attempt.user_id == user_id)
            if date_filter:
                attempts_query = attempts_query.filter(
                    Attempt.created_at >= date_filter
                )

            total_attempts = attempts_query.count()
            correct_attempts = attempts_query.filter(Attempt.is_correct == True).count()

            # Calculer le taux de réussite (éviter la division par zéro)
            success_rate = (
                round((correct_attempts / total_attempts) * 100)
                if total_attempts > 0
                else 0
            )

            # Statistiques par type d'exercice
            exercise_types_stats = {}

            # Récupérer les statistiques directement avec SQL brut pour éviter les problèmes d'enum
            # et gérer les types en MAJUSCULES/minuscules mélangés
            # Ajouter le filtre temporel dans la requête SQL
            if date_filter:
                stats_query = text("""
                    SELECT 
                        LOWER(e.exercise_type::text) as exercise_type_normalized,
                        COUNT(*) as total,
                        SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) as correct
                    FROM attempts a
                    JOIN exercises e ON e.id = a.exercise_id
                    WHERE a.user_id = :user_id
                      AND a.created_at >= :date_filter
                    GROUP BY LOWER(e.exercise_type::text)
                    ORDER BY total DESC
                """)
                result = db.execute(
                    stats_query, {"user_id": user_id, "date_filter": date_filter}
                )
            else:
                stats_query = text("""
                    SELECT 
                        LOWER(e.exercise_type::text) as exercise_type_normalized,
                        COUNT(*) as total,
                        SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) as correct
                    FROM attempts a
                    JOIN exercises e ON e.id = a.exercise_id
                    WHERE a.user_id = :user_id
                    GROUP BY LOWER(e.exercise_type::text)
                    ORDER BY total DESC
                """)
                result = db.execute(stats_query, {"user_id": user_id})

            stats_rows = result.fetchall()

            # Construire le dictionnaire de statistiques par type normalisé
            for row in stats_rows:
                ex_type_normalized = row[0]
                total_type = row[1]
                correct_type = row[2]
                success_rate_type = (
                    round((correct_type / total_type) * 100) if total_type > 0 else 0
                )

                exercise_types_stats[ex_type_normalized] = {
                    "total": total_type,
                    "correct": correct_type,
                    "success_rate": success_rate_type,
                }

            # Récupérer les données de progression si disponibles
            progress_records = (
                db.query(Progress).filter(Progress.user_id == user_id).all()
            )
            progress_data = {}

            for record in progress_records:
                ex_type = record.exercise_type
                difficulty = record.difficulty

                if ex_type not in progress_data:
                    progress_data[ex_type] = {}

                progress_data[ex_type][difficulty] = {
                    "mastery_level": record.mastery_level,
                    "streak": record.streak,
                    "highest_streak": record.highest_streak,
                    "total_attempts": record.total_attempts,
                    "correct_attempts": record.correct_attempts,
                }

            # Assembler toutes les statistiques
            stats = {
                "user_id": user.id,
                "username": user.username,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "grade_level": user.grade_level,
                },
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "success_rate": success_rate,
                "by_exercise_type": exercise_types_stats,
            }

            # Ajouter les données de progression si disponibles
            if progress_data:
                stats["progress"] = progress_data

            return stats

        except SQLAlchemyError as stats_fetch_error:
            logger.error(
                f"Erreur lors de la récupération des statistiques: {stats_fetch_error}"
            )
            return {"stats_error": "Erreur lors de la récupération des statistiques"}

    @staticmethod
    def build_gamification_level_for_api(user: User) -> Dict[str, Any]:
        """
        Snapshot d'affichage gamification compte — délègue au moteur unique.

        Indépendant du filtre temporel du dashboard ; aligné classement.
        """
        return GamificationService.build_level_indicator_payload(user)

    @staticmethod
    def get_user_stats_for_dashboard(
        db: Session, user_id: int, time_range: str = "30"
    ) -> DashboardStats:
        """
        Récupère les statistiques complètes pour le tableau de bord utilisateur.

        Agrège l'activité sur la période (sans pseudo-XP ni niveau compte).

        Points / niveau / XP palier persistants : GET /api/users/me (gamification_level, total_points, …).
        Route: GET /api/users/stats
        """
        from datetime import datetime, timezone

        stats = UserService.get_user_stats(db, user_id, time_range=time_range)
        if not stats:
            stats = {
                "total_attempts": 0,
                "correct_attempts": 0,
                "success_rate": 0,
                "by_exercise_type": {},
            }

        performance_by_type = UserService._compute_performance_by_type(stats)
        recent_activity = UserService._fetch_recent_activity(db, user_id, time_range)
        progress_over_time, exercises_by_day = UserService._compute_progress_over_time(
            db, user_id, time_range
        )
        total_challenges = UserService._count_completed_challenges(db, user_id)

        return {
            "total_exercises": stats.get("total_attempts", 0),
            "total_challenges": total_challenges,
            "correct_answers": stats.get("correct_attempts", 0),
            "success_rate": stats.get("success_rate", 0),
            "performance_by_type": performance_by_type,
            "recent_activity": recent_activity,
            "progress_over_time": progress_over_time,
            "exercises_by_day": exercises_by_day,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _compute_performance_by_type(
        stats: Dict[str, Any],
    ) -> Dict[str, PerformanceByType]:
        """Calcule les performances par type d'exercice à partir des stats brutes."""
        performance_by_type: Dict[str, Any] = {}
        for exercise_type, type_stats in stats.get("by_exercise_type", {}).items():
            type_key = str(exercise_type).lower() if exercise_type else "unknown"
            total_t = type_stats.get("total", 0)
            correct_t = type_stats.get("correct", 0)
            performance_by_type[type_key] = {
                "completed": total_t,
                "correct": correct_t,
                "success_rate": (correct_t / total_t * 100) if total_t > 0 else 0,
            }
        return performance_by_type

    @staticmethod
    def _fetch_recent_activity(
        db: Session, user_id: int, time_range: str
    ) -> List[Dict[str, Any]]:
        """Récupère les 10 dernières activités (exercices + challenges)."""
        from datetime import datetime, timedelta, timezone

        recent_activity: List[Dict[str, Any]] = []
        try:
            cutoff_date = None
            if time_range != "all":
                cutoff_date = datetime.now(timezone.utc) - timedelta(
                    days=int(time_range)
                )

            exercise_q = db.query(Attempt).filter(Attempt.user_id == user_id)
            if cutoff_date:
                exercise_q = exercise_q.filter(Attempt.created_at >= cutoff_date)
            for attempt in exercise_q.order_by(Attempt.created_at.desc()).limit(5):
                recent_activity.append(
                    {
                        "type": "exercise",
                        "description": "Exercice complété",
                        "time": (
                            attempt.created_at.isoformat()
                            if attempt.created_at
                            else datetime.now(timezone.utc).isoformat()
                        ),
                        "is_correct": attempt.is_correct,
                    }
                )

            challenge_q = db.query(LogicChallengeAttempt).filter(
                LogicChallengeAttempt.user_id == user_id
            )
            if cutoff_date:
                challenge_q = challenge_q.filter(
                    LogicChallengeAttempt.created_at >= cutoff_date
                )
            for attempt in challenge_q.order_by(
                LogicChallengeAttempt.created_at.desc()
            ).limit(5):
                recent_activity.append(
                    {
                        "type": "challenge",
                        "description": "Défi logique complété",
                        "time": (
                            attempt.created_at.isoformat()
                            if attempt.created_at
                            else datetime.now(timezone.utc).isoformat()
                        ),
                        "is_correct": attempt.is_correct,
                    }
                )

            recent_activity.sort(key=lambda x: x.get("time", ""), reverse=True)
            return recent_activity[:10]
        except SQLAlchemyError as activity_error:
            logger.error(f"Erreur activité récente: {activity_error}")
            return []

    @staticmethod
    def _compute_progress_over_time(
        db: Session, user_id: int, time_range: str
    ) -> Tuple[ChartData, ChartData]:
        """Calcule la progression (taux de réussite + exercices/jour).

        Returns:
            (progress_over_time, exercises_by_day) — deux dicts Chart.js-ready.
        """
        from collections import defaultdict
        from datetime import datetime, timedelta, timezone

        progress_over_time: Dict[str, Any] = {"labels": [], "datasets": []}
        exercises_by_day: Dict[str, Any] = {"labels": [], "datasets": []}
        try:
            if time_range == "all":
                start_date = datetime.now(timezone.utc) - timedelta(days=90)
            else:
                start_date = datetime.now(timezone.utc) - timedelta(
                    days=int(time_range)
                )
            daily_stats = defaultdict(lambda: {"total": 0, "correct": 0})
            for attempt in (
                db.query(Attempt)
                .filter(
                    Attempt.user_id == user_id,
                    Attempt.created_at >= start_date,
                )
                .all()
            ):
                if attempt.created_at:
                    day_key = attempt.created_at.date().isoformat()
                    daily_stats[day_key]["total"] += 1
                    if attempt.is_correct:
                        daily_stats[day_key]["correct"] += 1

            sorted_days = sorted(daily_stats.keys())
            progress_over_time = {
                "labels": sorted_days,
                "datasets": [
                    {
                        "label": "Taux de réussite (%)",
                        "data": [
                            (
                                daily_stats[d]["correct"]
                                / daily_stats[d]["total"]
                                * 100
                                if daily_stats[d]["total"] > 0
                                else 0
                            )
                            for d in sorted_days
                        ],
                    }
                ],
            }
            exercises_by_day = {
                "labels": sorted_days,
                "datasets": [
                    {
                        "label": "Exercices complétés",
                        "data": [daily_stats[d]["total"] for d in sorted_days],
                        "borderColor": "rgb(139, 92, 246)",
                        "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    }
                ],
            }
        except Exception as progress_err:
            logger.error(f"Erreur progression: {progress_err}")

        return progress_over_time, exercises_by_day

    @staticmethod
    def _count_completed_challenges(db: Session, user_id: int) -> int:
        """Compte les challenges réussis par l'utilisateur."""
        try:
            return (
                db.query(LogicChallengeAttempt)
                .filter(
                    LogicChallengeAttempt.user_id == user_id,
                    LogicChallengeAttempt.is_correct == True,
                )
                .count()
            )
        except SQLAlchemyError:
            return 0

    @staticmethod
    def get_leaderboard_for_api(
        db: Session,
        current_user_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Récupère le classement des utilisateurs pour l'API.
        Applique le filtre de confidentialité (show_in_leaderboards).
        """
        q = db.query(User).filter(User.is_active.is_(True))
        # Over-fetch to account for privacy-filtered users (show_in_leaderboards=False).
        # The filter is applied in Python because accessibility_settings is a TEXT-JSON column.
        users = (
            q.options(selectinload(User.user_achievements))
            .order_by(User.total_points.desc())
            .limit(limit + 50)
            .all()
        )

        leaderboard = []
        for user in users:
            if len(leaderboard) >= limit:
                break
            settings = user.accessibility_settings or {}
            privacy = (
                (settings.get("privacy_settings") or {})
                if isinstance(settings.get("privacy_settings"), dict)
                else {}
            )
            if privacy.get("show_in_leaderboards") is False:
                continue
            leaderboard.append(
                {
                    "username": user.username,
                    "total_points": user.total_points or 0,
                    "current_level": user.current_level or 1,
                    "jedi_rank": user.jedi_rank or "youngling",
                    "is_current_user": user.id == current_user_id,
                    "avatar_url": user.avatar_url,
                    "current_streak": user.current_streak or 0,
                    "badges_count": len(user.user_achievements),
                }
            )
        for i, entry in enumerate(leaderboard, start=1):
            entry["rank"] = i
        return leaderboard

    @staticmethod
    def get_user_rank_by_points_for_api(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Rang global par points (utilisateurs actifs uniquement) : 1 + nombre d'utilisateurs
        avec strictement plus de points. Même logique de tie que le tri du leaderboard
        (égalité de points → même rang affiché pour tous les ex aequo).
        """
        user = UserService.get_user(db, user_id)
        if user is None:
            raise UserNotFoundError(f"Utilisateur avec ID {user_id} non trouvé")
        my_points = int(user.total_points or 0)
        pts = func.coalesce(User.total_points, 0)
        ahead = (
            db.query(func.count())
            .select_from(User)
            .filter(User.is_active.is_(True), pts > my_points)
            .scalar()
        )
        ahead_int = int(ahead or 0)
        return {"rank": ahead_int + 1, "total_points": my_points}

    @staticmethod
    def get_user_progress_for_api(db: Session, user_id: int) -> UserProgressDict:
        """
        Récupère la progression globale de l'utilisateur (exercices) pour l'API.
        """
        attempts_query = (
            db.query(Attempt, Exercise)
            .join(Exercise, Attempt.exercise_id == Exercise.id)
            .filter(Attempt.user_id == user_id)
            .order_by(Attempt.created_at)
            .all()
        )

        user_row = UserService.get_user(db, user_id)
        current_streak = getattr(user_row, "current_streak", None) or 0
        best_streak = getattr(user_row, "best_streak", None) or 0

        if not attempts_query:
            return {
                "total_attempts": 0,
                "correct_attempts": 0,
                "accuracy": 0.0,
                "average_time": 0.0,
                "exercises_completed": 0,
                "highest_streak": best_streak,
                "current_streak": current_streak,
                "by_category": {},
            }

        total_attempts = len(attempts_query)
        correct_attempts = sum(1 for attempt, _ in attempts_query if attempt.is_correct)
        accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0.0

        times = [
            attempt.time_spent for attempt, _ in attempts_query if attempt.time_spent
        ]
        average_time = sum(times) / len(times) if times else 0.0

        completed_exercise_ids = set()
        for attempt, exercise in attempts_query:
            if attempt.is_correct:
                completed_exercise_ids.add(exercise.id)
        exercises_completed = len(completed_exercise_ids)

        by_category = {}
        category_attempts = {}

        for attempt, exercise in attempts_query:
            exercise_type = exercise.exercise_type or "unknown"
            if exercise_type not in category_attempts:
                category_attempts[exercise_type] = {
                    "total": 0,
                    "correct": 0,
                    "completed_ids": set(),
                }
            category_attempts[exercise_type]["total"] += 1
            if attempt.is_correct:
                category_attempts[exercise_type]["correct"] += 1
                category_attempts[exercise_type]["completed_ids"].add(exercise.id)

        for exercise_type, stats in category_attempts.items():
            total = stats["total"]
            correct = stats["correct"]
            by_category[exercise_type] = {
                "completed": len(stats["completed_ids"]),
                "attempts": total,
                "correct": correct,
                "accuracy": round(correct / total, 2) if total > 0 else 0.0,
            }

        return {
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "accuracy": round(accuracy, 2),
            "average_time": round(average_time, 1),
            "exercises_completed": exercises_completed,
            "highest_streak": best_streak,
            "current_streak": current_streak,
            "by_category": by_category,
        }

    @staticmethod
    def get_challenges_progress_for_api(
        db: Session, user_id: int
    ) -> ChallengesProgressDict:
        """
        Récupère la progression des défis logiques pour l'API.
        """
        total_challenges = (
            db.query(LogicChallenge)
            .filter(
                LogicChallenge.is_active == True,
                LogicChallenge.is_archived == False,
            )
            .count()
        )

        all_attempts = (
            db.query(LogicChallengeAttempt)
            .filter(LogicChallengeAttempt.user_id == user_id)
            .all()
        )

        if not all_attempts:
            return {
                "completed_challenges": 0,
                "total_challenges": total_challenges,
                "success_rate": 0.0,
                "average_time": 0.0,
                "challenges": [],
            }

        completed_challenge_ids = set()
        challenge_stats = {}

        for attempt in all_attempts:
            challenge_id = attempt.challenge_id
            if challenge_id not in challenge_stats:
                challenge_stats[challenge_id] = {
                    "attempts": 0,
                    "correct_attempts": 0,
                    "best_time": None,
                    "times": [],
                }
            challenge_stats[challenge_id]["attempts"] += 1

            if attempt.is_correct:
                challenge_stats[challenge_id]["correct_attempts"] += 1
                completed_challenge_ids.add(challenge_id)
                if attempt.time_spent:
                    bt = challenge_stats[challenge_id]["best_time"]
                    if bt is None:
                        challenge_stats[challenge_id]["best_time"] = attempt.time_spent
                    else:
                        challenge_stats[challenge_id]["best_time"] = min(
                            bt, attempt.time_spent
                        )
            if attempt.time_spent:
                challenge_stats[challenge_id]["times"].append(attempt.time_spent)

        total_attempts = len(all_attempts)
        correct_attempts = sum(1 for a in all_attempts if a.is_correct)
        success_rate = correct_attempts / total_attempts if total_attempts > 0 else 0.0
        all_times = [a.time_spent for a in all_attempts if a.time_spent]
        average_time = sum(all_times) / len(all_times) if all_times else 0.0

        challenges_list = []
        if completed_challenge_ids:
            completed_challenges = (
                db.query(LogicChallenge)
                .filter(LogicChallenge.id.in_(completed_challenge_ids))
                .all()
            )
            for challenge in completed_challenges:
                stats = challenge_stats.get(challenge.id, {})
                challenges_list.append(
                    {
                        "id": challenge.id,
                        "title": challenge.title,
                        "is_completed": True,
                        "attempts": stats.get("attempts", 0),
                        "best_time": (
                            round(stats.get("best_time", 0), 2)
                            if stats.get("best_time")
                            else None
                        ),
                    }
                )

        return {
            "completed_challenges": len(completed_challenge_ids),
            "total_challenges": total_challenges,
            "success_rate": round(success_rate, 2),
            "average_time": round(average_time, 1),
            "challenges": challenges_list,
        }

    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: int,
        update_data: Dict[str, Any],
        *,
        auto_commit: bool = True,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Met à jour le profil utilisateur.
        Vérifie l'unicité de l'email si modifié.
        Retourne (user, None) en succès, (None, "not_found") ou (None, "email_taken").
        """
        user = UserService.get_user(db, user_id)
        if not user:
            return None, "not_found"

        if "email" in update_data and update_data["email"] != user.email:
            existing = (
                db.query(User)
                .filter(
                    User.email == update_data["email"],
                    User.id != user_id,
                )
                .first()
            )
            if existing:
                return None, "email_taken"

        onboarding_fields = {
            "grade_level",
            "grade_system",
            "preferred_difficulty",
            "learning_goal",
            "practice_rhythm",
        }
        if not getattr(
            user, "onboarding_completed_at", None
        ) and onboarding_fields.intersection(update_data.keys()):
            from datetime import datetime, timezone

            user.onboarding_completed_at = datetime.now(timezone.utc)

        for field, value in update_data.items():
            if field == "accessibility_settings":
                existing_settings = dict(user.accessibility_settings or {})
                if isinstance(value, dict):
                    existing_settings.update(value)
                    setattr(user, field, existing_settings)
                else:
                    setattr(user, field, value)
            else:
                setattr(user, field, value)

        UserService._flush_or_commit(db, auto_commit=auto_commit)
        db.refresh(user)
        return user, None

    @staticmethod
    def normalize_profile_update_data(
        raw_data: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Normalise et valide la payload de mise à jour profil indépendamment du transport.
        Retourne (payload_normalisée, None) ou (None, message_erreur).
        """
        import re

        from app.core.constants import VALID_LEARNING_STYLES, VALID_THEMES

        allowed_fields = {
            "email",
            "full_name",
            "grade_level",
            "grade_system",
            "learning_style",
            "preferred_difficulty",
            "preferred_theme",
            "accessibility_settings",
            "learning_goal",
            "practice_rhythm",
        }

        data = dict(raw_data)

        privacy_fields = [
            "is_public_profile",
            "allow_friend_requests",
            "show_in_leaderboards",
            "data_retention_consent",
            "marketing_consent",
        ]
        privacy_data = {}
        for field in privacy_fields:
            if field in data:
                privacy_data[field] = data.pop(field)
        if privacy_data:
            data["privacy_settings"] = privacy_data

        json_fields = [
            "notification_preferences",
            "language_preference",
            "timezone",
            "privacy_settings",
        ]
        json_overrides = {}
        for field in json_fields:
            if field in data:
                json_overrides[field] = data.pop(field)

        if json_overrides:
            if "accessibility_settings" not in data:
                data["accessibility_settings"] = {}
            if isinstance(data["accessibility_settings"], dict):
                data["accessibility_settings"].update(json_overrides)
            else:
                data["accessibility_settings"] = json_overrides

        update_data = {
            key: value for key, value in data.items() if key in allowed_fields
        }
        if not update_data:
            return None, "Aucun champ valide à mettre à jour."

        if "email" in update_data:
            email = str(update_data["email"]).strip().lower()
            if not email or not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
                return None, "Adresse email invalide."
            update_data["email"] = email

        if "full_name" in update_data:
            full_name = (
                str(update_data["full_name"]).strip()
                if update_data["full_name"]
                else None
            )
            if full_name and len(full_name) > 100:
                return None, "Le nom complet ne peut pas dépasser 100 caractères."
            update_data["full_name"] = full_name

        valid_grade_systems = {"suisse", "unifie"}
        if "grade_system" in update_data:
            grade_system = update_data["grade_system"]
            if grade_system is not None and grade_system not in valid_grade_systems:
                return None, "Système scolaire invalide. Valeurs : suisse ou unifie."

        if "grade_level" in update_data:
            grade_level = update_data["grade_level"]
            if grade_level is not None:
                try:
                    grade_level = int(grade_level)
                except (ValueError, TypeError):
                    return None, "Le niveau scolaire doit être un nombre."

                grade_system = update_data.get("grade_system")
                max_grade = 11 if grade_system == "suisse" else 12
                if grade_level < 1 or grade_level > max_grade:
                    return (
                        None,
                        f"Le niveau scolaire doit être entre 1 et {max_grade}.",
                    )
                update_data["grade_level"] = grade_level

        if "learning_style" in update_data:
            learning_style = update_data["learning_style"]
            if learning_style and learning_style not in VALID_LEARNING_STYLES:
                return (
                    None,
                    "Style d'apprentissage invalide. Valeurs acceptées : "
                    + ", ".join(sorted(VALID_LEARNING_STYLES)),
                )

        if "preferred_theme" in update_data:
            preferred_theme = update_data["preferred_theme"]
            if preferred_theme and preferred_theme not in VALID_THEMES:
                return (
                    None,
                    "Thème invalide. Valeurs acceptées : "
                    + ", ".join(sorted(VALID_THEMES)),
                )

        return update_data, None

    @staticmethod
    def serialize_user_profile_for_api(user: User) -> Dict[str, Any]:
        """Construit la réponse API standard pour le profil utilisateur."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if user.role else None,
            "is_email_verified": getattr(user, "is_email_verified", True),
            "grade_level": user.grade_level,
            "grade_system": getattr(user, "grade_system", None),
            "learning_style": user.learning_style,
            "preferred_difficulty": user.preferred_difficulty,
            "onboarding_completed_at": (
                user.onboarding_completed_at.isoformat()
                if getattr(user, "onboarding_completed_at", None)
                else None
            ),
            "learning_goal": getattr(user, "learning_goal", None),
            "practice_rhythm": getattr(user, "practice_rhythm", None),
            "preferred_theme": user.preferred_theme,
            "accessibility_settings": user.accessibility_settings,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "total_points": user.total_points,
            "current_level": user.current_level,
            "jedi_rank": user.jedi_rank,
            "gamification_level": UserService.build_gamification_level_for_api(user),
        }

    @staticmethod
    def serialize_registered_user_for_api(user: User) -> Dict[str, Any]:
        """Construit la réponse API standard après création de compte."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    @staticmethod
    def update_user_password(
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str,
        *,
        auto_commit: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Met à jour le mot de passe de l'utilisateur.
        Retourne (True, None) en cas de succès, (False, "message_erreur") sinon.
        """
        from datetime import datetime, timezone

        from app.core.security import get_password_hash, verify_password

        user = UserService.get_user(db, user_id)
        if not user:
            return False, "Utilisateur introuvable."

        if not verify_password(current_password, user.hashed_password):
            return False, "Le mot de passe actuel est incorrect."

        now = datetime.now(timezone.utc)
        user.hashed_password = get_password_hash(new_password)
        user.password_changed_at = now
        user.updated_at = now

        # Invalider toutes les sessions ORM de l'utilisateur pour aligner le
        # changement de mot de passe avec la révocation post-reset.
        for session in list(user.user_sessions):
            db.delete(session)

        UserService._flush_or_commit(db, auto_commit=auto_commit)
        db.refresh(user)
        return True, None

    @staticmethod
    def get_user_sessions_for_api(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupère les sessions actives non expirées de l'utilisateur.
        """
        from datetime import datetime, timezone

        from sqlalchemy import and_

        sessions = (
            db.query(UserSession)
            .filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(timezone.utc),
                )
            )
            .order_by(UserSession.last_activity.desc())
            .all()
        )

        most_recent_id = sessions[0].id if sessions else None
        result = []
        for session in sessions:
            result.append(
                {
                    "id": session.id,
                    "device_info": session.device_info,
                    "ip_address": (
                        str(session.ip_address) if session.ip_address else None
                    ),
                    "user_agent": session.user_agent,
                    "location_data": session.location_data,
                    "is_active": session.is_active,
                    "last_activity": session.last_activity.isoformat(),
                    "created_at": session.created_at.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "is_current": session.id == most_recent_id,
                }
            )
        return result

    @staticmethod
    def revoke_user_session(
        db: Session,
        session_id: int,
        user_id: int,
        *,
        auto_commit: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Révoque une session utilisateur (la marque inactive).
        Retourne (True, None) en cas de succès, (False, "message_erreur") sinon.
        """
        session = (
            db.query(UserSession)
            .filter(UserSession.id == session_id, UserSession.user_id == user_id)
            .first()
        )
        if not session:
            return False, "Session non trouvée ou non autorisée"

        session.is_active = False
        UserService._flush_or_commit(db, auto_commit=auto_commit)
        return True, None

    @staticmethod
    def get_user_export_data_for_api(
        db: Session, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère toutes les données d'un utilisateur pour export RGPD.
        Retourne None si l'utilisateur n'existe pas.
        """
        from datetime import datetime, timezone

        user = UserService.get_user(db, user_id)
        if not user:
            return None

        profile = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "grade_level": user.grade_level,
            "grade_system": getattr(user, "grade_system", None),
            "learning_style": user.learning_style,
            "preferred_difficulty": user.preferred_difficulty,
            "preferred_theme": user.preferred_theme,
            "accessibility_settings": user.accessibility_settings,
            "total_points": user.total_points,
            "current_level": user.current_level,
            "experience_points": (
                user.experience_points if hasattr(user, "experience_points") else 0
            ),
            "jedi_rank": user.jedi_rank,
            "avatar_url": user.avatar_url if hasattr(user, "avatar_url") else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

        attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
        exercises_data = [
            {
                "exercise_id": a.exercise_id,
                "answer": a.user_answer if hasattr(a, "user_answer") else None,
                "is_correct": a.is_correct,
                "time_spent": a.time_spent if hasattr(a, "time_spent") else None,
                "attempt_number": (
                    a.attempt_number if hasattr(a, "attempt_number") else None
                ),
                "hints_used": a.hints_used if hasattr(a, "hints_used") else 0,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in attempts
        ]

        challenge_attempts = (
            db.query(LogicChallengeAttempt)
            .filter(LogicChallengeAttempt.user_id == user_id)
            .all()
        )
        challenges_data = [
            {
                "challenge_id": ca.challenge_id,
                "user_solution": ca.user_solution,
                "is_correct": ca.is_correct,
                "time_spent": ca.time_spent,
                "hints_used": ca.hints_used,
                "created_at": (ca.created_at.isoformat() if ca.created_at else None),
            }
            for ca in challenge_attempts
        ]

        achievements = (
            db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
        )
        badges_data = [
            {
                "achievement_id": ach.achievement_id,
                "earned_at": (
                    ach.earned_at.isoformat()
                    if hasattr(ach, "earned_at") and ach.earned_at
                    else None
                ),
                "progress_data": (
                    ach.progress_data if hasattr(ach, "progress_data") else None
                ),
                "is_displayed": (
                    ach.is_displayed if hasattr(ach, "is_displayed") else True
                ),
            }
            for ach in achievements
        ]

        progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
        progress_data = [
            {
                "exercise_type": p.exercise_type,
                "difficulty": p.difficulty,
                "total_attempts": p.total_attempts,
                "correct_attempts": p.correct_attempts,
                "success_rate": p.success_rate if hasattr(p, "success_rate") else None,
                "last_attempt_at": (
                    p.last_attempt_at.isoformat()
                    if hasattr(p, "last_attempt_at") and p.last_attempt_at
                    else None
                ),
            }
            for p in progress_records
        ]

        recommendations = (
            db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
        )
        recommendations_data = [
            {
                "exercise_type": (
                    r.exercise_type if hasattr(r, "exercise_type") else None
                ),
                "priority": r.priority if hasattr(r, "priority") else None,
                "is_completed": r.is_completed if hasattr(r, "is_completed") else False,
                "reason": r.reason if hasattr(r, "reason") else None,
                "created_at": (
                    r.created_at.isoformat()
                    if hasattr(r, "created_at") and r.created_at
                    else None
                ),
            }
            for r in recommendations
        ]

        return {
            "export_date": datetime.now(timezone.utc).isoformat(),
            "format_version": "1.1",
            "profile": profile,
            "exercise_attempts": exercises_data,
            "challenge_attempts": challenges_data,
            "badges_earned": badges_data,
            "progress": progress_data,
            "recommendations": recommendations_data,
            "statistics": {
                "total_exercise_attempts": len(exercises_data),
                "total_challenge_attempts": len(challenges_data),
                "total_badges": len(badges_data),
                "total_progress_records": len(progress_data),
                "total_recommendations": len(recommendations_data),
            },
        }
