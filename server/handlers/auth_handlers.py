"""
Handlers pour l'authentification et la vérification d'email
"""
import os
import traceback
from datetime import datetime, timezone

from app.core.logging_config import get_logger

logger = get_logger(__name__)
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
            from app.core.config import settings
            access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            response_data = {
                "access_token": token_data.get("access_token"),
                "token_type": token_data.get("token_type", "bearer"),
                "expires_in": access_token_max_age,
                "refresh_token": token_data.get("refresh_token"),  # Inclure pour cross-domain support
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
            
            # Déterminer la configuration des cookies selon l'environnement
            # En production (cross-domain), utiliser SameSite=None et Secure=True
            import os
            is_production = (
                os.getenv("NODE_ENV") == "production" or 
                os.getenv("ENVIRONMENT") == "production" or
                os.getenv("MATH_TRAINER_PROFILE") == "prod"
            )
            cookie_samesite = "none" if is_production else "lax"
            cookie_secure = is_production  # Secure=True obligatoire avec SameSite=None
            
            # Définir le cookie access_token (pour compatibilité avec l'ancien système)
            response.set_cookie(
                key="access_token",
                value=token_data.get("access_token"),
                httponly=True,
                max_age=access_token_max_age,
                samesite=cookie_samesite,
                secure=cookie_secure
            )
            
            # Définir le cookie refresh_token (nécessaire pour le refresh automatique)
            refresh_token_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            refresh_token_value = token_data.get("refresh_token")
            if refresh_token_value:
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token_value,
                    httponly=True,
                    max_age=refresh_token_max_age,
                    samesite=cookie_samesite,
                    secure=cookie_secure
                )
                logger.info(f"Cookie refresh_token défini pour l'utilisateur: {user.username} (SameSite={cookie_samesite}, Secure={cookie_secure})")
            else:
                logger.error(f"ERREUR: refresh_token non créé pour l'utilisateur: {user.username}")
            
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
        
        # Log pour diagnostic
        all_cookies = list(request.cookies.keys())
        logger.debug(f"Cookies présents lors du refresh: {all_cookies}")
        
        if refresh_token:
            logger.debug(f"Refresh token reçu depuis {'body' if 'refresh_token' not in request.cookies else 'cookie'} (longueur: {len(refresh_token)})")
        else:
            logger.warning("Aucun refresh_token trouvé dans les cookies ou le body")
            # FALLBACK: Pour les utilisateurs existants qui n'ont pas de refresh_token,
            # essayer d'utiliser l'access_token comme fallback temporaire
            access_token_fallback = request.cookies.get('access_token', '').strip()
            if access_token_fallback:
                logger.warning("Tentative de fallback avec access_token (utilisateur existant sans refresh_token)")
                # Essayer de décoder l'access_token pour vérifier s'il est valide
                try:
                    import jwt
                    from app.core.config import settings
                    payload = jwt.decode(
                        access_token_fallback,
                        settings.SECRET_KEY,
                        algorithms=[settings.ALGORITHM],
                        options={"verify_exp": False}  # Ne pas vérifier l'expiration pour le fallback
                    )
                    # Si l'access_token est valide mais expiré, créer un nouveau refresh_token
                    username = payload.get("sub")
                    if username:
                        logger.info(f"Fallback: Création d'un nouveau refresh_token pour l'utilisateur existant: {username}")
                        db_fallback = EnhancedServerAdapter.get_db_session()
                        try:
                            from app.services.auth_service import get_user_by_username, create_user_token
                            user_fallback = get_user_by_username(db_fallback, username)
                            if user_fallback:
                                # Créer un nouveau refresh_token pour cet utilisateur
                                new_token_data_fallback = create_user_token(user_fallback)
                                refresh_token = new_token_data_fallback.get("refresh_token")
                                logger.info(f"Fallback: Nouveau refresh_token créé pour {username}")
                            else:
                                logger.warning(f"Fallback: Utilisateur {username} non trouvé")
                        finally:
                            EnhancedServerAdapter.close_db_session(db_fallback)
                except Exception as fallback_error:
                    logger.debug(f"Fallback échoué: {fallback_error}")
        
        if not refresh_token:
            return JSONResponse(
                {"error": "Refresh token requis (body ou cookie). Veuillez vous reconnecter."},
                status_code=400
            )
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Rafraîchir le token
            new_token_data = refresh_access_token(db, refresh_token)
            
            logger.info("Token rafraîchi avec succès")
            
            # Créer la réponse avec le nouveau token
            response = JSONResponse(new_token_data, status_code=200)
            
            # Déterminer la configuration des cookies selon l'environnement
            # En production (cross-domain), utiliser SameSite=None et Secure=True
            import os
            is_production = (
                os.getenv("NODE_ENV") == "production" or 
                os.getenv("ENVIRONMENT") == "production" or
                os.getenv("MATH_TRAINER_PROFILE") == "prod"
            )
            cookie_samesite = "none" if is_production else "lax"
            cookie_secure = is_production  # Secure=True obligatoire avec SameSite=None
            
            # Mettre à jour le cookie access_token si présent dans la réponse
            from app.core.config import settings
            if "access_token" in new_token_data:
                access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                response.set_cookie(
                    key="access_token",
                    value=new_token_data.get("access_token"),
                    httponly=True,
                    max_age=access_token_max_age,
                    samesite=cookie_samesite,
                    secure=cookie_secure
                )
            
            # Si le refresh_token a été créé via fallback, l'ajouter au cookie
            # Sinon, s'assurer que le refresh_token existe toujours dans les cookies
            refresh_token_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            if refresh_token and "refresh_token" not in request.cookies:
                # Refresh_token créé via fallback, l'ajouter au cookie
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    max_age=refresh_token_max_age,
                    samesite=cookie_samesite,
                    secure=cookie_secure
                )
                logger.info(f"Cookie refresh_token créé via fallback et ajouté à la réponse (SameSite={cookie_samesite}, Secure={cookie_secure})")
            
            # Toujours mettre à jour le refresh_token dans les cookies après un refresh réussi
            # pour s'assurer qu'il reste valide
            if "refresh_token" in new_token_data:
                response.set_cookie(
                    key="refresh_token",
                    value=new_token_data.get("refresh_token"),
                    httponly=True,
                    max_age=refresh_token_max_age,
                    samesite=cookie_samesite,
                    secure=cookie_secure
                )
                logger.debug(f"Cookie refresh_token mis à jour après refresh réussi (SameSite={cookie_samesite}, Secure={cookie_secure})")
            
            # Ajouter le refresh_token dans la réponse JSON pour le cross-domain support
            # Le frontend peut le stocker dans localStorage
            response_data = new_token_data.copy()
            if refresh_token and "refresh_token" not in response_data:
                # Si le refresh_token utilisé est toujours valide, le renvoyer
                response_data["refresh_token"] = refresh_token
            
            # Mettre à jour la réponse avec le refresh_token
            import json
            response.body = json.dumps(response_data).encode('utf-8')
            
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


async def api_forgot_password(request: Request):
    """
    Handler pour la fonctionnalité de mot de passe oublié (placeholder).
    Route: POST /api/auth/forgot-password
    """
    logger.info("Tentative d'accès à la fonctionnalité 'mot de passe oublié'.")
    return JSONResponse(
        {"message": "La fonctionnalité de réinitialisation de mot de passe est en cours de développement."},
        status_code=501  # Not Implemented
    )


async def api_logout(request: Request):
    """
    Déconnexion de l'utilisateur en effaçant les cookies d'authentification.
    Route: POST /api/auth/logout
    """
    try:
        response = JSONResponse({"message": "Déconnexion réussie"}, status_code=200)
        
        # Effacer les cookies d'authentification
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        logger.info("Utilisateur déconnecté : cookies d'authentification effacés.")
        return response
    except Exception as logout_error:
        logger.error(f"Erreur lors de la déconnexion: {logout_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la déconnexion"},
            status_code=500
        )



