"""
Middleware for Mathakine.

This module centralizes Starlette middleware logic for consistent
request processing across the application.
"""
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from typing import List, Callable
from loguru import logger
import os

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
            "/api/auth/logout",  # Permet la déconnexion même sans token valide
            "/api/auth/forgot-password",
            "/api/auth/verify-email",
            "/api/auth/resend-verification",
            "/api/users/",
            "/api/exercises",  # API exercises (publique)
            "/api/challenges",  # API challenges (publique)
            "/static",
            "/exercises"  # On permet l'accès à la liste des exercices sans connexion
        ]
        
        # Check if the route is public
        is_public = any(request.url.path.startswith(route) for route in public_routes)
        
        if is_public:
            response = await call_next(request)
            return response
        
        # Check for authentication token
        access_token = request.cookies.get("access_token")
        if not access_token:
            logger.info(f"Unauthorized access attempt to {request.url.path}")
            # Return 401 JSON response (API backend, no HTML redirect)
            return JSONResponse(
                {"error": "Unauthorized", "message": "Authentication required"},
                status_code=401
            )
            
        try:
            # Verify the token
            from app.core.security import decode_token
            payload = decode_token(access_token)
            
            # Continue with the request if token is valid
            response = await call_next(request)
            return response
            
        except Exception as auth_error:
            logger.error(f"Invalid token for {request.url.path}: {str(auth_error)}")
            # Return 401 JSON response (API backend, no HTML redirect)
            return JSONResponse(
                {"error": "Unauthorized", "message": "Invalid or expired token"},
                status_code=401
            )

def get_middleware() -> List[Middleware]:
    """
    Get the list of middleware for use in Starlette app initialization.
    
    Returns:
        List of Middleware instances
    """
    # Liste des origines autorisées pour CORS
    # IMPORTANT: Ne pas utiliser "*" quand credentials='include' est utilisé côté client
    # Le navigateur bloque les requêtes avec credentials si Access-Control-Allow-Origin est "*"
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Ajouter FRONTEND_URL si définie
    frontend_url = os.getenv("FRONTEND_URL", "")
    if frontend_url:
        allowed_origins.append(frontend_url)
    
    # Filtrer les chaînes vides
    allowed_origins = [origin for origin in allowed_origins if origin]
    
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            allow_credentials=True,  # Important pour les cookies HTTP-only
        ),
        Middleware(AuthenticationMiddleware)
    ]
