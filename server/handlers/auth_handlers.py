"""
Handlers pour l'authentification et la vérification d'email
"""
import os
import traceback
from datetime import datetime, timezone

from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from app.services.auth_service import (authenticate_user, create_user_token,
                                       get_user_by_email, refresh_access_token)
from app.services.email_service import EmailService
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.utils.email_verification import (generate_verification_token,
                                          is_verification_token_expired)


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
            
    except Exception as email_verification_error:
        logger.error(f"Erreur lors de la vérification de l'email: {email_verification_error}")
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
            
    except Exception as resend_verification_error:
        logger.error(f"Erreur lors du renvoi de l'email de vérification: {resend_verification_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors du renvoi de l'email de vérification"},
            status_code=500
        )


async def api_login(request: Request):
    """
    Connexion avec nom d'utilisateur et mot de passe.
    Route: POST /api/auth/login
    Body: {"username": "...", "password": "..."}
    Returns: Token + user info
    """
    try:
        # Récupérer les données du body
        data = await request.json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return JSONResponse(
                {"error": "Nom d'utilisateur et mot de passe requis"},
                status_code=400
            )
        
        logger.debug(f"Tentative de connexion pour l'utilisateur: {username}")
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Authentifier l'utilisateur
            user = authenticate_user(db, username, password)
            
            if not user:
                logger.warning(f"Échec de connexion pour l'utilisateur: {username}")
                return JSONResponse(
                    {"error": "Nom d'utilisateur ou mot de passe incorrect"},
                    status_code=401
                )
            
            # Créer les tokens d'accès
            token_data = create_user_token(user)
            logger.info(f"Connexion réussie pour l'utilisateur: {user.username}")
            
            # Ajouter les informations utilisateur à la réponse
            response_data = {
                "access_token": token_data.get("access_token"),
                "token_type": token_data.get("token_type", "bearer"),
                "expires_in": token_data.get("expires_in", 3600),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email if hasattr(user, 'email') else None,
                    "full_name": user.full_name if hasattr(user, 'full_name') else None,
                    "role": user.role.value if hasattr(user, 'role') else None,
                    "is_email_verified": user.is_email_verified if hasattr(user, 'is_email_verified') else False
                }
            }
            
            # Créer la réponse avec le cookie
            response = JSONResponse(response_data, status_code=200)
            
            # Définir le cookie access_token (pour compatibilité avec l'ancien système)
            response.set_cookie(
                key="access_token",
                value=token_data.get("access_token"),
                httponly=True,
                max_age=token_data.get("expires_in", 3600),
                samesite="lax"
            )
            
            return response
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as login_error:
        logger.error(f"Erreur lors de la connexion: {login_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la connexion"},
            status_code=500
        )


async def api_refresh_token(request: Request):
    """
    Rafraîchit le token d'accès avec un refresh token.
    Route: POST /api/auth/refresh
    Body (optionnel): {"refresh_token": "..."}
    Cookie (optionnel): refresh_token
    Returns: New access token
    """
    try:
        refresh_token = None
        
        # Essayer de récupérer le refresh token depuis le body JSON (pour compatibilité)
        try:
            body_content = await request.body()
            if body_content:
                import json
                try:
                    data = json.loads(body_content.decode('utf-8'))
                    refresh_token = data.get('refresh_token', '').strip() if data else None
                except (ValueError, json.JSONDecodeError):
                    # JSON invalide, ce n'est pas grave, on essaiera les cookies
                    pass
        except Exception:
            # Erreur lors de la lecture du body, ce n'est pas grave, on essaiera les cookies
            pass
        
        # Si pas de token dans le body, essayer de le récupérer depuis les cookies
        if not refresh_token:
            refresh_token = request.cookies.get('refresh_token', '').strip()
        
        if not refresh_token:
            return JSONResponse(
                {"error": "Refresh token requis (body ou cookie)"},
                status_code=400
            )
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Rafraîchir le token
            new_token_data = refresh_access_token(db, refresh_token)
            
            logger.info("Token rafraîchi avec succès")
            
            # Créer la réponse avec le nouveau token
            response = JSONResponse(new_token_data, status_code=200)
            
            # Mettre à jour le cookie access_token si présent dans la réponse
            if "access_token" in new_token_data:
                response.set_cookie(
                    key="access_token",
                    value=new_token_data.get("access_token"),
                    httponly=True,
                    max_age=new_token_data.get("expires_in", 3600),
                    samesite="lax"
                )
            
            return response
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as token_refresh_error:
        logger.error(f"Erreur lors du rafraîchissement du token: {token_refresh_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Refresh token invalide ou expiré"},
            status_code=401
        )


async def api_get_current_user(request: Request):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    Route: GET /api/users/me
    Returns: User info
    """
    try:
        from server.auth import get_current_user
        
        user = await get_current_user(request)
        
        if not user:
            return JSONResponse(
                {"error": "Non authentifié"},
                status_code=401
            )
        
        return JSONResponse(user, status_code=200)
        
    except Exception as user_retrieval_error:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {user_retrieval_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la récupération de l'utilisateur"},
            status_code=500
        )

