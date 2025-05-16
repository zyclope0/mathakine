"""
Routes des vues pour Mathakine.

Ce module contient les fonctions de rendu pour les pages web.
"""
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
import traceback
import json

from app.core.constants import ExerciseTypes, DifficultyLevels, DISPLAY_NAMES, Messages
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.template_handler import render_template, render_error

# Fonction pour récupérer l'utilisateur courant
async def get_current_user(request: Request):
    """Récupère l'utilisateur actuellement connecté à partir du token"""
    try:
        access_token = request.cookies.get("access_token")
        if not access_token:
            return None
            
        # Utiliser le service d'authentification pour décoder le token
        from app.core.security import decode_token
        from app.services.auth_service import get_user_by_username
        
        # Décoder le token pour obtenir le nom d'utilisateur
        payload = decode_token(access_token)
        username = payload.get("sub")
        
        if not username:
            return None
            
        # Récupérer l'utilisateur depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = get_user_by_username(db, username)
            if user:
                return {
                    "is_authenticated": True,
                    "username": user.username,
                    "role": user.role
                }
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
        traceback.print_exc()
        
    return None

# Page d'accueil
async def homepage(request: Request):
    """Rendu de la page d'accueil"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    return render_template("home.html", request, {
        "current_user": current_user
    })

# Page de connexion
async def login_page(request: Request):
    """Rendu de la page de connexion"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    if current_user["is_authenticated"]:
        return RedirectResponse(url="/", status_code=302)
    return render_template("login.html", request, {
        "current_user": current_user
    })

# Traitement de l'authentification API
async def api_login(request: Request):
    """API pour l'authentification"""
    try:
        # Récupérer les données JSON du corps de la requête
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return JSONResponse(
                {"detail": "Nom d'utilisateur et mot de passe requis"},
                status_code=400
            )
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser le service d'authentification pour vérifier les identifiants
            from app.services.auth_service import authenticate_user, create_user_token
            
            user = authenticate_user(db, username, password)
            if user:
                # Générer les tokens d'accès et de rafraîchissement
                tokens = create_user_token(user)
                
                # Créer une réponse de redirection
                response = RedirectResponse(url="/", status_code=302)
                
                # Définir les cookies avec les tokens
                response.set_cookie(
                    key="access_token",
                    value=tokens["access_token"],
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=3600  # 1 heure
                )
                response.set_cookie(
                    key="refresh_token",
                    value=tokens["refresh_token"],
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=86400 * 30  # 30 jours
                )
                
                return response
            else:
                return JSONResponse(
                    {"detail": "Nom d'utilisateur ou mot de passe incorrect"},
                    status_code=401
                )
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors de l'authentification API: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            {"detail": "Erreur lors de l'authentification"},
            status_code=500
        )

# Page d'inscription
async def register_page(request: Request):
    """Rendu de la page d'inscription"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    if current_user["is_authenticated"]:
        return RedirectResponse(url="/", status_code=302)
    return render_template("register.html", request, {
        "current_user": current_user
    })

# Déconnexion
async def logout(request: Request):
    """Déconnexion de l'utilisateur"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

# Page des exercices
async def exercises_page(request: Request):
    """Rendu de la page des exercices"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Vérifier si nous venons d'une génération d'exercices
    just_generated = request.query_params.get('generated', 'false') == 'true'
    print(f"Page d'exercices chargée, just_generated={just_generated}")
    
    # Récupérer les paramètres de filtrage
    exercise_type = request.query_params.get('exercise_type', None)
    difficulty = request.query_params.get('difficulty', None)
    
    print(f"Paramètres reçus - exercise_type: {exercise_type}, difficulty: {difficulty}")
    
    # Normaliser les paramètres si présents
    if exercise_type:
        exercise_type = normalize_exercise_type(exercise_type)
        print(f"Type d'exercice normalisé: {exercise_type}")
    if difficulty:
        difficulty = normalize_difficulty(difficulty)
        print(f"Difficulté normalisée: {difficulty}")

    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser l'adaptateur pour lister les exercices
            exercises = EnhancedServerAdapter.list_exercises(
                db,
                exercise_type=exercise_type,
                difficulty=difficulty
            )
            
            print(f"Nombre d'exercices récupérés: {len(exercises)}")
            if len(exercises) > 0:
                print(f"Premier exercice: ID={exercises[0].get('id')}, Titre={exercises[0].get('title')}")
                print(f"Dernier exercice: ID={exercises[-1].get('id')}, Titre={exercises[-1].get('title')}")
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        exercises = []
    
    # Message pour indiquer si on vient de générer un exercice
    message = None
    message_type = None
    if just_generated:
        message = "Exercice généré avec succès. Vous pouvez maintenant le résoudre ou en générer un autre."
        message_type = "success"

    # Créer des dictionnaires pour l'affichage des types et niveaux
    exercise_types = {key: DISPLAY_NAMES[key] for key in ExerciseTypes.ALL_TYPES}
    difficulty_levels = {key: DISPLAY_NAMES[key] for key in DifficultyLevels.ALL_LEVELS}
    
    # Mappings pour l'affichage des exercices dans la liste
    exercise_type_display = DISPLAY_NAMES
    difficulty_display = DISPLAY_NAMES
    
    # Préfixe IA pour les templates
    ai_prefix = Messages.AI_EXERCISE_PREFIX

    print(f"Préparation du rendu template avec {len(exercises)} exercices")
    
    return render_template("exercises.html", request, {
        "exercises": exercises,
        "message": message,
        "message_type": message_type,
        "exercise_types": exercise_types,
        "difficulty_levels": difficulty_levels,
        "exercise_type_display": exercise_type_display,
        "difficulty_display": difficulty_display,
        "ai_prefix": ai_prefix,
        "current_user": current_user
    })

# Page du tableau de bord
async def dashboard(request: Request):
    """Rendu de la page de tableau de bord avec statistiques"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
        
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'utilisateur complet pour avoir son ID
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            if not user:
                return render_error(
                    request=request,
                    error="Utilisateur non trouvé",
                    message="Impossible de récupérer les statistiques de l'utilisateur",
                    status_code=404
                )
            
            # Utiliser l'adaptateur pour récupérer les statistiques utilisateur avec le bon ID
            stats = EnhancedServerAdapter.get_user_stats(db, user.id)
            
            if not stats:
                print("Aucune statistique trouvée, utilisation de valeurs par défaut")
                stats = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "success_rate": 0,
                    "by_exercise_type": {}
                }
                
            # Préparer les données pour le rendu
            total_completed = stats.get("total_attempts", 0)
            correct_answers = stats.get("correct_attempts", 0)
            success_rate = stats.get("success_rate", 0)
            
            # Performance par type d'exercice
            performance_by_type = {}
            for exercise_type, type_stats in stats.get("by_exercise_type", {}).items():
                type_fr = {
                    ExerciseTypes.ADDITION: "Addition",
                    ExerciseTypes.SUBTRACTION: "Soustraction",
                    ExerciseTypes.MULTIPLICATION: "Multiplication",
                    ExerciseTypes.DIVISION: "Division"
                }
                
                exercise_type_name = type_fr.get(exercise_type, exercise_type)
                performance_by_type[exercise_type_name] = {
                    "total": type_stats.get("total", 0),
                    "correct": type_stats.get("correct", 0),
                    "success_rate": type_stats.get("success_rate", 0)
                }
                
            # Récupérer les exercices récents (simulation)
            recent_results = []
            
            # Préparer les données pour les graphiques
            chart_data = {
                "performance": {
                    "labels": list(performance_by_type.keys()),
                    "values": [stats["success_rate"] for stats in performance_by_type.values()]
                },
                "activity": {
                    "labels": ["Jour 1", "Jour 2", "Jour 3", "Jour 4", "Jour 5", "Jour 6", "Jour 7"],
                    "values": [5, 7, 3, 8, 10, 6, 4]  # Données fictives pour l'exemple
                }
            }
            
            # Récupérer les recommandations personnalisées
            from app.services.recommendation_service import RecommendationService
            recommendations = RecommendationService.get_user_recommendations(db, user.id, limit=3)
            
            # Si aucune recommandation n'existe, générer de nouvelles recommandations
            if not recommendations:
                RecommendationService.generate_recommendations(db, user.id)
                recommendations = RecommendationService.get_user_recommendations(db, user.id, limit=3)
            
            # Préparer les données de recommandation pour le template
            recommendations_data = []
            for rec in recommendations:
                # Marquer comme affichée
                RecommendationService.mark_recommendation_as_shown(db, rec.id)
                
                rec_data = {
                    "id": rec.id,
                    "exercise_type": rec.exercise_type,
                    "difficulty": rec.difficulty,
                    "priority": rec.priority,
                    "reason": rec.reason,
                    "exercise_id": rec.exercise_id
                }
                
                # Ajouter les informations de l'exercice si présent
                if rec.exercise_id:
                    from app.models.exercise import Exercise
                    exercise = db.query(Exercise).filter(Exercise.id == rec.exercise_id).first()
                    if exercise:
                        rec_data["exercise_title"] = exercise.title
                        rec_data["exercise_question"] = exercise.question
                
                recommendations_data.append(rec_data)
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
        context = {
            "user": current_user,
            "total_completed": total_completed,
            "correct_answers": correct_answers,
            "success_rate": success_rate,
            "performance": performance_by_type,
            "recent_results": recent_results,
            "chart_data": json.dumps(chart_data),
            "current_user": current_user,
            "recommendations": recommendations_data  # Ajouter les recommandations au contexte
        }
        
        return render_template("dashboard.html", request, context)
        
    except Exception as e:
        print(f"Erreur lors de la génération du tableau de bord: {e}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur lors de la génération du tableau de bord",
            message=str(e),
            status_code=500
        )

# Page de détail d'un exercice
async def exercise_detail_page(request: Request):
    """Rendu de la page de détail d'un exercice"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    exercise_id = request.path_params["exercise_id"]
    
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'exercice
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            
            if not exercise:
                return render_error(
                    request=request,
                    error="Exercice non trouvé",
                    message=f"L'exercice avec l'ID {exercise_id} n'existe pas ou a été supprimé.",
                    status_code=404
                )
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
        # Mappings pour l'affichage des types et niveaux
        exercise_type_display = DISPLAY_NAMES
        difficulty_display = DISPLAY_NAMES
        
        return render_template("exercise_detail.html", request, {
            "exercise": exercise,
            "exercise_type_display": exercise_type_display,
            "difficulty_display": difficulty_display,
            "current_user": current_user
        })
        
    except Exception as e:
        print(f"Exception lors de la récupération de l'exercice {exercise_id}: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur de base de données",
            message=f"Une erreur est survenue lors de la récupération de l'exercice: {str(e)}",
            status_code=500
        )

# Fonction pour normaliser le type d'exercice
def normalize_exercise_type(exercise_type):
    """Normalise le type d'exercice"""
    if not exercise_type:
        return ExerciseTypes.ADDITION

    exercise_type = exercise_type.lower()

    # Parcourir tous les types d'exercices et leurs alias
    for type_key, aliases in ExerciseTypes.TYPE_ALIASES.items():
        if exercise_type in aliases:
            return type_key
            
    # Si aucune correspondance trouvée, retourner le type tel quel
    return exercise_type

# Fonction pour normaliser la difficulté
def normalize_difficulty(difficulty):
    """Normalise le niveau de difficulté"""
    if not difficulty:
        return DifficultyLevels.PADAWAN

    difficulty = difficulty.lower()

    # Parcourir tous les niveaux de difficulté et leurs alias
    for level_key, aliases in DifficultyLevels.LEVEL_ALIASES.items():
        if difficulty in aliases:
            return level_key
            
    # Si aucune correspondance trouvée, retourner la difficulté telle quelle
    return difficulty 