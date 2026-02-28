"""
Handlers pour la gestion des utilisateurs et statistiques (API)
"""

import json
import re
import traceback
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.messages import SystemMessages
from app.schemas.user import UserCreate
from app.services.auth_service import (
    create_user,
    get_user_by_email,
    set_verification_token_for_new_user,
)
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.user_service import UserService
from app.utils.csrf import validate_csrf_token
from app.utils.db_utils import db_session
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.pagination import parse_pagination_params
from app.utils.rate_limit import rate_limit_register
from app.utils.settings_reader import get_setting_bool
from server.auth import require_auth, require_full_access


@require_auth
async def get_user_stats(request):
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
async def create_user_account(request: Request):
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
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()

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

        if not password:
            return api_error_response(400, "Le mot de passe est requis")

        # Validation mot de passe selon le schéma UserCreate
        if len(password) < 8:
            return api_error_response(
                400, "Le mot de passe doit contenir au moins 8 caractères"
            )

        if not any(char.isdigit() for char in password):
            return api_error_response(
                400, "Le mot de passe doit contenir au moins un chiffre"
            )

        if not any(char.isupper() for char in password):
            return api_error_response(
                400, "Le mot de passe doit contenir au moins une majuscule"
            )

        # Créer l'utilisateur via le service
        try:
            async with db_session() as db:
                # Créer le schéma UserCreate
                user_create = UserCreate(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                )

                # Créer l'utilisateur
                user = create_user(db, user_create)

                from app.utils.email_verification import generate_verification_token

                verification_token = generate_verification_token()
                set_verification_token_for_new_user(db, user, verification_token)

                # Envoyer l'email de vérification
                try:
                    logger.info(
                        f"Préparation envoi email de vérification à {user.email}"
                    )
                    import os

                    from app.services.email_service import EmailService

                    frontend_url = os.getenv(
                        "FRONTEND_URL", "https://mathakine-frontend.onrender.com"
                    )

                    logger.debug(
                        f"Frontend URL: {frontend_url}, Token: {verification_token[:10]}..."
                    )

                    email_sent = EmailService.send_verification_email(
                        to_email=user.email,
                        username=user.username,
                        verification_token=verification_token,
                        frontend_url=frontend_url,
                    )

                    if email_sent:
                        logger.info(
                            f"✅ Email de vérification envoyé avec succès à {user.email}"
                        )
                        if "localhost" in frontend_url:
                            verify_link = f"{frontend_url}/verify-email?token={verification_token}"
                            logger.info(
                                f"[DEV] Si l'email n'arrive pas, copie ce lien : {verify_link}"
                            )
                    else:
                        logger.warning(
                            f"⚠️ Échec de l'envoi de l'email de vérification à {user.email}"
                        )
                        logger.warning(
                            f"Vérifiez la configuration SMTP dans les variables d'environnement"
                        )
                except Exception as email_error:
                    # Ne pas faire échouer l'inscription si l'email échoue
                    logger.error(
                        f"❌ Erreur lors de l'envoi de l'email de vérification: {email_error}"
                    )
                    logger.debug(traceback.format_exc())

                # Retourner les données de l'utilisateur créé (sans le mot de passe)
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": (
                        user.role.value
                        if hasattr(user.role, "value")
                        else str(user.role)
                    ),
                    "is_active": user.is_active,
                    "is_email_verified": user.is_email_verified,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                }

                logger.info(f"Nouvel utilisateur créé: {username} ({email})")

                return JSONResponse(user_data, status_code=201)
        except HTTPException as http_error:
            # Gérer les erreurs HTTP (ex: utilisateur déjà existant)
            logger.warning(
                f"Erreur HTTP lors de la création de l'utilisateur: {http_error.detail}"
            )
            return api_error_response(http_error.status_code, http_error.detail)
        except Exception as user_creation_error:
            logger.error(
                f"Erreur lors de la création de l'utilisateur: {user_creation_error}"
            )
            logger.debug(traceback.format_exc())
            return api_error_response(500, "Erreur lors de la création du compte")

    except json.JSONDecodeError:
        return api_error_response(400, "Format JSON invalide")
    except Exception as unexpected_creation_error:
        logger.error(
            f"Erreur inattendue lors de la création de l'utilisateur: {unexpected_creation_error}"
        )
        logger.debug(traceback.format_exc())
        return api_error_response(500, "Erreur lors de la création du compte")


@require_auth
async def get_all_users(request: Request):
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
        logger.error(f"Erreur lors de la récupération de tous les utilisateurs: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_users_leaderboard(request: Request):
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
        logger.error(f"Erreur lors de la récupération du classement: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_all_user_progress(request: Request):
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
            f"Erreur lors de la récupération de la progression globale de l'utilisateur: {e}"
        )
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_challenges_progress(request: Request):
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
        logger.error(f"Erreur lors de la récupération de la progression des défis: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def update_user_me(request: Request):
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
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        data = await request.json()
        logger.info(f"Mise à jour profil utilisateur {user_id}")

        # Champs autorisés à modifier
        ALLOWED_FIELDS = {
            "email",
            "full_name",
            "grade_level",
            "grade_system",
            "learning_style",
            "preferred_difficulty",
            "preferred_theme",
            "accessibility_settings",
            "learning_goal",
            "practice_rhythm",
        }

        # Gérer les champs de confidentialité : regrouper sous privacy_settings
        privacy_fields = [
            "is_public_profile",
            "allow_friend_requests",
            "show_in_leaderboards",
            "data_retention_consent",
            "marketing_consent",
        ]
        privacy_data = {}
        for field in privacy_fields:
            if field in data:
                privacy_data[field] = data.pop(field)
        if privacy_data:
            data["privacy_settings"] = privacy_data

        # Gérer les champs stockés dans accessibility_settings (JSON)
        # notification_preferences, language_preference, timezone, privacy_settings
        json_fields = [
            "notification_preferences",
            "language_preference",
            "timezone",
            "privacy_settings",
        ]
        json_overrides = {}
        for field in json_fields:
            if field in data:
                json_overrides[field] = data.pop(field)

        if json_overrides:
            if "accessibility_settings" not in data:
                data["accessibility_settings"] = {}
            if isinstance(data["accessibility_settings"], dict):
                data["accessibility_settings"].update(json_overrides)
            else:
                data["accessibility_settings"] = json_overrides

        # Filtrer les champs non autorisés
        update_data = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}

        if not update_data:
            return api_error_response(400, "Aucun champ valide à mettre à jour.")

        # Validation email si fourni
        if "email" in update_data:
            email = update_data["email"].strip().lower()
            if not email or not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
                return api_error_response(400, "Adresse email invalide.")
            update_data["email"] = email

        # Validation full_name
        if "full_name" in update_data:
            full_name = (
                update_data["full_name"].strip() if update_data["full_name"] else None
            )
            if full_name and len(full_name) > 100:
                return api_error_response(
                    400, "Le nom complet ne peut pas dépasser 100 caractères."
                )
            update_data["full_name"] = full_name

        # Validation grade_system
        VALID_GRADE_SYSTEMS = {"suisse", "unifie"}
        if "grade_system" in update_data:
            gs = update_data["grade_system"]
            if gs is not None and gs not in VALID_GRADE_SYSTEMS:
                return api_error_response(
                    400, "Système scolaire invalide. Valeurs : suisse ou unifie."
                )

        # Validation grade_level (max 11 pour suisse, 12 pour unifie)
        if "grade_level" in update_data:
            grade = update_data["grade_level"]
            if grade is not None:
                try:
                    grade = int(grade)
                    grade_sys = update_data.get("grade_system")
                    max_grade = 11 if grade_sys == "suisse" else 12
                    if grade < 1 or grade > max_grade:
                        return api_error_response(
                            400, f"Le niveau scolaire doit être entre 1 et {max_grade}."
                        )
                    update_data["grade_level"] = grade
                except (ValueError, TypeError):
                    return api_error_response(
                        400, "Le niveau scolaire doit être un nombre."
                    )

        # Validation learning_style
        VALID_STYLES = {"visuel", "auditif", "kinesthésique", "lecture"}
        if "learning_style" in update_data:
            style = update_data["learning_style"]
            if style and style not in VALID_STYLES:
                return api_error_response(
                    400,
                    f"Style d'apprentissage invalide. Valeurs acceptées : {', '.join(VALID_STYLES)}",
                )

        # Validation preferred_theme
        VALID_THEMES = {
            "spatial",
            "minimalist",
            "ocean",
            "dune",
            "forest",
            "peach",
            "dino",
            "neutral",
        }
        if "preferred_theme" in update_data:
            theme = update_data["preferred_theme"]
            if theme and theme not in VALID_THEMES:
                return api_error_response(
                    400,
                    f"Thème invalide. Valeurs acceptées : {', '.join(VALID_THEMES)}",
                )

        # Mise à jour en base via le service
        async with db_session() as db:
            user, err = UserService.update_user_profile(db, user_id, update_data)
            if err == "not_found":
                return api_error_response(404, "Utilisateur introuvable.")
            if err == "email_taken":
                return api_error_response(400, "Cette adresse email est déjà utilisée.")
            # user is not None

            # Construire la réponse
            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if user.role else None,
                "is_email_verified": getattr(user, "is_email_verified", True),
                "grade_level": user.grade_level,
                "grade_system": getattr(user, "grade_system", None),
                "learning_style": user.learning_style,
                "preferred_difficulty": user.preferred_difficulty,
                "onboarding_completed_at": (
                    user.onboarding_completed_at.isoformat()
                    if getattr(user, "onboarding_completed_at", None)
                    else None
                ),
                "learning_goal": getattr(user, "learning_goal", None),
                "practice_rhythm": getattr(user, "practice_rhythm", None),
                "preferred_theme": user.preferred_theme,
                "accessibility_settings": user.accessibility_settings,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "total_points": user.total_points,
                "current_level": user.current_level,
                "jedi_rank": user.jedi_rank,
            }

            logger.info(
                f"Profil utilisateur {user_id} mis à jour : {list(update_data.keys())}"
            )
            return JSONResponse(response_data)

    except json.JSONDecodeError:
        return api_error_response(400, "Données JSON invalides.")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def update_user_password_me(request: Request):
    """
    Handler pour mettre à jour le mot de passe de l'utilisateur actuel.
    Route: PUT /api/users/me/password
    Protégé CSRF (audit 3.2).

    Body attendu :
    - current_password: mot de passe actuel
    - new_password: nouveau mot de passe (min 8 caractères)
    """
    csrf_err = validate_csrf_token(request)
    if csrf_err:
        return csrf_err
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        data = await request.json()

        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()

        # Validation
        if not current_password:
            return api_error_response(400, "Le mot de passe actuel est requis.")
        if not new_password:
            return api_error_response(400, "Le nouveau mot de passe est requis.")
        if len(new_password) < 8:
            return api_error_response(
                400, "Le nouveau mot de passe doit contenir au moins 8 caractères."
            )
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

    except json.JSONDecodeError:
        return api_error_response(400, "Données JSON invalides.")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du mot de passe: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def delete_user_me(request: Request):
    """
    Handler pour supprimer le compte de l'utilisateur connecté.
    Route: DELETE /api/users/me
    Protégé CSRF (audit 3.2).

    Supprime l'utilisateur et toutes ses données associées (cascade).
    Accessible aux utilisateurs non vérifiés (RGPD, droit à l'effacement).
    """
    csrf_err = validate_csrf_token(request)
    if csrf_err:
        return csrf_err
    try:
        current_user = request.state.user
        user_id = current_user.get("id")
        username = current_user.get("username")

        async with db_session() as db:
            deleted = UserService.delete_user(db, user_id)
            if not deleted:
                return api_error_response(404, "Utilisateur introuvable.")

            logger.info(f"Compte utilisateur supprimé : {username} (ID: {user_id})")

            # Créer la réponse avec suppression du cookie
            response = JSONResponse(
                {"success": True, "message": "Votre compte a été supprimé avec succès."}
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

    except Exception as e:
        logger.error(f"Erreur lors de la suppression du compte: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
async def delete_user(request: Request):
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
        logger.error(f"Erreur lors de la suppression de l'utilisateur: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def export_user_data(request: Request):
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
        logger.error(f"Erreur lors de l'export des données: {e}")
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(e))


@require_auth
@require_full_access
async def get_user_sessions(request: Request):
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
        logger.error(f"Erreur lors de la récupération des sessions: {e}")
        traceback.print_exc()
        return api_error_response(500, "Erreur lors de la récupération des sessions")


@require_auth
@require_full_access
async def revoke_user_session(request: Request):
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
        logger.error(f"Erreur lors de la révocation de la session: {e}")
        traceback.print_exc()
        return api_error_response(500, "Erreur lors de la révocation de la session")
