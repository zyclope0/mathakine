"""
Agrégation challenge_progress — upsert après chaque tentative de défi logique.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.challenge_progress import ChallengeProgress
from app.models.logic_challenge import LogicChallenge, LogicChallengeType
from app.utils.db_helpers import get_python_enum_value


def normalize_challenge_type_key(challenge: LogicChallenge) -> str:
    """Clé stable stockée en base (minuscule, valeur enum)."""
    ct = challenge.challenge_type
    if ct is None:
        return "unknown"
    val = get_python_enum_value(LogicChallengeType, ct)
    return str(val).lower() if val else "unknown"


def _mastery_level_for_rate(rate_pct: float) -> str:
    if rate_pct >= 80.0:
        return "expert"
    if rate_pct >= 55.0:
        return "adept"
    if rate_pct >= 30.0:
        return "apprentice"
    return "novice"


def upsert_challenge_progress(
    db: Session,
    user_id: int,
    challenge_type_key: str,
    is_correct: bool,
) -> None:
    """
    Incrémente total_attempts / correct_attempts, recalcule completion_rate et mastery_level.
    Même transaction que l'enregistrement de la tentative (pas de commit ici).
    """
    bind = db.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    q = db.query(ChallengeProgress).filter(
        ChallengeProgress.user_id == user_id,
        ChallengeProgress.challenge_type == challenge_type_key,
    )
    if is_postgres:
        q = q.with_for_update()
    row = q.one_or_none()
    now = datetime.now(timezone.utc)

    if row is None:
        total = 1
        correct = 1 if is_correct else 0
        rate = (correct / total) * 100.0 if total > 0 else 0.0
        db.add(
            ChallengeProgress(
                user_id=user_id,
                challenge_type=challenge_type_key,
                total_attempts=total,
                correct_attempts=correct,
                completion_rate=round(rate, 2),
                mastery_level=_mastery_level_for_rate(rate),
                last_attempted_at=now,
            )
        )
        db.flush()
        return

    row.total_attempts = int(row.total_attempts or 0) + 1
    if is_correct:
        row.correct_attempts = int(row.correct_attempts or 0) + 1
    total = int(row.total_attempts)
    correct = int(row.correct_attempts)
    rate = (correct / total) * 100.0 if total > 0 else 0.0
    row.completion_rate = round(rate, 2)
    row.mastery_level = _mastery_level_for_rate(rate)
    row.last_attempted_at = now
    db.flush()


def list_challenge_progress_for_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Liste ordonnée des lignes challenge_progress pour l'utilisateur (API)."""
    rows = (
        db.query(ChallengeProgress)
        .filter(ChallengeProgress.user_id == user_id)
        .order_by(ChallengeProgress.challenge_type)
        .all()
    )
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "challenge_type": r.challenge_type,
            "total_attempts": r.total_attempts,
            "correct_attempts": r.correct_attempts,
            "completion_rate": r.completion_rate,
            "mastery_level": r.mastery_level,
            "last_attempted_at": (
                r.last_attempted_at.isoformat() if r.last_attempted_at else None
            ),
        }
        for r in rows
    ]
