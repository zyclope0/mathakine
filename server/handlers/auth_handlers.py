"""
Handlers pour l'authentification et la vérification d'email
"""

import secrets
import traceback
from typing import Optional

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.security import get_cookie_config
from app.schemas.user import ResetPasswordRequest
from app.services.auth_recovery_service import (
    AuthRecoveryError,
    perform_forgot_password as svc_perform_forgot_password,
    perform_resend_verification as svc_perform_resend_verification,
    perform_reset_password as svc_perform_reset_password,
    perform_verify_email as svc_perform_verify_email,
)
from app.services.auth_session_service import (
    perform_login as svc_perform_login,
    perform_refresh as svc_perform_refresh,
    recover_refresh_token_fallback as svc_recover_refresh_fallback,
    validate_access_token as svc_validate_access_token,
)
from app.utils.error_handler import api_error_response
from app.utils.rate_limit import rate_limit_auth, rate_limit_resend_verification
from app.utils.request_utils import parse_json_body, parse_json_body_any
from server.auth import require_auth


def _set_auth_cookie(
    response: JSONResponse, key: str, value: str, *, max_age: int
) -> None:
    cookie_samesite, cookie_secure = get_cookie_config()
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        max_age=max_age,
        samesite=cookie_samesite,
        secure=cookie_secure,
    )


def _set_csrf_cookie(response: JSONResponse, csrf_token: str) -> None:
    cookie_samesite, cookie_secure = get_cookie_config()
    response.set_cookie(
        "csrf_token",
        csrf_token,
        path="/",
        samesite=cookie_samesite,
        secure=cookie_secure,
        httponly=False,
        max_age=3600,
    )


def _build_login_response(user_payload: dict, token_data: dict) -> JSONResponse:
    access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_token_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    csrf_token = secrets.token_urlsafe(32)
    response = JSONResponse(
        {
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type", "bearer"),
            "expires_in": access_token_max_age,
            "csrf_token": csrf_token,
            "user": user_payload,
        },
        status_code=200,
    )

    if token_data.get("access_token"):
        _set_auth_cookie(
            response,
            "access_token",
            token_data["access_token"],
            max_age=access_token_max_age,
        )
    if token_data.get("refresh_token"):
        _set_auth_cookie(
            response,
            "refresh_token",
            token_data["refresh_token"],
            max_age=refresh_token_max_age,
        )
    _set_csrf_cookie(response, csrf_token)
    return response


async def _extract_refresh_token_from_request(request: Request) -> Optional[str]:
    try:
        body_content = await request.body()
    except Exception:
        body_content = b""

    if body_content:
        import json

        try:
            data = json.loads(body_content.decode("utf-8"))
            if data:
                refresh_token = data.get("refresh_token", "").strip()
                if refresh_token:
                    return refresh_token
        except (ValueError, json.JSONDecodeError):
            pass

    return request.cookies.get("refresh_token", "").strip() or None


def _build_refresh_response(
    new_token_data: dict,
    *,
    fallback_refresh_token: Optional[str],
    had_refresh_cookie: bool,
) -> JSONResponse:
    access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_token_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    csrf_token = secrets.token_urlsafe(32)
    response = JSONResponse(
        {
            "access_token": new_token_data.get("access_token"),
            "token_type": new_token_data.get("token_type", "bearer"),
            "csrf_token": csrf_token,
        },
        status_code=200,
    )

    if new_token_data.get("access_token"):
        _set_auth_cookie(
            response,
            "access_token",
            new_token_data["access_token"],
            max_age=access_token_max_age,
        )

    refresh_token_to_set = new_token_data.get("refresh_token")
    if not refresh_token_to_set and fallback_refresh_token and not had_refresh_cookie:
        refresh_token_to_set = fallback_refresh_token

    if refresh_token_to_set:
        _set_auth_cookie(
            response,
            "refresh_token",
            refresh_token_to_set,
            max_age=refresh_token_max_age,
        )

    _set_csrf_cookie(response, csrf_token)
    return response


async def api_get_csrf_token(request: Request) -> JSONResponse:
    """
    Récupère un token CSRF (pattern double-submit).
    Route: GET /api/auth/csrf
    Retourne le token et le pose en cookie. Le client doit l'envoyer dans X-CSRF-Token.
    """
    import secrets

    token = secrets.token_urlsafe(32)
    response = JSONResponse({"csrf_token": token})
    cookie_samesite, cookie_secure = get_cookie_config()
    response.set_cookie(
        "csrf_token",
        token,
        path="/",
        samesite=cookie_samesite,
        secure=cookie_secure,
        httponly=False,  # Le client doit pouvoir lire pour l'envoyer dans le header (double-submit)
        max_age=3600,  # 1 heure
    )
    return response


async def verify_email(request: Request) -> JSONResponse:
    """
    Vérifie l'adresse email d'un utilisateur avec un token.
    Route: GET /api/auth/verify-email?token=...
    """
    try:
        token = request.query_params.get("token")

        if not token:
            return api_error_response(400, "Token de vérification manquant")

        result = await svc_perform_verify_email(token)

        if result.state == "already_verified":
            return JSONResponse(
                {
                    "message": "Votre adresse email est déjà vérifiée",
                    "success": True,
                    "user": result.user_payload,
                },
                status_code=200,
            )

        return JSONResponse(
            {
                "message": "Votre adresse email a été vérifiée avec succès !",
                "success": True,
                "user": result.user_payload,
            },
            status_code=200,
        )

    except AuthRecoveryError as e:
        if e.code == "invalid":
            return api_error_response(400, "Token de vérification invalide")
        if e.code == "expired":
            return api_error_response(
                400,
                "Le token de vérification a expiré. Veuillez demander un nouveau lien.",
            )
        raise
    except Exception as email_verification_error:
        logger.error(
            f"Erreur lors de la vérification de l'email: {email_verification_error}"
        )
        logger.debug(traceback.format_exc())
        return api_error_response(500, "Erreur lors de la vérification de l'email")


@rate_limit_resend_verification
async def resend_verification_email(request: Request) -> JSONResponse:
    """
    Renvoie l'email de vérification.
    Route: POST /api/auth/resend-verification
    Body: {"email": "user@example.com"}
    Rate limit: 2 req/min par IP (protection abus).
    """
    try:
        data_or_err = await parse_json_body(
            request, required={"email": "Adresse email requise"}
        )
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        # Extraction brute (pas EmailStr) : email mal formé = même chemin que user not found
        # → 200 + message générique, sans révéler l'existence du compte
        email = (data_or_err.get("email") or "").strip().lower()
        if not email:
            return api_error_response(400, "Adresse email requise")

        result = await svc_perform_resend_verification(email)

        if result.outcome == "user_not_found":
            return JSONResponse(
                {
                    "message": "Si cette adresse email est associée à un compte non vérifié, vous recevrez un email de vérification."
                },
                status_code=200,
            )

        if result.outcome == "already_verified":
            return JSONResponse(
                {"message": "Votre adresse email est déjà vérifiée"},
                status_code=200,
            )

        if result.outcome == "cooldown":
            return JSONResponse(
                {
                    "message": "Veuillez patienter quelques minutes avant de demander un nouvel email."
                },
                status_code=200,
            )

        # result.outcome == "sent"
        if "localhost" in settings.FRONTEND_URL:
            logger.info("[DEV] email vérification renvoyé")
        return JSONResponse(
            {
                "message": "Un nouvel email de vérification a été envoyé à votre adresse."
            },
            status_code=200,
        )

    except AuthRecoveryError as e:
        if e.code == "email_send_failed":
            return api_error_response(
                500,
                "Impossible d'envoyer l'email de vérification. Veuillez réessayer plus tard.",
            )
        raise
    except Exception as resend_verification_error:
        logger.error(
            f"Erreur lors du renvoi de l'email de vérification: {resend_verification_error}"
        )
        logger.debug(traceback.format_exc())
        return api_error_response(
            500, "Erreur lors du renvoi de l'email de vérification"
        )


@rate_limit_auth("login")
async def api_login(request: Request) -> JSONResponse:
    """
    Connexion avec nom d'utilisateur et mot de passe.
    Route: POST /api/auth/login
    Body: {"username": "...", "password": "..."}
    Returns: Token + user info
    """
    try:
        data_or_err = await parse_json_body(
            request,
            required={
                "username": "Nom d'utilisateur requis",
                "password": "Mot de passe requis",
            },
            no_strip_fields={"password"},
        )
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        username = data_or_err["username"]
        password = data_or_err["password"]
        logger.debug(f"Tentative de connexion pour l'utilisateur: {username}")

        user_payload, token_data = await svc_perform_login(
            username,
            password,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent") or "",
        )

        if not user_payload:
            logger.warning(f"Échec de connexion pour l'utilisateur: {username}")
            return api_error_response(
                401, "Nom d'utilisateur ou mot de passe incorrect"
            )

        logger.info(
            f"Connexion réussie pour l'utilisateur: {user_payload.get('username')}"
        )
        return _build_login_response(user_payload, token_data)

    except Exception as login_error:
        logger.error(f"Erreur lors de la connexion: {login_error}")
        logger.debug(traceback.format_exc())
        return api_error_response(500, "Erreur lors de la connexion")


@rate_limit_auth("validate-token")
async def api_validate_token(request: Request) -> JSONResponse:
    """
    Valide un token JWT sans l'utiliser pour une action.
    Utilisé par la route sync-cookie du frontend pour s'assurer qu'un token
    est signé par notre backend et non expiré avant de le poser en cookie.
    Route: POST /api/auth/validate-token
    Body: {"token": "..."}
    Rate limit: 5 req/min par IP (protection brute-force).
    """
    try:
        data_or_err = await parse_json_body(
            request, required={"token": "Token manquant"}, no_strip_fields={"token"}
        )
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        token = data_or_err["token"]
        if not isinstance(token, str):
            return api_error_response(400, "Token invalide")
        result = svc_validate_access_token(token)
        return JSONResponse(result)
    except Exception:
        return api_error_response(401, "Token invalide ou expiré")


async def api_refresh_token(request: Request) -> JSONResponse:
    """
    Rafraîchit le token d'accès avec un refresh token.
    Route: POST /api/auth/refresh
    Body (optionnel): {"refresh_token": "..."}
    Cookie (optionnel): refresh_token
    Returns: New access token
    """
    try:
        refresh_token = await _extract_refresh_token_from_request(request)

        if not refresh_token:
            logger.warning("Aucun refresh_token trouvé dans les cookies ou le body")
            access_token = request.cookies.get("access_token", "").strip()
            refresh_token = await svc_recover_refresh_fallback(access_token)

        if not refresh_token:
            return api_error_response(
                401,
                "Refresh token requis (body ou cookie). Veuillez vous reconnecter.",
            )

        new_token_data, refresh_err, refresh_status = await svc_perform_refresh(
            refresh_token
        )
        if refresh_err:
            return api_error_response(refresh_status, refresh_err)

        logger.info("Token rafraîchi avec succès")
        return _build_refresh_response(
            new_token_data,
            fallback_refresh_token=refresh_token,
            had_refresh_cookie="refresh_token" in request.cookies,
        )

    except Exception as token_refresh_error:
        logger.error(f"Erreur lors du rafraîchissement du token: {token_refresh_error}")
        logger.debug(traceback.format_exc())
        return api_error_response(401, "Refresh token invalide ou expiré")


@require_auth
async def api_get_current_user(request: Request) -> JSONResponse:
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    Route: GET /api/users/me
    Returns: User info
    """
    try:
        current_user = request.state.user
        return JSONResponse(current_user, status_code=200)

    except Exception as user_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération de l'utilisateur: {user_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return api_error_response(
            500, "Erreur lors de la récupération de l'utilisateur"
        )


SUCCESS_MESSAGE_FORGOT = (
    "Si cette adresse email est associée à un compte, "
    "vous recevrez un email avec les instructions de réinitialisation."
)


@rate_limit_auth("forgot-password")
async def api_forgot_password(request: Request) -> JSONResponse:
    """
    Demande de réinitialisation de mot de passe.
    Génère un token, le stocke en DB, et envoie un email avec le lien.
    Route: POST /api/auth/forgot-password
    Body: {"email": "user@example.com"}
    """
    try:
        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        email = data_or_err.get("email", "").strip().lower()

        if not email:
            return api_error_response(400, "Adresse email requise")

        result = await svc_perform_forgot_password(email)

        if result.outcome == "sent" and "localhost" in settings.FRONTEND_URL:
            logger.info("[DEV] email reset envoyé")

        return JSONResponse({"message": SUCCESS_MESSAGE_FORGOT}, status_code=200)

    except AuthRecoveryError as e:
        if e.code == "email_send_failed":
            return api_error_response(
                500,
                "Impossible d'envoyer l'email. Veuillez réessayer plus tard.",
            )
        raise
    except Exception as forgot_err:
        logger.error(f"Erreur forgot-password: {forgot_err}")
        logger.debug(traceback.format_exc())
        return api_error_response(500, "Erreur lors du traitement de la demande")


def _extract_validation_message(exc) -> str:
    """Extrait le message de la première erreur de validation Pydantic."""
    errs = getattr(exc, "errors", lambda: [])()
    if errs and isinstance(errs, list):
        msg = errs[0].get("msg", "Erreur de validation")
        if isinstance(msg, str) and msg.startswith("Value error, "):
            return msg[13:]
        return str(msg)
    return "Erreur de validation"


async def api_reset_password(request: Request) -> JSONResponse:
    """
    Réinitialise le mot de passe avec un token valide.
    Route: POST /api/auth/reset-password
    Body: {"token": "...", "password": "...", "password_confirm": "..."}
    Protégé CSRF via CsrfMiddleware (audit H6).
    """
    try:
        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err

        try:
            req = ResetPasswordRequest.model_validate(data_or_err)
        except ValidationError as ve:
            return api_error_response(400, _extract_validation_message(ve))

        await svc_perform_reset_password(req.token, req.password)

        return JSONResponse(
            {
                "message": "Mot de passe réinitialisé avec succès. Vous pouvez vous connecter.",
                "success": True,
            },
            status_code=200,
        )

    except AuthRecoveryError as e:
        if e.code == "invalid":
            return api_error_response(400, "Token invalide ou déjà utilisé")
        if e.code == "expired":
            return api_error_response(
                400, "Le lien a expiré. Veuillez demander un nouveau lien."
            )
        raise
    except Exception as reset_err:
        logger.error(f"Erreur reset-password: {reset_err}")
        logger.debug(traceback.format_exc())
        return api_error_response(
            500, "Erreur lors de la réinitialisation du mot de passe"
        )


async def api_logout(request: Request) -> JSONResponse:
    """
    Déconnexion de l'utilisateur en effaçant les cookies d'authentification.
    Route: POST /api/auth/logout

    IMPORTANT: En prod cross-domain, les cookies sont définis avec SameSite=None, Secure.
    delete_cookie DOIT utiliser les mêmes paramètres sinon le navigateur ignore la suppression.
    """
    try:
        response = JSONResponse({"message": "Déconnexion réussie"}, status_code=200)

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

        logger.info("Utilisateur déconnecté : cookies d'authentification effacés.")
        return response
    except Exception as logout_error:
        logger.error(f"Erreur lors de la déconnexion: {logout_error}")
        logger.debug(traceback.format_exc())
        return api_error_response(500, "Erreur lors de la déconnexion")
