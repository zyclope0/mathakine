"""
Middleware for Mathakine.

This module centralizes Starlette middleware logic for consistent
request processing across the application.
"""

import re
import uuid
from typing import Callable, List, Set, Tuple

from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.core.config import _is_production, settings
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.utils.error_handler import api_error_response
from app.utils.settings_reader import get_setting_bool

logger = get_logger(__name__)

# Routes exemptées du mode maintenance (admin peut se connecter et désactiver)
# Headers de sécurité (OWASP) — appliqués si SECURE_HEADERS=true
SECURE_HEADERS_DICT = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

# EdTech / API : pas de besoin caméra, micro, géoloc ; policy minimale (SEC-HARDEN-01).
PERMISSIONS_POLICY_VALUE = "camera=(), microphone=(), geolocation=()"

# HTTPS uniquement en prod réelle — jamais en local/dev (navigateur pourrait mémoriser HSTS HTTP).
HSTS_VALUE = "max-age=31536000; includeSubDomains"

REQUEST_ID_HEADER = "X-Request-ID"


def _get_header(scope: dict, name: str) -> str | None:
    """Extrait une valeur de header depuis scope (ASGI)."""
    name_lower = name.lower().encode()
    for key, value in scope.get("headers", []):
        if key.lower() == name_lower:
            return value.decode("latin-1")
    return None


class RequestIdMiddleware:
    """
    Middleware ASGI pur : génère un request_id par requête pour corrélation logs / Sentry.

    Utilise ASGI natif (pas BaseHTTPMiddleware) pour éviter LocalProtocolError
    "Can't send data when our state is ERROR" avec streaming / déconnexion client.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        rid = _get_header(scope, REQUEST_ID_HEADER) or str(uuid.uuid4())[:12]

        # scope["state"] = dict pour que Request.state utilise State(dict) — pas State(State)
        scope.setdefault("state", {})
        scope["state"]["request_id"] = rid

        from app.core.logging_config import request_id_ctx

        token = request_id_ctx.set(rid)

        try:
            try:
                import sentry_sdk

                sentry_sdk.set_tag("request_id", rid)
            except ImportError:
                pass

            async def send_wrapper(message):
                if message.get("type") == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((REQUEST_ID_HEADER.encode(), rid.encode()))
                    message = {**message, "headers": headers}
                await send(message)

            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_ctx.reset(token)


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Ajoute les headers de sécurité HTTP (X-Content-Type-Options, X-Frame-Options, etc.) si config activée."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        if settings.SECURE_HEADERS:
            for key, value in SECURE_HEADERS_DICT.items():
                response.headers[key] = value
            response.headers["Permissions-Policy"] = PERMISSIONS_POLICY_VALUE
            if _is_production():
                response.headers["Strict-Transport-Security"] = HSTS_VALUE
        return response


MAINTENANCE_EXEMPT_PREFIXES = (
    "/live",
    "/ready",
    "/health",
    "/metrics",
    "/api/admin",
    "/api/auth/login",
    "/api/auth/refresh",
    "/api/auth/validate-token",
    "/api/auth/csrf",
)


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """
    Bloque les requêtes si maintenance_mode est activé (sauf routes exemptées).

    Politique fail-open: si la vérification maintenance échoue (ex. DB indisponible),
    la requête est laissée passer. Choix volontaire pour éviter de bloquer tout le site
    quand seul le check maintenance casse.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        if any(request.url.path.startswith(p) for p in MAINTENANCE_EXEMPT_PREFIXES):
            return await call_next(request)
        try:
            if await run_db_bound(get_setting_bool, "maintenance_mode", False):
                return api_error_response(
                    503, "Le temple est en maintenance. Réessayez plus tard."
                )
        except Exception as e:
            # Fail-open volontaire: laisser passer la requête si le check échoue
            logger.warning(
                f"Maintenance check failed: {e} — fail-open, requête autorisée"
            )
        return await call_next(request)


# ============================================================================
# A6 — Registre unique de routes publiques / exemptées
# Source unique pour auth-whitelist et CSRF-exempt. Chaque entrée :
#   (path, méthodes_autorisées_sans_auth, csrf_exempt?)
# csrf_exempt = True → POST/PUT/PATCH/DELETE ne vérifient pas le CSRF token
#   (routes où l'utilisateur n'a pas encore de session → pas de cookie CSRF).
# ============================================================================
_ROUTE_REGISTRY: List[Tuple[str, Set[str], bool]] = [
    # Infra
    ("/", {"GET", "HEAD"}, False),
    ("/live", {"GET"}, False),
    ("/ready", {"GET"}, False),
    ("/health", {"GET"}, False),
    ("/robots.txt", {"GET"}, False),
    ("/metrics", {"GET"}, False),
    # Auth — pré-session (pas de cookie CSRF dispo)
    ("/api/auth/login", {"POST"}, True),
    ("/api/auth/logout", {"POST"}, True),
    ("/api/auth/validate-token", {"POST"}, True),
    ("/api/auth/csrf", {"GET"}, False),
    ("/api/auth/refresh", {"POST"}, True),
    ("/api/auth/forgot-password", {"POST"}, True),
    ("/api/auth/reset-password", {"POST"}, False),  # formulaire = CSRF requis
    ("/api/auth/verify-email", {"GET"}, False),
    ("/api/auth/resend-verification", {"POST"}, True),
    # Inscription
    ("/api/users/", {"POST"}, True),
    # Lecture publique
    ("/api/exercises", {"GET"}, False),
    ("/api/exercises/stats", {"GET"}, False),
    ("/api/exercises/completed-ids", {"GET"}, False),
    ("/api/challenges/completed-ids", {"GET"}, False),
    ("/api/badges/available", {"GET"}, False),
    ("/api/badges/rarity", {"GET"}, False),
    # Chatbot — auth obligatoire (CHAT-AUTH-01) ; plus de whitelist publique
]

# Dérivations — calculées une seule fois au chargement du module
_AUTH_PUBLIC_EXACT: List[Tuple[str, Set[str]]] = [
    (path, methods) for path, methods, _ in _ROUTE_REGISTRY
]
_AUTH_PUBLIC_PATTERNS: List[Tuple[re.Pattern, Set[str]]] = [
    (re.compile(r"^/api/exercises/\d+$"), {"GET"}),
]

_CSRF_EXEMPT_NORMALIZED: frozenset = frozenset(
    path.rstrip("/") for path, _, csrf in _ROUTE_REGISTRY if csrf
)
_CSRF_MUTATING_METHODS: Set[str] = {"POST", "PUT", "PATCH", "DELETE"}


def _has_auth_credentials(request: Request) -> bool:
    """True si la requête porte déjà des credentials d'authentification exploitables."""
    access_token = request.cookies.get("access_token")
    if access_token:
        return True

    auth_header = request.headers.get("Authorization", "")
    return auth_header.startswith("Bearer ") and len(auth_header[7:].strip()) > 0


def _is_auth_public(path: str, method: str) -> bool:
    """True si la route est explicitement autorisée sans token."""
    for route_path, methods in _AUTH_PUBLIC_EXACT:
        if path == route_path or path.rstrip("/") == route_path.rstrip("/"):
            if method in methods:
                return True
    for pattern, methods in _AUTH_PUBLIC_PATTERNS:
        if pattern.match(path) and method in methods:
            return True
    return False


class CsrfMiddleware(BaseHTTPMiddleware):
    """
    Protection CSRF centralisée (audit H6).

    Vérifie le token CSRF (pattern double-submit) sur toutes les requêtes
    mutantes sauf les routes exemptées (login, inscription, etc.).
    """

    async def dispatch(self, request: Request, call_next: Callable):
        if request.method not in _CSRF_MUTATING_METHODS:
            return await call_next(request)
        path = request.url.path.rstrip("/") or "/"
        if path in _CSRF_EXEMPT_NORMALIZED:
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)
        if not _has_auth_credentials(request):
            # Laisse l'AuthenticationMiddleware produire le 401 canonique.
            return await call_next(request)

        from app.utils.csrf import validate_csrf_token

        csrf_err = validate_csrf_token(request)
        if csrf_err:
            return csrf_err
        return await call_next(request)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware d'authentification deny-by-default.

    Seules les routes de la whitelist sont accessibles sans token.
    Les routes /api/* non listées exigent un cookie access_token valide.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        method = request.method

        if _is_auth_public(path, method):
            return await call_next(request)

        # Routes hors /api : health, metrics, robots - déjà gérées en exact
        if not path.startswith("/api/"):
            return await call_next(request)

        access_token = request.cookies.get("access_token")
        if not access_token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                access_token = auth_header[7:].strip()
        if not access_token:
            logger.info(f"Unauthorized access attempt to {request.url.path}")
            return api_error_response(401, "Authentication required")

        try:
            # Verify the token (une seule fois — réutilisé par get_current_user)
            from app.core.security import decode_token

            payload = decode_token(access_token)
            request.state.auth_payload = payload

            # Contexte utilisateur Sentry — permet de corréler erreurs + "User Impact"
            try:
                import sentry_sdk

                sentry_sdk.set_user(
                    {
                        "username": payload.get("sub"),
                        "id": str(payload.get("user_id", payload.get("sub", ""))),
                    }
                )
            except Exception:
                pass

            # Continue with the request if token is valid
            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            # 401 attendu : token expiré ou invalide — pas une erreur applicative
            logger.warning(
                f"Unauthorized request to {request.url.path}: {http_exc.detail}"
            )
            return api_error_response(http_exc.status_code, http_exc.detail)
        except Exception as auth_error:
            # Erreur inattendue lors du décodage (ex. clé corrompue, librairie)
            logger.error(
                f"Unexpected auth error for {request.url.path}: {str(auth_error)}"
            )
            return api_error_response(401, "Invalid or expired token")


def get_middleware() -> List[Middleware]:
    """
    Get the list of middleware for use in Starlette app initialization.

    Returns:
        List of Middleware instances
    """
    # P1 — source unique : settings.BACKEND_CORS_ORIGINS (config.py)
    allowed_origins = settings.BACKEND_CORS_ORIGINS

    middleware_list = []

    # Request ID (corrélation logs + Sentry) — en premier
    middleware_list.append(Middleware(RequestIdMiddleware))

    # Prometheus métriques (audit HIGH #1) — capture toutes les requêtes
    try:
        from app.core.monitoring import PrometheusMetricsMiddleware

        middleware_list.append(Middleware(PrometheusMetricsMiddleware))
    except ImportError:
        pass

    middleware_list.extend(
        [
            Middleware(SecureHeadersMiddleware),
            Middleware(
                CORSMiddleware,
                allow_origins=allowed_origins,
                allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                # Audit 4.2: restreindre aux headers utilisés par le frontend
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "Accept",
                    "Accept-Language",
                    "X-CSRF-Token",  # Protection CSRF (audit 3.2)
                ],
                allow_credentials=True,  # Important pour les cookies HTTP-only
            ),
            Middleware(MaintenanceMiddleware),
            Middleware(CsrfMiddleware),
            Middleware(AuthenticationMiddleware),
        ]
    )

    return middleware_list
