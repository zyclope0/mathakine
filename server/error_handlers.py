"""
Error handlers for Mathakine.

This module centralizes Starlette exception handling logic for a consistent
error management across the application.

Since the frontend is now Next.js, all error responses are JSON (no HTML templates).
Utilise le schéma d'erreur unifié (app.utils.error_handler.api_error_response).
"""

import traceback
import uuid

from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.core.logging_config import get_logger
from app.utils.error_handler import api_error_response

logger = get_logger(__name__)


async def not_found(request: Request, exc: HTTPException):
    """
    Handle 404 Not Found errors.
    """
    logger.warning(f"404 Not Found: {request.url.path}")
    return api_error_response(
        404,
        "The requested resource does not exist.",
        path=str(request.url.path),
    )


async def server_error(request: Request, exc: Exception):
    """
    Handle 500 Server Error and other unexpected exceptions.
    """
    trace_id = str(uuid.uuid4())[:8]
    logger.error(f"500 Server Error for {request.url.path} [trace_id={trace_id}]: {exc}")
    logger.error(traceback.format_exc())

    return api_error_response(
        500,
        "An internal server error occurred. Please try again later.",
        path=str(request.url.path),
        trace_id=trace_id,
    )


def get_exception_handlers():
    """
    Get a dictionary of exception handlers for use in Starlette app initialization.

    Returns:
        Dict mapping exception types to handler functions
    """
    return {
        404: not_found,
        500: server_error,
        Exception: server_error,  # Catch all other exceptions
    }
