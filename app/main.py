from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import time
import os
from loguru import logger
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.init_db import create_tables_with_test_data
from app.api.api import api_router

logger.info("Démarrage de l'application FastAPI")

# Définir les chemins pour les dossiers statiques et templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Créer les dossiers s'ils n'existent pas
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Configuration des templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    # Startup
    try:
        logger.info("Démarrage de l'événement de startup")
        # Création des tables au démarrage si nécessaire
        create_tables_with_test_data()
        logger.success("Application prête")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {str(e)}")
        raise
    
    yield  # L'application est en cours d'exécution
    
    # Shutdown
    logger.info("Arrêt de l'application")

app = FastAPI(
    title="Math Trainer API",
    description="API pour l'application d'entraînement mathématique",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.DEBUG else settings.ALLOWED_HOSTS
)

# Middleware de logging pour les requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        # Log de la requête entrante
        logger.info(f"Requête entrante: {request.method} {request.url}")
        
        # Traitement de la requête
        response = await call_next(request)
        
        # Log de la réponse avec le temps de traitement
        process_time = time.time() - start_time
        logger.info(f"Requête traitée: {request.method} {request.url} - Status: {response.status_code} - Temps: {process_time:.4f}s")
        
        return response
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter les fichiers statiques
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routes de base
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Essayez de servir la page d'accueil HTML si elle existe
    try:
        logger.debug("Tentative de servir le template HTML")
        return templates.TemplateResponse("home.html", {"request": request})
    except Exception as e:
        # Si le template n'existe pas, retourner la réponse JSON par défaut
        logger.debug(f"Erreur de template, retour à la réponse JSON: {str(e)}")
        return {"message": "Bienvenue sur l'API Math Trainer"}

@app.get("/exercises", response_class=HTMLResponse)
async def exercises_page(request: Request):
    try:
        return templates.TemplateResponse("exercises.html", {"request": request})
    except Exception as e:
        logger.error(f"Erreur lors du chargement du template exercises.html: {str(e)}")
        return {"error": "Page non disponible"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        logger.error(f"Erreur lors du chargement du template dashboard.html: {str(e)}")
        return {"error": "Page non disponible"}

@app.get("/debug")
async def debug_info():
    """Endpoint pour vérifier l'état de l'application (utile pour le débogage)"""
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Endpoint de debug désactivé en production")
    
    logger.debug("Accès aux informations de débogage")
    return {
        "app_name": settings.PROJECT_NAME,
        "debug_mode": settings.DEBUG,
        "database_url": settings.DATABASE_URL.replace("://", "://*****:*****@") if "://" in settings.DATABASE_URL else settings.DATABASE_URL,
        "api_version": "0.1.0",
        "static_dir": STATIC_DIR,
        "templates_dir": TEMPLATES_DIR
    }

@app.get("/api/info")
async def api_info():
    """Endpoint pour obtenir des informations sur l'API"""
    logger.debug("Accès aux informations de l'API")
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "description": "API pour l'application d'entraînement mathématique Star Wars"
    }

# Inclusion du routeur API
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    logger.info("Démarrage du serveur uvicorn")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 