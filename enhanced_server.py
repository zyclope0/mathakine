"""
Point d'entrée principal du backend Mathakine (Math Trainer).

Lance l'application Starlette unifiée (server/app.py) avec toutes les routes API,
le middleware d'auth, SSE streaming IA, etc. FastAPI a été archivé (06/02/2026).

Usage:
    # Local / dev
    python enhanced_server.py

    # Production ASGI entrypoint
    gunicorn enhanced_server:app --worker-class uvicorn.workers.UvicornWorker
"""

import os

from dotenv import load_dotenv
from loguru import logger

# Charger les variables d'environnement (ignorer .env en prod - sécurité)
if os.environ.get("ENVIRONMENT") != "production":
    load_dotenv(override=False)

# Import from our server module
# Configuration from environment variables
# Port dev Mathakine : 10000 (cohérent avec NEXT_PUBLIC_API_* / .env.example)
PORT = int(os.environ.get("PORT", 10000))
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "false").lower() == "true"
HOST = os.environ.get("MATH_TRAINER_HOST", "0.0.0.0")

_app_instance = None


def get_app():
    """Construit l'application Starlette à la demande."""
    global _app_instance
    if _app_instance is None:
        from server.app import create_app

        _app_instance = create_app(debug=DEBUG)
    return _app_instance


# Expose a concrete Starlette instance for ASGI servers.
# Uvicorn/Gunicorn integration is more robust with a standard app object
# than with a custom lazy proxy exposing __call__.
app = get_app()


def main():
    """Point d'entrée pratique pour le développement/local."""
    from server.app import run_server

    print("========================================")
    print(f"ENHANCED_SERVER.PY - Serveur complet démarré sur le port {PORT}")
    print("Serveur avec interface graphique complète")
    print("========================================")
    run_server(app=app, host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":
    main()
