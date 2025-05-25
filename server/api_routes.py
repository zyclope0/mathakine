"""
Routes d'API pour enhanced_server.py
"""
import traceback
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.handlers.exercise_handlers import (
    generate_exercise,
    get_exercise,
    submit_answer,
    get_exercises_list
)
from app.core.messages import SystemMessages
from server.handlers.user_handlers import get_user_stats

# Fonction pour gérer la génération d'exercices
# async def generate_exercise(request):
#     ... (supprimé car déplacé)


# Fonction pour obtenir un exercice spécifique
# async def get_exercise(request):
#     ... (supprimé car déplacé)


# Fonction pour soumettre une réponse
# async def submit_answer(request):
#     ... (supprimé car déplacé)


# Fonction pour lister les exercices
# async def get_exercises_list(request):
#     ... (supprimé car déplacé)


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
# async def get_user_stats(request):
#     ... (supprimé car déplacé)


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

async def handle_recommendation_complete(request):
    """Marque une recommandation comme complétée après qu'un utilisateur ait terminé un exercice recommandé"""
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated", False):
            return JSONResponse({"error": "Non autorisé"}, status_code=401)
        
        # Récupérer les données
        data = await request.json()
        recommendation_id = data.get("recommendation_id")
        
        if not recommendation_id:
            return JSONResponse({"error": "ID de recommandation manquant"}, status_code=400)
        
        # Récupérer la session de base de données
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'utilisateur complet
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            if not user:
                return JSONResponse({"error": "Utilisateur non trouvé"}, status_code=404)
            
            # Récupérer et vérifier la recommandation
            from app.models.recommendation import Recommendation
            recommendation = db.query(Recommendation).filter(
                Recommendation.id == recommendation_id,
                Recommendation.user_id == user.id
            ).first()
            
            if not recommendation:
                return JSONResponse({"error": "Recommandation non trouvée"}, status_code=404)
            
            # Marquer comme complétée
            from app.services.recommendation_service import RecommendationService
            RecommendationService.mark_recommendation_as_completed(db, recommendation_id)
            
            return JSONResponse({"status": "success"})
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors du marquage de la recommandation comme complétée: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur serveur: {str(e)}"}, status_code=500) 