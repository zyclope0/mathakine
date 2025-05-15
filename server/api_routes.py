"""
Routes d'API pour enhanced_server.py
"""
import traceback
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.exercise_generator import generate_ai_exercise, generate_simple_exercise, ensure_explanation
from app.core.messages import SystemMessages

# Fonction pour gérer la génération d'exercices
async def generate_exercise(request):
    """Génère un nouvel exercice"""
    # Récupérer les paramètres (type d'exercice, difficulté)
    params = request.query_params
    exercise_type = params.get('type')
    difficulty = params.get('difficulty')
    use_ai = params.get('ai', False)
    
    # Si on demande de l'IA, utiliser la fonction de génération IA
    ai_generated = False
    if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
        exercise_dict = generate_ai_exercise(exercise_type, difficulty)
        ai_generated = True
    else:
        # Génération algorithmique simple
        exercise_dict = generate_simple_exercise(exercise_type, difficulty)
    
    # S'assurer que l'explication est définie
    exercise_dict = ensure_explanation(exercise_dict)
    
    print(f"Explication générée: {exercise_dict['explanation']}")
    
    try:
        # Utiliser l'adaptateur pour créer l'exercice
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Créer l'exercice avec l'adaptateur
            created_exercise = EnhancedServerAdapter.create_generated_exercise(
                db=db,
                exercise_type=exercise_dict['exercise_type'],
                difficulty=exercise_dict['difficulty'],
                title=exercise_dict['title'],
                question=exercise_dict['question'],
                correct_answer=exercise_dict['correct_answer'],
                choices=exercise_dict['choices'],
                explanation=exercise_dict['explanation'],
                hint=exercise_dict.get('hint'),
                tags=exercise_dict.get('tags', 'generated'),
                ai_generated=ai_generated
            )
            
            if created_exercise:
                exercise_id = created_exercise['id']
                print(f"Nouvel exercice créé avec ID={exercise_id}, explication: {exercise_dict['explanation']}")
            else:
                print("Erreur: L'exercice n'a pas été créé")
                # Récupérer les templates via une fonction externe ou un paramètre
                templates = request.app.state.templates
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Erreur de génération",
                    "message": "Impossible de créer l'exercice dans la base de données."
                }, status_code=500)
                
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)

        # Rediriger vers la page des exercices
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    
    except Exception as e:
        print(f"Erreur lors de la génération d'exercice: {e}")
        traceback.print_exc()
        # Récupérer les templates via une fonction externe ou un paramètre
        templates = request.app.state.templates
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Erreur de génération",
            "message": f"Impossible de générer l'exercice: {str(e)}"
        }, status_code=500)


# Fonction pour obtenir un exercice spécifique
async def get_exercise(request):
    """Récupère un exercice par son ID"""
    exercise_id = request.path_params.get('exercise_id')

    try:
        # Utiliser l'adaptateur pour récupérer l'exercice
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            
            if not exercise:
                return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)
                
            return JSONResponse(exercise)
        
        finally:
            EnhancedServerAdapter.close_db_session(db)
    
    except Exception as e:
        print(f"Erreur lors de la récupération de l'exercice: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)


# Fonction pour soumettre une réponse
async def submit_answer(request):
    """Traite la soumission d'une réponse à un exercice"""
    try:
        # Récupérer les données de la requête
        data = await request.json()
        exercise_id = data.get('exercise_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent', 0)
        user_id = data.get('user_id', 1)  # Utiliser l'ID 1 par défaut pour un utilisateur non authentifié

        print(f"Traitement de la réponse: exercise_id={exercise_id}, selected_answer={selected_answer}")

        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'exercice pour vérifier la réponse
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            if not exercise:
                return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)

            is_correct = selected_answer == exercise['correct_answer']
            print(f"Réponse correcte? {is_correct}")

            # Enregistrer la tentative avec notre adaptateur
            attempt_data = {
                "user_id": user_id,
                "exercise_id": exercise_id,
                "user_answer": selected_answer,
                "is_correct": is_correct,
                "time_spent": time_spent
            }
            
            attempt = EnhancedServerAdapter.record_attempt(db, attempt_data)
            
            if not attempt:
                print("ERREUR: La tentative n'a pas été enregistrée correctement")
                return JSONResponse({
                    "is_correct": is_correct,
                    "correct_answer": exercise['correct_answer'],
                    "explanation": exercise.get('explanation', ""),
                    "error": "Erreur lors de l'enregistrement de la tentative"
                }, status_code=500)
                
            print("Tentative enregistrée avec succès")

            # Retourner le résultat
            return JSONResponse({
                "is_correct": is_correct,
                "correct_answer": exercise['correct_answer'],
                "explanation": exercise.get('explanation', "")
            })
            
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)

    except Exception as e:
        print(f"Erreur lors du traitement de la réponse: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)


# Fonction pour lister les exercices
async def get_exercises_list(request):
    """Retourne la liste des exercices récents"""
    try:
        # Récupérer les paramètres de requête
        limit = int(request.query_params.get('limit', 10))
        skip = int(request.query_params.get('skip', 0))
        exercise_type = request.query_params.get('exercise_type', None)
        difficulty = request.query_params.get('difficulty', None)
        
        print(f"API - Paramètres reçus: exercise_type={exercise_type}, difficulty={difficulty}")
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser l'adaptateur pour lister les exercices
            exercises = EnhancedServerAdapter.list_exercises(
                db,
                exercise_type=exercise_type,
                difficulty=difficulty,
                limit=None  # Nous gérons la pagination manuellement pour être cohérent avec l'existant
            )
            
            # Appliquer pagination manuellement
            total = len(exercises)
            paginated_exercises = exercises[skip:skip+limit] if skip < total else []

            return JSONResponse({
                "items": paginated_exercises,
                "total": total,
                "skip": skip,
                "limit": limit
            })
            
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)

    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


# Fonction pour supprimer (archiver) un exercice
async def delete_exercise(request):
    """
    Archive un exercice par ID (marque comme supprimé sans suppression physique).
    Route: /api/exercises/{exercise_id}
    """
    try:
        # Extraire l'ID de l'exercice
        exercise_id = int(request.path_params["exercise_id"])
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Vérifier si l'exercice existe
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            if not exercise:
                return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)
            
            # Utiliser l'adaptateur pour archiver l'exercice
            success = EnhancedServerAdapter.archive_exercise(db, exercise_id)
            
            if not success:
                print(f"ERREUR: L'exercice {exercise_id} n'a pas été archivé correctement")
                return JSONResponse({"error": "L'exercice n'a pas été archivé correctement"}, status_code=500)
            
            print(f"Exercice {exercise_id} archivé avec succès")
            
            return JSONResponse({
                "success": True, 
                "message": SystemMessages.SUCCESS_ARCHIVED,
                "exercise_id": exercise_id
            }, status_code=200)
            
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)
        
    except Exception as error:
        print(f"Erreur lors de l'archivage de l'exercice {exercise_id}: {error}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(error)}"}, status_code=500)


# Fonction pour récupérer les statistiques utilisateur
async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    """
    try:
        # ID utilisateur fictif pour l'instant (sera remplacé par l'authentification plus tard)
        user_id = 1
        
        print("Début de la récupération des statistiques utilisateur")
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser l'adaptateur pour récupérer les statistiques utilisateur
            stats = EnhancedServerAdapter.get_user_stats(db, user_id)
            
            if not stats:
                print("Aucune statistique trouvée, utilisation de valeurs par défaut")
                stats = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "success_rate": 0,
                    "by_exercise_type": {}
                }
            
            # Calculer les points d'expérience
            experience_points = stats.get("total_attempts", 0) * 10
            
            # Reformater les données pour correspondre à l'API attendue
            performance_by_type = {}
            
            # Convertir le format des statistiques par type d'exercice
            for exercise_type, type_stats in stats.get("by_exercise_type", {}).items():
                performance_by_type[exercise_type.lower()] = {
                    "completed": type_stats.get("total", 0),
                    "correct": type_stats.get("correct", 0),
                    "success_rate": type_stats.get("success_rate", 0)
                }
            
            # Préparer des données fictives pour les parties non encore gérées par notre service
            # (à remplacer progressivement par des données réelles)
            
            # Activités récentes (à implémenter dans le service dans une future version)
            recent_activity = []
            
            # Niveau (simulation)
            level_data = {
                'current': 1,
                'title': 'Débutant Stellaire',
                'current_xp': 25,
                'next_level_xp': 100
            }
            
            # Graphique de progression (simulation)
            progress_over_time = {
                'labels': ['Addition', 'Soustraction', 'Multiplication', 'Division'],
                'datasets': [{
                    'label': 'Exercices résolus',
                    'data': [
                        performance_by_type.get('addition', {}).get('completed', 10),
                        performance_by_type.get('soustraction', {}).get('completed', 5),
                        performance_by_type.get('multiplication', {}).get('completed', 8),
                        performance_by_type.get('division', {}).get('completed', 3)
                    ]
                }]
            }
            
            # Graphique des exercices par jour (simulation)
            from datetime import datetime, timedelta
            current_date = datetime.now().date()
            
            daily_exercises = {}
            for i in range(30, -1, -1):
                day = current_date - timedelta(days=i)
                day_str = day.strftime("%d/%m")
                daily_exercises[day_str] = 0
            
            daily_labels = list(daily_exercises.keys())
            daily_counts = list(daily_exercises.values())
            
            exercises_by_day = {
                'labels': daily_labels,
                'datasets': [{
                    'label': 'Exercices par jour',
                    'data': daily_counts,
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                }]
            }
            
            # Construire la réponse complète
            response_data = {
                'total_exercises': stats.get("total_attempts", 0),
                'correct_answers': stats.get("correct_attempts", 0),
                'success_rate': stats.get("success_rate", 0),
                'experience_points': experience_points,
                'performance_by_type': performance_by_type,
                'recent_activity': recent_activity,
                'level': level_data,
                'progress_over_time': progress_over_time,
                'exercises_by_day': exercises_by_day
            }
            
            print("Données du tableau de bord générées avec le nouvel adaptateur")
            return JSONResponse(response_data)
            
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)
    
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500) 