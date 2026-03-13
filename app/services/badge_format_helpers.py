"""
Helpers de formatage pour l'affichage des badges (B3.1).
"""

import json
from typing import Optional

from app.models.achievement import Achievement


def format_requirements_to_text(badge: Achievement) -> Optional[str]:
    """Convertit le JSON requirements en texte lisible (critères d'obtention)."""
    if not badge.requirements:
        return None
    try:
        req = (
            json.loads(badge.requirements)
            if isinstance(badge.requirements, str)
            else badge.requirements
        )
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(req, dict):
        return None
    target = req.get("attempts_count")
    if target is not None:
        return f"Résoudre {target} exercices"
    target = req.get("min_attempts")
    rate = req.get("success_rate")
    if target is not None and rate is not None:
        return f"{target} tentatives avec {rate}% de réussite"
    ex_type = req.get("exercise_type", "").lower()
    consec = req.get("consecutive_correct")
    if consec is not None:
        labels = {
            "addition": "additions",
            "soustraction": "soustractions",
            "multiplication": "multiplications",
            "division": "divisions",
        }
        label = labels.get(ex_type, ex_type)
        return f"{consec} {label} consécutives correctes"
    max_t = req.get("max_time")
    if max_t is not None:
        return f"Résoudre un exercice en moins de {max_t} secondes"
    days = req.get("consecutive_days")
    if days is not None:
        return f"{days} jours consécutifs d'activité"
    logic_target = req.get("logic_attempts_count")
    ex_target = req.get("attempts_count")
    if logic_target is not None and ex_target is not None:
        return f"{ex_target} exercices et {logic_target} défis logiques"
    if logic_target is not None:
        return f"Résoudre {logic_target} défis logiques"
    cb = req.get("comeback_days")
    if cb is not None:
        return f"Revenir après {cb} jours sans activité"
    return None
