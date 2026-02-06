"""
API endpoints spécifiques pour la page Challenges - Support complet des interactions
"""
import asyncio
import json

from starlette.responses import JSONResponse

from server.auth import get_current_user


async def api_start_challenge(request):
    """
    Démarre un challenge et redirige vers les exercices appropriés
    POST /api/challenges/start/{challenge_id}
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
        challenge_id = int(request.path_params["challenge_id"])
        
        # Récupérer les données du challenge et déterminer le type d'exercice
        challenge_mappings = {
            1: {"type": "ADDITION", "difficulty": "INITIE"},
            2: {"type": "MULTIPLICATION", "difficulty": "PADAWAN"}, 
            3: {"type": "FRACTIONS", "difficulty": "CHEVALIER"},
            4: {"type": "GEOMETRIE", "difficulty": "MAITRE"},
            999: {"type": "GEOMETRIE", "difficulty": "CHEVALIER"}  # Mission Alderaan
        }
        
        challenge_info = challenge_mappings.get(challenge_id)
        if not challenge_info:
            return JSONResponse({"error": "Challenge non trouvé"}, status_code=404)
        
        # Construire l'URL de redirection vers les exercices
        exercises_url = f"/exercises?exercise_type={challenge_info['type'].lower()}&difficulty={challenge_info['difficulty'].lower()}"
        
        return JSONResponse({
            "success": True,
            "message": f"Challenge {challenge_id} démarré avec succès",
            "redirect_url": exercises_url,
            "challenge_type": challenge_info["type"],
            "difficulty": challenge_info["difficulty"]
        })
        
    except Exception as challenge_start_error:
        return JSONResponse({"error": f"Erreur serveur: {str(challenge_start_error)}"}, status_code=500)

async def api_get_challenge_progress(request):
    """
    Récupère la progression d'un challenge spécifique
    GET /api/challenges/progress/{challenge_id}
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
        challenge_id = int(request.path_params["challenge_id"])
        
        # Données de progression simulées (à connecter à la vraie BDD)
        progress_data = {
            1: {"attempts": 4, "total_exercises": 5, "progress_percentage": 80, "points_earned": 40},
            2: {"attempts": 0, "total_exercises": 8, "progress_percentage": 0, "points_earned": 0},
            3: {"attempts": 3, "total_exercises": 6, "progress_percentage": 50, "points_earned": 100},
            4: {"attempts": 0, "total_exercises": 10, "progress_percentage": 0, "points_earned": 0},
            999: {"attempts": 7, "total_exercises": 20, "progress_percentage": 35, "points_earned": 175}
        }
        
        progress = progress_data.get(challenge_id)
        if not progress:
            return JSONResponse({"error": "Challenge non trouvé"}, status_code=404)
        
        return JSONResponse({
            "challenge_id": challenge_id,
            "progress": progress,
            "is_completed": progress["progress_percentage"] >= 100,
            "next_action": "continue" if progress["progress_percentage"] > 0 else "start"
        })
        
    except Exception as progress_api_error:
        return JSONResponse({"error": f"Erreur serveur: {str(progress_api_error)}"}, status_code=500)

async def api_get_challenge_rewards(request):
    """
    Récupère les récompenses d'un challenge
    GET /api/challenges/rewards/{challenge_id}
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
        challenge_id = int(request.path_params["challenge_id"])
        
        # Données des récompenses par challenge
        rewards_data = {
            1: {
                "stars": 50,
                "badges": ["Compteur de Tatooine"],
                "xp": 25,
                "description": "Maîtrise des additions de base"
            },
            2: {
                "stars": 120,
                "badges": ["Pilote Hyperespace"],
                "xp": 60,
                "description": "Expert en multiplications"
            },
            3: {
                "stars": 200,
                "badges": ["Maître des Rations", "Survivant de Hoth"],
                "xp": 100,
                "description": "Sage des fractions"
            },
            4: {
                "stars": 500,
                "badges": ["Architecte Impérial", "Destructeur d'Étoile"],
                "xp": 250,
                "description": "Génie de la géométrie"
            },
            999: {
                "stars": 250,
                "badges": ["Héros d'Alderaan", "Sauveur de la Galaxie"],
                "xp": 125,
                "description": "Mission spéciale accomplie",
                "special_reward": "Accès au niveau Maître Jedi"
            }
        }
        
        rewards = rewards_data.get(challenge_id)
        if not rewards:
            return JSONResponse({"error": "Challenge non trouvé"}, status_code=404)
        
        return JSONResponse({
            "challenge_id": challenge_id,
            "rewards": rewards,
            "can_claim": True,  # À connecter à la logique métier
            "already_claimed": False
        })
        
    except Exception as e:
        return JSONResponse({"error": f"Erreur serveur: {str(e)}"}, status_code=500)

async def api_get_users_leaderboard(request):
    """
    Récupère le leaderboard des utilisateurs
    GET /api/users/leaderboard
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
        # Leaderboard simulé (à connecter à la vraie BDD)
        leaderboard = [
            {
                "rank": 1,
                "username": "Maître Yoda",
                "total_points": 2450,
                "jedi_rank": "MAITRE",
                "avatar_url": None,
                "badges_count": 15,
                "recent_activity": "Mission Dagobah terminée"
            },
            {
                "rank": 2,
                "username": "Obi-Wan Kenobi", 
                "total_points": 2180,
                "jedi_rank": "MAITRE",
                "avatar_url": None,
                "badges_count": 12,
                "recent_activity": "Défi géométrie réussi"
            },
            {
                "rank": 3,
                "username": "Luke Skywalker",
                "total_points": 1950,
                "jedi_rank": "CHEVALIER",
                "avatar_url": None,
                "badges_count": 8,
                "recent_activity": "Entraînement Padawan"
            },
            {
                "rank": 4,
                "username": "Princesse Leia",
                "total_points": 1720,
                "jedi_rank": "CHEVALIER",
                "avatar_url": None,
                "badges_count": 7,
                "recent_activity": "Mission diplomatique"
            },
            {
                "rank": 5,
                "username": current_user.get("username", "Vous"),
                "total_points": current_user.get("total_points", 0),
                "jedi_rank": current_user.get("jedi_rank", "INITIE"),
                "avatar_url": current_user.get("avatar_url"),
                "badges_count": 3,
                "recent_activity": "Défis quotidiens",
                "is_current_user": True
            }
        ]
        
        return JSONResponse({
            "leaderboard": leaderboard,
            "total_users": len(leaderboard),
            "current_user_rank": next((user["rank"] for user in leaderboard if user.get("is_current_user")), 5),
            "updated_at": "2025-06-04T19:49:00Z"
        })
        
    except Exception as e:
        return JSONResponse({"error": f"Erreur serveur: {str(e)}"}, status_code=500)

async def api_get_user_badges_progress(request):
    """
    Récupère la progression des badges de l'utilisateur
    GET /api/challenges/badges/progress
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
        # Progression des badges simulée
        badges_progress = [
            {
                "id": 1,
                "name": "Série de Victoires",
                "description": "Réussir 5 défis d'affilée",
                "icon": "fas fa-fire",
                "color": "blue",
                "current_progress": 3,
                "target": 5,
                "progress_percentage": 60,
                "is_unlocked": False,
                "reward_stars": 100
            },
            {
                "id": 2,
                "name": "Maître des Fractions",
                "description": "Terminer 20 exercices de fractions",
                "icon": "fas fa-star",
                "color": "purple",
                "current_progress": 7,
                "target": 20,
                "progress_percentage": 35,
                "is_unlocked": False,
                "reward_stars": 200
            },
            {
                "id": 3,
                "name": "Empereur des Maths",
                "description": "Être #1 du classement",
                "icon": "fas fa-crown",
                "color": "red",
                "current_progress": 0,
                "target": 1,
                "progress_percentage": 0,
                "is_unlocked": False,
                "reward_stars": 1000,
                "is_legendary": True
            }
        ]
        
        return JSONResponse({
            "badges_progress": badges_progress,
            "total_badges": len(badges_progress),
            "unlocked_count": len([b for b in badges_progress if b["is_unlocked"]]),
            "total_possible_stars": sum(b["reward_stars"] for b in badges_progress)
        })
        
    except Exception as e:
        return JSONResponse({"error": f"Erreur serveur: {str(e)}"}, status_code=500) 