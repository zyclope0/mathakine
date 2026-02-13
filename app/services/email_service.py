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

# Optionnel : Support SendGrid si API key disponible
try:
    import sendgrid
    from sendgrid.helpers.mail import (
        Content,
        Email,
        Mail,
        To,
        TrackingSettings,
        ClickTracking,
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
        text_content: Optional[str] = None
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
        # Vérifier si SendGrid est configuré
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_api_key and SENDGRID_AVAILABLE:
            logger.info(f"[Email] Envoi via SendGrid vers {to_email}")
            return EmailService._send_via_sendgrid(to_email, subject, html_content, text_content)
        else:
            logger.info(f"[Email] Envoi via SMTP vers {to_email} (SendGrid: key={'✓' if sendgrid_api_key else '✗'}, pkg={SENDGRID_AVAILABLE})")
            return EmailService._send_via_smtp(to_email, subject, html_content, text_content)
    
    @staticmethod
    def _send_via_sendgrid(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Envoie un email via SendGrid API"""
        try:
            sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
            if not sendgrid_api_key:
                logger.error("SENDGRID_API_KEY non configurée")
                return False
            
            sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
            from_email = Email(os.getenv("SENDGRID_FROM_EMAIL", "noreply@mathakine.com"))
            to_email_obj = To(to_email)
            
            if text_content:
                content = Content("text/plain", text_content)
            else:
                # Extraire le texte depuis le HTML si possible
                import re
                text_content = re.sub(r'<[^>]+>', '', html_content)
                content = Content("text/html", html_content)
            
            message = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject,
                html_content=html_content
            )
            # Désactiver le click tracking : les liens restent directs (verify-email, reset-password)
            message.tracking_settings = TrackingSettings()
            message.tracking_settings.click_tracking = ClickTracking(enable=False)

            if text_content:
                message.add_content(Content("text/plain", text_content))
            
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email envoyé via SendGrid à {to_email}")
                return True
            else:
                logger.error(f"Erreur SendGrid: {response.status_code} - {response.body}")
                return False
                
        except Exception as sendgrid_error:
            logger.error(f"Erreur lors de l'envoi via SendGrid: {sendgrid_error}")
            return False
    
    @staticmethod
    def _send_via_smtp(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Envoie un email via SMTP"""
        try:
            # Configuration SMTP depuis les variables d'environnement
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_password = os.getenv("SMTP_PASSWORD", "")
            smtp_from_email = os.getenv("SMTP_FROM_EMAIL", smtp_user or "noreply@mathakine.com")
            smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            
            # Si SMTP non configuré, logger et retourner False
            if not smtp_user or not smtp_password:
                logger.warning(f"SMTP non configuré - Email non envoyé")
                logger.warning(f"SMTP_USER={'configuré' if smtp_user else 'MANQUANT'}, SMTP_PASSWORD={'configuré' if smtp_password else 'MANQUANT'}")
                logger.info(f"Email qui aurait été envoyé à {to_email}: {subject}")
                # En développement, on peut simuler l'envoi
                if os.getenv("ENVIRONMENT", "").lower() != "production":
                    logger.info("Mode développement: Email simulé")
                    return True
                return False
            
            logger.info(f"Tentative d'envoi email SMTP à {to_email} via {smtp_host}:{smtp_port}")
            
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_from_email
            msg['To'] = to_email
            
            # Ajouter le contenu texte si fourni
            if text_content:
                part_text = MIMEText(text_content, 'plain')
                msg.attach(part_text)
            
            # Ajouter le contenu HTML
            part_html = MIMEText(html_content, 'html')
            msg.attach(part_html)
            
            # Envoyer l'email
            logger.debug(f"Connexion SMTP à {smtp_host}:{smtp_port}")
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                logger.debug(f"Connexion établie, démarrage TLS: {smtp_use_tls}")
                if smtp_use_tls:
                    server.starttls()
                logger.debug(f"Authentification avec {smtp_user}")
                server.login(smtp_user, smtp_password)
                logger.debug(f"Envoi du message à {to_email}")
                server.send_message(msg)
            
            logger.info(f"✅ Email envoyé via SMTP à {to_email} depuis {smtp_from_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as smtp_auth_error:
            logger.error(f"❌ Erreur d'authentification SMTP: {smtp_auth_error}")
            logger.error(f"Vérifiez SMTP_USER ({smtp_user}) et SMTP_PASSWORD")
            return False
        except smtplib.SMTPException as smtp_error:
            logger.error(f"❌ Erreur SMTP: {smtp_error}")
            return False
        except Exception as smtp_general_error:
            logger.error(f"❌ Erreur lors de l'envoi via SMTP: {type(smtp_general_error).__name__}: {smtp_general_error}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    @staticmethod
    def send_verification_email(
        to_email: str,
        username: str,
        verification_token: str,
        frontend_url: Optional[str] = None
    ) -> bool:
        """
        Envoie un email de vérification à l'inscription.
        Template thème Jedi, ergonomique et accessible.
        """
        if not frontend_url:
            frontend_url = os.getenv("FRONTEND_URL", "https://mathakine-frontend.onrender.com")
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
        frontend_url: Optional[str] = None
    ) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe.
        Template thème Jedi, ergonomique et accessible.
        """
        if not frontend_url:
            frontend_url = os.getenv("FRONTEND_URL", "https://mathakine-frontend.onrender.com")
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        subject = "Réinitialisation de ton mot de passe — Mathakine"
        html_content = password_reset_email_html(username, reset_link)
        text_content = password_reset_email_text(username, reset_link)
        return EmailService.send_email(to_email, subject, html_content, text_content)

