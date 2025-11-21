"""
Handlers pour les recommandations personnalisées.
"""
import traceback
from starlette.responses import JSONResponse
from server.auth import get_current_user
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.recommendation_service import RecommendationService
from app.core.messages import SystemMessages


async def get_recommendations(request):
    """
    Récupère les recommandations personnalisées pour l'utilisateur connecté.
    Route: GET /api/recommendations
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Authentification requise"}, status_code=401)

        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)

        db = EnhancedServerAdapter.get_db_session()
        try:
            # Récupérer les recommandations existantes
            recommendations = RecommendationService.get_user_recommendations(db, user_id, limit=5)

            # Si aucune recommandation n'existe, générer de nouvelles
            if not recommendations:
                try:
                    RecommendationService.generate_recommendations(db, user_id)
                    db.commit()
                    recommendations = RecommendationService.get_user_recommendations(db, user_id, limit=5)
                except Exception as gen_error:
                    print(f"Erreur lors de la génération des recommandations: {str(gen_error)}")
                    traceback.print_exc()
                    recommendations = []

            # Sérialiser les recommandations
            recommendations_data = []
            for rec in recommendations:
                rec_data = {
                    "id": rec.id,
                    "exercise_type": str(rec.exercise_type),  # Déjà une string dans le modèle
                    "difficulty": str(rec.difficulty),  # Déjà une string dans le modèle
                    "reason": rec.reason or "",
                    "priority": rec.priority,  # Inclure la priorité pour le frontend
                }

                # Ajouter les informations de l'exercice si disponible
                if rec.exercise_id:
                    rec_data["exercise_id"] = rec.exercise_id
                    # Optionnel: récupérer le titre et la question de l'exercice
                    try:
                        from app.services.exercise_service import ExerciseService
                        exercise = ExerciseService.get_exercise(db, rec.exercise_id)
                        if exercise:
                            rec_data["exercise_title"] = exercise.title
                            rec_data["exercise_question"] = exercise.question
                    except Exception:
                        pass  # Ignorer si l'exercice n'existe plus

                recommendations_data.append(rec_data)

            return JSONResponse(recommendations_data)
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except Exception as recommendations_retrieval_error:
        print(f"Erreur lors de la récupération des recommandations: {recommendations_retrieval_error}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


async def generate_recommendations(request):
    """
    Génère de nouvelles recommandations pour l'utilisateur connecté.
    Route: POST /api/recommendations/generate
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Authentification requise"}, status_code=401)

        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "ID utilisateur manquant"}, status_code=400)

        db = EnhancedServerAdapter.get_db_session()
        try:
            # Générer de nouvelles recommandations
            recommendations = RecommendationService.generate_recommendations(db, user_id)
            db.commit()

            return JSONResponse({
                "message": "Recommandations générées avec succès",
                "count": len(recommendations) if recommendations else 0
            })
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except Exception as recommendations_generation_error:
        print(f"Erreur lors de la génération des recommandations: {recommendations_generation_error}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

