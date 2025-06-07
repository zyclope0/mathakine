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
    about_page,
    login_page,
    api_login,
    register_page,
    forgot_password_page,
    profile_page,
    logout,
    exercises_page,
    dashboard,
    exercise_detail_page,
    redirect_old_exercise_url,
    badges_page
)

# Importer les vues pour exercices simples
from server.simple_views import (
    simple_exercises_page,
    generate_simple_exercise,
    simple_exercise_page
)

# Importer les fonctions d'API
from server.api_routes import (
    get_exercises_list,
    delete_exercise,
    handle_recommendation_complete,
    api_forgot_password
)

from server.handlers.exercise_handlers import generate_exercise, get_exercise, submit_answer, generate_exercise_api
from server.handlers.user_handlers import get_user_stats
from server.handlers.badge_handlers import get_user_badges, get_available_badges, check_user_badges, get_user_gamification_stats

# Importer les fonctions API pour les challenges
from server.api_challenges import (
    api_start_challenge, 
    api_get_challenge_progress, 
    api_get_challenge_rewards,
    api_get_users_leaderboard, 
    api_get_user_badges_progress
)
from server.api_challenges import (
    api_start_challenge, api_get_challenge_progress, api_get_challenge_rewards,
    api_get_users_leaderboard, api_get_user_badges_progress
)

# Import des handlers pour logic challenges et système hybride  
from server.handlers.logic_challenge_handlers import (
    logic_challenge_page, hybrid_mission_page, submit_logic_challenge_answer
)
from server.handlers.hybrid_challenge_handlers import (
    hybrid_challenges_page, api_hybrid_start_challenge
)

# Import handlers pour logic challenges et système hybride
from server.handlers.logic_challenge_handlers import (
    logic_challenge_page, hybrid_mission_page, submit_logic_challenge_answer
)
from server.handlers.hybrid_challenge_handlers import (
    hybrid_challenges_page, api_hybrid_start_challenge
)

# Fonctions temporaires pour exercices simples
async def simple_exercises_page_temp(request):
    """Page temporaire des exercices simples"""
    from server.views import get_current_user, render_template, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        return render_template("exercises.html", request, {
            "exercises": [],
            "exercise_types": ['ADDITION', 'SOUSTRACTION', 'DIVISION'],
            "difficulty_levels": ['INITIE', 'PADAWAN'],
            "exercise_type_display": {'ADDITION': 'Addition', 'SOUSTRACTION': 'Soustraction', 'DIVISION': 'Division'},
            "difficulty_display": {'INITIE': 'Initié', 'PADAWAN': 'Padawan'},
            "current_user": current_user,
            "page_title": "Exercices Simples",
            "is_simple_mode": True
        })
    except Exception as e:
        return render_error(
            request=request,
            error="Page en construction",
            message="La page des exercices simples est en cours de développement.",
            status_code=503
        )

async def generate_simple_exercise_temp(request):
    """Génération temporaire d'exercice simple"""
    from starlette.responses import RedirectResponse
    return RedirectResponse(url="/api/exercises/generate", status_code=302)

async def simple_exercise_page_temp(request):
    """Page temporaire d'exercice simple"""
    from starlette.responses import RedirectResponse
    exercise_id = request.path_params["exercise_id"]
    return RedirectResponse(url=f"/exercise/{exercise_id}", status_code=302)

# Vues temporaires pour les nouvelles pages
async def new_exercise_temp(request):
    """Page de création d'exercice temporaire"""
    from server.views import get_current_user, render_template, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        return render_template("new_exercise.html", request, {
            "current_user": current_user
        })
    except Exception as e:
        return render_error(
            request=request,
            error="Page en construction",
            message="La page de création d'exercice sera bientôt disponible.",
            status_code=503
        )

async def challenges_temp(request):
    """Page des défis connectée au backend logic_challenge"""
    from server.views import get_current_user, render_template, render_error
    from starlette.responses import RedirectResponse
    from app.services.enhanced_server_adapter import EnhancedServerAdapter
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        # Connecter aux vrais défis logiques du backend
        adapter = EnhancedServerAdapter()
        
        # Récupérer les défis depuis la base de données
        try:
            logic_challenges = adapter.get_logic_challenges(limit=8)
        except Exception as db_error:
            print(f"Erreur connexion DB logic_challenges: {db_error}")
            logic_challenges = []
        
        # Convertir en format pour le template Star Wars
        challenges = []
        for idx, challenge in enumerate(logic_challenges):
            # Mapping des difficultés
            difficulty_map = {
                "GROUP_10_12": "initie",
                "GROUP_13_15": "padawan",
                "AGE_9_12": "initie",
                "AGE_13_16": "chevalier"
            }
            
            # Mapping des catégories avec thème Star Wars
            category_map = {
                "SEQUENCE": "hyperespace",
                "PATTERN": "reconnaissance", 
                "PUZZLE": "strategie",
                "VISUAL": "navigation",
                "DEDUCTION": "enquete",
                "SPATIAL": "architecture"
            }
            
            difficulty = difficulty_map.get(challenge.get("age_group", ""), "padawan")
            category = category_map.get(challenge.get("challenge_type", ""), "logique")
            
            challenges.append({
                "id": challenge.get("id", idx + 1),
                "title": challenge.get("title", "Défi Mystère"),
                "description": challenge.get("description", "Un défi passionnant vous attend..."),
                "difficulty": difficulty,
                "category": category,
                "points": int(50 + (challenge.get("difficulty_rating", 2.0) * 25)),
                "attempts": 0,
                "is_completed": False,
                "is_new": True,
                "status": "available",
                "time_limit": challenge.get("estimated_time_minutes", 15),
                "success_rate": challenge.get("success_rate", 0.75)
            })
        
        # Si aucun défi en base, utiliser des exemples Star Wars cohérents
        if not challenges:
            challenges = [
                {
                    "id": 1,
                    "title": "Séquence de l'Hyperespace",
                    "description": "Calculez les coordonnées pour le saut vers Alderaan : 2, 4, 8, 16, ...",
                    "difficulty": "padawan",
                    "category": "hyperespace",
                    "points": 100,
                    "attempts": 0,
                    "is_completed": False,
                    "is_new": True,
                    "status": "available",
                    "time_limit": 10
                },
                {
                    "id": 2,
                    "title": "Reconnaissance Rebelle",
                    "description": "Analysez les patterns de patrouilles impériales",
                    "difficulty": "chevalier",
                    "category": "reconnaissance",
                    "points": 150,
                    "attempts": 0,
                    "is_completed": False,
                    "is_new": True,
                    "status": "available",
                    "time_limit": 15
                },
                {
                    "id": 3,
                    "title": "Architecture de l'Étoile Noire",
                    "description": "Trouvez la faiblesse dans les plans secrets",
                    "difficulty": "maitre",
                    "category": "architecture",
                    "points": 250,
                    "attempts": 0,
                    "is_completed": False,
                    "is_new": True,
                    "status": "available",
                    "time_limit": 20
                }
            ]
        
        return render_template("challenges-hybrid.html", request, {
            "current_user": current_user,
            "challenges": challenges,
            "total_challenges": len(challenges),
            "weekly_challenge": {
                "id": 999,
                "title": "Mission Alderaan",
                "description": "La princesse Leia a besoin de votre aide pour calculer les coordonnées hyperespace vers Alderaan ! Résolvez 20 exercices de géométrie.",
                "progress": 35,
                "progress_text": "7/20 exercices terminés",
                "time_remaining": "4j 12h 33m",
                "reward_points": 250
            }
        })
        
    except Exception as e:
        print(f"Erreur dans challenges_temp: {e}")
        # Fallback avec données statiques
        return render_template("challenges-hybrid.html", request, {
            "current_user": current_user,
            "challenges": [
                {
                    "id": 1,
                    "title": "Mission de Reconnaissance",
                    "description": "Analysez les données de la Rébellion",
                    "difficulty": "initie",
                    "category": "logique",
                    "points": 75,
                    "attempts": 0,
                    "is_completed": False,
                    "is_new": True,
                    "status": "available"
                }
            ],
            "total_challenges": 1,
            "error_mode": True
        })

async def control_center_temp(request):
    """Centre de contrôle temporaire"""
    from server.views import get_current_user, render_template, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        return render_template("control-center.html", request, {
            "current_user": current_user,
            "user_stats": {}
        })
    except Exception as e:
        return render_error(
            request=request,
            error="Page en construction",
            message="Le centre de contrôle sera bientôt disponible.",
            status_code=503
        )

async def settings_temp(request):
    """Page des paramètres temporaire"""
    from server.views import get_current_user, render_template, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        user_settings = {
            "theme": "star-wars",
            "accessibility_settings": {},
            "learning_style": "standard",
            "preferred_difficulty": "padawan"
        }
        
        return render_template("settings.html", request, {
            "current_user": current_user,
            "user_settings": user_settings
        })
    except Exception as e:
        return render_error(
            request=request,
            error="Page en construction",
            message="La page des paramètres sera bientôt disponible.",
            status_code=503
        )

# === SYSTÈME HYBRIDE DE CHALLENGES - FONCTIONS TEMPORAIRES ===

async def hybrid_challenges_page_temp(request):
    """Page des challenges hybrides - version temporaire"""
    from server.views import get_current_user
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        from server.handlers.hybrid_challenge_handlers import hybrid_challenges_page
        return await hybrid_challenges_page(request)
    except ImportError:
        # Fallback vers challenges normaux
        return RedirectResponse(url="/challenges", status_code=302)

async def logic_challenge_page_temp(request):
    """Page d'un logic challenge spécifique - version temporaire"""
    from server.views import get_current_user, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        from server.handlers.logic_challenge_handlers import logic_challenge_page
        return await logic_challenge_page(request)
    except ImportError:
        challenge_id = request.path_params["challenge_id"]
        return render_error(
            request=request,
            error="Logic Challenge en construction",
            message=f"Le défi logique #{challenge_id} sera bientôt disponible ! 🧩",
            status_code=503
        )

async def hybrid_mission_page_temp(request):
    """Page d'une mission hybride - version temporaire"""
    from server.views import get_current_user, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        from server.handlers.logic_challenge_handlers import hybrid_mission_page
        return await hybrid_mission_page(request)
    except ImportError:
        mission_id = int(request.path_params["mission_id"])
        
        if mission_id == 999:
            # Mission Alderaan - rediriger vers exercices géométrie
            return RedirectResponse(url="/exercises?exercise_type=geometrie&difficulty=chevalier", status_code=302)
        
        return render_error(
            request=request,
            error="Mission Hybride en construction",
            message=f"La mission #{mission_id} sera bientôt disponible ! ⚔️",
            status_code=503
        )

async def api_hybrid_start_challenge_temp(request):
    """API pour démarrer un challenge hybride - version temporaire"""
    from starlette.responses import JSONResponse
    
    try:
        from server.handlers.hybrid_challenge_handlers import api_hybrid_start_challenge
        return await api_hybrid_start_challenge(request)
    except ImportError:
        challenge_id = int(request.path_params["challenge_id"])
        
        # Mapping temporaire
        redirect_map = {
            1: "/exercises?exercise_type=addition&difficulty=initie",
            2: "/exercises?exercise_type=multiplication&difficulty=padawan",
            3: "/exercises?exercise_type=fractions&difficulty=chevalier", 
            4: "/exercises?exercise_type=geometrie&difficulty=maitre",
            100: "/logic-challenge/2270",
            101: "/logic-challenge/2271", 
            102: "/logic-challenge/2275",
            999: "/hybrid-mission/999"
        }
        
        redirect_url = redirect_map.get(challenge_id, "/challenges")
        
        return JSONResponse({
            "success": True,
            "message": f"Challenge #{challenge_id} démarré !",
            "redirect_url": redirect_url
        })

async def submit_logic_challenge_answer_temp(request):
    """Soumettre une réponse à un logic challenge - version temporaire"""
    from starlette.responses import JSONResponse
    
    try:
        from server.handlers.logic_challenge_handlers import submit_logic_challenge_answer
        return await submit_logic_challenge_answer(request)
    except ImportError:
        return JSONResponse({
            "success": False,
            "error": "Non implémenté",
            "message": "La soumission de réponses sera bientôt disponible !"
        }, status_code=503)

# === SYSTÈME HYBRIDE DE CHALLENGES - FONCTIONS TEMPORAIRES ===

async def hybrid_challenges_page_temp(request):
    """Page des challenges hybrides - version temporaire"""
    from server.views import get_current_user, render_template
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        return render_template("challenges-hybrid.html", request, {
            "current_user": current_user,
            "page_title": "Défis Galactiques Hybrides"
        })
    except Exception:
        # Fallback vers challenges normaux
        return RedirectResponse(url="/challenges", status_code=302)

async def logic_challenge_page_temp(request):
    """Page d'un logic challenge spécifique - version temporaire"""
    from server.views import get_current_user, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    challenge_id = request.path_params["challenge_id"]
    
    return render_error(
        request=request,
        error="Logic Challenge en construction",
        message=f"Le défi logique #{challenge_id} sera bientôt disponible ! 🧩",
        status_code=503
    )

async def hybrid_mission_page_temp(request):
    """Page d'une mission hybride - version temporaire"""
    from server.views import get_current_user, render_error
    from starlette.responses import RedirectResponse
    
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    mission_id = request.path_params["mission_id"]
    
    if mission_id == 999:
        # Mission Alderaan - rediriger vers exercices géométrie
        return RedirectResponse(url="/exercises?exercise_type=geometrie&difficulty=chevalier", status_code=302)
    
    return render_error(
        request=request,
        error="Mission Hybride en construction",
        message=f"La mission #{mission_id} sera bientôt disponible ! ⚔️",
        status_code=503
    )

async def api_hybrid_start_challenge_temp(request):
    """API pour démarrer un challenge hybride - version temporaire"""
    from starlette.responses import JSONResponse
    
    challenge_id = int(request.path_params["challenge_id"])
    
    # Mapping temporaire
    redirect_map = {
        1: "/exercises?exercise_type=addition&difficulty=initie",
        2: "/exercises?exercise_type=multiplication&difficulty=padawan",
        3: "/exercises?exercise_type=fractions&difficulty=chevalier", 
        4: "/exercises?exercise_type=geometrie&difficulty=maitre",
        100: "/logic-challenge/2270",
        101: "/logic-challenge/2271", 
        102: "/logic-challenge/2275",
        999: "/hybrid-mission/999"
    }
    
    redirect_url = redirect_map.get(challenge_id, "/challenges")
    
    return JSONResponse({
        "success": True,
        "message": f"Challenge #{challenge_id} démarré !",
        "redirect_url": redirect_url
    })

async def submit_logic_challenge_answer_temp(request):
    """Soumettre une réponse à un logic challenge - version temporaire"""
    from starlette.responses import JSONResponse
    
    return JSONResponse({
        "success": False,
        "error": "Non implémenté",
        "message": "La soumission de réponses sera bientôt disponible !"
    }, status_code=503)

def get_routes() -> List:
    """
    Get the list of routes for use in Starlette app initialization.
    
    Returns:
        List of Route and Mount instances
    """
    return [
        # Main routes
        Route("/", endpoint=homepage),
        Route("/about", endpoint=about_page),
        Route("/login", endpoint=login_page),
        Route("/api/auth/login", endpoint=api_login, methods=["POST"]),
        Route("/register", endpoint=register_page),
        Route("/forgot-password", endpoint=forgot_password_page),
        Route("/profile", endpoint=profile_page),
        Route("/logout", endpoint=logout),
        Route("/exercises", endpoint=exercises_page, name="exercises"),
        Route("/exercises/simple", endpoint=simple_exercises_page),
        Route("/exercises/simple/generate", endpoint=generate_simple_exercise),
        Route("/exercise/simple/{exercise_id:int}", endpoint=simple_exercise_page),
        Route("/dashboard", endpoint=dashboard),
        Route("/badges", endpoint=badges_page),
        
        # Nouvelles pages intégrées
        Route("/new-exercise", endpoint=new_exercise_temp, methods=["GET", "POST"]),
        Route("/challenges", endpoint=challenges_temp),
        Route("/control-center", endpoint=control_center_temp),
        Route("/settings", endpoint=settings_temp),
        
        Route("/exercise/{exercise_id:int}", endpoint=exercise_detail_page),
        Route("/exercises/{exercise_id:int}", endpoint=redirect_old_exercise_url),
        
        # API routes
        Route("/api/exercises", endpoint=get_exercises_list),
        Route("/api/exercises/{exercise_id:int}", endpoint=get_exercise, methods=["GET"]),
        Route("/api/exercises/{exercise_id:int}", endpoint=delete_exercise, methods=["DELETE"]),
        Route("/api/exercises/generate", endpoint=generate_exercise, methods=["GET"]),
        Route("/api/exercises/generate", endpoint=generate_exercise_api, methods=["POST"]),
        Route("/api/submit-answer", endpoint=submit_answer, methods=["POST"]),
        Route("/api/users/stats", endpoint=get_user_stats),
        Route("/api/badges/user", endpoint=get_user_badges),
        Route("/api/badges/available", endpoint=get_available_badges),
        Route("/api/badges/check", endpoint=check_user_badges, methods=["POST"]),
        Route("/api/badges/stats", endpoint=get_user_gamification_stats),
        Route("/api/recommendations/complete", endpoint=handle_recommendation_complete, methods=["POST"]),
        Route("/api/auth/forgot-password", endpoint=api_forgot_password, methods=["POST"]),
        
        # API routes pour les challenges
        Route("/api/challenges/start/{challenge_id:int}", endpoint=api_start_challenge, methods=["POST"]),
        Route("/api/challenges/progress/{challenge_id:int}", endpoint=api_get_challenge_progress),
        Route("/api/challenges/rewards/{challenge_id:int}", endpoint=api_get_challenge_rewards),
        Route("/api/users/leaderboard", endpoint=api_get_users_leaderboard),
        Route("/api/challenges/badges/progress", endpoint=api_get_user_badges_progress),
        
        # Routes pour le système hybride de challenges (NOUVEAU !)
        Route("/challenges-hybrid", endpoint=hybrid_challenges_page_temp),
        Route("/logic-challenge/{challenge_id:int}", endpoint=logic_challenge_page_temp),
        Route("/hybrid-mission/{mission_id:int}", endpoint=hybrid_mission_page_temp),
        
        # Static files
        Mount("/static", app=StaticFiles(directory="static"), name="static")
    ] 