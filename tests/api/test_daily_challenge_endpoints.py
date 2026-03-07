from datetime import date

from app.models.daily_challenge import DailyChallenge


async def test_get_daily_challenges_creates_and_reuses_todays_batch(
    padawan_client, db_session
):
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]

    first_response = await client.get("/api/daily-challenges")
    assert first_response.status_code == 200
    first_payload = first_response.json()
    first_challenges = first_payload.get("challenges")

    assert isinstance(first_challenges, list)
    assert len(first_challenges) == 3

    second_response = await client.get("/api/daily-challenges")
    assert second_response.status_code == 200
    second_payload = second_response.json()
    second_challenges = second_payload.get("challenges")

    assert isinstance(second_challenges, list)
    assert len(second_challenges) == 3
    assert [item["id"] for item in first_challenges] == [
        item["id"] for item in second_challenges
    ]

    persisted_count = (
        db_session.query(DailyChallenge)
        .filter(DailyChallenge.user_id == user_id, DailyChallenge.date == date.today())
        .count()
    )
    assert persisted_count == 3
