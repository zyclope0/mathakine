"""
Handlers pour l'authentification et la vérification d'email
"""
import traceback
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.auth_service import get_user_by_email
from app.utils.email_verification import generate_verification_token, is_verification_token_expired
from app.services.email_service import EmailService
from loguru import logger
from datetime import datetime, timezone
import os


async def verify_email(request: Request):
    """
    Vérifie l'adresse email d'un utilisateur avec un token.
    Route: GET /api/auth/verify-email?token=...
    """
    try:
        # Récupérer le token depuis les query params
        token = request.query_params.get('token')
        
        if not token:
            return JSONResponse(
                {"error": "Token de vérification manquant"},
                status_code=400
            )
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Chercher l'utilisateur avec ce token
            from app.models.user import User
            user = db.query(User).filter(
                User.email_verification_token == token
            ).first()
            
            if not user:
                return JSONResponse(
                    {"error": "Token de vérification invalide"},
                    status_code=400
                )
            
            # Vérifier si le token a expiré
            if is_verification_token_expired(user.email_verification_sent_at):
                return JSONResponse(
                    {"error": "Le token de vérification a expiré. Veuillez demander un nouveau lien."},
                    status_code=400
                )
            
            # Vérifier si l'email est déjà vérifié
            if user.is_email_verified:
                return JSONResponse(
                    {"message": "Votre adresse email est déjà vérifiée"},
                    status_code=200
                )
            
            # Marquer l'email comme vérifié
            user.is_email_verified = True
            user.email_verification_token = None  # Supprimer le token utilisé
            user.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Email vérifié pour l'utilisateur {user.username} ({user.email})")
            
            return JSONResponse({
                "message": "Votre adresse email a été vérifiée avec succès !",
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_email_verified": user.is_email_verified
                }
            }, status_code=200)
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'email: {e}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la vérification de l'email"},
            status_code=500
        )


async def resend_verification_email(request: Request):
    """
    Renvoie l'email de vérification.
    Route: POST /api/auth/resend-verification
    Body: {"email": "user@example.com"}
    """
    try:
        # Récupérer l'email depuis le body
        data = await request.json()
        email = data.get('email', '').strip()
        
        if not email:
            return JSONResponse(
                {"error": "Adresse email requise"},
                status_code=400
            )
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Chercher l'utilisateur
            user = get_user_by_email(db, email)
            
            if not user:
                # Pour des raisons de sécurité, ne pas révéler si l'email existe
                return JSONResponse({
                    "message": "Si cette adresse email est associée à un compte non vérifié, vous recevrez un email de vérification."
                }, status_code=200)
            
            # Vérifier si l'email est déjà vérifié
            if user.is_email_verified:
                return JSONResponse({
                    "message": "Votre adresse email est déjà vérifiée"
                }, status_code=200)
            
            # Générer un nouveau token
            verification_token = generate_verification_token()
            user.email_verification_token = verification_token
            user.email_verification_sent_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(user)
            
            # Envoyer l'email
            frontend_url = os.getenv("FRONTEND_URL", "https://mathakine-frontend.onrender.com")
            email_sent = EmailService.send_verification_email(
                to_email=user.email,
                username=user.username,
                verification_token=verification_token,
                frontend_url=frontend_url
            )
            
            if email_sent:
                logger.info(f"Email de vérification renvoyé à {user.email}")
                return JSONResponse({
                    "message": "Un nouvel email de vérification a été envoyé à votre adresse."
                }, status_code=200)
            else:
                logger.warning(f"Échec de l'envoi de l'email de vérification à {user.email}")
                return JSONResponse({
                    "error": "Impossible d'envoyer l'email de vérification. Veuillez réessayer plus tard."
                }, status_code=500)
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors du renvoi de l'email de vérification: {e}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors du renvoi de l'email de vérification"},
            status_code=500
        )

