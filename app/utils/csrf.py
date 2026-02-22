"""
Protection CSRF pour les actions sensibles (audit 3.2).

Pattern double-submit : le backend génère un token, le met en cookie
et le retourne. Le client renvoie le token dans le header X-CSRF-Token.
Un attaquant cross-site ne peut pas lire le cookie ni forger le header.
"""

import os
import secrets

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def get_csrf_token_from_request(request: Request) -> str | None:
    """Récupère le token CSRF depuis le cookie de la requête."""
    return request.cookies.get("csrf_token")


def validate_csrf_token(request: Request) -> JSONResponse | None:
    """
    Valide que le header X-CSRF-Token correspond au cookie csrf_token.
    Retourne None si valide, sinon une JSONResponse d'erreur 403.
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return None  # Skip en mode test

    cookie_token = get_csrf_token_from_request(request)
    header_token = request.headers.get("X-CSRF-Token", "").strip()

    if not cookie_token or not header_token:
        logger.warning("CSRF: token manquant (cookie ou header)")
        return JSONResponse(
            {"error": "Token CSRF manquant. Rafraîchissez la page et réessayez."},
            status_code=403,
        )

    if not secrets.compare_digest(cookie_token, header_token):
        logger.warning("CSRF: token invalide ou expiré")
        return JSONResponse(
            {"error": "Token CSRF invalide. Rafraîchissez la page et réessayez."},
            status_code=403,
        )

    return None
