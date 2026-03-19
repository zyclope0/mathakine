"""
Mapping LogicChallenge → dict API (I4).

Responsabilité unique : adapter le modèle ORM vers les payloads attendus
par le frontend (liste et détail). Extrait de challenge_service pour
réduire la densité et clarifier la séparation mapping / orchestration.
"""

from typing import Any, Dict

from app.services.challenges.challenge_age_group import normalize_age_group_for_frontend
from app.utils.json_utils import safe_parse_json


def challenge_to_list_item(challenge) -> Dict[str, Any]:
    """
    Convertit un LogicChallenge en dict pour l'API liste (GET /api/challenges).
    """
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "challenge_type": challenge.challenge_type,
        "age_group": normalize_age_group_for_frontend(challenge.age_group),
        "difficulty": challenge.difficulty,
        "tags": challenge.tags,
        "difficulty_rating": challenge.difficulty_rating,
        "estimated_time_minutes": challenge.estimated_time_minutes,
        "success_rate": challenge.success_rate,
        "view_count": challenge.view_count,
        "is_archived": challenge.is_archived,
    }


def challenge_to_detail_dict(challenge) -> Dict[str, Any]:
    """
    Convertit un LogicChallenge en dict pour l'API détail (GET /api/challenges/{id}).
    """
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "challenge_type": challenge.challenge_type,
        "age_group": normalize_age_group_for_frontend(challenge.age_group),
        "difficulty": challenge.difficulty,
        "question": challenge.question,
        "correct_answer": challenge.correct_answer,
        "choices": safe_parse_json(challenge.choices, []),
        "solution_explanation": challenge.solution_explanation,
        "visual_data": safe_parse_json(challenge.visual_data, {}),
        "hints": safe_parse_json(challenge.hints, []),
        "tags": challenge.tags,
        "difficulty_rating": challenge.difficulty_rating,
        "estimated_time_minutes": challenge.estimated_time_minutes,
        "success_rate": challenge.success_rate,
        "view_count": challenge.view_count,
        "is_active": challenge.is_active,
        "is_archived": challenge.is_archived,
    }
