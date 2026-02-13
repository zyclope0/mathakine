"""
Handlers pour la gestion des utilisateurs et statistiques (API)
"""
import json
import re
import traceback
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.messages import SystemMessages
from app.schemas.user import UserCreate
from app.services.auth_service import create_user, get_user_by_email
from app.utils.error_handler import get_safe_error_message
from app.utils.rate_limit import rate_limit_register
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.auth import require_auth


@require_auth
async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    Paramètres de requête:
        - timeRange: "7" (7 jours), "30" (30 jours), "90" (3 mois), "all" (tout)
    """
    try:
        current_user = request.state.user
        
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
                    "success_rate": (type_stats.get("correct", 0) / type_stats.get("total", 1) * 100)
                }
            # Récupérer l'activité récente (dernières 10 tentatives)
            # Filtrer selon time_range si différent de "all"
            recent_activity = []
            try:
                from datetime import datetime, timedelta, timezone

                from app.models.attempt import Attempt
                from app.models.logic_challenge import LogicChallengeAttempt

                # Calculer la date limite si nécessaire
                if time_range != "all":
                    days = int(time_range)
                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                else:
                    cutoff_date = None
                
                # Récupérer les tentatives d'exercices récentes
                # IMPORTANT: Appliquer tous les filter() AVANT limit() et order_by()
                exercise_attempts_query = db.query(Attempt).filter(
                    Attempt.user_id == user_id
                )
                
                if cutoff_date:
                    exercise_attempts_query = exercise_attempts_query.filter(Attempt.created_at >= cutoff_date)
                
                exercise_attempts = exercise_attempts_query.order_by(Attempt.created_at.desc()).limit(5).all()
                
                for attempt in exercise_attempts:
                    recent_activity.append({
                        "type": "exercise",
                        "description": f"Exercice complété",
                        "time": attempt.created_at.isoformat() if attempt.created_at else datetime.now(timezone.utc).isoformat(),
                        "is_correct": attempt.is_correct
                    })
                
                # Récupérer les tentatives de challenges récentes
                # IMPORTANT: Appliquer tous les filter() AVANT limit() et order_by()
                challenge_attempts_query = db.query(LogicChallengeAttempt).filter(
                    LogicChallengeAttempt.user_id == user_id
                )
                
                if cutoff_date:
                    challenge_attempts_query = challenge_attempts_query.filter(LogicChallengeAttempt.created_at >= cutoff_date)
                
                challenge_attempts = challenge_attempts_query.order_by(LogicChallengeAttempt.created_at.desc()).limit(5).all()
                
                for attempt in challenge_attempts:
                    recent_activity.append({
                        "type": "challenge",
                        "description": f"Défi logique complété",
                        "time": attempt.created_at.isoformat() if attempt.created_at else datetime.now(timezone.utc).isoformat(),
                        "is_correct": attempt.is_correct
                    })
                
                # Trier par date décroissante et prendre les 10 plus récentes
                recent_activity.sort(key=lambda x: x.get("time", ""), reverse=True)
                recent_activity = recent_activity[:10]
                
            except Exception as activity_error:
                logger.error(f"Erreur lors de la récupération de l'activité récente: {activity_error}")
                recent_activity = []
            
            # Calculer le niveau et XP
            def calculate_user_level(xp: int) -> dict:
                """
                Calcule le niveau utilisateur basé sur les points d'expérience.
                
                Args:
                    xp: Points d'expérience totaux
                
                Returns:
                    Dictionnaire avec current, title, current_xp, next_level_xp
                """
                # Seuils de niveau (100 points par niveau)
                level_thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]
                
                # Trouver le niveau actuel
                current_level = 1
                for i, threshold in enumerate(level_thresholds):
                    if xp >= threshold:
                        current_level = i + 1
                
                # Calculer les XP pour le niveau actuel et suivant
                current_xp = xp - level_thresholds[current_level - 1] if current_level > 1 else xp
                next_level_xp = level_thresholds[current_level] - level_thresholds[current_level - 1] if current_level < len(level_thresholds) else 100
                
                # Titres de niveau
                level_titles = {
                    1: "Jeune Padawan",
                    2: "Padawan",
                    3: "Chevalier Jedi",
                    4: "Maître Jedi",
                    5: "Grand Maître",
                    6: "Maître du Conseil",
                    7: "Légende Jedi",
                    8: "Gardien de la Force",
                    9: "Seigneur Jedi",
                    10: "Archiviste Jedi",
                    11: "Grand Archiviste"
                }
                
                title = level_titles.get(current_level, f"Niveau {current_level}")
                
                return {
                    "current": current_level,
                    "title": title,
                    "current_xp": current_xp,
                    "next_level_xp": next_level_xp
                }
            
            level_data = calculate_user_level(experience_points)
            
            # Calculer la progression dans le temps
            progress_over_time = []
            exercises_by_day = []
            
            try:
                from collections import defaultdict
                from datetime import datetime, timedelta, timezone

                # Calculer la date de début selon time_range
                if time_range == "all":
                    start_date = datetime.now(timezone.utc) - timedelta(days=90)  # Par défaut 90 jours
                else:
                    start_date = datetime.now(timezone.utc) - timedelta(days=int(time_range))
                
                # Récupérer les tentatives par jour
                daily_stats = defaultdict(lambda: {"total": 0, "correct": 0})
                
                attempts_query = db.query(Attempt).filter(
                    Attempt.user_id == user_id,
                    Attempt.created_at >= start_date
                ).all()
                
                for attempt in attempts_query:
                    if attempt.created_at:
                        day_key = attempt.created_at.date().isoformat()
                        daily_stats[day_key]["total"] += 1
                        if attempt.is_correct:
                            daily_stats[day_key]["correct"] += 1
                
                # Créer les datasets pour les graphiques
                sorted_days = sorted(daily_stats.keys())
                progress_over_time = {
                    "labels": sorted_days,
                    "datasets": [{
                        "label": "Taux de réussite (%)",
                        "data": [
                            (daily_stats[day]["correct"] / daily_stats[day]["total"] * 100) 
                            if daily_stats[day]["total"] > 0 else 0
                            for day in sorted_days
                        ]
                    }]
                }
                
                exercises_by_day = {
                    "labels": sorted_days,
                    "datasets": [{
                        "label": "Exercices complétés",
                        "data": [daily_stats[day]["total"] for day in sorted_days],
                        "borderColor": "rgb(139, 92, 246)",
                        "backgroundColor": "rgba(139, 92, 246, 0.1)"
                    }]
                }
                
            except Exception as progress_calculation_error:
                logger.error(f"Erreur lors du calcul de la progression: {progress_calculation_error}")
                progress_over_time = {"labels": [], "datasets": []}
                exercises_by_day = {"labels": [], "datasets": []}
            
            # Compter les challenges complétés
            try:
                from app.models.logic_challenge import LogicChallengeAttempt
                total_challenges = db.query(LogicChallengeAttempt).filter(
                    LogicChallengeAttempt.user_id == user_id,
                    LogicChallengeAttempt.is_correct == True
                ).count()
            except Exception as challenge_count_error:
                logger.error(f"Erreur lors du comptage des challenges: {challenge_count_error}")
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
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }
            
            return JSONResponse(response_data)
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as stats_retrieval_error:
        logger.error(f"Erreur lors de la récupération des statistiques: {stats_retrieval_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse({"error": "Erreur lors de la récupération des statistiques"}, status_code=500)


@rate_limit_register
async def create_user_account(request: Request):
    """
    Endpoint pour créer un nouveau compte utilisateur.
    Route: POST /api/users/
    
    Body JSON:
    {
        "username": "nom_utilisateur",
        "email": "email@example.com",
        "password": "MotDePasse123",
        "full_name": "Nom Complet" (optionnel)
    }
    """
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()
        
        # Extraire les champs requis
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip() or None
        
        # Validation basique côté serveur
        if not username:
            return JSONResponse(
                {"error": "Le nom d'utilisateur est requis"},
                status_code=400
            )
        
        if len(username) < 3:
            return JSONResponse(
                {"error": "Le nom d'utilisateur doit contenir au moins 3 caractères"},
                status_code=400
            )
        
        if not email:
            return JSONResponse(
                {"error": "L'email est requis"},
                status_code=400
            )
        
        # Validation email basique
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            return JSONResponse(
                {"error": "Format d'email invalide"},
                status_code=400
            )
        
        if not password:
            return JSONResponse(
                {"error": "Le mot de passe est requis"},
                status_code=400
            )
        
        # Validation mot de passe selon le schéma UserCreate
        if len(password) < 8:
            return JSONResponse(
                {"error": "Le mot de passe doit contenir au moins 8 caractères"},
                status_code=400
            )
        
        if not any(char.isdigit() for char in password):
            return JSONResponse(
                {"error": "Le mot de passe doit contenir au moins un chiffre"},
                status_code=400
            )
        
        if not any(char.isupper() for char in password):
            return JSONResponse(
                {"error": "Le mot de passe doit contenir au moins une majuscule"},
                status_code=400
            )
        
        # Créer l'utilisateur via le service
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Créer le schéma UserCreate
            user_create = UserCreate(
                username=username,
                email=email,
                password=password,
                full_name=full_name
            )
            
            # Créer l'utilisateur
            user = create_user(db, user_create)
            
            # Générer un token de vérification email
            from datetime import datetime, timezone

            from app.utils.email_verification import \
                generate_verification_token
            
            verification_token = generate_verification_token()
            user.email_verification_token = verification_token
            user.email_verification_sent_at = datetime.now(timezone.utc)
            user.is_email_verified = False  # Par défaut non vérifié
            
            # Sauvegarder les modifications
            db.commit()
            db.refresh(user)
            
            # Envoyer l'email de vérification
            try:
                logger.info(f"Préparation envoi email de vérification à {user.email}")
                import os

                from app.services.email_service import EmailService
                frontend_url = os.getenv("FRONTEND_URL", "https://mathakine-frontend.onrender.com")
                
                logger.debug(f"Frontend URL: {frontend_url}, Token: {verification_token[:10]}...")
                
                email_sent = EmailService.send_verification_email(
                    to_email=user.email,
                    username=user.username,
                    verification_token=verification_token,
                    frontend_url=frontend_url
                )
                
                if email_sent:
                    logger.info(f"✅ Email de vérification envoyé avec succès à {user.email}")
                    if "localhost" in frontend_url:
                        verify_link = f"{frontend_url}/verify-email?token={verification_token}"
                        logger.info(f"[DEV] Si l'email n'arrive pas, copie ce lien : {verify_link}")
                else:
                    logger.warning(f"⚠️ Échec de l'envoi de l'email de vérification à {user.email}")
                    logger.warning(f"Vérifiez la configuration SMTP dans les variables d'environnement")
            except Exception as email_error:
                # Ne pas faire échouer l'inscription si l'email échoue
                logger.error(f"❌ Erreur lors de l'envoi de l'email de vérification: {email_error}")
                logger.debug(traceback.format_exc())
            
            # Retourner les données de l'utilisateur créé (sans le mot de passe)
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "is_active": user.is_active,
                "is_email_verified": user.is_email_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            
            logger.info(f"Nouvel utilisateur créé: {username} ({email})")
            
            return JSONResponse(user_data, status_code=201)
            
        except HTTPException as http_error:
            # Gérer les erreurs HTTP (ex: utilisateur déjà existant)
            logger.warning(f"Erreur HTTP lors de la création de l'utilisateur: {http_error.detail}")
            return JSONResponse(
                {"error": http_error.detail},
                status_code=http_error.status_code
            )
        except Exception as user_creation_error:
            logger.error(f"Erreur lors de la création de l'utilisateur: {user_creation_error}")
            logger.debug(traceback.format_exc())
            return JSONResponse(
                {"error": "Erreur lors de la création du compte"},
                status_code=500
            )
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "Format JSON invalide"},
            status_code=400
        )
    except Exception as unexpected_creation_error:
        logger.error(f"Erreur inattendue lors de la création de l'utilisateur: {unexpected_creation_error}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"error": "Erreur lors de la création du compte"},
            status_code=500
        )


@require_auth
async def get_all_users(request: Request):
    """
    Handler pour récupérer tous les utilisateurs (placeholder).
    Route: GET /api/users/
    """
    try:
        current_user = request.state.user
        
        logger.info(f"Accès à la liste de tous les utilisateurs par {current_user.get('username')}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": "La liste de tous les utilisateurs est en cours de développement."},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de tous les utilisateurs: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def get_users_leaderboard(request: Request):
    """
    Handler pour récupérer le classement des utilisateurs (placeholder).
    Route: GET /api/users/leaderboard
    """
    try:
        current_user = request.state.user
        
        logger.info(f"Accès au classement des utilisateurs par {current_user.get('username')}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": "Le classement des utilisateurs est en cours de développement."},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du classement des utilisateurs: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def get_all_user_progress(request: Request):
    """
    Handler pour récupérer la progression globale de l'utilisateur avec vraies données.
    Route: GET /api/users/me/progress
    """
    try:
        current_user = request.state.user
        
        user_id = current_user.get('id')
        logger.info(f"Récupération de la progression globale pour l'utilisateur {user_id}")
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.attempt import Attempt
            from app.models.exercise import Exercise
            
            # Récupérer toutes les tentatives avec jointure sur exercises
            attempts_query = db.query(Attempt, Exercise).join(
                Exercise, Attempt.exercise_id == Exercise.id
            ).filter(
                Attempt.user_id == user_id
            ).order_by(Attempt.created_at).all()
            
            if not attempts_query:
                return JSONResponse({
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "accuracy": 0.0,
                    "average_time": 0.0,
                    "exercises_completed": 0,
                    "highest_streak": 0,
                    "current_streak": 0,
                    "by_category": {}
                }, status_code=200)
            
            # Stats globales
            total_attempts = len(attempts_query)
            correct_attempts = sum(1 for attempt, _ in attempts_query if attempt.is_correct)
            accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0.0
            
            # Temps moyen
            times = [attempt.time_spent for attempt, _ in attempts_query if attempt.time_spent]
            average_time = sum(times) / len(times) if times else 0.0
            
            # Exercices uniques complétés
            completed_exercise_ids = set()
            for attempt, exercise in attempts_query:
                if attempt.is_correct:
                    completed_exercise_ids.add(exercise.id)
            exercises_completed = len(completed_exercise_ids)
            
            # Calcul des streaks
            streaks = []
            current_streak = 0
            for attempt, _ in attempts_query:
                if attempt.is_correct:
                    current_streak += 1
                else:
                    if current_streak > 0:
                        streaks.append(current_streak)
                    current_streak = 0
            if current_streak > 0:
                streaks.append(current_streak)
            
            highest_streak = max(streaks) if streaks else 0
            current_streak_value = streaks[-1] if streaks else 0
            
            # Grouper par catégorie
            by_category = {}
            category_attempts = {}
            
            for attempt, exercise in attempts_query:
                exercise_type = exercise.exercise_type or "unknown"
                
                if exercise_type not in category_attempts:
                    category_attempts[exercise_type] = {
                        "total": 0,
                        "correct": 0,
                        "completed_ids": set()
                    }
                
                category_attempts[exercise_type]["total"] += 1
                if attempt.is_correct:
                    category_attempts[exercise_type]["correct"] += 1
                    category_attempts[exercise_type]["completed_ids"].add(exercise.id)
            
            for exercise_type, stats in category_attempts.items():
                total = stats["total"]
                correct = stats["correct"]
                by_category[exercise_type] = {
                    "completed": len(stats["completed_ids"]),
                    "accuracy": round(correct / total, 2) if total > 0 else 0.0
                }
            
            return JSONResponse({
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "accuracy": round(accuracy, 2),
                "average_time": round(average_time, 1),
                "exercises_completed": exercises_completed,
                "highest_streak": highest_streak,
                "current_streak": current_streak_value,
                "by_category": by_category
            }, status_code=200)
        
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la progression globale de l'utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def get_user_progress_by_exercise_type(request: Request):
    """
    Handler pour récupérer la progression de l'utilisateur par type d'exercice (placeholder).
    Route: GET /api/users/me/progress/{exercise_type}
    """
    try:
        current_user = request.state.user
        
        user_id = current_user.get('id')
        exercise_type = request.path_params.get('exercise_type')
        logger.info(f"Accès à la progression de l'utilisateur {user_id} pour le type d'exercice '{exercise_type}'. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": f"La progression de l'utilisateur {user_id} pour le type d'exercice '{exercise_type}' est en cours de développement."},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la progression par type d'exercice: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def get_challenges_progress(request: Request):
    """
    Handler pour récupérer la progression des défis logiques de l'utilisateur.
    Route: GET /api/users/me/challenges/progress
    """
    try:
        current_user = request.state.user
        
        user_id = current_user.get('id')
        logger.info(f"Récupération de la progression des défis pour l'utilisateur {user_id}")
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
            
            # Nombre total de défis actifs dans le système
            total_challenges = db.query(LogicChallenge).filter(
                LogicChallenge.is_active == True,
                LogicChallenge.is_archived == False
            ).count()
            
            # Récupérer toutes les tentatives de l'utilisateur
            all_attempts = db.query(LogicChallengeAttempt).filter(
                LogicChallengeAttempt.user_id == user_id
            ).all()
            
            if not all_attempts:
                return JSONResponse({
                    "completed_challenges": 0,
                    "total_challenges": total_challenges,
                    "success_rate": 0.0,
                    "average_time": 0.0,
                    "challenges": []
                }, status_code=200)
            
            # Identifier les défis complétés
            completed_challenge_ids = set()
            challenge_stats = {}
            
            for attempt in all_attempts:
                challenge_id = attempt.challenge_id
                
                if challenge_id not in challenge_stats:
                    challenge_stats[challenge_id] = {
                        "attempts": 0,
                        "correct_attempts": 0,
                        "best_time": None,
                        "times": []
                    }
                
                challenge_stats[challenge_id]["attempts"] += 1
                
                if attempt.is_correct:
                    challenge_stats[challenge_id]["correct_attempts"] += 1
                    completed_challenge_ids.add(challenge_id)
                    
                    if attempt.time_spent:
                        if challenge_stats[challenge_id]["best_time"] is None:
                            challenge_stats[challenge_id]["best_time"] = attempt.time_spent
                        else:
                            challenge_stats[challenge_id]["best_time"] = min(
                                challenge_stats[challenge_id]["best_time"],
                                attempt.time_spent
                            )
                
                if attempt.time_spent:
                    challenge_stats[challenge_id]["times"].append(attempt.time_spent)
            
            # Calculer le success_rate global
            total_attempts = len(all_attempts)
            correct_attempts = sum(1 for a in all_attempts if a.is_correct)
            success_rate = correct_attempts / total_attempts if total_attempts > 0 else 0.0
            
            # Calculer le temps moyen
            all_times = [a.time_spent for a in all_attempts if a.time_spent]
            average_time = sum(all_times) / len(all_times) if all_times else 0.0
            
            # Construire la liste des défis complétés avec détails
            challenges_list = []
            if completed_challenge_ids:
                completed_challenges = db.query(LogicChallenge).filter(
                    LogicChallenge.id.in_(completed_challenge_ids)
                ).all()
                
                for challenge in completed_challenges:
                    stats = challenge_stats.get(challenge.id, {})
                    challenges_list.append({
                        "id": challenge.id,
                        "title": challenge.title,
                        "is_completed": True,
                        "attempts": stats.get("attempts", 0),
                        "best_time": round(stats.get("best_time", 0), 2) if stats.get("best_time") else None
                    })
            
            return JSONResponse({
                "completed_challenges": len(completed_challenge_ids),
                "total_challenges": total_challenges,
                "success_rate": round(success_rate, 2),
                "average_time": round(average_time, 1),
                "challenges": challenges_list
            }, status_code=200)
        
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la progression des défis: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def update_user_me(request: Request):
    """
    Handler pour mettre à jour les informations de l'utilisateur actuel.
    Route: PUT /api/users/me
    
    Champs modifiables :
    - email (avec vérification unicité)
    - full_name
    - grade_level
    - learning_style
    - preferred_difficulty
    - preferred_theme
    - accessibility_settings (JSON)
    """
    try:
        from app.models.user import User
        
        current_user = request.state.user
        
        user_id = current_user.get('id')
        data = await request.json()
        logger.info(f"Mise à jour profil utilisateur {user_id}")
        
        # Champs autorisés à modifier
        ALLOWED_FIELDS = {
            'email', 'full_name', 'grade_level', 'learning_style',
            'preferred_difficulty', 'preferred_theme', 'accessibility_settings'
        }
        
        # Gérer les champs de confidentialité : regrouper sous privacy_settings
        privacy_fields = ['is_public_profile', 'allow_friend_requests', 'show_in_leaderboards', 
                          'data_retention_consent', 'marketing_consent']
        privacy_data = {}
        for field in privacy_fields:
            if field in data:
                privacy_data[field] = data.pop(field)
        if privacy_data:
            data['privacy_settings'] = privacy_data
        
        # Gérer les champs stockés dans accessibility_settings (JSON)
        # notification_preferences, language_preference, timezone, privacy_settings
        json_fields = ['notification_preferences', 'language_preference', 'timezone', 'privacy_settings']
        json_overrides = {}
        for field in json_fields:
            if field in data:
                json_overrides[field] = data.pop(field)
        
        if json_overrides:
            if 'accessibility_settings' not in data:
                data['accessibility_settings'] = {}
            if isinstance(data['accessibility_settings'], dict):
                data['accessibility_settings'].update(json_overrides)
            else:
                data['accessibility_settings'] = json_overrides
        
        # Filtrer les champs non autorisés
        update_data = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
        
        if not update_data:
            return JSONResponse(
                {"error": "Aucun champ valide à mettre à jour."},
                status_code=400
            )
        
        # Validation email si fourni
        if 'email' in update_data:
            email = update_data['email'].strip().lower()
            if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return JSONResponse(
                    {"error": "Adresse email invalide."},
                    status_code=400
                )
            update_data['email'] = email
        
        # Validation full_name
        if 'full_name' in update_data:
            full_name = update_data['full_name'].strip() if update_data['full_name'] else None
            if full_name and len(full_name) > 100:
                return JSONResponse(
                    {"error": "Le nom complet ne peut pas dépasser 100 caractères."},
                    status_code=400
                )
            update_data['full_name'] = full_name
        
        # Validation grade_level
        if 'grade_level' in update_data:
            grade = update_data['grade_level']
            if grade is not None:
                try:
                    grade = int(grade)
                    if grade < 1 or grade > 12:
                        return JSONResponse(
                            {"error": "Le niveau scolaire doit être entre 1 et 12."},
                            status_code=400
                        )
                    update_data['grade_level'] = grade
                except (ValueError, TypeError):
                    return JSONResponse(
                        {"error": "Le niveau scolaire doit être un nombre."},
                        status_code=400
                    )
        
        # Validation learning_style
        VALID_STYLES = {'visuel', 'auditif', 'kinesthésique', 'lecture'}
        if 'learning_style' in update_data:
            style = update_data['learning_style']
            if style and style not in VALID_STYLES:
                return JSONResponse(
                    {"error": f"Style d'apprentissage invalide. Valeurs acceptées : {', '.join(VALID_STYLES)}"},
                    status_code=400
                )
        
        # Validation preferred_theme
        VALID_THEMES = {'spatial', 'minimalist', 'ocean', 'neutral'}
        if 'preferred_theme' in update_data:
            theme = update_data['preferred_theme']
            if theme and theme not in VALID_THEMES:
                return JSONResponse(
                    {"error": f"Thème invalide. Valeurs acceptées : {', '.join(VALID_THEMES)}"},
                    status_code=400
                )
        
        # Mise à jour en base
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return JSONResponse({"error": "Utilisateur introuvable."}, status_code=404)
            
            # Vérifier unicité email si modifié
            if 'email' in update_data and update_data['email'] != user.email:
                existing = db.query(User).filter(
                    User.email == update_data['email'],
                    User.id != user_id
                ).first()
                if existing:
                    return JSONResponse(
                        {"error": "Cette adresse email est déjà utilisée."},
                        status_code=400
                    )
            
            # Appliquer les modifications
            for field, value in update_data.items():
                if field == 'accessibility_settings':
                    # Merger avec les settings existants pour ne pas écraser
                    # IMPORTANT: créer un NOUVEAU dict pour que SQLAlchemy détecte le changement
                    # (les mutations in-place sur JSON ne sont pas trackées)
                    existing_settings = dict(user.accessibility_settings or {})
                    if isinstance(value, dict):
                        existing_settings.update(value)
                        setattr(user, field, existing_settings)
                    else:
                        setattr(user, field, value)
                else:
                    setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            # Construire la réponse
            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if user.role else None,
                "grade_level": user.grade_level,
                "learning_style": user.learning_style,
                "preferred_difficulty": user.preferred_difficulty,
                "preferred_theme": user.preferred_theme,
                "accessibility_settings": user.accessibility_settings,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "total_points": user.total_points,
                "current_level": user.current_level,
                "jedi_rank": user.jedi_rank,
            }
            
            logger.info(f"Profil utilisateur {user_id} mis à jour : {list(update_data.keys())}")
            return JSONResponse(response_data)
            
        finally:
            db.close()
            
    except json.JSONDecodeError:
        return JSONResponse({"error": "Données JSON invalides."}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def update_user_password_me(request: Request):
    """
    Handler pour mettre à jour le mot de passe de l'utilisateur actuel.
    Route: PUT /api/users/me/password
    
    Body attendu :
    - current_password: mot de passe actuel
    - new_password: nouveau mot de passe (min 8 caractères)
    """
    try:
        from app.models.user import User
        from app.core.security import verify_password, get_password_hash
        
        current_user = request.state.user
        
        user_id = current_user.get('id')
        data = await request.json()
        
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # Validation
        if not current_password:
            return JSONResponse(
                {"error": "Le mot de passe actuel est requis."},
                status_code=400
            )
        if not new_password:
            return JSONResponse(
                {"error": "Le nouveau mot de passe est requis."},
                status_code=400
            )
        if len(new_password) < 8:
            return JSONResponse(
                {"error": "Le nouveau mot de passe doit contenir au moins 8 caractères."},
                status_code=400
            )
        if current_password == new_password:
            return JSONResponse(
                {"error": "Le nouveau mot de passe doit être différent de l'ancien."},
                status_code=400
            )
        
        # Vérification et mise à jour en base
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return JSONResponse({"error": "Utilisateur introuvable."}, status_code=404)
            
            # Vérifier le mot de passe actuel
            if not verify_password(current_password, user.hashed_password):
                return JSONResponse(
                    {"error": "Le mot de passe actuel est incorrect."},
                    status_code=401
                )
            
            # Hasher et sauvegarder le nouveau mot de passe
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            
            logger.info(f"Mot de passe de l'utilisateur {user_id} mis à jour avec succès")
            return JSONResponse({
                "success": True,
                "message": "Mot de passe mis à jour avec succès."
            })
            
        finally:
            db.close()
            
    except json.JSONDecodeError:
        return JSONResponse({"error": "Données JSON invalides."}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du mot de passe: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def delete_user_me(request: Request):
    """
    Handler pour supprimer le compte de l'utilisateur connecté.
    Route: DELETE /api/users/me
    
    Supprime l'utilisateur et toutes ses données associées (cascade).
    """
    try:
        from app.models.user import User
        
        current_user = request.state.user
        
        user_id = current_user.get('id')
        username = current_user.get('username')
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return JSONResponse({"error": "Utilisateur introuvable."}, status_code=404)
            
            # Suppression (les relations cascade suppriment les données liées)
            db.delete(user)
            db.commit()
            
            logger.info(f"Compte utilisateur supprimé : {username} (ID: {user_id})")
            
            # Créer la réponse avec suppression du cookie
            response = JSONResponse({
                "success": True,
                "message": "Votre compte a été supprimé avec succès."
            })
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du compte: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def delete_user(request: Request):
    """
    Handler pour supprimer un utilisateur par ID (admin).
    Route: DELETE /api/users/{user_id}
    """
    try:
        current_user = request.state.user
        
        user_to_delete_id = int(request.path_params.get('user_id'))
        current_user_id = current_user.get('id')
        
        if user_to_delete_id != current_user_id:
            return JSONResponse({"error": "Non autorisé à supprimer cet utilisateur"}, status_code=403)
            
        logger.info(f"Tentative de suppression de l'utilisateur {user_to_delete_id} - Redirigé vers DELETE /api/users/me")
        return JSONResponse(
            {"message": "Utilisez DELETE /api/users/me pour supprimer votre compte."},
            status_code=400
        )
    except ValueError:
        return JSONResponse({"error": "ID utilisateur invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def export_user_data(request: Request):
    """
    Exporte toutes les données de l'utilisateur connecté (RGPD).
    Route: GET /api/users/me/export
    
    Retourne un JSON avec : profil, exercices tentés, défis tentés, badges, progression.
    """
    try:
        from app.models.user import User
        from app.models.attempt import Attempt
        from app.models.exercise import Exercise
        from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
        from app.models.achievement import UserAchievement
        from app.models.progress import Progress
        from app.models.recommendation import Recommendation
        
        current_user = request.state.user
        
        user_id = current_user.get('id')
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return JSONResponse({"error": "Utilisateur introuvable."}, status_code=404)
            
            # Profil utilisateur (tous les champs)
            profile = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if user.role else None,
                "is_active": user.is_active,
                "grade_level": user.grade_level,
                "learning_style": user.learning_style,
                "preferred_difficulty": user.preferred_difficulty,
                "preferred_theme": user.preferred_theme,
                "accessibility_settings": user.accessibility_settings,
                "total_points": user.total_points,
                "current_level": user.current_level,
                "experience_points": user.experience_points if hasattr(user, 'experience_points') else 0,
                "jedi_rank": user.jedi_rank,
                "avatar_url": user.avatar_url if hasattr(user, 'avatar_url') else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            }
            
            # Tentatives d'exercices
            attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
            exercises_data = []
            for a in attempts:
                exercises_data.append({
                    "exercise_id": a.exercise_id,
                    "answer": a.user_answer if hasattr(a, 'user_answer') else None,
                    "is_correct": a.is_correct,
                    "time_spent": a.time_spent if hasattr(a, 'time_spent') else None,
                    "attempt_number": a.attempt_number if hasattr(a, 'attempt_number') else None,
                    "hints_used": a.hints_used if hasattr(a, 'hints_used') else 0,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                })
            
            # Tentatives de défis logiques
            challenge_attempts = db.query(LogicChallengeAttempt).filter(
                LogicChallengeAttempt.user_id == user_id
            ).all()
            challenges_data = []
            for ca in challenge_attempts:
                challenges_data.append({
                    "challenge_id": ca.challenge_id,
                    "user_solution": ca.user_solution,
                    "is_correct": ca.is_correct,
                    "time_spent": ca.time_spent,
                    "hints_used": ca.hints_used,
                    "created_at": ca.created_at.isoformat() if ca.created_at else None,
                })
            
            # Badges obtenus
            achievements = db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()
            badges_data = []
            for ach in achievements:
                badges_data.append({
                    "achievement_id": ach.achievement_id if hasattr(ach, 'achievement_id') else ach.id,
                    "earned_at": ach.earned_at.isoformat() if hasattr(ach, 'earned_at') and ach.earned_at else None,
                    "progress_data": ach.progress_data if hasattr(ach, 'progress_data') else None,
                    "is_displayed": ach.is_displayed if hasattr(ach, 'is_displayed') else True,
                })
            
            # Progression par type d'exercice
            progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
            progress_data = []
            for p in progress_records:
                progress_data.append({
                    "exercise_type": p.exercise_type,
                    "difficulty": p.difficulty,
                    "total_attempts": p.total_attempts,
                    "correct_attempts": p.correct_attempts,
                    "success_rate": p.success_rate if hasattr(p, 'success_rate') else None,
                    "last_attempt_at": p.last_attempt_at.isoformat() if hasattr(p, 'last_attempt_at') and p.last_attempt_at else None,
                })
            
            # Recommandations personnalisées
            recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
            recommendations_data = []
            for r in recommendations:
                recommendations_data.append({
                    "exercise_type": r.exercise_type if hasattr(r, 'exercise_type') else None,
                    "priority": r.priority if hasattr(r, 'priority') else None,
                    "is_completed": r.is_completed if hasattr(r, 'is_completed') else False,
                    "reason": r.reason if hasattr(r, 'reason') else None,
                    "created_at": r.created_at.isoformat() if hasattr(r, 'created_at') and r.created_at else None,
                })
            
            export = {
                "export_date": datetime.now(timezone.utc).isoformat(),
                "format_version": "1.1",
                "profile": profile,
                "exercise_attempts": exercises_data,
                "challenge_attempts": challenges_data,
                "badges_earned": badges_data,
                "progress": progress_data,
                "recommendations": recommendations_data,
                "statistics": {
                    "total_exercise_attempts": len(exercises_data),
                    "total_challenge_attempts": len(challenges_data),
                    "total_badges": len(badges_data),
                    "total_progress_records": len(progress_data),
                    "total_recommendations": len(recommendations_data),
                }
            }
            
            logger.info(f"Export de données pour l'utilisateur {user_id} : {len(exercises_data)} exercices, {len(challenges_data)} défis, {len(badges_data)} badges")
            return JSONResponse(export)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erreur lors de l'export des données: {e}")
        traceback.print_exc()
        return JSONResponse({"error": get_safe_error_message(e)}, status_code=500)


@require_auth
async def get_user_sessions(request: Request):
    """
    Handler pour récupérer les sessions actives de l'utilisateur.
    Route: GET /api/users/me/sessions
    """
    try:
        current_user = request.state.user
        
        user_id = current_user.get("id")
        
        # Récupérer la session DB
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.user_session import UserSession
            from sqlalchemy import and_
            
            # Récupérer toutes les sessions actives non expirées
            sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(timezone.utc)
                )
            ).order_by(UserSession.last_activity.desc()).all()
            
            logger.debug(f"Récupération de {len(sessions)} sessions actives pour user_id={user_id}")
            
            # Convertir en dict
            session_list = []
            for session in sessions:
                session_dict = {
                    "id": session.id,
                    "device_info": session.device_info,
                    "ip_address": str(session.ip_address) if session.ip_address else None,
                    "user_agent": session.user_agent,
                    "location_data": session.location_data,
                    "is_active": session.is_active,
                    "last_activity": session.last_activity.isoformat(),
                    "created_at": session.created_at.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "is_current": False  # TODO: Détecter la session actuelle via le token
                }
                session_list.append(session_dict)
            
            return JSONResponse(session_list, status_code=200)
        finally:
            EnhancedServerAdapter.close_db_session(db)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sessions: {e}")
        traceback.print_exc()
        return JSONResponse({"error": "Erreur lors de la récupération des sessions"}, status_code=500)


@require_auth
async def revoke_user_session(request: Request):
    """
    Handler pour révoquer une session utilisateur spécifique.
    Route: DELETE /api/users/me/sessions/{session_id}
    """
    try:
        current_user = request.state.user
        
        user_id = current_user.get("id")
        session_id = int(request.path_params.get('session_id'))
        
        # Récupérer la session DB
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.user_session import UserSession
            
            # Récupérer la session
            session = db.query(UserSession).filter(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            ).first()
            
            if not session:
                logger.warning(f"Tentative de révocation d'une session inexistante ou non autorisée: session_id={session_id}, user_id={user_id}")
                return JSONResponse(
                    {"error": "Session non trouvée ou vous n'avez pas l'autorisation de la révoquer"},
                    status_code=404
                )
            
            # Marquer la session comme inactive
            session.is_active = False
            db.commit()
            
            logger.info(f"Session {session_id} révoquée pour user_id={user_id}")
            
            return JSONResponse({
                "success": True,
                "message": "Session révoquée avec succès"
            }, status_code=200)
        
        except Exception as e:
            db.rollback()
            raise
        finally:
            EnhancedServerAdapter.close_db_session(db)
    
    except ValueError:
        return JSONResponse({"error": "ID de session invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la révocation de la session: {e}")
        traceback.print_exc()
        return JSONResponse({"error": "Erreur lors de la révocation de la session"}, status_code=500)