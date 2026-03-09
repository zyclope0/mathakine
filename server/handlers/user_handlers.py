"""
Handlers pour la gestion des utilisateurs et statistiques (API)

LOT 6 : handlers anémiques — lecture HTTP, validation schema, appel service, mapping erreurs.
"""

import traceback

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.security import get_cookie_config
from app.exceptions import UserNotFoundError
from app.schemas.user import UserCreate, UserPasswordUpdate
from app.services.user_application_service import (
    delete_user_account,
    export_user_data,
    get_challenges_progress_data,
    get_dashboard_stats,
    get_leaderboard,
    get_progress_timeline_data,
    get_user_progress_data,
    get_user_sessions_list,
    register_user,
    revoke_session,
    update_password,
    update_profile,
)
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.pagination import parse_pagination_params
from app.utils.rate_limit import rate_limit_register
from app.utils.request_utils import parse_json_body_any
from app.utils.settings_reader import get_setting_bool
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)

VALID_TIME_RANGES = frozenset({"7", "30", "90", "all"})


def _first_validation_error_message(ve: ValidationError) -> str:
    """Extrait le premier message d'erreur d'une ValidationError Pydantic."""
    errors = ve.errors()
    if not errors:
        return "Données invalides"
    first = errors[0]
    msg = first.get("msg", "Données invalides")
    ctx = first.get("ctx", {})
    if "limit_value" in ctx:
        return f"{msg} (min: {ctx['limit_value']})"
    return str(msg)


@require_auth
async def get_user_stats(request: Request) -> JSONResponse:
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    Paramètres de requête: timeRange: "7", "30", "90", "all"
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        username = current_user.get("username")

        if not user_id:
            logger.warning(f"ID utilisateur manquant pour {username}")
            return api_error_response(400, "ID utilisateur manquant")

        time_range = request.query_params.get("timeRange", "30")
        if time_range not in VALID_TIME_RANGES:
            time_range = "30"

        logger.debug(
            f"Récupération des statistiques pour {username} (ID: {user_id}), période: {time_range}"
        )

        response_data = await get_dashboard_stats(user_id, time_range=time_range)
        return JSONResponse(response_data)

    except Exception as stats_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des statistiques: {stats_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return api_error_response(
            500, "Erreur lors de la récupération des statistiques"
        )


@rate_limit_register
async def create_user_account(request: Request) -> JSONResponse:
    """
    Endpoint pour créer un nouveau compte utilisateur.
    Route: POST /api/users/
    Body: UserCreate (username, email, password, full_name optionnel)
    """
    if not await get_setting_bool("registration_enabled", True):
        return api_error_response(403, "Les inscriptions sont temporairement fermées.")

    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    data = data_or_err

    try:
        user_create = UserCreate(
            username=(data.get("username") or "").strip(),
            email=(data.get("email") or "").strip(),
            password=data.get("password", ""),
            full_name=(data.get("full_name") or "").strip() or None,
        )
    except ValidationError as ve:
        return api_error_response(400, _first_validation_error_message(ve))

    try:
        payload, error, status_code = await register_user(user_create)
        if error:
            return api_error_response(status_code, error)
        return JSONResponse(payload, status_code=201)
    except Exception as user_creation_error:
        logger.error(
            f"Erreur lors de la création de l'utilisateur: {user_creation_error}"
        )
        logger.debug(traceback.format_exc())
        return api_error_response(500, "Erreur lors de la création du compte")


@require_auth
async def get_all_users(request: Request) -> JSONResponse:
    """
    Handler pour récupérer tous les utilisateurs (placeholder).
    Route: GET /api/users/
    """
    try:
        current_user = request.state.user
        logger.info(
            f"Accès à la liste de tous les utilisateurs par {current_user.get('username')}. Fonctionnalité en développement."
        )
        return JSONResponse(
            {
                "message": "La liste de tous les utilisateurs est en cours de développement."
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de tous les utilisateurs: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_users_leaderboard(request: Request) -> JSONResponse:
    """
    Handler pour récupérer le classement des utilisateurs par points.
    Route: GET /api/users/leaderboard
    Paramètres: limit, orderBy, age_group
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        query_params = dict(request.query_params)
        _, limit = parse_pagination_params(
            query_params, default_limit=50, max_limit=100
        )
        age_group = query_params.get("age_group", "").strip() or None

        leaderboard = await get_leaderboard(
            current_user_id=user_id,
            limit=limit,
            age_group=age_group,
        )
        logger.info(
            f"Classement récupéré par {current_user.get('username')}: {len(leaderboard)} utilisateurs"
        )
        return JSONResponse({"leaderboard": leaderboard}, status_code=200)

    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération du classement: {e}", exc_info=True
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_progress_timeline_handler(request: Request) -> JSONResponse:
    """
    Handler pour la courbe d'évolution temporelle (F07).
    Route: GET /api/users/me/progress/timeline?period=7d|30d
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        period = request.query_params.get("period", "7d")

        response_data = await get_progress_timeline_data(user_id, period=period)
        return JSONResponse(response_data, status_code=200)

    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de la timeline de progression: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_all_user_progress(request: Request) -> JSONResponse:
    """
    Handler pour récupérer la progression globale de l'utilisateur.
    Route: GET /api/users/me/progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(
            f"Récupération de la progression globale pour l'utilisateur {user_id}"
        )

        response_data = await get_user_progress_data(user_id)
        return JSONResponse(response_data, status_code=200)

    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de la progression globale de l'utilisateur: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_challenges_progress(request: Request) -> JSONResponse:
    """
    Handler pour récupérer la progression des défis logiques.
    Route: GET /api/users/me/challenges/progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(
            f"Récupération de la progression des défis pour l'utilisateur {user_id}"
        )

        response_data = await get_challenges_progress_data(user_id)
        return JSONResponse(response_data, status_code=200)

    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de la progression des défis: {e}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def update_user_me(request: Request) -> JSONResponse:
    """
    Handler pour mettre à jour les informations de l'utilisateur actuel.
    Route: PUT /api/users/me
    """
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    data = data_or_err

    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(f"Mise à jour profil utilisateur {user_id}")

        user_payload, err = await update_profile(user_id, data)
        if err == "not_found":
            return api_error_response(404, "Utilisateur introuvable.")
        if err == "email_taken":
            return api_error_response(400, "Cette adresse email est déjà utilisée.")
        if err:
            return api_error_response(400, err)

        logger.info(f"Profil utilisateur {user_id} mis à jour")
        return JSONResponse(user_payload)

    except Exception as e:
        logger.error(
            f"Erreur lors de la mise à jour de l'utilisateur: {e}", exc_info=True
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def update_user_password_me(request: Request) -> JSONResponse:
    """
    Handler pour mettre à jour le mot de passe de l'utilisateur actuel.
    Route: PUT /api/users/me/password
    Body: UserPasswordUpdate (current_password, new_password)
    """
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    data = data_or_err

    try:
        payload = UserPasswordUpdate(
            current_password=(data.get("current_password") or "").strip(),
            new_password=(data.get("new_password") or "").strip(),
        )
    except ValidationError as ve:
        return api_error_response(400, _first_validation_error_message(ve))

    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        ok, err_msg = await update_password(
            user_id,
            payload.current_password,
            payload.new_password,
        )
        if not ok:
            if "introuvable" in (err_msg or ""):
                return api_error_response(404, "Utilisateur introuvable.")
            return api_error_response(401, err_msg or "Erreur lors de la mise à jour.")

        logger.info(f"Mot de passe de l'utilisateur {user_id} mis à jour avec succès")
        return JSONResponse(
            {"success": True, "message": "Mot de passe mis à jour avec succès."}
        )

    except Exception as e:
        logger.error(
            f"Erreur lors de la mise à jour du mot de passe: {e}", exc_info=True
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def delete_user_me(request: Request) -> JSONResponse:
    """
    Handler pour supprimer le compte de l'utilisateur connecté.
    Route: DELETE /api/users/me
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        username = current_user.get("username")

        await delete_user_account(user_id)

        logger.info(f"Compte utilisateur supprimé : {username} (ID: {user_id})")

        response = JSONResponse(
            {"success": True, "message": "Votre compte a été supprimé avec succès."}
        )
        cookie_samesite, cookie_secure = get_cookie_config()
        response.delete_cookie(
            "access_token",
            path="/",
            samesite=cookie_samesite,
            secure=cookie_secure,
        )
        response.delete_cookie(
            "refresh_token",
            path="/",
            samesite=cookie_samesite,
            secure=cookie_secure,
        )
        return response

    except UserNotFoundError:
        return api_error_response(404, "Utilisateur introuvable.")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du compte: {e}", exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def delete_user(request: Request) -> JSONResponse:
    """
    Handler pour supprimer un utilisateur par ID (admin).
    Route: DELETE /api/users/{user_id}
    """
    try:
        current_user = request.state.user
        user_to_delete_id = int(request.path_params.get("user_id"))
        current_user_id = current_user.get("id")

        if user_to_delete_id != current_user_id:
            return api_error_response(403, "Non autorisé à supprimer cet utilisateur")

        logger.info(
            f"Tentative de suppression de l'utilisateur {user_to_delete_id} - Redirigé vers DELETE /api/users/me"
        )
        return api_error_response(
            400, "Utilisez DELETE /api/users/me pour supprimer votre compte."
        )
    except ValueError:
        return api_error_response(400, "ID utilisateur invalide")
    except Exception as e:
        logger.error(
            f"Erreur lors de la suppression de l'utilisateur: {e}", exc_info=True
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def export_user_data_handler(request: Request) -> JSONResponse:
    """
    Exporte toutes les données de l'utilisateur connecté (RGPD).
    Route: GET /api/users/me/export
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        export = await export_user_data(user_id)
        if export is None:
            return api_error_response(404, "Utilisateur introuvable.")

        stats = export["statistics"]
        logger.info(
            f"Export de données pour l'utilisateur {user_id} : "
            f"{stats['total_exercise_attempts']} exercices, "
            f"{stats['total_challenge_attempts']} défis, "
            f"{stats['total_badges']} badges"
        )
        return JSONResponse(export)

    except Exception as e:
        logger.error(f"Erreur lors de l'export des données: {e}", exc_info=True)
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_user_sessions(request: Request) -> JSONResponse:
    """
    Handler pour récupérer les sessions actives de l'utilisateur.
    Route: GET /api/users/me/sessions
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        session_list = await get_user_sessions_list(user_id)

        logger.debug(
            f"Récupération de {len(session_list)} sessions actives pour user_id={user_id}"
        )
        return JSONResponse(session_list, status_code=200)

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sessions: {e}", exc_info=True)
        return api_error_response(500, "Erreur lors de la récupération des sessions")


@require_auth
@require_full_access
async def revoke_user_session(request: Request) -> JSONResponse:
    """
    Handler pour révoquer une session utilisateur spécifique.
    Route: DELETE /api/users/me/sessions/{session_id}
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        session_id = int(request.path_params.get("session_id"))

        ok, err_msg = await revoke_session(user_id, session_id)

        if not ok:
            logger.warning(
                f"Tentative de révocation d'une session inexistante ou non autorisée: session_id={session_id}, user_id={user_id}"
            )
            return api_error_response(
                404,
                "Session non trouvée ou vous n'avez pas l'autorisation de la révoquer",
            )

        logger.info(f"Session {session_id} révoquée pour user_id={user_id}")
        return JSONResponse(
            {"success": True, "message": "Session révoquée avec succès"},
            status_code=200,
        )

    except ValueError:
        return api_error_response(400, "ID de session invalide")
    except Exception as e:
        logger.error(f"Erreur lors de la révocation de la session: {e}", exc_info=True)
        return api_error_response(500, "Erreur lors de la révocation de la session")
