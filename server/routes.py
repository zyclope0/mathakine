"""
Routes API pour Mathakine (backend Starlette).

Ce module définit uniquement les routes API JSON utilisées par le frontend Next.js.
Toutes les routes HTML/templates ont été supprimées (frontend géré par Next.js).
"""
from typing import List

from starlette.routing import Route

# Imports API challenges
from server.api_challenges import (api_get_challenge_progress,
                                   api_get_challenge_rewards,
                                   api_get_user_badges_progress,
                                   api_get_users_leaderboard,
                                   api_start_challenge)
# Imports API routes helpers (fonctions qui existent vraiment)
from server.api_routes import (api_forgot_password, api_logout,
                               delete_exercise, get_exercises_list,
                               handle_recommendation_complete)
# Imports API handlers - Auth
from server.handlers.auth_handlers import (api_get_current_user, api_login,
                                           api_refresh_token,
                                           resend_verification_email,
                                           verify_email)
# Imports API handlers - Badges
from server.handlers.badge_handlers import (check_user_badges,
                                            get_available_badges,
                                            get_user_badges,
                                            get_user_gamification_stats)
# Imports API handlers - Challenges
from server.handlers.challenge_handlers import (generate_ai_challenge_stream,
                                                get_challenge,
                                                get_challenge_hint,
                                                get_challenges_list)
from server.handlers.challenge_handlers import \
    get_completed_challenges_ids as get_completed_challenges_ids_challenges
from server.handlers.challenge_handlers import submit_challenge_answer
# Imports API handlers - Chat
from server.handlers.chat_handlers import chat_api, chat_api_stream
# Imports API handlers - Exercises
from server.handlers.exercise_handlers import (generate_ai_exercise_stream,
                                               generate_exercise,
                                               generate_exercise_api,
                                               get_completed_exercises_ids,
                                               get_exercise, submit_answer)
# Imports API handlers - Recommendations
from server.handlers.recommendation_handlers import (generate_recommendations,
                                                     get_recommendations)
# Imports API handlers - Users
from server.handlers.user_handlers import create_user_account, get_user_stats


def get_routes() -> List:
    """
    Retourne la liste des routes API JSON pour le backend Starlette.
    
    Toutes les routes HTML/templates ont été supprimées car le frontend
    est géré par Next.js. Ce backend expose uniquement une API JSON.
    
    Returns:
        List[Route]: Liste des routes API
    """
    return [
        # ========================================
        # AUTH API (7 routes)
        # ========================================
        Route("/api/auth/login", endpoint=api_login, methods=["POST"]),
        Route("/api/auth/refresh", endpoint=api_refresh_token, methods=["POST"]),
        Route("/api/auth/logout", endpoint=api_logout, methods=["POST"]),
        Route("/api/auth/forgot-password", endpoint=api_forgot_password, methods=["POST"]),
        Route("/api/auth/verify-email", endpoint=verify_email, methods=["GET"]),
        Route("/api/auth/resend-verification", endpoint=resend_verification_email, methods=["POST"]),
        
        # ========================================
        # USERS API (3 routes)
        # ========================================
        Route("/api/users/", endpoint=create_user_account, methods=["POST"]),
        Route("/api/users/me", endpoint=api_get_current_user, methods=["GET"]),
        Route("/api/users/stats", endpoint=get_user_stats),
        
        # ========================================
        # EXERCISES API (8 routes)
        # ========================================
        Route("/api/exercises", endpoint=get_exercises_list),
        Route("/api/exercises/{exercise_id:int}", endpoint=get_exercise, methods=["GET"]),
        Route("/api/exercises/{exercise_id:int}", endpoint=delete_exercise, methods=["DELETE"]),
        Route("/api/exercises/generate", endpoint=generate_exercise, methods=["GET"]),
        Route("/api/exercises/generate", endpoint=generate_exercise_api, methods=["POST"]),
        Route("/api/exercises/generate-ai-stream", endpoint=generate_ai_exercise_stream, methods=["GET"]),
        Route("/api/exercises/completed-ids", endpoint=get_completed_exercises_ids, methods=["GET"]),
        Route("/api/submit-answer", endpoint=submit_answer, methods=["POST"]),
        
        # ========================================
        # BADGES API (4 routes)
        # ========================================
        Route("/api/badges/user", endpoint=get_user_badges),
        Route("/api/badges/available", endpoint=get_available_badges),
        Route("/api/badges/check", endpoint=check_user_badges, methods=["POST"]),
        Route("/api/badges/stats", endpoint=get_user_gamification_stats),
        
        # ========================================
        # RECOMMENDATIONS API (3 routes)
        # ========================================
        Route("/api/recommendations", endpoint=get_recommendations, methods=["GET"]),
        Route("/api/recommendations/generate", endpoint=generate_recommendations, methods=["POST"]),
        Route("/api/recommendations/complete", endpoint=handle_recommendation_complete, methods=["POST"]),
        
        # ========================================
        # CHAT API (2 routes)
        # ========================================
        Route("/api/chat", endpoint=chat_api, methods=["POST"]),
        Route("/api/chat/stream", endpoint=chat_api_stream, methods=["POST"]),
        
        # ========================================
        # CHALLENGES API (10 routes) ⚠️ CRITIQUE pour Next.js
        # ========================================
        Route("/api/challenges", endpoint=get_challenges_list, methods=["GET"]),
        Route("/api/challenges/{challenge_id:int}", endpoint=get_challenge, methods=["GET"]),
        Route("/api/challenges/{challenge_id:int}/attempt", endpoint=submit_challenge_answer, methods=["POST"]),
        Route("/api/challenges/{challenge_id:int}/hint", endpoint=get_challenge_hint, methods=["GET"]),
        Route("/api/challenges/completed-ids", endpoint=get_completed_challenges_ids_challenges, methods=["GET"]),
        Route("/api/challenges/start/{challenge_id:int}", endpoint=api_start_challenge, methods=["POST"]),
        Route("/api/challenges/progress/{challenge_id:int}", endpoint=api_get_challenge_progress),
        Route("/api/challenges/rewards/{challenge_id:int}", endpoint=api_get_challenge_rewards),
        Route("/api/challenges/generate-ai-stream", endpoint=generate_ai_challenge_stream, methods=["GET"]),
        Route("/api/challenges/badges/progress", endpoint=api_get_user_badges_progress),
        
        # ========================================
        # USERS LEADERBOARD (1 route)
        # ========================================
        Route("/api/users/leaderboard", endpoint=api_get_users_leaderboard),
    ]
