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
        # Récupérer l'utilisateur connecté au lieu d'utiliser un ID fixe
        from server.views import get_current_user
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated", False):
            print("Utilisateur non authentifié pour récupération des statistiques")
            return JSONResponse({"error": "Authentification requise"}, status_code=401)
        
        user_id = current_user.get("id")
        username = current_user.get("username")
        
        if not user_id:
            print(f"ID utilisateur manquant pour {username}")
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)
        
        print(f"Début de la récupération des statistiques pour l'utilisateur {username} (ID: {user_id})")
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            stats = EnhancedServerAdapter.get_user_stats(db, user_id)
            if not stats:
                print(f"Aucune statistique trouvée pour l'utilisateur {username}, utilisation de valeurs par défaut")
                stats = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "success_rate": 0,
                    "by_exercise_type": {}
                }
            
            print(f"Statistiques récupérées pour {username}: {stats.get('total_attempts', 0)} tentatives")
            
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
                'current_xp': experience_points,
                'next_level_xp': 100
            }
            progress_over_time = {
                'labels': ['Addition', 'Soustraction', 'Multiplication', 'Division'],
                'datasets': [{
                    'label': 'Exercices résolus',
                    'data': [
                        performance_by_type.get('addition', {}).get('completed', 0),
                        performance_by_type.get('soustraction', {}).get('completed', 0),
                        performance_by_type.get('multiplication', {}).get('completed', 0),
                        performance_by_type.get('division', {}).get('completed', 0)
                    ]
                }]
            }
            # Générer le graphique des exercices par jour avec les vraies données
            from datetime import datetime, timedelta
            current_date = datetime.now().date()
            
            # Initialiser avec zéro pour chaque jour des 30 derniers jours
            daily_exercises = {}
            for i in range(30, -1, -1):
                day = current_date - timedelta(days=i)
                day_str = day.strftime("%d/%m")
                daily_exercises[day_str] = 0
            
            # Récupérer les vraies données des tentatives par jour
            try:
                from sqlalchemy import func, text
                from app.models.attempt import Attempt
                
                # Requête pour compter les tentatives par jour pour cet utilisateur
                daily_attempts_query = db.query(
                    func.date(Attempt.created_at).label('attempt_date'),
                    func.count(Attempt.id).label('count')
                ).filter(
                    Attempt.user_id == user_id,
                    Attempt.created_at >= current_date - timedelta(days=30)
                ).group_by(
                    func.date(Attempt.created_at)
                ).all()
                
                print(f"Tentatives par jour trouvées: {len(daily_attempts_query)} jours avec des données")
                
                # Remplir avec les données réelles
                for attempt_date, count in daily_attempts_query:
                    day_str = attempt_date.strftime("%d/%m")
                    if day_str in daily_exercises:
                        daily_exercises[day_str] = count
                        print(f"Jour {day_str}: {count} tentatives")
                        
            except Exception as e:
                print(f"Erreur lors de la récupération des tentatives quotidiennes: {e}")
                # En cas d'erreur, garder les valeurs à 0
            
            daily_labels = list(daily_exercises.keys())
            daily_counts = list(daily_exercises.values())
            
            print(f"Données du graphique quotidien: {sum(daily_counts)} tentatives au total sur {len(daily_labels)} jours")
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
            print(f"Données du tableau de bord générées pour {username} avec {stats.get('total_attempts', 0)} tentatives")
            return JSONResponse(response_data)
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500) 