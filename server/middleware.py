"""
Middleware for Mathakine.

This module centralizes Starlette middleware logic for consistent
request processing across the application.
"""

import os
import re
import uuid
from typing import Callable, List, Set, Tuple

from app.core.config import settings
from app.core.logging_config import get_logger
from app.utils.settings_reader import get_setting_bool

logger = get_logger(__name__)
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Routes exemptées du mode maintenance (admin peut se connecter et désactiver)
# Headers de sécurité (OWASP) — appliqués si SECURE_HEADERS=true
SECURE_HEADERS_DICT = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Génère un request_id par requête pour corrélation logs / Sentry.
    Un seul outil : Sentry pour erreurs + métriques + corrélation.
    """

    REQUEST_ID_HEADER = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: Callable):
        from app.core.logging_config import request_id_ctx

        # Réutiliser un ID client si fourni (traçabilité distribuée)
        rid = request.headers.get(self.REQUEST_ID_HEADER) or str(uuid.uuid4())[:12]
        request.state.request_id = rid
        token = request_id_ctx.set(rid)

        try:
            # Tag Sentry pour corrélation erreurs ↔ logs
            try:
                import sentry_sdk

                sentry_sdk.set_tag("request_id", rid)
            except ImportError:
                pass

            response = await call_next(request)
            response.headers[self.REQUEST_ID_HEADER] = rid
            return response
        finally:
            request_id_ctx.reset(token)


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Ajoute les headers de sécurité HTTP (X-Content-Type-Options, X-Frame-Options, etc.) si config activée."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        if settings.SECURE_HEADERS:
            for key, value in SECURE_HEADERS_DICT.items():
                response.headers[key] = value
        return response


MAINTENANCE_EXEMPT_PREFIXES = (
    "/health",
    "/metrics",
    "/api/admin",
    "/api/auth/login",
    "/api/auth/refresh",
    "/api/auth/validate-token",
    "/api/auth/csrf",
)


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """Bloque les requêtes si maintenance_mode est activé (sauf routes exemptées)."""

    async def dispatch(self, request: Request, call_next: Callable):
        if any(request.url.path.startswith(p) for p in MAINTENANCE_EXEMPT_PREFIXES):
            return await call_next(request)
        try:
            if await get_setting_bool("maintenance_mode", False):
                return JSONResponse(
                    {
                        "error": "maintenance",
                        "message": "Le temple est en maintenance. Réessayez plus tard.",
                    },
                    status_code=503,
                )
        except Exception as e:
            logger.debug(f"Maintenance check failed (default: off): {e}")
        return await call_next(request)


# Whitelist deny-by-default : seules ces routes sont accessibles sans token.
# Format : (path_exact ou path_prefix, méthodes autorisées, None=exact, True=prefix)
# Les routes /api/* non listées exigent l'auth au niveau middleware.
_AUTH_PUBLIC_EXACT: List[Tuple[str, Set[str]]] = [
    ("/health", {"GET"}),
    ("/robots.txt", {"GET"}),
    ("/metrics", {"GET"}),
    ("/api/auth/login", {"POST"}),
    ("/api/auth/logout", {"POST"}),
    ("/api/auth/validate-token", {"POST"}),
    ("/api/auth/csrf", {"GET"}),
    ("/api/auth/refresh", {"POST"}),
    ("/api/auth/forgot-password", {"POST"}),
    ("/api/auth/reset-password", {"POST"}),
    ("/api/auth/verify-email", {"GET"}),
    ("/api/auth/resend-verification", {"POST"}),
    ("/api/users/", {"POST"}),  # Inscription uniquement ; GET = admin (auth)
    ("/api/exercises", {"GET"}),
    ("/api/exercises/stats", {"GET"}),
    ("/api/exercises/completed-ids", {"GET"}),
    ("/api/challenges/completed-ids", {"GET"}),
    ("/api/badges/available", {"GET"}),
    ("/api/badges/rarity", {"GET"}),
    ("/api/users/leaderboard", {"GET"}),
]
_AUTH_PUBLIC_PATTERNS: List[Tuple[re.Pattern, Set[str]]] = [
    # Détail exercice (get_exercise sans décorateur = public)
    (re.compile(r"^/api/exercises/\d+$"), {"GET"}),
]


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
            logger.info(f"Unauthorized access attempt to {request.url.path}")
            # Return 401 JSON response (API backend, no HTML redirect)
            return JSONResponse(
                {"error": "Unauthorized", "message": "Authentication required"},
                status_code=401,
            )

        try:
            # Verify the token (une seule fois — réutilisé par get_current_user)
            from app.core.security import decode_token

            payload = decode_token(access_token)
            request.state.auth_payload = payload

            # Continue with the request if token is valid
            response = await call_next(request)
            return response

        except Exception as auth_error:
            logger.error(f"Invalid token for {request.url.path}: {str(auth_error)}")
            # Return 401 JSON response (API backend, no HTML redirect)
            return JSONResponse(
                {"error": "Unauthorized", "message": "Invalid or expired token"},
                status_code=401,
            )


def get_middleware() -> List[Middleware]:
    """
    Get the list of middleware for use in Starlette app initialization.

    Returns:
        List of Middleware instances
    """
    # Liste des origines autorisées pour CORS
    # IMPORTANT: Ne pas utiliser "*" quand credentials='include' est utilisé côté client
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Ajouter FRONTEND_URL + variantes www/non-www pour éviter OPTIONS 400
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if frontend_url:
        allowed_origins.append(frontend_url)
        # Si https://mathakine.fun, ajouter https://www.mathakine.fun et inversement
        try:
            from urllib.parse import urlparse

            parsed = urlparse(frontend_url)
            if (
                parsed.netloc
                and "." in parsed.netloc
                and not parsed.netloc.startswith("www.")
            ):
                allowed_origins.append(f"{parsed.scheme}://www.{parsed.netloc}")
            elif parsed.netloc.startswith("www."):
                allowed_origins.append(f"{parsed.scheme}://{parsed.netloc[4:]}")
        except Exception:
            pass
        # Fallback Render frontend si déployé sur Render
        if "mathakine" in frontend_url.lower() and "render.com" not in frontend_url:
            allowed_origins.append("https://mathakine-frontend.onrender.com")

    # Filtrer les chaînes vides et doublons
    allowed_origins = list(dict.fromkeys(o for o in allowed_origins if o))

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
            Middleware(AuthenticationMiddleware),
        ]
    )

    return middleware_list
