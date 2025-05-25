"""
Handlers pour la gestion des utilisateurs et statistiques (API)
"""
import traceback
from starlette.responses import JSONResponse
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.core.messages import SystemMessages

async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    """
    try:
        # ID utilisateur fictif pour l'instant (sera remplacé par l'authentification plus tard)
        user_id = 1
        print("Début de la récupération des statistiques utilisateur")
        db = EnhancedServerAdapter.get_db_session()
        try:
            stats = EnhancedServerAdapter.get_user_stats(db, user_id)
            if not stats:
                print("Aucune statistique trouvée, utilisation de valeurs par défaut")
                stats = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "success_rate": 0,
                    "by_exercise_type": {}
                }
            experience_points = stats.get("total_attempts", 0) * 10
            performance_by_type = {}
            for exercise_type, type_stats in stats.get("by_exercise_type", {}).items():
                performance_by_type[exercise_type.lower()] = {
                    "completed": type_stats.get("total", 0),
                    "correct": type_stats.get("correct", 0),
                    "success_rate": type_stats.get("success_rate", 0)
                }
            recent_activity = []
            level_data = {
                'current': 1,
                'title': 'Débutant Stellaire',
                'current_xp': 25,
                'next_level_xp': 100
            }
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
            EnhancedServerAdapter.close_db_session(db)
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500) 