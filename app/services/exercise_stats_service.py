"""
Service de statistiques pour les exercices et défis.
Extrait de ExerciseService pour séparer la responsabilité analytics.
"""

import random
from typing import Any, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt


class ExerciseStatsService:
    """Statistiques globales exercices/défis (thème Académie des Sages)."""

    @staticmethod
    def get_exercises_stats_for_api(db: Session) -> Dict[str, Any]:
        """
        Statistiques globales des exercices et défis pour l'API.
        Thème Académie des Sages.
        """
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

        def _mastery_msg(rate: float) -> str:
            if rate >= 90:
                return (
                    "L'Académie forme d'excellents mathématiciens ! "
                    "La sagesse règne ici."
                )
            if rate >= 75:
                return "Belle progression des apprentis. Le Conseil est satisfait."
            if rate >= 60:
                return (
                    "Les apprentis progressent. " "La patience est une vertu des sages."
                )
            if rate >= 40:
                return (
                    "L'entraînement doit s'intensifier. "
                    "La voie de la maîtrise est exigeante."
                )
            return (
                "Beaucoup reste à apprendre. "
                "Persévérance et courage sont essentiels."
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
