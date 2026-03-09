"""
Service d'orchestration pour la boundary auth recovery (Lot 5).

Responsabilité : verify-email, resend-verification, forgot-password, reset-password.
Pas d'accès DB direct dans les handlers — tout passe par ce service.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, Optional

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.auth_service import (
    get_user_by_email,
    initiate_password_reset,
    resend_verification_token,
    reset_password_with_token,
    verify_email_token,
)
from app.services.email_service import EmailService
from app.utils.db_utils import db_session

logger = get_logger(__name__)

# Cooldown resend verification (minutes)
RESEND_COOLDOWN_MINUTES = 2


class AuthRecoveryError(Exception):
    """Erreur métier recovery/verification. Le handler mappe vers HTTP."""

    def __init__(self, code: str):
        self.code = code


@dataclass
class VerifyEmailResult:
    """Résultat de la vérification d'email."""

    user_payload: Dict[str, Any]
    state: Literal["verified", "already_verified"]


@dataclass
class ResendVerificationResult:
    """Résultat du renvoi d'email de vérification."""

    outcome: Literal["sent", "user_not_found", "already_verified", "cooldown"]


@dataclass
class ForgotPasswordResult:
    """Résultat de la demande forgot-password."""

    outcome: Literal["sent", "user_not_found_or_inactive"]


def _build_verify_user_payload(user) -> Dict[str, Any]:
    """Construit le payload user pour verify-email (dans la session DB)."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_email_verified": user.is_email_verified,
    }


async def perform_verify_email(token: str) -> VerifyEmailResult:
    """
    Vérifie un token d'email et marque l'utilisateur comme vérifié si valide.

    Returns:
        VerifyEmailResult si succès
    Raises:
        AuthRecoveryError("invalid") ou ("expired") si échec
    """
    if not token or not token.strip():
        raise AuthRecoveryError("invalid")

    async with db_session() as db:
        user, err = verify_email_token(db, token.strip())

        if err == "invalid":
            raise AuthRecoveryError("invalid")

        if err == "expired":
            raise AuthRecoveryError("expired")

        if err == "already_verified":
            payload = _build_verify_user_payload(user)
            return VerifyEmailResult(user_payload=payload, state="already_verified")

        # err is None: success
        payload = _build_verify_user_payload(user)
        return VerifyEmailResult(user_payload=payload, state="verified")


async def perform_resend_verification(email: str) -> ResendVerificationResult:
    """
    Renvoie l'email de vérification avec cooldown.

    Returns:
        ResendVerificationResult (outcome)
    Raises:
        AuthRecoveryError("email_send_failed") si échec envoi
    """
    email = (email or "").strip().lower()
    if not email:
        return ResendVerificationResult(outcome="user_not_found")

    async with db_session() as db:
        user = get_user_by_email(db, email)

        if not user:
            return ResendVerificationResult(outcome="user_not_found")

        if user.is_email_verified:
            return ResendVerificationResult(outcome="already_verified")

        # Cooldown 2 minutes
        if user.email_verification_sent_at:
            cooldown_until = user.email_verification_sent_at + timedelta(
                minutes=RESEND_COOLDOWN_MINUTES
            )
            if datetime.now(timezone.utc) < cooldown_until:
                return ResendVerificationResult(outcome="cooldown")

        verification_token = resend_verification_token(db, user)
        to_email = user.email
        username = user.username

    # Envoi email hors session (EmailService n'a pas besoin de DB)
    email_sent = EmailService.send_verification_email(
        to_email=to_email,
        username=username,
        verification_token=verification_token,
        frontend_url=settings.FRONTEND_URL,
    )

    if not email_sent:
        logger.warning("Échec envoi email de vérification")
        raise AuthRecoveryError("email_send_failed")

    logger.info("Email de vérification renvoyé")
    return ResendVerificationResult(outcome="sent")


async def perform_forgot_password(email: str) -> ForgotPasswordResult:
    """
    Demande de réinitialisation de mot de passe.
    Génère un token, le stocke en DB, et envoie un email.

    Returns:
        ForgotPasswordResult (toujours succès côté message pour sécurité)
    Raises:
        AuthRecoveryError("email_send_failed") si envoi échoue pour un compte valide
    """
    email = (email or "").strip().lower()
    if not email:
        return ForgotPasswordResult(outcome="user_not_found_or_inactive")

    async with db_session() as db:
        user = get_user_by_email(db, email)

        if not user:
            logger.debug("Demande reset pour email inexistant")
            return ForgotPasswordResult(outcome="user_not_found_or_inactive")

        if not user.is_active:
            logger.debug("Demande reset pour compte inactif")
            return ForgotPasswordResult(outcome="user_not_found_or_inactive")

        reset_token = initiate_password_reset(db, user)
        to_email = user.email
        username = user.username

    email_sent = EmailService.send_password_reset_email(
        to_email=to_email,
        username=username,
        reset_token=reset_token,
        frontend_url=settings.FRONTEND_URL,
    )

    if not email_sent:
        logger.warning("Échec envoi email reset")
        raise AuthRecoveryError("email_send_failed")

    logger.info("Email de réinitialisation envoyé")
    return ForgotPasswordResult(outcome="sent")


async def perform_reset_password(token: str, new_password: str) -> None:
    """
    Réinitialise le mot de passe avec un token valide.

    Raises:
        AuthRecoveryError("invalid") ou ("expired") si token invalide
    """
    token = (token or "").strip()
    if not token:
        raise AuthRecoveryError("invalid")

    async with db_session() as db:
        user, err = reset_password_with_token(db, token, new_password)

        if err == "invalid":
            raise AuthRecoveryError("invalid")

        if err == "expired":
            raise AuthRecoveryError("expired")

    # err is None: success
    logger.info("Mot de passe réinitialisé")
