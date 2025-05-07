from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from loguru import logger

from app.core.config import settings
from app.db.init_db import create_tables

logger.info("Démarrage de l'application FastAPI")

app = FastAPI(
    title="Math Trainer API",
    description="API pour l'application d'entraînement mathématique",
    version="0.1.0",
    debug=settings.DEBUG
)

# Middleware de logging pour les requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log de la requête entrante
    logger.info(f"Requête entrante: {request.method} {request.url}")
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Log de la réponse avec le temps de traitement
    process_time = time.time() - start_time
    logger.info(f"Requête traitée: {request.method} {request.url} - Status: {response.status_code} - Temps: {process_time:.4f}s")
    
    return response

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Démarrage de l'événement de startup")
    # Création des tables au démarrage si nécessaire
    create_tables()
    logger.success("Application prête")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Arrêt de l'application")

@app.get("/")
async def root():
    logger.debug("Accès à la route racine")
    return {"message": "Bienvenue sur l'API Math Trainer"}

@app.get("/debug")
async def debug_info():
    """Endpoint pour vérifier l'état de l'application (utile pour le débogage)"""
    logger.debug("Accès aux informations de débogage")
    return {
        "app_name": settings.PROJECT_NAME,
        "debug_mode": settings.DEBUG,
        "database_url": settings.DATABASE_URL.replace("://", "://*****:*****@") if "://" in settings.DATABASE_URL else settings.DATABASE_URL,
        "api_version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Démarrage du serveur uvicorn")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 