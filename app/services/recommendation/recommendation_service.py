from collections import Counter
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, exists, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import set_committed_value
from sqlalchemy.sql import func

from app.core.constants import AgeGroups, normalize_age_group
from app.core.difficulty_tier import (
    compute_user_target_difficulty_tier,
    exercise_tier_filter_expression,
)
from app.core.logging_config import get_logger
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeAttempt
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.recommendation.recommendation_exercise_ranking import (
    MAX_CANDIDATES_TO_RANK,
    collect_recent_recommended_exercise_ids,
    select_top_ranked_exercises,
)
from app.services.recommendation.recommendation_exercise_reasons import (
    REASON_EXERCISE_DISCOVERY,
    REASON_EXERCISE_FALLBACK,
    REASON_EXERCISE_IMPROVEMENT,
    REASON_EXERCISE_MAINTENANCE,
    REASON_EXERCISE_PROGRESSION,
    english_discovery,
    english_fallback,
    english_improvement,
    english_maintenance,
    english_progression,
    params_discovery,
    params_fallback,
    params_improvement,
    params_maintenance,
    params_progression,
)
from app.services.recommendation.recommendation_user_context import (
    build_recommendation_user_context,
    get_target_difficulty_for_type,
)
from app.utils.exercise_type_normalization import normalize_exercise_type_key

logger = get_logger(__name__)

# --- R5 — Défis logiques : codes de raison stables (i18n côté client) ---
REASON_CHALLENGE_ONBOARDING = "reco.challenge.onboarding"
REASON_CHALLENGE_GENTLE = "reco.challenge.gentle_progress"
REASON_CHALLENGE_STRETCH = "reco.challenge.skill_stretch"
REASON_CHALLENGE_VARIETY = "reco.challenge.variety"

_CHALLENGE_ONBOARDING_TYPES = frozenset({"sequence", "puzzle", "pattern"})


def _challenge_type_key(ch: LogicChallenge) -> str:
    ct = ch.challenge_type
    if ct is None:
        return "custom"
    return getattr(ct, "value", str(ct)).lower()


def _compute_logic_challenge_user_stats(db, user_id: int) -> SimpleNamespace:
    """Signaux R5 : tentatives 90j, taux de réussite, diversité récente (30j)."""
    now = datetime.now(timezone.utc)
    d30 = now - timedelta(days=30)
    d90 = now - timedelta(days=90)
    attempts = (
        db.query(LogicChallengeAttempt)
        .options(selectinload(LogicChallengeAttempt.challenge))
        .filter(
            LogicChallengeAttempt.user_id == user_id,
            LogicChallengeAttempt.created_at >= d90,
        )
        .all()
    )
    attempts_30 = [a for a in attempts if a.created_at and a.created_at >= d30]
    total_90 = len(attempts)
    success_90 = sum(1 for a in attempts if a.is_correct)
    sr_90 = (success_90 / total_90) if total_90 else None
    type_counts: Counter[str] = Counter()
    for a in attempts_30:
        ch = a.challenge
        if ch is not None:
            type_counts[_challenge_type_key(ch)] += 1
    dominant = type_counts.most_common(1)[0][0] if type_counts else None
    recent_types = set(type_counts.keys())
    last_activity = max((a.created_at for a in attempts if a.created_at), default=None)
    return SimpleNamespace(
        total_attempts_90d=total_90,
        success_rate_90d=sr_90,
        recent_types_30d=recent_types,
        dominant_recent_type=dominant,
        last_activity_at=last_activity,
    )


def _classify_challenge_profile(completed_count: int, stats: SimpleNamespace) -> str:
    """
    Profil utilisateur sur les défis (explicite, ordre des tests important).
    - struggling : priorité si beaucoup d'échecs relatifs
    - novice : peu d'historique défi et aucune complétion enregistrée
    - mature : assez de défis réussis ou historique riche et solide
    """
    if (
        stats.total_attempts_90d >= 3
        and stats.success_rate_90d is not None
        and stats.success_rate_90d < 0.45
    ):
        return "struggling"
    if completed_count == 0 and stats.total_attempts_90d < 5:
        return "novice"
    if completed_count >= 3 or (
        stats.total_attempts_90d >= 10
        and stats.success_rate_90d is not None
        and stats.success_rate_90d >= 0.5
    ):
        return "mature"
    return "developing"


def _profile_to_reason_code(profile: str) -> str:
    return {
        "novice": REASON_CHALLENGE_ONBOARDING,
        "struggling": REASON_CHALLENGE_GENTLE,
        "developing": REASON_CHALLENGE_STRETCH,
        "mature": REASON_CHALLENGE_VARIETY,
    }[profile]


def _english_fallback_reason(profile: str, type_key: str) -> str:
    """Fallback non-FR pour clients ne lisant pas reason_code (transition)."""
    return {
        "novice": f"Guided logic challenge ({type_key}) to get started.",
        "struggling": f"A gentler {type_key} challenge to rebuild confidence.",
        "developing": f"A {type_key} challenge matched to your current level.",
        "mature": f"A {type_key} challenge to diversify your logic practice.",
    }[profile]


def _score_challenge_for_recommendation(
    ch: LogicChallenge,
    profile: str,
    stats: SimpleNamespace,
    learning_goal: str,
    now: datetime,
    user_target_tier: Optional[int] = None,
) -> float:
    """
    Score borné et lisible. ``difficulty_rating`` est traité comme indicateur souvent partiel
    (défaut 3.0 si absent) — ne pas sur-interpréter.
    """
    dr_raw = ch.difficulty_rating
    dr = 3.0 if dr_raw is None else float(dr_raw)
    dr = max(1.0, min(5.0, dr))
    tv = _challenge_type_key(ch)
    inactive = False
    if stats.last_activity_at:
        inactive = (now - stats.last_activity_at) > timedelta(days=14)

    if profile == "struggling":
        score = (4.6 - dr) * 3.5
        if tv in _CHALLENGE_ONBOARDING_TYPES:
            score += 4.0
        if dr <= 2.5:
            score += 2.0
    elif profile == "novice":
        score = (4.2 - min(dr, 4.0)) * 2.8
        if tv in _CHALLENGE_ONBOARDING_TYPES:
            score += 6.0
    elif profile == "mature":
        score = (dr - 2.0) * 1.2
        if tv not in stats.recent_types_30d:
            score += 5.0
        if stats.dominant_recent_type and tv == stats.dominant_recent_type:
            score -= 4.0
    else:
        score = (5.0 - abs(dr - 3.0)) * 2.0
        if tv not in stats.recent_types_30d:
            score += 2.5

    if inactive and tv in _CHALLENGE_ONBOARDING_TYPES:
        score += 2.0
    if learning_goal == "samuser":
        score += 1.2
    if (
        user_target_tier is not None
        and getattr(ch, "difficulty_tier", None) is not None
    ):
        dist = abs(int(ch.difficulty_tier) - int(user_target_tier))
        score -= dist * 0.35
    return score


def _select_logic_challenge_recommendation_entries(
    db,
    user_id: int,
    user_age_group: str,
    learning_goal: str,
    completed_challenge_ids: Set[int],
    user_target_tier: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    R5 — Pool filtré (actif, non archivé, âge, non réussi), tri par score explicite
    (pas de tirage aléatoire dominant).
    """
    from app.services.challenges.challenge_service import normalize_age_group_for_db

    stats = _compute_logic_challenge_user_stats(db, user_id)
    completed_count = len(completed_challenge_ids)
    profile = _classify_challenge_profile(completed_count, stats)
    reason_code = _profile_to_reason_code(profile)
    now = datetime.now(timezone.utc)

    challenge_query = db.query(LogicChallenge).filter(
        LogicChallenge.is_archived == False,
        LogicChallenge.is_active == True,
    )
    if user_age_group != AgeGroups.ALL_AGES:
        try:
            db_age_group = normalize_age_group_for_db(user_age_group)
            challenge_query = challenge_query.filter(
                or_(
                    LogicChallenge.age_group == db_age_group,
                    LogicChallenge.age_group == AgeGroup.ALL_AGES,
                )
            )
        except (TypeError, ValueError):
            pass
    if completed_challenge_ids:
        challenge_query = challenge_query.filter(
            ~LogicChallenge.id.in_(list(completed_challenge_ids))
        )
    pool = challenge_query.order_by(LogicChallenge.id.desc()).limit(150).all()
    if not pool:
        return []

    scored: List[Tuple[float, LogicChallenge]] = []
    for ch in pool:
        sc = _score_challenge_for_recommendation(
            ch,
            profile,
            stats,
            learning_goal or "",
            now,
            user_target_tier=user_target_tier,
        )
        scored.append((sc, ch))
    scored.sort(key=lambda x: (-x[0], -x[1].id))
    top = scored[:4]

    pri_base = {"novice": 8, "struggling": 8, "developing": 7, "mature": 6}[profile]
    if learning_goal == "samuser":
        pri_base = min(9, pri_base + 1)

    out: List[Dict[str, Any]] = []
    for _sc, ch in top:
        tk = _challenge_type_key(ch)
        dr_raw = ch.difficulty_rating
        dr = 3.0 if dr_raw is None else float(dr_raw)
        dr = max(1.0, min(5.0, dr))
        params = {
            "challenge_type": tk,
            "difficulty_rating": round(dr, 2),
        }
        out.append(
            {
                "challenge": ch,
                "reason_code": reason_code,
                "reason_params": params,
                "priority": pri_base,
                "reason": _english_fallback_reason(profile, tk),
            }
        )
    return out


# --- R1 — Comparaison des types d'exercice ---
# Convention unique : ``normalize_exercise_type_key`` (chaîne minuscule strip).
# Toute comparaison Progress / Exercise / stats ``by_exercise_type`` doit passer par cette clé.

# --- R2 — Contexte utilisateur : diagnostic par type (``RecommendationUserContext``) ---


class RecommendationService:
    """Service analysant les performances et générant des recommandations personnalisées"""

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
                    "Tentative de génération de recommandations pour un utilisateur inexistant: %s",
                    user_id,
                )
                return []

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error("Utilisateur %s non trouvé", user_id)
                return []

            # R2 — Contexte explicite : diagnostic par type + médiane globale
            ctx = build_recommendation_user_context(user, db=db)
            user_age_group = ctx.age_group
            learning_goal = ctx.learning_goal
            practice_rhythm = ctx.practice_rhythm
            logger.debug(
                "Recommandations user %s: age_group=%s, global_default_difficulty=%s, diagnostic_by_type=%s, goal=%s",
                user_id,
                user_age_group,
                ctx.global_default_difficulty,
                ctx.diagnostic_difficulty_by_type,
                learning_goal,
            )

            # Récupérer les stats récentes (30 derniers jours) pour mieux cibler
            from app.services.users.user_service import UserService

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

            # R3 — Avant suppression des incomplètes : capturer les exercices récemment recommandés
            penalized_exercise_ids = collect_recent_recommended_exercise_ids(
                db, user_id
            )

            # Supprimer les anciennes recommandations non complétées.
            # synchronize_session=False : évite de marquer des instances ORM déjà en session
            # comme « supprimées » (ObjectDeletedError) lors d’un 2e generate dans la même session.
            db.query(Recommendation).filter(
                Recommendation.user_id == user_id, Recommendation.is_completed == False
            ).delete(synchronize_session=False)
            # Le DELETE bulk ne vide pas ``user.recommendations`` (relation ``delete-orphan``).
            # ``expire`` sur la relation a montré des effets de bord (FK user_id) ; on réaligne
            # la collection en mémoire sans toucher à la ligne ``users``.
            set_committed_value(user, "recommendations", [])

            # Générer de nouvelles recommandations
            recommendations = []

            # 1. Recommandations basées sur les domaines à améliorer (utilisant les stats récentes)
            # Prioriser les types avec faible taux de réussite récent
            for ex_type_key, type_stats in performance_by_type.items():
                # Clé canonique (alignée UserService : stats SQL en LOWER)
                ex_type = normalize_exercise_type_key(ex_type_key)
                success_rate = type_stats.get("success_rate", 0)
                total = type_stats.get("total", 0)

                # Seulement recommander si au moins 3 tentatives récentes pour avoir des données fiables
                if total >= 3 and success_rate < 70:
                    # Déterminer la priorité selon le taux de réussite + objectif (learning_goal)
                    if success_rate < 50:
                        priority = 9  # Urgent
                    else:
                        priority = 8  # Important
                    if learning_goal == "preparer_exam":
                        priority = min(10, priority + 1)  # Prioriser en vue d'un examen

                    # Niveau cible : Progress si présent, sinon diagnostic par type (R2), sinon global
                    progress_difficulty = None
                    for progress in progress_records:
                        if (
                            normalize_exercise_type_key(progress.exercise_type)
                            == ex_type
                        ):
                            progress_difficulty = progress.difficulty
                            break
                    target_difficulty = get_target_difficulty_for_type(
                        ctx, ex_type, progress_difficulty
                    )

                    # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                    valid_types = [t.value for t in ExerciseType]
                    valid_difficulties = [d.value for d in DifficultyLevel]

                    improv_tier = compute_user_target_difficulty_tier(
                        user_age_group, target_difficulty
                    )
                    # Trouver des exercices appropriés (F42 : fenêtre tier ±1 + legacy)
                    exercise_query = db.query(Exercise).filter(
                        func.lower(Exercise.exercise_type) == ex_type,
                        exercise_tier_filter_expression(improv_tier, target_difficulty),
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

                    # Borne le pool : ids décroissants = contenus récents d'abord (évite un LIMIT arbitraire)
                    candidates = (
                        exercise_query.order_by(Exercise.id.desc())
                        .limit(MAX_CANDIDATES_TO_RANK)
                        .all()
                    )
                    exercises = select_top_ranked_exercises(
                        candidates,
                        user_age_group,
                        penalized_exercise_ids,
                        2,
                        user_target_tier=improv_tier,
                    )
                    ex_reason_params = params_improvement(
                        ex_type, int(success_rate), target_difficulty
                    )
                    ex_reason_en = english_improvement(ex_type, int(success_rate))

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
                                    reason=ex_reason_en,
                                    reason_code=REASON_EXERCISE_IMPROVEMENT,
                                    reason_params=ex_reason_params,
                                )
                            )

            # 2. Recommandations pour monter en niveau (progression) - basé sur stats récentes
            for ex_type_key, type_stats in performance_by_type.items():
                ex_type = normalize_exercise_type_key(ex_type_key)
                success_rate = type_stats.get("success_rate", 0)
                total = type_stats.get("total", 0)

                # Si taux de réussite > 85% avec au moins 5 tentatives récentes, proposer niveau supérieur
                if total >= 5 and success_rate > 85:
                    # Trouver le niveau actuel depuis Progress
                    current_difficulty = None
                    for progress in progress_records:
                        if (
                            normalize_exercise_type_key(progress.exercise_type)
                            == ex_type
                        ):
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

                        prog_tier = compute_user_target_difficulty_tier(
                            user_age_group, next_difficulty
                        )
                        exercise_query = db.query(Exercise).filter(
                            func.lower(Exercise.exercise_type) == ex_type,
                            exercise_tier_filter_expression(prog_tier, next_difficulty),
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

                        candidates = (
                            exercise_query.order_by(Exercise.id.desc())
                            .limit(MAX_CANDIDATES_TO_RANK)
                            .all()
                        )
                        exercises = select_top_ranked_exercises(
                            candidates,
                            user_age_group,
                            penalized_exercise_ids,
                            1,
                            user_target_tier=prog_tier,
                        )
                        prog_params = params_progression(
                            ex_type, int(success_rate), next_difficulty
                        )
                        prog_en = english_progression(
                            ex_type, int(success_rate), next_difficulty
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
                                        reason=prog_en,
                                        reason_code=REASON_EXERCISE_PROGRESSION,
                                        reason_params=prog_params,
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

            # B4.2: précharger les exercices des tentatives récentes en une requête
            # au lieu de N requêtes dans la boucle (évite O(attempts × types) requêtes)
            recent_exercise_ids = [
                a.exercise_id for a in recent_attempts if a.exercise_id
            ]
            exercises_by_id = {}
            if recent_exercise_ids:
                exercises = (
                    db.query(Exercise)
                    .filter(
                        Exercise.id.in_(recent_exercise_ids),
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties),
                    )
                    .all()
                )
                exercises_by_id = {ex.id: ex for ex in exercises}

            for ex_type in all_exercise_types:
                ex_type = ex_type[0]  # Extraction du tuple
                # Vérifier si ce type d'exercice a été pratiqué récemment
                recent_type_attempts = []
                for a in recent_attempts:
                    if not a.exercise_id:
                        continue
                    exercise = exercises_by_id.get(a.exercise_id)
                    if exercise and normalize_exercise_type_key(
                        exercise.exercise_type
                    ) == normalize_exercise_type_key(ex_type):
                        recent_type_attempts.append(a)

                if not recent_type_attempts:
                    # Trouver le niveau le plus élevé maîtrisé par l'utilisateur pour ce type
                    user_level = None
                    for p in progress_records:
                        if (
                            normalize_exercise_type_key(p.exercise_type)
                            == normalize_exercise_type_key(ex_type)
                            and p.calculate_completion_rate() > 70
                        ):
                            user_level = p.difficulty

                    # Sinon diagnostic par type (R2) puis défaut global
                    if not user_level:
                        user_level = get_target_difficulty_for_type(
                            ctx, normalize_exercise_type_key(ex_type), None
                        )

                    # Proposer un exercice pour maintenir cette compétence
                    maint_tier = compute_user_target_difficulty_tier(
                        user_age_group, user_level
                    )
                    ex_filter = [
                        func.lower(Exercise.exercise_type)
                        == normalize_exercise_type_key(ex_type),
                        exercise_tier_filter_expression(maint_tier, user_level),
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
                    cand_react = (
                        db.query(Exercise)
                        .filter(*ex_filter)
                        .order_by(Exercise.id.desc())
                        .limit(MAX_CANDIDATES_TO_RANK)
                        .all()
                    )
                    exercises = select_top_ranked_exercises(
                        cand_react,
                        user_age_group,
                        penalized_exercise_ids,
                        1,
                        user_target_tier=maint_tier,
                    )
                    nt_key = normalize_exercise_type_key(ex_type)
                    maint_params = params_maintenance(nt_key, user_level)
                    maint_en = english_maintenance(nt_key)

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
                                    reason=maint_en,
                                    reason_code=REASON_EXERCISE_MAINTENANCE,
                                    reason_params=maint_params,
                                )
                            )

            # 4. Recommandations de découverte (R6 — diversité par type + ranking R3 + anti-répétition)
            practised_types = {
                normalize_exercise_type_key(p.exercise_type) for p in progress_records
            }
            all_types = {
                normalize_exercise_type_key(ex_type[0])
                for ex_type in all_exercise_types
            }
            new_types = all_types - practised_types

            if new_types:
                valid_types = [t.value for t in ExerciseType]
                valid_difficulties = [d.value for d in DifficultyLevel]
                discovery_penalized: Set[int] = set(penalized_exercise_ids)

                for nt in sorted(new_types):
                    target_d = get_target_difficulty_for_type(ctx, nt, None)
                    disc_tier = compute_user_target_difficulty_tier(
                        user_age_group, target_d
                    )
                    ex_filter = [
                        func.lower(Exercise.exercise_type) == nt,
                        exercise_tier_filter_expression(disc_tier, target_d),
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
                    if all_completed_exercise_ids:
                        ex_filter.append(
                            ~Exercise.id.in_(list(all_completed_exercise_ids))
                        )

                    candidates = (
                        db.query(Exercise)
                        .filter(*ex_filter)
                        .order_by(Exercise.id.desc())
                        .limit(MAX_CANDIDATES_TO_RANK)
                        .all()
                    )
                    picked = select_top_ranked_exercises(
                        candidates,
                        user_age_group,
                        discovery_penalized,
                        1,
                        user_target_tier=disc_tier,
                    )
                    if not picked:
                        continue
                    ex = picked[0]
                    disc_params = params_discovery(nt, target_d)
                    disc_en = english_discovery(nt)
                    recommendations.append(
                        Recommendation(
                            user_id=user_id,
                            exercise_type=ex.exercise_type,
                            difficulty=ex.difficulty,
                            exercise_id=ex.id,
                            priority=4,
                            reason=disc_en,
                            reason_code=REASON_EXERCISE_DISCOVERY,
                            reason_params=disc_params,
                        )
                    )
                    discovery_penalized.add(ex.id)

            # 5. Recommandations de défis logiques (R5 — scoring explicite + reason_code)
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
            for entry in _select_logic_challenge_recommendation_entries(
                db,
                user_id,
                user_age_group,
                learning_goal or "",
                completed_challenge_ids,
                user_target_tier=ctx.target_difficulty_tier,
            ):
                ch = entry["challenge"]
                recommendations.append(
                    Recommendation(
                        user_id=user_id,
                        exercise_id=None,
                        challenge_id=ch.id,
                        recommendation_type="challenge",
                        exercise_type="challenge",
                        difficulty=ch.difficulty or "PADAWAN",
                        priority=entry["priority"],
                        reason=entry["reason"],
                        reason_code=entry["reason_code"],
                        reason_params=entry["reason_params"],
                    )
                )

            # Si aucune recommandation n'a été générée, proposer quelques exercices aléatoires
            if not recommendations:
                # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                valid_types = [t.value for t in ExerciseType]
                valid_difficulties = [d.value for d in DifficultyLevel]

                logger.debug(
                    "Aucune recommandation générée, recherche d'exercices aléatoires..."
                )
                logger.debug("Types valides: %s", valid_types)
                logger.debug("Difficultés valides: %s", valid_difficulties)

                fb_tier = compute_user_target_difficulty_tier(
                    user_age_group, ctx.global_default_difficulty
                )
                ex_filter = [
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True,
                ]
                if fb_tier is not None:
                    lo_fb = max(1, fb_tier - 1)
                    hi_fb = min(12, fb_tier + 1)
                    ex_filter.append(
                        or_(
                            Exercise.difficulty_tier.is_(None),
                            Exercise.difficulty_tier.between(lo_fb, hi_fb),
                        )
                    )
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

                fb_candidates = (
                    exercise_query.order_by(Exercise.id.desc())
                    .limit(MAX_CANDIDATES_TO_RANK)
                    .all()
                )
                ranked_fallback = select_top_ranked_exercises(
                    fb_candidates,
                    user_age_group,
                    penalized_exercise_ids,
                    3,
                    user_target_tier=fb_tier,
                )

                logger.debug(
                    "Exercices trouvés (fallback classé): %s", len(ranked_fallback)
                )
                for ex in ranked_fallback:
                    logger.debug(
                        "  - %s (%s/%s)", ex.title, ex.exercise_type, ex.difficulty
                    )

                for ex in ranked_fallback:
                    if ex.id in all_completed_exercise_ids:
                        continue
                    recommendations.append(
                        Recommendation(
                            user_id=user_id,
                            exercise_type=ex.exercise_type,
                            difficulty=ex.difficulty,
                            exercise_id=ex.id,
                            priority=3,
                            reason=english_fallback(),
                            reason_code=REASON_EXERCISE_FALLBACK,
                            reason_params=params_fallback(),
                        )
                    )

                logger.debug(
                    "Recommandations fallback créées: %s", len(recommendations)
                )

            # Ajouter toutes les recommandations
            db.add_all(recommendations)
            db.commit()

            return recommendations

        except SQLAlchemyError as recommendations_generation_error:
            logger.error(
                "Erreur dans la génération des recommandations: %s",
                str(recommendations_generation_error),
            )
            db.rollback()
            return []

    @staticmethod
    def recommendation_has_verified_attempt(
        db, user_id: int, recommendation: Recommendation
    ) -> bool:
        """
        True si l'utilisateur a au moins une tentative **réussie** sur le contenu ciblé
        par la recommandation (exercice ou défi). Utilisé pour qualifier le signal « complété ».
        """
        if recommendation.exercise_id:
            return bool(
                db.query(
                    exists().where(
                        and_(
                            Attempt.user_id == user_id,
                            Attempt.exercise_id == recommendation.exercise_id,
                            Attempt.is_correct == True,
                        )
                    )
                ).scalar()
            )
        cid = getattr(recommendation, "challenge_id", None)
        if cid:
            return bool(
                db.query(
                    exists().where(
                        and_(
                            LogicChallengeAttempt.user_id == user_id,
                            LogicChallengeAttempt.challenge_id == cid,
                            LogicChallengeAttempt.is_correct == True,
                        )
                    )
                ).scalar()
            )
        return False

    @staticmethod
    def record_recommendations_list_impression(
        db, user_id: int, recommendation_ids: List[int]
    ) -> None:
        """
        R4 — Incrémente ``shown_count`` pour chaque reco réellement renvoyée au client.

        Appelé après construction de la liste API (une fois par requête GET liste).
        Limite les surcomptes **React** : le front ne déclenche pas ce signal ; seul le GET compte.
        """
        if not recommendation_ids:
            return
        try:
            rows = (
                db.query(Recommendation)
                .filter(
                    Recommendation.id.in_(recommendation_ids),
                    Recommendation.user_id == user_id,
                    Recommendation.is_completed == False,
                )
                .all()
            )
            for row in rows:
                row.shown_count = (row.shown_count or 0) + 1
            db.commit()
        except SQLAlchemyError as impression_error:
            logger.error(
                "Erreur lors de l'enregistrement des impressions recommandations: %s",
                impression_error,
            )
            db.rollback()

    @staticmethod
    def mark_recommendation_as_clicked(
        db, recommendation_id: int, user_id: int
    ) -> Tuple[bool, Optional[Recommendation]]:
        """
        R4 — Enregistre une ouverture / clic sur le CTA (exercice ou défi) pour cette reco.

        Vérifie que la recommandation appartient à ``user_id``. Chaque appel incrémente
        ``clicked_count`` (signal « intent » — pas idempotent).
        """
        try:
            recommendation = (
                db.query(Recommendation)
                .filter(
                    Recommendation.id == recommendation_id,
                    Recommendation.user_id == user_id,
                    Recommendation.is_completed == False,
                )
                .first()
            )
            if not recommendation:
                return False, None
            recommendation.clicked_count = (recommendation.clicked_count or 0) + 1
            recommendation.last_clicked_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(recommendation)
            return True, recommendation
        except SQLAlchemyError as mark_clicked_error:
            logger.error(
                "Erreur lors du marquage de la recommandation comme cliquée: %s",
                str(mark_clicked_error),
            )
            db.rollback()
            return False, None

    @staticmethod
    def mark_recommendation_as_completed(db, recommendation_id, user_id=None):
        """
        Marque une recommandation comme complétée (acquittement manuel dashboard).

        Si user_id fourni, vérifie que la recommandation appartient à l'utilisateur.

        ``verified_by_attempt`` : à l'instant T, une tentative réussie existe déjà sur
        l'exercice ou le défi recommandé — le « fait » est corrélé au contenu. Sinon le
        signal reste un **acquittement utilisateur** sans preuve de réussite (honnête).

        Returns:
            (success, recommendation | None, verified_by_attempt | None)
        """
        try:
            q = db.query(Recommendation).filter(Recommendation.id == recommendation_id)
            if user_id is not None:
                q = q.filter(Recommendation.user_id == user_id)
            recommendation = q.first()
            if recommendation:
                uid_for_verify = (
                    user_id if user_id is not None else recommendation.user_id
                )
                verified = RecommendationService.recommendation_has_verified_attempt(
                    db, uid_for_verify, recommendation
                )
                recommendation.is_completed = True
                recommendation.completed_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(recommendation)
                return True, recommendation, verified
            return False, None, None
        except SQLAlchemyError as mark_completed_error:
            logger.error(
                "Erreur lors du marquage de la recommandation comme complétée: %s",
                str(mark_completed_error),
            )
            db.rollback()
            return False, None, None

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
            except SQLAlchemyError as gen_error:
                logger.error("Erreur génération recommandations: %s", gen_error)
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
        displayed_ids: List[int] = []
        for rec in recommendations:
            if rec.exercise_id and rec.exercise_id in completed_exercise_ids:
                continue
            if (
                getattr(rec, "challenge_id", None)
                and rec.challenge_id in completed_challenge_ids
            ):
                continue

            exercise = rec.exercise if rec.exercise_id else None
            challenge = rec.challenge if getattr(rec, "challenge_id", None) else None
            if rec.exercise_id and (
                not exercise
                or exercise.is_archived
                or not getattr(exercise, "is_active", True)
            ):
                continue
            if getattr(rec, "challenge_id", None) and (
                not challenge
                or getattr(challenge, "is_archived", False)
                or not getattr(challenge, "is_active", True)
            ):
                continue

            difficulty_str = (
                str(rec.difficulty).upper() if rec.difficulty else "PADAWAN"
            )
            # Utiliser l'âge réel de l'exercice/défi, pas celui dérivé de la difficulté
            if exercise and getattr(exercise, "age_group", None):
                age_group = normalize_age_group(exercise.age_group)
            elif challenge and getattr(challenge, "age_group", None):
                from app.services.challenges.challenge_service import (
                    normalize_age_group_for_frontend,
                )

                age_group = normalize_age_group_for_frontend(challenge.age_group)
            else:
                age_group = difficulty_to_age_group.get(difficulty_str, "9-11")

            rec_data = {
                "id": rec.id,
                "exercise_type": str(rec.exercise_type),
                "difficulty": difficulty_str,
                "age_group": age_group,
                "reason": rec.reason or "",
                "priority": rec.priority,
                "recommendation_type": getattr(rec, "recommendation_type", None)
                or "exercise",
            }
            rc = getattr(rec, "reason_code", None)
            if rc:
                rec_data["reason_code"] = rc
            rp = getattr(rec, "reason_params", None)
            if rp is not None:
                rec_data["reason_params"] = rp
            if rec.exercise_id and exercise:
                rec_data["exercise_id"] = rec.exercise_id
                rec_data["exercise_title"] = exercise.title
                rec_data["exercise_question"] = getattr(exercise, "question", None)
            if getattr(rec, "challenge_id", None) and challenge:
                rec_data["challenge_id"] = rec.challenge_id
                rec_data["challenge_title"] = getattr(challenge, "title", None)
                rec_data["exercise_title"] = (
                    rec_data.get("exercise_title") or challenge.title
                )

            result.append(rec_data)
            displayed_ids.append(rec.id)

        # R4 — une impression liste par requête GET (évite les surcomptes de rendu React)
        RecommendationService.record_recommendations_list_impression(
            db, user_id, displayed_ids
        )

        return result

    @staticmethod
    def get_user_recommendations(db, user_id, limit=7):
        """Récupère les recommandations actives (mix exercices + défis)"""
        all_recs = (
            db.query(Recommendation)
            .options(
                selectinload(Recommendation.exercise),
                selectinload(Recommendation.challenge),
            )
            .filter(
                Recommendation.user_id == user_id, Recommendation.is_completed == False
            )
            .order_by(Recommendation.priority.desc())
            .limit(limit + 10)
            .all()
        )
        result = list(all_recs[:limit])
        challenges = [r for r in all_recs if getattr(r, "challenge_id", None)]
        # Si peu de défis dans le top limit mais qu'il en existe, en insérer davantage
        num_challenges_in_result = sum(
            1 for r in result if getattr(r, "challenge_id", None)
        )
        min_challenges = min(2, len(challenges))  # viser au moins 2 défis si dispo
        if challenges and num_challenges_in_result < min_challenges:
            exercises_only = [r for r in result if not getattr(r, "challenge_id", None)]
            slots_for_challenges = min(min_challenges, limit - 1)
            if len(exercises_only) >= limit - slots_for_challenges:
                result = (
                    exercises_only[: limit - slots_for_challenges]
                    + challenges[:slots_for_challenges]
                )
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


# --- Sync wrappers pour run_db_bound (LOT A4) ---


def get_recommendations_for_api_sync(user_id: int, limit: int = 7):
    """
    Use case sync: récupère les recommandations formatées pour l'API.
    Exécuté via run_db_bound() depuis les handlers.
    """
    from app.core.db_boundary import sync_db_session

    with sync_db_session() as db:
        return RecommendationService.get_recommendations_for_api(
            db, user_id, limit=limit
        )


def generate_recommendations_sync(user_id: int):
    """
    Use case sync: génère des recommandations pour l'utilisateur.
    Exécuté via run_db_bound() depuis les handlers.
    """
    from app.core.db_boundary import sync_db_session

    with sync_db_session() as db:
        return RecommendationService.generate_recommendations(db, user_id)


def mark_recommendation_as_completed_sync(
    recommendation_id: int, user_id: int
) -> Tuple[bool, Optional[Recommendation], Optional[bool]]:
    """
    Use case sync: marque une recommandation comme complétée.
    Exécuté via run_db_bound() depuis les handlers.
    Returns:
        (success, recommendation, verified_by_attempt)
    """
    from app.core.db_boundary import sync_db_session

    with sync_db_session() as db:
        return RecommendationService.mark_recommendation_as_completed(
            db, recommendation_id, user_id=user_id
        )


def mark_recommendation_as_opened_sync(
    recommendation_id: int, user_id: int
) -> Tuple[bool, Optional[Recommendation]]:
    """R4 — sync wrapper: clic / ouverture CTA depuis le dashboard."""
    from app.core.db_boundary import sync_db_session

    with sync_db_session() as db:
        return RecommendationService.mark_recommendation_as_clicked(
            db, recommendation_id, user_id
        )
