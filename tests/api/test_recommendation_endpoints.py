"""
Tests des endpoints API pour les recommandations.

Routes réelles:
- GET /api/recommendations
- POST /api/recommendations/generate
- POST /api/recommendations/complete (body: { recommendation_id: int })
"""
import pytest
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
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


@pytest.mark.skip(reason="POST /api/recommendations/{id}/clicked non exposé (service existant, route absente)")
async def test_mark_recommendation_as_clicked(padawan_client, db_session, mock_exercise):
    """POST /api/recommendations/{id}/clicked — endpoint non implémenté."""
    pass


async def test_mark_recommendation_as_completed(padawan_client, db_session, mock_exercise):
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
    db_session.refresh(recommendation)
    assert recommendation.is_completed is True
    assert recommendation.completed_at is not None


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
