"""
Handlers pour la gestion des utilisateurs et statistiques (API)

LOT 6 : handlers anémiques — lecture HTTP, validation schema, appel service, mapping erreurs.
LOT A6 : appels via run_db_bound() vers facades sync.
"""

import traceback

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.leaderboard_period import parse_leaderboard_period
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.core.security import get_cookie_config
from app.exceptions import UserNotFoundError
from app.schemas.user import UserCreate, UserPasswordUpdate
from app.services.spaced_repetition.spaced_repetition_next_review_service import (
    get_next_review_api_payload,
)
from app.services.users.user_application_service import (
    delete_user_account,
    export_user_data,
    get_challenges_detailed_progress_data,
    get_challenges_progress_data,
    get_leaderboard,
    get_progress_timeline_data,
    get_user_progress_data,
    get_user_rank_by_points_data,
    get_user_sessions_list,
    get_user_stats_for_api,
    register_user,
    revoke_session,
    update_password,
    update_profile,
)
from app.utils.error_handler import (
    api_error_response,
    capture_internal_error_response,
    get_safe_error_message,
)
from app.utils.pagination import parse_pagination_params
from app.utils.rate_limit import rate_limit_register
from app.utils.request_utils import parse_json_body_any
from app.utils.settings_reader import get_setting_bool
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)


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
        result = await run_db_bound(
            get_user_stats_for_api,
            request.state.user,
            request.query_params.get("timeRange"),
        )
        if result.error_message is not None:
            return api_error_response(result.status_code, result.error_message)
        return JSONResponse(result.payload)

    except SQLAlchemyError as stats_db_error:
        logger.exception("users.get_user_stats: erreur base de données")
        return capture_internal_error_response(
            stats_db_error,
            "Erreur lors de la récupération des statistiques",
            tags={"handler": "users.get_user_stats", "error_class": "SQLAlchemyError"},
        )
    except Exception as stats_retrieval_error:
        logger.error(
            "Erreur lors de la récupération des statistiques: %s", stats_retrieval_error
        )
        logger.debug(traceback.format_exc())
        return capture_internal_error_response(
            stats_retrieval_error,
            "Erreur lors de la récupération des statistiques",
            tags={"handler": "users.get_user_stats"},
        )


@rate_limit_register
async def create_user_account(request: Request) -> JSONResponse:
    """
    Endpoint pour créer un nouveau compte utilisateur.
    Route: POST /api/users/
    Body: UserCreate (username, email, password, full_name optionnel)
    """
    if not await run_db_bound(get_setting_bool, "registration_enabled", True):
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
            grade_level=None,
            learning_style=None,
            preferred_difficulty=None,
            preferred_theme="spatial",
            accessibility_settings=None,
        )
    except ValidationError as ve:
        return api_error_response(400, _first_validation_error_message(ve))

    try:
        result = await run_db_bound(register_user, user_create)
        if result.error_message is not None:
            return api_error_response(result.status_code, result.error_message)
        if result.payload is None:
            return capture_internal_error_response(
                ValueError("Payload inscription manquant"),
                "Erreur lors de la création du compte",
                tags={"handler": "users.create_user_account"},
            )
        return JSONResponse(result.payload, status_code=201)
    except Exception as user_creation_error:
        logger.error(
            "Erreur lors de la création de l'utilisateur: %s", user_creation_error
        )
        logger.debug(traceback.format_exc())
        return capture_internal_error_response(
            user_creation_error,
            "Erreur lors de la création du compte",
            tags={"handler": "users.create_user_account"},
        )


@require_auth
async def get_all_users(request: Request) -> JSONResponse:
    """
    Handler pour récupérer tous les utilisateurs (placeholder).
    Route: GET /api/users/
    """
    try:
        current_user = request.state.user
        logger.info(
            "Accès à la liste de tous les utilisateurs par %s. Fonctionnalité en développement.",
            current_user.get("username"),
        )
        return JSONResponse(
            {
                "message": "La liste de tous les utilisateurs est en cours de développement."
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(
            "Erreur lors de la récupération de tous les utilisateurs: %s",
            e,
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_users_leaderboard(request: Request) -> JSONResponse:
    """
    Handler pour récupérer le classement des utilisateurs par points.
    Route: GET /api/users/leaderboard
    Paramètres: ``limit`` (pagination), ``period`` = ``all`` | ``week`` | ``month``
    (fenêtre glissante sur ``point_events`` pour ``week`` / ``month`` ; ``all`` = cumul
    ``users.total_points``). Le paramètre historique ``age_group`` a été retiré.
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        query_params = dict(request.query_params)
        _, limit = parse_pagination_params(
            query_params, default_limit=50, max_limit=100
        )
        try:
            period = parse_leaderboard_period(query_params.get("period"))
        except ValueError:
            return api_error_response(
                400,
                "Période invalide. Valeurs acceptées : all, week, month.",
            )

        leaderboard = await run_db_bound(
            get_leaderboard,
            user_id,
            limit=limit,
            period=period,
        )
        logger.info(
            "Classement récupéré par %s: %s utilisateurs",
            current_user.get("username"),
            len(leaderboard),
        )
        return JSONResponse({"leaderboard": leaderboard}, status_code=200)

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération du classement: %s", e, exc_info=True
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_user_me_rank(request: Request) -> JSONResponse:
    """
    Rang par points (1 + nombre d'utilisateurs actifs avec plus de points).
    Route: GET /api/users/me/rank
    Query: ``period`` = ``all`` | ``week`` | ``month`` (aligné sur le classement).
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        try:
            period = parse_leaderboard_period(request.query_params.get("period"))
        except ValueError:
            return api_error_response(
                400,
                "Période invalide. Valeurs acceptées : all, week, month.",
            )
        payload = await run_db_bound(
            get_user_rank_by_points_data, user_id, period=period
        )
        return JSONResponse(payload, status_code=200)
    except UserNotFoundError:
        return api_error_response(404, "Utilisateur introuvable.")
    except Exception as e:
        logger.error(
            "Erreur lors de la récupération du rang utilisateur: %s",
            e,
            exc_info=True,
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

        response_data = await run_db_bound(
            get_progress_timeline_data, user_id, period=period
        )
        return JSONResponse(response_data, status_code=200)

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération de la timeline de progression: %s",
            e,
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
            "Récupération de la progression globale pour l'utilisateur %s", user_id
        )

        response_data = await run_db_bound(get_user_progress_data, user_id)
        return JSONResponse(response_data, status_code=200)

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération de la progression globale de l'utilisateur: %s",
            e,
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
            "Récupération de la progression des défis pour l'utilisateur %s", user_id
        )

        response_data = await run_db_bound(get_challenges_progress_data, user_id)
        return JSONResponse(response_data, status_code=200)

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération de la progression des défis: %s",
            e,
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_challenges_detailed_progress(request: Request) -> JSONResponse:
    """
    Progression agrégée par type de défi (table challenge_progress).
    Route: GET /api/users/me/challenges/detailed-progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(
            "Récupération challenge_progress détaillé pour l'utilisateur %s",
            user_id,
        )
        response_data = await run_db_bound(
            get_challenges_detailed_progress_data, user_id
        )
        return JSONResponse(response_data, status_code=200)
    except Exception as e:
        logger.error(
            "Erreur lors de la récupération du challenge_progress détaillé: %s",
            e,
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_user_me_reviews_next(request: Request) -> JSONResponse:
    """
    F04-P4 : prochaine carte SR due (lecture seule, exercice sans correction).
    Route: GET /api/users/me/reviews/next
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info("F04 next review fetch for user %s", user_id)
        response_data = await run_db_bound(get_next_review_api_payload, user_id)
        return JSONResponse(response_data, status_code=200)
    except Exception as e:
        logger.error(
            "Erreur lors de la récupération de la prochaine révision SR: %s",
            e,
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
        logger.info("Mise à jour profil utilisateur %s", user_id)

        user_payload, err = await run_db_bound(update_profile, user_id, data)
        if err == "not_found":
            return api_error_response(404, "Utilisateur introuvable.")
        if err == "email_taken":
            return api_error_response(400, "Cette adresse email est déjà utilisée.")
        if err:
            return api_error_response(400, err)

        logger.info("Profil utilisateur %s mis à jour", user_id)
        return JSONResponse(user_payload)

    except Exception as e:
        logger.error(
            "Erreur lors de la mise à jour de l'utilisateur: %s", e, exc_info=True
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

        ok, err_msg = await run_db_bound(
            update_password,
            user_id,
            payload.current_password,
            payload.new_password,
        )
        if not ok:
            if "introuvable" in (err_msg or ""):
                return api_error_response(404, "Utilisateur introuvable.")
            return api_error_response(401, err_msg or "Erreur lors de la mise à jour.")

        logger.info("Mot de passe de l'utilisateur %s mis à jour avec succès", user_id)
        return JSONResponse(
            {"success": True, "message": "Mot de passe mis à jour avec succès."}
        )

    except Exception as e:
        logger.error(
            "Erreur lors de la mise à jour du mot de passe: %s", e, exc_info=True
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

        await run_db_bound(delete_user_account, user_id)

        logger.info("Compte utilisateur supprimé : %s (ID: %s)", username, user_id)

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
        logger.error("Erreur lors de la suppression du compte: %s", e, exc_info=True)
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
            "Tentative de suppression de l'utilisateur %s - Redirigé vers DELETE /api/users/me",
            user_to_delete_id,
        )
        return api_error_response(
            400, "Utilisez DELETE /api/users/me pour supprimer votre compte."
        )
    except ValueError:
        return api_error_response(400, "ID utilisateur invalide")
    except Exception as e:
        logger.error(
            "Erreur lors de la suppression de l'utilisateur: %s", e, exc_info=True
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

        export = await run_db_bound(export_user_data, user_id)
        if export is None:
            return api_error_response(404, "Utilisateur introuvable.")

        stats = export["statistics"]
        logger.info(
            "Export de données pour l'utilisateur %s : %s exercices, %s défis, %s badges",
            user_id,
            stats["total_exercise_attempts"],
            stats["total_challenge_attempts"],
            stats["total_badges"],
        )
        return JSONResponse(export)

    except Exception as e:
        logger.error("Erreur lors de l'export des données: %s", e, exc_info=True)
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

        session_list = await run_db_bound(get_user_sessions_list, user_id)

        logger.debug(
            "Récupération de %s sessions actives pour user_id=%s",
            len(session_list),
            user_id,
        )
        return JSONResponse(session_list, status_code=200)

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération des sessions: %s", e, exc_info=True
        )
        return capture_internal_error_response(
            e,
            "Erreur lors de la récupération des sessions",
            tags={"handler": "users.get_user_sessions"},
        )


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

        ok, err_msg = await run_db_bound(revoke_session, user_id, session_id)

        if not ok:
            logger.warning(
                "Tentative de révocation d'une session inexistante ou non autorisée: session_id=%s, user_id=%s",
                session_id,
                user_id,
            )
            return api_error_response(
                404,
                "Session non trouvée ou vous n'avez pas l'autorisation de la révoquer",
            )

        logger.info("Session %s révoquée pour user_id=%s", session_id, user_id)
        return JSONResponse(
            {"success": True, "message": "Session révoquée avec succès"},
            status_code=200,
        )

    except ValueError:
        return api_error_response(400, "ID de session invalide")
    except Exception as e:
        logger.error("Erreur lors de la révocation de la session: %s", e, exc_info=True)
        return capture_internal_error_response(
            e,
            "Erreur lors de la révocation de la session",
            tags={"handler": "users.revoke_user_session"},
        )
