"""
Mapping LogicChallenge → dict API (I4).

Responsabilité unique : adapter le modèle ORM vers les payloads attendus
par le frontend (liste et détail). Extrait de challenge_service pour
réduire la densité et clarifier la séparation mapping / orchestration.
"""

from typing import Any, Dict, Union

from app.services.challenges.challenge_age_group import normalize_age_group_for_frontend
from app.services.challenges.challenge_contract_policy import (
    RESPONSE_MODE_SINGLE_CHOICE,
    RESPONSE_MODES,
    compute_response_mode,
    sanitize_choices_for_delivery,
)
from app.utils.json_utils import safe_parse_json


def _challenge_type_api_value(challenge: Any) -> str:
    ct = getattr(challenge, "challenge_type", "")
    if hasattr(ct, "value"):
        return str(ct.value)
    return str(ct)


def _generation_params_dict(challenge: Any) -> Dict[str, Any]:
    raw = getattr(challenge, "generation_parameters", None)
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        return safe_parse_json(raw, {})
    return {}


def resolve_challenge_response_mode(challenge: Any) -> str:
    """
    Modalité d'interaction pour le frontend (IA9 / IA9b).

    Priorité : ``generation_parameters.response_mode`` si présent et valide ;
    ``single_choice`` n'est honoré que si les ``choices`` passent policy + qualité QCM.
    Sinon recalcul depuis type, ``visual_data``, difficulté et choix **sanitisés**.
    """
    ct = _challenge_type_api_value(challenge)
    vd = safe_parse_json(getattr(challenge, "visual_data", None), {})
    dr = getattr(challenge, "difficulty_rating", None)
    drf: Union[float, None]
    if isinstance(dr, (int, float)) and 1.0 <= float(dr) <= 5.0:
        drf = float(dr)
    else:
        drf = None

    ca = getattr(challenge, "correct_answer", None)
    ca_str = str(ca).strip() if ca is not None else ""
    ch_raw = safe_parse_json(getattr(challenge, "choices", None), [])
    sanitized = sanitize_choices_for_delivery(ct, drf, ch_raw, ca_str)

    gp = _generation_params_dict(challenge)
    rm = gp.get("response_mode")
    if isinstance(rm, str) and rm in RESPONSE_MODES:
        if ct.upper() == "CODING":
            return compute_response_mode(ct, vd, drf, sanitized)
        if rm == RESPONSE_MODE_SINGLE_CHOICE:
            if sanitized:
                return RESPONSE_MODE_SINGLE_CHOICE
            # GP obsolète (choices invalides / legacy) : ne pas activer de QCM fantôme
        else:
            return rm

    return compute_response_mode(ct, vd, drf, sanitized)


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
        "difficulty_tier": getattr(challenge, "difficulty_tier", None),
    }


def challenge_to_detail_dict(challenge) -> Dict[str, Any]:
    """
    Convertit un LogicChallenge en dict pour l'API détail (GET /api/challenges/{id}).

    Les ``choices`` sont sanitisés (IA9 + IA9b : policy + qualité QCM).
    """
    ct = _challenge_type_api_value(challenge)
    dr = getattr(challenge, "difficulty_rating", None)
    drf: Union[float, None]
    if isinstance(dr, (int, float)) and 1.0 <= float(dr) <= 5.0:
        drf = float(dr)
    else:
        drf = None
    ch_raw = safe_parse_json(challenge.choices, [])
    ca = getattr(challenge, "correct_answer", None)
    ca_str = str(ca).strip() if ca is not None else ""
    choices_out: list = sanitize_choices_for_delivery(ct, drf, ch_raw, ca_str)

    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "challenge_type": challenge.challenge_type,
        "age_group": normalize_age_group_for_frontend(challenge.age_group),
        "difficulty": challenge.difficulty,
        "question": challenge.question,
        "correct_answer": challenge.correct_answer,
        "choices": choices_out,
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
        "response_mode": resolve_challenge_response_mode(challenge),
        "difficulty_tier": getattr(challenge, "difficulty_tier", None),
    }
