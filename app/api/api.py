"""
API principale regroupant tous les routeurs
"""
from fastapi import APIRouter

from app.api.endpoints import users, exercises, challenges, auth, recommendations

api_router = APIRouter()

# Ajouter les différents routeurs avec leurs préfixes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])

# Ajouter d'autres routeurs selon les besoins
