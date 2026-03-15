"""
Point d'entrée principal du backend Mathakine (Math Trainer).

Lance l'application Starlette unifiée (server/app.py) avec toutes les routes API,
le middleware d'auth, SSE streaming IA, etc. FastAPI a été archivé (06/02/2026).

Usage:
    python enhanced_server.py
"""

import os
from typing import Any

from dotenv import load_dotenv
from loguru import logger

# Charger les variables d'environnement (ignorer .env en prod - sécurité)
if os.environ.get("ENVIRONMENT") != "production":
    load_dotenv(override=False)

# Import from our server module
# Configuration from environment variables
PORT = int(os.environ.get("PORT", 8000))
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"
HOST = os.environ.get("MATH_TRAINER_HOST", "0.0.0.0")

_app_instance = None


def get_app():
    """Construit l'application Starlette à la demande."""
    global _app_instance
    if _app_instance is None:
        from server.app import create_app

        _app_instance = create_app(debug=DEBUG)
    return _app_instance


class LazyStarletteApp:
    """
    Proxy ASGI paresseux.

    Evite l'initialisation lourde au simple import de `enhanced_server`
    tout en restant compatible avec httpx/uvicorn qui attendent une app ASGI.
    """

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        await get_app()(scope, receive, send)

    def __getattr__(self, name: str) -> Any:
        return getattr(get_app(), name)


# Exposé pour les tests et les usages ASGI externes.
app = LazyStarletteApp()


def main():
    """Point d'entrée principal pour le serveur"""
    from server.app import run_server

    print("========================================")
    print(f"ENHANCED_SERVER.PY - Serveur complet démarré sur le port {PORT}")
    print("Serveur avec interface graphique complète")
    print("========================================")
    run_server(app=get_app(), host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":
    main()
