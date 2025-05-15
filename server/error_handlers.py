"""
Error handlers for Mathakine.

This module centralizes Starlette exception handling logic for a consistent
error management across the application.
"""
from starlette.requests import Request
from starlette.exceptions import HTTPException
import traceback
from loguru import logger

from server.template_handler import render_error

async def not_found(request: Request, exc: HTTPException):
    """
    Handle 404 Not Found errors.
    
    Args:
        request: The Starlette request object
        exc: The exception that was raised
        
    Returns:
        Rendered error template
    """
    logger.warning(f"404 Not Found: {request.url.path}")
    return render_error(
        request=request,
        error="Page not found",
        message="The page you are looking for does not exist or has been moved.",
        status_code=404
    )

async def server_error(request: Request, exc: Exception):
    """
    Handle 500 Server Error and other unexpected exceptions.
    
    Args:
        request: The Starlette request object
        exc: The exception that was raised
        
    Returns:
        Rendered error template
    """
    # Log the error for debugging
    logger.error(f"500 Server Error for {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return render_error(
        request=request,
        error="Server Error",
        message="An internal server error occurred. Please try again later.",
        status_code=500
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
        Exception: server_error  # Catch all other exceptions
    } 