"""
Tests pour le service de recommandations.

Ce module teste toutes les fonctionnalités du service de recommandations,
incluant la génération, la récupération et le marquage des recommandations.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.constants import AgeGroups
from app.core.security import get_password_hash
from app.models.attempt import Attempt
from app.models.diagnostic_result import DiagnosticResult
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.user import User, UserRole
from app.services.recommendation.recommendation_exercise_ranking import (
    exercise_rank_sort_key,
    select_top_ranked_exercises,
)
from app.services.recommendation.recommendation_exercise_reasons import (
    REASON_EXERCISE_DISCOVERY,
    REASON_EXERCISE_IMPROVEMENT,
    REASON_EXERCISE_MAINTENANCE,
)
from app.services.recommendation.recommendation_service import (
    REASON_CHALLENGE_GENTLE,
    REASON_CHALLENGE_ONBOARDING,
    REASON_CHALLENGE_VARIETY,
    RecommendationService,
    _classify_challenge_profile,
    _profile_to_reason_code,
    _score_challenge_for_recommendation,
)
from app.services.recommendation.recommendation_user_context import (
    RecommendationUserContext,
    build_recommendation_user_context,
    get_target_difficulty_for_type,
)
from app.utils.db_helpers import get_enum_value
from app.utils.exercise_type_normalization import normalize_exercise_type_key
from tests.utils.test_helpers import unique_email, unique_username


def test_generate_recommendations_basic(db_session):
    """
    Teste la génération de base de recommandations pour un utilisateur.

    Vérifie que:
    - Au moins une recommandation est générée
    - Chaque recommandation a un exercice, une priorité et une raison
    """
    # Arrangement: Créer un utilisateur test avec des valeurs uniques
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)

    # Créer quelques exercices disponibles
    exercise1 = Exercise(
        title="Test Exercice pour recommandation 1",
        exercise_type=get_enum_value(
            ExerciseType, ExerciseType.ADDITION.value, db_session
        ),
        difficulty=get_enum_value(
            DifficultyLevel, DifficultyLevel.INITIE.value, db_session
        ),
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        is_active=True,
    )

    exercise2 = Exercise(
        title="Test Exercice pour recommandation 2",
        exercise_type=get_enum_value(
            ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
        ),
        difficulty=get_enum_value(
            DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session
        ),
        age_group="9-11",
        question="3×4=?",
        correct_answer="12",
        is_active=True,
    )

    db_session.add_all([exercise1, exercise2])
    db_session.commit()

    # Action: Générer des recommandations
    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )

    # Assertion: Vérifier les recommandations
    assert len(recommendations) > 0, "Au moins une recommandation devrait être générée"

    for rec in recommendations:
        assert (
            rec.user_id == user.id
        ), "La recommandation doit être associée à l'utilisateur"
        assert (
            rec.priority >= 1 and rec.priority <= 10
        ), "La priorité doit être entre 1 et 10"
        assert rec.reason, "Une raison doit être fournie"


def test_generate_recommendations_for_improvement(db_session):
    """
    Teste la génération de recommandations pour améliorer un domaine faible.

    Vérifie que:
    - Des exercices sont recommandés dans les domaines où l'utilisateur est faible
    - La raison indique clairement l'objectif d'amélioration
    """
    # Arrangement: Créer un utilisateur avec des performances faibles dans un domaine
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    # Créer plusieurs exercices de multiplication (le service ne recommande que les non tentés)
    mult_type = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    initie_diff = get_enum_value(
        DifficultyLevel, DifficultyLevel.INITIE.value, db_session
    )
    exercises = [
        Exercise(
            title="Test Mult 1",
            exercise_type=mult_type,
            difficulty=initie_diff,
            age_group="6-8",
            question="7x6=?",
            correct_answer="42",
            is_active=True,
            is_archived=False,
        ),
        Exercise(
            title="Test Mult 2",
            exercise_type=mult_type,
            difficulty=initie_diff,
            age_group="6-8",
            question="8x9=?",
            correct_answer="72",
            is_active=True,
            is_archived=False,
        ),
        Exercise(
            title="Test Mult 3",
            exercise_type=mult_type,
            difficulty=initie_diff,
            age_group="6-8",
            question="6x7=?",
            correct_answer="42",
            is_active=True,
            is_archived=False,
        ),
    ]
    for ex in exercises:
        db_session.add(ex)
    db_session.flush()
    exercise = exercises[0]

    # Créer un progrès faible dans ce domaine (50% de réussite seulement)
    progress = Progress(
        user_id=user.id,  # Utiliser l'ID du nouvel utilisateur
        exercise_type="multiplication",
        difficulty="INITIE",  # Doit correspondre à Exercise.difficulty pour le filtre du service
        total_attempts=10,
        correct_attempts=5,  # 50% de réussite
        mastery_level=1,
    )
    db_session.add(progress)
    db_session.flush()

    # Créer des tentatives récentes sur exercise SEULEMENT (exercise2 reste non tenté → recommandable)
    # Le service requiert >= 3 tentatives et < 70% de réussite pour les recommandations d'amélioration
    db_session.add_all(
        [
            Attempt(
                user_id=user.id,
                exercise_id=exercise.id,
                user_answer="42" if i < 5 else "0",
                is_correct=(i < 5),
                time_spent=2.0,
            )
            for i in range(10)
        ]
    )
    db_session.commit()

    # Action: Générer des recommandations
    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )

    # Assertion: Vérifier que des recommandations d'amélioration sont générées
    assert len(recommendations) > 0, "Des recommandations devraient être générées"

    # Au moins une recommandation devrait être pour la multiplication
    multiplication_recs = [
        r for r in recommendations if str(r.exercise_type).lower() == "multiplication"
    ]
    assert (
        len(multiplication_recs) > 0
    ), "Au moins une recommandation pour multiplication devrait être générée"

    # R6 — amélioration : reason_code stable + fallback EN (i18n côté client)
    high_pri_mult = [r for r in multiplication_recs if r.priority >= 8]
    assert high_pri_mult, "Au moins une reco multiplication prioritaire (amélioration)"
    assert all(
        getattr(r, "reason_code", None) == REASON_EXERCISE_IMPROVEMENT
        for r in high_pri_mult
    ), "Les recos d'amélioration portent reco.exercise.improvement"
    for rec in multiplication_recs:
        reason_lower = (rec.reason or "").lower()
        assert "success" in reason_lower or getattr(
            rec, "reason_code", None
        ), f"Fallback EN ou reason_code attendu: {rec.reason}"
        assert rec.priority >= 1, "La priorité devrait être positive"


def test_generate_recommendations_excludes_completed_exercises(db_session):
    """
    Les exercices déjà réussis (Attempt avec is_correct=True) ne doivent jamais être recommandés.
    """
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    add_type = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)

    ex_completed = Exercise(
        title="Ex déjà réussi",
        exercise_type=add_type,
        difficulty=initie,
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        is_active=True,
        is_archived=False,
    )
    ex_available = Exercise(
        title="Ex jamais fait",
        exercise_type=add_type,
        difficulty=initie,
        age_group="6-8",
        question="2+2=?",
        correct_answer="4",
        is_active=True,
        is_archived=False,
    )
    db_session.add_all([ex_completed, ex_available])
    db_session.commit()

    attempt = Attempt(
        user_id=user.id,
        exercise_id=ex_completed.id,
        user_answer="2",
        is_correct=True,
        time_spent=1.0,
    )
    db_session.add(attempt)
    db_session.commit()

    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )

    completed_ids = {r.exercise_id for r in recommendations if r.exercise_id}
    assert (
        ex_completed.id not in completed_ids
    ), "L'exercice déjà réussi ne doit pas être recommandé"


def test_get_next_difficulty():
    """
    Teste la fonction _get_next_difficulty pour vérifier qu'elle retourne le bon niveau suivant.
    """
    # Tests des niveaux de difficulté (la fonction retourne en majuscules)
    assert (
        RecommendationService._get_next_difficulty("initie") == "PADAWAN"
    ), "Le niveau suivant d'initié devrait être padawan"
    assert (
        RecommendationService._get_next_difficulty("padawan") == "CHEVALIER"
    ), "Le niveau suivant de padawan devrait être chevalier"
    assert (
        RecommendationService._get_next_difficulty("chevalier") == "MAITRE"
    ), "Le niveau suivant de chevalier devrait être maître"
    assert (
        RecommendationService._get_next_difficulty("maitre") is None
    ), "Le niveau maître ne devrait pas avoir de niveau suivant"

    # Cas d'erreur
    assert (
        RecommendationService._get_next_difficulty("Niveau_Inexistant") is None
    ), "Un niveau inexistant ne devrait pas avoir de niveau suivant"


def test_normalize_exercise_type_key_variants():
    """R1 — clé canonique : ADDITION, addition, enum et espaces se comparent pareil."""
    assert normalize_exercise_type_key("ADDITION") == normalize_exercise_type_key(
        "addition"
    )
    assert normalize_exercise_type_key(ExerciseType.ADDITION) == "addition"
    assert normalize_exercise_type_key("  MULTIPLICATION  ") == "multiplication"
    assert normalize_exercise_type_key("") == ""


def test_discovery_does_not_treat_practised_type_as_new_when_progress_casing_differs(
    db_session,
):
    """
    R1 — Progress en minuscules vs Exercise en enum : ne pas proposer « découverte » pour ce type.
    """
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    add_val = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    div_val = get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session)
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)

    for title, et in (
        ("Div A", div_val),
        ("Add A", add_val),
    ):
        db_session.add(
            Exercise(
                title=title,
                exercise_type=et,
                difficulty=initie,
                age_group="6-8",
                question="1+1=?",
                correct_answer="2",
                is_active=True,
                is_archived=False,
            )
        )
    db_session.flush()

    # Historique : type stocké en minuscules (données legacy possibles)
    db_session.add(
        Progress(
            user_id=user.id,
            exercise_type="addition",
            difficulty="INITIE",
            total_attempts=10,
            correct_attempts=8,
            mastery_level=3,
        )
    )
    db_session.commit()

    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )

    discovery_for_addition = [
        r
        for r in recommendations
        if r.exercise_id
        and normalize_exercise_type_key(r.exercise_type) == "addition"
        and r.priority == 4
        and getattr(r, "reason_code", None) == REASON_EXERCISE_DISCOVERY
    ]
    assert (
        not discovery_for_addition
    ), "Le type déjà présent en Progress (casing différent) ne doit pas être « découverte »"


def test_reactivation_finds_progress_when_exercise_type_casing_differs(db_session):
    """
    R1 — Réactivation : Progress en minuscules doit matcher le type distinct des exercices (MAJ).
    """
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    add_val = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    mult_val = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)

    ex_add = Exercise(
        title="R1 Add",
        exercise_type=add_val,
        difficulty=initie,
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        is_active=True,
        is_archived=False,
    )
    ex_mult = Exercise(
        title="R1 Mult",
        exercise_type=mult_val,
        difficulty=initie,
        age_group="6-8",
        question="2x3=?",
        correct_answer="6",
        is_active=True,
        is_archived=False,
    )
    db_session.add_all([ex_add, ex_mult])
    db_session.flush()

    # Tentatives récentes uniquement sur l'addition → multiplication « non pratiquée »
    db_session.add_all(
        [
            Attempt(
                user_id=user.id,
                exercise_id=ex_add.id,
                user_answer="2",
                is_correct=True,
                time_spent=1.0,
            )
            for _ in range(12)
        ]
    )

    db_session.add(
        Progress(
            user_id=user.id,
            exercise_type="multiplication",
            difficulty="INITIE",
            total_attempts=20,
            correct_attempts=18,
            mastery_level=3,
        )
    )
    db_session.commit()

    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )

    reactivation_mult = [
        r
        for r in recommendations
        if r.exercise_id
        and normalize_exercise_type_key(r.exercise_type) == "multiplication"
        and r.priority == 5
        and getattr(r, "reason_code", None) == REASON_EXERCISE_MAINTENANCE
    ]
    assert (
        len(reactivation_mult) >= 1
    ), "La réactivation doit retrouver le Progress malgré le casing différent"


def test_get_target_difficulty_for_type_order():
    """R2 — Progress > diagnostic par type > défaut global."""
    ctx = RecommendationUserContext(
        age_group="tous-ages",
        global_default_difficulty="PADAWAN",
        learning_goal="",
        practice_rhythm="",
        diagnostic_difficulty_by_type={"division": "INITIE", "addition": "CHEVALIER"},
    )
    assert (
        get_target_difficulty_for_type(ctx, "division", "MAITRE") == "MAITRE"
    ), "Le Progress doit primer"
    assert (
        get_target_difficulty_for_type(ctx, "division", None) == "INITIE"
    ), "Sans Progress, utiliser le diagnostic pour ce type"
    assert (
        get_target_difficulty_for_type(ctx, "fractions", None) == "PADAWAN"
    ), "Sans score diagnostic pour ce type → défaut global"


def test_build_recommendation_user_context_normalizes_diagnostic_keys(db_session):
    """R2 — Clés diagnostic tolérantes (casing) via normalize_exercise_type_key."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    db_session.add(
        DiagnosticResult(
            user_id=user.id,
            triggered_from="onboarding",
            scores={
                "ADDITION": {
                    "level": 2,
                    "difficulty": "CHEVALIER",
                    "correct": 3,
                    "total": 4,
                },
                "division": {
                    "level": 0,
                    "difficulty": "INITIE",
                    "correct": 2,
                    "total": 4,
                },
            },
            questions_asked=8,
        )
    )
    db_session.commit()

    ctx = build_recommendation_user_context(user, db_session)
    assert ctx.diagnostic_difficulty_by_type["addition"] == "CHEVALIER"
    assert ctx.diagnostic_difficulty_by_type["division"] == "INITIE"


def test_build_recommendation_user_context_prefers_persisted_age_group(db_session):
    """F42 — users.age_group prime sur preferred_difficulty pour l'axe âge."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        age_group="6-8",
        preferred_difficulty="GRAND_MAITRE",
    )
    db_session.add(user)
    db_session.commit()

    ctx = build_recommendation_user_context(user, db_session)
    assert ctx.age_group == AgeGroups.GROUP_6_8


def test_improvement_uses_diagnostic_per_type_when_no_progress(db_session):
    """
    R2 — Fort en 3 types, faible en division : la reco « amélioration » division cible INITIE
    (diagnostic), pas la médiane globale (GRAND_MAITRE).
    """
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    db_session.add(
        DiagnosticResult(
            user_id=user.id,
            triggered_from="onboarding",
            scores={
                "addition": {
                    "level": 4,
                    "difficulty": "GRAND_MAITRE",
                    "correct": 5,
                    "total": 5,
                },
                "soustraction": {
                    "level": 4,
                    "difficulty": "GRAND_MAITRE",
                    "correct": 5,
                    "total": 5,
                },
                "multiplication": {
                    "level": 4,
                    "difficulty": "GRAND_MAITRE",
                    "correct": 5,
                    "total": 5,
                },
                "division": {
                    "level": 0,
                    "difficulty": "INITIE",
                    "correct": 2,
                    "total": 5,
                },
            },
            questions_asked=10,
        )
    )

    div_type = get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session)
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
    gm = get_enum_value(DifficultyLevel, DifficultyLevel.GRAND_MAITRE.value, db_session)

    ex_div_init = Exercise(
        title="R2 Div Init",
        exercise_type=div_type,
        difficulty=initie,
        age_group="6-8",
        question="6/2=?",
        correct_answer="3",
        is_active=True,
        is_archived=False,
    )
    ex_div_gm = Exercise(
        title="R2 Div GM",
        exercise_type=div_type,
        difficulty=gm,
        age_group="6-8",
        question="999/3=?",
        correct_answer="333",
        is_active=True,
        is_archived=False,
    )
    db_session.add_all([ex_div_init, ex_div_gm])
    db_session.flush()

    db_session.add_all(
        [
            Attempt(
                user_id=user.id,
                exercise_id=ex_div_init.id,
                user_answer="wrong",
                is_correct=False,
                time_spent=1.0,
            )
            for _ in range(10)
        ]
    )
    db_session.commit()

    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )

    div_improvement = [
        r
        for r in recommendations
        if r.exercise_id
        and normalize_exercise_type_key(r.exercise_type) == "division"
        and r.priority in (8, 9)
    ]
    assert div_improvement, "Une reco d'amélioration division est attendue"
    assert all(
        str(r.difficulty).upper() == "INITIE" for r in div_improvement
    ), "La difficulté cible doit suivre le diagnostic INITIE pour la division, pas la médiane globale"


def test_r3_exercise_rank_sort_key_stable_tie_break():
    """R3 — à critères égaux, plus grand id d'abord (tie-break explicite via -id)."""
    a = SimpleNamespace(id=10, view_count=0, age_group="6-8")
    b = SimpleNamespace(id=20, view_count=0, age_group="6-8")
    assert exercise_rank_sort_key(
        b, AgeGroups.GROUP_6_8, set()
    ) < exercise_rank_sort_key(a, AgeGroups.GROUP_6_8, set())


def test_r3_penalized_exercise_ranks_after_equivalent_fresh():
    """R3 — exercice récemment recommandé (pénalisé) passe après un équivalent non pénalisé."""
    penalized = SimpleNamespace(id=1, view_count=0, age_group="6-8")
    fresh = SimpleNamespace(id=999, view_count=0, age_group="6-8")
    assert exercise_rank_sort_key(
        penalized, AgeGroups.GROUP_6_8, {1}
    ) > exercise_rank_sort_key(fresh, AgeGroups.GROUP_6_8, {1})


def test_r3_select_top_ranked_is_repeatable():
    """R3 — même entrée → même ordre (stabilité inter-appels)."""
    items = [
        SimpleNamespace(id=3, view_count=1, age_group="6-8"),
        SimpleNamespace(id=1, view_count=1, age_group="6-8"),
        SimpleNamespace(id=2, view_count=0, age_group="6-8"),
    ]
    a = select_top_ranked_exercises(items, AgeGroups.GROUP_6_8, set(), 2)
    b = select_top_ranked_exercises(items, AgeGroups.GROUP_6_8, set(), 2)
    assert [x.id for x in a] == [x.id for x in b]


def test_r3_regenerate_prefers_unpenalized_alternative(db_session):
    """
    R3 — Après une première vague, un 3e exercice équivalent n'était pas choisi ;
    il doit passer avant les exercices déjà en reco récente.
    """
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    mult_type = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    padawan = get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session)

    exercises = []
    for i, title in enumerate(("R3 M1", "R3 M2", "R3 M3")):
        ex = Exercise(
            title=title,
            exercise_type=mult_type,
            difficulty=padawan,
            age_group="6-8",
            question=f"{i}×2=?",
            correct_answer=str(i * 2),
            is_active=True,
            is_archived=False,
            view_count=0,
        )
        db_session.add(ex)
        exercises.append(ex)
    db_session.flush()

    base = exercises[0]
    db_session.add_all(
        [
            Attempt(
                user_id=user.id,
                exercise_id=base.id,
                user_answer="wrong",
                is_correct=False,
                time_spent=1.0,
            )
            for _ in range(5)
        ]
    )
    db_session.commit()

    stats_payload = {
        "by_exercise_type": {
            "multiplication": {
                "total": 5,
                "success_rate": 0,
                "correct": 0,
            },
        }
    }
    our_exercise_ids = {e.id for e in exercises}

    with patch(
        "app.services.users.user_service.UserService.get_user_stats",
        return_value=stats_payload,
    ):
        first = RecommendationService.generate_recommendations(db_session, user.id)
    first_mult_ids = {
        r.exercise_id
        for r in first
        if r.exercise_id
        and normalize_exercise_type_key(r.exercise_type) == "multiplication"
        and r.priority in (8, 9)
    } & our_exercise_ids
    assert first_mult_ids, "Première génération : reco amélioration mult attendue"

    with patch(
        "app.services.users.user_service.UserService.get_user_stats",
        return_value=stats_payload,
    ):
        second = RecommendationService.generate_recommendations(db_session, user.id)
    second_mult_ids = {
        r.exercise_id
        for r in second
        if r.exercise_id
        and normalize_exercise_type_key(r.exercise_type) == "multiplication"
        and r.priority in (8, 9)
    } & our_exercise_ids
    assert second_mult_ids, "Seconde génération : toujours une reco mult"

    third_id = our_exercise_ids - first_mult_ids
    assert third_id, "Il doit rester un exercice mult non choisi au 1er tour"
    # Au moins une reco du 2e tour doit cibler l'exercice non présent dans la 1ère vague
    assert second_mult_ids & third_id, (
        "Le 3e exercice (non pénalisé en priorité) doit être privilégié vs "
        "reproposer uniquement les mêmes ids"
    )


# --- R4 — feedback lifecycle (service) ---


def test_r4_recommendation_has_verified_attempt_exercise(db_session):
    """Tentative réussie sur l'exercice recommandé → verified True."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    mult_type = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    padawan = get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session)
    ex = Exercise(
        title="R4 verify",
        exercise_type=mult_type,
        difficulty=padawan,
        age_group="6-8",
        question="2×2=?",
        correct_answer="4",
        is_active=True,
        is_archived=False,
    )
    db_session.add(ex)
    db_session.commit()

    db_session.add(
        Attempt(
            user_id=user.id,
            exercise_id=ex.id,
            user_answer="4",
            is_correct=True,
            time_spent=1.0,
        )
    )
    rec = Recommendation(
        user_id=user.id,
        exercise_id=ex.id,
        exercise_type=mult_type,
        difficulty=padawan,
        reason="x",
        priority=5,
    )
    db_session.add(rec)
    db_session.commit()

    assert RecommendationService.recommendation_has_verified_attempt(
        db_session, user.id, rec
    )


def test_r4_mark_clicked_rejects_wrong_user(db_session):
    """Clic enregistré seulement pour le propriétaire de la reco."""
    u1 = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="h",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    u2 = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="h",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add_all([u1, u2])
    db_session.commit()

    mult_type = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
    ex = Exercise(
        title="R4 click",
        exercise_type=mult_type,
        difficulty=initie,
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        is_active=True,
        is_archived=False,
    )
    db_session.add(ex)
    db_session.commit()

    rec = Recommendation(
        user_id=u1.id,
        exercise_id=ex.id,
        exercise_type=mult_type,
        difficulty=initie,
        reason="y",
        priority=5,
        clicked_count=0,
    )
    db_session.add(rec)
    db_session.commit()

    ok, _ = RecommendationService.mark_recommendation_as_clicked(
        db_session, rec.id, u2.id
    )
    assert ok is False

    ok2, r2 = RecommendationService.mark_recommendation_as_clicked(
        db_session, rec.id, u1.id
    )
    assert ok2 is True
    assert (r2.clicked_count or 0) == 1


def test_r4_record_list_impression_increments_shown(db_session):
    """Impression liste : shown_count +1 par id affiché."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="h",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    add_t = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
    ex = Exercise(
        title="R4 shown",
        exercise_type=add_t,
        difficulty=initie,
        age_group="6-8",
        question="1+0=?",
        correct_answer="1",
        is_active=True,
        is_archived=False,
    )
    db_session.add(ex)
    db_session.commit()

    rec = Recommendation(
        user_id=user.id,
        exercise_id=ex.id,
        exercise_type=add_t,
        difficulty=initie,
        reason="z",
        priority=5,
        shown_count=0,
    )
    db_session.add(rec)
    db_session.commit()

    RecommendationService.record_recommendations_list_impression(
        db_session, user.id, [rec.id]
    )
    db_session.refresh(rec)
    assert rec.shown_count == 1


def _r5_mock_challenge(
    challenge_id: int, difficulty_rating: float, type_value: str
) -> SimpleNamespace:
    return SimpleNamespace(
        id=challenge_id,
        difficulty_rating=difficulty_rating,
        challenge_type=SimpleNamespace(value=type_value),
    )


def test_r5_score_struggling_prefers_lower_difficulty_rating():
    """R5 — même type de défi : difficulty_rating bas score plus haut si profil struggling."""
    now = datetime.now(timezone.utc)
    stats = SimpleNamespace(
        total_attempts_90d=5,
        success_rate_90d=0.2,
        recent_types_30d=set(),
        dominant_recent_type=None,
        last_activity_at=now,
    )
    easy = _r5_mock_challenge(1, 1.0, "graph")
    hard = _r5_mock_challenge(2, 5.0, "graph")
    se = _score_challenge_for_recommendation(easy, "struggling", stats, "", now)
    sh = _score_challenge_for_recommendation(hard, "struggling", stats, "", now)
    assert se > sh


def test_r5_score_mature_prefers_type_not_seen_recently():
    """R5 — profil mature : bonus pour un type absent des 30 derniers jours."""
    now = datetime.now(timezone.utc)
    stats = SimpleNamespace(
        total_attempts_90d=12,
        success_rate_90d=0.55,
        recent_types_30d={"sequence"},
        dominant_recent_type="sequence",
        last_activity_at=now,
    )
    seq = _r5_mock_challenge(1, 3.0, "sequence")
    graph = _r5_mock_challenge(2, 3.0, "graph")
    assert _score_challenge_for_recommendation(
        graph, "mature", stats, "", now
    ) > _score_challenge_for_recommendation(seq, "mature", stats, "", now)


def test_r5_score_novice_prefers_onboarding_types_at_equal_rating():
    """R5 — novice : sequence/puzzle mieux notés que chess à difficulté égale."""
    now = datetime.now(timezone.utc)
    stats = SimpleNamespace(
        total_attempts_90d=0,
        success_rate_90d=None,
        recent_types_30d=set(),
        dominant_recent_type=None,
        last_activity_at=None,
    )
    seq = _r5_mock_challenge(1, 3.0, "sequence")
    chess = _r5_mock_challenge(2, 3.0, "chess")
    assert _score_challenge_for_recommendation(
        seq, "novice", stats, "", now
    ) > _score_challenge_for_recommendation(chess, "novice", stats, "", now)


def test_r5_classify_profile_and_reason_codes():
    """R5 — profils explicites → reason_code stable."""
    now = datetime.now(timezone.utc)
    st_struggling = SimpleNamespace(
        total_attempts_90d=5,
        success_rate_90d=0.2,
        recent_types_30d=set(),
        dominant_recent_type=None,
        last_activity_at=now,
    )
    assert _classify_challenge_profile(0, st_struggling) == "struggling"
    assert _profile_to_reason_code("struggling") == REASON_CHALLENGE_GENTLE

    st_novice = SimpleNamespace(
        total_attempts_90d=0,
        success_rate_90d=None,
        recent_types_30d=set(),
        dominant_recent_type=None,
        last_activity_at=None,
    )
    assert _classify_challenge_profile(0, st_novice) == "novice"
    assert _profile_to_reason_code("novice") == REASON_CHALLENGE_ONBOARDING

    st_mature = SimpleNamespace(
        total_attempts_90d=12,
        success_rate_90d=0.6,
        recent_types_30d={"sequence"},
        dominant_recent_type="sequence",
        last_activity_at=now,
    )
    assert _classify_challenge_profile(4, st_mature) == "mature"
    assert _profile_to_reason_code("mature") == REASON_CHALLENGE_VARIETY


def test_r5_generate_persists_reason_code_on_challenge_rows(db_session):
    """R5 — génération : les lignes challenge portent reason_code + reason_params (si schéma DB OK)."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    ch = LogicChallenge(
        title="R5 persist check",
        description="d",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.ALL_AGES.value, db_session),
        correct_answer="1",
        solution_explanation="x",
        difficulty_rating=2.0,
        is_active=True,
        is_archived=False,
    )
    db_session.add(ch)
    db_session.commit()

    recommendations = RecommendationService.generate_recommendations(
        db_session, user.id
    )
    ch_rows = [r for r in recommendations if r.challenge_id == ch.id]
    assert ch_rows, "Une reco défi attendue pour le défi seed minimal"
    assert ch_rows[0].reason_code == REASON_CHALLENGE_ONBOARDING
    assert ch_rows[0].reason_params.get("challenge_type") == "sequence"
    assert ch_rows[0].reason  # fallback EN toujours présent


def test_r6_discovery_has_reason_code_and_params(db_session):
    """R6 — branche discovery : reason_code stable + params (i18n client)."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        grade_level=3,
    )
    db_session.add(user)
    db_session.commit()

    add_val = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    mult_val = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)

    db_session.add(
        Progress(
            user_id=user.id,
            exercise_type="addition",
            difficulty="INITIE",
            total_attempts=10,
            correct_attempts=9,
            mastery_level=3,
        )
    )
    db_session.add(
        Exercise(
            title="R6 disc mult",
            exercise_type=mult_val,
            difficulty=initie,
            age_group="6-8",
            question="2×2=?",
            correct_answer="4",
            is_active=True,
            is_archived=False,
            view_count=0,
        )
    )
    db_session.commit()

    with patch(
        "app.services.users.user_service.UserService.get_user_stats",
        return_value={},
    ):
        recommendations = RecommendationService.generate_recommendations(
            db_session, user.id
        )

    disc = [
        r
        for r in recommendations
        if getattr(r, "reason_code", None) == REASON_EXERCISE_DISCOVERY
        and r.exercise_id
        and normalize_exercise_type_key(r.exercise_type) == "multiplication"
    ]
    assert disc, "Une reco discovery multiplication attendue"
    assert disc[0].reason_params.get("exercise_type") == "multiplication"
    assert disc[0].reason_params.get("target_difficulty")
    assert disc[0].reason and "multiplication" in disc[0].reason.lower()


def test_r6_discovery_prefers_unpenalized_alternative(db_session):
    """
    R6 — discovery passe par le ranking R3 : si un id est pénalisé (reco récente),
    préférer l'autre candidat équivalent (même type / difficulté).
    """
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        grade_level=3,
    )
    db_session.add(user)
    db_session.commit()

    add_val = get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
    mult_val = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)

    db_session.add(
        Progress(
            user_id=user.id,
            exercise_type="addition",
            difficulty="INITIE",
            total_attempts=10,
            correct_attempts=9,
            mastery_level=3,
        )
    )
    ex_low = Exercise(
        title="R6 mult low id",
        exercise_type=mult_val,
        difficulty=initie,
        age_group="6-8",
        question="1×1=?",
        correct_answer="1",
        is_active=True,
        is_archived=False,
        view_count=0,
    )
    ex_high = Exercise(
        title="R6 mult high id",
        exercise_type=mult_val,
        difficulty=initie,
        age_group="6-8",
        question="3×3=?",
        correct_answer="9",
        is_active=True,
        is_archived=False,
        view_count=0,
    )
    db_session.add_all([ex_low, ex_high])
    db_session.flush()
    db_session.add_all(
        [
            Attempt(
                user_id=user.id,
                exercise_id=ex_high.id,
                user_answer="0",
                is_correct=False,
                time_spent=1.0,
            )
            for _ in range(5)
        ]
    )
    db_session.commit()

    def _mult_discovery_exercise_ids(recs):
        out = []
        for r in recs:
            rc = getattr(r, "reason_code", None)
            eid = r.exercise_id
            if (
                rc == REASON_EXERCISE_DISCOVERY
                and eid
                and normalize_exercise_type_key(r.exercise_type) == "multiplication"
            ):
                out.append(eid)
        return out

    with patch(
        "app.services.users.user_service.UserService.get_user_stats",
        return_value={},
    ):
        first = RecommendationService.generate_recommendations(db_session, user.id)
    ids_first = _mult_discovery_exercise_ids(first)
    with patch(
        "app.services.users.user_service.UserService.get_user_stats",
        return_value={},
    ):
        second = RecommendationService.generate_recommendations(db_session, user.id)
    ids_second = _mult_discovery_exercise_ids(second)

    assert ids_first and ids_second, "Discovery mult attendue sur deux générations"
    assert ids_first[0] == ex_high.id
    assert ids_second[0] == ex_low.id


def test_r6_at_most_one_discovery_recommendation_per_new_type(db_session):
    """R6 — diversité : une seule reco discovery par type « nouveau »."""
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        grade_level=3,
    )
    db_session.add(user)
    db_session.commit()

    div_val = get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session)
    mult_val = get_enum_value(
        ExerciseType, ExerciseType.MULTIPLICATION.value, db_session
    )
    initie = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)

    db_session.add(
        Progress(
            user_id=user.id,
            exercise_type="addition",
            difficulty="INITIE",
            total_attempts=10,
            correct_attempts=9,
            mastery_level=3,
        )
    )
    for title, et in (("R6d1", div_val), ("R6m1", mult_val), ("R6m2", mult_val)):
        db_session.add(
            Exercise(
                title=title,
                exercise_type=et,
                difficulty=initie,
                age_group="6-8",
                question="q",
                correct_answer="1",
                is_active=True,
                is_archived=False,
                view_count=0,
            )
        )
    db_session.commit()

    with patch(
        "app.services.users.user_service.UserService.get_user_stats",
        return_value={},
    ):
        recommendations = RecommendationService.generate_recommendations(
            db_session, user.id
        )

    disc = [
        r
        for r in recommendations
        if getattr(r, "reason_code", None) == REASON_EXERCISE_DISCOVERY
        and r.exercise_id
    ]
    by_type = {}
    for r in disc:
        k = normalize_exercise_type_key(r.exercise_type)
        by_type[k] = by_type.get(k, 0) + 1
    assert by_type.get("multiplication", 0) <= 1
    assert by_type.get("division", 0) <= 1
