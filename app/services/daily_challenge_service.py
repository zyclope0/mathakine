"""
Service des défis quotidiens — F02.

Génère et met à jour les 3 défis quotidiens par utilisateur.
Types : volume_exercises, specific_type, logic_challenge.

Fondements EdTech :
  - Cepeda et al. (2006) : pratique distribuée, rétention à long terme
  - Deci & Ryan (2000) : SDT, défis optionnels sans punition si manqués
"""

import random
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.constants import ExerciseTypes
from app.core.logging_config import get_logger
from app.models.daily_challenge import DailyChallenge
from app.models.user import User

logger = get_logger(__name__)

# Types de défis quotidiens
CHALLENGE_TYPE_VOLUME = "volume_exercises"
CHALLENGE_TYPE_SPECIFIC = "specific_type"
CHALLENGE_TYPE_LOGIC = "logic_challenge"

# Types d'exercices pour specific_type (ceux du diagnostic)
SPECIFIC_TYPES = [
    ExerciseTypes.ADDITION,
    ExerciseTypes.SUBTRACTION,
    ExerciseTypes.MULTIPLICATION,
    ExerciseTypes.DIVISION,
]

# Templates : (challenge_type, target_count_min, target_count_max, bonus_points)
VOLUME_TEMPLATES = [(CHALLENGE_TYPE_VOLUME, 3, 5, 10)]
SPECIFIC_TEMPLATES = [(CHALLENGE_TYPE_SPECIFIC, 2, 4, 15)]
LOGIC_TEMPLATES = [(CHALLENGE_TYPE_LOGIC, 1, 2, 20)]


def get_or_create_today(db: Session, user_id: int) -> list[DailyChallenge]:
    """
    Récupère les défis du jour pour l'utilisateur.
    Les crée si aucun n'existe pour aujourd'hui.
    """
    today = date.today()
    existing = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.user_id == user_id,
            DailyChallenge.date == today,
        )
        .order_by(DailyChallenge.id)
        .all()
    )
    if existing:
        return list(existing)

    return _generate_today(db, user_id, today)


def _generate_today(db: Session, user_id: int, day: date) -> list[DailyChallenge]:
    """Génère 3 défis adaptés au profil utilisateur."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    challenges = []

    # 1. Volume : N exercices quelconques
    t = random.choice(VOLUME_TEMPLATES)
    target = random.randint(t[1], t[2])
    c1 = DailyChallenge(
        user_id=user_id,
        date=day,
        challenge_type=t[0],
        metadata_={},
        target_count=target,
        completed_count=0,
        status="pending",
        bonus_points=t[3],
    )
    db.add(c1)
    challenges.append(c1)

    # 2. Specific type : N exercices d'un type donné
    t = random.choice(SPECIFIC_TEMPLATES)
    target = random.randint(t[1], t[2])
    ex_type = random.choice(SPECIFIC_TYPES)
    c2 = DailyChallenge(
        user_id=user_id,
        date=day,
        challenge_type=t[0],
        metadata_={"exercise_type": ex_type},
        target_count=target,
        completed_count=0,
        status="pending",
        bonus_points=t[3],
    )
    db.add(c2)
    challenges.append(c2)

    # 3. Logic challenge : N défis logiques
    t = random.choice(LOGIC_TEMPLATES)
    target = random.randint(t[1], t[2])
    c3 = DailyChallenge(
        user_id=user_id,
        date=day,
        challenge_type=t[0],
        metadata_={},
        target_count=target,
        completed_count=0,
        status="pending",
        bonus_points=t[3],
    )
    db.add(c3)
    challenges.append(c3)

    db.flush()
    logger.info(
        f"[DailyChallenge] Généré 3 défis pour user={user_id} date={day}: "
        f"volume={c1.target_count}, specific={ex_type}={c2.target_count}, logic={c3.target_count}"
    )
    return challenges


def record_exercise_completed(
    db: Session,
    user_id: int,
    exercise_type: str,
    is_correct: bool,
) -> list[dict]:
    """
    Met à jour les défis du jour après une tentative d'exercice réussie.
    Retourne la liste des défis qui viennent d'être complétés (pour feedback).
    """
    if not is_correct:
        return []

    today = date.today()
    challenges = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.user_id == user_id,
            DailyChallenge.date == today,
            DailyChallenge.status == "pending",
        )
        .all()
    )

    completed_now = []
    ex_type_lower = (exercise_type or "").lower()

    for dc in challenges:
        if dc.challenge_type == CHALLENGE_TYPE_VOLUME:
            dc.completed_count += 1
        elif dc.challenge_type == CHALLENGE_TYPE_SPECIFIC:
            meta = dc.metadata_ or {}
            target_type = (meta.get("exercise_type") or "").lower()
            if target_type and ex_type_lower == target_type:
                dc.completed_count += 1
        else:
            continue

        if dc.completed_count >= dc.target_count:
            dc.status = "completed"
            dc.completed_at = datetime.now(timezone.utc)
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.total_points = (user.total_points or 0) + dc.bonus_points
            completed_now.append(
                {
                    "id": dc.id,
                    "challenge_type": dc.challenge_type,
                    "bonus_points": dc.bonus_points,
                }
            )

    return completed_now


def record_logic_challenge_completed(
    db: Session,
    user_id: int,
    is_correct: bool,
) -> list[dict]:
    """
    Met à jour les défis du jour après une tentative de défi logique réussie.
    Retourne la liste des défis qui viennent d'être complétés.
    """
    if not is_correct:
        return []

    today = date.today()
    challenges = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.user_id == user_id,
            DailyChallenge.date == today,
            DailyChallenge.status == "pending",
            DailyChallenge.challenge_type == CHALLENGE_TYPE_LOGIC,
        )
        .all()
    )

    completed_now = []
    for dc in challenges:
        dc.completed_count += 1
        if dc.completed_count >= dc.target_count:
            dc.status = "completed"
            dc.completed_at = datetime.now(timezone.utc)
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.total_points = (user.total_points or 0) + dc.bonus_points
            completed_now.append(
                {
                    "id": dc.id,
                    "challenge_type": dc.challenge_type,
                    "bonus_points": dc.bonus_points,
                }
            )

    return completed_now


def expire_past_daily_challenges(db: Session) -> int:
    """
    Marque comme expirés les défis des jours passés encore en pending.
    À appeler périodiquement (ex: cron ou au démarrage).
    Retourne le nombre de défis expirés.
    """
    today = date.today()
    updated = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.date < today,
            DailyChallenge.status == "pending",
        )
        .update({"status": "expired"}, synchronize_session=False)
    )
    if updated:
        logger.info(f"[DailyChallenge] {updated} défis expirés")
    return updated
