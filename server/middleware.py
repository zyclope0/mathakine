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
            "/api/users/",
            "/static",
            "/exercises"  # On permet l'accès à la liste des exercices sans connexion
        ]
        
        # Check if the route is public
        if any(request.url.path.startswith(route) for route in public_routes):
            response = await call_next(request)
            return response
        
        # Check for authentication token
        access_token = request.cookies.get("access_token")
        if not access_token:
            logger.info(f"Unauthorized access attempt to {request.url.path}, redirecting to login")
            return RedirectResponse(url="/login", status_code=303)
            
        try:
            # Verify the token
            from app.core.security import decode_token
            payload = decode_token(access_token)
            
            # Continue with the request if token is valid
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Invalid token for {request.url.path}: {str(e)}")
            return RedirectResponse(url="/login", status_code=303)

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