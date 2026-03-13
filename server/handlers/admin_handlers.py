"""
Handlers pour l'espace admin (rôle archiviste).
LOT A6 : appels via run_db_bound() vers facades sync.
"""

import csv
import io

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from app.core.runtime import run_db_bound
from app.schemas.admin import AdminError
from app.services.admin_application_service import AdminApplicationService
from app.services.admin_read_service import (
    get_audit_log_for_api,
    get_badge_for_admin,
    get_challenge_for_admin,
    get_config_for_api,
    get_exercise_for_admin,
    get_moderation_for_api,
    get_overview_for_api,
    get_reports_for_api,
    list_badges_for_admin,
    list_challenges_for_admin,
    list_exercises_for_admin,
    list_users_for_admin,
)
from app.utils.error_handler import api_error_response
from app.utils.generation_metrics import generation_metrics
from app.utils.pagination import parse_pagination_params
from app.utils.request_utils import parse_json_body_any
from app.utils.token_tracker import token_tracker
from server.auth import require_admin, require_auth


@require_auth
@require_admin
async def admin_health(request: Request) -> JSONResponse:
    """
    GET /api/admin/health
    Vérification que les routes admin répondent (test RBAC).
    """
    return JSONResponse({"status": "ok", "admin": True})


@require_auth
@require_admin
async def admin_config_get(request: Request) -> JSONResponse:
    """
    GET /api/admin/config
    Liste les paramètres globaux (paramètres du Temple).
    """
    result = await run_db_bound(get_config_for_api)
    return JSONResponse({"settings": result})


@require_auth
@require_admin
async def admin_config_put(request: Request) -> JSONResponse:
    """
    PUT /api/admin/config
    Met à jour les paramètres globaux.
    Body: { "settings": { "key": value, ... } }
    """

    body_or_err = await parse_json_body_any(request)
    if isinstance(body_or_err, JSONResponse):
        return body_or_err
    settings_in = body_or_err.get("settings") or {}
    if not isinstance(settings_in, dict):
        return api_error_response(400, "'settings' doit être un objet")

    admin_user_id = getattr(request.state, "user", {}).get("id")
    await run_db_bound(
        AdminApplicationService.update_config, settings_in, admin_user_id
    )
    return JSONResponse({"status": "ok"})


@require_auth
@require_admin
async def admin_overview(request: Request) -> JSONResponse:
    """
    GET /api/admin/overview
    KPIs globaux de la plateforme.
    """
    result = await run_db_bound(get_overview_for_api)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_users(request: Request) -> JSONResponse:
    """
    GET /api/admin/users
    Liste paginée des utilisateurs avec filtres (search, role, is_active).
    """
    from server.handlers.admin_list_params import parse_admin_users_params

    p = parse_admin_users_params(request)
    result = await run_db_bound(
        list_users_for_admin,
        search=p.search,
        role=p.role,
        is_active=p.is_active,
        skip=p.skip,
        limit=p.limit,
    )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_users_patch(request: Request) -> JSONResponse:
    """
    PATCH /api/admin/users/{user_id}
    Mise à jour is_active et/ou role. Un admin ne peut pas se désactiver ni se rétrograder.
    """

    try:
        user_id = int(request.path_params["user_id"])
    except (ValueError, TypeError):
        return api_error_response(400, "user_id invalide")
    admin_user_id = request.state.user.get("id")

    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    try:
        result = await run_db_bound(
            AdminApplicationService.patch_user,
            user_id,
            admin_user_id,
            data_or_err,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result.model_dump())


@require_auth
@require_admin
async def admin_users_send_reset_password(request: Request) -> JSONResponse:
    """
    POST /api/admin/users/{user_id}/send-reset-password
    Force l'envoi d'un email de réinitialisation de mot de passe (bypass rate limit).
    """
    try:
        user_id = int(request.path_params["user_id"])
    except (ValueError, TypeError):
        return api_error_response(400, "user_id invalide")

    try:
        result = await run_db_bound(
            AdminApplicationService.send_reset_password, user_id
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse({"message": result.message})


@require_auth
@require_admin
async def admin_users_resend_verification(request: Request) -> JSONResponse:
    """
    POST /api/admin/users/{user_id}/resend-verification
    Force l'envoi d'un email de vérification d'inscription (bypass cooldown).
    """

    try:
        user_id = int(request.path_params["user_id"])
    except (ValueError, TypeError):
        return api_error_response(400, "user_id invalide")

    try:
        result = await run_db_bound(
            AdminApplicationService.resend_verification, user_id
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse({"message": result.message})


@require_auth
@require_admin
async def admin_users_delete(request: Request) -> JSONResponse:
    """
    DELETE /api/admin/users/{user_id}
    Supprime définitivement un utilisateur et toutes ses données (cascade).
    Un admin ne peut pas supprimer son propre compte.
    """
    try:
        user_id = int(request.path_params["user_id"])
    except (ValueError, TypeError):
        return api_error_response(400, "user_id invalide")
    admin_user_id = getattr(request.state, "user", {}).get("id")
    if not admin_user_id:
        return api_error_response(401, "Non authentifié.")

    try:
        result = await run_db_bound(
            AdminApplicationService.delete_user, user_id, admin_user_id
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse({"message": result.message})


@require_auth
@require_admin
async def admin_exercises(request: Request) -> JSONResponse:
    """
    GET /api/admin/exercises
    Liste paginée avec recherche (titre), tri (sort, order).
    """
    from server.handlers.admin_list_params import parse_admin_exercises_params

    base, exercise_type = parse_admin_exercises_params(request)
    result = await run_db_bound(
        list_exercises_for_admin,
        archived=base.archived,
        exercise_type=exercise_type,
        search=base.search,
        sort=base.sort,
        order=base.order,
        skip=base.skip,
        limit=base.limit,
    )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_exercises_post(request: Request) -> JSONResponse:
    """POST /api/admin/exercises — création d'un exercice."""
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.create_exercise_for_admin,
            data_or_err,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_exercise_get(request: Request) -> JSONResponse:
    """GET /api/admin/exercises/{exercise_id} — détail complet pour édition."""
    exercise_id = request.path_params["exercise_id"]
    try:
        result = await run_db_bound(get_exercise_for_admin, exercise_id)
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_exercises_put(request: Request) -> JSONResponse:
    """PUT /api/admin/exercises/{exercise_id} — mise à jour complète."""
    exercise_id = request.path_params["exercise_id"]
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.put_exercise_for_admin,
            exercise_id,
            data_or_err,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_exercises_duplicate(request: Request) -> JSONResponse:
    """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie."""
    exercise_id = request.path_params["exercise_id"]
    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.duplicate_exercise_for_admin,
            exercise_id,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_exercises_patch(request: Request) -> JSONResponse:
    """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived."""
    exercise_id = request.path_params["exercise_id"]
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    is_archived = data_or_err.get("is_archived")
    if not isinstance(is_archived, bool):
        return api_error_response(400, "Le champ is_archived doit être un booléen.")

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.patch_exercise_for_admin,
            exercise_id,
            is_archived,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


# ==================== ADMIN BADGES (Lot B-1) — via AdminService ====================


@require_auth
@require_admin
async def admin_badges(request: Request) -> JSONResponse:
    """
    GET /api/admin/badges
    Liste tous les badges (actifs et inactifs).
    """
    result = await run_db_bound(list_badges_for_admin)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_badges_post(request: Request) -> JSONResponse:
    """POST /api/admin/badges — création d'un badge."""
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.create_badge_for_admin,
            data_or_err,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_badge_get(request: Request) -> JSONResponse:
    """GET /api/admin/badges/{badge_id} — détail pour édition."""
    badge_id = request.path_params["badge_id"]
    try:
        result = await run_db_bound(get_badge_for_admin, badge_id)
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_badges_put(request: Request) -> JSONResponse:
    """PUT /api/admin/badges/{badge_id} — mise à jour complète."""
    badge_id = request.path_params["badge_id"]
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.put_badge_for_admin,
            badge_id,
            data_or_err,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_badges_delete(request: Request) -> JSONResponse:
    """
    DELETE /api/admin/badges/{badge_id}
    Soft delete : is_active = False (recommandé).
    """
    badge_id = request.path_params["badge_id"]
    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.delete_badge_for_admin,
            badge_id,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_post(request: Request) -> JSONResponse:
    """POST /api/admin/challenges — création d'un défi."""
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.create_challenge_for_admin,
            data_or_err,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_challenge_get(request: Request) -> JSONResponse:
    """GET /api/admin/challenges/{challenge_id} — détail complet pour édition."""
    challenge_id = request.path_params["challenge_id"]
    try:
        result = await run_db_bound(get_challenge_for_admin, challenge_id)
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_put(request: Request) -> JSONResponse:
    """PUT /api/admin/challenges/{challenge_id} — mise à jour complète."""
    challenge_id = request.path_params["challenge_id"]
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.put_challenge_for_admin,
            challenge_id,
            data_or_err,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_duplicate(request: Request) -> JSONResponse:
    """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie."""
    challenge_id = request.path_params["challenge_id"]
    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.duplicate_challenge_for_admin,
            challenge_id,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result, status_code=201)


@require_auth
@require_admin
async def admin_challenges(request: Request) -> JSONResponse:
    """
    GET /api/admin/challenges
    Liste paginée avec recherche (titre), tri (sort, order).
    """
    from server.handlers.admin_list_params import parse_admin_challenges_params

    base, challenge_type_param = parse_admin_challenges_params(request)
    result = await run_db_bound(
        list_challenges_for_admin,
        archived=base.archived,
        challenge_type=challenge_type_param,
        search=base.search,
        sort=base.sort,
        order=base.order,
        skip=base.skip,
        limit=base.limit,
    )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_challenges_patch(request: Request) -> JSONResponse:
    """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived."""
    challenge_id = request.path_params["challenge_id"]
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    is_archived = data_or_err.get("is_archived")
    if not isinstance(is_archived, bool):
        return api_error_response(400, "Le champ is_archived doit être un booléen.")

    admin_id = getattr(request.state, "user", {}).get("id")
    try:
        result = await run_db_bound(
            AdminApplicationService.patch_challenge_for_admin,
            challenge_id,
            is_archived,
            admin_id,
        )
    except AdminError as e:
        return api_error_response(e.status_code, e.message)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_audit_log(request: Request) -> JSONResponse:
    """
    GET /api/admin/audit-log?skip=&limit=&action=&resource_type=
    Journal des actions admin (qui a fait quoi, quand).
    """
    query_params = dict(request.query_params)
    skip, limit = parse_pagination_params(query_params, default_limit=50, max_limit=200)
    action_filter = (query_params.get("action") or "").strip() or None
    resource_filter = (query_params.get("resource_type") or "").strip() or None
    result = await run_db_bound(
        get_audit_log_for_api,
        skip=skip,
        limit=limit,
        action_filter=action_filter,
        resource_filter=resource_filter,
    )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_moderation(request: Request) -> JSONResponse:
    """
    GET /api/admin/moderation?type=exercises|challenges
    Liste du contenu généré par IA pour modération (validation, signalement).
    """
    query_params = dict(request.query_params)
    mod_type = (query_params.get("type") or "all").strip().lower()
    skip, limit = parse_pagination_params(query_params, default_limit=50, max_limit=100)
    result = await run_db_bound(
        get_moderation_for_api,
        mod_type=mod_type,
        skip=skip,
        limit=limit,
    )
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_reports(request: Request) -> JSONResponse:
    """
    GET /api/admin/reports?period=7d|30d
    Rapports par période : inscriptions, activité, taux succès.
    """
    query_params = dict(request.query_params)
    period = (query_params.get("period") or "7d").strip().lower()
    if period not in ("7d", "30d"):
        return api_error_response(400, "period invalide. Valeurs: 7d, 30d.")
    result = await run_db_bound(get_reports_for_api, period=period)
    return JSONResponse(result)


@require_auth
@require_admin
async def admin_export(request: Request) -> Response:
    """
    GET /api/admin/export?type=users|exercises|attempts|overview&period=7d|30d|all
    Export CSV streamé. Limite 10 000 lignes par export.
    """
    query_params = dict(request.query_params)
    export_type = (query_params.get("type") or "users").strip().lower()
    period = (query_params.get("period") or "all").strip().lower()
    if export_type not in ("users", "exercises", "attempts", "overview"):
        return api_error_response(
            400, "type invalide. Valeurs: users, exercises, attempts, overview."
        )
    admin_id = getattr(request.state, "user", {}).get("id")
    export_result = await run_db_bound(
        AdminApplicationService.export_csv_data_for_admin,
        export_type,
        period,
        admin_id,
    )
    headers = export_result.headers
    rows_data = export_result.rows

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


@require_auth
@require_admin
async def admin_ai_stats(request: Request) -> JSONResponse:
    """
    GET /api/admin/ai-stats?days=N&challenge_type=...
    Stats tokens OpenAI : coûts, volumes, breakdown par type de challenge.
    Données in-memory collectées par token_tracker depuis challenge_ai_service.
    """
    try:
        days = int(request.query_params.get("days", 1))
        challenge_type = request.query_params.get("challenge_type") or None
        if days < 1 or days > 365:
            return api_error_response(400, "days doit être compris entre 1 et 365.")
        stats = token_tracker.get_stats(challenge_type=challenge_type, days=days)
        daily = token_tracker.get_daily_summary()
        return JSONResponse({"stats": stats, "daily_summary": daily, "days": days})
    except ValueError:
        return api_error_response(400, "Paramètre days invalide.")


@require_auth
@require_admin
async def admin_generation_metrics(request: Request) -> JSONResponse:
    """
    GET /api/admin/generation-metrics?days=N
    Qualité des générations IA : taux de succès, échecs de validation,
    auto-corrections, durée moyenne. Données in-memory collectées par
    generation_metrics depuis challenge_ai_service.
    """
    try:
        days = int(request.query_params.get("days", 1))
        if days < 1 or days > 365:
            return api_error_response(400, "days doit être compris entre 1 et 365.")
        summary = generation_metrics.get_summary(days=days)
        return JSONResponse({"summary": summary, "days": days})
    except ValueError:
        return api_error_response(400, "Paramètre days invalide.")
