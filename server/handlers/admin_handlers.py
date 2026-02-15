"""
Handlers pour l'espace admin (rôle archiviste).
"""
from sqlalchemy import func

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge
from app.models.user import User
from app.utils.db_utils import db_session
from server.auth import require_auth, require_admin


@require_auth
@require_admin
async def admin_health(request: Request):
    """
    GET /api/admin/health
    Vérification que les routes admin répondent (test RBAC).
    """
    return JSONResponse({"status": "ok", "admin": True})


@require_auth
@require_admin
async def admin_overview(request: Request):
    """
    GET /api/admin/overview
    KPIs globaux de la plateforme.
    """
    async with db_session() as db:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_exercises = db.query(func.count(Exercise.id)).filter(Exercise.is_archived == False).scalar() or 0
        total_challenges = db.query(func.count(LogicChallenge.id)).filter(LogicChallenge.is_archived == False).scalar() or 0
        # Tentatives (table attempts)
        from app.models.attempt import Attempt
        total_attempts = db.query(func.count(Attempt.id)).scalar() or 0

    return JSONResponse({
        "total_users": total_users,
        "total_exercises": total_exercises,
        "total_challenges": total_challenges,
        "total_attempts": total_attempts,
    })
