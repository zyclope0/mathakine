"""
App initialization for Mathakine.

This module centralizes Starlette application creation and configuration.
It ties together routes, middleware, exception handlers, and other components.
"""
from starlette.applications import Starlette
import uvicorn
import os
from loguru import logger

from server.routes import get_routes
from server.middleware import get_middleware
from server.error_handlers import get_exception_handlers
from server.template_handler import get_templates
from server.database import init_database

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
        on_startup=[startup]
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
    init_database()
    
    # Appliquer automatiquement la migration pour la vérification d'email si nécessaire
    try:
        from scripts.apply_email_verification_migration import apply_migration
        logger.info("Vérification des colonnes de vérification email...")
        apply_migration()
    except Exception as e:
        logger.warning(f"Impossible d'appliquer la migration email automatiquement: {e}")
        logger.warning("Les colonnes de vérification email peuvent être manquantes. Utilisez le script manuel si nécessaire.")
    
    logger.info("Mathakine server started successfully")

def run_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """
    Run the Starlette server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Whether to enable debug mode
    """
    log_level = os.environ.get("MATH_TRAINER_LOG_LEVEL", "INFO").lower()
    
    logger.info(f"Starting Mathakine server on {host}:{port} (debug={debug})")
    
    uvicorn.run(
        "enhanced_server:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level
    ) 