"""
App initialization for Mathakine.

This module centralizes Starlette application creation and configuration.
It ties together routes, middleware, exception handlers, and other components.
"""

import os

import uvicorn

from app.core.logging_config import get_logger
from app.core.monitoring import init_monitoring

logger = get_logger(__name__)
from starlette.applications import Starlette

from server.database import init_database
from server.error_handlers import get_exception_handlers
from server.middleware import get_middleware
from server.routes import get_routes
from server.template_handler import get_templates


def create_app(debug: bool = False) -> Starlette:
    """
    Create and configure the Starlette application.

    Args:
        debug: Whether to enable debug mode

    Returns:
        Configured Starlette application
    """
    # Create the application
    app = Starlette(
        debug=debug,
        routes=get_routes(),
        middleware=get_middleware(),
        exception_handlers=get_exception_handlers(),
        on_startup=[startup],
    )

    # Store templates in application state for API routes
    app.state.templates = get_templates()

    return app


async def startup():
    """
    Startup event handler for the application.

    This function is called when the application starts.
    It initializes the database and performs other setup tasks.
    """
    logger.info("Starting up Mathakine server")
    init_monitoring()
    init_database()

    # Note: La migration email est désormais gérée via Alembic (migrations/versions/)
    # L'ancien script scripts/apply_email_verification_migration.py a été archivé dans _ARCHIVE_2026

    logger.info("Mathakine server started successfully")


def run_server(
    app: object | None = None,
    host: str = "0.0.0.0",
    port: int = 10000,
    debug: bool = False,
):
    """
    Run the Starlette server.

    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Whether to enable debug mode
    """
    import sys

    log_level = os.environ.get("MATH_TRAINER_LOG_LEVEL", "INFO").lower()

    # Windows : désactiver reload — le processus enfant réimporte tout et peut bloquer
    # (deadlock import connu). Le reload reste actif sur Unix.
    use_reload = debug and sys.platform != "win32"
    if debug and sys.platform == "win32":
        logger.info(
            "Reload désactivé sur Windows (évite blocage à l'import), "
            "redémarrer manuellement pour appliquer les changements"
        )

    logger.info(f"Starting Mathakine server on {host}:{port} (debug={debug})")

    uvicorn_app = (
        "enhanced_server:app"
        if use_reload
        else (app if app is not None else "enhanced_server:app")
    )

    uvicorn.run(
        uvicorn_app,
        host=host,
        port=port,
        reload=use_reload,
        log_level=log_level,
    )
