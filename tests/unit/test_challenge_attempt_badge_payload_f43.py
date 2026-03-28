"""F43-A4 — alias contractuel thematic_title / star_wars_title sur new_badges."""

from app.services.challenges.challenge_attempt_service import _badge_dict_to_earned


def test_badge_dict_to_earned_f43_thematic_title_matches_legacy() -> None:
    earned = _badge_dict_to_earned(
        {
            "id": 1,
            "code": "x",
            "name": "N",
            "description": "D",
            "star_wars_title": "Subtitle",
            "difficulty": "bronze",
            "points_reward": 5,
            "earned_at": "2026-01-01T00:00:00+00:00",
        }
    )
    dumped = earned.model_dump(mode="json")
    assert dumped["thematic_title"] == "Subtitle"
    assert dumped["star_wars_title"] == "Subtitle"


def test_badge_dict_to_earned_prefers_thematic_title_key_when_present() -> None:
    earned = _badge_dict_to_earned(
        {
            "id": 1,
            "thematic_title": "Primary",
            "star_wars_title": "Legacy",
        }
    )
    dumped = earned.model_dump(mode="json")
    assert dumped["thematic_title"] == "Primary"
    assert dumped["star_wars_title"] == "Primary"
