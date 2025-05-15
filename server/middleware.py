"""
Middleware for Mathakine.

This module centralizes Starlette middleware logic for consistent
request processing across the application.
"""
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing import List, Callable
from loguru import logger

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authenticating users.
    
    This middleware checks for authentication tokens in cookies and
    redirects unauthenticated users for protected routes.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process the request through the middleware.
        
        Args:
            request: The Starlette request object
            call_next: The next middleware or route handler
            
        Returns:
            Starlette Response
        """
        # List of routes that don't require authentication
        public_routes = [
            "/", 
            "/login", 
            "/register", 
            "/api/auth/login", 
            "/api/users/"
        ]
        
        # Check if the route is public or a static file
        if request.url.path in public_routes or request.url.path.startswith("/static/"):
            response = await call_next(request)
            return response
        
        # Check for authentication token
        token = request.cookies.get("token")
        if not token:
            logger.info(f"Unauthorized access attempt to {request.url.path}, redirecting to login")
            return RedirectResponse(url="/login", status_code=303)
        
        # Continue with the request
        response = await call_next(request)
        return response

def get_middleware() -> List[Middleware]:
    """
    Get the list of middleware for use in Starlette app initialization.
    
    Returns:
        List of Middleware instances
    """
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(AuthenticationMiddleware)
    ] 