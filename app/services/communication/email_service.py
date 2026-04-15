"""
Service d'envoi d'emails pour Mathakine
Support SMTP et SendGrid (optionnel)
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)

from app.core.config import settings
from app.utils.email_templates import (
    password_reset_email_html,
    password_reset_email_text,
    verification_email_html,
    verification_email_text,
)


def _mask_email(email: str) -> str:
    """Masque un email pour les logs : user@domain.com → u***@domain.com"""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def _mask_user(user: Optional[str]) -> str:
    """Masque un identifiant SMTP pour les logs."""
    if not user:
        return "***"
    return f"{user[:2]}***"


# Optionnel : Support SendGrid si API key disponible
try:
    import sendgrid
    from sendgrid.helpers.mail import (
        ClickTracking,
        Content,
        Email,
        Mail,
        To,
        TrackingSettings,
    )

    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.debug("SendGrid non disponible, utilisation SMTP uniquement")


class EmailService:
    """Service pour l'envoi d'emails"""

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Envoie un email.

        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            text_content: Contenu texte alternatif (optionnel)

        Returns:
            True si l'email a été envoyé avec succès, False sinon
        """
        if os.getenv("TESTING", "false").lower() == "true":
            logger.debug(
                "[Email] Mode test : envoi simulé vers %s", _mask_email(to_email)
            )
            return True

        # Vérifier si SendGrid est configuré
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_api_key and SENDGRID_AVAILABLE:
            logger.info("[Email] Envoi via SendGrid vers %s", _mask_email(to_email))
            return EmailService._send_via_sendgrid(
                to_email, subject, html_content, text_content
            )
        else:
            logger.info(
                "[Email] Envoi via SMTP vers %s (SendGrid: key=%s, pkg=%s)",
                _mask_email(to_email),
                "✓" if sendgrid_api_key else "✗",
                SENDGRID_AVAILABLE,
            )
            return EmailService._send_via_smtp(
                to_email, subject, html_content, text_content
            )

    @staticmethod
    def _send_via_sendgrid(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Envoie un email via SendGrid API"""
        try:
            sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
            if not sendgrid_api_key:
                logger.error("SENDGRID_API_KEY non configurée")
                return False

            sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
            from_email = Email(
                os.getenv("SENDGRID_FROM_EMAIL", "noreply@mathakine.com")
            )
            to_email_obj = To(to_email)

            if text_content:
                content = Content("text/plain", text_content)
            else:
                # Extraire le texte depuis le HTML si possible
                import re

                text_content = re.sub(r"<[^>]+>", "", html_content)
                content = Content("text/html", html_content)

            message = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject,
                html_content=html_content,
            )
            # Désactiver le click tracking : les liens restent directs (verify-email, reset-password)
            message.tracking_settings = TrackingSettings()
            message.tracking_settings.click_tracking = ClickTracking(enable=False)

            if text_content:
                message.add_content(Content("text/plain", text_content))

            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info("Email envoyé via SendGrid à %s", _mask_email(to_email))
                return True
            else:
                logger.error(
                    "Erreur SendGrid: %s - %s", response.status_code, response.body
                )
                return False

        except Exception as sendgrid_error:
            logger.error("Erreur lors de l'envoi via SendGrid: %s", sendgrid_error)
            return False

    @staticmethod
    def _send_via_smtp(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Envoie un email via SMTP"""
        try:
            # Configuration SMTP depuis les variables d'environnement
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_password = os.getenv("SMTP_PASSWORD", "")
            smtp_from_email = os.getenv(
                "SMTP_FROM_EMAIL", smtp_user or "noreply@mathakine.com"
            )
            smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

            # Si SMTP non configuré, logger et retourner False
            if not smtp_user or not smtp_password:
                logger.warning("SMTP non configuré - Email non envoyé")
                logger.warning(
                    "SMTP_USER=%s, SMTP_PASSWORD=%s",
                    "configuré" if smtp_user else "MANQUANT",
                    "configuré" if smtp_password else "MANQUANT",
                )
                logger.info(
                    "Email qui aurait été envoyé à %s: %s",
                    _mask_email(to_email),
                    subject,
                )
                # En développement, on peut simuler l'envoi
                if os.getenv("ENVIRONMENT", "").lower() != "production":
                    logger.info("Mode développement: Email simulé")
                    return True
                return False

            logger.info(
                "Tentative d'envoi email SMTP à %s via %s:%s",
                _mask_email(to_email),
                smtp_host,
                smtp_port,
            )

            # Créer le message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_from_email
            msg["To"] = to_email

            # Ajouter le contenu texte si fourni
            if text_content:
                part_text = MIMEText(text_content, "plain")
                msg.attach(part_text)

            # Ajouter le contenu HTML
            part_html = MIMEText(html_content, "html")
            msg.attach(part_html)

            # Envoyer l'email
            logger.debug("Connexion SMTP à %s:%s", smtp_host, smtp_port)
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                logger.debug("Connexion établie, démarrage TLS: %s", smtp_use_tls)
                if smtp_use_tls:
                    server.starttls()
                logger.debug("Authentification avec %s", _mask_user(smtp_user))
                server.login(smtp_user, smtp_password)
                logger.debug("Envoi du message à %s", _mask_email(to_email))
                server.send_message(msg)

            logger.info(
                "✅ Email envoyé via SMTP à %s depuis %s",
                _mask_email(to_email),
                _mask_email(smtp_from_email),
            )
            return True

        except smtplib.SMTPAuthenticationError as smtp_auth_error:
            logger.error("❌ Erreur d'authentification SMTP: %s", smtp_auth_error)
            logger.error(
                "Vérifiez SMTP_USER (%s) et SMTP_PASSWORD", _mask_user(smtp_user)
            )
            return False
        except smtplib.SMTPException as smtp_error:
            logger.error("❌ Erreur SMTP: %s", smtp_error)
            return False
        except Exception as smtp_general_error:
            logger.error(
                "❌ Erreur lors de l'envoi via SMTP: %s: %s",
                type(smtp_general_error).__name__,
                smtp_general_error,
            )
            import traceback

            logger.debug(traceback.format_exc())
            return False

    @staticmethod
    def send_verification_email(
        to_email: str,
        username: str,
        verification_token: str,
        frontend_url: Optional[str] = None,
    ) -> bool:
        """
        Envoie un email de vérification à l'inscription.
        Template thème Jedi, ergonomique et accessible.
        """
        if not frontend_url:
            frontend_url = settings.FRONTEND_URL
        verification_link = f"{frontend_url}/verify-email?token={verification_token}"
        subject = "Bienvenue ! Active ton compte Mathakine"
        html_content = verification_email_html(username, verification_link)
        text_content = verification_email_text(username, verification_link)
        return EmailService.send_email(to_email, subject, html_content, text_content)

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        username: str,
        reset_token: str,
        frontend_url: Optional[str] = None,
    ) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe.
        Template thème Jedi, ergonomique et accessible.
        """
        if not frontend_url:
            frontend_url = settings.FRONTEND_URL
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        subject = "Réinitialisation de ton mot de passe — Mathakine"
        html_content = password_reset_email_html(username, reset_link)
        text_content = password_reset_email_text(username, reset_link)
        return EmailService.send_email(to_email, subject, html_content, text_content)
