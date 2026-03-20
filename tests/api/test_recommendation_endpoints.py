"""
Tests des endpoints API pour les recommandations.

Routes réelles:
- GET /api/recommendations
- POST /api/recommendations/generate
- POST /api/recommendations/open (body: { recommendation_id: int }) — R4
- POST /api/recommendations/clicked — alias même handler que `/open`
- POST /api/recommendations/complete (body: { recommendation_id: int })
"""

import pytest

from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeType
from app.models.recommendation import Recommendation
from app.utils.db_helpers import get_enum_value


async def test_get_recommendations(padawan_client, db_session, mock_exercise):
    """GET /api/recommendations : récupère les recommandations de l'utilisateur."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    recommendation = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Test recommendation reason",
        priority=8,
        shown_count=0,
        clicked_count=0,
        last_clicked_at=None,
        completed_at=None,
    )
    db_session.add(recommendation)
    db_session.commit()

    response = await client.get("/api/recommendations")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    rec = next((r for r in data if r.get("id") == recommendation.id), None)
    assert rec is not None
    assert rec["exercise_id"] == exercise.id
    assert rec["exercise_type"] == str(exercise.exercise_type)
    assert rec["reason"] == "Test recommendation reason"
    assert rec["priority"] == 8

    db_session.refresh(recommendation)
    assert recommendation.shown_count == 1


async def test_get_recommendations_exposes_reason_code_r5_optional(
    padawan_client, db_session, mock_exercise
):
    """R5 — reason_code / reason_params sur les recos défi ; absents si non définis (exercice)."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    challenge = LogicChallenge(
        title="R5 API reason",
        description="Test",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.GRAPH.value, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.ALL_AGES.value, db_session),
        correct_answer="42",
        solution_explanation="Test",
        difficulty_rating=2.5,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    reco_ex = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        challenge_id=None,
        exercise_type=str(exercise.exercise_type),
        difficulty=str(exercise.difficulty),
        reason="Legacy exercise reason",
        priority=5,
        recommendation_type="exercise",
    )
    reco_ch = Recommendation(
        user_id=user_id,
        exercise_id=None,
        challenge_id=challenge.id,
        exercise_type="challenge",
        difficulty="PADAWAN",
        reason="Fallback EN short",
        priority=8,
        recommendation_type="challenge",
        reason_code="reco.challenge.variety",
        reason_params={"challenge_type": "graph", "difficulty_rating": 2.5},
    )
    db_session.add_all([reco_ex, reco_ch])
    db_session.commit()

    response = await client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.json()
    ex = next((r for r in data if r.get("id") == reco_ex.id), None)
    ch = next((r for r in data if r.get("id") == reco_ch.id), None)
    assert ex is not None and ch is not None
    assert "reason_code" not in ex
    assert ch.get("reason_code") == "reco.challenge.variety"
    assert ch.get("reason_params", {}).get("challenge_type") == "graph"


async def test_post_recommendation_open_increments_clicked(
    padawan_client, db_session, mock_exercise
):
    """POST /api/recommendations/open : clic / ouverture CTA (R4)."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    recommendation = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Open test",
        priority=8,
        shown_count=0,
        clicked_count=0,
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)

    r1 = await client.post(
        "/api/recommendations/open",
        json={"recommendation_id": recommendation.id},
    )
    assert r1.status_code == 200
    body = r1.json()
    assert body["clicked_count"] == 1
    assert body["last_clicked_at"] is not None

    r2 = await client.post(
        "/api/recommendations/open",
        json={"recommendation_id": recommendation.id},
    )
    assert r2.status_code == 200
    assert r2.json()["clicked_count"] == 2

    db_session.refresh(recommendation)
    assert recommendation.clicked_count == 2


async def test_post_recommendation_clicked_alias_same_as_open(
    padawan_client, db_session, mock_exercise
):
    """POST /api/recommendations/clicked est un alias de /open (R4)."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    recommendation = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="alias",
        priority=5,
        clicked_count=0,
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)

    r = await client.post(
        "/api/recommendations/clicked",
        json={"recommendation_id": recommendation.id},
    )
    assert r.status_code == 200
    assert r.json()["clicked_count"] == 1


async def test_mark_recommendation_as_completed(
    padawan_client, db_session, mock_exercise
):
    """POST /api/recommendations/complete : marque une recommandation comme complétée."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    recommendation = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Test recommendation reason",
        priority=8,
        shown_count=0,
        clicked_count=0,
        last_clicked_at=None,
        completed_at=None,
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)

    response = await client.post(
        "/api/recommendations/complete",
        json={"recommendation_id": recommendation.id},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload.get("verified_by_attempt") is False
    assert payload.get("completion_kind") == "manual_ack"
    db_session.refresh(recommendation)
    assert recommendation.is_completed is True
    assert recommendation.completed_at is not None


async def test_mark_recommendation_complete_verified_when_correct_attempt(
    padawan_client, db_session, mock_exercise
):
    """R4 — verified_by_attempt true si une tentative réussie existe déjà sur l'exercice."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    db_session.add(
        Attempt(
            user_id=user_id,
            exercise_id=exercise.id,
            user_answer=exercise.correct_answer,
            is_correct=True,
            time_spent=1.0,
        )
    )

    recommendation = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Déjà réussi",
        priority=8,
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)

    response = await client.post(
        "/api/recommendations/complete",
        json={"recommendation_id": recommendation.id},
    )
    assert response.status_code == 200
    assert response.json().get("verified_by_attempt") is True


async def test_get_recommendations_returns_exercise_and_challenge_ids(
    padawan_client, db_session, mock_exercise
):
    """GET /api/recommendations : exercise_id et challenge_id pour parcours guidé (QuickStartActions)."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    # Recommandation exercice
    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    # Recommandation défi
    challenge = LogicChallenge(
        title="Défi Test Reco QuickStart",
        description="Test",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12.value, db_session),
        correct_answer="42",
        solution_explanation="Test",
        difficulty_rating=2.0,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    reco_exercise = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        challenge_id=None,
        exercise_type="ADDITION",
        difficulty="PADAWAN",
        reason="Exo prioritaire",
        priority=9,
        recommendation_type="exercise",
    )
    reco_challenge = Recommendation(
        user_id=user_id,
        exercise_id=None,
        challenge_id=challenge.id,
        exercise_type="SEQUENCE",
        difficulty="PADAWAN",
        reason="Défi prioritaire",
        priority=8,
        recommendation_type="challenge",
    )
    db_session.add_all([reco_exercise, reco_challenge])
    db_session.commit()

    response = await client.get("/api/recommendations")

    assert response.status_code == 200
    data = response.json()

    reco_exo = next((r for r in data if r.get("exercise_id") == exercise.id), None)
    reco_ch = next((r for r in data if r.get("challenge_id") == challenge.id), None)

    assert reco_exo is not None, "Recommandation exercice doit être retournée"
    assert reco_exo["exercise_id"] == exercise.id
    assert "exercise_title" in reco_exo or "exercise_type" in reco_exo

    assert reco_ch is not None, "Recommandation défi doit être retournée"
    assert reco_ch["challenge_id"] == challenge.id
    assert "challenge_title" in reco_ch or "exercise_title" in reco_ch


async def test_get_recommendations_excludes_archived_challenge(
    padawan_client, db_session, mock_exercise
):
    """Les recommandations n'incluent pas les défis archivés."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    challenge = LogicChallenge(
        title="Défi à archiver",
        description="Test",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12.value, db_session),
        correct_answer="42",
        solution_explanation="Test",
        difficulty_rating=2.0,
        is_archived=False,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    reco = Recommendation(
        user_id=user_id,
        exercise_id=None,
        challenge_id=challenge.id,
        exercise_type="SEQUENCE",
        difficulty="PADAWAN",
        reason="Défi archivé",
        priority=8,
        recommendation_type="challenge",
    )
    db_session.add(reco)
    db_session.commit()

    # Archiver le défi
    challenge.is_archived = True
    db_session.commit()

    response = await client.get("/api/recommendations")

    assert response.status_code == 200
    data = response.json()
    reco_archived = next(
        (r for r in data if r.get("challenge_id") == challenge.id), None
    )
    assert reco_archived is None, "Un défi archivé ne doit pas être proposé"


async def test_get_recommendations_excludes_inactive_challenge(
    padawan_client, db_session
):
    """R5b — reco défi persistée : si le défi passe inactif, il disparaît du GET liste."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    challenge = LogicChallenge(
        title="Défi à désactiver",
        description="Test",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12.value, db_session),
        correct_answer="42",
        solution_explanation="Test",
        difficulty_rating=2.0,
        is_archived=False,
        is_active=True,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    reco = Recommendation(
        user_id=user_id,
        exercise_id=None,
        challenge_id=challenge.id,
        exercise_type="SEQUENCE",
        difficulty="PADAWAN",
        reason="Défi inactif test",
        priority=8,
        recommendation_type="challenge",
    )
    db_session.add(reco)
    db_session.commit()

    challenge.is_active = False
    db_session.commit()

    response = await client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.json()
    inactive_hit = next(
        (r for r in data if r.get("challenge_id") == challenge.id), None
    )
    assert inactive_hit is None, "Un défi inactif ne doit pas être proposé"


async def test_get_recommendations_unauthorized(client):
    """GET /api/recommendations requiert authentification."""
    response = await client.get("/api/recommendations")
    assert response.status_code == 401


async def test_mark_recommendation_complete_nonexistent(padawan_client):
    """POST /api/recommendations/complete avec recommendation_id inexistant → 404."""
    client = padawan_client["client"]
    response = await client.post(
        "/api/recommendations/complete",
        json={"recommendation_id": 99999},
    )
    assert response.status_code == 404


async def test_mark_other_user_recommendation_as_completed(
    padawan_client, maitre_client, db_session, mock_exercise
):
    """Un utilisateur ne peut pas compléter la recommandation d'un autre."""
    padawan_id = padawan_client["user_id"]
    maitre_client_api = maitre_client["client"]
    assert padawan_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    recommendation = Recommendation(
        user_id=padawan_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Padawan reco",
        priority=8,
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)

    response = await maitre_client_api.post(
        "/api/recommendations/complete",
        json={"recommendation_id": recommendation.id},
    )

    assert response.status_code == 404


async def test_mark_other_user_recommendation_open(
    padawan_client, maitre_client, db_session, mock_exercise
):
    """R4 — POST /api/recommendations/open refusé pour la reco d'un autre utilisateur."""
    padawan_id = padawan_client["user_id"]
    maitre_client_api = maitre_client["client"]
    assert padawan_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    recommendation = Recommendation(
        user_id=padawan_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Padawan reco open",
        priority=8,
    )
    db_session.add(recommendation)
    db_session.commit()

    response = await maitre_client_api.post(
        "/api/recommendations/open",
        json={"recommendation_id": recommendation.id},
    )
    assert response.status_code == 404


async def test_get_recommendations_shown_increments_per_request(
    padawan_client, db_session, mock_exercise
):
    """R4 — chaque GET liste incrémente shown_count pour les recos renvoyées."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    recommendation = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        reason="Shown test",
        priority=9,
        shown_count=0,
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)

    await client.get("/api/recommendations")
    await client.get("/api/recommendations")

    db_session.refresh(recommendation)
    assert recommendation.shown_count == 2


async def test_get_recommendations_exposes_reason_code_r6_exercise(
    padawan_client, db_session, mock_exercise
):
    """R6 — GET liste expose reason_code / reason_params pour une reco exercice si présents en DB."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    assert user_id is not None

    exercise_data = mock_exercise()
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_data["exercise_type"],
        difficulty=exercise_data["difficulty"],
        age_group=exercise_data.get("age_group", "6-8"),
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    reco_ex = Recommendation(
        user_id=user_id,
        exercise_id=exercise.id,
        challenge_id=None,
        exercise_type=str(exercise.exercise_type),
        difficulty=str(exercise.difficulty),
        reason="Try division at initiate level.",
        priority=4,
        recommendation_type="exercise",
        reason_code="reco.exercise.discovery",
        reason_params={"exercise_type": "division", "target_difficulty": "initie"},
    )
    db_session.add(reco_ex)
    db_session.commit()

    response = await client.get("/api/recommendations")
    assert response.status_code == 200
    row = next((r for r in response.json() if r.get("id") == reco_ex.id), None)
    assert row is not None
    assert row.get("reason_code") == "reco.exercise.discovery"
    assert row.get("reason_params", {}).get("exercise_type") == "division"
    assert row.get("reason")
