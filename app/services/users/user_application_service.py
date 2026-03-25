"""
Service applicatif pour la boundary users (LOT 6).

Responsabilité : registration, dashboard stats, leaderboard, timeline,
profile update, password update, delete, export, sessions.
Pas d'accès DB direct dans les handlers — tout passe par ce service via run_db_bound.

LOT A6 : sync + sync_db_session, exécuté via run_db_bound() depuis les handlers.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.schemas.user import UserCreate
from app.services.auth.auth_service import create_registered_user_with_verification
from app.services.challenges.challenge_progress_service import (
    list_challenge_progress_for_user,
)
from app.services.communication.email_service import EmailService
from app.services.progress.progress_timeline_service import get_progress_timeline
from app.services.users.user_service import UserService

logger = get_logger(__name__)


def register_user(
    user_create: UserCreate,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """
    Inscription utilisateur : création + envoi email de vérification.

    Returns:
        (user_payload, error_message, status_code)
        user_payload si succès (201), sinon None + message + code HTTP.
    """
    with sync_db_session() as db:
        from app.utils.email_verification import generate_verification_token

        verification_token = generate_verification_token()
        result = create_registered_user_with_verification(
            db,
            user_create,
            verification_token,
        )
        if not result.is_success:
            return None, result.error_message, result.status_code

        user = result.user
        try:
            logger.info(f"Préparation envoi email de vérification à {user.email}")
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
        except Exception as email_error:
            logger.error(
                f"❌ Erreur lors de l'envoi de l'email de vérification: {email_error}"
            )

        payload = UserService.serialize_registered_user_for_api(user)
        logger.info(f"Nouvel utilisateur créé: {user.username} ({user.email})")
        return payload, None, 201


def get_dashboard_stats(
    user_id: int,
    time_range: str = "30",
) -> Dict[str, Any]:
    """Récupère les statistiques dashboard pour un utilisateur."""
    with sync_db_session() as db:
        return UserService.get_user_stats_for_dashboard(
            db, user_id, time_range=time_range
        )


def get_leaderboard(
    current_user_id: int,
    limit: int = 50,
    age_group: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Récupère le classement des utilisateurs."""
    with sync_db_session() as db:
        return UserService.get_leaderboard_for_api(
            db, current_user_id, limit=limit, age_group=age_group
        )


def get_progress_timeline_data(
    user_id: int,
    period: str = "7d",
) -> Dict[str, Any]:
    """Récupère la timeline de progression."""
    with sync_db_session() as db:
        return get_progress_timeline(db, user_id, period=period)


def get_user_progress_data(user_id: int) -> Dict[str, Any]:
    """Récupère la progression globale de l'utilisateur."""
    with sync_db_session() as db:
        return UserService.get_user_progress_for_api(db, user_id)


def get_challenges_progress_data(user_id: int) -> Dict[str, Any]:
    """Récupère la progression des défis logiques."""
    with sync_db_session() as db:
        return UserService.get_challenges_progress_for_api(db, user_id)


def get_challenges_detailed_progress_data(user_id: int) -> Dict[str, Any]:
    """Liste challenge_progress par type pour l'utilisateur (GET detailed-progress)."""
    with sync_db_session() as db:
        return {"items": list_challenge_progress_for_user(db, user_id)}


def update_profile(
    user_id: int,
    raw_data: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Met à jour le profil utilisateur.
    Normalise et valide raw_data via UserService.normalize_profile_update_data.

    Returns:
        (user_payload, None) si succès
        (None, "not_found") ou (None, "email_taken") si échec métier
        (None, message_validation) si validation échoue
    """
    update_data, validation_error = UserService.normalize_profile_update_data(raw_data)
    if validation_error:
        return None, validation_error

    with sync_db_session() as db:
        user, err = UserService.update_user_profile(db, user_id, update_data)
        if err:
            return None, err
        return UserService.serialize_user_profile_for_api(user), None


def update_password(
    user_id: int,
    current_password: str,
    new_password: str,
) -> Tuple[bool, Optional[str]]:
    """
    Met à jour le mot de passe.

    Returns:
        (True, None) si succès
        (False, "Utilisateur introuvable.") ou (False, "Le mot de passe actuel est incorrect.")
    """
    with sync_db_session() as db:
        return UserService.update_user_password(
            db, user_id, current_password, new_password
        )


def delete_user_account(user_id: int) -> None:
    """Supprime le compte utilisateur. Lève UserNotFoundError si introuvable."""
    from app.exceptions import UserNotFoundError

    with sync_db_session() as db:
        UserService.delete_user(db, user_id)


def export_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Exporte les données utilisateur (RGPD). Retourne None si introuvable."""
    with sync_db_session() as db:
        return UserService.get_user_export_data_for_api(db, user_id)


def get_user_sessions_list(user_id: int) -> List[Dict[str, Any]]:
    """Récupère les sessions actives de l'utilisateur."""
    with sync_db_session() as db:
        return UserService.get_user_sessions_for_api(db, user_id)


def revoke_session(
    user_id: int,
    session_id: int,
) -> Tuple[bool, Optional[str]]:
    """
    Révoque une session utilisateur.

    Returns:
        (True, None) si succès
        (False, "Session non trouvée ou non autorisée") sinon
    """
    with sync_db_session() as db:
        return UserService.revoke_user_session(db, session_id, user_id)
