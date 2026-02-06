"""
Vues pour les exercices simples de Mathakine - Version simplifiée
"""
import traceback

from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.constants import DISPLAY_NAMES
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.views import get_current_user, render_error, render_template


# Page des exercices simples
async def simple_exercises_page(request: Request):
    """Rendu de la page des exercices simples avec filtrage sur les types basiques"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Récupérer les paramètres de filtrage (s'ils sont fournis)
    exercise_type = request.query_params.get('exercise_type', None)
    difficulty = request.query_params.get('difficulty', None)
    
    print(f"Page exercices simples - Paramètres reçus - exercise_type: {exercise_type}, difficulty: {difficulty}")
    
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Si aucun filtre spécifique, charger tous les exercices simples par défaut
            # Sinon, utiliser les filtres fournis
            exercises = EnhancedServerAdapter.list_exercises(
                db,
                exercise_type=exercise_type,
                difficulty=difficulty
            )
            
            # Filtrer pour ne garder que les types simples si aucun type spécifique demandé
            if not exercise_type:
                simple_types = ['ADDITION', 'SOUSTRACTION', 'DIVISION']
                exercises = [ex for ex in exercises if ex.get('exercise_type') in simple_types]
            
            print(f"Nombre d'exercices simples récupérés: {len(exercises)}")
            if len(exercises) > 0:
                print(f"Premier exercice: ID={exercises[0].get('id')}, Titre={exercises[0].get('title')}")
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors de la récupération des exercices simples: {e}")
        traceback.print_exc()
        exercises = []
        
        return render_template("exercises.html", request, {
            "exercises": exercises,
            "exercise_types": {
                'ADDITION': 'Addition',
                'SOUSTRACTION': 'Soustraction', 
                'DIVISION': 'Division'
            },
            "difficulty_levels": {
                'INITIE': 'Initié',
                'PADAWAN': 'Padawan'
            },
            "exercise_type_display": {
                'ADDITION': 'Addition',
                'SOUSTRACTION': 'Soustraction', 
                'DIVISION': 'Division'
            },
            "difficulty_display": {
                'INITIE': 'Initié',
                'PADAWAN': 'Padawan'
            },
            "current_user": current_user,
            "page_title": "Exercices Simples",
            "is_simple_mode": True,
            "message": "Erreur lors du chargement des exercices simples.",
            "message_type": "error"
        })
    
    try:
        # Utiliser le template exercises.html avec un titre spécial et des types limités
        return render_template("exercises.html", request, {
            "exercises": exercises,
            "exercise_types": {
                'ADDITION': 'Addition',
                'SOUSTRACTION': 'Soustraction', 
                'DIVISION': 'Division'
            },
            "difficulty_levels": {
                'INITIE': 'Initié',
                'PADAWAN': 'Padawan'
            },
            "exercise_type_display": {
                'ADDITION': 'Addition',
                'SOUSTRACTION': 'Soustraction', 
                'DIVISION': 'Division'
            },
            "difficulty_display": {
                'INITIE': 'Initié',
                'PADAWAN': 'Padawan'
            },
            "current_user": current_user,
            "page_title": "Exercices Simples",
            "is_simple_mode": True
        })
        
    except Exception as e:
        return render_error(
            request=request,
            error="Erreur de chargement",
            message="Impossible de charger les exercices simples.",
            status_code=500
        )

# Génération d'exercice simple
async def generate_simple_exercise(request: Request):
    """Génère un exercice simple - redirection vers génération normale"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Pour l'instant, rediriger vers la génération normale
    return RedirectResponse(url="/api/exercises/generate", status_code=302)

# Page d'exercice simple individuel
async def simple_exercise_page(request: Request):
    """Rendu d'un exercice simple - force l'utilisation du template simple"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    exercise_id = request.path_params["exercise_id"]
    
    # Pour l'instant, rediriger vers l'exercice normal qui utilisera le template simple en fallback
    return RedirectResponse(url=f"/exercise/{exercise_id}", status_code=302)