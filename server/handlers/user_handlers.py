"""
Handlers pour la gestion des utilisateurs et statistiques (API)
"""

import json
import re
import traceback

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import get_cookie_config, validate_password_strength
from app.exceptions import UserNotFoundError
from app.schemas.user import UserCreate
from app.services.auth_service import create_registered_user_with_verification
from app.services.email_service import EmailService
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.progress_timeline_service import get_progress_timeline
from app.services.user_service import UserService
from app.utils.db_utils import db_session
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.pagination import parse_pagination_params
from app.utils.rate_limit import rate_limit_register
from app.utils.request_utils import parse_json_body_any
from app.utils.settings_reader import get_setting_bool
from server.auth import require_auth, require_full_access

logger = get_logger(__name__)


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
        valid_ranges = ["7", "30", "90", "all"]
        if time_range not in valid_ranges:
            time_range = "30"

        logger.debug(
            f"Récupération des statistiques pour {username} (ID: {user_id}), période: {time_range}"
        )

        async with db_session() as db:
            response_data = EnhancedServerAdapter.get_user_stats_for_dashboard(
                db, user_id, time_range=time_range
            )
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

    Body JSON:
    {
        "username": "nom_utilisateur",
        "email": "email@example.com",
        "password": "MotDePasse123",
        "full_name": "Nom Complet" (optionnel)
    }
    """
    if not await get_setting_bool("registration_enabled", True):
        return api_error_response(403, "Les inscriptions sont temporairement fermées.")
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    data = data_or_err
    try:
        # Extraire les champs requis
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip() or None

        # Validation basique côté serveur
        if not username:
            return api_error_response(400, "Le nom d'utilisateur est requis")

        if len(username) < 3:
            return api_error_response(
                400, "Le nom d'utilisateur doit contenir au moins 3 caractères"
            )

        if not email:
            return api_error_response(400, "L'email est requis")

        # Validation email basique
        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not re.match(email_pattern, email):
            return api_error_response(400, "Format d'email invalide")

        pwd_err = validate_password_strength(password)
        if pwd_err:
            return api_error_response(400, pwd_err)

        # Créer l'utilisateur via le service
        try:
            async with db_session() as db:
                # Créer le schéma UserCreate
                user_create = UserCreate(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                    grade_level=None,
                    learning_style=None,
                    preferred_difficulty=None,
                    preferred_theme=None,
                    accessibility_settings=None,
                )
                from app.utils.email_verification import generate_verification_token

                verification_token = generate_verification_token()

                # Créer l'utilisateur et son token de vérification dans un seul commit.
                user, create_err, create_status = (
                    create_registered_user_with_verification(
                        db,
                        user_create,
                        verification_token,
                    )
                )
                if create_err:
                    return api_error_response(create_status, create_err)

                # Envoyer l'email de vérification
                try:
                    logger.info(
                        f"Préparation envoi email de vérification à {user.email}"
                    )
                    logger.debug(
                        f"Frontend URL: {settings.FRONTEND_URL}, Token: {verification_token[:10]}..."
                    )

                    email_sent = EmailService.send_verification_email(
                        to_email=user.email,
                        username=user.username,
                        verification_token=verification_token,
                        frontend_url=settings.FRONTEND_URL,
                    )

                    if email_sent:
                        logger.info(
                            f"✅ Email de vérification envoyé avec succès à {user.email}"
                        )
                        if "localhost" in settings.FRONTEND_URL:
                            verify_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
                            logger.info(
                                f"[DEV] Si l'email n'arrive pas, copie ce lien : {verify_link}"
                            )
                    else:
                        logger.warning(
                            f"⚠️ Échec de l'envoi de l'email de vérification à {user.email}"
                        )
                        logger.warning(
                            "Vérifiez la configuration SMTP dans les variables d'environnement"
                        )
                except Exception as email_error:
                    # Ne pas faire échouer l'inscription si l'email échoue
                    logger.error(
                        f"❌ Erreur lors de l'envoi de l'email de vérification: {email_error}"
                    )
                    logger.debug(traceback.format_exc())

                logger.info(f"Nouvel utilisateur créé: {username} ({email})")
                return JSONResponse(
                    UserService.serialize_registered_user_for_api(user),
                    status_code=201,
                )
        except Exception as user_creation_error:
            logger.error(
                f"Erreur lors de la création de l'utilisateur: {user_creation_error}"
            )
            logger.debug(traceback.format_exc())
            return api_error_response(500, "Erreur lors de la création du compte")

    except Exception as unexpected_creation_error:
        logger.error(
            f"Erreur inattendue lors de la création de l'utilisateur: {unexpected_creation_error}"
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
    Paramètres:
      - limit (défaut 50)
      - orderBy (total_points|experience_points, défaut total_points)
      - age_group (optionnel): filtrer par groupe d'âge (preferred_difficulty du profil)
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        query_params = dict(request.query_params)
        _, limit = parse_pagination_params(
            query_params, default_limit=50, max_limit=100
        )
        age_group = query_params.get("age_group", "").strip() or None

        async with db_session() as db:
            leaderboard = UserService.get_leaderboard_for_api(
                db, user_id, limit=limit, age_group=age_group
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

        async with db_session() as db:
            response_data = get_progress_timeline(db, user_id, period=period)
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
    Handler pour récupérer la progression globale de l'utilisateur avec vraies données.
    Route: GET /api/users/me/progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(
            f"Récupération de la progression globale pour l'utilisateur {user_id}"
        )

        async with db_session() as db:
            response_data = UserService.get_user_progress_for_api(db, user_id)
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
    Handler pour récupérer la progression des défis logiques de l'utilisateur.
    Route: GET /api/users/me/challenges/progress
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(
            f"Récupération de la progression des défis pour l'utilisateur {user_id}"
        )

        async with db_session() as db:
            response_data = UserService.get_challenges_progress_for_api(db, user_id)
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

    Champs modifiables :
    - email (avec vérification unicité)
    - full_name
    - grade_level
    - learning_style
    - preferred_difficulty
    - preferred_theme
    - accessibility_settings (JSON)
    """
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    data = data_or_err
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        logger.info(f"Mise à jour profil utilisateur {user_id}")

        update_data, validation_error = UserService.normalize_profile_update_data(data)
        if validation_error:
            return api_error_response(400, validation_error)

        # Mise à jour en base via le service
        async with db_session() as db:
            user, err = UserService.update_user_profile(db, user_id, update_data)
            if err == "not_found":
                return api_error_response(404, "Utilisateur introuvable.")
            if err == "email_taken":
                return api_error_response(400, "Cette adresse email est déjà utilisée.")

            logger.info(
                f"Profil utilisateur {user_id} mis à jour : {list(update_data.keys())}"
            )
            return JSONResponse(UserService.serialize_user_profile_for_api(user))

    except json.JSONDecodeError:
        return api_error_response(400, "Données JSON invalides.")
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
    Protégé CSRF via CsrfMiddleware (audit H6).

    Body attendu :
    - current_password: mot de passe actuel
    - new_password: nouveau mot de passe (min 8 caractères)
    """
    data_or_err = await parse_json_body_any(request)
    if isinstance(data_or_err, JSONResponse):
        return data_or_err
    data = data_or_err
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()

        # Validation
        if not current_password:
            return api_error_response(400, "Le mot de passe actuel est requis.")
        pwd_err = validate_password_strength(new_password)
        if pwd_err:
            return api_error_response(400, pwd_err)
        if current_password == new_password:
            return api_error_response(
                400, "Le nouveau mot de passe doit être différent de l'ancien."
            )

        # Vérification et mise à jour en base via le service
        async with db_session() as db:
            ok, err_msg = UserService.update_user_password(
                db, user_id, current_password, new_password
            )
            if not ok:
                if "introuvable" in (err_msg or ""):
                    return api_error_response(404, "Utilisateur introuvable.")
                return api_error_response(
                    401, err_msg or "Erreur lors de la mise à jour."
                )

            logger.info(
                f"Mot de passe de l'utilisateur {user_id} mis à jour avec succès"
            )
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
    Protégé CSRF via CsrfMiddleware (audit H6).

    Supprime l'utilisateur et toutes ses données associées (cascade).
    Accessible aux utilisateurs non vérifiés (RGPD, droit à l'effacement).
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        username = current_user.get("username")

        async with db_session() as db:
            UserService.delete_user(db, user_id)

            logger.info(f"Compte utilisateur supprimé : {username} (ID: {user_id})")

            # Créer la réponse avec suppression du cookie
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
async def export_user_data(request: Request) -> JSONResponse:
    """
    Exporte toutes les données de l'utilisateur connecté (RGPD).
    Route: GET /api/users/me/export

    Retourne un JSON avec : profil, exercices tentés, défis tentés, badges, progression.
    """
    try:
        current_user = request.state.user
        user_id = current_user.get("id")

        async with db_session() as db:
            export = UserService.get_user_export_data_for_api(db, user_id)
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

        async with db_session() as db:
            session_list = UserService.get_user_sessions_for_api(db, user_id)

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

        async with db_session() as db:
            ok, err_msg = UserService.revoke_user_session(db, session_id, user_id)

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
