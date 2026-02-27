"""
Handlers pour l'espace admin (rôle archiviste).
"""

import csv
import io
import json
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from app.models.admin_audit_log import AdminAuditLog
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.setting import Setting
from app.models.user import User, UserRole
from app.services.email_service import EmailService
from app.utils.db_utils import db_session
from app.utils.email_verification import generate_verification_token
from server.auth import require_admin, require_auth
from server.handlers.admin_handlers_utils import _log_admin_action


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
async def admin_config_get(request: Request):
    """
    GET /api/admin/config
    Liste les paramètres globaux (paramètres du Temple).
    """
    from app.services.admin_service import AdminService

    async with db_session() as db:
        result = AdminService.get_config_for_api(db)
    return JSONResponse({"settings": result})


@require_auth
@require_admin
async def admin_config_put(request: Request):
    """
    PUT /api/admin/config
    Met à jour les paramètres globaux.
    Body: { "settings": { "key": value, ... } }
    """
    from app.services.admin_service import AdminService

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"detail": "Body JSON invalide"}, status_code=400)
    settings_in = body.get("settings") or {}
    if not isinstance(settings_in, dict):
        return JSONResponse(
            {"detail": "'settings' doit être un objet"}, status_code=400
        )

    async with db_session() as db:
        admin_user_id = getattr(request.state, "user", {}).get("id")
        AdminService.update_config(db, settings_in, admin_user_id)

    return JSONResponse({"status": "ok"})


@require_auth
@require_admin
async def admin_overview(request: Request):
    """
    GET /api/admin/overview
    KPIs globaux de la plateforme.
    """
    from app.services.admin_service import AdminService

    async with db_session() as db:
        result = AdminService.get_overview_for_api(db)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_users(request: Request):
    """
    GET /api/admin/users
    Liste paginée des utilisateurs avec filtres (search, role, is_active).
    """
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    search = (query_params.get("search") or "").strip()
    role = (query_params.get("role") or "").strip().lower()
    is_active_param = query_params.get("is_active")
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(100, max(1, int(query_params.get("limit", 20))))
    is_active = (
        str(is_active_param).lower() in ("true", "1", "yes")
        if is_active_param is not None
        else None
    )

    async with db_session() as db:
        result = AdminService.list_users_for_admin(
            db, search=search, role=role, is_active=is_active, skip=skip, limit=limit
        )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_users_patch(request: Request):
    """
    PATCH /api/admin/users/{user_id}
    Mise à jour is_active et/ou role. Un admin ne peut pas se désactiver ni se rétrograder.
    """
    from app.services.admin_service import AdminService

    user_id = int(request.path_params.get("user_id"))
    current_user_id = request.state.user.get("id")

    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            {"error": "Corps JSON invalide."},
            status_code=400,
        )

    is_active = data.get("is_active")
    role_raw = data.get("role")

    if is_active is not None and not isinstance(is_active, bool):
        return JSONResponse(
            {"error": "Le champ is_active doit être un booléen."},
            status_code=400,
        )

    role_map = {
        "padawan": UserRole.PADAWAN,
        "maitre": UserRole.MAITRE,
        "gardien": UserRole.GARDIEN,
        "archiviste": UserRole.ARCHIVISTE,
    }
    new_role = None
    if role_raw is not None:
        r = str(role_raw).strip().lower()
        if r not in role_map:
            return JSONResponse(
                {
                    "error": "Rôle invalide. Valeurs: padawan, maitre, gardien, archiviste."
                },
                status_code=400,
            )
        new_role = role_map[r]

    if is_active is None and new_role is None:
        return JSONResponse(
            {"error": "Fournissez is_active et/ou role à modifier."},
            status_code=400,
        )

    if user_id == current_user_id:
        if is_active is False:
            return JSONResponse(
                {"error": "Vous ne pouvez pas désactiver votre propre compte."},
                status_code=400,
            )
        if new_role is not None and new_role != UserRole.ARCHIVISTE:
            return JSONResponse(
                {"error": "Vous ne pouvez pas rétrograder votre propre rôle."},
                status_code=400,
            )

    async with db_session() as db:
        result, err, code = AdminService.patch_user_for_admin(
            db,
            user_id=user_id,
            admin_user_id=current_user_id,
            is_active=is_active,
            new_role=new_role,
            role_raw=role_raw,
        )
    if err:
        return JSONResponse({"error": err}, status_code=code)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_users_send_reset_password(request: Request):
    """
    POST /api/admin/users/{user_id}/send-reset-password
    Force l'envoi d'un email de réinitialisation de mot de passe (bypass rate limit).
    """
    from app.services.admin_service import AdminService

    user_id = int(request.path_params.get("user_id"))
    async with db_session() as db:
        success, err, code = AdminService.send_reset_password_for_admin(db, user_id)
    if not success:
        return JSONResponse({"error": err}, status_code=code)
    return JSONResponse({"message": "Email de réinitialisation envoyé."})


@require_auth
@require_admin
async def admin_users_resend_verification(request: Request):
    """
    POST /api/admin/users/{user_id}/resend-verification
    Force l'envoi d'un email de vérification d'inscription (bypass cooldown).
    """
    from app.services.admin_service import AdminService

    user_id = int(request.path_params.get("user_id"))
    async with db_session() as db:
        success, already_verified, err, code = (
            AdminService.resend_verification_for_admin(db, user_id)
        )
    if not success:
        return JSONResponse({"error": err}, status_code=code)
    if already_verified:
        return JSONResponse({"message": "L'email est déjà vérifié."})
    return JSONResponse({"message": "Email de vérification envoyé."})


@require_auth
@require_admin
async def admin_exercises(request: Request):
    """
    GET /api/admin/exercises
    Liste paginée avec recherche (titre), tri (sort, order).
    """
    query_params = dict(request.query_params)
    archived_param = query_params.get("archived")
    exercise_type = (query_params.get("type") or "").strip().upper() or None
    search = (query_params.get("search") or "").strip()
    sort = (query_params.get("sort") or "created_at").strip().lower()
    order = (query_params.get("order") or "desc").strip().lower()
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(100, max(1, int(query_params.get("limit", 20))))

    sortable = {"title", "exercise_type", "difficulty", "age_group", "created_at"}
    if sort not in sortable:
        sort = "created_at"
    order_fn = "asc" if order == "asc" else "desc"
    sort_col = getattr(Exercise, sort, Exercise.created_at)
    order_by = getattr(sort_col, order_fn)()

    async with db_session() as db:
        q = db.query(Exercise)
        if archived_param is not None:
            is_archived = str(archived_param).lower() in ("true", "1", "yes")
            q = q.filter(Exercise.is_archived == is_archived)
        if exercise_type:
            q = q.filter(Exercise.exercise_type == exercise_type)
        if search:
            q = q.filter(Exercise.title.ilike(f"%{search}%"))
        total = q.count()
        exercises = q.order_by(order_by).offset(skip).limit(limit).all()
        ex_ids = [e.id for e in exercises]

        attempt_stats = {}
        if ex_ids:
            rows = (
                db.query(
                    Attempt.exercise_id,
                    func.count(Attempt.id).label("attempt_count"),
                    func.sum(case((Attempt.is_correct == True, 1), else_=0)).label(
                        "correct_count"
                    ),
                )
                .filter(Attempt.exercise_id.in_(ex_ids))
                .group_by(Attempt.exercise_id)
                .all()
            )
            for ex_id, a_count, c_count in rows:
                attempt_stats[ex_id] = {
                    "attempt_count": a_count or 0,
                    "correct_count": c_count or 0,
                }

        items = []
        for e in exercises:
            stats = attempt_stats.get(e.id, {"attempt_count": 0, "correct_count": 0})
            a_count = stats["attempt_count"]
            c_count = stats["correct_count"]
            success_rate = round((c_count / a_count * 100), 1) if a_count > 0 else 0.0
            items.append(
                {
                    "id": e.id,
                    "title": e.title,
                    "exercise_type": e.exercise_type,
                    "difficulty": e.difficulty,
                    "age_group": e.age_group,
                    "is_archived": e.is_archived,
                    "attempt_count": a_count,
                    "success_rate": success_rate,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
            )

    return JSONResponse({"items": items, "total": total})


def _exercise_to_detail(e) -> dict:
    """Sérialise un exercice pour l'édition admin."""
    return {
        "id": e.id,
        "title": e.title,
        "exercise_type": e.exercise_type or "",
        "difficulty": e.difficulty or "",
        "age_group": e.age_group or "",
        "tags": e.tags or "",
        "context_theme": e.context_theme or "",
        "complexity": e.complexity,
        "ai_generated": e.ai_generated or False,
        "question": e.question or "",
        "correct_answer": e.correct_answer or "",
        "choices": e.choices,
        "explanation": e.explanation or "",
        "hint": e.hint or "",
        "image_url": e.image_url or "",
        "audio_url": e.audio_url or "",
        "is_active": e.is_active,
        "is_archived": e.is_archived,
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "updated_at": e.updated_at.isoformat() if e.updated_at else None,
    }


@require_auth
@require_admin
async def admin_exercises_post(request: Request):
    """POST /api/admin/exercises — création d'un exercice."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)

    title = (data.get("title") or "").strip()
    question = (data.get("question") or "").strip()
    correct_answer = (data.get("correct_answer") or "").strip()
    exercise_type = (data.get("exercise_type") or "DIVERS").strip().upper()
    difficulty = (data.get("difficulty") or "PADAWAN").strip()
    age_group = (data.get("age_group") or "9-11").strip()

    if not title:
        return JSONResponse({"error": "Le titre est obligatoire."}, status_code=400)
    if not question:
        return JSONResponse({"error": "La question est obligatoire."}, status_code=400)
    if not correct_answer:
        return JSONResponse(
            {"error": "La réponse correcte est obligatoire."}, status_code=400
        )

    async with db_session() as db:
        ex = Exercise(
            title=title,
            exercise_type=exercise_type,
            difficulty=difficulty,
            age_group=age_group,
            question=question,
            correct_answer=correct_answer,
            choices=data.get("choices"),
            explanation=(data.get("explanation") or "").strip() or None,
            hint=(data.get("hint") or "").strip() or None,
            tags=(data.get("tags") or "").strip() or None,
            ai_generated=False,
        )
        db.add(ex)
        db.flush()
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db, admin_id, "exercise_create", "exercise", ex.id, {"title": ex.title}
        )
        db.commit()
        db.refresh(ex)
    return JSONResponse(_exercise_to_detail(ex), status_code=201)


@require_auth
@require_admin
async def admin_exercise_get(request: Request):
    """GET /api/admin/exercises/{exercise_id} — détail complet pour édition."""
    exercise_id = int(request.path_params.get("exercise_id"))
    async with db_session() as db:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return JSONResponse({"error": "Exercice non trouvé."}, status_code=404)
        return JSONResponse(_exercise_to_detail(ex))


@require_auth
@require_admin
async def admin_exercises_put(request: Request):
    """PUT /api/admin/exercises/{exercise_id} — mise à jour complète."""
    exercise_id = int(request.path_params.get("exercise_id"))
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)

    allowed_str = {
        "title",
        "exercise_type",
        "difficulty",
        "age_group",
        "tags",
        "context_theme",
        "complexity",
        "question",
        "correct_answer",
        "explanation",
        "hint",
        "image_url",
        "audio_url",
    }
    allowed_bool = {"is_active", "is_archived"}
    allowed_json = {"choices"}

    update_data = {}
    for k, v in data.items():
        if k in allowed_str and v is not None:
            update_data[k] = str(v) if not isinstance(v, str) else v
        elif k in allowed_bool:
            if v is not None:
                update_data[k] = v in (True, "true", "1", 1)
        elif k in allowed_json:
            update_data[k] = v

    async with db_session() as db:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return JSONResponse({"error": "Exercice non trouvé."}, status_code=404)
        for k, v in update_data.items():
            setattr(ex, k, v)
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db,
            admin_id,
            "exercise_update",
            "exercise",
            exercise_id,
            {"fields": list(update_data.keys())},
        )
        db.commit()
        db.refresh(ex)
    return JSONResponse(_exercise_to_detail(ex))


@require_auth
@require_admin
async def admin_exercises_duplicate(request: Request):
    """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie."""
    exercise_id = int(request.path_params.get("exercise_id"))
    async with db_session() as db:
        orig = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not orig:
            return JSONResponse({"error": "Exercice non trouvé."}, status_code=404)
        copy = Exercise(
            title=f"{orig.title} (copie)",
            exercise_type=orig.exercise_type,
            difficulty=orig.difficulty,
            age_group=orig.age_group,
            tags=orig.tags,
            context_theme=orig.context_theme,
            complexity=orig.complexity,
            ai_generated=orig.ai_generated,
            question=orig.question,
            correct_answer=orig.correct_answer,
            choices=orig.choices,
            explanation=orig.explanation,
            hint=orig.hint,
            image_url=orig.image_url,
            audio_url=orig.audio_url,
            is_active=orig.is_active,
            is_archived=False,
        )
        db.add(copy)
        db.flush()
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db,
            admin_id,
            "exercise_duplicate",
            "exercise",
            copy.id,
            {"from_id": exercise_id, "title": copy.title},
        )
        db.commit()
        db.refresh(copy)
    return JSONResponse(_exercise_to_detail(copy))


@require_auth
@require_admin
async def admin_exercises_patch(request: Request):
    """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived."""
    exercise_id = int(request.path_params.get("exercise_id"))
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)
    is_archived = data.get("is_archived")
    if not isinstance(is_archived, bool):
        return JSONResponse(
            {"error": "Le champ is_archived doit être un booléen."}, status_code=400
        )

    async with db_session() as db:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return JSONResponse({"error": "Exercice non trouvé."}, status_code=404)
        ex.is_archived = is_archived
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db,
            admin_id,
            "exercise_archive",
            "exercise",
            exercise_id,
            {"is_archived": is_archived},
        )
        db.commit()
        db.refresh(ex)

    return JSONResponse(
        {
            "id": ex.id,
            "title": ex.title,
            "is_archived": ex.is_archived,
        }
    )


# ==================== ADMIN BADGES (Lot B-1) — via AdminService ====================


@require_auth
@require_admin
async def admin_badges(request: Request):
    """
    GET /api/admin/badges
    Liste tous les badges (actifs et inactifs).
    """
    from app.services.admin_service import AdminService

    async with db_session() as db:
        result = AdminService.list_badges_for_admin(db)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_badges_post(request: Request):
    """POST /api/admin/badges — création d'un badge."""
    from app.services.admin_service import AdminService

    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.create_badge_for_admin(
            db, data=data, admin_user_id=admin_id
        )
    if err:
        return JSONResponse({"error": err}, status_code=code)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_badge_get(request: Request):
    """GET /api/admin/badges/{badge_id} — détail pour édition."""
    from app.services.admin_service import AdminService

    badge_id = int(request.path_params.get("badge_id"))
    async with db_session() as db:
        result, err, code = AdminService.get_badge_for_admin(db, badge_id=badge_id)
    if err:
        return JSONResponse({"error": err}, status_code=code)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_badges_put(request: Request):
    """PUT /api/admin/badges/{badge_id} — mise à jour complète."""
    from app.services.admin_service import AdminService

    badge_id = int(request.path_params.get("badge_id"))
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.put_badge_for_admin(
            db, badge_id=badge_id, data=data, admin_user_id=admin_id
        )
    if err:
        return JSONResponse({"error": err}, status_code=code)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_badges_delete(request: Request):
    """
    DELETE /api/admin/badges/{badge_id}
    Soft delete : is_active = False (recommandé).
    """
    from app.services.admin_service import AdminService

    badge_id = int(request.path_params.get("badge_id"))
    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.delete_badge_for_admin(
            db, badge_id=badge_id, admin_user_id=admin_id
        )
    if err:
        return JSONResponse({"error": err}, status_code=code)
    return JSONResponse(result)


def _challenge_to_detail(c) -> dict:
    """Sérialise un défi pour l'édition admin."""
    ct_val = (
        c.challenge_type.value
        if hasattr(c.challenge_type, "value")
        else str(c.challenge_type)
    )
    ag_val = c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description or "",
        "challenge_type": ct_val,
        "age_group": ag_val,
        "difficulty": c.difficulty or "",
        "content": c.content or "",
        "question": c.question or "",
        "solution": c.solution or "",
        "correct_answer": c.correct_answer or "",
        "choices": c.choices,
        "solution_explanation": c.solution_explanation or "",
        "visual_data": c.visual_data,
        "hints": c.hints,
        "image_url": c.image_url or "",
        "tags": c.tags or "",
        "is_active": c.is_active,
        "is_archived": c.is_archived,
        "difficulty_rating": c.difficulty_rating,
        "estimated_time_minutes": c.estimated_time_minutes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@require_auth
@require_admin
async def admin_challenges_post(request: Request):
    """POST /api/admin/challenges — création d'un défi."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    challenge_type_raw = (data.get("challenge_type") or "puzzle").strip().lower()
    age_group_raw = (data.get("age_group") or "GROUP_10_12").strip()

    if not title:
        return JSONResponse({"error": "Le titre est obligatoire."}, status_code=400)
    if not description:
        return JSONResponse(
            {"error": "La description est obligatoire."}, status_code=400
        )

    try:
        ct = LogicChallengeType(challenge_type_raw)
    except ValueError:
        ct = LogicChallengeType.PUZZLE
    try:
        ag = AgeGroup(age_group_raw)
    except ValueError:
        ag = AgeGroup.GROUP_10_12

    async with db_session() as db:
        ch = LogicChallenge(
            title=title,
            description=description,
            challenge_type=ct,
            age_group=ag,
            question=(data.get("question") or "").strip() or None,
            content=(data.get("content") or "").strip() or None,
            solution=(data.get("solution") or "").strip() or None,
            correct_answer=(data.get("correct_answer") or "").strip() or None,
            solution_explanation=(data.get("solution_explanation") or "").strip()
            or None,
            visual_data=data.get("visual_data"),
            hints=data.get("hints"),
        )
        db.add(ch)
        db.flush()
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db, admin_id, "challenge_create", "challenge", ch.id, {"title": ch.title}
        )
        db.commit()
        db.refresh(ch)
    return JSONResponse(_challenge_to_detail(ch), status_code=201)


@require_auth
@require_admin
async def admin_challenge_get(request: Request):
    """GET /api/admin/challenges/{challenge_id} — détail complet pour édition."""
    challenge_id = int(request.path_params.get("challenge_id"))
    async with db_session() as db:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return JSONResponse({"error": "Défi non trouvé."}, status_code=404)
        return JSONResponse(_challenge_to_detail(ch))


@require_auth
@require_admin
async def admin_challenges_put(request: Request):
    """PUT /api/admin/challenges/{challenge_id} — mise à jour complète."""
    challenge_id = int(request.path_params.get("challenge_id"))
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)

    allowed_str = {
        "title",
        "description",
        "difficulty",
        "content",
        "question",
        "solution",
        "correct_answer",
        "solution_explanation",
        "image_url",
        "tags",
    }
    allowed_bool = {"is_active", "is_archived"}
    allowed_int = {"difficulty_rating", "estimated_time_minutes"}
    allowed_json = {"choices", "visual_data", "hints"}

    update_data = {}
    for k, v in data.items():
        if k in allowed_str and v is not None:
            update_data[k] = str(v) if not isinstance(v, str) else v
        elif k in allowed_bool:
            if v is not None:
                update_data[k] = v in (True, "true", "1", 1)
        elif k in allowed_int and v is not None:
            update_data[k] = int(v) if isinstance(v, (int, float)) else v
        elif k in allowed_json:
            update_data[k] = v
        elif k == "challenge_type" and v is not None:
            try:
                update_data[k] = LogicChallengeType(str(v).lower())
            except ValueError:
                pass
        elif k == "age_group" and v is not None:
            try:
                sv = str(v).strip()
                update_data[k] = AgeGroup(sv)
            except ValueError:
                pass

    async with db_session() as db:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return JSONResponse({"error": "Défi non trouvé."}, status_code=404)
        for k, v in update_data.items():
            setattr(ch, k, v)
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db,
            admin_id,
            "challenge_update",
            "challenge",
            challenge_id,
            {"fields": list(update_data.keys())},
        )
        db.commit()
        db.refresh(ch)
    return JSONResponse(_challenge_to_detail(ch))


@require_auth
@require_admin
async def admin_challenges_duplicate(request: Request):
    """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie."""
    challenge_id = int(request.path_params.get("challenge_id"))
    async with db_session() as db:
        orig = (
            db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        )
        if not orig:
            return JSONResponse({"error": "Défi non trouvé."}, status_code=404)
        copy = LogicChallenge(
            title=f"{orig.title} (copie)",
            description=orig.description,
            challenge_type=orig.challenge_type,
            age_group=orig.age_group,
            difficulty=orig.difficulty,
            content=orig.content,
            question=orig.question,
            solution=orig.solution,
            correct_answer=orig.correct_answer,
            choices=orig.choices,
            solution_explanation=orig.solution_explanation,
            visual_data=orig.visual_data,
            hints=orig.hints,
            image_url=orig.image_url,
            tags=orig.tags,
            is_active=orig.is_active,
            is_archived=False,
            difficulty_rating=orig.difficulty_rating,
            estimated_time_minutes=orig.estimated_time_minutes,
        )
        db.add(copy)
        db.flush()
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db,
            admin_id,
            "challenge_duplicate",
            "challenge",
            copy.id,
            {"from_id": challenge_id, "title": copy.title},
        )
        db.commit()
        db.refresh(copy)
    return JSONResponse(_challenge_to_detail(copy))


@require_auth
@require_admin
async def admin_challenges(request: Request):
    """
    GET /api/admin/challenges
    Liste paginée avec recherche (titre), tri (sort, order).
    """
    from sqlalchemy import or_

    query_params = dict(request.query_params)
    archived_param = query_params.get("archived")
    challenge_type_param = (query_params.get("type") or "").strip().lower() or None
    search = (query_params.get("search") or "").strip()
    sort = (query_params.get("sort") or "created_at").strip().lower()
    order = (query_params.get("order") or "desc").strip().lower()
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(100, max(1, int(query_params.get("limit", 20))))

    sortable = {"title", "challenge_type", "age_group", "created_at"}
    if sort not in sortable:
        sort = "created_at"
    order_fn = "asc" if order == "asc" else "desc"
    sort_col = getattr(LogicChallenge, sort, LogicChallenge.created_at)
    order_by = getattr(sort_col, order_fn)()

    async with db_session() as db:
        q = db.query(LogicChallenge)
        if archived_param is not None:
            is_archived = str(archived_param).lower() in ("true", "1", "yes")
            q = q.filter(LogicChallenge.is_archived == is_archived)
        if challenge_type_param:
            try:
                ct = LogicChallengeType(challenge_type_param)
                q = q.filter(LogicChallenge.challenge_type == ct)
            except ValueError:
                pass
        if search:
            pattern = f"%{search}%"
            q = q.filter(
                or_(
                    LogicChallenge.title.ilike(pattern),
                    LogicChallenge.description.ilike(pattern),
                )
            )
        total = q.count()
        challenges = q.order_by(order_by).offset(skip).limit(limit).all()
        ch_ids = [c.id for c in challenges]

        attempt_stats = {}
        if ch_ids:
            rows = (
                db.query(
                    LogicChallengeAttempt.challenge_id,
                    func.count(LogicChallengeAttempt.id).label("attempt_count"),
                    func.sum(
                        case((LogicChallengeAttempt.is_correct == True, 1), else_=0)
                    ).label("correct_count"),
                )
                .filter(LogicChallengeAttempt.challenge_id.in_(ch_ids))
                .group_by(LogicChallengeAttempt.challenge_id)
                .all()
            )
            for ch_id, a_count, c_count in rows:
                attempt_stats[ch_id] = {
                    "attempt_count": a_count or 0,
                    "correct_count": c_count or 0,
                }

        items = []
        for c in challenges:
            stats = attempt_stats.get(c.id, {"attempt_count": 0, "correct_count": 0})
            a_count = stats["attempt_count"]
            c_count = stats["correct_count"]
            success_rate = round((c_count / a_count * 100), 1) if a_count > 0 else 0.0
            ct_val = (
                c.challenge_type.value
                if hasattr(c.challenge_type, "value")
                else str(c.challenge_type)
            )
            ag_val = (
                c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
            )
            items.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "challenge_type": ct_val,
                    "age_group": ag_val,
                    "is_archived": c.is_archived,
                    "attempt_count": a_count,
                    "success_rate": success_rate,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
            )

    return JSONResponse({"items": items, "total": total})


@require_auth
@require_admin
async def admin_challenges_patch(request: Request):
    """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived."""
    challenge_id = int(request.path_params.get("challenge_id"))
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Corps JSON invalide."}, status_code=400)
    is_archived = data.get("is_archived")
    if not isinstance(is_archived, bool):
        return JSONResponse(
            {"error": "Le champ is_archived doit être un booléen."}, status_code=400
        )

    async with db_session() as db:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return JSONResponse({"error": "Défi non trouvé."}, status_code=404)
        ch.is_archived = is_archived
        admin_id = getattr(request.state, "user", {}).get("id")
        _log_admin_action(
            db,
            admin_id,
            "challenge_archive",
            "challenge",
            challenge_id,
            {"is_archived": is_archived},
        )
        db.commit()
        db.refresh(ch)

    return JSONResponse(
        {
            "id": ch.id,
            "title": ch.title,
            "is_archived": ch.is_archived,
        }
    )


@require_auth
@require_admin
async def admin_audit_log(request: Request):
    """
    GET /api/admin/audit-log?skip=&limit=&action=&resource_type=
    Journal des actions admin (qui a fait quoi, quand).
    """
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(200, max(1, int(query_params.get("limit", 50))))
    action_filter = (query_params.get("action") or "").strip() or None
    resource_filter = (query_params.get("resource_type") or "").strip() or None

    async with db_session() as db:
        result = AdminService.get_audit_log_for_api(
            db,
            skip=skip,
            limit=limit,
            action_filter=action_filter,
            resource_filter=resource_filter,
        )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_moderation(request: Request):
    """
    GET /api/admin/moderation?type=exercises|challenges
    Liste du contenu généré par IA pour modération (validation, signalement).
    """
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    mod_type = (query_params.get("type") or "all").strip().lower()
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(100, max(1, int(query_params.get("limit", 50))))

    async with db_session() as db:
        result = AdminService.get_moderation_for_api(
            db, mod_type=mod_type, skip=skip, limit=limit
        )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_reports(request: Request):
    """
    GET /api/admin/reports?period=7d|30d
    Rapports par période : inscriptions, activité, taux succès.
    """
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    period = (query_params.get("period") or "7d").strip().lower()

    if period not in ("7d", "30d"):
        return JSONResponse(
            {"error": "period invalide. Valeurs: 7d, 30d."},
            status_code=400,
        )

    async with db_session() as db:
        result = AdminService.get_reports_for_api(db, period=period)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_export(request: Request):
    """
    GET /api/admin/export?type=users|exercises|attempts|overview&period=7d|30d|all
    Export CSV streamé. Limite 10 000 lignes par export.
    """
    query_params = dict(request.query_params)
    export_type = (query_params.get("type") or "users").strip().lower()
    period = (query_params.get("period") or "all").strip().lower()

    if export_type not in ("users", "exercises", "attempts", "overview"):
        return JSONResponse(
            {"error": "type invalide. Valeurs: users, exercises, attempts, overview."},
            status_code=400,
        )

    admin_id = getattr(request.state, "user", {}).get("id")
    async with db_session() as _db:
        _log_admin_action(
            _db,
            admin_id,
            "export_csv",
            None,
            None,
            {"type": export_type, "period": period},
        )
        _db.commit()

    since = None
    if period == "7d":
        since = datetime.now(timezone.utc) - timedelta(days=7)
    elif period == "30d":
        since = datetime.now(timezone.utc) - timedelta(days=30)

    MAX_ROWS = 10_000
    rows_data = []

    async with db_session() as db:
        if export_type == "users":
            q = db.query(User)
            if since:
                q = q.filter(User.created_at >= since)
            rows = q.order_by(User.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    u.id,
                    u.username or "",
                    u.email or "",
                    u.full_name or "",
                    u.role.value if u.role else "",
                    u.is_active,
                    u.created_at.isoformat() if u.created_at else "",
                ]
                for u in rows
            ]
            headers = [
                "id",
                "username",
                "email",
                "full_name",
                "role",
                "is_active",
                "created_at",
            ]
        elif export_type == "exercises":
            q = db.query(Exercise)
            if since:
                q = q.filter(Exercise.created_at >= since)
            rows = q.order_by(Exercise.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    e.id,
                    (e.title or "").replace("\n", " "),
                    e.exercise_type or "",
                    e.difficulty or "",
                    e.age_group or "",
                    e.is_archived,
                    e.created_at.isoformat() if e.created_at else "",
                ]
                for e in rows
            ]
            headers = [
                "id",
                "title",
                "exercise_type",
                "difficulty",
                "age_group",
                "is_archived",
                "created_at",
            ]
        elif export_type == "attempts":
            q = db.query(Attempt)
            if since:
                q = q.filter(Attempt.created_at >= since)
            rows = q.order_by(Attempt.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    a.id,
                    a.user_id,
                    a.exercise_id,
                    a.is_correct,
                    a.time_spent or "",
                    a.created_at.isoformat() if a.created_at else "",
                ]
                for a in rows
            ]
            headers = [
                "id",
                "user_id",
                "exercise_id",
                "is_correct",
                "time_spent",
                "created_at",
            ]
        else:  # overview
            total_users = db.query(func.count(User.id)).scalar() or 0
            total_exercises = db.query(func.count(Exercise.id)).scalar() or 0
            total_challenges = db.query(func.count(LogicChallenge.id)).scalar() or 0
            total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
            headers = ["metric", "value", "period"]
            rows_data = [
                ["total_users", total_users, period],
                ["total_exercises", total_exercises, period],
                ["total_challenges", total_challenges, period],
                ["total_attempts", total_attempts, period],
            ]

    def generate_csv():
        buf = io.StringIO()
        writer = csv.writer(buf)
        yield "\ufeff"
        writer.writerow(headers)
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)
        for row in rows_data:
            writer.writerow(row)
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    filename = f"mathakine_export_{export_type}_{period}.csv"
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
