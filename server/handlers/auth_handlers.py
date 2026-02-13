"""
Handlers pour l'authentification et la vérification d'email
"""
import os
import traceback
from datetime import datetime, timedelta, timezone

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from app.core.security import decode_token
from app.services.auth_service import (authenticate_user, create_user_token,
                                       get_user_by_email, refresh_access_token)
from app.utils.rate_limit import rate_limit_auth, rate_limit_resend_verification
from app.utils.csrf import validate_csrf_token
from server.auth import require_auth
from app.services.email_service import EmailService
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.core.security import get_password_hash
from app.utils.email_verification import (
    generate_verification_token,
    is_password_reset_token_expired,
    is_verification_token_expired,
)


async def api_get_csrf_token(request: Request):
    """
    Récupère un token CSRF (pattern double-submit).
    Route: GET /api/auth/csrf
    Retourne le token et le pose en cookie. Le client doit l'envoyer dans X-CSRF-Token.
    """
    import secrets
    token = secrets.token_urlsafe(32)
    response = JSONResponse({"csrf_token": token})
    is_production = (
        os.getenv("ENVIRONMENT") == "production"
        or os.getenv("NODE_ENV") == "production"
    )
    cookie_opts = (
        "Path=/; SameSite=None; Secure"
        if is_production
        else "Path=/; SameSite=Lax"
    )
    response.set_cookie(
        "csrf_token",
        token,
        path="/",
        samesite="none" if is_production else "lax",
        secure=is_production,
        httponly=False,  # Le client doit pouvoir lire pour l'envoyer dans le header (double-submit)
        max_age=3600,  # 1 heure
    )
    return response


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
            
            # Vérifier si l'email est déjà vérifié (idempotent : double-clic, refresh)
            if user.is_email_verified:
                return JSONResponse({
                    "message": "Votre adresse email est déjà vérifiée",
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_email_verified": True
                    }
                }, status_code=200)
            
            # Marquer l'email comme vérifié
            user.is_email_verified = True
            # Ne pas supprimer le token : permet requêtes idempotentes (double-clic, refresh)
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


@rate_limit_resend_verification
async def resend_verification_email(request: Request):
    """
    Renvoie l'email de vérification.
    Route: POST /api/auth/resend-verification
    Body: {"email": "user@example.com"}
    Rate limit: 2 req/min par IP (protection abus).
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
            
            # Rate limit : ne pas renvoyer avant 2 minutes
            if user.email_verification_sent_at:
                cooldown = user.email_verification_sent_at + timedelta(minutes=2)
                if datetime.now(timezone.utc) < cooldown:
                    return JSONResponse({
                        "message": "Veuillez patienter quelques minutes avant de demander un nouvel email."
                    }, status_code=200)  # 200 pour ne pas révéler l'existence du compte
            
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
                if "localhost" in frontend_url:
                    verify_link = f"{frontend_url}/verify-email?token={verification_token}"
                    logger.info(f"[DEV] Si l'email n'arrive pas, copie ce lien : {verify_link}")
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


@rate_limit_auth("login")
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

            if not getattr(user, 'is_email_verified', True):
                return JSONResponse(
                    {"error": "Veuillez vérifier votre adresse email avant de vous connecter. Consultez votre boîte de réception."},
                    status_code=403
                )
            
            # Créer les tokens d'accès
            token_data = create_user_token(user)
            logger.info(f"Connexion réussie pour l'utilisateur: {user.username}")
            
            # Ajouter les informations utilisateur à la réponse
            from app.core.config import settings
            access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            # refresh_token uniquement en cookie (HttpOnly) — pas dans le body (sécurité XSS)
            response_data = {
                "access_token": token_data.get("access_token"),
                "token_type": token_data.get("token_type", "bearer"),
                "expires_in": access_token_max_age,
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


@rate_limit_auth("validate-token")
async def api_validate_token(request: Request):
    """
    Valide un token JWT sans l'utiliser pour une action.
    Utilisé par la route sync-cookie du frontend pour s'assurer qu'un token
    est signé par notre backend et non expiré avant de le poser en cookie.
    Route: POST /api/auth/validate-token
    Body: {"token": "..."}
    Rate limit: 5 req/min par IP (protection brute-force).
    """
    try:
        data = await request.json()
        token = data.get("token")
        if not token or not isinstance(token, str):
            return JSONResponse({"valid": False, "error": "Token manquant"}, status_code=400)
        payload = decode_token(token)
        # Vérifier que c'est un access token (type=access)
        if payload.get("type") != "access":
            return JSONResponse({"valid": False}, status_code=401)
        return JSONResponse({"valid": True, "user_id": payload.get("sub")})
    except Exception:
        return JSONResponse({"valid": False}, status_code=401)


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
            
            # Rotation: nouveau refresh_token à chaque refresh — cookie HttpOnly uniquement
            if "refresh_token" in new_token_data:
                response.set_cookie(
                    key="refresh_token",
                    value=new_token_data.get("refresh_token"),
                    httponly=True,
                    max_age=refresh_token_max_age,
                    samesite=cookie_samesite,
                    secure=cookie_secure
                )
                logger.debug(f"Cookie refresh_token roté (SameSite={cookie_samesite}, Secure={cookie_secure})")
            
            # refresh_token UNIQUEMENT en cookie (HttpOnly) — jamais dans le body (sécurité XSS)
            response_data = {
                "access_token": new_token_data.get("access_token"),
                "token_type": new_token_data.get("token_type", "bearer"),
            }
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


@require_auth
async def api_get_current_user(request: Request):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    Route: GET /api/users/me
    Returns: User info
    """
    try:
        current_user = request.state.user
        return JSONResponse(current_user, status_code=200)
        
    except Exception as user_retrieval_error:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {user_retrieval_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la récupération de l'utilisateur"},
            status_code=500
        )


@rate_limit_auth("forgot-password")
async def api_forgot_password(request: Request):
    """
    Demande de réinitialisation de mot de passe.
    Génère un token, le stocke en DB, et envoie un email avec le lien.
    Route: POST /api/auth/forgot-password
    Body: {"email": "user@example.com"}
    """
    try:
        data = await request.json()
        email = data.get('email', '').strip().lower()

        if not email:
            return JSONResponse(
                {"error": "Adresse email requise"},
                status_code=400
            )

        db = EnhancedServerAdapter.get_db_session()
        try:
            user = get_user_by_email(db, email)

            # Pour la sécurité, toujours retourner le même message (évite l'énumération d'emails)
            success_message = (
                "Si cette adresse email est associée à un compte, "
                "vous recevrez un email avec les instructions de réinitialisation."
            )

            if not user:
                logger.warning(f"Demande reset password pour email inexistant: {email}")
                return JSONResponse({"message": success_message}, status_code=200)

            if not user.is_active:
                logger.warning(f"Demande reset password pour compte inactif: {email}")
                return JSONResponse({"message": success_message}, status_code=200)

            # Générer token (1h d'expiration)
            reset_token = generate_verification_token()
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            user.password_reset_token = reset_token
            user.password_reset_expires_at = expires_at
            user.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(user)

            frontend_url = os.getenv("FRONTEND_URL", "https://mathakine-frontend.onrender.com")
            email_sent = EmailService.send_password_reset_email(
                to_email=user.email,
                username=user.username,
                reset_token=reset_token,
                frontend_url=frontend_url
            )

            if not email_sent:
                logger.warning(f"Échec envoi email reset à {user.email}")
                return JSONResponse(
                    {"error": "Impossible d'envoyer l'email. Veuillez réessayer plus tard."},
                    status_code=500
                )

            logger.info(f"Email de réinitialisation envoyé à {user.email}")
            # En dev avec localhost : Gmail filtre souvent ces emails. Afficher le lien en console pour tester.
            if "localhost" in frontend_url:
                reset_link = f"{frontend_url}/reset-password?token={reset_token}"
                logger.info(f"[DEV] Si l'email n'arrive pas (filtre Gmail), copie ce lien : {reset_link}")
            return JSONResponse({"message": success_message}, status_code=200)

        finally:
            EnhancedServerAdapter.close_db_session(db)

    except Exception as forgot_err:
        logger.error(f"Erreur forgot-password: {forgot_err}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors du traitement de la demande"},
            status_code=500
        )


async def api_reset_password(request: Request):
    """
    Réinitialise le mot de passe avec un token valide.
    Route: POST /api/auth/reset-password
    Body: {"token": "...", "password": "...", "password_confirm": "..."}
    Protégé CSRF (audit 3.2).
    """
    csrf_err = validate_csrf_token(request)
    if csrf_err:
        return csrf_err
    try:
        data = await request.json()
        token = (data.get('token') or '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')

        if not token:
            return JSONResponse(
                {"error": "Token de réinitialisation manquant"},
                status_code=400
            )

        if not password or len(password) < 8:
            return JSONResponse(
                {"error": "Le mot de passe doit contenir au moins 8 caractères"},
                status_code=400
            )
        if not any(char.isdigit() for char in password):
            return JSONResponse(
                {"error": "Le mot de passe doit contenir au moins un chiffre"},
                status_code=400
            )
        if not any(char.isupper() for char in password):
            return JSONResponse(
                {"error": "Le mot de passe doit contenir au moins une majuscule"},
                status_code=400
            )

        if password != password_confirm:
            return JSONResponse(
                {"error": "Les mots de passe ne correspondent pas"},
                status_code=400
            )

        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.user import User
            user = db.query(User).filter(User.password_reset_token == token).first()

            if not user:
                return JSONResponse(
                    {"error": "Token invalide ou déjà utilisé"},
                    status_code=400
                )

            if is_password_reset_token_expired(user.password_reset_expires_at):
                return JSONResponse(
                    {"error": "Le lien a expiré. Veuillez demander un nouveau lien."},
                    status_code=400
                )

            user.hashed_password = get_password_hash(password)
            user.password_reset_token = None
            user.password_reset_expires_at = None
            user.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(user)

            logger.info(f"Mot de passe réinitialisé pour {user.username}")
            return JSONResponse({
                "message": "Mot de passe réinitialisé avec succès. Vous pouvez vous connecter.",
                "success": True
            }, status_code=200)

        finally:
            EnhancedServerAdapter.close_db_session(db)

    except Exception as reset_err:
        logger.error(f"Erreur reset-password: {reset_err}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la réinitialisation du mot de passe"},
            status_code=500
        )


async def api_logout(request: Request):
    """
    Déconnexion de l'utilisateur en effaçant les cookies d'authentification.
    Route: POST /api/auth/logout

    IMPORTANT: En prod cross-domain, les cookies sont définis avec SameSite=None, Secure.
    delete_cookie DOIT utiliser les mêmes paramètres sinon le navigateur ignore la suppression.
    """
    try:
        response = JSONResponse({"message": "Déconnexion réussie"}, status_code=200)

        is_production = (
            os.getenv("NODE_ENV") == "production"
            or os.getenv("ENVIRONMENT") == "production"
            or os.getenv("MATH_TRAINER_PROFILE") == "prod"
        )
        cookie_samesite = "none" if is_production else "lax"
        cookie_secure = is_production

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

        logger.info("Utilisateur déconnecté : cookies d'authentification effacés.")
        return response
    except Exception as logout_error:
        logger.error(f"Erreur lors de la déconnexion: {logout_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la déconnexion"},
            status_code=500
        )



