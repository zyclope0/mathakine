"""
Handlers pour l'espace admin (rôle archiviste).
"""

import csv
import io
import json
import os

from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from app.models.admin_audit_log import AdminAuditLog
from app.models.setting import Setting
from app.models.user import User, UserRole
from app.services.email_service import EmailService
from app.utils.db_utils import db_session
from app.utils.email_verification import generate_verification_token
from app.utils.error_handler import api_error_response
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
        return api_error_response(400, "Body JSON invalide")
    settings_in = body.get("settings") or {}
    if not isinstance(settings_in, dict):
        return api_error_response(400, "'settings' doit être un objet")

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
        return api_error_response(400, "Corps JSON invalide.")

    is_active = data.get("is_active")
    role_raw = data.get("role")

    if is_active is not None and not isinstance(is_active, bool):
        return api_error_response(400, "Le champ is_active doit être un booléen.")

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
            return api_error_response(
                400, "Rôle invalide. Valeurs: padawan, maitre, gardien, archiviste."
            )
        new_role = role_map[r]

    if is_active is None and new_role is None:
        return api_error_response(400, "Fournissez is_active et/ou role à modifier.")

    if user_id == current_user_id:
        if is_active is False:
            return api_error_response(
                400, "Vous ne pouvez pas désactiver votre propre compte."
            )
        if new_role is not None and new_role != UserRole.ARCHIVISTE:
            return api_error_response(
                400, "Vous ne pouvez pas rétrograder votre propre rôle."
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
        return api_error_response(code, err)
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
        return api_error_response(code, err)
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
        return api_error_response(code, err)
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
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    archived_param = query_params.get("archived")
    exercise_type = (query_params.get("type") or "").strip().upper() or None
    search = (query_params.get("search") or "").strip()
    sort = (query_params.get("sort") or "created_at").strip().lower()
    order = (query_params.get("order") or "desc").strip().lower()
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(100, max(1, int(query_params.get("limit", 20))))

    is_archived = None
    if archived_param is not None:
        is_archived = str(archived_param).lower() in ("true", "1", "yes")

    async with db_session() as db:
        result = AdminService.list_exercises_for_admin(
            db,
            archived=is_archived,
            exercise_type=exercise_type,
            search=search,
            sort=sort,
            order=order,
            skip=skip,
            limit=limit,
        )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_exercises_post(request: Request):
    """POST /api/admin/exercises — création d'un exercice."""
    from app.services.admin_service import AdminService

    try:
        data = await request.json()
    except Exception:
        return api_error_response(400, "Corps JSON invalide.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.create_exercise_for_admin(
            db, data=data, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_exercise_get(request: Request):
    """GET /api/admin/exercises/{exercise_id} — détail complet pour édition."""
    from app.services.admin_service import AdminService

    exercise_id = int(request.path_params.get("exercise_id"))
    async with db_session() as db:
        result, err, code = AdminService.get_exercise_for_admin(db, exercise_id)
    if err:
        return api_error_response(code, err)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_exercises_put(request: Request):
    """PUT /api/admin/exercises/{exercise_id} — mise à jour complète."""
    from app.services.admin_service import AdminService

    exercise_id = int(request.path_params.get("exercise_id"))
    try:
        data = await request.json()
    except Exception:
        return api_error_response(400, "Corps JSON invalide.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.put_exercise_for_admin(
            db, exercise_id=exercise_id, data=data, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_exercises_duplicate(request: Request):
    """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie."""
    from app.services.admin_service import AdminService

    exercise_id = int(request.path_params.get("exercise_id"))
    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.duplicate_exercise_for_admin(
            db, exercise_id=exercise_id, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_exercises_patch(request: Request):
    """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived."""
    from app.services.admin_service import AdminService

    exercise_id = int(request.path_params.get("exercise_id"))
    try:
        data = await request.json()
    except Exception:
        return api_error_response(400, "Corps JSON invalide.")
    is_archived = data.get("is_archived")
    if not isinstance(is_archived, bool):
        return api_error_response(400, "Le champ is_archived doit être un booléen.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.patch_exercise_for_admin(
            db, exercise_id=exercise_id, is_archived=is_archived, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result)


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
        return api_error_response(400, "Corps JSON invalide.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.create_badge_for_admin(
            db, data=data, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
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
        return api_error_response(code, err)
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
        return api_error_response(400, "Corps JSON invalide.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.put_badge_for_admin(
            db, badge_id=badge_id, data=data, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
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
        return api_error_response(code, err)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_post(request: Request):
    """POST /api/admin/challenges — création d'un défi."""
    from app.services.admin_service import AdminService

    try:
        data = await request.json()
    except Exception:
        return api_error_response(400, "Corps JSON invalide.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.create_challenge_for_admin(
            db, data=data, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_challenge_get(request: Request):
    """GET /api/admin/challenges/{challenge_id} — détail complet pour édition."""
    from app.services.admin_service import AdminService

    challenge_id = int(request.path_params.get("challenge_id"))
    async with db_session() as db:
        result, err, code = AdminService.get_challenge_for_admin(db, challenge_id)
    if err:
        return api_error_response(code, err)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_put(request: Request):
    """PUT /api/admin/challenges/{challenge_id} — mise à jour complète."""
    from app.services.admin_service import AdminService

    challenge_id = int(request.path_params.get("challenge_id"))
    try:
        data = await request.json()
    except Exception:
        return api_error_response(400, "Corps JSON invalide.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.put_challenge_for_admin(
            db, challenge_id=challenge_id, data=data, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_duplicate(request: Request):
    """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie."""
    from app.services.admin_service import AdminService

    challenge_id = int(request.path_params.get("challenge_id"))
    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.duplicate_challenge_for_admin(
            db, challenge_id=challenge_id, admin_user_id=admin_id
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_challenges(request: Request):
    """
    GET /api/admin/challenges
    Liste paginée avec recherche (titre), tri (sort, order).
    """
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    archived_param = query_params.get("archived")
    challenge_type_param = (query_params.get("type") or "").strip().lower() or None
    search = (query_params.get("search") or "").strip()
    sort = (query_params.get("sort") or "created_at").strip().lower()
    order = (query_params.get("order") or "desc").strip().lower()
    skip = max(0, int(query_params.get("skip", 0)))
    limit = min(100, max(1, int(query_params.get("limit", 20))))

    is_archived = None
    if archived_param is not None:
        is_archived = str(archived_param).lower() in ("true", "1", "yes")

    async with db_session() as db:
        result = AdminService.list_challenges_for_admin(
            db,
            archived=is_archived,
            challenge_type=challenge_type_param,
            search=search,
            sort=sort,
            order=order,
            skip=skip,
            limit=limit,
        )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_patch(request: Request):
    """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived."""
    from app.services.admin_service import AdminService

    challenge_id = int(request.path_params.get("challenge_id"))
    try:
        data = await request.json()
    except Exception:
        return api_error_response(400, "Corps JSON invalide.")
    is_archived = data.get("is_archived")
    if not isinstance(is_archived, bool):
        return api_error_response(400, "Le champ is_archived doit être un booléen.")

    async with db_session() as db:
        admin_id = getattr(request.state, "user", {}).get("id")
        result, err, code = AdminService.patch_challenge_for_admin(
            db,
            challenge_id=challenge_id,
            is_archived=is_archived,
            admin_user_id=admin_id,
        )
    if err:
        return api_error_response(code, err)
    return JSONResponse(result)


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
        return api_error_response(400, "period invalide. Valeurs: 7d, 30d.")

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
    from app.services.admin_service import AdminService

    query_params = dict(request.query_params)
    export_type = (query_params.get("type") or "users").strip().lower()
    period = (query_params.get("period") or "all").strip().lower()

    if export_type not in ("users", "exercises", "attempts", "overview"):
        return api_error_response(
            400, "type invalide. Valeurs: users, exercises, attempts, overview."
        )

    admin_id = getattr(request.state, "user", {}).get("id")
    async with db_session() as db:
        headers, rows_data = AdminService.export_csv_data_for_admin(
            db, export_type=export_type, period=period, admin_user_id=admin_id
        )

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
