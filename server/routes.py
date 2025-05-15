"""
Routes for Mathakine.

This module centralizes Starlette route definitions for better organization
and maintainability.
"""
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from typing import List

# Importer les fonctions de vues (pages HTML)
from server.views import (
    homepage,
    login_page,
    api_login,
    register_page,
    logout,
    exercises_page,
    dashboard,
    exercise_detail_page
)

# Importer les fonctions d'API
from server.api_routes import (
    get_exercises_list,
    get_exercise,
    delete_exercise,
    generate_exercise,
    submit_answer,
    get_user_stats
)

def get_routes() -> List:
    """
    Get the list of routes for use in Starlette app initialization.
    
    Returns:
        List of Route and Mount instances
    """
    return [
        # Main routes
        Route("/", endpoint=homepage),
        Route("/login", endpoint=login_page),
        Route("/api/auth/login", endpoint=api_login, methods=["POST"]),
        Route("/register", endpoint=register_page),
        Route("/logout", endpoint=logout),
        Route("/exercises", endpoint=exercises_page),
        Route("/dashboard", endpoint=dashboard),
        Route("/exercise/{exercise_id:int}", endpoint=exercise_detail_page),
        
        # API routes
        Route("/api/exercises", endpoint=get_exercises_list),
        Route("/api/exercises/{exercise_id:int}", endpoint=get_exercise, methods=["GET"]),
        Route("/api/exercises/{exercise_id:int}", endpoint=delete_exercise, methods=["DELETE"]),
        Route("/api/exercises/generate", endpoint=generate_exercise),
        Route("/api/submit-answer", endpoint=submit_answer, methods=["POST"]),
        Route("/api/users/stats", endpoint=get_user_stats),
        
        # Static files
        Mount("/static", app=StaticFiles(directory="static"), name="static")
    ] 