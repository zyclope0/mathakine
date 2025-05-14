from fastapi import FastAPI, Request, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
import time
import os
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.init_db import create_tables_with_test_data
from app.api.api import api_router
from app.models.exercise import ExerciseType, DifficultyLevel

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

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

# Définition des tags pour la documentation OpenAPI
api_tags_metadata = [
    {
        "name": "users",
        "description": "Opérations liées aux utilisateurs et à leur progression",
    },
    {
        "name": "exercises",
        "description": "Gestion des exercices mathématiques de base",
    },
    {
        "name": "challenges",
        "description": "Défis logiques avancés (Épreuves du Conseil Jedi)",
    },
    {
        "name": "auth",
        "description": "Authentification et gestion des sessions",
    },
]

app = FastAPI(
    title="Mathakine API",
    description="""
    API pour l'application éducative Mathakine (anciennement Math Trainer).
    
    Cette API permet de gérer:
    * Les exercices mathématiques pour enfants avec thématique Star Wars
    * Les défis logiques avancés pour les 10-15 ans
    * Les comptes utilisateurs et leur progression
    * L'authentification et les autorisations
    
    Pour accéder aux ressources protégées, utilisez l'authentification JWT avec le préfixe "Bearer".
    """,
    version="1.0.0",
    terms_of_service="https://mathakine.example.com/terms/",
    contact={
        "name": "Équipe de développement Mathakine",
        "email": "dev@mathakine.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=api_tags_metadata,
    openapi_url="/api/openapi.json",
    docs_url=None,
    redoc_url=None,
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

# Inclure le routeur API avec le préfixe
app.include_router(api_router, prefix="/api")

# Routes de documentation OpenAPI personnalisées
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    """Endpoint pour accéder à la documentation Swagger UI personnalisée"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentation API",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

@app.get("/api/redoc", include_in_schema=False)
async def redoc_html(request: Request):
    """Endpoint pour accéder à la documentation ReDoc"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentation API (ReDoc)",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        with_google_fonts=True
    )

# Routes de base
@app.get("/")
async def root():
    # Retourner un JSON simple pour compatibilité avec les tests
    return {"message": "Bienvenue sur l'API Mathakine", "docs": "/api/docs"}

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
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

@app.get("/exercise/{exercise_id}", response_class=HTMLResponse)
async def exercise_page(request: Request, exercise_id: int):
    try:
        # Ici, vous pourriez récupérer les détails de l'exercice depuis l'API
        return templates.TemplateResponse("exercise.html", {
            "request": request,
            "exercise_id": exercise_id
        })
    except Exception as e:
        logger.error(f"Erreur lors du chargement du template exercise.html: {str(e)}")
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

@app.get("/api/v1/exercises/generate")
async def redirect_to_api_v1_generate():
    """Redirige les anciennes URLs vers la nouvelle version de l'API"""
    return RedirectResponse(url="/api/exercises/generate")

@app.get("/api/info")
async def api_info():
    """Endpoint pour obtenir des informations sur l'API"""
    logger.debug("Accès aux informations de l'API")
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "description": "API pour l'application d'entraînement mathématique Star Wars"
    }

@app.get("/api/exercises/generate")
async def direct_generate_exercise(
    request: Request,
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    use_ai: Optional[bool] = Query(False)
):
    """
    Endpoint direct pour la génération d'exercices compatible avec les liens de l'interface.
    Cette fonction implémente la logique de génération d'exercice directement.
    """
    import random
    from datetime import datetime
    from app.api.deps import get_db_session
    from app.models.exercise import Exercise as ExerciseModel, ExerciseType, DifficultyLevel

    # Obtenir une session de base de données
    db = next(get_db_session())

    try:
        # Conversion des types - s'assurer que nous utilisons les valeurs valides de l'énumération
        if exercise_type:
            # Conversion en minuscule pour correspondre aux valeurs de l'énumération
            exercise_type_lower = exercise_type.lower()
            # Vérifier si c'est une valeur valide
            valid_types = [t.value for t in ExerciseType]
            if exercise_type_lower in valid_types:
                selected_type = exercise_type_lower
            else:
                selected_type = random.choice(valid_types)
        else:
            selected_type = random.choice([t.value for t in ExerciseType])

        # Même chose pour la difficulté
        if difficulty:
            difficulty_lower = difficulty.lower()
            valid_difficulties = [d.value for d in DifficultyLevel]
            if difficulty_lower in valid_difficulties:
                selected_difficulty = difficulty_lower
            else:
                selected_difficulty = random.choice(valid_difficulties)
        else:
            selected_difficulty = random.choice([d.value for d in DifficultyLevel])

        logger.info(f"Génération d'un exercice: type={selected_type}, difficulté={selected_difficulty}, IA={use_ai}")

        # Génération simple d'un exercice d'addition
        if selected_type == ExerciseType.ADDITION.value or selected_type == "addition":
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            result = num1 + num2
            question = f"Combien font {num1} + {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(result+2)]
            random.shuffle(choices)
            explanation = f"{num1} + {num2} = {result}"
            title = f"Exercice d'addition"
        else:
            # Pour les autres types, on fait une addition par défaut
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            result = num1 + num2
            question = f"Combien font {num1} + {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(result+2)]
            random.shuffle(choices)
            explanation = f"{num1} + {num2} = {result}"
            title = f"Exercice de {selected_type}"

        # Créer l'exercice
        new_exercise = ExerciseModel(
            title=title,
            exercise_type=selected_type,
            difficulty=selected_difficulty,
            question=question,
            correct_answer=correct_answer,
            choices=choices,
            explanation=explanation,
            hint="Résolvez le calcul étape par étape",
            is_active=True,
            is_archived=False,
            view_count=0,
            creator_id=1,  # Admin ou système
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Ajouter et sauvegarder dans la base de données
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        logger.success(f"Exercice {new_exercise.id} créé avec succès")

        # Rediriger vers la page des exercices
        return RedirectResponse(url="/exercises?generated=true", status_code=303)

    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la génération d'exercice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération d'exercice: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import sys
    import os

    logger.info("Démarrage du serveur")

    # En environnement de développement, lancer l'interface complète par défaut
    if settings.DEBUG and os.environ.get("MATH_TRAINER_PROFILE", "dev") == "dev":
        try:
            logger.info("Lancement de l'interface graphique complète (mode développement)")
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import enhanced_server
            enhanced_server.main()
        except ImportError as e:
            logger.error(f"Erreur lors du chargement de l'interface graphique: {e}")
            logger.warning("Retour à l'API standard")
            uvicorn.run("app.main:app", host="0.0.0.0", port=8081, reload=True)
    else:
        # En production, lancer l'API standard
        uvicorn.run("app.main:app", host="0.0.0.0", port=8081, reload=True)
