"""
Service F32 — Session entrelacée (Interleaved Practice).

Calcule un plan d'exercices par type pour une session guidée.
Types éligibles : au moins 2 tentatives sur 7 jours, taux réussite >= 60%.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

DEFAULT_LENGTH = 10
MIN_ATTEMPTS = 2
MIN_SUCCESS_RATE = 0.6
MIN_ELIGIBLE_TYPES = 2
MAX_TYPES_IN_PLAN = 4


def get_interleaved_plan(
    db: Session,
    user_id: int,
    length: int = DEFAULT_LENGTH,
) -> Dict[str, Any]:
    """
    Retourne un plan entrelacé de types d'exercices pour l'utilisateur.

    Args:
        db: Session SQLAlchemy
        user_id: ID utilisateur
        length: Nombre d'exercices dans le plan (défaut 10)

    Returns:
        Dict avec session_kind, length, eligible_types, plan, message_key
        ou lève InterleavedNotEnoughVariety si < 2 types éligibles
    """
    if length < 1:
        length = DEFAULT_LENGTH

    since = datetime.now(timezone.utc) - timedelta(days=7)

    # Types éligibles : >= 2 tentatives, >= 60% réussite, 7 derniers jours
    result = db.execute(
        text("""
            SELECT
                LOWER(e.exercise_type::text) as ex_type,
                COUNT(*) as attempts,
                SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) as correct
            FROM attempts a
            JOIN exercises e ON e.id = a.exercise_id
            WHERE a.user_id = :user_id
              AND a.created_at >= :since
              AND LOWER(e.exercise_type::text) IN (
                'addition', 'soustraction', 'multiplication', 'division',
                'fractions', 'geometrie', 'texte', 'mixte', 'divers'
              )
            GROUP BY LOWER(e.exercise_type::text)
            HAVING COUNT(*) >= :min_attempts
        """),
        {"user_id": user_id, "since": since, "min_attempts": MIN_ATTEMPTS},
    )
    rows = result.fetchall()

    eligible: List[tuple[str, int, int]] = []
    for row in rows:
        ex_type = row[0] or ""
        attempts = row[1] or 0
        correct = row[2] or 0
        if attempts >= MIN_ATTEMPTS and (correct / attempts) >= MIN_SUCCESS_RATE:
            eligible.append((ex_type, attempts, correct))

    if len(eligible) < MIN_ELIGIBLE_TYPES:
        from app.exceptions import InterleavedNotEnoughVariety

        raise InterleavedNotEnoughVariety(
            "Pas assez de types pratiques récemment pour lancer une session entrelacée."
        )

    # Trier par volume décroissant, prendre jusqu'à 4 types
    eligible.sort(key=lambda x: -x[1])
    types_for_plan = [t[0] for t in eligible[:MAX_TYPES_IN_PLAN]]

    # Round-robin stable : conserve toute la variété et évite les doublons
    # consécutifs tant qu'il y a au moins 2 types distincts.
    plan: List[str] = []
    type_count = len(types_for_plan)
    for idx in range(length):
        chosen = types_for_plan[idx % type_count]
        if plan and chosen == plan[-1] and type_count > 1:
            chosen = types_for_plan[(idx + 1) % type_count]
        plan.append(chosen)

    return {
        "session_kind": "interleaved",
        "length": length,
        "eligible_types": types_for_plan,
        "plan": plan,
        "message_key": "dashboard.quickStart.interleavedPedagogy",
    }
