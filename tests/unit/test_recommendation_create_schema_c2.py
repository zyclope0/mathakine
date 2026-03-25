"""Lot C2 — RecommendationCreate accepte challenge_id et recommendation_type."""

from app.schemas.recommendation import RecommendationCreate


def test_recommendation_create_accepts_challenge_fields():
    m = RecommendationCreate(
        user_id=1,
        exercise_type="ADDITION",
        difficulty="INITIE",
        exercise_id=None,
        challenge_id=99,
        recommendation_type="challenge",
    )
    assert m.challenge_id == 99
    assert m.recommendation_type == "challenge"


def test_recommendation_create_challenge_fields_optional():
    m = RecommendationCreate(
        user_id=1,
        exercise_type="ADDITION",
        difficulty="INITIE",
    )
    assert m.challenge_id is None
    assert m.recommendation_type is None
