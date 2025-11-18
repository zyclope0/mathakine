"""
Handlers pour la gestion des utilisateurs et statistiques (API)
"""
import traceback
from starlette.responses import JSONResponse
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.core.messages import SystemMessages
from loguru import logger

async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    Paramètres de requête:
        - timeRange: "7" (7 jours), "30" (30 jours), "90" (3 mois), "all" (tout)
    """
    try:
        # Récupérer l'utilisateur connecté au lieu d'utiliser un ID fixe
        from server.views import get_current_user
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated", False):
            # Logger en debug plutôt qu'en print pour éviter le bruit
            logger.debug("Utilisateur non authentifié pour récupération des statistiques")
            # Vérifier si un token était présent mais invalide
            access_token = request.cookies.get("access_token")
            if access_token:
                logger.debug("Token présent mais invalide ou expiré")
            else:
                logger.debug("Aucun token présent dans les cookies")
            return JSONResponse({"error": "Authentification requise"}, status_code=401)
        
        user_id = current_user.get("id")
        username = current_user.get("username")
        
        if not user_id:
            logger.warning(f"ID utilisateur manquant pour {username}")
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)
        
        # Récupérer le paramètre timeRange depuis la requête
        from starlette.requests import Request
        query_params = dict(request.query_params)
        time_range = query_params.get("timeRange", "30")  # Par défaut 30 jours
        
        # Valider timeRange
        valid_ranges = ["7", "30", "90", "all"]
        if time_range not in valid_ranges:
            logger.debug(f"TimeRange invalide '{time_range}', utilisation de la valeur par défaut '30'")
            time_range = "30"  # Fallback sur 30 jours
        
        logger.debug(f"Récupération des statistiques pour l'utilisateur {username} (ID: {user_id}), période: {time_range}")
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            stats = EnhancedServerAdapter.get_user_stats(db, user_id, time_range=time_range)
            if not stats:
                logger.debug(f"Aucune statistique trouvée pour l'utilisateur {username}, utilisation de valeurs par défaut")
                stats = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "success_rate": 0,
                    "by_exercise_type": {}
                }
            
            logger.debug(f"Statistiques récupérées pour {username}: {stats.get('total_attempts', 0)} tentatives")
            
            experience_points = stats.get("total_attempts", 0) * 10
            performance_by_type = {}
            # Les types sont déjà normalisés en minuscules dans user_service.py
            for exercise_type, type_stats in stats.get("by_exercise_type", {}).items():
                # S'assurer que la clé est en minuscules (déjà normalisée mais sécurité)
                type_key = str(exercise_type).lower() if exercise_type else 'unknown'
                performance_by_type[type_key] = {
                    "completed": type_stats.get("total", 0),
                    "correct": type_stats.get("correct", 0),
                    "success_rate": type_stats.get("success_rate", 0)
                }
            # Récupérer l'activité récente (dernières 10 tentatives)
            # Filtrer selon time_range si différent de "all"
            recent_activity = []
            try:
                from datetime import datetime, timedelta, timezone
                from sqlalchemy import text
                
                # Calculer la date de début pour le filtre
                date_filter = None
                if time_range != "all":
                    days = int(time_range)
                    date_filter = datetime.now(timezone.utc) - timedelta(days=days)
                
                # Utiliser une requête SQL brute pour éviter la validation d'enum SQLAlchemy
                # Récupérer directement les valeurs depuis la base sans passer par les modèles
                if date_filter:
                    recent_attempts_query = text("""
                        SELECT 
                            a.id,
                            a.is_correct,
                            a.created_at,
                            LOWER(e.exercise_type::text) as exercise_type,
                            e.title as exercise_title
                        FROM attempts a
                        JOIN exercises e ON e.id = a.exercise_id
                        WHERE a.user_id = :user_id
                          AND a.created_at >= :date_filter
                        ORDER BY a.created_at DESC
                        LIMIT 10
                    """)
                    result = db.execute(recent_attempts_query, {
                        "user_id": user_id,
                        "date_filter": date_filter
                    })
                else:
                    recent_attempts_query = text("""
                        SELECT 
                            a.id,
                            a.is_correct,
                            a.created_at,
                            LOWER(e.exercise_type::text) as exercise_type,
                            e.title as exercise_title
                        FROM attempts a
                        JOIN exercises e ON e.id = a.exercise_id
                        WHERE a.user_id = :user_id
                        ORDER BY a.created_at DESC
                        LIMIT 10
                    """)
                    result = db.execute(recent_attempts_query, {"user_id": user_id})
                
                recent_attempts_rows = result.fetchall()
                
                logger.debug(f"Tentatives récentes trouvées: {len(recent_attempts_rows)}")
                
                # Mapping des types d'exercices pour les descriptions
                type_display_mapping = {
                    'addition': 'Addition',
                    'soustraction': 'Soustraction',
                    'subtraction': 'Soustraction',
                    'multiplication': 'Multiplication',
                    'division': 'Division',
                    'mixte': 'Mixte',
                    'fractions': 'Fractions',
                    'geometrie': 'Géométrie',
                    'geometry': 'Géométrie',
                    'texte': 'Texte',
                    'text': 'Texte',
                    'divers': 'Divers',
                }
                
                # Fonction pour formater le temps relatif
                def format_relative_time(created_at):
                    """Formate une date en temps relatif (il y a X minutes/heures/jours)"""
                    if not created_at:
                        return "Récemment"
                    
                    # Gérer les timezones correctement
                    from datetime import timezone
                    if created_at.tzinfo:
                        now = datetime.now(created_at.tzinfo)
                        attempt_time = created_at
                    else:
                        # Si created_at n'a pas de timezone, utiliser UTC
                        now = datetime.now(timezone.utc)
                        attempt_time = created_at.replace(tzinfo=timezone.utc)
                    
                    delta = now - attempt_time
                    
                    if delta.total_seconds() < 60:
                        return "À l'instant"
                    elif delta.total_seconds() < 3600:
                        minutes = int(delta.total_seconds() / 60)
                        return f"Il y a {minutes} minute{'s' if minutes > 1 else ''}"
                    elif delta.total_seconds() < 86400:
                        hours = int(delta.total_seconds() / 3600)
                        return f"Il y a {hours} heure{'s' if hours > 1 else ''}"
                    elif delta.days < 7:
                        days = delta.days
                        return f"Il y a {days} jour{'s' if days > 1 else ''}"
                    else:
                        return created_at.strftime("%d/%m/%Y")
                
                # Formater chaque tentative
                for row in recent_attempts_rows:
                    # Les données viennent directement de la requête SQL brute
                    attempt_id = row[0]
                    is_correct = row[1]
                    created_at = row[2]
                    exercise_type = row[3]  # Déjà en minuscules grâce à LOWER()
                    exercise_title = row[4]
                    
                    # Normaliser le type d'exercice (déjà en minuscules depuis SQL)
                    exercise_type = exercise_type.lower() if exercise_type else 'divers'
                    type_label = type_display_mapping.get(exercise_type, exercise_type.capitalize())
                    
                    # Description de l'activité
                    status = "réussi" if is_correct else "échoué"
                    description = f"Exercice {type_label} {status}"
                    
                    # Temps relatif
                    time_str = format_relative_time(created_at)
                    
                    recent_activity.append({
                        'type': 'exercise_completed',
                        'description': description,
                        'time': time_str,
                        'is_correct': is_correct
                    })
                
                logger.debug(f"Activité récente formatée: {len(recent_activity)} items")
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'activité récente: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                # En cas d'erreur, garder la liste vide
                recent_activity = []
            
            level_data = {
                'current': 1,
                'title': 'Débutant Stellaire',
                'current_xp': experience_points,
                'next_level_xp': 100
            }
            
            # Générer progress_over_time dynamiquement depuis performance_by_type
            # Mapping des types d'exercices vers leurs labels (sera traduit côté frontend)
            type_label_mapping = {
                'addition': 'Addition',
                'soustraction': 'Soustraction',
                'subtraction': 'Soustraction',
                'multiplication': 'Multiplication',
                'division': 'Division',
                'mixte': 'Mixte',
                'fractions': 'Fractions',
                'geometrie': 'Géométrie',
                'geometry': 'Géométrie',
                'texte': 'Texte',
                'text': 'Texte',
                'divers': 'Divers',
            }
            
            # Trier les types par nombre d'exercices complétés (décroissant)
            # Limiter à top 8 pour lisibilité du graphique
            sorted_types = sorted(
                performance_by_type.items(),
                key=lambda x: x[1].get('completed', 0),
                reverse=True
            )[:8]
            
            # Générer labels et data dynamiquement
            progress_labels = []
            progress_data = []
            
            for ex_type, type_stats in sorted_types:
                # Utiliser le mapping ou le type original en fallback
                label = type_label_mapping.get(ex_type.lower(), ex_type.capitalize())
                progress_labels.append(label)
                progress_data.append(type_stats.get('completed', 0))
            
            # Si aucun type n'a de données, utiliser les types principaux par défaut
            if not progress_labels:
                default_types = ['addition', 'soustraction', 'multiplication', 'division']
                progress_labels = [type_label_mapping.get(t, t.capitalize()) for t in default_types]
                progress_data = [performance_by_type.get(t, {}).get('completed', 0) for t in default_types]
            
            progress_over_time = {
                'labels': progress_labels,
                'datasets': [{
                    'label': 'Exercices résolus',
                    'data': progress_data
                }]
            }
            # Générer le graphique des exercices par jour selon la période sélectionnée
            from datetime import datetime, timedelta, timezone
            current_date = datetime.now(timezone.utc).date()
            
            # Déterminer le nombre de jours à afficher selon time_range
            if time_range == "all":
                # Pour "all", on prend les 90 derniers jours pour l'affichage
                days_to_show = 90
            else:
                days_to_show = int(time_range)
            
            # Initialiser avec zéro pour chaque jour
            daily_exercises = {}
            for i in range(days_to_show - 1, -1, -1):
                day = current_date - timedelta(days=i)
                day_str = day.strftime("%d/%m")
                daily_exercises[day_str] = 0
            
            # Récupérer les vraies données des tentatives par jour
            try:
                from sqlalchemy import func, text
                from app.models.attempt import Attempt
                
                # Calculer la date de début pour le filtre
                start_date = current_date - timedelta(days=days_to_show - 1)
                start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                
                # Requête pour compter les tentatives par jour pour cet utilisateur
                daily_attempts_query = db.query(
                    func.date(Attempt.created_at).label('attempt_date'),
                    func.count(Attempt.id).label('count')
                ).filter(
                    Attempt.user_id == user_id,
                    Attempt.created_at >= start_datetime
                ).group_by(
                    func.date(Attempt.created_at)
                ).all()
                
                logger.debug(f"Tentatives par jour trouvées: {len(daily_attempts_query)} jours avec des données")
                
                # Remplir avec les données réelles
                for attempt_date, count in daily_attempts_query:
                    day_str = attempt_date.strftime("%d/%m")
                    if day_str in daily_exercises:
                        daily_exercises[day_str] = count
                        logger.debug(f"Jour {day_str}: {count} tentatives")
                        
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des tentatives quotidiennes: {e}")
                # En cas d'erreur, garder les valeurs à 0
            
            daily_labels = list(daily_exercises.keys())
            daily_counts = list(daily_exercises.values())
            
            logger.debug(f"Données du graphique quotidien: {sum(daily_counts)} tentatives au total sur {len(daily_labels)} jours")
            exercises_by_day = {
                'labels': daily_labels,
                'datasets': [{
                    'label': 'Exercices par jour',
                    'data': daily_counts,
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                }]
            }
            # Ajouter le timestamp de dernière mise à jour
            # Format ISO 8601 strict avec 'Z' pour UTC (compatible avec Zod datetime)
            from datetime import datetime, timezone
            last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Compter les challenges complétés
            try:
                from app.models.logic_challenge import LogicChallengeAttempt
                total_challenges = db.query(LogicChallengeAttempt).filter(
                    LogicChallengeAttempt.user_id == user_id,
                    LogicChallengeAttempt.is_correct == True
                ).count()
            except Exception as e:
                logger.error(f"Erreur lors du comptage des challenges: {e}")
                total_challenges = 0
            
            response_data = {
                'total_exercises': stats.get("total_attempts", 0),
                'total_challenges': total_challenges,
                'correct_answers': stats.get("correct_attempts", 0),
                'success_rate': stats.get("success_rate", 0),
                'experience_points': experience_points,
                'performance_by_type': performance_by_type,
                'recent_activity': recent_activity,
                'level': level_data,
                'progress_over_time': progress_over_time,
                'exercises_by_day': exercises_by_day,
                'lastUpdated': last_updated
            }
            logger.debug(f"Données du tableau de bord générées pour {username} avec {stats.get('total_attempts', 0)} tentatives")
            return JSONResponse(response_data)
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500) 