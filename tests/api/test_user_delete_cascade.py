"""
Test de suppression de compte utilisateur : vérification qu'aucun reliquat ne reste en base.

Vérifie que DELETE /api/users/me supprime l'utilisateur et toutes les données
associées (cascade) sans orphelins.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import get_password_hash
from app.models.achievement import Achievement, UserAchievement
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
from app.models.notification import Notification
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.user import User, UserRole
from app.models.user_session import UserSession
from app.utils.db_helpers import get_enum_value


@pytest.fixture
def user_to_delete_data():
    """Données d'un utilisateur créé via API puis enrichi en DB."""
    uid = uuid.uuid4().hex[:8]
    return {
        "username": f"del_cascade_{uid}",
        "email": f"del_cascade_{uid}@test.com",
        "password": "SecurePass123!",
    }


async def test_delete_user_me_cascade_no_orphans(
    client, db_session, user_to_delete_data
):
    """
    Suppression via DELETE /api/users/me : aucune ligne orpheline en base.

    Crée un utilisateur avec des données dans :
    - attempts, progress, recommendations, user_achievements,
      user_sessions, notifications, logic_challenge_attempts

    Puis supprime le compte et vérifie que toutes les tables liées
    n'ont plus aucune ligne avec user_id = id supprimé.
    """
    # 1. Créer l'utilisateur via API
    create_resp = await client.post("/api/users/", json=user_to_delete_data)
    assert create_resp.status_code in (200, 201)

    # 2. Vérifier l'email pour pouvoir se connecter et avoir full access (optionnel)
    from tests.utils.test_helpers import verify_user_email_for_tests

    verify_user_email_for_tests(user_to_delete_data["username"])

    # 3. Login
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": user_to_delete_data["username"],
            "password": user_to_delete_data["password"],
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 4. Récupérer l'ID utilisateur
    me_resp = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    user_id = me_resp.json()["id"]

    # 5. Insérer des données liées en DB (exercice partagé pour attempts)
    # Créer un exercice système (sans creator)
    exercise = Exercise(
        title="Ex Cascade",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE, db_session),
        age_group="6-8",
        question="1+1?",
        correct_answer="2",
    )
    db_session.add(exercise)
    db_session.flush()

    attempt = Attempt(
        user_id=user_id,
        exercise_id=exercise.id,
        user_answer="2",
        is_correct=True,
        time_spent=5.0,
    )
    db_session.add(attempt)

    progress = Progress(
        user_id=user_id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE, db_session),
        total_attempts=1,
        correct_attempts=1,
    )
    db_session.add(progress)

    # Achievement existant pour lier un UserAchievement
    achievement = (
        db_session.query(Achievement).filter(Achievement.is_active == True).first()
    )
    if achievement:
        ua = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id,
        )
        db_session.add(ua)

    rec = Recommendation(
        user_id=user_id,
        recommendation_type="exercise",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE, db_session),
        priority=1,
        reason="test",
    )
    db_session.add(rec)

    session_token = f"tok_{uuid.uuid4().hex}"
    user_session = UserSession(
        user_id=user_id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(user_session)

    notif = Notification(
        user_id=user_id,
        type="info",
        title="Test",
        message="Cascade test",
    )
    db_session.add(notif)

    # Défi logique existant (sans creator = user)
    challenge = (
        db_session.query(LogicChallenge)
        .filter(LogicChallenge.is_active == True)
        .first()
    )
    if challenge:
        lca = LogicChallengeAttempt(
            user_id=user_id,
            challenge_id=challenge.id,
            user_solution="{}",
            is_correct=False,
        )
        db_session.add(lca)

    db_session.commit()

    # 6. Supprimer le compte via API
    delete_resp = await client.delete(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
    data = delete_resp.json()
    assert data.get("success") is True

    # 7. Vérifier qu'il n'y a plus de reliquats
    assert db_session.query(User).filter(User.id == user_id).first() is None

    assert db_session.query(Attempt).filter(Attempt.user_id == user_id).count() == 0
    assert db_session.query(Progress).filter(Progress.user_id == user_id).count() == 0
    assert (
        db_session.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .count()
        == 0
    )
    assert (
        db_session.query(UserAchievement)
        .filter(UserAchievement.user_id == user_id)
        .count()
        == 0
    )
    assert (
        db_session.query(UserSession).filter(UserSession.user_id == user_id).count()
        == 0
    )
    assert (
        db_session.query(Notification).filter(Notification.user_id == user_id).count()
        == 0
    )
    assert (
        db_session.query(LogicChallengeAttempt)
        .filter(LogicChallengeAttempt.user_id == user_id)
        .count()
        == 0
    )
