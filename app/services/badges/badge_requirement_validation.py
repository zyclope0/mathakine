"""
Validation des requirements de badges pour l'admin.

Cluster E4 : extraction depuis admin_content_service.
Responsabilité métier : valider la structure et les valeurs des requirements
avant création ou mise à jour d'un badge (create_badge_for_admin, put_badge_for_admin).

Aligné sur les types supportés par badge_requirement_engine.
"""

from typing import Any, Dict, Optional, Tuple


def validate_badge_requirements(
    req: Optional[Dict[str, Any]],
) -> Tuple[bool, Optional[str]]:
    """
    Valide la structure et les valeurs des requirements d'un badge.

    Returns:
        (True, None) si valide
        (False, message_erreur) si invalide
    """
    if req is None:
        return False, "requirements est requis"
    if not isinstance(req, dict):
        return False, "requirements doit être un objet JSON"
    if len(req) == 0:
        return False, "requirements doit contenir au moins une clé"

    # attempts_count (ordre original : mixte atteint aussi ce bloc en premier)
    if "attempts_count" in req:
        v = req.get("attempts_count")
        if not isinstance(v, (int, float)) or v < 1:
            return False, "attempts_count doit être un nombre >= 1"
        return True, None

    # success_rate (min_attempts + success_rate)
    if "min_attempts" in req and "success_rate" in req:
        ma, sr = req.get("min_attempts"), req.get("success_rate")
        if not isinstance(ma, (int, float)) or ma < 1:
            return False, "min_attempts doit être un nombre >= 1"
        if not isinstance(sr, (int, float)) or sr < 0 or sr > 100:
            return False, "success_rate doit être entre 0 et 100"
        return True, None

    # consecutive
    if "consecutive_correct" in req:
        cc = req.get("consecutive_correct")
        if not isinstance(cc, (int, float)) or cc < 1:
            return False, "consecutive_correct doit être un nombre >= 1"
        return True, None

    # max_time
    if "max_time" in req:
        mt = req.get("max_time")
        if not isinstance(mt, (int, float)) or mt < 0:
            return False, "max_time doit être un nombre >= 0"
        return True, None

    # consecutive_days
    if "consecutive_days" in req:
        cd = req.get("consecutive_days")
        if not isinstance(cd, (int, float)) or cd < 1:
            return False, "consecutive_days doit être un nombre >= 1"
        return True, None

    # logic_attempts_count (seul ou mixte)
    if "logic_attempts_count" in req:
        lac = req.get("logic_attempts_count")
        if not isinstance(lac, (int, float)) or lac < 1:
            return False, "logic_attempts_count doit être un nombre >= 1"
        if "attempts_count" in req:
            ac = req.get("attempts_count")
            if not isinstance(ac, (int, float)) or ac < 1:
                return False, "attempts_count doit être un nombre >= 1 (mixte)"
        return True, None

    # comeback_days
    if "comeback_days" in req:
        cd = req.get("comeback_days")
        if not isinstance(cd, (int, float)) or cd < 1:
            return False, "comeback_days doit être un nombre >= 1"
        return True, None

    # Autres types (perfect_day, all_types, min_per_type) : acceptés sans validation stricte
    return True, None
