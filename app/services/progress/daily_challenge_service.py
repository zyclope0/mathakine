"""
Service des defis quotidiens - F02.

Genere et met a jour les 3 defis quotidiens par utilisateur.
Types : volume_exercises, specific_type, logic_challenge.

Fondements EdTech :
  - Cepeda et al. (2006) : pratique distribuee, retention a long terme
  - Deci & Ryan (2000) : SDT, defis optionnels sans punition si manques
"""

import random
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.constants import ExerciseTypes
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.models.daily_challenge import DailyChallenge
from app.models.user import User
from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType

logger = get_logger(__name__)


def _grant_daily_challenge_bonus(
    db: Session,
    user_id: int,
    dc: DailyChallenge,
) -> None:
    """Crédite les points bonus via le moteur gamification unique + ledger."""
    pts = int(dc.bonus_points or 0)
    if pts <= 0:
        return
    GamificationService.apply_points(
        db,
        user_id,
        pts,
        PointEventSourceType.DAILY_CHALLENGE_COMPLETED,
        source_id=dc.id,
        details={
            "challenge_type": dc.challenge_type,
            "date": dc.date.isoformat() if dc.date else None,
        },
    )


# Types de defis quotidiens
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


def _daily_challenge_to_dict(dc: DailyChallenge) -> dict:
    """Serialise un DailyChallenge pour l'API (dans le contexte session)."""
    return {
        "id": dc.id,
        "date": dc.date.isoformat() if dc.date else None,
        "challenge_type": dc.challenge_type,
        "metadata": dc.metadata_ or {},
        "target_count": dc.target_count,
        "completed_count": dc.completed_count,
        "status": dc.status,
        "bonus_points": dc.bonus_points,
    }


def get_or_create_today_for_user_sync(user_id: int) -> list[dict]:
    """
    Use case sync: recupere ou cree les defis du jour pour l'utilisateur.
    Retourne une liste de dicts serialises (evite DetachedInstanceError hors session).
    Execute via run_db_bound() depuis les handlers async.
    """
    with sync_db_session() as db:
        challenges = get_or_create_today_for_user(db, user_id)
        return [_daily_challenge_to_dict(c) for c in challenges]


def get_or_create_today(db: Session, user_id: int) -> list[DailyChallenge]:
    """
    Recupere les defis du jour pour l'utilisateur.
    Les cree si aucun n'existe pour aujourd'hui.
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


def get_or_create_today_for_user(db: Session, user_id: int) -> list[DailyChallenge]:
    """
    Orchestrateur transactionnel du flux daily challenge.
    Le handler HTTP ne commit plus directement ce flux.
    """
    challenges = get_or_create_today(db, user_id)
    db.commit()
    return challenges


def _generate_today(db: Session, user_id: int, day: date) -> list[DailyChallenge]:
    """Genere 3 defis adaptes au profil utilisateur."""
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

    # 2. Specific type : N exercices d'un type donne
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

    # 3. Logic challenge : N defis logiques
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
        "[DailyChallenge] Genere 3 defis pour user=%s date=%s: volume=%s, specific=%s=%s, logic=%s",
        user_id,
        day,
        c1.target_count,
        ex_type,
        c2.target_count,
        c3.target_count,
    )
    return challenges


def record_exercise_completed(
    db: Session,
    user_id: int,
    exercise_type: str,
    is_correct: bool,
) -> list[dict]:
    """
    Met a jour les defis du jour apres une tentative d'exercice reussie.
    Retourne la liste des defis qui viennent d'etre completes (pour feedback).
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
            _grant_daily_challenge_bonus(db, user_id, dc)
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
    Met a jour les defis du jour apres une tentative de defi logique reussie.
    Retourne la liste des defis qui viennent d'etre completes.
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
            _grant_daily_challenge_bonus(db, user_id, dc)
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
    Marque comme expires les defis des jours passes encore en pending.
    A appeler periodiquement (ex: cron ou au demarrage).
    Retourne le nombre de defis expires.
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
        logger.info("[DailyChallenge] %s defis expires", updated)
    return updated
