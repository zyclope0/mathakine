"""
Handlers pour la gestion des utilisateurs et statistiques (API)
"""
import traceback
import json
import re
from datetime import datetime, timedelta, timezone
from starlette.responses import JSONResponse
from starlette.requests import Request
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.auth_service import create_user, get_user_by_email
from app.schemas.user import UserCreate
from app.core.messages import SystemMessages
from loguru import logger
from fastapi import HTTPException, status

async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    Paramètres de requête:
        - timeRange: "7" (7 jours), "30" (30 jours), "90" (3 mois), "all" (tout)
    """
    try:
        # Récupérer l'utilisateur connecté au lieu d'utiliser un ID fixe
        from server.auth import get_current_user
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
                from app.models.attempt import Attempt
                from app.models.logic_challenge import LogicChallengeAttempt
                
                # Calculer la date limite si nécessaire
                if time_range != "all":
                    days = int(time_range)
                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                else:
                    cutoff_date = None
                
                # Récupérer les tentatives d'exercices récentes
                exercise_attempts_query = db.query(Attempt).filter(
                    Attempt.user_id == user_id
                ).order_by(Attempt.created_at.desc()).limit(5)
                
                if cutoff_date:
                    exercise_attempts_query = exercise_attempts_query.filter(Attempt.created_at >= cutoff_date)
                
                exercise_attempts = exercise_attempts_query.all()
                
                for attempt in exercise_attempts:
                    recent_activity.append({
                        "type": "exercise",
                        "description": f"Exercice complété",
                        "time": attempt.created_at.isoformat() if attempt.created_at else datetime.now(timezone.utc).isoformat(),
                        "is_correct": attempt.is_correct
                    })
                
                # Récupérer les tentatives de challenges récentes
                challenge_attempts_query = db.query(LogicChallengeAttempt).filter(
                    LogicChallengeAttempt.user_id == user_id
                ).order_by(LogicChallengeAttempt.created_at.desc()).limit(5)
                
                if cutoff_date:
                    challenge_attempts_query = challenge_attempts_query.filter(LogicChallengeAttempt.created_at >= cutoff_date)
                
                challenge_attempts = challenge_attempts_query.all()
                
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
            from app.utils.email_verification import generate_verification_token
            from datetime import datetime, timezone
            
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
                from app.services.email_service import EmailService
                import os
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
