"""
Error handlers for Mathakine.

This module centralizes Starlette exception handling logic for a consistent
error management across the application.

Since the frontend is now Next.js, all error responses are JSON (no HTML templates).
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
import traceback
from loguru import logger

async def not_found(request: Request, exc: HTTPException):
    """
    Handle 404 Not Found errors.
    
    Args:
        request: The Starlette request object
        exc: The exception that was raised
        
    Returns:
        JSON error response
    """
    logger.warning(f"404 Not Found: {request.url.path}")
    return JSONResponse(
        {
            "error": "Not Found",
            "message": "The requested resource does not exist.",
            "path": str(request.url.path)
        },
        status_code=404
    )

async def server_error(request: Request, exc: Exception):
    """
    Handle 500 Server Error and other unexpected exceptions.
    
    Args:
        request: The Starlette request object
        exc: The exception that was raised
        
    Returns:
        JSON error response
    """
    # Log the error for debugging
    logger.error(f"500 Server Error for {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        {
            "error": "Internal Server Error",
            "message": "An internal server error occurred. Please try again later.",
            "path": str(request.url.path)
        },
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